#!/usr/bin/env python3
"""
Async Execution Service
Orchestrates trading execution with high-performance async patterns
Replaces multiple execution scripts with unified service architecture
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Local imports
from ..core.trading_engine import TradingEngine, TradeRequest, ExecutionResult, TradeDirection
from ..core.signal_processor import SignalProcessor, ProcessedSignal
# Import with fallback for missing dependencies
try:
    from ..config.settings import TradingConfig
except ImportError:
    # Use trading engine's fallback config
    from ..core.trading_engine import TradingConfig
from ..utils.encoding_utils import ASCIIFileManager, ascii_print
from ..utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class ServiceMode(Enum):
    LIVE = "LIVE"
    PAPER = "PAPER"
    BACKTEST = "BACKTEST"
    MONITOR = "MONITOR"


class ExecutionStrategy(Enum):
    IMMEDIATE = "IMMEDIATE"  # Execute immediately when signal received
    BATCHED = "BATCHED"     # Batch multiple signals together
    SCHEDULED = "SCHEDULED" # Execute at specific times
    CONTINUOUS = "CONTINUOUS" # Continuous monitoring and execution


@dataclass
class ServiceConfig:
    """Execution service configuration"""
    mode: ServiceMode = ServiceMode.LIVE
    strategy: ExecutionStrategy = ExecutionStrategy.CONTINUOUS
    max_concurrent_executions: int = 5
    signal_check_interval: int = 5  # seconds
    max_signals_per_batch: int = 10
    enable_risk_management: bool = True
    enable_performance_monitoring: bool = True
    log_level: str = "INFO"


class ExecutionService:
    """
    High-performance async execution service
    Replaces all standalone execute_*.py files with unified orchestration
    """
    
    def __init__(self, config: ServiceConfig = None):
        self.config = config or ServiceConfig()
        self.trading_config = TradingConfig()
        
        # Core components
        self.trading_engine: Optional[TradingEngine] = None
        self.signal_processor: Optional[SignalProcessor] = None
        self.performance_monitor = PerformanceMonitor()
        
        # Service state
        self.is_running = False
        self.is_initialized = False
        self._stop_event = asyncio.Event()
        self._execution_semaphore = asyncio.Semaphore(self.config.max_concurrent_executions)
        
        # Execution tracking
        self.active_executions: Dict[str, asyncio.Task] = {}
        self.execution_history: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.service_metrics = {
            'service_start_time': None,
            'total_signals_processed': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time_ms': 0.0,
            'signals_per_minute': 0.0,
            'uptime_percentage': 0.0
        }
        
        # Initialize logging
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize ASCII output
        ASCIIFileManager.initialize_ascii_output()
    
    async def initialize(self) -> bool:
        """Initialize execution service and all components"""
        try:
            ascii_print("EXECUTION SERVICE INITIALIZATION")
            ascii_print("=" * 38)
            ascii_print(f"Mode: {self.config.mode.value}")
            ascii_print(f"Strategy: {self.config.strategy.value}")
            ascii_print(f"Max Concurrent: {self.config.max_concurrent_executions}")
            ascii_print("")
            
            # Initialize trading engine
            self.trading_engine = TradingEngine(self.trading_config)
            if not await self.trading_engine.initialize():
                ascii_print("ERROR: Failed to initialize trading engine")
                return False
            
            # Initialize signal processor
            self.signal_processor = SignalProcessor()
            if not await self.signal_processor.initialize():
                ascii_print("ERROR: Failed to initialize signal processor")
                return False
            
            # Initialize performance monitoring
            await self.performance_monitor.initialize()
            
            self.is_initialized = True
            self.service_metrics['service_start_time'] = datetime.now()
            
            ascii_print("Execution service initialized successfully")
            ascii_print("Ready for signal processing and trade execution")
            ascii_print("")
            
            return True
            
        except Exception as e:
            logger.error(f"Execution service initialization failed: {str(e)}")
            ascii_print(f"ERROR: Initialization failed - {str(e)}")
            return False
    
    async def start(self) -> bool:
        """Start the execution service"""
        if not self.is_initialized:
            if not await self.initialize():
                return False
        
        self.is_running = True
        self._stop_event.clear()
        
        ascii_print("EXECUTION SERVICE STARTED")
        ascii_print("=" * 27)
        ascii_print(f"Timestamp: {datetime.now().isoformat()}")
        ascii_print(f"Strategy: {self.config.strategy.value}")
        ascii_print("")
        
        try:
            # Start appropriate execution strategy
            if self.config.strategy == ExecutionStrategy.CONTINUOUS:
                await self._run_continuous_monitoring()
            elif self.config.strategy == ExecutionStrategy.IMMEDIATE:
                await self._run_immediate_execution()
            elif self.config.strategy == ExecutionStrategy.BATCHED:
                await self._run_batched_execution()
            elif self.config.strategy == ExecutionStrategy.SCHEDULED:
                await self._run_scheduled_execution()
            
            return True
            
        except Exception as e:
            logger.error(f"Execution service runtime error: {str(e)}")
            ascii_print(f"ERROR: Service runtime error - {str(e)}")
            return False
        finally:
            self.is_running = False
    
    async def stop(self):
        """Stop the execution service gracefully"""
        ascii_print("EXECUTION SERVICE STOPPING")
        ascii_print("=" * 27)
        
        self.is_running = False
        self._stop_event.set()
        
        # Wait for active executions to complete
        if self.active_executions:
            ascii_print(f"Waiting for {len(self.active_executions)} active executions to complete...")
            
            # Wait up to 30 seconds for clean shutdown
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.active_executions.values(), return_exceptions=True),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                ascii_print("WARNING: Some executions did not complete within timeout")
                # Cancel remaining tasks
                for task in self.active_executions.values():
                    task.cancel()
        
        # Shutdown components
        if self.trading_engine:
            await self.trading_engine.shutdown()
        
        # Display final metrics
        await self._display_final_metrics()
        
        ascii_print("Execution service stopped")
        ascii_print("")
    
    async def execute_single_signal(self, signal_data: Union[Dict[str, Any], str, Path]) -> ExecutionResult:
        """Execute a single signal (replaces individual execute_*.py files)"""
        execution_id = f"exec_{datetime.now().strftime('%H%M%S_%f')}"
        
        async with self._execution_semaphore:
            try:
                # Process the signal
                processed_signal = await self.signal_processor.process_signal(signal_data)
                
                if not processed_signal.valid:
                    return ExecutionResult(
                        success=False,
                        error_message=f"Invalid signal: {processed_signal.reason}"
                    )
                
                # Execute the trade
                result = await self.trading_engine.execute_signal(processed_signal.__dict__)
                
                # Update metrics
                self.service_metrics['total_signals_processed'] += 1
                if result.success:
                    self.service_metrics['successful_executions'] += 1
                else:
                    self.service_metrics['failed_executions'] += 1
                
                # Log execution
                await self._log_execution(execution_id, processed_signal, result)
                
                return result
                
            except Exception as e:
                logger.error(f"Single signal execution error: {str(e)}")
                self.service_metrics['failed_executions'] += 1
                
                return ExecutionResult(
                    success=False,
                    error_message=f"Execution error: {str(e)}"
                )
    
    async def execute_multiple_signals(self, signals: List[Union[Dict[str, Any], str, Path]]) -> List[ExecutionResult]:
        """Execute multiple signals in parallel (replaces execute_multi_asset_signals.py)"""
        ascii_print(f"MULTI-SIGNAL EXECUTION: {len(signals)} signals")
        ascii_print("=" * 35)
        
        # Create execution tasks
        tasks = []
        for i, signal in enumerate(signals):
            task = asyncio.create_task(
                self.execute_single_signal(signal),
                name=f"signal_exec_{i}"
            )
            tasks.append(task)
        
        # Execute with controlled concurrency
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        execution_results = []
        successful_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                execution_results.append(ExecutionResult(
                    success=False,
                    error_message=f"Exception in signal {i}: {str(result)}"
                ))
            else:
                execution_results.append(result)
                if result.success:
                    successful_count += 1
        
        ascii_print(f"MULTI-SIGNAL RESULTS: {successful_count}/{len(signals)} successful")
        ascii_print("")
        
        return execution_results
    
    async def _run_continuous_monitoring(self):
        """Run continuous signal monitoring and execution"""
        ascii_print("Starting continuous monitoring mode...")
        
        while not self._stop_event.is_set():
            try:
                # Check for new signals
                current_signal = await self.signal_processor.read_current_signal()
                
                if current_signal and current_signal.valid:
                    # Check if this signal has already been processed
                    signal_id = f"{current_signal.symbol}_{current_signal.timestamp.isoformat()}"
                    
                    if signal_id not in self.active_executions:
                        # Create execution task
                        task = asyncio.create_task(
                            self._execute_with_tracking(signal_id, current_signal),
                            name=f"exec_{signal_id}"
                        )
                        self.active_executions[signal_id] = task
                
                # Clean up completed executions
                await self._cleanup_completed_executions()
                
                # Wait before next check
                await asyncio.sleep(self.config.signal_check_interval)
                
            except Exception as e:
                logger.error(f"Continuous monitoring error: {str(e)}")
                await asyncio.sleep(self.config.signal_check_interval)
    
    async def _run_immediate_execution(self):
        """Run immediate execution mode - execute as soon as signal is received"""
        ascii_print("Starting immediate execution mode...")
        ascii_print("Waiting for signals...")
        
        while not self._stop_event.is_set():
            try:
                current_signal = await self.signal_processor.read_current_signal()
                
                if current_signal and current_signal.valid:
                    result = await self.trading_engine.execute_signal(current_signal.__dict__)
                    
                    if result.success:
                        ascii_print(f"IMMEDIATE EXECUTION SUCCESS: {current_signal.symbol} {current_signal.direction}")
                    else:
                        ascii_print(f"IMMEDIATE EXECUTION FAILED: {result.error_message}")
                
                # Short delay to prevent excessive polling
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Immediate execution error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _run_batched_execution(self):
        """Run batched execution mode - collect signals and execute in batches"""
        ascii_print("Starting batched execution mode...")
        
        signal_batch = []
        last_batch_time = datetime.now()
        batch_interval = timedelta(minutes=5)  # Execute batch every 5 minutes
        
        while not self._stop_event.is_set():
            try:
                # Check for new signals
                current_signal = await self.signal_processor.read_current_signal()
                
                if current_signal and current_signal.valid:
                    signal_batch.append(current_signal)
                    ascii_print(f"Added signal to batch: {current_signal.symbol} (batch size: {len(signal_batch)})")
                
                # Execute batch if conditions met
                now = datetime.now()
                should_execute_batch = (
                    len(signal_batch) >= self.config.max_signals_per_batch or
                    (signal_batch and now - last_batch_time >= batch_interval)
                )
                
                if should_execute_batch:
                    ascii_print(f"Executing batch of {len(signal_batch)} signals")
                    
                    # Convert signals to dict format for execute_multiple_signals
                    signal_dicts = [signal.__dict__ for signal in signal_batch]
                    results = await self.execute_multiple_signals(signal_dicts)
                    
                    # Reset batch
                    signal_batch.clear()
                    last_batch_time = now
                    
                    successful = sum(1 for r in results if r.success)
                    ascii_print(f"Batch execution completed: {successful}/{len(results)} successful")
                
                await asyncio.sleep(self.config.signal_check_interval)
                
            except Exception as e:
                logger.error(f"Batched execution error: {str(e)}")
                await asyncio.sleep(self.config.signal_check_interval)
    
    async def _run_scheduled_execution(self):
        """Run scheduled execution mode - execute at specific times"""
        ascii_print("Starting scheduled execution mode...")
        # Implementation would depend on specific scheduling requirements
        # This is a placeholder for custom scheduling logic
        pass
    
    async def _execute_with_tracking(self, execution_id: str, signal: ProcessedSignal) -> ExecutionResult:
        """Execute signal with full tracking and error handling"""
        start_time = datetime.now()
        
        try:
            ascii_print(f"EXECUTING: {signal.symbol} {signal.direction} (ID: {execution_id})")
            
            # Execute the signal
            result = await self.trading_engine.execute_signal(signal.__dict__)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update metrics
            self._update_execution_time_metric(execution_time)
            
            if result.success:
                ascii_print(f"SUCCESS: {execution_id} completed in {execution_time:.2f}ms")
                self.service_metrics['successful_executions'] += 1
            else:
                ascii_print(f"FAILED: {execution_id} - {result.error_message}")
                self.service_metrics['failed_executions'] += 1
            
            # Log the execution
            await self._log_execution(execution_id, signal, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Execution tracking error for {execution_id}: {str(e)}")
            self.service_metrics['failed_executions'] += 1
            
            return ExecutionResult(
                success=False,
                error_message=f"Tracking error: {str(e)}"
            )
        finally:
            # Remove from active executions
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
    
    async def _cleanup_completed_executions(self):
        """Clean up completed execution tasks"""
        completed_ids = []
        
        for execution_id, task in self.active_executions.items():
            if task.done():
                completed_ids.append(execution_id)
        
        for execution_id in completed_ids:
            del self.active_executions[execution_id]
    
    async def _log_execution(self, execution_id: str, signal: ProcessedSignal, result: ExecutionResult):
        """Log execution details for audit and analysis"""
        log_entry = {
            'execution_id': execution_id,
            'timestamp': datetime.now().isoformat(),
            'signal': {
                'symbol': signal.symbol,
                'direction': signal.direction,
                'signal_type': signal.signal_type.value,
                'confidence': signal.confidence,
                'strategy': signal.strategy
            },
            'result': {
                'success': result.success,
                'ticket': result.ticket,
                'fill_price': result.fill_price,
                'volume': result.volume,
                'latency_ms': result.latency_ms,
                'error_message': result.error_message
            },
            'service_metrics': self.get_metrics()
        }
        
        # Add to execution history
        self.execution_history.append(log_entry)
        
        # Keep only last 1000 executions in memory
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
        
        # Log to file
        log_file = Path('logs/execution_service.json')
        log_file.parent.mkdir(exist_ok=True)
        
        ASCIIFileManager.log_to_file(
            str(log_file),
            f"Execution: {execution_id} - {signal.symbol} {signal.direction} - Success: {result.success}"
        )
    
    def _update_execution_time_metric(self, execution_time_ms: float):
        """Update average execution time metric"""
        total_executions = self.service_metrics['successful_executions'] + self.service_metrics['failed_executions']
        current_avg = self.service_metrics['average_execution_time_ms']
        
        if total_executions > 0:
            self.service_metrics['average_execution_time_ms'] = (
                (current_avg * (total_executions - 1) + execution_time_ms) / total_executions
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics"""
        now = datetime.now()
        start_time = self.service_metrics['service_start_time']
        
        if start_time:
            uptime_seconds = (now - start_time).total_seconds()
            uptime_percentage = 100.0 if self.is_running else 0.0
            
            # Calculate signals per minute
            if uptime_seconds > 0:
                signals_per_minute = (self.service_metrics['total_signals_processed'] * 60) / uptime_seconds
            else:
                signals_per_minute = 0.0
        else:
            uptime_percentage = 0.0
            signals_per_minute = 0.0
        
        base_metrics = {
            **self.service_metrics,
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'active_executions': len(self.active_executions),
            'uptime_percentage': round(uptime_percentage, 2),
            'signals_per_minute': round(signals_per_minute, 2)
        }
        
        # Add component metrics
        if self.trading_engine:
            base_metrics['trading_engine'] = self.trading_engine.get_metrics()
        
        if self.signal_processor:
            base_metrics['signal_processor'] = self.signal_processor.get_metrics()
        
        return base_metrics
    
    async def _display_final_metrics(self):
        """Display final service metrics on shutdown"""
        metrics = self.get_metrics()
        
        ascii_print("FINAL SERVICE METRICS")
        ascii_print("=" * 22)
        ascii_print(f"Total signals processed: {metrics['total_signals_processed']}")
        ascii_print(f"Successful executions: {metrics['successful_executions']}")
        ascii_print(f"Failed executions: {metrics['failed_executions']}")
        
        if metrics['total_signals_processed'] > 0:
            success_rate = metrics['successful_executions'] / metrics['total_signals_processed']
            ascii_print(f"Success rate: {success_rate:.1%}")
        
        ascii_print(f"Average execution time: {metrics['average_execution_time_ms']:.2f}ms")
        ascii_print(f"Signals per minute: {metrics['signals_per_minute']:.2f}")
        ascii_print("")


# Convenience functions for backward compatibility
async def run_execution_service(config: ServiceConfig = None) -> bool:
    """Run execution service with given configuration"""
    service = ExecutionService(config)
    
    try:
        return await service.start()
    except KeyboardInterrupt:
        ascii_print("Service interrupted by user")
        return True
    finally:
        await service.stop()


async def execute_legacy_simple() -> bool:
    """Legacy compatibility for execute_compliant_simple.py"""
    config = ServiceConfig(
        mode=ServiceMode.LIVE,
        strategy=ExecutionStrategy.IMMEDIATE
    )
    
    service = ExecutionService(config)
    
    if not await service.initialize():
        return False
    
    try:
        # Create a simple EUR/JPY signal
        signal_data = {
            'symbol': 'EURJPY',
            'trade_direction': 'SELL',
            'timestamp': datetime.now().isoformat(),
            'strategy': 'LEGACY_SIMPLE'
        }
        
        result = await service.execute_single_signal(signal_data)
        return result.success
        
    finally:
        await service.stop()


async def execute_legacy_multi_asset() -> bool:
    """Legacy compatibility for execute_multi_asset_signals.py"""
    config = ServiceConfig(
        mode=ServiceMode.LIVE,
        strategy=ExecutionStrategy.BATCHED
    )
    
    service = ExecutionService(config)
    
    if not await service.initialize():
        return False
    
    try:
        # Create sample multi-asset signals
        signals = [
            {
                'symbol': 'EURJPY',
                'trade_direction': 'SELL',
                'timestamp': datetime.now().isoformat(),
                'strategy': 'LEGACY_MULTI'
            },
            {
                'symbol': '_FERRARI.IT',
                'trade_direction': 'BUY',
                'timestamp': datetime.now().isoformat(),
                'strategy': 'LEGACY_MULTI'
            }
        ]
        
        results = await service.execute_multiple_signals(signals)
        return all(result.success for result in results)
        
    finally:
        await service.stop()


if __name__ == "__main__":
    # Default continuous execution
    config = ServiceConfig(
        mode=ServiceMode.LIVE,
        strategy=ExecutionStrategy.CONTINUOUS
    )
    
    asyncio.run(run_execution_service(config))
