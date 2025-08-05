"""
Six Sigma Quality Monitor for MikroBot FastVersion
Implements statistical process control and Cp/Cpk monitoring for trading system

Integrates with LeanSixSigmaMasterBlackBelt agent for comprehensive quality management
Author: ProductOwnerAgent + LeanSixSigmaMasterBlackBelt
Created: 2025-08-03
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import statistics
from collections import deque, defaultdict
from enum import Enum

logger = logging.getLogger(__name__)


class QualityAlert(Enum):
    """Quality alert severity levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"         # 24-hour response
    MEDIUM = "medium"     # 7-day response
    LOW = "low"          # 30-day response


@dataclass
class QualityMetric:
    """Statistical quality metric tracking"""
    name: str
    value: float
    target: float
    upper_spec_limit: float
    lower_spec_limit: float
    upper_control_limit: float
    lower_control_limit: float
    cp: float
    cpk: float
    sigma_level: float
    in_control: bool
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class QualityViolation:
    """Quality violation record"""
    timestamp: datetime
    metric_name: str
    value: float
    violation_type: str  # "out_of_spec", "out_of_control", "trend"
    severity: QualityAlert
    financial_impact: float
    corrective_action: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['severity'] = self.severity.value
        return result


class SixSigmaQualityMonitor:
    """
    Six Sigma Quality Monitor for MikroBot FastVersion
    
    Implements statistical process control with:
    - Real-time Cp/Cpk monitoring
    - Control chart analysis
    - Quality gate enforcement
    - MikroBot_BOS_M5M1 strategy compliance tracking
    - Cross-agent quality coordination
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "src/config/quality_standards.json"
        
        # Quality standards for MikroBot trading system
        self.quality_standards = {
            'execution_latency_ms': {
                'target': 50.0,
                'upper_spec_limit': 100.0,
                'lower_spec_limit': 0.0,
                'sigma_target': 6.0,
                'weight': 0.2
            },
            'signal_accuracy': {
                'target': 0.85,
                'upper_spec_limit': 1.0,
                'lower_spec_limit': 0.7,
                'sigma_target': 5.0,
                'weight': 0.25
            },
            'risk_adherence': {
                'target': 0.99,
                'upper_spec_limit': 1.0,
                'lower_spec_limit': 0.95,
                'sigma_target': 6.0,
                'weight': 0.20
            },
            'trade_execution_success': {
                'target': 0.98,
                'upper_spec_limit': 1.0,
                'lower_spec_limit': 0.90,
                'sigma_target': 6.0,
                'weight': 0.15
            },
            'slippage_pips': {
                'target': 0.5,
                'upper_spec_limit': 2.0,
                'lower_spec_limit': 0.0,
                'sigma_target': 5.0,
                'weight': 0.1
            },
            'bos_strategy_compliance': {
                'target': 1.0,
                'upper_spec_limit': 1.0,
                'lower_spec_limit': 0.95,
                'sigma_target': 6.0,
                'weight': 0.1
            }
        }
        
        # Control chart data storage
        self.control_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Quality metrics history
        self.quality_metrics: Dict[str, QualityMetric] = {}
        self.quality_violations: List[QualityViolation] = []
        
        # Statistical tracking
        self.control_limits: Dict[str, Dict[str, float]] = {}
        
        # Integration with LeanSixSigmaMasterBlackBelt
        self.sixsigma_agent = None
        
        # Quality monitoring status
        self.monitoring_active = False
        self.last_quality_check = None
        
        # Alert thresholds
        self.alert_thresholds = {
            'cp_critical': 1.0,
            'cpk_critical': 1.0,
            'out_of_control_points': 3,
            'trend_points': 7
        }
        
        logger.info("Six Sigma Quality Monitor initialized")
    
    def set_sixsigma_integration(self, sixsigma_agent):
        """Set integration with LeanSixSigmaMasterBlackBelt agent"""
        self.sixsigma_agent = sixsigma_agent
        logger.info("Six Sigma agent integration established")
    
    async def start_monitoring(self) -> bool:
        """Start continuous quality monitoring"""
        try:
            self.monitoring_active = True
            self.last_quality_check = datetime.utcnow()
            
            # Initialize control limits
            await self._initialize_control_limits()
            
            logger.info("Six Sigma quality monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start quality monitoring: {str(e)}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop quality monitoring"""
        try:
            self.monitoring_active = False
            logger.info("Six Sigma quality monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop quality monitoring: {str(e)}")
            return False
    
    async def record_metric(self, metric_name: str, value: float, timestamp: Optional[datetime] = None) -> bool:
        """Record a quality metric measurement"""
        try:
            if not self.monitoring_active:
                return False
                
            timestamp = timestamp or datetime.utcnow()
            
            # Add to control chart data
            self.control_data[metric_name].append(value)
            
            # Calculate statistical metrics
            quality_metric = await self._calculate_quality_metric(metric_name, value, timestamp)
            
            if quality_metric:
                self.quality_metrics[metric_name] = quality_metric
                
                # Check for quality violations
                await self._check_quality_violations(quality_metric)
                
                # Update control limits if needed
                await self._update_control_limits(metric_name)
                
                logger.debug(f"Recorded quality metric: {metric_name} = {value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to record metric {metric_name}: {str(e)}")
            return False
    
    async def _calculate_quality_metric(self, metric_name: str, value: float, timestamp: datetime) -> Optional[QualityMetric]:
        """Calculate comprehensive quality metrics"""
        try:
            if metric_name not in self.quality_standards:
                logger.warning(f"Unknown quality metric: {metric_name}")
                return None
            
            standard = self.quality_standards[metric_name]
            data_points = list(self.control_data[metric_name])
            
            if len(data_points) < 5:  # Need minimum data for statistical analysis
                return None
            
            # Calculate control limits
            mean_val = np.mean(data_points)
            std_dev = np.std(data_points, ddof=1)
            
            ucl = mean_val + 3 * std_dev
            lcl = max(0, mean_val - 3 * std_dev)  # Non-negative for most trading metrics
            
            # Calculate capability indices
            cp = self._calculate_cp(data_points, standard['upper_spec_limit'], standard['lower_spec_limit'])
            cpk = self._calculate_cpk(data_points, standard['upper_spec_limit'], standard['lower_spec_limit'])
            
            # Calculate sigma level
            sigma_level = min(6.0, cpk + 1.5) if cpk > 0 else 0.0
            
            # Check if in control
            in_control = standard['lower_spec_limit'] <= value <= standard['upper_spec_limit']
            in_control = in_control and lcl <= value <= ucl
            
            quality_metric = QualityMetric(
                name=metric_name,
                value=value,
                target=standard['target'],
                upper_spec_limit=standard['upper_spec_limit'],
                lower_spec_limit=standard['lower_spec_limit'],
                upper_control_limit=ucl,
                lower_control_limit=lcl,
                cp=cp,
                cpk=cpk,
                sigma_level=sigma_level,
                in_control=in_control,
                timestamp=timestamp
            )
            
            return quality_metric
            
        except Exception as e:
            logger.error(f"Failed to calculate quality metric for {metric_name}: {str(e)}")
            return None
    
    def _calculate_cp(self, data: List[float], usl: float, lsl: float) -> float:
        """Calculate Process Capability (Cp)"""
        if len(data) < 2:
            return 0.0
        
        std_dev = np.std(data, ddof=1)
        if std_dev == 0:
            return float('inf')
        
        return (usl - lsl) / (6 * std_dev)
    
    def _calculate_cpk(self, data: List[float], usl: float, lsl: float) -> float:
        """Calculate Process Capability Index (Cpk)"""
        if len(data) < 2:
            return 0.0
        
        mean_val = np.mean(data)
        std_dev = np.std(data, ddof=1)
        
        if std_dev == 0:
            return float('inf')
        
        cpu = (usl - mean_val) / (3 * std_dev)
        cpl = (mean_val - lsl) / (3 * std_dev)
        
        return min(cpu, cpl)
    
    async def _check_quality_violations(self, metric: QualityMetric) -> None:
        """Check for quality violations and generate alerts"""
        try:
            violations = []
            
            # Check specification limits
            if metric.value > metric.upper_spec_limit or metric.value < metric.lower_spec_limit:
                violation = QualityViolation(
                    timestamp=metric.timestamp,
                    metric_name=metric.name,
                    value=metric.value,
                    violation_type="out_of_spec",
                    severity=QualityAlert.HIGH,
                    financial_impact=self._estimate_violation_cost(metric.name, "out_of_spec"),
                    corrective_action=f"Immediate process adjustment required for {metric.name}"
                )
                violations.append(violation)
            
            # Check control limits
            if not metric.in_control:
                violation = QualityViolation(
                    timestamp=metric.timestamp,
                    metric_name=metric.name,
                    value=metric.value,
                    violation_type="out_of_control",
                    severity=QualityAlert.MEDIUM,
                    financial_impact=self._estimate_violation_cost(metric.name, "out_of_control"),
                    corrective_action=f"Statistical control investigation required for {metric.name}"
                )
                violations.append(violation)
            
            # Check process capability
            if metric.cpk < self.alert_thresholds['cpk_critical']:
                violation = QualityViolation(
                    timestamp=metric.timestamp,
                    metric_name=metric.name,
                    value=metric.cpk,
                    violation_type="poor_capability",
                    severity=QualityAlert.CRITICAL if metric.cpk < 1.0 else QualityAlert.HIGH,
                    financial_impact=self._estimate_violation_cost(metric.name, "poor_capability"),
                    corrective_action=f"Process improvement required for {metric.name} (Cpk: {metric.cpk:.2f})"
                )
                violations.append(violation)
            
            # Record violations
            for violation in violations:
                self.quality_violations.append(violation)
                await self._escalate_violation(violation)
            
            # Limit violation history
            if len(self.quality_violations) > 1000:
                self.quality_violations = self.quality_violations[-1000:]
            
        except Exception as e:
            logger.error(f"Failed to check quality violations: {str(e)}")
    
    def _estimate_violation_cost(self, metric_name: str, violation_type: str) -> float:
        """Estimate financial impact of quality violation"""
        
        # Base cost multipliers for different metrics
        base_costs = {
            'execution_latency_ms': 100.0,
            'signal_accuracy': 1000.0,
            'risk_adherence': 2000.0,
            'trade_execution_success': 500.0,
            'slippage_pips': 200.0,
            'bos_strategy_compliance': 1500.0
        }
        
        # Violation type multipliers
        violation_multipliers = {
            'out_of_spec': 2.0,
            'out_of_control': 1.5,
            'poor_capability': 3.0
        }
        
        base_cost = base_costs.get(metric_name, 500.0)
        multiplier = violation_multipliers.get(violation_type, 1.0)
        
        return base_cost * multiplier
    
    async def _escalate_violation(self, violation: QualityViolation) -> None:
        """Escalate quality violation to appropriate stakeholders"""
        try:
            # Log violation
            logger.warning(f"Quality violation: {violation.metric_name} - {violation.violation_type} "
                          f"(${violation.financial_impact:.0f} impact)")
            
            # Integrate with Six Sigma agent if available
            if self.sixsigma_agent:
                await self._notify_sixsigma_agent(violation)
            
            # Save violation to file for audit trail
            await self._save_violation_record(violation)
            
        except Exception as e:
            logger.error(f"Failed to escalate violation: {str(e)}")
    
    async def _notify_sixsigma_agent(self, violation: QualityViolation) -> None:
        """Notify Six Sigma agent of quality violation"""
        try:
            if hasattr(self.sixsigma_agent, 'handle_quality_violation'):
                await self.sixsigma_agent.handle_quality_violation(violation)
            
        except Exception as e:
            logger.error(f"Failed to notify Six Sigma agent: {str(e)}")
    
    async def _save_violation_record(self, violation: QualityViolation) -> None:
        """Save violation record to audit file"""
        try:
            violations_file = Path("logs/quality_violations.json")
            violations_file.parent.mkdir(exist_ok=True)
            
            # Load existing violations
            violations_data = []
            if violations_file.exists():
                with open(violations_file, 'r') as f:
                    violations_data = json.load(f)
            
            # Add new violation
            violations_data.append(violation.to_dict())
            
            # Keep only last 1000 violations
            if len(violations_data) > 1000:
                violations_data = violations_data[-1000:]
            
            # Save updated violations
            with open(violations_file, 'w') as f:
                json.dump(violations_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save violation record: {str(e)}")
    
    async def _initialize_control_limits(self) -> None:
        """Initialize statistical control limits"""
        try:
            for metric_name in self.quality_standards.keys():
                self.control_limits[metric_name] = {
                    'ucl': 0.0,
                    'lcl': 0.0,
                    'mean': 0.0,
                    'std': 0.0,
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            logger.info("Control limits initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize control limits: {str(e)}")
    
    async def _update_control_limits(self, metric_name: str) -> None:
        """Update control limits based on recent data"""
        try:
            data_points = list(self.control_data[metric_name])
            
            if len(data_points) >= 20:  # Minimum for reliable control limits
                mean_val = np.mean(data_points)
                std_dev = np.std(data_points, ddof=1)
                
                self.control_limits[metric_name] = {
                    'ucl': mean_val + 3 * std_dev,
                    'lcl': max(0, mean_val - 3 * std_dev),
                    'mean': mean_val,
                    'std': std_dev,
                    'last_updated': datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Failed to update control limits for {metric_name}: {str(e)}")
    
    async def get_quality_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive quality dashboard data"""
        try:
            current_time = datetime.utcnow()
            
            # Calculate overall quality score
            overall_cp = []
            overall_cpk = []
            
            for metric_name, metric in self.quality_metrics.items():
                if metric.cp != float('inf'):
                    overall_cp.append(metric.cp)
                if metric.cpk != float('inf'):
                    overall_cpk.append(metric.cpk)
            
            avg_cp = np.mean(overall_cp) if overall_cp else 0.0
            avg_cpk = np.mean(overall_cpk) if overall_cpk else 0.0
            overall_sigma = min(6.0, avg_cpk + 1.5) if avg_cpk > 0 else 0.0
            
            # Quality grade
            if overall_sigma >= 6.0:
                quality_grade = "Six Sigma (World Class)"
                grade_color = "green"
            elif overall_sigma >= 5.0:
                quality_grade = "Five Sigma (Excellent)"
                grade_color = "blue"
            elif overall_sigma >= 4.0:
                quality_grade = "Four Sigma (Good)"
                grade_color = "yellow"
            elif overall_sigma >= 3.0:
                quality_grade = "Three Sigma (Industry Average)"
                grade_color = "orange"
            else:
                quality_grade = "Below Three Sigma (Poor)"
                grade_color = "red"
            
            # Recent violations
            recent_violations = [v for v in self.quality_violations 
                               if (current_time - v.timestamp).days <= 1]
            
            # Metrics in control
            in_control_count = sum(1 for m in self.quality_metrics.values() if m.in_control)
            total_metrics = len(self.quality_metrics)
            control_percentage = (in_control_count / max(1, total_metrics)) * 100
            
            dashboard = {
                'timestamp': current_time.isoformat(),
                'monitoring_status': 'active' if self.monitoring_active else 'inactive',
                'overall_quality': {
                    'cp': avg_cp,
                    'cpk': avg_cpk,
                    'sigma_level': overall_sigma,
                    'quality_grade': quality_grade,
                    'grade_color': grade_color,
                    'dpmo': self._calculate_dpmo(overall_sigma),
                    'in_control_percentage': control_percentage
                },
                'metric_details': {
                    name: metric.to_dict() 
                    for name, metric in self.quality_metrics.items()
                },
                'recent_violations': {
                    'count_24h': len(recent_violations),
                    'total_cost_24h': sum(v.financial_impact for v in recent_violations),
                    'violations': [v.to_dict() for v in recent_violations[-10:]]
                },
                'bos_strategy_compliance': {
                    'current_compliance': self.quality_metrics.get('bos_strategy_compliance', {}).get('value', 0.0),
                    'target_compliance': 1.0,
                    'compliance_sigma': self.quality_metrics.get('bos_strategy_compliance', {}).get('sigma_level', 0.0)
                },
                'control_status': {
                    'metrics_in_control': in_control_count,
                    'total_metrics': total_metrics,
                    'control_percentage': control_percentage,
                    'out_of_control_metrics': [
                        name for name, metric in self.quality_metrics.items() 
                        if not metric.in_control
                    ]
                },
                'quality_targets': {
                    'cp_target': 3.0,
                    'cpk_target': 3.0,
                    'sigma_target': 6.0,
                    'target_achievement': {
                        'cp_achieved': avg_cp >= 3.0,
                        'cpk_achieved': avg_cpk >= 3.0,
                        'sigma_achieved': overall_sigma >= 6.0
                    }
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to generate quality dashboard: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    def _calculate_dpmo(self, sigma_level: float) -> float:
        """Calculate Defects Per Million Opportunities"""
        dpmo_mapping = {
            6.0: 3.4,
            5.0: 233,
            4.0: 6210,
            3.0: 66807,
            2.0: 308537,
            1.0: 690000
        }
        
        closest_sigma = min(dpmo_mapping.keys(), key=lambda x: abs(x - sigma_level))
        return dpmo_mapping[closest_sigma]
    
    async def validate_bos_strategy_compliance(self, trade_data: Dict[str, Any]) -> bool:
        """Validate MikroBot_BOS_M5M1 strategy compliance for a trade"""
        try:
            # Check required BOS strategy parameters
            required_params = ['timeframe', 'signal_type', 'pip_trigger', 'break_level', 'retest_confirmation']
            
            compliance_score = 0.0
            total_checks = len(required_params)
            
            for param in required_params:
                if param in trade_data:
                    # Validate specific parameter compliance
                    if self._validate_bos_parameter(param, trade_data[param]):
                        compliance_score += 1.0
            
            compliance_ratio = compliance_score / total_checks
            
            # Record compliance metric
            await self.record_metric('bos_strategy_compliance', compliance_ratio)
            
            # Return true if compliance is above threshold
            return compliance_ratio >= 0.95
            
        except Exception as e:
            logger.error(f"Failed to validate BOS strategy compliance: {str(e)}")
            return False
    
    def _validate_bos_parameter(self, param: str, value: Any) -> bool:
        """Validate specific BOS strategy parameter"""
        try:
            validation_rules = {
                'timeframe': lambda x: x in ['M5', 'M1'],
                'signal_type': lambda x: x == 'BOS_BREAK_RETEST',
                'pip_trigger': lambda x: isinstance(x, (int, float)) and 0.1 <= x <= 0.5,
                'break_level': lambda x: isinstance(x, (int, float)),
                'retest_confirmation': lambda x: isinstance(x, bool)
            }
            
            rule = validation_rules.get(param)
            if rule:
                return rule(value)
            
            return True  # Unknown parameters pass by default
            
        except Exception as e:
            logger.error(f"Failed to validate BOS parameter {param}: {str(e)}")
            return False
    
    async def get_quality_report(self, period_days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        try:
            current_time = datetime.utcnow()
            period_start = current_time - timedelta(days=period_days)
            
            # Filter violations in period
            period_violations = [
                v for v in self.quality_violations 
                if v.timestamp >= period_start
            ]
            
            # Calculate period metrics
            dashboard = await self.get_quality_dashboard()
            
            report = {
                'report_period': {
                    'start': period_start.isoformat(),
                    'end': current_time.isoformat(),
                    'days': period_days
                },
                'quality_summary': dashboard['overall_quality'],
                'period_performance': {
                    'total_violations': len(period_violations),
                    'violation_cost': sum(v.financial_impact for v in period_violations),
                    'critical_violations': len([v for v in period_violations if v.severity == QualityAlert.CRITICAL]),
                    'most_problematic_metric': self._get_most_problematic_metric(period_violations),
                    'improvement_trend': self._calculate_improvement_trend()
                },
                'compliance_analysis': {
                    'bos_strategy_compliance': dashboard['bos_strategy_compliance'],
                    'control_chart_compliance': dashboard['control_status'],
                    'specification_compliance': self._calculate_spec_compliance()
                },
                'recommendations': self._generate_quality_recommendations(dashboard, period_violations),
                'financial_impact': {
                    'period_cost_of_poor_quality': sum(v.financial_impact for v in period_violations),
                    'annualized_impact': sum(v.financial_impact for v in period_violations) * (365 / period_days),
                    'improvement_opportunity': self._calculate_improvement_opportunity()
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate quality report: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    def _get_most_problematic_metric(self, violations: List[QualityViolation]) -> str:
        """Identify the most problematic metric"""
        metric_counts = defaultdict(int)
        
        for violation in violations:
            metric_counts[violation.metric_name] += 1
        
        if metric_counts:
            return max(metric_counts.items(), key=lambda x: x[1])[0]
        
        return "None"
    
    def _calculate_improvement_trend(self) -> str:
        """Calculate quality improvement trend"""
        try:
            if len(self.quality_violations) < 10:
                return "Insufficient data"
            
            # Compare recent violations to historical
            recent_violations = self.quality_violations[-5:]
            historical_violations = self.quality_violations[-10:-5]
            
            recent_avg = len(recent_violations) / 5
            historical_avg = len(historical_violations) / 5
            
            if recent_avg < historical_avg * 0.8:
                return "Improving"
            elif recent_avg > historical_avg * 1.2:
                return "Degrading"
            else:
                return "Stable"
                
        except Exception as e:
            logger.error(f"Failed to calculate improvement trend: {str(e)}")
            return "Unknown"
    
    def _calculate_spec_compliance(self) -> Dict[str, float]:
        """Calculate specification compliance for each metric"""
        compliance = {}
        
        for name, metric in self.quality_metrics.items():
            if metric.lower_spec_limit <= metric.value <= metric.upper_spec_limit:
                compliance[name] = 1.0
            else:
                compliance[name] = 0.0
        
        return compliance
    
    def _generate_quality_recommendations(self, dashboard: Dict[str, Any], violations: List[QualityViolation]) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        # Overall quality recommendations
        overall_sigma = dashboard['overall_quality']['sigma_level']
        if overall_sigma < 3.0:
            recommendations.append("CRITICAL: Implement emergency quality improvement program")
        elif overall_sigma < 4.0:
            recommendations.append("HIGH: Focus on process standardization and control")
        elif overall_sigma < 6.0:
            recommendations.append("MEDIUM: Continue process optimization for Six Sigma level")
        
        # Metric-specific recommendations
        for name, metric in dashboard['metric_details'].items():
            if metric['cpk'] < 1.0:
                recommendations.append(f"CRITICAL: {name} requires immediate process capability improvement")
            elif metric['cpk'] < 1.67:
                recommendations.append(f"HIGH: {name} needs process optimization")
        
        # Violation-based recommendations
        if len(violations) > 5:
            recommendations.append("Implement more stringent process controls")
        
        # BOS strategy recommendations
        bos_compliance = dashboard['bos_strategy_compliance']['current_compliance']
        if bos_compliance < 0.95:
            recommendations.append("Improve MikroBot_BOS_M5M1 strategy standardization")
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _calculate_improvement_opportunity(self) -> float:
        """Calculate financial improvement opportunity"""
        try:
            # Calculate potential savings from achieving Six Sigma level
            current_sigma = np.mean([m.sigma_level for m in self.quality_metrics.values()])
            current_dpmo = self._calculate_dpmo(current_sigma)
            target_dpmo = 3.4  # Six Sigma level
            
            improvement_factor = current_dpmo / target_dpmo
            
            # Estimate annual savings opportunity
            recent_violations = self.quality_violations[-30:]  # Last 30 violations
            if recent_violations:
                avg_violation_cost = np.mean([v.financial_impact for v in recent_violations])
                annual_violations = len(recent_violations) * (365 / 30)
                annual_cost = annual_violations * avg_violation_cost
                improvement_opportunity = annual_cost * (1 - 1/improvement_factor)
                return improvement_opportunity
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Failed to calculate improvement opportunity: {str(e)}")
            return 0.0


# Factory function for integration
def create_quality_monitor(config_path: Optional[str] = None) -> SixSigmaQualityMonitor:
    """Create and configure Six Sigma Quality Monitor"""
    return SixSigmaQualityMonitor(config_path)


# Integration test function
async def test_quality_monitor():
    """Test the quality monitoring system"""
    monitor = create_quality_monitor()
    
    # Start monitoring
    await monitor.start_monitoring()
    
    # Record some test metrics
    test_metrics = [
        ('execution_latency_ms', 45.0),
        ('signal_accuracy', 0.87),
        ('risk_adherence', 0.98),
        ('trade_execution_success', 0.99),
        ('slippage_pips', 0.3),
        ('bos_strategy_compliance', 1.0)
    ]
    
    for metric_name, value in test_metrics:
        await monitor.record_metric(metric_name, value)
    
    # Get quality dashboard
    dashboard = await monitor.get_quality_dashboard()
    print(f"Quality Dashboard: {json.dumps(dashboard, indent=2)}")
    
    # Generate quality report
    report = await monitor.get_quality_report()
    print(f"Quality Report: {json.dumps(report, indent=2)}")
    
    return monitor


if __name__ == "__main__":
    # Run test
    asyncio.run(test_quality_monitor())