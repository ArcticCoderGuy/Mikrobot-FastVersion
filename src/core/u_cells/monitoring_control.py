"""
U-Cell 5: Monitoring & Control
Six Sigma quality control with Cp/Cpk ≥ 2.9
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from collections import deque
import numpy as np
from . import UCell, CellInput, CellOutput
import logging
import statistics

logger = logging.getLogger(__name__)


class MonitoringControlCell(UCell):
    """
    Continuous monitoring and quality control
    - Six Sigma metrics (Cp/Cpk)
    - Performance tracking
    - Alert system
    - Self-healing mechanisms
    """
    
    def __init__(self, alert_callback=None):
        super().__init__(cell_id="U5", name="Monitoring & Control")
        self.alert_callback = alert_callback
        
        # Six Sigma configuration
        self.quality_config = {
            'target_cpk': 2.9,  # Ultra-high quality target
            'min_cpk': 1.67,    # Minimum acceptable quality
            'sample_size': 30,   # Minimum samples for Cpk calculation
            'control_limits_sigma': 3,  # 3-sigma control limits
            'spec_limits': {
                'win_rate': {'LSL': 0.55, 'USL': 0.85, 'target': 0.70},
                'risk_reward': {'LSL': 1.5, 'USL': 4.0, 'target': 2.5},
                'execution_time': {'LSL': 0, 'USL': 1000, 'target': 200},  # ms
                'slippage': {'LSL': 0, 'USL': 2.0, 'target': 0.5}  # pips
            }
        }
        
        # Performance tracking
        self.performance_data = {
            'trades': deque(maxlen=1000),
            'win_rates': deque(maxlen=100),
            'execution_times': deque(maxlen=100),
            'slippages': deque(maxlen=100),
            'risk_rewards': deque(maxlen=100)
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'consecutive_losses': 3,
            'drawdown_percent': 5.0,
            'high_slippage_pips': 3.0,
            'low_cpk': 1.67,
            'system_latency_ms': 500
        }
        
        # Control state
        self.control_state = {
            'trading_enabled': True,
            'alert_active': False,
            'last_cpk_calculation': None,
            'quality_status': 'OPTIMAL'
        }
    
    def validate_input(self, cell_input: CellInput) -> bool:
        """Validate input from Trade Execution"""
        required_keys = ['order_id', 'symbol', 'direction', 'status']
        return all(key in cell_input.data for key in required_keys)
    
    def process(self, cell_input: CellInput) -> CellOutput:
        """Monitor trade and system performance"""
        data = cell_input.data
        
        try:
            # Update performance data
            self._update_performance_data(data)
            
            # Calculate Six Sigma metrics
            quality_metrics = self._calculate_six_sigma_metrics()
            
            # Perform quality checks
            quality_checks = self._perform_quality_checks(quality_metrics)
            
            # Generate alerts if needed
            alerts = self._check_alert_conditions(data, quality_metrics)
            
            # Determine control actions
            control_actions = self._determine_control_actions(quality_checks, alerts)
            
            # Apply control actions
            if control_actions:
                self._apply_control_actions(control_actions)
            
            # Prepare monitoring report
            monitoring_report = {
                'trade_id': data.get('order_id'),
                'timestamp': datetime.utcnow().isoformat(),
                'quality_metrics': quality_metrics,
                'quality_status': self.control_state['quality_status'],
                'alerts': alerts,
                'control_actions': control_actions,
                'performance_summary': self._get_performance_summary(),
                'trading_enabled': self.control_state['trading_enabled'],
                'system_health': self._assess_system_health()
            }
            
            return CellOutput(
                timestamp=datetime.utcnow(),
                status='success',
                data=monitoring_report,
                next_cell=None,  # End of pipeline
                trace_id=cell_input.trace_id
            )
            
        except Exception as e:
            logger.error(f"Monitoring error: {str(e)}")
            return CellOutput(
                timestamp=datetime.utcnow(),
                status='failed',
                data={},
                trace_id=cell_input.trace_id,
                errors=[str(e)]
            )
    
    def _update_performance_data(self, trade_data: Dict[str, Any]):
        """Update performance tracking data"""
        # Add trade to history
        self.performance_data['trades'].append({
            'timestamp': datetime.utcnow(),
            'order_id': trade_data.get('order_id'),
            'result': trade_data.get('result', 'pending'),
            'pnl': trade_data.get('pnl', 0),
            'execution_time': trade_data.get('execution_time_ms', 0),
            'slippage': trade_data.get('slippage', 0)
        })
        
        # Update specific metrics if available
        if 'execution_time_ms' in trade_data:
            self.performance_data['execution_times'].append(trade_data['execution_time_ms'])
        
        if 'slippage' in trade_data:
            self.performance_data['slippages'].append(trade_data['slippage'])
    
    def _calculate_six_sigma_metrics(self) -> Dict[str, Any]:
        """Calculate Six Sigma quality metrics"""
        metrics = {}
        
        # Calculate Cp and Cpk for each metric
        for metric_name, spec_limits in self.quality_config['spec_limits'].items():
            data = self._get_metric_data(metric_name)
            
            if len(data) >= self.quality_config['sample_size']:
                cp, cpk = self._calculate_cp_cpk(data, spec_limits)
                sigma_level = self._cpk_to_sigma_level(cpk)
                
                metrics[metric_name] = {
                    'cp': round(cp, 3),
                    'cpk': round(cpk, 3),
                    'sigma_level': round(sigma_level, 2),
                    'mean': round(statistics.mean(data), 3),
                    'std_dev': round(statistics.stdev(data), 3),
                    'samples': len(data),
                    'meets_target': cpk >= self.quality_config['target_cpk']
                }
            else:
                metrics[metric_name] = {
                    'status': 'insufficient_data',
                    'samples': len(data),
                    'required': self.quality_config['sample_size']
                }
        
        return metrics
    
    def _calculate_cp_cpk(self, data: List[float], spec_limits: Dict[str, float]) -> Tuple[float, float]:
        """Calculate Process Capability indices"""
        if not data or len(data) < 2:
            return 0.0, 0.0
        
        # Get specification limits
        lsl = spec_limits.get('LSL', float('-inf'))
        usl = spec_limits.get('USL', float('inf'))
        target = spec_limits.get('target')
        
        # Calculate statistics
        mean = statistics.mean(data)
        std_dev = statistics.stdev(data)
        
        if std_dev == 0:
            return float('inf'), float('inf')
        
        # Calculate Cp (potential capability)
        if lsl != float('-inf') and usl != float('inf'):
            cp = (usl - lsl) / (6 * std_dev)
        else:
            cp = float('inf')
        
        # Calculate Cpk (actual capability)
        cpu = float('inf') if usl == float('inf') else (usl - mean) / (3 * std_dev)
        cpl = float('inf') if lsl == float('-inf') else (mean - lsl) / (3 * std_dev)
        cpk = min(cpu, cpl)
        
        return cp, cpk
    
    def _cpk_to_sigma_level(self, cpk: float) -> float:
        """Convert Cpk to approximate Sigma level"""
        # Approximation: Sigma Level ≈ 3 * Cpk
        return min(3 * cpk, 6.0)
    
    def _get_metric_data(self, metric_name: str) -> List[float]:
        """Get data for specific metric"""
        if metric_name == 'win_rate':
            # Calculate win rate from recent trades
            recent_trades = list(self.performance_data['trades'])[-100:]
            if not recent_trades:
                return []
            
            wins = sum(1 for t in recent_trades if t.get('pnl', 0) > 0)
            total = len([t for t in recent_trades if t.get('result') in ['win', 'loss']])
            
            if total > 0:
                return [wins / total]
            return []
        
        elif metric_name == 'execution_time':
            return list(self.performance_data['execution_times'])
        
        elif metric_name == 'slippage':
            return list(self.performance_data['slippages'])
        
        elif metric_name == 'risk_reward':
            return list(self.performance_data['risk_rewards'])
        
        return []
    
    def _perform_quality_checks(self, quality_metrics: Dict[str, Any]) -> Dict[str, bool]:
        """Perform quality control checks"""
        checks = {}
        
        # Check each metric against quality standards
        for metric_name, metric_data in quality_metrics.items():
            if isinstance(metric_data, dict) and 'cpk' in metric_data:
                checks[f"{metric_name}_quality"] = metric_data['cpk'] >= self.quality_config['min_cpk']
                checks[f"{metric_name}_optimal"] = metric_data['cpk'] >= self.quality_config['target_cpk']
        
        # Overall quality check
        all_metrics_available = all(
            isinstance(m, dict) and 'cpk' in m 
            for m in quality_metrics.values()
        )
        
        if all_metrics_available:
            avg_cpk = statistics.mean([
                m['cpk'] for m in quality_metrics.values() 
                if isinstance(m, dict) and 'cpk' in m
            ])
            checks['overall_quality'] = avg_cpk >= self.quality_config['min_cpk']
            checks['optimal_quality'] = avg_cpk >= self.quality_config['target_cpk']
        
        return checks
    
    def _check_alert_conditions(self, trade_data: Dict[str, Any], 
                               quality_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        
        # Check consecutive losses
        recent_trades = list(self.performance_data['trades'])[-10:]
        consecutive_losses = 0
        for trade in reversed(recent_trades):
            if trade.get('pnl', 0) < 0:
                consecutive_losses += 1
            else:
                break
        
        if consecutive_losses >= self.alert_thresholds['consecutive_losses']:
            alerts.append({
                'type': 'CONSECUTIVE_LOSSES',
                'severity': 'HIGH',
                'message': f"{consecutive_losses} consecutive losses detected",
                'value': consecutive_losses
            })
        
        # Check quality degradation
        for metric_name, metric_data in quality_metrics.items():
            if isinstance(metric_data, dict) and 'cpk' in metric_data:
                if metric_data['cpk'] < self.alert_thresholds['low_cpk']:
                    alerts.append({
                        'type': 'LOW_QUALITY',
                        'severity': 'MEDIUM',
                        'message': f"Low Cpk for {metric_name}: {metric_data['cpk']}",
                        'metric': metric_name,
                        'value': metric_data['cpk']
                    })
        
        # Check high slippage
        if trade_data.get('slippage', 0) > self.alert_thresholds['high_slippage_pips']:
            alerts.append({
                'type': 'HIGH_SLIPPAGE',
                'severity': 'MEDIUM',
                'message': f"High slippage: {trade_data['slippage']} pips",
                'value': trade_data['slippage']
            })
        
        return alerts
    
    def _determine_control_actions(self, quality_checks: Dict[str, bool], 
                                  alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Determine control actions based on quality and alerts"""
        actions = []
        
        # Check if trading should be disabled
        high_severity_alerts = [a for a in alerts if a['severity'] == 'HIGH']
        if high_severity_alerts:
            actions.append({
                'action': 'DISABLE_TRADING',
                'reason': 'High severity alerts detected',
                'alerts': high_severity_alerts
            })
        
        # Check if quality is degraded
        if not quality_checks.get('overall_quality', True):
            actions.append({
                'action': 'REDUCE_POSITION_SIZE',
                'reason': 'Quality below minimum standards',
                'reduction_factor': 0.5
            })
        
        # Check if system needs recalibration
        if not quality_checks.get('optimal_quality', True):
            actions.append({
                'action': 'RECALIBRATE_SYSTEM',
                'reason': 'Quality below optimal levels',
                'parameters': ['ml_model', 'risk_parameters']
            })
        
        return actions
    
    def _apply_control_actions(self, actions: List[Dict[str, Any]]):
        """Apply control actions"""
        for action in actions:
            if action['action'] == 'DISABLE_TRADING':
                self.control_state['trading_enabled'] = False
                self.control_state['quality_status'] = 'CRITICAL'
                logger.warning(f"Trading disabled: {action['reason']}")
            
            elif action['action'] == 'REDUCE_POSITION_SIZE':
                # This would be communicated to Risk Engine
                logger.warning(f"Position size reduced: {action['reason']}")
            
            elif action['action'] == 'RECALIBRATE_SYSTEM':
                # Trigger system recalibration
                logger.info(f"System recalibration triggered: {action['reason']}")
        
        # Send alerts if callback is configured
        if self.alert_callback and actions:
            self.alert_callback(actions)
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        trades = list(self.performance_data['trades'])
        if not trades:
            return {'status': 'no_data'}
        
        completed_trades = [t for t in trades if t.get('result') in ['win', 'loss']]
        if not completed_trades:
            return {'status': 'no_completed_trades'}
        
        wins = sum(1 for t in completed_trades if t.get('pnl', 0) > 0)
        losses = len(completed_trades) - wins
        total_pnl = sum(t.get('pnl', 0) for t in completed_trades)
        
        return {
            'total_trades': len(completed_trades),
            'wins': wins,
            'losses': losses,
            'win_rate': round(wins / len(completed_trades), 3) if completed_trades else 0,
            'total_pnl': round(total_pnl, 2),
            'average_pnl': round(total_pnl / len(completed_trades), 2) if completed_trades else 0,
            'quality_status': self.control_state['quality_status']
        }
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health"""
        health_score = 100.0
        issues = []
        
        # Check trading status
        if not self.control_state['trading_enabled']:
            health_score -= 50
            issues.append('Trading disabled')
        
        # Check quality metrics
        if self.control_state['quality_status'] != 'OPTIMAL':
            health_score -= 20
            issues.append(f"Quality status: {self.control_state['quality_status']}")
        
        # Check for recent alerts
        if self.control_state['alert_active']:
            health_score -= 10
            issues.append('Active alerts')
        
        return {
            'score': max(0, health_score),
            'status': 'HEALTHY' if health_score >= 80 else 'DEGRADED' if health_score >= 50 else 'CRITICAL',
            'issues': issues
        }