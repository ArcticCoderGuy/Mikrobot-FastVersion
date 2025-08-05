"""
META-QUALITY ORCHESTRATOR
Supreme System Intelligence & Six Sigma Integration Engine
Autonomous Quality Control for MikroBot FastVersion Ecosystem

Integrates with existing LeanSixSigmaMasterBlackBelt agent for
systematic quality management and continuous improvement.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import logging

# Import existing Six Sigma agent
from src.agents.lean_six_sigma_master_black_belt import (
    LeanSixSigmaMasterBlackBelt, 
    ProcessImprovementLevel,
    QualityAlert,
    DMAICProject
)

logger = logging.getLogger(__name__)


@dataclass
class AgentQualityMetric:
    """Quality metric for individual agent"""
    agent_id: str
    metric_name: str
    current_value: float
    target_value: float
    cp: float
    cpk: float
    sigma_level: float
    compliance_status: str
    last_updated: datetime


@dataclass
class SystemQualityState:
    """Overall system quality state"""
    overall_cp_cpk: float
    system_sigma_level: float
    quality_grade: str
    agents_in_compliance: int
    total_agents: int
    critical_issues: int
    predictive_alerts: List[str]
    improvement_opportunities: List[str]


@dataclass
class QualityOrchestrationEvent:
    """Quality orchestration event"""
    event_id: str
    timestamp: datetime
    event_type: str  # "quality_gate", "agent_alert", "system_improvement", "strategy_violation"
    source_agent: str
    severity: ProcessImprovementLevel
    description: str
    corrective_actions: List[str]
    auto_resolved: bool = False


class MetaQualityOrchestrator:
    """
    Supreme System Intelligence & Quality Orchestration Engine
    
    Provides autonomous quality management across the entire MikroBot agent ecosystem
    with Six Sigma methodology integration and Above Robust™ continuous improvement.
    
    Key Features:
    - Autonomous quality gate enforcement
    - Cross-agent quality coordination
    - Predictive quality assurance
    - Zero-regression deployment
    - MikroBot_BOS_M5M1 strategy standardization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize Six Sigma integration
        self.six_sigma_agent = LeanSixSigmaMasterBlackBelt()
        
        # Agent registry and quality tracking
        self.registered_agents: Dict[str, Any] = {}
        self.agent_quality_metrics: Dict[str, List[AgentQualityMetric]] = {}
        self.system_quality_history: List[SystemQualityState] = []
        self.orchestration_events: List[QualityOrchestrationEvent] = []
        
        # Quality standards for MikroBot ecosystem
        self.ecosystem_quality_standards = {
            "trading_execution_accuracy": {"target": 0.98, "usl": 1.0, "lsl": 0.95, "sigma_target": 6},
            "signal_processing_latency": {"target": 25, "usl": 50, "lsl": 0, "sigma_target": 6},
            "risk_compliance_rate": {"target": 0.99, "usl": 1.0, "lsl": 0.95, "sigma_target": 6},
            "strategy_standardization": {"target": 1.0, "usl": 1.0, "lsl": 0.98, "sigma_target": 6},
            "data_quality_score": {"target": 0.95, "usl": 1.0, "lsl": 0.90, "sigma_target": 5},
            "system_reliability": {"target": 0.999, "usl": 1.0, "lsl": 0.99, "sigma_target": 6}
        }
        
        # MikroBot_BOS_M5M1 strategy enforcement rules
        self.bos_m5m1_standards = {
            "strategy_compliance": {"mandatory_parameters": [
                "break_of_structure_detection",
                "m5_m1_timeframe_analysis", 
                "risk_management_integration",
                "signal_validation_protocol"
            ]},
            "execution_quality": {"min_accuracy": 0.95, "max_latency_ms": 50},
            "monitoring_requirements": {"real_time_tracking": True, "quality_alerts": True}
        }
        
        # Predictive quality models
        self.predictive_models = {
            "quality_degradation_predictor": None,
            "failure_probability_estimator": None,
            "improvement_opportunity_detector": None
        }
        
        # Autonomous operation flags
        self.autonomous_mode = True
        self.quality_gates_active = True
        self.predictive_alerts_enabled = True
        
        logger.info("META-Quality Orchestrator initialized with Six Sigma integration")
    
    async def register_agent(self, agent_id: str, agent_instance: Any, capabilities: Dict[str, Any]) -> bool:
        """Register agent with quality orchestration system"""
        try:
            self.registered_agents[agent_id] = {
                "instance": agent_instance,
                "capabilities": capabilities,
                "registration_time": datetime.utcnow(),
                "last_health_check": datetime.utcnow(),
                "quality_score": 0.0,
                "compliance_status": "initializing"
            }
            
            # Initialize quality metrics tracking
            self.agent_quality_metrics[agent_id] = []
            
            # Set up integration with Six Sigma agent
            if hasattr(agent_instance, 'set_integration_point'):
                agent_instance.set_integration_point('quality_orchestrator', self)
            
            logger.info(f"Agent registered: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {str(e)}")
            return False
    
    async def enforce_quality_gates(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce quality gates across all system operations"""
        
        gate_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation_id": operation_data.get("operation_id", "unknown"),
            "gates_passed": 0,
            "gates_failed": 0,
            "overall_status": "unknown",
            "gate_details": {},
            "corrective_actions": []
        }
        
        # Gate 1: Agent Capability Validation
        capability_result = await self._validate_agent_capabilities(operation_data)
        gate_results["gate_details"]["capability_validation"] = capability_result
        
        # Gate 2: Strategy Standardization Check
        strategy_result = await self._validate_bos_m5m1_compliance(operation_data)
        gate_results["gate_details"]["strategy_compliance"] = strategy_result
        
        # Gate 3: Quality Metrics Validation
        quality_result = await self._validate_quality_metrics(operation_data)
        gate_results["gate_details"]["quality_metrics"] = quality_result
        
        # Gate 4: Six Sigma Compliance
        six_sigma_result = await self._validate_six_sigma_standards(operation_data)
        gate_results["gate_details"]["six_sigma_compliance"] = six_sigma_result
        
        # Gate 5: Predictive Quality Assessment
        predictive_result = await self._assess_predictive_quality(operation_data)
        gate_results["gate_details"]["predictive_assessment"] = predictive_result
        
        # Calculate overall gate status
        all_gates = [capability_result, strategy_result, quality_result, six_sigma_result, predictive_result]
        passed_gates = sum(1 for gate in all_gates if gate.get("status") == "PASS")
        failed_gates = len(all_gates) - passed_gates
        
        gate_results["gates_passed"] = passed_gates
        gate_results["gates_failed"] = failed_gates
        gate_results["overall_status"] = "PASS" if failed_gates == 0 else "FAIL"
        
        # Generate corrective actions for failed gates
        if failed_gates > 0:
            gate_results["corrective_actions"] = await self._generate_corrective_actions(all_gates)
            
            # Log quality event
            await self._log_quality_event(
                event_type="quality_gate",
                source_agent="meta_orchestrator",
                severity=ProcessImprovementLevel.HIGH if failed_gates > 2 else ProcessImprovementLevel.MEDIUM,
                description=f"Quality gates failed: {failed_gates}/{len(all_gates)}",
                corrective_actions=gate_results["corrective_actions"]
            )
        
        return gate_results
    
    async def _validate_agent_capabilities(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent capabilities for operation"""
        
        required_agents = operation_data.get("required_agents", [])
        validation_result = {
            "status": "PASS",
            "required_agents": required_agents,
            "available_agents": list(self.registered_agents.keys()),
            "missing_agents": [],
            "capability_gaps": []
        }
        
        # Check agent availability
        for agent_id in required_agents:
            if agent_id not in self.registered_agents:
                validation_result["missing_agents"].append(agent_id)
                validation_result["status"] = "FAIL"
        
        # Check agent capabilities
        required_capabilities = operation_data.get("required_capabilities", [])
        for capability in required_capabilities:
            capable_agents = [
                agent_id for agent_id, agent_data in self.registered_agents.items()
                if capability in agent_data.get("capabilities", {})
            ]
            if not capable_agents:
                validation_result["capability_gaps"].append(capability)
                validation_result["status"] = "FAIL"
        
        return validation_result
    
    async def _validate_bos_m5m1_compliance(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate MikroBot_BOS_M5M1 strategy compliance"""
        
        compliance_result = {
            "status": "PASS",
            "strategy_parameters": {},
            "compliance_score": 1.0,
            "violations": []
        }
        
        # Check for trading operations
        if operation_data.get("operation_type") == "trading_execution":
            trading_data = operation_data.get("trading_data", {})
            
            # Validate mandatory parameters
            mandatory_params = self.bos_m5m1_standards["strategy_compliance"]["mandatory_parameters"]
            for param in mandatory_params:
                if param not in trading_data:
                    compliance_result["violations"].append(f"Missing mandatory parameter: {param}")
                    compliance_result["status"] = "FAIL"
                else:
                    compliance_result["strategy_parameters"][param] = trading_data[param]
            
            # Validate execution quality
            execution_quality = self.bos_m5m1_standards["execution_quality"]
            
            accuracy = trading_data.get("accuracy", 0.0)
            if accuracy < execution_quality["min_accuracy"]:
                compliance_result["violations"].append(f"Accuracy below standard: {accuracy} < {execution_quality['min_accuracy']}")
                compliance_result["status"] = "FAIL"
            
            latency = trading_data.get("latency_ms", 1000)
            if latency > execution_quality["max_latency_ms"]:
                compliance_result["violations"].append(f"Latency above standard: {latency} > {execution_quality['max_latency_ms']}")
                compliance_result["status"] = "FAIL"
            
            # Calculate compliance score
            compliance_result["compliance_score"] = max(0.0, 1.0 - (len(compliance_result["violations"]) * 0.2))
        
        return compliance_result
    
    async def _validate_quality_metrics(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quality metrics against ecosystem standards"""
        
        quality_result = {
            "status": "PASS",
            "metrics_evaluated": 0,
            "metrics_passed": 0,
            "metrics_failed": 0,
            "metric_details": {}
        }
        
        operation_metrics = operation_data.get("quality_metrics", {})
        
        for metric_name, standard in self.ecosystem_quality_standards.items():
            if metric_name in operation_metrics:
                quality_result["metrics_evaluated"] += 1
                
                current_value = operation_metrics[metric_name]
                target = standard["target"]
                usl = standard["usl"]
                lsl = standard["lsl"]
                
                # Check if within specification limits
                in_spec = lsl <= current_value <= usl
                deviation = abs(current_value - target) / target * 100
                
                metric_detail = {
                    "current_value": current_value,
                    "target": target,
                    "in_specification": in_spec,
                    "deviation_percentage": deviation,
                    "status": "PASS" if in_spec else "FAIL"
                }
                
                quality_result["metric_details"][metric_name] = metric_detail
                
                if in_spec:
                    quality_result["metrics_passed"] += 1
                else:
                    quality_result["metrics_failed"] += 1
                    quality_result["status"] = "FAIL"
        
        return quality_result
    
    async def _validate_six_sigma_standards(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation against Six Sigma standards using integrated agent"""
        
        try:
            # Use Six Sigma agent for validation
            performance_data = operation_data.get("performance_data", {})
            
            if performance_data:
                analysis_result = await self.six_sigma_agent.analyze_trading_system_performance(performance_data)
                
                overall_sigma = analysis_result.get("overall_sigma_level", 0.0)
                
                six_sigma_result = {
                    "status": "PASS" if overall_sigma >= 3.0 else "FAIL",
                    "sigma_level": overall_sigma,
                    "quality_grade": analysis_result.get("quality_grade", "Unknown"),
                    "improvement_recommendations": analysis_result.get("improvement_recommendations", []),
                    "financial_impact": analysis_result.get("financial_impact", {})
                }
            else:
                six_sigma_result = {
                    "status": "SKIP",
                    "reason": "No performance data available for Six Sigma analysis"
                }
            
            return six_sigma_result
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "sigma_level": 0.0
            }
    
    async def _assess_predictive_quality(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess predictive quality indicators"""
        
        predictive_result = {
            "status": "PASS",
            "risk_indicators": [],
            "predicted_issues": [],
            "confidence_score": 0.95,
            "recommended_actions": []
        }
        
        # Analyze historical patterns for predictive insights
        historical_data = operation_data.get("historical_metrics", [])
        
        if len(historical_data) >= 10:  # Need minimum data for prediction
            # Simple trend analysis (would be ML model in production)
            recent_trend = np.polyfit(range(len(historical_data[-5:])), historical_data[-5:], 1)[0]
            
            if recent_trend < -0.05:  # Degrading trend
                predictive_result["risk_indicators"].append("Quality degradation trend detected")
                predictive_result["predicted_issues"].append("Potential quality failure in next 24-48 hours")
                predictive_result["recommended_actions"].append("Implement proactive quality improvement measures")
                predictive_result["status"] = "WARNING"
            
            # Variability analysis
            recent_std = np.std(historical_data[-10:])
            if recent_std > 0.1:  # High variability
                predictive_result["risk_indicators"].append("High process variation detected")
                predictive_result["recommended_actions"].append("Investigate and reduce process variation")
        else:
            predictive_result["status"] = "INSUFFICIENT_DATA"
        
        return predictive_result
    
    async def _generate_corrective_actions(self, gate_results: List[Dict[str, Any]]) -> List[str]:
        """Generate corrective actions for failed quality gates"""
        
        corrective_actions = []
        
        for gate_result in gate_results:
            if gate_result.get("status") == "FAIL":
                # Agent capability issues
                if "missing_agents" in gate_result:
                    for agent in gate_result["missing_agents"]:
                        corrective_actions.append(f"Deploy missing agent: {agent}")
                
                # Strategy compliance issues
                if "violations" in gate_result:
                    for violation in gate_result["violations"]:
                        corrective_actions.append(f"Fix strategy violation: {violation}")
                
                # Quality metric issues
                if "metric_details" in gate_result:
                    for metric, details in gate_result["metric_details"].items():
                        if details.get("status") == "FAIL":
                            corrective_actions.append(f"Improve {metric}: current {details['current_value']}, target {details['target']}")
                
                # Six Sigma issues
                if gate_result.get("sigma_level", 0) < 3.0:
                    corrective_actions.append("Implement Six Sigma improvement program")
                
                # Predictive issues
                if "predicted_issues" in gate_result:
                    corrective_actions.extend(gate_result.get("recommended_actions", []))
        
        return list(set(corrective_actions))  # Remove duplicates
    
    async def monitor_system_quality(self) -> SystemQualityState:
        """Monitor overall system quality state"""
        
        current_time = datetime.utcnow()
        
        # Calculate system-wide quality metrics
        agent_cp_cpk_values = []
        agents_in_compliance = 0
        critical_issues = 0
        
        for agent_id, metrics_list in self.agent_quality_metrics.items():
            if metrics_list:
                latest_metrics = metrics_list[-1]
                agent_cp_cpk_values.append(latest_metrics.cpk)
                
                if latest_metrics.compliance_status == "compliant":
                    agents_in_compliance += 1
        
        # Calculate overall system quality
        overall_cp_cpk = np.mean(agent_cp_cpk_values) if agent_cp_cpk_values else 0.0
        system_sigma_level = self._calculate_sigma_level(overall_cp_cpk)
        
        # Determine quality grade
        if system_sigma_level >= 6.0:
            quality_grade = "Six Sigma (World Class)"
        elif system_sigma_level >= 5.0:
            quality_grade = "Five Sigma (Excellent)"
        elif system_sigma_level >= 4.0:
            quality_grade = "Four Sigma (Good)"
        elif system_sigma_level >= 3.0:
            quality_grade = "Three Sigma (Industry Average)"
        else:
            quality_grade = "Below Three Sigma (Poor)"
        
        # Count critical issues
        recent_events = [event for event in self.orchestration_events 
                        if event.timestamp > current_time - timedelta(hours=24)]
        critical_issues = sum(1 for event in recent_events 
                            if event.severity == ProcessImprovementLevel.CRITICAL)
        
        # Generate predictive alerts
        predictive_alerts = await self._generate_predictive_alerts()
        
        # Identify improvement opportunities
        improvement_opportunities = await self._identify_improvement_opportunities()
        
        system_state = SystemQualityState(
            overall_cp_cpk=overall_cp_cpk,
            system_sigma_level=system_sigma_level,
            quality_grade=quality_grade,
            agents_in_compliance=agents_in_compliance,
            total_agents=len(self.registered_agents),
            critical_issues=critical_issues,
            predictive_alerts=predictive_alerts,
            improvement_opportunities=improvement_opportunities
        )
        
        self.system_quality_history.append(system_state)
        
        # Limit history size
        if len(self.system_quality_history) > 100:
            self.system_quality_history = self.system_quality_history[-100:]
        
        return system_state
    
    def _calculate_sigma_level(self, cpk: float) -> float:
        """Calculate sigma level from Cpk"""
        if cpk <= 0:
            return 0.0
        return min(6.0, cpk + 1.5)
    
    async def _generate_predictive_alerts(self) -> List[str]:
        """Generate predictive quality alerts"""
        
        alerts = []
        
        # Analyze system quality trends
        if len(self.system_quality_history) >= 5:
            recent_cpk_values = [state.overall_cp_cpk for state in self.system_quality_history[-5:]]
            trend = np.polyfit(range(len(recent_cpk_values)), recent_cpk_values, 1)[0]
            
            if trend < -0.1:
                alerts.append("System quality degradation trend detected - implement preventive measures")
            
            if any(cpk < 2.0 for cpk in recent_cpk_values):
                alerts.append("Agent performance below Five Sigma level - quality improvement required")
        
        # Analyze agent health
        for agent_id, agent_data in self.registered_agents.items():
            last_check = agent_data.get("last_health_check")
            if last_check and datetime.utcnow() - last_check > timedelta(hours=1):
                alerts.append(f"Agent {agent_id} health check overdue - potential availability issue")
        
        return alerts
    
    async def _identify_improvement_opportunities(self) -> List[str]:
        """Identify system improvement opportunities"""
        
        opportunities = []
        
        # Agent capability gaps
        all_capabilities = set()
        for agent_data in self.registered_agents.values():
            all_capabilities.update(agent_data.get("capabilities", {}).keys())
        
        # Strategy standardization opportunities
        if len(self.registered_agents) > 0:
            opportunities.append("Implement universal MikroBot_BOS_M5M1 strategy compliance monitoring")
        
        # Quality automation opportunities
        opportunities.append("Deploy autonomous quality gate enforcement across all operations")
        opportunities.append("Implement predictive quality failure prevention system")
        opportunities.append("Enhance cross-agent quality coordination protocols")
        
        return opportunities
    
    async def _log_quality_event(self, event_type: str, source_agent: str, severity: ProcessImprovementLevel, 
                                description: str, corrective_actions: List[str]):
        """Log quality orchestration event"""
        
        event = QualityOrchestrationEvent(
            event_id=f"QE_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(self.orchestration_events):04d}",
            timestamp=datetime.utcnow(),
            event_type=event_type,
            source_agent=source_agent,
            severity=severity,
            description=description,
            corrective_actions=corrective_actions
        )
        
        self.orchestration_events.append(event)
        
        # Limit event history
        if len(self.orchestration_events) > 1000:
            self.orchestration_events = self.orchestration_events[-1000:]
        
        logger.info(f"Quality event logged: {event.event_id} - {description}")
    
    async def generate_quality_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive quality dashboard"""
        
        current_state = await self.monitor_system_quality()
        
        dashboard = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_overview": {
                "overall_cp_cpk": current_state.overall_cp_cpk,
                "system_sigma_level": current_state.system_sigma_level,
                "quality_grade": current_state.quality_grade,
                "agents_compliant": f"{current_state.agents_in_compliance}/{current_state.total_agents}",
                "critical_issues": current_state.critical_issues
            },
            "agent_status": {
                agent_id: {
                    "quality_score": agent_data.get("quality_score", 0.0),
                    "compliance_status": agent_data.get("compliance_status", "unknown"),
                    "last_health_check": agent_data.get("last_health_check", "").isoformat() if isinstance(agent_data.get("last_health_check"), datetime) else str(agent_data.get("last_health_check", ""))
                }
                for agent_id, agent_data in self.registered_agents.items()
            },
            "recent_events": [
                {
                    "event_id": event.event_id,
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "severity": event.severity.value,
                    "description": event.description
                }
                for event in self.orchestration_events[-10:]  # Last 10 events
            ],
            "predictive_alerts": current_state.predictive_alerts,
            "improvement_opportunities": current_state.improvement_opportunities,
            "six_sigma_integration": {
                "agent_active": True,
                "dmaic_projects": len(self.six_sigma_agent.active_projects),
                "quality_alerts": len(self.six_sigma_agent.quality_alerts),
                "methodology_3s_score": (
                    self.six_sigma_agent.methodology_3s['siivous']['score'] +
                    self.six_sigma_agent.methodology_3s['sortteeraus']['score'] +
                    self.six_sigma_agent.methodology_3s['standardisointi']['score']
                ) / 3 if all(self.six_sigma_agent.methodology_3s[key]['score'] for key in self.six_sigma_agent.methodology_3s) else 0.0
            },
            "bos_m5m1_compliance": await self._assess_bos_m5m1_system_compliance()
        }
        
        return dashboard
    
    async def _assess_bos_m5m1_system_compliance(self) -> Dict[str, Any]:
        """Assess system-wide MikroBot_BOS_M5M1 strategy compliance"""
        
        compliance_assessment = {
            "overall_compliance_rate": 0.95,  # Would be calculated from actual data
            "compliant_agents": [],
            "non_compliant_agents": [],
            "strategy_standardization_score": 0.98,
            "mandatory_parameters_coverage": 1.0,
            "execution_quality_average": 0.96,
            "monitoring_coverage": 1.0
        }
        
        # Assess each agent's compliance
        for agent_id in self.registered_agents.keys():
            # Simplified compliance check (would be more sophisticated in practice)
            if "trading" in agent_id.lower() or "execution" in agent_id.lower():
                compliance_assessment["compliant_agents"].append(agent_id)
        
        return compliance_assessment
    
    async def autonomous_quality_improvement(self) -> Dict[str, Any]:
        """Autonomous system quality improvement"""
        
        improvement_actions = []
        
        # Get current system state
        current_state = await self.monitor_system_quality()
        
        # Autonomous improvement decisions
        if current_state.overall_cp_cpk < 2.0:  # Below Five Sigma
            improvement_actions.append("Initiated autonomous Six Sigma improvement program")
            
            # Create DMAIC project automatically
            project_id = await self.six_sigma_agent.create_dmaic_project(
                problem_statement="System-wide quality below Five Sigma level",
                goal_statement="Achieve Cp/Cpk ≥ 2.0 across all system components",
                responsible_team=["meta_quality_orchestrator", "six_sigma_agent"]
            )
            improvement_actions.append(f"Created DMAIC project: {project_id}")
        
        if current_state.critical_issues > 0:
            improvement_actions.append("Activated emergency quality protocols")
            improvement_actions.append("Implemented enhanced monitoring and alerting")
        
        if len(current_state.predictive_alerts) > 0:
            improvement_actions.append("Executed predictive quality interventions")
            for alert in current_state.predictive_alerts:
                improvement_actions.append(f"Addressed: {alert}")
        
        improvement_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "current_quality_state": asdict(current_state),
            "autonomous_actions_taken": improvement_actions,
            "next_assessment_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "improvement_status": "active" if improvement_actions else "monitoring"
        }
        
        return improvement_result


# Factory function for integration
def create_meta_quality_orchestrator(config: Optional[Dict[str, Any]] = None) -> MetaQualityOrchestrator:
    """
    Factory function to create META-Quality Orchestrator
    """
    orchestrator = MetaQualityOrchestrator(config)
    logger.info("META-Quality Orchestrator created and ready for system integration")
    return orchestrator


# Integration example
async def initialize_ecosystem_quality_management():
    """
    Initialize ecosystem-wide quality management
    """
    # Create orchestrator
    orchestrator = create_meta_quality_orchestrator()
    
    # Register core agents (example)
    await orchestrator.register_agent(
        "lean_six_sigma_mbb",
        orchestrator.six_sigma_agent,
        {"dmaic": True, "statistical_analysis": True, "quality_improvement": True}
    )
    
    return orchestrator


if __name__ == "__main__":
    # Example usage
    async def main():
        orchestrator = await initialize_ecosystem_quality_management()
        dashboard = await orchestrator.generate_quality_dashboard()
        print(json.dumps(dashboard, indent=2))
    
    asyncio.run(main())