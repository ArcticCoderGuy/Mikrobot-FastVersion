from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Production Integration Bridge
Connects Live Trading Engine with Error Recovery System

Session #3 - Production-Ready System
Above Robust! operational standards
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Import core components
from .live_trading_engine import LiveTradingEngine, TradingOrder, ExecutionResult, TradeResult
from .error_recovery_system import ErrorRecoverySystem, ErrorSeverity, RecoveryState

# Import connectors
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'connectors'))
from mt5_connector import MT5Connector, MT5Config

# Import MCP components
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from product_owner_agent import ProductOwnerAgent

logger = logging.getLogger(__name__)


class ProductionTradingSystem:
    """
    Production-grade trading system with integrated error recovery
    
    Features:
    - Unified Live Trading + Error Recovery
    - Above Robust! operational standards
    - Automated failover and recovery
    - Real-time health monitoring
    - ProductOwner integration
    """
    
    def __init__(self, mt5_config: MT5Config, product_owner: ProductOwnerAgent):
        self.mt5_config = mt5_config
        self.product_owner = product_owner
        
        # Initialize core components
        self.mt5_connector = MT5Connector(mt5_config)
        self.live_trading_engine: Optional[LiveTradingEngine] = None
        self.error_recovery_system: Optional[ErrorRecoverySystem] = None
        
        # System state
        self.is_initialized = False
        self.is_running = False
        
        # Performance metrics
        self.metrics = {
            'system_uptime_start': None,
            'total_orders': 0,
            'successful_orders': 0,
            'recovery_events': 0,
            'avg_response_time': 0.0
        }
        
        logger.info("Production Trading System created - Above Robust! standards")
    
    async def initialize(self) -> bool:
        """Initialize all system components"""
        try:
            logger.info("ROCKET Initializing Production Trading System...")
            
            # 1. Connect to MT5
            if not await self.mt5_connector.connect():
                logger.error("Failed to connect to MT5")
                return False
            
            logger.info("OK MT5 connection established")
            
            # 2. Initialize Live Trading Engine
            self.live_trading_engine = LiveTradingEngine(
                mt5_connector=self.mt5_connector,
                product_owner=self.product_owner,
                max_concurrent_orders=10
            )
            
            # 3. Initialize Error Recovery System
            self.error_recovery_system = ErrorRecoverySystem(
                mt5_connector=self.mt5_connector,
                product_owner=self.product_owner,
                live_trading_engine=self.live_trading_engine
            )
            
            # 4. Register callbacks for integration
            self._setup_integration_callbacks()
            
            # 5. Start error recovery monitoring
            if not await self.error_recovery_system.start_monitoring():
                logger.error("Failed to start error recovery monitoring")
                return False
            
            logger.info("OK Error Recovery System active")
            
            # 6. Start live trading engine
            if not await self.live_trading_engine.start_engine():
                logger.error("Failed to start live trading engine")
                return False
            
            logger.info("OK Live Trading Engine active")
            
            self.is_initialized = True
            self.metrics['system_uptime_start'] = datetime.now(timezone.utc)
            
            logger.info("TARGET Production Trading System READY - Above Robust! operational")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            await self._emergency_cleanup()
            return False
    
    async def start(self) -> bool:
        """Start the production trading system"""
        if not self.is_initialized:
            logger.error("System not initialized")
            return False
        
        try:
            self.is_running = True
            logger.info(" Production Trading System STARTED")
            return True
            
        except Exception as e:
            logger.error(f"System start failed: {e}")
            return False
    
    async def stop(self):
        """Stop the production trading system"""
        try:
            logger.info(" Stopping Production Trading System...")
            
            self.is_running = False
            
            # Stop components in reverse order
            if self.live_trading_engine:
                await self.live_trading_engine.emergency_stop("System shutdown")
            
            if self.error_recovery_system:
                await self.error_recovery_system.stop_monitoring()
            
            if self.mt5_connector:
                await self.mt5_connector.disconnect()
            
            logger.info(" Production Trading System STOPPED")
            
        except Exception as e:
            logger.error(f"System stop error: {e}")
    
    async def submit_order(self, order: TradingOrder) -> str:
        """Submit order through production system with error handling"""
        if not self.is_running:
            await self.error_recovery_system.report_error(
                "production_system",
                "system_not_running",
                ErrorSeverity.HIGH,
                "Order submitted while system not running"
            )
            return ""
        
        try:
            # Submit order through live trading engine
            order_id = await self.live_trading_engine.submit_order(order)
            
            if order_id:
                self.metrics['total_orders'] += 1
                self.metrics['successful_orders'] += 1
            else:
                # Report error if order submission failed
                await self.error_recovery_system.report_error(
                    "live_trading_engine",
                    "order_submission_failed",
                    ErrorSeverity.MEDIUM,
                    f"Order submission failed for {order.symbol}",
                    context={'order_id': order.order_id, 'symbol': order.symbol}
                )
            
            return order_id
            
        except Exception as e:
            await self.error_recovery_system.report_error(
                "production_system",
                "order_submission_error",
                ErrorSeverity.HIGH,
                f"Order submission error: {str(e)}",
                context={'order_id': order.order_id, 'error': str(e)}
            )
            return ""
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order through production system"""
        try:
            return await self.live_trading_engine.cancel_order(order_id)
            
        except Exception as e:
            await self.error_recovery_system.report_error(
                "live_trading_engine",
                "order_cancellation_error",
                ErrorSeverity.MEDIUM,
                f"Order cancellation error: {str(e)}",
                context={'order_id': order_id}
            )
            return False
    
    def _setup_integration_callbacks(self):
        """Setup callbacks for component integration"""
        
        # Execution result callback
        def on_execution_result(result: ExecutionResult):
            """Handle execution results"""
            try:
                if result.result == TradeResult.FAILED:
                    # Report execution failure
                    asyncio.create_task(self.error_recovery_system.report_error(
                        "live_trading_engine",
                        "execution_failed",
                        ErrorSeverity.MEDIUM,
                        f"Order execution failed: {result.error_message}",
                        context={
                            'order_id': result.order_id,
                            'execution_time': result.execution_time_ms,
                            'error': result.error_message
                        }
                    ))
                elif result.execution_time_ms > 1000:  # >1 second
                    # Report slow execution
                    asyncio.create_task(self.error_recovery_system.report_error(
                        "live_trading_engine",
                        "slow_execution",
                        ErrorSeverity.LOW,
                        f"Slow execution: {result.execution_time_ms}ms",
                        context={
                            'order_id': result.order_id,
                            'execution_time': result.execution_time_ms
                        }
                    ))
                
            except Exception as e:
                logger.error(f"Execution result callback error: {e}")
        
        # Register callback
        if self.live_trading_engine:
            self.live_trading_engine.register_execution_callback(on_execution_result)
        
        # Recovery state change callback
        def on_recovery_state_change(old_state: RecoveryState, new_state: RecoveryState):
            """Handle recovery state changes"""
            try:
                self.metrics['recovery_events'] += 1
                
                if new_state == RecoveryState.CRITICAL:
                    # Emergency stop on critical state
                    if self.live_trading_engine:
                        asyncio.create_task(
                            self.live_trading_engine.emergency_stop("Critical recovery state")
                        )
                
                logger.info(f"Recovery state changed: {old_state.value} -> {new_state.value}")
                
            except Exception as e:
                logger.error(f"Recovery state callback error: {e}")
        
        # Register callback
        if self.error_recovery_system:
            self.error_recovery_system.register_state_change_callback(on_recovery_state_change)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            status = {
                'system': {
                    'initialized': self.is_initialized,
                    'running': self.is_running,
                    'uptime_hours': 0.0
                },
                'metrics': self.metrics.copy(),
                'mt5_connection': None,
                'trading_engine': None,
                'error_recovery': None
            }
            
            # Calculate uptime
            if self.metrics['system_uptime_start']:
                uptime = datetime.now(timezone.utc) - self.metrics['system_uptime_start']
                status['system']['uptime_hours'] = round(uptime.total_seconds() / 3600, 2)
            
            # MT5 status
            if self.mt5_connector:
                status['mt5_connection'] = self.mt5_connector.get_metrics()
            
            # Trading engine status
            if self.live_trading_engine:
                status['trading_engine'] = self.live_trading_engine.get_execution_stats()
            
            # Error recovery status
            if self.error_recovery_system:
                status['error_recovery'] = self.error_recovery_system.get_system_health()
            
            return status
            
        except Exception as e:
            logger.error(f"System status error: {e}")
            return {'error': str(e)}
    
    async def force_recovery(self, component: str, reason: str = "Manual recovery") -> bool:
        """Force recovery of specific component"""
        if not self.error_recovery_system:
            return False
        
        return await self.error_recovery_system.force_recovery(component, reason)
    
    async def emergency_stop(self, reason: str = "Manual emergency stop"):
        """Emergency stop all trading activities"""
        logger.critical(f" EMERGENCY STOP: {reason}")
        
        try:
            # Stop trading engine
            if self.live_trading_engine:
                await self.live_trading_engine.emergency_stop(reason)
            
            # Report to error recovery
            if self.error_recovery_system:
                await self.error_recovery_system.report_error(
                    "production_system",
                    "emergency_stop",
                    ErrorSeverity.CRITICAL,
                    reason
                )
            
            self.is_running = False
            
        except Exception as e:
            logger.error(f"Emergency stop error: {e}")
    
    async def _emergency_cleanup(self):
        """Emergency cleanup on initialization failure"""
        try:
            if self.error_recovery_system:
                await self.error_recovery_system.stop_monitoring()
            
            if self.mt5_connector:
                await self.mt5_connector.disconnect()
            
        except Exception as e:
            logger.error(f"Emergency cleanup error: {e}")
    
    def get_live_trading_engine(self) -> Optional[LiveTradingEngine]:
        """Get live trading engine instance"""
        return self.live_trading_engine
    
    def get_error_recovery_system(self) -> Optional[ErrorRecoverySystem]:
        """Get error recovery system instance"""
        return self.error_recovery_system
    
    def get_mt5_connector(self) -> Optional[MT5Connector]:
        """Get MT5 connector instance"""
        return self.mt5_connector


# Production system factory
async def create_production_system(
    mt5_config: MT5Config,
    product_owner: ProductOwnerAgent
) -> ProductionTradingSystem:
    """Factory function to create and initialize production system"""
    
    system = ProductionTradingSystem(mt5_config, product_owner)
    
    if await system.initialize():
        logger.info("OK Production system created and initialized")
        return system
    else:
        logger.error("ERROR Production system initialization failed")
        raise Exception("Failed to initialize production trading system")