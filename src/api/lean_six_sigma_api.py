"""
LeanSixSigma API Endpoints
FastAPI endpoints for LeanSixSigma MasterBlackBelt functionality

Provides REST API access to Six Sigma quality management, DMAIC projects,
statistical process control, and continuous improvement capabilities.

Author: Claude Code
Integration: MikroBot FastAPI Application
Created: 2025-08-03
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from ..core.lean_six_sigma_integration import LeanSixSigmaIntegrationManager

logger = logging.getLogger(__name__)

# Router for LeanSixSigma endpoints
router = APIRouter(prefix="/quality", tags=["Six Sigma Quality Management"])


# Pydantic models for API requests/responses
class CreateProjectRequest(BaseModel):
    problem_statement: str = Field(..., description="Clear problem statement")
    goal_statement: str = Field(..., description="Specific goal statement")
    responsible_team: List[str] = Field(..., description="List of responsible team members")
    priority: str = Field(default="medium", description="Project priority: low, medium, high, critical")


class ProcessOptimizationRequest(BaseModel):
    process_name: str = Field(..., description="Name of process to optimize")
    time_period_days: int = Field(default=7, description="Analysis time period in days", ge=1, le=30)
    include_ml_optimization: bool = Field(default=True, description="Include ML optimization analysis")


class QFDRequest(BaseModel):
    customer_requirements: List[str] = Field(..., description="List of customer requirements")
    importance_ratings: List[float] = Field(..., description="Importance ratings (1-10 scale)")
    technical_requirements: List[str] = Field(..., description="List of technical requirements")


class QualityThresholdUpdate(BaseModel):
    metric_name: str = Field(..., description="Name of quality metric")
    target: float = Field(..., description="Target value")
    upper_spec_limit: float = Field(..., description="Upper specification limit")
    lower_spec_limit: float = Field(..., description="Lower specification limit")
    sigma_target: int = Field(..., description="Target sigma level", ge=1, le=6)


# Dependency to get LeanSixSigma integration manager
# This would be injected in the main application
lean_six_sigma_manager: Optional[LeanSixSigmaIntegrationManager] = None


def get_lean_six_sigma_manager() -> LeanSixSigmaIntegrationManager:
    """Get LeanSixSigma integration manager"""
    if lean_six_sigma_manager is None:
        raise HTTPException(
            status_code=503,
            detail="LeanSixSigma service not available"
        )
    return lean_six_sigma_manager


def set_lean_six_sigma_manager(manager: LeanSixSigmaIntegrationManager):
    """Set LeanSixSigma integration manager (called from main app)"""
    global lean_six_sigma_manager
    lean_six_sigma_manager = manager


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_quality_dashboard(
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get comprehensive quality management dashboard
    
    Returns:
    - Overall quality metrics and sigma levels
    - Active alerts and DMAIC projects
    - Real-time process capability
    - Improvement recommendations
    - Financial impact analysis
    """
    try:
        dashboard = await manager.get_quality_dashboard()
        return dashboard
    except Exception as e:
        logger.error(f"Error getting quality dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/comprehensive", response_model=Dict[str, Any])
async def get_comprehensive_analysis(
    time_period_days: int = 7,
    include_ml_optimization: bool = True,
    include_3s_methodology: bool = True,
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get comprehensive Six Sigma analysis of trading system performance
    
    Parameters:
    - time_period_days: Analysis time period (1-30 days)
    - include_ml_optimization: Include TensorFlow ML optimization analysis
    - include_3s_methodology: Include 3S methodology assessment
    
    Returns:
    - Statistical process control analysis
    - Process capability assessment
    - Root cause analysis with Pareto charts
    - Quality level assessment
    - Improvement recommendations
    - Financial impact analysis
    """
    try:
        if not (1 <= time_period_days <= 30):
            raise HTTPException(status_code=400, detail="Time period must be between 1 and 30 days")
        
        # Collect performance data
        performance_data = await manager._collect_performance_data()
        
        # Perform comprehensive analysis
        analysis_result = await manager.lean_six_sigma_agent.analyze_trading_system_performance(
            performance_data,
            time_period=timedelta(days=time_period_days)
        )
        
        # Add ML optimization if requested
        if include_ml_optimization and 'ml_performance' in performance_data:
            ml_optimization = await manager.lean_six_sigma_agent.optimize_tensorflow_learning(
                performance_data['ml_performance'],
                performance_data
            )
            analysis_result['ml_optimization'] = ml_optimization
        
        # Add 3S methodology if requested
        if include_3s_methodology:
            methodology_3s = await manager.lean_six_sigma_agent.implement_3s_methodology()
            analysis_result['methodology_3s'] = methodology_3s
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/real-time", response_model=Dict[str, Any])
async def get_real_time_quality_status(
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get real-time quality status and metrics
    
    Returns:
    - Current quality metrics vs targets
    - Process control status
    - Active quality alerts
    - System health indicators
    """
    try:
        quality_status = await manager.lean_six_sigma_agent.monitor_real_time_quality()
        return quality_status
    except Exception as e:
        logger.error(f"Error getting real-time quality status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/create", response_model=Dict[str, str])
async def create_improvement_project(
    project_request: CreateProjectRequest,
    background_tasks: BackgroundTasks,
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Create new DMAIC improvement project
    
    Parameters:
    - problem_statement: Clear description of the problem
    - goal_statement: Specific, measurable goal
    - responsible_team: List of team members responsible
    - priority: Project priority level
    
    Returns:
    - project_id: Unique identifier for the project
    - status: Creation status
    """
    try:
        project_id = await manager.create_improvement_project(
            problem_statement=project_request.problem_statement,
            goal_statement=project_request.goal_statement,
            responsible_team=project_request.responsible_team,
            priority=project_request.priority
        )
        
        return {
            "project_id": project_id,
            "status": "created",
            "message": f"DMAIC project {project_id} created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating improvement project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=Dict[str, Any])
async def get_active_projects(
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get all active DMAIC projects
    
    Returns:
    - List of active projects with status and progress
    - Project statistics by phase
    - Auto-created vs manual projects
    """
    try:
        quality_report = manager.lean_six_sigma_agent.get_comprehensive_quality_report()
        
        projects_info = {
            "active_projects": quality_report['active_dmaic_projects'],
            "auto_created_projects": manager.integration_state['auto_created_projects'],
            "summary": {
                "total_active": len(quality_report['active_dmaic_projects']),
                "auto_created": len(manager.integration_state['auto_created_projects']),
                "by_phase": manager._summarize_projects_by_phase(quality_report['active_dmaic_projects'])
            }
        }
        
        return projects_info
        
    except Exception as e:
        logger.error(f"Error getting active projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/advance", response_model=Dict[str, Any])
async def advance_project_phase(
    project_id: str,
    phase_data: Dict[str, Any],
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Advance DMAIC project to next phase
    
    Parameters:
    - project_id: Project identifier
    - phase_data: Data and deliverables for current phase
    
    Returns:
    - Updated project status and phase information
    """
    try:
        result = await manager.lean_six_sigma_agent.advance_dmaic_project(project_id, phase_data)
        return result
    except Exception as e:
        logger.error(f"Error advancing project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimization/process", response_model=Dict[str, Any])
async def get_process_optimization(
    optimization_request: ProcessOptimizationRequest,
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get process-specific optimization recommendations
    
    Parameters:
    - process_name: Name of process to optimize
    - time_period_days: Analysis time period
    - include_ml_optimization: Include ML optimization analysis
    
    Returns:
    - Process-specific analysis and recommendations
    - Implementation roadmap
    - Expected benefits and ROI
    """
    try:
        optimization_result = await manager.get_process_optimization_recommendations(
            optimization_request.process_name
        )
        return optimization_result
    except Exception as e:
        logger.error(f"Error getting process optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qfd/create", response_model=Dict[str, Any])
async def create_qfd_matrix(
    qfd_request: QFDRequest,
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Create Quality Function Deployment (QFD) House of Quality matrix
    
    Parameters:
    - customer_requirements: List of customer needs/requirements
    - importance_ratings: Importance ratings for each requirement (1-10 scale)
    - technical_requirements: List of technical requirements/features
    
    Returns:
    - Complete QFD matrix with relationships
    - Technical importance scores
    - Implementation priorities
    - Correlation matrix
    """
    try:
        if len(qfd_request.customer_requirements) != len(qfd_request.importance_ratings):
            raise HTTPException(
                status_code=400,
                detail="Number of customer requirements must match number of importance ratings"
            )
        
        qfd_matrix = await manager.lean_six_sigma_agent.create_qfd_matrix(
            customer_requirements=qfd_request.customer_requirements,
            importance_ratings=qfd_request.importance_ratings,
            technical_requirements=qfd_request.technical_requirements
        )
        
        return qfd_matrix
        
    except Exception as e:
        logger.error(f"Error creating QFD matrix: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimization/tensorflow", response_model=Dict[str, Any])
async def optimize_tensorflow_models(
    model_performance_data: Dict[str, Any],
    training_data: Optional[Dict[str, Any]] = None,
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Optimize TensorFlow ML models using QFD methodology
    
    Parameters:
    - model_performance_data: Current model performance metrics
    - training_data: Training dataset information (optional)
    
    Returns:
    - QFD analysis for ML optimization
    - Performance improvement recommendations
    - Implementation roadmap
    - Success metrics definition
    """
    try:
        if training_data is None:
            training_data = {}
        
        ml_optimization = await manager.lean_six_sigma_agent.optimize_tensorflow_learning(
            model_performance=model_performance_data,
            training_data=training_data
        )
        
        return ml_optimization
        
    except Exception as e:
        logger.error(f"Error optimizing TensorFlow models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/methodology/3s", response_model=Dict[str, Any])
async def get_3s_methodology_assessment(
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get 3S methodology (Siivous, Sortteeraus, Standardisointi) assessment
    
    Returns:
    - Current 3S scores for each component
    - Improvement actions and roadmap
    - Next assessment schedule
    """
    try:
        methodology_3s = await manager.lean_six_sigma_agent.implement_3s_methodology()
        return methodology_3s
    except Exception as e:
        logger.error(f"Error getting 3S methodology assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/spc", response_model=Dict[str, Any])
async def get_statistical_process_control(
    metric_name: Optional[str] = None,
    time_period_hours: int = 24,
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get Statistical Process Control (SPC) analysis
    
    Parameters:
    - metric_name: Specific metric to analyze (optional, analyzes all if not provided)
    - time_period_hours: Time period for analysis (1-168 hours)
    
    Returns:
    - Control charts data
    - Process capability indices (Cp, Cpk)
    - Sigma levels
    - Out-of-control points
    - Trend analysis
    """
    try:
        if not (1 <= time_period_hours <= 168):
            raise HTTPException(status_code=400, detail="Time period must be between 1 and 168 hours")
        
        # Get comprehensive performance data
        performance_data = await manager._collect_performance_data()
        
        # Perform SPC analysis
        spc_analysis = await manager.lean_six_sigma_agent._perform_spc_analysis(performance_data)
        
        # Filter for specific metric if requested
        if metric_name:
            if metric_name in spc_analysis:
                spc_analysis = {metric_name: spc_analysis[metric_name]}
            else:
                raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")
        
        return {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "time_period_hours": time_period_hours,
            "spc_analysis": spc_analysis,
            "summary": {
                "total_metrics_analyzed": len(spc_analysis),
                "metrics_in_control": len([m for m in spc_analysis.values() 
                                         if m['process_metric']['in_control']]),
                "average_sigma_level": sum(m['process_metric']['sigma_level'] 
                                         for m in spc_analysis.values()) / len(spc_analysis) if spc_analysis else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting SPC analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=Dict[str, Any])
async def get_quality_alerts(
    severity: Optional[str] = None,
    active_only: bool = True,
    limit: int = 50,
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get quality alerts
    
    Parameters:
    - severity: Filter by severity (critical, high, medium, low)
    - active_only: Return only active alerts
    - limit: Maximum number of alerts to return
    
    Returns:
    - List of quality alerts
    - Alert statistics
    - Escalation recommendations
    """
    try:
        all_alerts = manager.integration_state['active_quality_alerts']
        
        # Filter by severity if specified
        if severity:
            severity_mapping = {
                'critical': 'CRITICAL',
                'high': 'HIGH',
                'medium': 'MEDIUM',
                'low': 'LOW'
            }
            if severity.lower() not in severity_mapping:
                raise HTTPException(status_code=400, detail="Invalid severity level")
            
            target_severity = severity_mapping[severity.lower()]
            all_alerts = [alert for alert in all_alerts if alert.severity.name == target_severity]
        
        # Apply limit
        alerts = all_alerts[:limit]
        
        # Convert to dict for JSON serialization
        alert_data = []
        for alert in alerts:
            alert_dict = {
                'timestamp': alert.timestamp.isoformat(),
                'severity': alert.severity.value,
                'process': alert.process,
                'metric': alert.metric,
                'current_value': alert.current_value,
                'target_value': alert.target_value,
                'deviation_percentage': alert.deviation_percentage,
                'sigma_level': alert.sigma_level,
                'root_cause_hypothesis': alert.root_cause_hypothesis,
                'recommended_actions': alert.recommended_actions,
                'financial_impact': alert.financial_impact,
                'trace_id': alert.trace_id
            }
            alert_data.append(alert_dict)
        
        # Calculate statistics
        statistics = {
            'total_alerts': len(all_alerts),
            'returned_alerts': len(alerts),
            'by_severity': {},
            'total_financial_impact': sum(alert.financial_impact for alert in all_alerts),
            'oldest_alert': min(alert.timestamp for alert in all_alerts).isoformat() if all_alerts else None,
            'newest_alert': max(alert.timestamp for alert in all_alerts).isoformat() if all_alerts else None
        }
        
        # Count by severity
        for alert in all_alerts:
            severity_name = alert.severity.value
            statistics['by_severity'][severity_name] = statistics['by_severity'].get(severity_name, 0) + 1
        
        return {
            "alerts": alert_data,
            "statistics": statistics,
            "escalation_recommendations": manager._get_escalation_recommendations(all_alerts)
        }
        
    except Exception as e:
        logger.error(f"Error getting quality alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_escalation_recommendations(self, alerts: List) -> List[str]:
    """Get escalation recommendations based on alerts"""
    recommendations = []
    
    critical_count = len([a for a in alerts if a.severity.name == 'CRITICAL'])
    high_count = len([a for a in alerts if a.severity.name == 'HIGH'])
    
    if critical_count >= 3:
        recommendations.append("Immediate management escalation required - multiple critical quality issues")
    
    if high_count >= 5:
        recommendations.append("Consider creating systematic improvement project")
    
    total_impact = sum(alert.financial_impact for alert in alerts)
    if total_impact > 10000:
        recommendations.append(f"High financial impact (${total_impact:,.0f}) - prioritize resolution")
    
    return recommendations


@router.put("/thresholds/update", response_model=Dict[str, str])
async def update_quality_thresholds(
    threshold_update: QualityThresholdUpdate,
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Update quality thresholds and standards
    
    Parameters:
    - metric_name: Name of the quality metric
    - target: Target value for the metric
    - upper_spec_limit: Upper specification limit
    - lower_spec_limit: Lower specification limit
    - sigma_target: Target sigma level (1-6)
    
    Returns:
    - Update confirmation and new threshold values
    """
    try:
        # Update quality standards
        manager.lean_six_sigma_agent.quality_standards[threshold_update.metric_name] = {
            'target': threshold_update.target,
            'usl': threshold_update.upper_spec_limit,
            'lsl': threshold_update.lower_spec_limit,
            'sigma_target': threshold_update.sigma_target
        }
        
        return {
            "status": "updated",
            "metric_name": threshold_update.metric_name,
            "message": f"Quality thresholds updated for {threshold_update.metric_name}"
        }
        
    except Exception as e:
        logger.error(f"Error updating quality thresholds: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/expertise", response_model=Dict[str, Any])
async def get_expertise_domains(
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get LeanSixSigma agent expertise domains and confidence levels
    
    Returns:
    - Expertise domains with confidence levels
    - Specialization areas
    - Integration status
    """
    try:
        expertise_info = {
            "expertise_domains": manager.lean_six_sigma_agent.expertise_domains,
            "integration_status": manager.lean_six_sigma_agent.get_integration_status(),
            "integration_health": manager.get_integration_health(),
            "capabilities": {
                "dmaic_methodology": "Full DMAIC project management with automated tracking",
                "root_cause_analysis": "Advanced Pareto analysis with nested investigation",
                "statistical_process_control": "Real-time SPC with automated alerts",
                "qfd_analysis": "Complete House of Quality for ML optimization",
                "3s_methodology": "Comprehensive process improvement framework",
                "fintech_quality": "Specialized trading system quality management"
            }
        }
        
        return expertise_info
        
    except Exception as e:
        logger.error(f"Error getting expertise domains: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/comprehensive", response_model=Dict[str, Any])
async def get_comprehensive_quality_report(
    include_financial_analysis: bool = True,
    include_recommendations: bool = True,
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get comprehensive quality management report
    
    Parameters:
    - include_financial_analysis: Include financial impact analysis
    - include_recommendations: Include improvement recommendations
    
    Returns:
    - Complete quality management report
    - Executive summary with key metrics
    - Detailed analysis and recommendations
    - Financial impact assessment
    """
    try:
        comprehensive_report = manager.lean_six_sigma_agent.get_comprehensive_quality_report()
        
        if not include_financial_analysis:
            comprehensive_report.pop('financial_impact', None)
        
        if not include_recommendations:
            comprehensive_report.pop('recommendations', None)
        
        return comprehensive_report
        
    except Exception as e:
        logger.error(f"Error getting comprehensive quality report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def get_lean_six_sigma_health(
    manager: LeanSixSigmaIntegrationManager = Depends(get_lean_six_sigma_manager)
):
    """
    Get LeanSixSigma system health status
    
    Returns:
    - Integration health status
    - Monitoring status
    - System performance metrics
    - Configuration status
    """
    try:
        health_status = manager.get_integration_health()
        
        # Add system metrics
        health_status.update({
            "system_metrics": {
                "active_projects": len(manager.lean_six_sigma_agent.active_projects),
                "quality_alerts": len(manager.integration_state['active_quality_alerts']),
                "process_metrics": len(manager.lean_six_sigma_agent.process_metrics),
                "pareto_analyses": len(manager.lean_six_sigma_agent.pareto_analysis_history)
            },
            "service_status": "healthy" if manager.is_monitoring else "stopped",
            "last_health_check": datetime.utcnow().isoformat()
        })
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error getting LeanSixSigma health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))