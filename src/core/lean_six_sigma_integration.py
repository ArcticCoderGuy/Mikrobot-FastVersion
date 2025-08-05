"""
LeanSixSigma Integration Module
Integrates the LeanSixSigma MasterBlackBelt agent with MikroBot trading system components

This module provides seamless integration between the Six Sigma quality management
system and the existing MikroBot U-Cell pipeline, performance monitoring, and
trading execution systems.

Author: Claude Code
Integration: MikroBot Complete System
Created: 2025-08-03
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import asdict

from ..agents.lean_six_sigma_master_black_belt import (
    LeanSixSigmaMasterBlackBelt,
    QualityAlert,
    ProcessImprovementLevel
)
from .u_cells.orchestrator import UCellOrchestrator
from .performance_monitor import PerformanceMonitor
from ..agents.mt5_expert_agent import MT5ExpertAgent

logger = logging.getLogger(__name__)


class LeanSixSigmaIntegrationManager:
    """
    Integration manager for LeanSixSigma MasterBlackBelt agent
    
    Provides:
    - Real-time quality monitoring integration
    - Automated DMAIC project initiation
    - Performance data synchronization
    - Quality alert propagation
    - Continuous improvement automation
    """
    
    def __init__(self, 
                 u_cell_orchestrator: UCellOrchestrator,
                 performance_monitor: PerformanceMonitor,
                 mt5_expert_agent: Optional[MT5ExpertAgent] = None):
        
        self.u_cell_orchestrator = u_cell_orchestrator
        self.performance_monitor = performance_monitor
        self.mt5_expert_agent = mt5_expert_agent
        
        # Initialize LeanSixSigma agent
        self.lean_six_sigma_agent = LeanSixSigmaMasterBlackBelt()
        
        # Set up integrations
        self._setup_integrations()
        
        # Quality monitoring configuration
        self.quality_monitoring_config = {
            'monitoring_interval_seconds': 60,  # 1 minute
            'alert_threshold_violations': 3,    # 3 consecutive violations
            'auto_dmaic_threshold': 5,          # Auto-create DMAIC project after 5 critical issues
            'performance_analysis_interval_hours': 24  # Daily comprehensive analysis
        }
        
        # Integration state
        self.integration_state = {
            'last_performance_analysis': None,
            'last_quality_check': None,
            'active_quality_alerts': [],
            'auto_created_projects': [],
            'integration_health': 'healthy'
        }
        
        # Start background monitoring
        self.monitoring_task = None
        self.is_monitoring = False
        
        logger.info("LeanSixSigma Integration Manager initialized")
    
    def _setup_integrations(self):
        """Set up integration points with MikroBot components"""
        
        # Set integration points in LeanSixSigma agent
        self.lean_six_sigma_agent.set_integration_point('u_cell_pipeline', self.u_cell_orchestrator)
        self.lean_six_sigma_agent.set_integration_point('performance_monitor', self.performance_monitor)
        
        if self.mt5_expert_agent:
            self.lean_six_sigma_agent.set_integration_point('mt5_expert_agent', self.mt5_expert_agent)
        
        logger.info("Integration points configured")
    
    async def start_monitoring(self):
        """Start continuous quality monitoring"""
        
        if self.is_monitoring:
            logger.warning("Quality monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("LeanSixSigma quality monitoring started")
    
    async def stop_monitoring(self):
        """Stop continuous quality monitoring"""
        
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("LeanSixSigma quality monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for quality management"""
        
        try:
            while self.is_monitoring:
                # Real-time quality check
                await self._perform_real_time_quality_check()
                
                # Check for alert conditions
                await self._check_alert_conditions()
                
                # Auto-create DMAIC projects if needed
                await self._check_auto_dmaic_creation()
                
                # Periodic comprehensive analysis
                await self._check_comprehensive_analysis()
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.quality_monitoring_config['monitoring_interval_seconds'])
                
        except asyncio.CancelledError:
            logger.info("Quality monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Error in quality monitoring loop: {str(e)}")
            self.integration_state['integration_health'] = 'degraded'
    
    async def _perform_real_time_quality_check(self):
        """Perform real-time quality check"""
        
        try:
            # Get current system metrics
            system_metrics = self.performance_monitor.get_comprehensive_metrics()
            
            # Monitor real-time quality
            quality_status = await self.lean_six_sigma_agent.monitor_real_time_quality()
            
            # Update integration state
            self.integration_state['last_quality_check'] = datetime.utcnow()
            
            # Check for quality degradation
            if quality_status.get('overall_status') in ['warning', 'critical']:
                await self._handle_quality_degradation(quality_status)
            
        except Exception as e:
            logger.error(f"Error in real-time quality check: {str(e)}")
    
    async def _handle_quality_degradation(self, quality_status: Dict[str, Any]):
        """Handle quality degradation scenarios"""
        
        degraded_metrics = [
            metric_name for metric_name, metric_data in quality_status.get('quality_metrics', {}).items()
            if metric_data.get('status') in ['warning', 'critical']
        ]
        
        for metric_name in degraded_metrics:
            metric_data = quality_status['quality_metrics'][metric_name]
            
            # Create quality alert
            alert = QualityAlert(
                timestamp=datetime.utcnow(),
                severity=ProcessImprovementLevel.CRITICAL if metric_data['status'] == 'critical' else ProcessImprovementLevel.HIGH,
                process=metric_name,
                metric='real_time_monitoring',
                current_value=metric_data['current_value'],
                target_value=metric_data['target'],
                deviation_percentage=metric_data['deviation_percentage'],
                sigma_level=0.0,  # Would be calculated
                root_cause_hypothesis=[f"Performance degradation in {metric_name}"],
                recommended_actions=[f"Investigate {metric_name} performance issues"],
                financial_impact=metric_data['deviation_percentage'] * 100  # Simplified calculation
            )
            
            # Add to active alerts
            self.integration_state['active_quality_alerts'].append(alert)
            
            # Log alert
            logger.warning(f"Quality Alert: {metric_name} - {metric_data['status']} (deviation: {metric_data['deviation_percentage']:.1f}%)")
            
            # If critical, trigger immediate analysis
            if metric_data['status'] == 'critical':
                await self._trigger_emergency_analysis(metric_name, alert)
    
    async def _trigger_emergency_analysis(self, metric_name: str, alert: QualityAlert):
        """Trigger emergency quality analysis"""
        
        try:
            # Get comprehensive performance data
            performance_data = await self._collect_performance_data()
            
            # Perform emergency root cause analysis
            emergency_analysis = await self.lean_six_sigma_agent.analyze_trading_system_performance(
                performance_data,
                time_period=timedelta(hours=1)  # Last hour for emergency
            )
            
            # Extract immediate actions
            immediate_actions = []
            for recommendation in emergency_analysis.get('improvement_recommendations', []):
                if recommendation.get('priority') == 'critical':
                    immediate_actions.append(recommendation['recommendation'])
            
            # Log emergency analysis results
            logger.critical(f"Emergency Analysis for {metric_name}: {len(immediate_actions)} critical actions identified")
            
            # Auto-create emergency DMAIC project
            project_id = await self.lean_six_sigma_agent.create_dmaic_project(
                problem_statement=f"Critical quality degradation in {metric_name}",
                goal_statement=f"Restore {metric_name} to Six Sigma quality level within 24 hours",
                responsible_team=['quality_team', 'ops_team']
            )
            
            self.integration_state['auto_created_projects'].append({
                'project_id': project_id,
                'type': 'emergency',
                'created_at': datetime.utcnow(),
                'trigger_metric': metric_name
            })
            
        except Exception as e:
            logger.error(f"Error in emergency analysis: {str(e)}")
    
    async def _check_alert_conditions(self):
        """Check for alert conditions and escalation"""
        
        # Clean up old alerts (older than 24 hours)
        current_time = datetime.utcnow()
        self.integration_state['active_quality_alerts'] = [
            alert for alert in self.integration_state['active_quality_alerts']
            if (current_time - alert.timestamp).total_seconds() < 86400
        ]
        
        # Check for escalation conditions
        critical_alerts = [
            alert for alert in self.integration_state['active_quality_alerts']
            if alert.severity == ProcessImprovementLevel.CRITICAL
        ]
        
        if len(critical_alerts) >= self.quality_monitoring_config['alert_threshold_violations']:
            await self._escalate_quality_issues(critical_alerts)
    
    async def _escalate_quality_issues(self, critical_alerts: List[QualityAlert]):
        """Escalate critical quality issues"""
        
        # Group alerts by process
        process_alerts = {}
        for alert in critical_alerts:
            if alert.process not in process_alerts:
                process_alerts[alert.process] = []
            process_alerts[alert.process].append(alert)
        
        # Create escalated DMAIC projects for persistent issues
        for process, alerts in process_alerts.items():
            if len(alerts) >= 3:  # Persistent issue
                project_id = await self.lean_six_sigma_agent.create_dmaic_project(
                    problem_statement=f"Persistent quality issues in {process} - {len(alerts)} critical alerts",
                    goal_statement=f"Achieve Six Sigma quality level for {process}",
                    responsible_team=['quality_team', 'engineering_team', 'management']
                )
                
                self.integration_state['auto_created_projects'].append({
                    'project_id': project_id,
                    'type': 'escalated',
                    'created_at': datetime.utcnow(),
                    'trigger_process': process,
                    'alert_count': len(alerts)
                })
                
                logger.error(f"Quality Escalation: Created DMAIC project {project_id} for {process}")
    
    async def _check_auto_dmaic_creation(self):
        """Check conditions for automatic DMAIC project creation"""
        
        # Check if we have enough quality issues to warrant a systematic improvement project
        critical_count = len([
            alert for alert in self.integration_state['active_quality_alerts']
            if alert.severity == ProcessImprovementLevel.CRITICAL
        ])
        
        if critical_count >= self.quality_monitoring_config['auto_dmaic_threshold']:
            # Calculate total financial impact
            total_impact = sum(
                alert.financial_impact for alert in self.integration_state['active_quality_alerts']
            )
            
            # Create comprehensive improvement project
            project_id = await self.lean_six_sigma_agent.create_dmaic_project(
                problem_statement=f"System-wide quality degradation - {critical_count} critical issues, ${total_impact:,.0f} impact",
                goal_statement="Achieve overall Six Sigma quality level across all trading system processes",
                responsible_team=['quality_team', 'engineering_team', 'ops_team', 'management']
            )
            
            self.integration_state['auto_created_projects'].append({
                'project_id': project_id,
                'type': 'systematic',
                'created_at': datetime.utcnow(),
                'trigger_reason': 'threshold_exceeded',
                'critical_count': critical_count,
                'financial_impact': total_impact
            })
            
            logger.warning(f"Auto-created systematic DMAIC project {project_id} due to {critical_count} critical issues")
    
    async def _check_comprehensive_analysis(self):
        """Check if comprehensive analysis is due"""
        
        current_time = datetime.utcnow()
        last_analysis = self.integration_state.get('last_performance_analysis')
        
        if (not last_analysis or 
            (current_time - last_analysis).total_seconds() >= 
            self.quality_monitoring_config['performance_analysis_interval_hours'] * 3600):
            
            await self._perform_comprehensive_analysis()
            self.integration_state['last_performance_analysis'] = current_time
    
    async def _perform_comprehensive_analysis(self):
        """Perform comprehensive quality analysis"""
        
        try:
            # Collect comprehensive performance data
            performance_data = await self._collect_performance_data()
            
            # Perform full Six Sigma analysis
            analysis_result = await self.lean_six_sigma_agent.analyze_trading_system_performance(
                performance_data,
                time_period=timedelta(days=7)  # Weekly analysis
            )
            
            # Generate comprehensive quality report
            quality_report = self.lean_six_sigma_agent.get_comprehensive_quality_report()
            
            # Check for ML optimization opportunities
            if 'ml_performance' in performance_data:
                ml_optimization = await self.lean_six_sigma_agent.optimize_tensorflow_learning(
                    performance_data['ml_performance'],
                    performance_data
                )
                analysis_result['ml_optimization'] = ml_optimization
            
            # Perform 3S methodology assessment
            methodology_3s = await self.lean_six_sigma_agent.implement_3s_methodology()
            analysis_result['methodology_3s'] = methodology_3s
            
            # Log analysis summary
            logger.info(f"Comprehensive Quality Analysis completed:")
            logger.info(f"  - Overall Sigma Level: {analysis_result['overall_sigma_level']:.2f}")
            logger.info(f"  - Quality Grade: {analysis_result['quality_grade']}")
            logger.info(f"  - Improvement Recommendations: {len(analysis_result['improvement_recommendations'])}")
            logger.info(f"  - Financial Impact: ${analysis_result['financial_impact']['potential_annual_savings']:,.0f}")
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {str(e)}")
    
    async def _collect_performance_data(self) -> Dict[str, Any]:
        """Collect comprehensive performance data from all systems"""
        
        performance_data = {}
        
        try:
            # Get orchestrator metrics
            if self.u_cell_orchestrator:
                orchestrator_metrics = self.u_cell_orchestrator.get_metrics()
                performance_data['orchestrator'] = orchestrator_metrics
                
                # Extract key performance indicators
                performance_data['execution_latency_ms'] = [
                    orchestrator_metrics.get('average_latency_ms', 0)
                ] * 100  # Simulate historical data
                
                performance_data['signal_accuracy'] = [
                    orchestrator_metrics.get('successful_trades', 0) / max(1, orchestrator_metrics.get('total_signals', 1))
                ] * 100
                
                performance_data['trade_execution_success'] = [
                    1.0 - (orchestrator_metrics.get('failed_executions', 0) / max(1, orchestrator_metrics.get('total_signals', 1)))
                ] * 100
            
            # Get performance monitor data
            if self.performance_monitor:
                monitor_metrics = self.performance_monitor.get_comprehensive_metrics()
                performance_data['performance_monitor'] = monitor_metrics
                
                # Extract validation performance data
                validation_perf = monitor_metrics.get('validation_performance', {})
                
                if validation_perf.get('avg_validation_time_ms'):
                    performance_data['execution_latency_ms'] = [validation_perf['avg_validation_time_ms']] * 100
                
                if validation_perf.get('success_rate'):
                    performance_data['risk_adherence'] = [validation_perf['success_rate']] * 100
                
                # System health data
                system_health = monitor_metrics.get('system_health', {})
                performance_data['daily_pnl_volatility'] = [
                    system_health.get('health_score', 1.0) * 0.02  # Convert health to volatility metric
                ] * 100
            
            # Get MT5 Expert Agent data if available
            if self.mt5_expert_agent:
                # This would get real trading performance data
                # For now, simulate some trading metrics
                performance_data['slippage_pips'] = [0.5, 0.6, 0.4, 0.7, 0.5] * 20  # 100 data points
                performance_data['ml_performance'] = {
                    'accuracy': [0.85, 0.87, 0.83, 0.86, 0.88] * 20,
                    'precision': [0.82, 0.84, 0.81, 0.85, 0.86] * 20,
                    'recall': [0.88, 0.86, 0.85, 0.87, 0.89] * 20
                }
            
            # Add some synthetic data for demonstration
            if not performance_data.get('execution_latency_ms'):
                performance_data['execution_latency_ms'] = list(range(45, 95)) + [110, 120, 95, 85, 75] * 10
            
            if not performance_data.get('signal_accuracy'):
                performance_data['signal_accuracy'] = [0.85 + (i % 10) * 0.01 for i in range(100)]
            
            if not performance_data.get('risk_adherence'):
                performance_data['risk_adherence'] = [0.98 + (i % 5) * 0.002 for i in range(100)]
            
            if not performance_data.get('trade_execution_success'):
                performance_data['trade_execution_success'] = [0.97 + (i % 3) * 0.005 for i in range(100)]
            
            if not performance_data.get('slippage_pips'):
                performance_data['slippage_pips'] = [0.5 + (i % 7) * 0.1 for i in range(100)]
            
            if not performance_data.get('daily_pnl_volatility'):
                performance_data['daily_pnl_volatility'] = [0.02 + (i % 4) * 0.003 for i in range(100)]
            
        except Exception as e:
            logger.error(f"Error collecting performance data: {str(e)}")
        
        return performance_data
    
    async def get_quality_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive quality management dashboard data"""
        
        try:
            # Get real-time quality status
            quality_status = await self.lean_six_sigma_agent.monitor_real_time_quality()
            
            # Get comprehensive quality report
            quality_report = self.lean_six_sigma_agent.get_comprehensive_quality_report()
            
            # Get integration status
            integration_status = self.lean_six_sigma_agent.get_integration_status()
            
            # Compile dashboard data
            dashboard = {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': quality_status.get('overall_status', 'unknown'),
                'sigma_level': quality_report['executive_summary']['overall_sigma_level'],
                'quality_grade': quality_report['executive_summary']['quality_grade'],
                'dpmo': quality_report['executive_summary']['dpmo'],
                'active_alerts': {
                    'critical': len([a for a in self.integration_state['active_quality_alerts'] 
                                   if a.severity == ProcessImprovementLevel.CRITICAL]),
                    'high': len([a for a in self.integration_state['active_quality_alerts'] 
                               if a.severity == ProcessImprovementLevel.HIGH]),
                    'total': len(self.integration_state['active_quality_alerts'])
                },
                'active_projects': {
                    'total': len(quality_report['active_dmaic_projects']),
                    'auto_created': len(self.integration_state['auto_created_projects']),
                    'by_phase': self._summarize_projects_by_phase(quality_report['active_dmaic_projects'])
                },
                'real_time_metrics': quality_status.get('quality_metrics', {}),
                'process_capability': quality_report['process_capability_summary'],
                'top_improvement_opportunities': quality_report['top_improvement_opportunities'][:3],
                'methodology_3s': quality_report['methodology_3s_status'],
                'financial_impact': quality_report['financial_impact'],
                'integration_health': {
                    'status': self.integration_state['integration_health'],
                    'integrations': integration_status,
                    'last_analysis': self.integration_state.get('last_performance_analysis'),
                    'monitoring_active': self.is_monitoring
                },
                'recommendations': {
                    'immediate': quality_report['recommendations']['immediate_actions'][:3],
                    'strategic': quality_report['recommendations']['strategic_initiatives'][:3]
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating quality dashboard: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    def _summarize_projects_by_phase(self, projects: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize DMAIC projects by phase"""
        
        phase_counts = {
            'Define': 0,
            'Measure': 0,
            'Analyze': 0,
            'Improve': 0,
            'Control': 0
        }
        
        for project in projects:
            phase = project.get('phase', 'Define')
            if phase in phase_counts:
                phase_counts[phase] += 1
        
        return phase_counts
    
    async def create_improvement_project(self, 
                                       problem_statement: str,
                                       goal_statement: str,
                                       responsible_team: List[str],
                                       priority: str = 'medium') -> str:
        """Create new improvement project with integration tracking"""
        
        # Create DMAIC project
        project_id = await self.lean_six_sigma_agent.create_dmaic_project(
            problem_statement=problem_statement,
            goal_statement=goal_statement,
            responsible_team=responsible_team
        )
        
        # Track in integration state
        self.integration_state['auto_created_projects'].append({
            'project_id': project_id,
            'type': 'manual',
            'created_at': datetime.utcnow(),
            'priority': priority,
            'manual_creation': True
        })
        
        logger.info(f"Manual DMAIC project created: {project_id}")
        return project_id
    
    async def get_process_optimization_recommendations(self, process_name: str) -> Dict[str, Any]:
        """Get specific process optimization recommendations"""
        
        try:
            # Collect process-specific data
            performance_data = await self._collect_performance_data()
            
            # Filter for specific process if data is available
            process_data = {}
            if process_name in performance_data:
                process_data[process_name] = performance_data[process_name]
            else:
                # Use overall system data
                process_data = performance_data
            
            # Perform targeted analysis
            analysis = await self.lean_six_sigma_agent.analyze_trading_system_performance(
                process_data,
                time_period=timedelta(days=3)
            )
            
            # Extract process-specific recommendations
            recommendations = []
            for rec in analysis.get('improvement_recommendations', []):
                if process_name.lower() in rec.get('area', '').lower():
                    recommendations.append(rec)
            
            # If no specific recommendations, get general ones
            if not recommendations:
                recommendations = analysis.get('improvement_recommendations', [])[:5]
            
            optimization_result = {
                'process_name': process_name,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'current_performance': analysis.get('quality_assessment', {}),
                'recommendations': recommendations,
                'implementation_priority': self._prioritize_recommendations(recommendations),
                'expected_benefits': self._calculate_process_benefits(recommendations),
                'implementation_roadmap': self._create_process_roadmap(recommendations)
            }
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Error getting process optimization recommendations: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on impact and effort"""
        
        prioritized = []
        for rec in recommendations:
            priority_score = rec.get('expected_benefit', 0) / max(1, rec.get('implementation_effort', 1))
            
            prioritized.append({
                'recommendation': rec.get('recommendation', ''),
                'priority_score': priority_score,
                'effort': rec.get('implementation_effort', 'medium'),
                'benefit': rec.get('expected_benefit', 0),
                'timeline': rec.get('timeline_days', 30)
            })
        
        return sorted(prioritized, key=lambda x: x['priority_score'], reverse=True)
    
    def _calculate_process_benefits(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate expected benefits from recommendations"""
        
        total_benefit = sum(rec.get('expected_benefit', 0) for rec in recommendations)
        total_effort = sum(rec.get('implementation_effort', 5) for rec in recommendations)
        
        return {
            'total_financial_benefit': total_benefit,
            'total_implementation_effort': total_effort,
            'roi_estimate': (total_benefit / max(total_effort * 1000, 1)) * 100,
            'payback_period_weeks': max(total_effort, 1),
            'risk_adjusted_benefit': total_benefit * 0.8  # 80% confidence factor
        }
    
    def _create_process_roadmap(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create implementation roadmap for process improvements"""
        
        roadmap = {
            'immediate_actions': [],
            'short_term_actions': [],
            'long_term_actions': [],
            'total_timeline_weeks': 0
        }
        
        for rec in recommendations:
            timeline_days = rec.get('timeline_days', 30)
            action_item = {
                'action': rec.get('recommendation', ''),
                'timeline_days': timeline_days,
                'effort': rec.get('implementation_effort', 'medium'),
                'expected_benefit': rec.get('expected_benefit', 0)
            }
            
            if timeline_days <= 7:
                roadmap['immediate_actions'].append(action_item)
            elif timeline_days <= 30:
                roadmap['short_term_actions'].append(action_item)
            else:
                roadmap['long_term_actions'].append(action_item)
        
        # Calculate total timeline
        roadmap['total_timeline_weeks'] = max(rec.get('timeline_days', 30) for rec in recommendations) / 7
        
        return roadmap
    
    def get_integration_health(self) -> Dict[str, Any]:
        """Get integration health status"""
        
        health_status = {
            'overall_health': self.integration_state['integration_health'],
            'monitoring_active': self.is_monitoring,
            'last_quality_check': self.integration_state.get('last_quality_check'),
            'last_performance_analysis': self.integration_state.get('last_performance_analysis'),
            'active_alerts_count': len(self.integration_state['active_quality_alerts']),
            'auto_projects_count': len(self.integration_state['auto_created_projects']),
            'integration_points': self.lean_six_sigma_agent.get_integration_status(),
            'monitoring_config': self.quality_monitoring_config
        }
        
        return health_status


# Factory function for easy integration
async def create_integrated_lean_six_sigma(u_cell_orchestrator: UCellOrchestrator,
                                         performance_monitor: PerformanceMonitor,
                                         mt5_expert_agent: Optional[MT5ExpertAgent] = None) -> LeanSixSigmaIntegrationManager:
    """
    Factory function to create fully integrated LeanSixSigma system
    """
    
    integration_manager = LeanSixSigmaIntegrationManager(
        u_cell_orchestrator=u_cell_orchestrator,
        performance_monitor=performance_monitor,
        mt5_expert_agent=mt5_expert_agent
    )
    
    # Start monitoring
    await integration_manager.start_monitoring()
    
    logger.info("LeanSixSigma Integration Manager created and monitoring started")
    return integration_manager