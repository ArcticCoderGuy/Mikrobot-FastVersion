from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Production Position Management System
Real-time P&L tracking and automated risk controls

Session #3 - Production-Ready System
PRIORITY 2: Business intelligence and risk management
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import threading
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict, deque
import uuid

# Import existing components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'connectors'))
from mt5_connector import MT5Connector

# Import MCP and ProductOwner from Session #1
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from mcp_controller import MCPMessage, MessageType
from product_owner_agent import ProductOwnerAgent

# Import live trading components
from .live_trading_engine import TradingOrder, ExecutionResult, TradeResult, OrderStatus
from .error_recovery_system import ErrorRecoverySystem, ErrorSeverity

logger = logging.getLogger(__name__)


class PositionStatus(Enum):
    """Position status states"""
    OPEN = "open"
    CLOSED = "closed"
    CLOSING = "closing"
    FAILED = "failed"


class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Position:
    """Position data structure"""
    position_id: str
    order_id: str
    mt5_ticket: int
    symbol: str
    side: str  # BUY/SELL
    volume: float
    entry_price: float
    current_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # P&L tracking
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    commission: float = 0.0
    swap: float = 0.0
    
    # Risk metrics
    risk_amount: float = 0.0
    risk_reward_ratio: float = 0.0
    max_favorable_excursion: float = 0.0
    max_adverse_excursion: float = 0.0
    
    # Timestamps
    open_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    close_time: Optional[datetime] = None
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Status and metadata
    status: PositionStatus = PositionStatus.OPEN
    strategy_id: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    
    # Performance tracking
    duration_minutes: float = 0.0
    price_updates: int = 0
    max_drawdown: float = 0.0


@dataclass
class PortfolioSummary:
    """Portfolio summary metrics"""
    timestamp: datetime
    total_equity: float
    available_margin: float
    used_margin: float
    margin_level: float
    
    # P&L metrics
    daily_pnl: float = 0.0
    weekly_pnl: float = 0.0
    monthly_pnl: float = 0.0
    total_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    
    # Position metrics
    open_positions: int = 0
    total_volume: float = 0.0
    total_risk: float = 0.0
    
    # Performance metrics
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    
    # Risk metrics
    risk_exposure: float = 0.0
    portfolio_heat: float = 0.0  # Combined risk percentage
    var_95: float = 0.0  # Value at Risk (95%)


class PositionManager:
    """
    Production Position Management System
    
    Features:
    - Sub-second P&L updates
    - Automated risk controls
    - Real-time position tracking
    - Portfolio analytics
    - Risk management automation
    - ProductOwner integration
    """
    
    def __init__(self, 
                 mt5_connector: MT5Connector,
                 product_owner: ProductOwnerAgent,
                 error_recovery: ErrorRecoverySystem):
        
        self.mt5_connector = mt5_connector
        self.product_owner = product_owner
        self.error_recovery = error_recovery
        
        # Position tracking
        self.positions: Dict[str, Position] = {}
        self.closed_positions: Dict[str, Position] = {}
        self.position_history: deque = deque(maxlen=10000)
        
        # Portfolio state
        self.portfolio_summary = PortfolioSummary(
            timestamp=datetime.now(timezone.utc),
            total_equity=0.0,
            available_margin=0.0,
            used_margin=0.0,
            margin_level=0.0
        )
        
        # Risk management
        self.risk_config = {
            'max_daily_loss': -500.0,  # EUR500 daily loss limit
            'max_position_risk': 100.0,  # EUR100 per position
            'max_portfolio_risk': 1000.0,  # EUR1000 total portfolio risk
            'max_positions': 10,
            'margin_call_level': 100.0,  # 100% margin level
            'stop_out_level': 50.0,  # 50% margin level
            'max_correlation': 0.7  # Position correlation limit
        }
        
        # Performance tracking
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'largest_win': 0.0,
            'largest_loss': 0.0,
            'consecutive_wins': 0,
            'consecutive_losses': 0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0
        }
        
        # Real-time updates
        self.update_interval = 1.0  # 1 second updates
        self.monitoring_active = False
        self.update_lock = threading.Lock()
        self.position_callbacks: List[Callable[[Position], None]] = []
        self.portfolio_callbacks: List[Callable[[PortfolioSummary], None]] = []
        
        # Risk alerts
        self.risk_alerts_active = True
        self.alert_thresholds = {
            'daily_loss_warning': -250.0,  # EUR250 warning
            'position_risk_warning': 75.0,  # EUR75 position risk
            'margin_level_warning': 150.0,  # 150% margin level
            'correlation_warning': 0.6  # 60% correlation warning
        }
        
        # Background tasks
        self.monitoring_tasks: Set[asyncio.Task] = set()
        
        logger.info("Production Position Manager initialized")
    
    async def start_monitoring(self) -> bool:
        """Start real-time position monitoring"""
        try:
            self.monitoring_active = True
            
            # Start position update task
            update_task = asyncio.create_task(self._position_update_loop())
            self.monitoring_tasks.add(update_task)
            
            # Start risk monitoring task
            risk_task = asyncio.create_task(self._risk_monitoring_loop())
            self.monitoring_tasks.add(risk_task)
            
            # Start portfolio analytics task
            analytics_task = asyncio.create_task(self._analytics_update_loop())
            self.monitoring_tasks.add(analytics_task)
            
            # Load existing positions from MT5
            await self._synchronize_positions()
            
            logger.info("CHART Position Manager monitoring STARTED")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start position monitoring: {e}")
            await self.error_recovery.report_error(
                "position_manager",
                "monitoring_start_failed",
                ErrorSeverity.HIGH,
                f"Position monitoring start failed: {str(e)}"
            )
            return False
    
    async def stop_monitoring(self):
        """Stop position monitoring"""
        try:
            self.monitoring_active = False
            
            # Cancel all monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            logger.info("Position Manager monitoring stopped")
            
        except Exception as e:
            logger.error(f"Position monitoring stop error: {e}")
    
    async def add_position(self, 
                          order: TradingOrder, 
                          execution_result: ExecutionResult) -> Optional[str]:
        """Add new position from order execution"""
        try:
            if execution_result.result != TradeResult.SUCCESS:
                logger.warning(f"Cannot add position for failed execution: {order.order_id}")
                return None
            
            # Create position
            position = Position(
                position_id=str(uuid.uuid4()),
                order_id=order.order_id,
                mt5_ticket=execution_result.mt5_ticket or 0,
                symbol=order.symbol,
                side=order.side.value,
                volume=order.quantity,
                entry_price=execution_result.fill_price or 0.0,
                current_price=execution_result.fill_price or 0.0,
                stop_loss=order.stop_loss,
                take_profit=order.take_profit,
                commission=execution_result.commission,
                risk_amount=getattr(order, 'monetary_risk', 0.0),
                strategy_id=order.strategy_id,
                open_time=datetime.now(timezone.utc)
            )
            
            # Calculate initial risk metrics
            await self._calculate_position_metrics(position)
            
            # Add to tracking
            with self.update_lock:
                self.positions[position.position_id] = position
                self.position_history.append({
                    'action': 'position_opened',
                    'position_id': position.position_id,
                    'timestamp': position.open_time,
                    'symbol': position.symbol,
                    'volume': position.volume,
                    'price': position.entry_price
                })
            
            # Update performance metrics
            self.performance_metrics['total_trades'] += 1
            
            # Invoke callbacks
            for callback in self.position_callbacks:
                try:
                    callback(position)
                except Exception as e:
                    logger.error(f"Position callback error: {e}")
            
            # Check risk limits
            await self._check_risk_limits(position)
            
            logger.info(
                f"GRAPH_UP Position added: {position.symbol} {position.side} "
                f"{position.volume} @ {position.entry_price:.5f}"
            )
            
            return position.position_id
            
        except Exception as e:
            logger.error(f"Add position error: {e}")
            await self.error_recovery.report_error(
                "position_manager",
                "add_position_failed",
                ErrorSeverity.MEDIUM,
                f"Failed to add position: {str(e)}",
                context={'order_id': order.order_id}
            )
            return None
    
    async def close_position(self, position_id: str, reason: str = "manual") -> bool:
        """Close position"""
        try:
            if position_id not in self.positions:
                logger.warning(f"Position not found: {position_id}")
                return False
            
            position = self.positions[position_id]
            position.status = PositionStatus.CLOSING
            
            # Close position in MT5
            close_result = await self.mt5_connector.close_position(position.mt5_ticket)
            
            if close_result['success']:
                # Update position with close data
                position.status = PositionStatus.CLOSED
                position.close_time = datetime.now(timezone.utc)
                position.current_price = close_result['close_price']
                position.realized_pnl = close_result.get('profit', 0.0)
                position.commission += close_result.get('commission', 0.0)
                
                # Calculate final metrics
                await self._calculate_position_metrics(position)
                
                # Move to closed positions
                with self.update_lock:
                    self.closed_positions[position_id] = position
                    del self.positions[position_id]
                    
                    self.position_history.append({
                        'action': 'position_closed',
                        'position_id': position_id,
                        'timestamp': position.close_time,
                        'symbol': position.symbol,
                        'pnl': position.realized_pnl,
                        'reason': reason
                    })
                
                # Update performance metrics
                if position.realized_pnl > 0:
                    self.performance_metrics['winning_trades'] += 1
                    self.performance_metrics['total_profit'] += position.realized_pnl
                    self.performance_metrics['consecutive_wins'] += 1
                    self.performance_metrics['consecutive_losses'] = 0
                    
                    if position.realized_pnl > self.performance_metrics['largest_win']:
                        self.performance_metrics['largest_win'] = position.realized_pnl
                else:
                    self.performance_metrics['losing_trades'] += 1
                    self.performance_metrics['total_loss'] += abs(position.realized_pnl)
                    self.performance_metrics['consecutive_losses'] += 1
                    self.performance_metrics['consecutive_wins'] = 0
                    
                    if position.realized_pnl < self.performance_metrics['largest_loss']:
                        self.performance_metrics['largest_loss'] = position.realized_pnl
                
                # Update consecutive records
                self.performance_metrics['max_consecutive_wins'] = max(
                    self.performance_metrics['max_consecutive_wins'],
                    self.performance_metrics['consecutive_wins']
                )
                self.performance_metrics['max_consecutive_losses'] = max(
                    self.performance_metrics['max_consecutive_losses'],
                    self.performance_metrics['consecutive_losses']
                )
                
                logger.info(
                    f" Position closed: {position.symbol} "
                    f"P&L: {position.realized_pnl:.2f}EUR ({reason})"
                )
                
                return True
            else:
                position.status = PositionStatus.FAILED
                logger.error(f"Failed to close position: {close_result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"Close position error: {e}")
            await self.error_recovery.report_error(
                "position_manager",
                "close_position_failed",
                ErrorSeverity.MEDIUM,
                f"Failed to close position: {str(e)}",
                context={'position_id': position_id}
            )
            return False
    
    async def _position_update_loop(self):
        """Real-time position update loop"""
        logger.info("Position update loop started")
        
        while self.monitoring_active:
            try:
                start_time = time.perf_counter()
                
                # Update all open positions
                if self.positions:
                    await self._update_positions()
                    await self._update_portfolio_summary()
                
                # Calculate update time
                update_time = (time.perf_counter() - start_time) * 1000
                
                # Log slow updates
                if update_time > 500:  # >500ms
                    logger.warning(f"Slow position update: {update_time:.1f}ms")
                
                # Sleep for remaining interval
                sleep_time = max(0, self.update_interval - (update_time / 1000))
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Position update error: {e}")
                await asyncio.sleep(5)  # Extended delay on error
    
    async def _update_positions(self):
        """Update all position prices and P&L"""
        try:
            # Get current prices for all symbols
            symbols = list(set(pos.symbol for pos in self.positions.values()))
            
            for symbol in symbols:
                try:
                    price_info = await self.mt5_connector.get_current_price(symbol)
                    if not price_info:
                        continue
                    
                    # Update positions for this symbol
                    symbol_positions = [pos for pos in self.positions.values() 
                                      if pos.symbol == symbol and pos.status == PositionStatus.OPEN]
                    
                    for position in symbol_positions:
                        # Update current price
                        if position.side == "BUY":
                            position.current_price = price_info['bid']
                        else:
                            position.current_price = price_info['ask']
                        
                        # Update P&L and metrics
                        await self._calculate_position_metrics(position)
                        
                        # Update timestamp
                        position.last_update = datetime.now(timezone.utc)
                        position.price_updates += 1
                        
                        # Check for automatic closures (SL/TP)
                        await self._check_automatic_closures(position)
                        
                except Exception as e:
                    logger.error(f"Price update error for {symbol}: {e}")
            
        except Exception as e:
            logger.error(f"Position updates error: {e}")
    
    async def _calculate_position_metrics(self, position: Position):
        """Calculate position P&L and risk metrics"""
        try:
            # Calculate unrealized P&L
            if position.side == "BUY":
                price_diff = position.current_price - position.entry_price
            else:
                price_diff = position.entry_price - position.current_price
            
            # Calculate pip value
            if 'JPY' in position.symbol:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            # P&L calculation
            pips_profit = price_diff / pip_value
            position.unrealized_pnl = pips_profit * pip_value * position.volume * 100000
            
            # Update excursions
            if position.unrealized_pnl > position.max_favorable_excursion:
                position.max_favorable_excursion = position.unrealized_pnl
            
            if position.unrealized_pnl < 0:
                position.max_adverse_excursion = min(
                    position.max_adverse_excursion, 
                    position.unrealized_pnl
                )
            
            # Calculate duration
            if position.status == PositionStatus.OPEN:
                duration = datetime.now(timezone.utc) - position.open_time
                position.duration_minutes = duration.total_seconds() / 60
            
            # Risk level assessment
            risk_percentage = abs(position.unrealized_pnl) / position.risk_amount if position.risk_amount > 0 else 0
            
            if risk_percentage < 0.5:
                position.risk_level = RiskLevel.LOW
            elif risk_percentage < 0.8:
                position.risk_level = RiskLevel.MEDIUM
            elif risk_percentage < 1.2:
                position.risk_level = RiskLevel.HIGH
            else:
                position.risk_level = RiskLevel.CRITICAL
            
        except Exception as e:
            logger.error(f"Position metrics calculation error: {e}")
    
    async def _update_portfolio_summary(self):
        """Update portfolio summary metrics"""
        try:
            # Get account info from MT5
            account_info = await self.mt5_connector.get_account_info()
            if not account_info:
                return
            
            # Update basic metrics
            self.portfolio_summary.timestamp = datetime.now(timezone.utc)
            self.portfolio_summary.total_equity = account_info['equity']
            self.portfolio_summary.available_margin = account_info['margin_free']
            self.portfolio_summary.used_margin = account_info['margin']
            self.portfolio_summary.margin_level = account_info.get('margin_level', 0)
            
            # Calculate P&L metrics
            self.portfolio_summary.unrealized_pnl = sum(
                pos.unrealized_pnl for pos in self.positions.values()
            )
            
            # Position metrics
            self.portfolio_summary.open_positions = len(self.positions)
            self.portfolio_summary.total_volume = sum(
                pos.volume for pos in self.positions.values()
            )
            self.portfolio_summary.total_risk = sum(
                pos.risk_amount for pos in self.positions.values()
            )
            
            # Performance metrics
            total_trades = self.performance_metrics['total_trades']
            winning_trades = self.performance_metrics['winning_trades']
            
            if total_trades > 0:
                self.portfolio_summary.win_rate = winning_trades / total_trades
            
            total_profit = self.performance_metrics['total_profit']
            total_loss = self.performance_metrics['total_loss']
            
            if total_loss > 0:
                self.portfolio_summary.profit_factor = total_profit / total_loss
            
            # Risk metrics
            if self.portfolio_summary.total_equity > 0:
                self.portfolio_summary.risk_exposure = (
                    self.portfolio_summary.total_risk / self.portfolio_summary.total_equity
                )
            
            # Invoke portfolio callbacks
            for callback in self.portfolio_callbacks:
                try:
                    callback(self.portfolio_summary)
                except Exception as e:
                    logger.error(f"Portfolio callback error: {e}")
            
        except Exception as e:
            logger.error(f"Portfolio summary update error: {e}")
    
    async def _risk_monitoring_loop(self):
        """Risk monitoring and alert loop"""
        logger.info("Risk monitoring loop started")
        
        while self.monitoring_active:
            try:
                if self.risk_alerts_active:
                    await self._check_portfolio_risk()
                    await self._check_margin_levels()
                    await self._check_daily_loss_limits()
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Risk monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _check_risk_limits(self, position: Position):
        """Check individual position risk limits"""
        try:
            # Position risk check
            if position.risk_amount > self.risk_config['max_position_risk']:
                await self.error_recovery.report_error(
                    "position_manager",
                    "position_risk_exceeded",
                    ErrorSeverity.HIGH,
                    f"Position risk exceeded: {position.risk_amount}EUR",
                    context={'position_id': position.position_id, 'symbol': position.symbol}
                )
            
            # Portfolio position limit
            if len(self.positions) > self.risk_config['max_positions']:
                await self.error_recovery.report_error(
                    "position_manager",
                    "position_limit_exceeded",
                    ErrorSeverity.MEDIUM,
                    f"Position limit exceeded: {len(self.positions)} positions"
                )
            
        except Exception as e:
            logger.error(f"Risk limit check error: {e}")
    
    async def _check_automatic_closures(self, position: Position):
        """Check for automatic stop-loss/take-profit closures"""
        try:
            should_close = False
            close_reason = ""
            
            # Stop-loss check
            if position.stop_loss:
                if ((position.side == "BUY" and position.current_price <= position.stop_loss) or
                    (position.side == "SELL" and position.current_price >= position.stop_loss)):
                    should_close = True
                    close_reason = "stop_loss"
            
            # Take-profit check
            if position.take_profit and not should_close:
                if ((position.side == "BUY" and position.current_price >= position.take_profit) or
                    (position.side == "SELL" and position.current_price <= position.take_profit)):
                    should_close = True
                    close_reason = "take_profit"
            
            # Close position if needed
            if should_close:
                logger.info(f"Automatic closure triggered: {position.symbol} ({close_reason})")
                await self.close_position(position.position_id, close_reason)
            
        except Exception as e:
            logger.error(f"Automatic closure check error: {e}")
    
    async def _analytics_update_loop(self):
        """Portfolio analytics update loop"""
        logger.info("Analytics update loop started")
        
        while self.monitoring_active:
            try:
                # Update performance analytics
                await self._calculate_advanced_metrics()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Analytics update error: {e}")
                await asyncio.sleep(120)
    
    async def _calculate_advanced_metrics(self):
        """Calculate advanced portfolio metrics"""
        try:
            # Daily P&L calculation
            today = datetime.now(timezone.utc).date()
            daily_positions = [
                pos for pos in list(self.closed_positions.values()) + list(self.positions.values())
                if pos.open_time.date() == today
            ]
            
            self.portfolio_summary.daily_pnl = sum(
                pos.realized_pnl + pos.unrealized_pnl for pos in daily_positions
            )
            
            # Weekly P&L calculation  
            week_start = datetime.now(timezone.utc) - timedelta(days=7)
            weekly_positions = [
                pos for pos in list(self.closed_positions.values()) + list(self.positions.values())
                if pos.open_time >= week_start
            ]
            
            self.portfolio_summary.weekly_pnl = sum(
                pos.realized_pnl + pos.unrealized_pnl for pos in weekly_positions
            )
            
            # Calculate Sharpe ratio (simplified)
            if len(self.closed_positions) > 10:
                returns = [pos.realized_pnl for pos in self.closed_positions.values()]
                avg_return = sum(returns) / len(returns)
                
                if len(returns) > 1:
                    variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
                    std_dev = variance ** 0.5
                    
                    if std_dev > 0:
                        self.portfolio_summary.sharpe_ratio = avg_return / std_dev
            
        except Exception as e:
            logger.error(f"Advanced metrics calculation error: {e}")
    
    async def _synchronize_positions(self):
        """Synchronize positions with MT5"""
        try:
            # Get positions from MT5
            mt5_positions = await self.mt5_connector.get_positions()
            
            if not mt5_positions:
                logger.info("No existing positions found in MT5")
                return
            
            # Convert MT5 positions to our format
            for mt5_pos in mt5_positions:
                position = Position(
                    position_id=str(uuid.uuid4()),
                    order_id=f"mt5_{mt5_pos['ticket']}",
                    mt5_ticket=mt5_pos['ticket'],
                    symbol=mt5_pos['symbol'],
                    side=mt5_pos['type'],
                    volume=mt5_pos['volume'],
                    entry_price=mt5_pos['price_open'],
                    current_price=mt5_pos['price_current'],
                    stop_loss=mt5_pos.get('sl'),
                    take_profit=mt5_pos.get('tp'),
                    unrealized_pnl=mt5_pos['profit'],
                    swap=mt5_pos.get('swap', 0.0),
                    open_time=mt5_pos['time']
                )
                
                # Calculate metrics
                await self._calculate_position_metrics(position)
                
                # Add to tracking
                self.positions[position.position_id] = position
            
            logger.info(f"Synchronized {len(mt5_positions)} positions from MT5")
            
        except Exception as e:
            logger.error(f"Position synchronization error: {e}")
            await self.error_recovery.report_error(
                "position_manager",
                "synchronization_failed",
                ErrorSeverity.MEDIUM,
                f"Position synchronization failed: {str(e)}"
            )
    
    def register_position_callback(self, callback: Callable[[Position], None]):
        """Register callback for position updates"""
        self.position_callbacks.append(callback)
    
    def register_portfolio_callback(self, callback: Callable[[PortfolioSummary], None]):
        """Register callback for portfolio updates"""
        self.portfolio_callbacks.append(callback)
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """Get position by ID"""
        return self.positions.get(position_id) or self.closed_positions.get(position_id)
    
    def get_open_positions(self) -> List[Position]:
        """Get all open positions"""
        return list(self.positions.values())
    
    def get_positions_by_symbol(self, symbol: str) -> List[Position]:
        """Get positions for specific symbol"""
        return [pos for pos in self.positions.values() if pos.symbol == symbol]
    
    def get_portfolio_summary(self) -> PortfolioSummary:
        """Get current portfolio summary"""
        return self.portfolio_summary
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            **self.performance_metrics,
            'portfolio_summary': {
                'total_equity': self.portfolio_summary.total_equity,
                'daily_pnl': self.portfolio_summary.daily_pnl,
                'weekly_pnl': self.portfolio_summary.weekly_pnl,
                'unrealized_pnl': self.portfolio_summary.unrealized_pnl,
                'open_positions': self.portfolio_summary.open_positions,
                'win_rate': self.portfolio_summary.win_rate,
                'profit_factor': self.portfolio_summary.profit_factor,
                'risk_exposure': self.portfolio_summary.risk_exposure
            }
        }
    
    async def emergency_close_all(self, reason: str = "Emergency closure"):
        """Emergency close all positions"""
        logger.critical(f" Emergency closing all positions: {reason}")
        
        try:
            # Close all open positions
            position_ids = list(self.positions.keys())
            
            for position_id in position_ids:
                try:
                    await self.close_position(position_id, f"emergency_{reason}")
                except Exception as e:
                    logger.error(f"Emergency close failed for {position_id}: {e}")
            
            # Report to ProductOwner
            await self._notify_product_owner_emergency(reason, len(position_ids))
            
        except Exception as e:
            logger.error(f"Emergency close all error: {e}")
    
    async def _notify_product_owner_emergency(self, reason: str, position_count: int):
        """Notify ProductOwner of emergency actions"""
        try:
            notification = MCPMessage(
                id=f"emergency_close_{int(time.time())}",
                method="emergency_position_closure",
                params={
                    'reason': reason,
                    'positions_closed': position_count,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'portfolio_status': {
                        'total_equity': self.portfolio_summary.total_equity,
                        'unrealized_pnl': self.portfolio_summary.unrealized_pnl,
                        'daily_pnl': self.portfolio_summary.daily_pnl
                    }
                },
                type=MessageType.NOTIFICATION,
                recipient="product_owner"
            )
            
            await self.product_owner.handle_message(notification)
            
        except Exception as e:
            logger.error(f"ProductOwner emergency notification error: {e}")
    
    async def _check_portfolio_risk(self):
        """Check overall portfolio risk"""
        try:
            # Portfolio heat check
            total_risk = sum(pos.risk_amount for pos in self.positions.values())
            
            if total_risk > self.risk_config['max_portfolio_risk']:
                await self.error_recovery.report_error(
                    "position_manager",
                    "portfolio_risk_exceeded",
                    ErrorSeverity.HIGH,
                    f"Portfolio risk exceeded: {total_risk}EUR"
                )
        
        except Exception as e:
            logger.error(f"Portfolio risk check error: {e}")
    
    async def _check_margin_levels(self):
        """Check margin levels"""
        try:
            margin_level = self.portfolio_summary.margin_level
            
            if margin_level < self.risk_config['stop_out_level']:
                await self.error_recovery.report_error(
                    "position_manager",
                    "stop_out_level",
                    ErrorSeverity.CRITICAL,
                    f"Stop out level reached: {margin_level}%"
                )
                await self.emergency_close_all("stop_out_level")
            elif margin_level < self.risk_config['margin_call_level']:
                await self.error_recovery.report_error(
                    "position_manager",
                    "margin_call_level",
                    ErrorSeverity.HIGH,
                    f"Margin call level: {margin_level}%"
                )
        
        except Exception as e:
            logger.error(f"Margin level check error: {e}")
    
    async def _check_daily_loss_limits(self):
        """Check daily loss limits"""
        try:
            daily_pnl = self.portfolio_summary.daily_pnl
            
            if daily_pnl <= self.risk_config['max_daily_loss']:
                await self.error_recovery.report_error(
                    "position_manager",
                    "daily_loss_limit",
                    ErrorSeverity.CRITICAL,
                    f"Daily loss limit reached: {daily_pnl}EUR"
                )
                await self.emergency_close_all("daily_loss_limit")
        
        except Exception as e:
            logger.error(f"Daily loss limit check error: {e}")