"""
Enhanced Orchestrator
ProductOwner → MCPController → U-Cells orchestration system
Implements deterministic processing pipeline with strategic oversight
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
from dataclasses import dataclass, asdict
from enum import Enum

from .mcp_controller import MCPController, MCPMessage, MessageType
from .product_owner_agent import ProductOwnerAgent, StrategyType
from .u_cells.orchestrator import UCellOrchestrator
from .u_cells import CellInput, CellOutput

logger = logging.getLogger(__name__)


class ProcessingStage(Enum):
    """Processing pipeline stages"""
    STRATEGIC_EVALUATION = "strategic_evaluation"
    SIGNAL_VALIDATION = "signal_validation"
    ML_ANALYSIS = "ml_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    TRADE_EXECUTION = "trade_execution"
    MONITORING = "monitoring"
    PERFORMANCE_UPDATE = "performance_update"


@dataclass
class PipelineResult:
    """Result of complete pipeline processing"""
    pipeline_id: str
    trace_id: str
    signal_data: Dict[str, Any]
    strategic_decision: Dict[str, Any]
    u_cell_results: Dict[str, Any]
    final_status: str
    total_latency_ms: float
    stage_results: Dict[str, Any]
    timestamp: datetime
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class EnhancedOrchestrator:
    """
    Enhanced orchestrator implementing ProductOwner → MCPController → U-Cells flow
    
    Architecture:
    1. ProductOwner Agent: Strategic decision making and business logic
    2. MCP Controller: Agent coordination and communication management
    3. U-Cell Orchestrator: Deterministic trading pipeline execution
    
    Features:
    - Strategic oversight of all trading decisions
    - Circuit breaker protection for agent failures
    - Event sourcing for decision replay and analysis
    - Priority-based message routing
    - Performance optimization feedback loops
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize core components
        self.mcp_controller = MCPController(config.get('mcp_config', {}))
        self.product_owner = ProductOwnerAgent()
        self.ucell_orchestrator = UCellOrchestrator(config.get('ucell_config', {}))
        
        # Register ProductOwner with MCP Controller
        self.mcp_controller.register_agent(self.product_owner)
        
        # Enhanced metrics
        self.orchestration_metrics = {
            'total_signals_processed': 0,
            'strategic_approvals': 0,
            'strategic_rejections': 0,
            'pipeline_completions': 0,
            'pipeline_failures': 0,
            'average_pipeline_latency_ms': 0.0,
            'performance_optimization_triggers': 0
        }
        
        # Pipeline tracking
        self.active_pipelines: Dict[str, PipelineResult] = {}
        self.completed_pipelines: List[PipelineResult] = []
        
        # State management
        self.is_running = False
        self.processing_queue = asyncio.Queue()
        
        logger.info("Enhanced Orchestrator initialized with ProductOwner → MCP → U-Cells architecture")
    
    async def start(self):
        """Start the enhanced orchestrator"""
        self.is_running = True
        
        # Start MCP Controller
        await self.mcp_controller.start()
        
        # Start processing loop
        asyncio.create_task(self._processing_loop())
        
        logger.info("Enhanced Orchestrator started")
    
    async def stop(self):
        """Stop the enhanced orchestrator"""
        self.is_running = False
        
        # Stop components
        await self.mcp_controller.stop()
        self.ucell_orchestrator.shutdown()
        
        logger.info("Enhanced Orchestrator stopped")
    
    async def process_trading_signal(self, signal_data: Dict[str, Any]) -> PipelineResult:
        """
        Process trading signal through complete ProductOwner → MCP → U-Cells pipeline
        
        Pipeline Flow:
        1. Strategic Evaluation by ProductOwner
        2. If approved, route through U-Cell pipeline via MCP Controller
        3. Update ProductOwner with results for learning
        4. Return comprehensive results
        """
        pipeline_id = str(uuid.uuid4())
        trace_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Processing signal {trace_id} through enhanced pipeline: {signal_data.get('symbol')} {signal_data.get('pattern_type')}")
        
        # Initialize pipeline result
        pipeline_result = PipelineResult(
            pipeline_id=pipeline_id,
            trace_id=trace_id,
            signal_data=signal_data,
            strategic_decision={},
            u_cell_results={},
            final_status='processing',
            total_latency_ms=0.0,
            stage_results={},
            timestamp=start_time
        )
        
        self.active_pipelines[pipeline_id] = pipeline_result
        
        try:
            # Stage 1: Strategic Evaluation by ProductOwner
            stage_start = datetime.utcnow()
            strategic_decision = await self._strategic_evaluation(signal_data, trace_id)
            stage_latency = (datetime.utcnow() - stage_start).total_seconds() * 1000\n            \n            pipeline_result.strategic_decision = strategic_decision\n            pipeline_result.stage_results[ProcessingStage.STRATEGIC_EVALUATION.value] = {\n                'latency_ms': round(stage_latency, 2),\n                'result': strategic_decision\n            }\n            \n            self.orchestration_metrics['total_signals_processed'] += 1\n            \n            # Check strategic approval\n            if not strategic_decision.get('approved', False):\n                pipeline_result.final_status = 'strategically_rejected'\n                pipeline_result.stage_results['rejection_reason'] = strategic_decision.get('reasons', [])\n                self.orchestration_metrics['strategic_rejections'] += 1\n                \n                logger.info(f\"Signal {trace_id} strategically rejected: {strategic_decision.get('reasons')}\")\n                return pipeline_result\n            \n            self.orchestration_metrics['strategic_approvals'] += 1\n            \n            # Stage 2: Execute U-Cell Pipeline with strategic adjustments\n            stage_start = datetime.utcnow()\n            \n            # Apply strategic adjustments to signal\n            adjusted_signal = self._apply_strategic_adjustments(signal_data, strategic_decision)\n            \n            # Process through U-Cell pipeline\n            ucell_results = await self.ucell_orchestrator.process_signal(adjusted_signal)\n            stage_latency = (datetime.utcnow() - stage_start).total_seconds() * 1000\n            \n            pipeline_result.u_cell_results = ucell_results\n            pipeline_result.stage_results[ProcessingStage.SIGNAL_VALIDATION.value] = {\n                'latency_ms': round(stage_latency, 2),\n                'result': ucell_results\n            }\n            \n            # Stage 3: Performance Feedback to ProductOwner\n            if ucell_results.get('final_status') in ['success', 'failed']:\n                stage_start = datetime.utcnow()\n                \n                # Extract trade result for performance update\n                trade_result = self._extract_trade_result(ucell_results)\n                await self._update_product_owner_performance(trade_result, trace_id)\n                \n                stage_latency = (datetime.utcnow() - stage_start).total_seconds() * 1000\n                pipeline_result.stage_results[ProcessingStage.PERFORMANCE_UPDATE.value] = {\n                    'latency_ms': round(stage_latency, 2),\n                    'result': trade_result\n                }\n            \n            # Set final status\n            pipeline_result.final_status = ucell_results.get('final_status', 'unknown')\n            \n            # Calculate total latency\n            pipeline_result.total_latency_ms = round(\n                (datetime.utcnow() - start_time).total_seconds() * 1000, 2\n            )\n            \n            # Update metrics\n            self._update_orchestration_metrics(pipeline_result)\n            \n            logger.info(f\"Pipeline {pipeline_id} completed: {pipeline_result.final_status} in {pipeline_result.total_latency_ms}ms\")\n            \n            return pipeline_result\n            \n        except Exception as e:\n            logger.error(f\"Pipeline {pipeline_id} error: {str(e)}\")\n            \n            pipeline_result.final_status = 'pipeline_error'\n            pipeline_result.errors.append(str(e))\n            pipeline_result.total_latency_ms = round(\n                (datetime.utcnow() - start_time).total_seconds() * 1000, 2\n            )\n            \n            self.orchestration_metrics['pipeline_failures'] += 1\n            \n            return pipeline_result\n            \n        finally:\n            # Move to completed pipelines\n            if pipeline_id in self.active_pipelines:\n                self.completed_pipelines.append(self.active_pipelines[pipeline_id])\n                del self.active_pipelines[pipeline_id]\n                \n                # Keep only last 1000 completed pipelines\n                if len(self.completed_pipelines) > 1000:\n                    self.completed_pipelines = self.completed_pipelines[-1000:]\n    \n    async def _strategic_evaluation(self, signal_data: Dict[str, Any], trace_id: str) -> Dict[str, Any]:\n        \"\"\"Get strategic evaluation from ProductOwner\"\"\"\n        evaluation_message = MCPMessage(\n            id=f\"strategic_eval_{trace_id}\",\n            method=\"evaluate_signal\",\n            params={\n                'signal_data': signal_data,\n                'trace_id': trace_id\n            },\n            recipient='product_owner'\n        )\n        \n        response = await self.mcp_controller.route_message(evaluation_message, priority='high')\n        \n        if response and response.method == \"signal_evaluation_result\":\n            return response.params.get('evaluation', {})\n        else:\n            logger.error(f\"Failed to get strategic evaluation for {trace_id}\")\n            return {\n                'approved': False,\n                'confidence': 0.0,\n                'reasons': ['Strategic evaluation failed']\n            }\n    \n    def _apply_strategic_adjustments(self, signal_data: Dict[str, Any], strategic_decision: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Apply strategic adjustments to signal data\"\"\"\n        adjusted_signal = signal_data.copy()\n        adjustments = strategic_decision.get('adjustments', {})\n        \n        # Apply risk adjustments\n        if 'risk_reduction' in adjustments:\n            current_risk = adjusted_signal.get('risk_percent', 0.01)\n            adjusted_signal['risk_percent'] = current_risk * adjustments['risk_reduction']\n            \n        if 'risk_increase' in adjustments:\n            current_risk = adjusted_signal.get('risk_percent', 0.01)\n            adjusted_signal['risk_percent'] = current_risk * adjustments['risk_increase']\n        \n        # Apply target RR adjustments\n        if 'target_rr' in adjustments:\n            adjusted_signal['target_rr_ratio'] = adjustments['target_rr']\n        \n        # Add strategic metadata\n        adjusted_signal['strategic_metadata'] = {\n            'confidence': strategic_decision.get('confidence', 0.0),\n            'adjustments_applied': adjustments,\n            'strategy_match': strategic_decision.get('strategy_match', False)\n        }\n        \n        return adjusted_signal\n    \n    def _extract_trade_result(self, ucell_results: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Extract trade result for performance tracking\"\"\"\n        trade_result = {\n            'timestamp': datetime.utcnow().isoformat(),\n            'final_status': ucell_results.get('final_status'),\n            'pnl': 0.0,\n            'rr_ratio': 0.0,\n            'execution_latency_ms': ucell_results.get('total_latency_ms', 0)\n        }\n        \n        # Extract PnL from trade execution cell\n        if 'U4' in ucell_results.get('cell_outputs', {}):\n            u4_data = ucell_results['cell_outputs']['U4'].get('data', {})\n            trade_result['pnl'] = u4_data.get('pnl', 0.0)\n            trade_result['rr_ratio'] = u4_data.get('rr_achieved', 0.0)\n        \n        return trade_result\n    \n    async def _update_product_owner_performance(self, trade_result: Dict[str, Any], trace_id: str):\n        \"\"\"Update ProductOwner with trade results\"\"\"\n        performance_message = MCPMessage(\n            id=f\"perf_update_{trace_id}\",\n            method=\"update_performance\",\n            params={\n                'trade_result': trade_result,\n                'trace_id': trace_id\n            },\n            recipient='product_owner'\n        )\n        \n        await self.mcp_controller.route_message(performance_message, priority='normal')\n    \n    def _update_orchestration_metrics(self, pipeline_result: PipelineResult):\n        \"\"\"Update orchestration metrics\"\"\"\n        if pipeline_result.final_status == 'success':\n            self.orchestration_metrics['pipeline_completions'] += 1\n        elif pipeline_result.final_status in ['failed', 'pipeline_error']:\n            self.orchestration_metrics['pipeline_failures'] += 1\n        \n        # Update average latency\n        current_avg = self.orchestration_metrics['average_pipeline_latency_ms']\n        total_processed = self.orchestration_metrics['total_signals_processed']\n        new_latency = pipeline_result.total_latency_ms\n        \n        if total_processed > 0:\n            self.orchestration_metrics['average_pipeline_latency_ms'] = (\n                (current_avg * (total_processed - 1)) + new_latency\n            ) / total_processed\n    \n    async def _processing_loop(self):\n        \"\"\"Main processing loop for queued signals\"\"\"\n        while self.is_running:\n            try:\n                # Get signal from queue with timeout\n                signal_data = await asyncio.wait_for(\n                    self.processing_queue.get(),\n                    timeout=1.0\n                )\n                \n                # Process signal through pipeline\n                result = await self.process_trading_signal(signal_data)\n                \n                # Handle result (could emit events, store in DB, etc.)\n                await self._handle_pipeline_result(result)\n                \n            except asyncio.TimeoutError:\n                # No signal in queue, continue\n                continue\n            except Exception as e:\n                logger.error(f\"Processing loop error: {str(e)}\")\n    \n    async def _handle_pipeline_result(self, result: PipelineResult):\n        \"\"\"Handle completed pipeline result\"\"\"\n        if result.final_status == 'success':\n            logger.info(f\"Pipeline {result.pipeline_id} successful: Trade executed\")\n        elif result.final_status == 'strategically_rejected':\n            logger.info(f\"Pipeline {result.pipeline_id} strategically rejected\")\n        else:\n            logger.warning(f\"Pipeline {result.pipeline_id} failed: {result.final_status}\")\n    \n    async def add_signal_to_queue(self, signal_data: Dict[str, Any]):\n        \"\"\"Add signal to processing queue\"\"\"\n        await self.processing_queue.put(signal_data)\n    \n    def get_comprehensive_metrics(self) -> Dict[str, Any]:\n        \"\"\"Get comprehensive orchestration metrics\"\"\"\n        return {\n            'orchestration': self.orchestration_metrics,\n            'mcp_controller': self.mcp_controller.get_metrics(),\n            'product_owner': self.product_owner.get_comprehensive_status(),\n            'ucell_orchestrator': self.ucell_orchestrator.get_metrics(),\n            'active_pipelines': len(self.active_pipelines),\n            'completed_pipelines': len(self.completed_pipelines),\n            'system_status': {\n                'is_running': self.is_running,\n                'queue_size': self.processing_queue.qsize() if hasattr(self.processing_queue, 'qsize') else 0\n            }\n        }\n    \n    def get_pipeline_status(self, pipeline_id: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:\n        \"\"\"Get status of specific pipeline or all active pipelines\"\"\"\n        if pipeline_id:\n            if pipeline_id in self.active_pipelines:\n                return asdict(self.active_pipelines[pipeline_id])\n            else:\n                # Check completed pipelines\n                for completed in self.completed_pipelines:\n                    if completed.pipeline_id == pipeline_id:\n                        return asdict(completed)\n                return None\n        else:\n            return [asdict(pipeline) for pipeline in self.active_pipelines.values()]\n    \n    async def emergency_stop(self, reason: str = \"Emergency stop requested\"):\n        \"\"\"Emergency stop all processing\"\"\"\n        logger.critical(f\"EMERGENCY STOP: {reason}\")\n        \n        # Stop ProductOwner trading\n        await self.product_owner.send_message(\n            method=\"emergency_stop\",\n            params={'reason': reason}\n        )\n        \n        # Emergency shutdown MCP Controller\n        emergency_message = MCPMessage(\n            id=f\"emergency_{datetime.utcnow().timestamp()}\",\n            method=\"emergency_shutdown\",\n            params={'reason': reason}\n        )\n        \n        await self.mcp_controller.route_message(emergency_message, priority='critical')\n        \n        # Stop orchestrator\n        await self.stop()