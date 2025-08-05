"""
U-Cell Orchestrator
Manages the flow of data through the 5 deterministic U-Cells
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import logging
import uuid
from . import CellInput, CellOutput
from .signal_validation import SignalValidationCell
from .ml_analysis import MLAnalysisCell
from .risk_engine import RiskEngineCell
from .trade_execution import TradeExecutionCell
from .monitoring_control import MonitoringControlCell

logger = logging.getLogger(__name__)


class UCellOrchestrator:
    """
    Orchestrates the flow through U-Cells following FoxBox deterministic principles
    Ensures proper sequencing and error handling
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize U-Cells
        self.cells = {
            'U1': SignalValidationCell(),
            'U2': MLAnalysisCell(model_path=self.config.get('ml_model_path')),
            'U3': RiskEngineCell(account_config=self.config.get('account_config')),
            'U4': TradeExecutionCell(mt5_connection=self.config.get('mt5_connection')),
            'U5': MonitoringControlCell(alert_callback=self.config.get('alert_callback'))
        }
        
        # Define cell sequence
        self.cell_sequence = ['U1', 'U2', 'U3', 'U4', 'U5']
        
        # Orchestration metrics
        self.metrics = {
            'total_signals': 0,
            'successful_trades': 0,
            'rejected_signals': 0,
            'failed_executions': 0,
            'average_latency_ms': 0
        }
        
        # Active trades tracking
        self.active_trades = {}
        
        # Orchestration state
        self.is_running = True
        self.processing_queue = asyncio.Queue()
    
    async def process_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a trading signal through all U-Cells
        Returns the final result with complete trace
        """
        trace_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Processing signal {trace_id}: {signal_data.get('symbol')} {signal_data.get('pattern_type')}")
        
        # Create initial input
        cell_input = CellInput(
            timestamp=datetime.utcnow(),
            data=signal_data,
            metadata={'source': 'webhook', 'version': '1.0'},
            trace_id=trace_id
        )
        
        # Track results through pipeline
        pipeline_results = {
            'trace_id': trace_id,
            'start_time': start_time.isoformat(),
            'signal_data': signal_data,
            'cell_outputs': {},
            'final_status': None,
            'total_latency_ms': 0
        }
        
        try:
            # Process through each cell
            current_input = cell_input
            
            for cell_id in self.cell_sequence:
                cell = self.cells[cell_id]
                
                # Execute cell
                cell_start = datetime.utcnow()
                output = cell.execute(current_input)
                cell_latency = (datetime.utcnow() - cell_start).total_seconds() * 1000
                
                # Store result
                pipeline_results['cell_outputs'][cell_id] = {
                    'status': output.status,
                    'data': output.data,
                    'errors': output.errors,
                    'latency_ms': round(cell_latency, 2)
                }
                
                # Check if we should continue
                if output.status != 'success' or not output.next_cell:
                    pipeline_results['final_status'] = output.status
                    break
                
                # Prepare input for next cell
                current_input = CellInput(
                    timestamp=datetime.utcnow(),
                    data=output.data,
                    metadata={'previous_cell': cell_id},
                    previous_cell=cell_id,
                    trace_id=trace_id
                )
            
            # Calculate total latency
            total_latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            pipeline_results['total_latency_ms'] = round(total_latency, 2)
            
            # Update metrics
            self._update_metrics(pipeline_results)
            
            # Handle successful trade
            if pipeline_results['final_status'] == 'success' and 'U4' in pipeline_results['cell_outputs']:
                trade_data = pipeline_results['cell_outputs']['U4']['data']
                if 'order_id' in trade_data:
                    self.active_trades[trade_data['order_id']] = trade_data
            
            logger.info(f"Signal {trace_id} processing completed: {pipeline_results['final_status']}")
            
            return pipeline_results
            
        except Exception as e:
            logger.error(f"Orchestration error for {trace_id}: {str(e)}")
            pipeline_results['final_status'] = 'orchestration_error'
            pipeline_results['error'] = str(e)
            return pipeline_results
    
    async def process_signal_async(self, signal_data: Dict[str, Any]):
        """Add signal to processing queue"""
        await self.processing_queue.put(signal_data)
    
    async def run(self):
        """Run the orchestrator processing loop"""
        logger.info("U-Cell Orchestrator started")
        
        while self.is_running:
            try:
                # Get signal from queue with timeout
                signal_data = await asyncio.wait_for(
                    self.processing_queue.get(), 
                    timeout=1.0
                )
                
                # Process signal
                result = await self.process_signal(signal_data)
                
                # Handle result (could emit events, store in DB, etc.)
                await self._handle_result(result)
                
            except asyncio.TimeoutError:
                # No signal in queue, continue
                continue
            except Exception as e:
                logger.error(f"Processing loop error: {str(e)}")
    
    async def _handle_result(self, result: Dict[str, Any]):
        """Handle processing result"""
        # This could emit events, store in database, send notifications, etc.
        if result['final_status'] == 'success':
            logger.info(f"Trade executed successfully: {result['trace_id']}")
        elif result['final_status'] == 'rejected':
            logger.info(f"Signal rejected: {result['trace_id']}")
        else:
            logger.warning(f"Signal processing failed: {result['trace_id']}")
    
    def _update_metrics(self, pipeline_results: Dict[str, Any]):
        """Update orchestration metrics"""
        self.metrics['total_signals'] += 1
        
        if pipeline_results['final_status'] == 'success':
            self.metrics['successful_trades'] += 1
        elif pipeline_results['final_status'] == 'rejected':
            self.metrics['rejected_signals'] += 1
        elif pipeline_results['final_status'] == 'failed':
            self.metrics['failed_executions'] += 1
        
        # Update average latency
        current_avg = self.metrics['average_latency_ms']
        total = self.metrics['total_signals']
        new_latency = pipeline_results['total_latency_ms']
        self.metrics['average_latency_ms'] = ((current_avg * (total - 1)) + new_latency) / total
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestration metrics"""
        metrics = self.metrics.copy()
        
        # Add cell-specific metrics
        metrics['cell_metrics'] = {}
        for cell_id, cell in self.cells.items():
            metrics['cell_metrics'][cell_id] = cell.get_metrics()
        
        # Add active trades count
        metrics['active_trades'] = len(self.active_trades)
        
        return metrics
    
    def get_active_trades(self) -> Dict[str, Any]:
        """Get currently active trades"""
        return self.active_trades.copy()
    
    def update_trade_status(self, order_id: str, status_update: Dict[str, Any]):
        """Update status of an active trade"""
        if order_id in self.active_trades:
            self.active_trades[order_id].update(status_update)
            
            # If trade is closed, run through monitoring
            if status_update.get('status') == 'CLOSED':
                # Create monitoring input
                monitoring_input = CellInput(
                    timestamp=datetime.utcnow(),
                    data={**self.active_trades[order_id], **status_update},
                    metadata={'update_type': 'trade_closed'},
                    trace_id=self.active_trades[order_id].get('trace_id')
                )
                
                # Run monitoring
                self.cells['U5'].execute(monitoring_input)
                
                # Remove from active trades
                del self.active_trades[order_id]
    
    def shutdown(self):
        """Shutdown the orchestrator"""
        logger.info("Shutting down U-Cell Orchestrator")
        self.is_running = False
        
        # Close any open positions
        for order_id, trade in self.active_trades.items():
            logger.warning(f"Force closing trade {order_id} due to shutdown")
            # This would trigger actual position closing through U4
    
    def reset_daily_metrics(self):
        """Reset daily metrics (call at start of trading day)"""
        # Reset risk engine daily metrics
        self.cells['U3'].reset_daily_metrics()
        
        # Could reset other daily metrics as needed
        logger.info("Daily metrics reset completed")