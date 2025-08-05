from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Emergency Protocols for MT5 Crypto Demo Trading
Critical error handling and emergency stop procedures

Above Robust! operational standards for 24/7 crypto trading
"""

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import json

logger = logging.getLogger(__name__)


class EmergencyLevel(Enum):
    """Emergency severity levels"""
    LOW = "low"           # Warning condition
    MEDIUM = "medium"     # Requires attention
    HIGH = "high"         # Immediate action needed
    CRITICAL = "critical" # Emergency stop required


class EmergencyType(Enum):
    """Types of emergency conditions"""
    CONNECTION_LOST = "connection_lost"
    EXECUTION_FAILURE = "execution_failure"
    EXCESSIVE_LOSS = "excessive_loss"
    SYSTEM_ERROR = "system_error"
    ACCOUNT_SUSPENDED = "account_suspended"
    MARGIN_CALL = "margin_call"
    DATA_FEED_ERROR = "data_feed_error"
    POSITION_ERROR = "position_error"
    NETWORK_ERROR = "network_error"


class EmergencyProtocol:
    """
    Emergency protocol handler for crypto trading system
    
    Implements graduated response system:
    - Level 1: Warning alerts and monitoring
    - Level 2: Reduce trading activity
    - Level 3: Pause new orders
    - Level 4: Emergency stop all trading
    """
    
    def __init__(self, trading_environment):
        self.trading_env = trading_environment
        self.emergency_active = False
        self.emergency_history: List[Dict[str, Any]] = []
        
        # Emergency thresholds
        self.thresholds = {
            'max_consecutive_failures': 5,
            'max_loss_percentage': 10.0,
            'max_execution_time_ms': 1000.0,
            'min_success_rate': 0.90,
            'max_connection_downtime_minutes': 5
        }
        
        # Response procedures
        self.response_procedures = {
            EmergencyLevel.LOW: self._level_1_response,
            EmergencyLevel.MEDIUM: self._level_2_response,
            EmergencyLevel.HIGH: self._level_3_response,
            EmergencyLevel.CRITICAL: self._level_4_response
        }
        
        # Emergency callbacks
        self.emergency_callbacks: List[Callable] = []
        
        # Monitoring state
        self.monitoring_active = False
        self.last_check = datetime.now(timezone.utc)
        
        logger.info("Emergency Protocol System initialized")
    
    async def start_monitoring(self):
        """Start emergency monitoring system"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        logger.info(" Emergency monitoring STARTED")
        
        # Start monitoring tasks
        asyncio.create_task(self._connection_monitor())
        asyncio.create_task(self._performance_monitor())
        asyncio.create_task(self._position_monitor())
        asyncio.create_task(self._account_monitor())
    
    async def stop_monitoring(self):
        """Stop emergency monitoring"""
        self.monitoring_active = False
        logger.info("Emergency monitoring stopped")
    
    async def trigger_emergency(self, 
                              emergency_type: EmergencyType,
                              level: EmergencyLevel,
                              details: Dict[str, Any],
                              auto_recovery: bool = True):
        """Trigger emergency response protocol"""
        try:
            emergency_record = {
                'timestamp': datetime.now(timezone.utc),
                'type': emergency_type.value,
                'level': level.value,
                'details': details,
                'auto_recovery': auto_recovery,
                'response_actions': []
            }
            
            logger.critical(
                f" EMERGENCY TRIGGERED: {emergency_type.value.upper()} "
                f"(Level: {level.value.upper()})"
            )
            logger.critical(f"Details: {details}")
            
            # Execute response procedure
            response_actions = await self.response_procedures[level](
                emergency_type, details
            )
            emergency_record['response_actions'] = response_actions
            
            # Log emergency
            self.emergency_history.append(emergency_record)
            
            # Save emergency log
            await self._save_emergency_log(emergency_record)
            
            # Notify callbacks
            for callback in self.emergency_callbacks:
                try:
                    await callback(emergency_record)
                except Exception as e:
                    logger.error(f"Emergency callback error: {e}")
            
            # Auto-recovery if enabled
            if auto_recovery and level in [EmergencyLevel.LOW, EmergencyLevel.MEDIUM]:
                asyncio.create_task(self._attempt_recovery(emergency_type, details))
            
            return emergency_record
            
        except Exception as e:
            logger.error(f"Emergency trigger error: {e}")
            return None
    
    async def _level_1_response(self, emergency_type: EmergencyType, details: Dict[str, Any]) -> List[str]:
        """Level 1: Warning response - monitoring and alerts"""
        actions = []
        
        try:
            logger.warning(f"WARNING Level 1 Emergency Response: {emergency_type.value}")
            
            # Increase monitoring frequency
            actions.append("Increased monitoring frequency")
            
            # Log detailed system state
            if self.trading_env.trading_engine:
                stats = self.trading_env.trading_engine.get_execution_stats()
                logger.warning(f"System stats: {stats}")
                actions.append("Logged system statistics")
            
            # Check system health
            await self._comprehensive_health_check()
            actions.append("Performed health check")
            
            # Alert but continue trading
            logger.warning("Continuing trading with increased monitoring")
            actions.append("Continued trading with enhanced monitoring")
            
        except Exception as e:
            logger.error(f"Level 1 response error: {e}")
            actions.append(f"Response error: {e}")
        
        return actions
    
    async def _level_2_response(self, emergency_type: EmergencyType, details: Dict[str, Any]) -> List[str]:
        """Level 2: Reduce trading activity"""
        actions = []
        
        try:
            logger.error(f" Level 2 Emergency Response: {emergency_type.value}")
            
            # Reduce position sizes
            if self.trading_env.trading_engine:
                original_size = self.trading_env.trading_engine.max_position_size
                self.trading_env.trading_engine.max_position_size = original_size * 0.5
                actions.append(f"Reduced max position size to {original_size * 0.5}")
            
            # Cancel pending orders
            if self.trading_env.trading_engine:
                active_orders = list(self.trading_env.trading_engine.active_orders.keys())
                for order_id in active_orders:
                    await self.trading_env.trading_engine.cancel_order(order_id)
                actions.append(f"Cancelled {len(active_orders)} pending orders")
            
            # Implement tighter risk controls
            if self.trading_env.position_manager:
                # Reduce risk per trade
                original_risk = self.trading_env.position_manager.risk_per_trade
                self.trading_env.position_manager.risk_per_trade = original_risk * 0.5
                actions.append(f"Reduced risk per trade to {original_risk * 0.5}")
            
            # Continue trading with restrictions
            logger.error("Trading continues with reduced activity")
            actions.append("Implemented trading restrictions")
            
        except Exception as e:
            logger.error(f"Level 2 response error: {e}")
            actions.append(f"Response error: {e}")
        
        return actions
    
    async def _level_3_response(self, emergency_type: EmergencyType, details: Dict[str, Any]) -> List[str]:
        """Level 3: Pause new orders, manage existing positions"""
        actions = []
        
        try:
            logger.critical(f" Level 3 Emergency Response: {emergency_type.value}")
            
            # Disable new order submission
            if self.trading_env.trading_engine:
                self.trading_env.trading_engine.trading_enabled = False
                actions.append("Disabled new order submission")
            
            # Cancel all pending orders
            if self.trading_env.trading_engine:
                active_orders = list(self.trading_env.trading_engine.active_orders.keys())
                for order_id in active_orders:
                    await self.trading_env.trading_engine.cancel_order(order_id)
                actions.append(f"Cancelled all {len(active_orders)} pending orders")
            
            # Assess existing positions
            if self.trading_env.position_manager:
                positions = await self.trading_env.position_manager.get_all_positions()
                losing_positions = [p for p in positions if p['profit'] < 0]
                
                if len(losing_positions) > 3:  # Too many losing positions
                    # Close worst performing positions
                    worst_positions = sorted(losing_positions, key=lambda x: x['profit'])[:2]
                    for position in worst_positions:
                        await self.trading_env.mt5_connector.close_position(position['ticket'])
                    actions.append(f"Closed {len(worst_positions)} worst performing positions")
            
            # Wait for manual intervention or auto-recovery
            self.emergency_active = True
            actions.append("Trading paused - awaiting recovery or manual intervention")
            
        except Exception as e:
            logger.error(f"Level 3 response error: {e}")
            actions.append(f"Response error: {e}")
        
        return actions
    
    async def _level_4_response(self, emergency_type: EmergencyType, details: Dict[str, Any]) -> List[str]:
        """Level 4: Emergency stop all trading"""
        actions = []
        
        try:
            logger.critical(f" LEVEL 4 EMERGENCY STOP: {emergency_type.value}")
            
            # Emergency stop trading engine
            if self.trading_env.trading_engine:
                await self.trading_env.trading_engine.emergency_stop(
                    f"Level 4 emergency: {emergency_type.value}"
                )
                actions.append("Emergency stopped trading engine")
            
            # Close all positions immediately
            if self.trading_env.mt5_connector:
                positions = await self.trading_env.mt5_connector.get_positions()
                for position in positions:
                    try:
                        await self.trading_env.mt5_connector.close_position(position['ticket'])
                        actions.append(f"Emergency closed position {position['ticket']}")
                    except Exception as e:
                        logger.error(f"Failed to close position {position['ticket']}: {e}")
            
            # Disable all trading systems
            self.trading_env.trading_active = False
            self.emergency_active = True
            actions.append("Disabled all trading systems")
            
            # Generate emergency report
            await self._generate_emergency_report(emergency_type, details)
            actions.append("Generated emergency report")
            
            logger.critical(" EMERGENCY STOP COMPLETED - ALL TRADING HALTED")
            
        except Exception as e:
            logger.error(f"Level 4 response error: {e}")
            actions.append(f"Response error: {e}")
        
        return actions
    
    async def _connection_monitor(self):
        """Monitor MT5 connection status"""
        connection_failures = 0
        last_connection_check = datetime.now(timezone.utc)
        
        while self.monitoring_active:
            try:
                # Check MT5 connection
                if not self.trading_env.mt5_connector.is_connected:
                    connection_failures += 1
                    logger.warning(f"MT5 connection failure #{connection_failures}")
                    
                    if connection_failures >= 3:
                        await self.trigger_emergency(
                            EmergencyType.CONNECTION_LOST,
                            EmergencyLevel.HIGH,
                            {
                                'consecutive_failures': connection_failures,
                                'last_connected': last_connection_check.isoformat()
                            }
                        )
                    elif connection_failures >= 1:
                        await self.trigger_emergency(
                            EmergencyType.CONNECTION_LOST,
                            EmergencyLevel.MEDIUM,
                            {'consecutive_failures': connection_failures}
                        )
                else:
                    # Reset failure count on successful connection
                    if connection_failures > 0:
                        logger.info(f"MT5 connection restored after {connection_failures} failures")
                        connection_failures = 0
                    last_connection_check = datetime.now(timezone.utc)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Connection monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _performance_monitor(self):
        """Monitor trading performance metrics"""
        while self.monitoring_active:
            try:
                if self.trading_env.trading_engine:
                    stats = self.trading_env.trading_engine.get_execution_stats()
                    
                    # Check success rate
                    if stats['success_rate'] < self.thresholds['min_success_rate']:
                        await self.trigger_emergency(
                            EmergencyType.EXECUTION_FAILURE,
                            EmergencyLevel.HIGH,
                            {
                                'success_rate': stats['success_rate'],
                                'threshold': self.thresholds['min_success_rate'],
                                'failed_executions': stats['failed_executions']
                            }
                        )
                    
                    # Check execution time
                    if stats['avg_execution_time_ms'] > self.thresholds['max_execution_time_ms']:
                        await self.trigger_emergency(
                            EmergencyType.EXECUTION_FAILURE,
                            EmergencyLevel.MEDIUM,
                            {
                                'avg_execution_time': stats['avg_execution_time_ms'],
                                'threshold': self.thresholds['max_execution_time_ms']
                            }
                        )
                    
                    # Check consecutive failures
                    if stats['failed_executions'] >= self.thresholds['max_consecutive_failures']:
                        await self.trigger_emergency(
                            EmergencyType.EXECUTION_FAILURE,
                            EmergencyLevel.HIGH,
                            {
                                'consecutive_failures': stats['failed_executions']
                            }
                        )
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(120)
    
    async def _position_monitor(self):
        """Monitor position risks and P&L"""
        while self.monitoring_active:
            try:
                if self.trading_env.mt5_connector:
                    account_info = await self.trading_env.mt5_connector.get_account_info()
                    
                    if account_info:
                        balance = account_info['balance']
                        equity = account_info['equity']
                        margin_level = account_info.get('margin_level', 0)
                        
                        # Check drawdown
                        if balance > 0:
                            drawdown = (balance - equity) / balance * 100
                            
                            if drawdown > self.thresholds['max_loss_percentage']:
                                await self.trigger_emergency(
                                    EmergencyType.EXCESSIVE_LOSS,
                                    EmergencyLevel.CRITICAL,
                                    {
                                        'drawdown_percentage': drawdown,
                                        'balance': balance,
                                        'equity': equity,
                                        'loss_amount': balance - equity
                                    }
                                )
                            elif drawdown > self.thresholds['max_loss_percentage'] * 0.7:
                                await self.trigger_emergency(
                                    EmergencyType.EXCESSIVE_LOSS,
                                    EmergencyLevel.HIGH,
                                    {
                                        'drawdown_percentage': drawdown,
                                        'approaching_limit': True
                                    }
                                )
                        
                        # Check margin level
                        if margin_level > 0 and margin_level < 200:  # Approaching margin call
                            await self.trigger_emergency(
                                EmergencyType.MARGIN_CALL,
                                EmergencyLevel.HIGH,
                                {
                                    'margin_level': margin_level,
                                    'balance': balance,
                                    'equity': equity
                                }
                            )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Position monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _account_monitor(self):
        """Monitor account status and permissions"""
        while self.monitoring_active:
            try:
                if self.trading_env.mt5_connector:
                    account_info = await self.trading_env.mt5_connector.get_account_info()
                    
                    if account_info:
                        # Check trading permission
                        if not account_info.get('trade_allowed', True):
                            await self.trigger_emergency(
                                EmergencyType.ACCOUNT_SUSPENDED,
                                EmergencyLevel.CRITICAL,
                                {
                                    'trade_allowed': False,
                                    'account': account_info['login']
                                }
                            )
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Account monitor error: {e}")
                await asyncio.sleep(180)
    
    async def _comprehensive_health_check(self):
        """Perform comprehensive system health check"""
        try:
            health_report = {
                'timestamp': datetime.now(timezone.utc),
                'mt5_connected': self.trading_env.mt5_connector.is_connected if self.trading_env.mt5_connector else False,
                'trading_engine_active': self.trading_env.trading_engine.trading_enabled if self.trading_env.trading_engine else False,
                'positions_count': 0,
                'account_balance': 0,
                'system_errors': []
            }
            
            # Check positions
            if self.trading_env.position_manager:
                positions = await self.trading_env.position_manager.get_all_positions()
                health_report['positions_count'] = len(positions)
            
            # Check account
            if self.trading_env.mt5_connector:
                account_info = await self.trading_env.mt5_connector.get_account_info()
                if account_info:
                    health_report['account_balance'] = account_info['balance']
            
            logger.info(f"Health check: {health_report}")
            return health_report
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {'error': str(e)}
    
    async def _attempt_recovery(self, emergency_type: EmergencyType, details: Dict[str, Any]):
        """Attempt automatic recovery from emergency condition"""
        try:
            logger.info(f"Attempting auto-recovery for {emergency_type.value}")
            
            recovery_actions = []
            
            if emergency_type == EmergencyType.CONNECTION_LOST:
                # Attempt reconnection
                if self.trading_env.mt5_connector:
                    if await self.trading_env.mt5_connector.connect():
                        recovery_actions.append("Reconnected to MT5")
                        logger.info("OK Auto-recovery: MT5 reconnection successful")
                    else:
                        recovery_actions.append("Failed to reconnect to MT5")
            
            elif emergency_type == EmergencyType.DATA_FEED_ERROR:
                # Attempt to reconnect data feed
                if self.trading_env.crypto_connector:
                    if await self.trading_env.crypto_connector.connect():
                        recovery_actions.append("Reconnected crypto data feed")
                        logger.info("OK Auto-recovery: Crypto feed reconnection successful")
            
            elif emergency_type == EmergencyType.EXECUTION_FAILURE:
                # Reset trading engine if possible
                if self.trading_env.trading_engine:
                    # Reset circuit breaker
                    self.trading_env.trading_engine.circuit_breaker['is_open'] = False
                    self.trading_env.trading_engine.circuit_breaker['failure_count'] = 0
                    recovery_actions.append("Reset execution circuit breaker")
                    logger.info("OK Auto-recovery: Reset execution circuit breaker")
            
            # Log recovery attempt
            self.emergency_history.append({
                'timestamp': datetime.now(timezone.utc),
                'type': 'auto_recovery_attempt',
                'original_emergency': emergency_type.value,
                'recovery_actions': recovery_actions
            })
            
            return recovery_actions
            
        except Exception as e:
            logger.error(f"Auto-recovery error: {e}")
            return [f"Recovery failed: {e}"]
    
    async def _save_emergency_log(self, emergency_record: Dict[str, Any]):
        """Save emergency record to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"emergency_log_{timestamp}.json"
            
            with open(filename, 'w', encoding='ascii', errors='ignore') as f:
                # Convert datetime objects to strings for JSON serialization
                record_copy = emergency_record.copy()
                record_copy['timestamp'] = record_copy['timestamp'].isoformat()
                json.dump(record_copy, f, indent=2)
            
            logger.info(f"Emergency log saved: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save emergency log: {e}")
    
    async def _generate_emergency_report(self, emergency_type: EmergencyType, details: Dict[str, Any]):
        """Generate comprehensive emergency report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Get system state
            account_info = await self.trading_env.mt5_connector.get_account_info() if self.trading_env.mt5_connector else {}
            engine_stats = self.trading_env.trading_engine.get_execution_stats() if self.trading_env.trading_engine else {}
            
            report = f"""
 EMERGENCY STOP REPORT 
{'='*50}

EMERGENCY DETAILS:
  Type: {emergency_type.value.upper()}
  Timestamp: {datetime.now(timezone.utc)}
  Details: {details}

ACCOUNT STATUS:
  Account: {account_info.get('login', 'N/A')}
  Balance: {account_info.get('balance', 'N/A')} {account_info.get('currency', '')}
  Equity: {account_info.get('equity', 'N/A')} {account_info.get('currency', '')}
  Margin Level: {account_info.get('margin_level', 'N/A')}%
  Trade Allowed: {account_info.get('trade_allowed', 'N/A')}

TRADING STATISTICS:
  Total Orders: {engine_stats.get('total_orders', 0)}
  Success Rate: {engine_stats.get('success_rate', 0):.1%}
  Failed Orders: {engine_stats.get('failed_executions', 0)}
  Avg Execution: {engine_stats.get('avg_execution_time_ms', 0):.1f}ms

EMERGENCY HISTORY:
  Total Emergencies: {len(self.emergency_history)}
  Recent Emergencies: {[e['type'] for e in self.emergency_history[-5:]]}

SYSTEM STATE:
  MT5 Connected: {self.trading_env.mt5_connector.is_connected if self.trading_env.mt5_connector else False}
  Trading Active: {self.trading_env.trading_active}
  Emergency Active: {self.emergency_active}

{'='*50}
IMMEDIATE ACTIONS REQUIRED:
1. Review emergency details and root cause
2. Check account status and positions
3. Verify system connectivity
4. Plan recovery strategy
5. Manual intervention may be required

Report generated: {datetime.now(timezone.utc)}
{'='*50}
"""
            
            # Save report
            with open(f"emergency_report_{timestamp}.txt", "w") as f:
                f.write(report)
            
            logger.critical("Emergency report generated")
            print(report)  # Also print to console for immediate visibility
            
        except Exception as e:
            logger.error(f"Emergency report generation error: {e}")
    
    def register_emergency_callback(self, callback: Callable):
        """Register callback for emergency events"""
        self.emergency_callbacks.append(callback)
    
    def get_emergency_status(self) -> Dict[str, Any]:
        """Get current emergency system status"""
        return {
            'monitoring_active': self.monitoring_active,
            'emergency_active': self.emergency_active,
            'total_emergencies': len(self.emergency_history),
            'last_emergency': self.emergency_history[-1] if self.emergency_history else None,
            'thresholds': self.thresholds,
            'last_check': self.last_check
        }