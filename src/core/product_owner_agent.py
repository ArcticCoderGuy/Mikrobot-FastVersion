"""
ProductOwner Agent
Strategic orchestrator for the Mikrobot trading system
Implements business logic, trade strategy management, and performance optimization
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import asyncio
import logging
import json
from enum import Enum

from .mcp_controller import MCPAgent, MCPMessage, AgentRole, MessageType

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Trading strategy types"""
    M5_BOS = "m5_breakout_structure"
    M1_RETEST = "m1_break_retest"
    SCALPING = "scalping"
    SWING = "swing_trading"
    ADAPTIVE = "adaptive_multi_timeframe"


class MarketSession(Enum):
    """Market session types"""
    LONDON = "london"
    NEW_YORK = "new_york" 
    TOKYO = "tokyo"
    SYDNEY = "sydney"
    OVERLAP = "session_overlap"


@dataclass
class StrategyConfig:
    """Strategy configuration"""
    strategy_type: StrategyType
    max_risk_per_trade: float = 0.01  # 1% risk per trade
    max_daily_risk: float = 0.05      # 5% daily risk
    max_concurrent_trades: int = 3
    preferred_sessions: List[MarketSession] = None
    min_win_rate: float = 0.65        # 65% minimum win rate
    target_rr_ratio: float = 2.0      # 1:2 risk reward
    enabled: bool = True
    
    def __post_init__(self):
        if self.preferred_sessions is None:
            self.preferred_sessions = [MarketSession.LONDON, MarketSession.NEW_YORK]


@dataclass 
class PerformanceMetrics:
    """Performance tracking metrics"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    avg_rr_ratio: float = 0.0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


class ProductOwnerAgent(MCPAgent):
    """
    ProductOwner Agent - Central strategic orchestrator
    
    Responsibilities:
    - Trade strategy selection and optimization
    - Portfolio risk management
    - Performance monitoring and adaptation
    - Business rule enforcement
    - Strategic decision making
    """
    
    def __init__(self, agent_id: str = "product_owner"):
        super().__init__(agent_id, AgentRole.ORCHESTRATOR)
        
        # Strategy management
        self.strategies: Dict[str, StrategyConfig] = {}
        self.active_strategy: Optional[StrategyConfig] = None
        
        # Performance tracking
        self.performance: PerformanceMetrics = PerformanceMetrics()
        self.daily_performance: Dict[str, PerformanceMetrics] = {}
        
        # Risk management
        self.portfolio_state = {
            'total_exposure': 0.0,
            'active_trades': 0,
            'daily_pnl': 0.0,
            'daily_loss_limit': -0.05,  # 5% daily loss limit (FTMO)
            'max_drawdown_limit': -0.10,  # 10% max drawdown
            'risk_on': True
        }
        
        # Market conditions
        self.market_state = {
            'current_session': None,
            'volatility_level': 'medium',  # low, medium, high
            'trend_direction': 'neutral',  # bullish, bearish, neutral
            'news_risk': 'normal',         # high, medium, normal
            'last_updated': datetime.utcnow()
        }
        
        # Decision engine
        self.decision_history: List[Dict[str, Any]] = []
        self.auto_adapt_enabled = True
        
        # Initialize default strategies
        self._initialize_strategies()
        
        logger.info(f"ProductOwner Agent {self.agent_id} initialized")
    
    def _initialize_strategies(self):
        """Initialize default trading strategies"""
        # M5 BOS Strategy
        self.strategies['m5_bos'] = StrategyConfig(
            strategy_type=StrategyType.M5_BOS,
            max_risk_per_trade=0.01,
            max_daily_risk=0.05,
            max_concurrent_trades=2,
            preferred_sessions=[MarketSession.LONDON, MarketSession.NEW_YORK],
            min_win_rate=0.70,
            target_rr_ratio=2.5
        )
        
        # M1 Retest Strategy  
        self.strategies['m1_retest'] = StrategyConfig(
            strategy_type=StrategyType.M1_RETEST,
            max_risk_per_trade=0.005,  # Lower risk for scalping
            max_daily_risk=0.03,
            max_concurrent_trades=1,
            preferred_sessions=[MarketSession.LONDON],
            min_win_rate=0.75,
            target_rr_ratio=2.0
        )
        
        # Set default active strategy
        self.active_strategy = self.strategies['m5_bos']
        
        logger.info(f"Initialized {len(self.strategies)} trading strategies")
    
    async def handle_message(self, message: MCPMessage) -> Optional[MCPMessage]:
        """Handle incoming MCP messages"""
        self.metrics['messages_received'] += 1
        
        try:
            if message.method == "evaluate_signal":
                return await self._evaluate_trading_signal(message)
            elif message.method == "update_performance":
                return await self._update_performance_metrics(message)
            elif message.method == "get_strategy":
                return await self._get_current_strategy(message)
            elif message.method == "set_strategy":
                return await self._set_trading_strategy(message)
            elif message.method == "risk_check":
                return await self._perform_risk_check(message)
            elif message.method == "market_update":
                return await self._update_market_conditions(message)
            elif message.method == "optimize_strategy":
                return await self._optimize_strategy_performance(message)
            elif message.method == "get_portfolio_status":
                return await self._get_portfolio_status(message)
            elif message.method == "emergency_stop":
                return await self._emergency_stop_trading(message)
            elif message.method == "ping":
                return await self._handle_ping(message)
            else:
                logger.warning(f"Unknown method: {message.method}")
                return None
                
        except Exception as e:
            logger.error(f"Error handling message {message.method}: {str(e)}")
            self.metrics['errors'] += 1
            return None
    
    async def _evaluate_trading_signal(self, message: MCPMessage) -> MCPMessage:
        """Evaluate trading signal against current strategy and market conditions"""
        signal_data = message.params.get('signal_data', {})
        
        # Strategic evaluation
        evaluation = {
            'approved': False,
            'confidence': 0.0,
            'strategy_match': False,
            'risk_acceptable': False,
            'market_conditions_favorable': False,
            'reasons': [],
            'adjustments': {}
        }
        
        try:
            # 1. Strategy alignment check
            if self._check_strategy_alignment(signal_data):
                evaluation['strategy_match'] = True
                evaluation['reasons'].append("Signal aligns with active strategy")
            else:
                evaluation['reasons'].append("Signal does not match active strategy criteria")
            
            # 2. Risk assessment
            if self._assess_signal_risk(signal_data):
                evaluation['risk_acceptable'] = True
                evaluation['reasons'].append("Risk parameters acceptable")
            else:
                evaluation['reasons'].append("Risk parameters exceed limits")
            
            # 3. Market conditions check
            if self._evaluate_market_conditions(signal_data):
                evaluation['market_conditions_favorable'] = True
                evaluation['reasons'].append("Market conditions favorable")
            else:
                evaluation['reasons'].append("Market conditions unfavorable")
            
            # 4. Portfolio state check
            if not self._check_portfolio_limits():
                evaluation['reasons'].append("Portfolio limits exceeded")
            
            # 5. Calculate confidence and approval
            factors = [
                evaluation['strategy_match'],
                evaluation['risk_acceptable'], 
                evaluation['market_conditions_favorable'],
                self.portfolio_state['risk_on']
            ]
            
            evaluation['confidence'] = sum(factors) / len(factors)
            evaluation['approved'] = evaluation['confidence'] >= 0.75 and all(factors)
            
            # 6. Add strategy-specific adjustments
            if evaluation['approved']:
                evaluation['adjustments'] = self._get_strategy_adjustments(signal_data)
            
            # Log decision
            self._log_decision('signal_evaluation', evaluation, signal_data)
            
        except Exception as e:
            logger.error(f"Signal evaluation error: {str(e)}")
            evaluation['approved'] = False
            evaluation['reasons'].append(f"Evaluation error: {str(e)}")
        
        return MCPMessage(
            id=f"eval_result_{message.id}",
            method="signal_evaluation_result",
            params={
                'evaluation': evaluation,
                'strategy_config': asdict(self.active_strategy) if self.active_strategy else None
            },
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    def _check_strategy_alignment(self, signal_data: Dict[str, Any]) -> bool:
        """Check if signal aligns with active strategy"""
        if not self.active_strategy or not self.active_strategy.enabled:
            return False
        
        # Check pattern type
        pattern_type = signal_data.get('pattern_type', '').lower()
        strategy_type = self.active_strategy.strategy_type.value
        
        if 'm5_bos' in strategy_type and 'bos' not in pattern_type:
            return False
        
        if 'm1_retest' in strategy_type and 'retest' not in pattern_type:
            return False
        
        # Check market session preference
        current_time = datetime.utcnow()
        current_session = self._get_current_market_session(current_time)
        
        if current_session not in self.active_strategy.preferred_sessions:
            return False
        
        return True
    
    def _assess_signal_risk(self, signal_data: Dict[str, Any]) -> bool:
        """Assess if signal risk is acceptable"""
        # Check individual trade risk
        proposed_risk = signal_data.get('risk_percent', 0.02)  # Default 2%
        if proposed_risk > self.active_strategy.max_risk_per_trade:
            return False
        
        # Check daily risk accumulation
        if abs(self.portfolio_state['daily_pnl']) + proposed_risk > self.active_strategy.max_daily_risk:
            return False
        
        # Check concurrent trades limit
        if self.portfolio_state['active_trades'] >= self.active_strategy.max_concurrent_trades:
            return False
        
        return True
    
    def _evaluate_market_conditions(self, signal_data: Dict[str, Any]) -> bool:
        """Evaluate if market conditions are favorable"""
        # High news risk check
        if self.market_state['news_risk'] == 'high':
            return False
        
        # Volatility appropriateness
        signal_type = signal_data.get('pattern_type', '').lower()
        volatility = self.market_state['volatility_level']
        
        # BOS patterns prefer medium to high volatility
        if 'bos' in signal_type and volatility == 'low':
            return False
        
        # Retest patterns prefer low to medium volatility  
        if 'retest' in signal_type and volatility == 'high':
            return False
        
        return True
    
    def _update_validation_timing(self, validation_time_ms: float):
        """Update validation timing metrics"""
        current_avg = self.validation_metrics['avg_validation_time_ms']
        total_validations = (self.validation_metrics['bos_validations'] + 
                           self.validation_metrics['retest_validations'])
        
        if total_validations > 0:
            self.validation_metrics['avg_validation_time_ms'] = (
                (current_avg * (total_validations - 1)) + validation_time_ms
            ) / total_validations
    
    def _check_portfolio_limits(self) -> bool:
        """Check if portfolio is within risk limits"""
        # Check daily loss limit
        if self.portfolio_state['daily_pnl'] <= self.portfolio_state['daily_loss_limit']:
            return False
        
        # Check max drawdown
        if self.performance.max_drawdown <= self.portfolio_state['max_drawdown_limit']:
            return False
        
        # Check if risk is still on
        if not self.portfolio_state['risk_on']:
            return False
        
        return True
    
    def _get_strategy_adjustments(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get strategy-specific adjustments for the signal"""
        adjustments = {}
        
        if not self.active_strategy:
            return adjustments
        
        # Adjust position size based on performance
        if self.performance.win_rate < self.active_strategy.min_win_rate:
            adjustments['risk_reduction'] = 0.5  # Reduce risk by 50%
        elif self.performance.win_rate > 0.8:  # Very high win rate
            adjustments['risk_increase'] = 1.2   # Increase risk by 20%
        
        # Adjust target RR based on market conditions
        if self.market_state['volatility_level'] == 'high':
            adjustments['target_rr'] = self.active_strategy.target_rr_ratio * 1.3
        elif self.market_state['volatility_level'] == 'low':
            adjustments['target_rr'] = self.active_strategy.target_rr_ratio * 0.8
        else:
            adjustments['target_rr'] = self.active_strategy.target_rr_ratio
        
        # Session-based adjustments
        current_session = self._get_current_market_session(datetime.utcnow())
        if current_session == MarketSession.OVERLAP:
            adjustments['increased_confidence'] = True
        
        return adjustments
    
    async def _update_performance_metrics(self, message: MCPMessage) -> MCPMessage:
        """Update performance metrics from trade results"""
        trade_result = message.params.get('trade_result', {})
        
        try:
            # Update trade counts
            self.performance.total_trades += 1
            
            if trade_result.get('pnl', 0) > 0:
                self.performance.winning_trades += 1
            else:
                self.performance.losing_trades += 1
            
            # Update PnL
            pnl = trade_result.get('pnl', 0)
            self.performance.total_pnl += pnl
            self.portfolio_state['daily_pnl'] += pnl
            
            # Update win rate
            if self.performance.total_trades > 0:
                self.performance.win_rate = self.performance.winning_trades / self.performance.total_trades
            
            # Update RR ratio
            rr = trade_result.get('rr_ratio', 0)
            if rr > 0:
                current_avg = self.performance.avg_rr_ratio
                total = self.performance.total_trades
                self.performance.avg_rr_ratio = ((current_avg * (total - 1)) + rr) / total
            
            # Update drawdown
            if pnl < 0 and abs(pnl) > self.performance.max_drawdown:
                self.performance.max_drawdown = abs(pnl)
            
            # Update timestamps
            self.performance.last_updated = datetime.utcnow()
            
            # Check if strategy optimization is needed
            if self.auto_adapt_enabled and self.performance.total_trades % 10 == 0:
                await self._auto_optimize_strategy()
            
            # Risk management check
            if self.performance.win_rate < 0.5 and self.performance.total_trades >= 20:
                self.portfolio_state['risk_on'] = False
                logger.warning("Risk turned OFF due to poor performance")
            
            logger.info(f"Performance updated: WR={self.performance.win_rate:.1%}, PnL=${self.performance.total_pnl:.2f}")
            
        except Exception as e:
            logger.error(f"Performance update error: {str(e)}")
        
        return MCPMessage(
            id=f"perf_updated_{message.id}",
            method="performance_updated",
            params={
                'performance': asdict(self.performance),
                'portfolio_state': self.portfolio_state
            },
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _auto_optimize_strategy(self):
        """Automatically optimize strategy based on performance"""
        if not self.active_strategy:
            return
        
        # If win rate is low, reduce risk
        if self.performance.win_rate < self.active_strategy.min_win_rate:
            self.active_strategy.max_risk_per_trade *= 0.8
            logger.info(f"Reduced risk per trade to {self.active_strategy.max_risk_per_trade:.1%}")
        
        # If performance is very good, slightly increase risk
        elif self.performance.win_rate > 0.8 and self.performance.avg_rr_ratio > 2.0:
            self.active_strategy.max_risk_per_trade = min(
                self.active_strategy.max_risk_per_trade * 1.1,
                0.02  # Maximum 2% per trade
            )
            logger.info(f"Increased risk per trade to {self.active_strategy.max_risk_per_trade:.1%}")
    
    def _get_current_market_session(self, timestamp: datetime) -> MarketSession:
        """Determine current market session"""
        hour_utc = timestamp.hour
        
        # London: 08:00-16:00 UTC
        if 8 <= hour_utc < 16:
            # New York overlap: 13:00-16:00 UTC  
            if 13 <= hour_utc < 16:
                return MarketSession.OVERLAP
            return MarketSession.LONDON
        
        # New York: 13:00-21:00 UTC
        elif 13 <= hour_utc < 21:
            return MarketSession.NEW_YORK
        
        # Tokyo: 23:00-08:00 UTC
        elif hour_utc >= 23 or hour_utc < 8:
            return MarketSession.TOKYO
        
        # Sydney: 21:00-06:00 UTC
        else:
            return MarketSession.SYDNEY
    
    def _log_decision(self, decision_type: str, decision_data: Dict[str, Any], context: Dict[str, Any]):
        """Log strategic decision for analysis"""
        decision_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': decision_type,
            'decision': decision_data,
            'context': context,
            'strategy': self.active_strategy.strategy_type.value if self.active_strategy else None,
            'performance_at_time': asdict(self.performance)
        }
        
        self.decision_history.append(decision_record)
        
        # Keep only last 1000 decisions
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-1000:]
    
    async def _handle_ping(self, message: MCPMessage) -> MCPMessage:
        """Handle ping message"""
        return MCPMessage(
            id=f"pong_{message.id}",
            method="pong", 
            params={
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'active',
                'strategy': self.active_strategy.strategy_type.value if self.active_strategy else None,
                'performance': {
                    'win_rate': self.performance.win_rate,
                    'total_trades': self.performance.total_trades,
                    'daily_pnl': self.portfolio_state['daily_pnl']
                }
            },
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _emergency_stop_trading(self, message: MCPMessage) -> MCPMessage:
        """Emergency stop all trading activities"""
        reason = message.params.get('reason', 'Emergency stop requested')
        
        # Turn off risk
        self.portfolio_state['risk_on'] = False
        
        # Disable all strategies
        for strategy in self.strategies.values():
            strategy.enabled = False
        
        # Log emergency stop
        self._log_decision('emergency_stop', {'reason': reason}, {})
        
        logger.critical(f"EMERGENCY STOP: {reason}")
        
        # Broadcast emergency stop to all agents
        await self.send_message(
            method="broadcast",
            params={
                'method': 'emergency_stop',
                'params': {'reason': reason}
            }
        )
        
        return MCPMessage(
            id=f"emergency_stop_{message.id}",
            method="emergency_stop_confirmed",
            params={'reason': reason, 'timestamp': datetime.utcnow().isoformat()},
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        return {
            'agent_info': {
                'agent_id': self.agent_id,
                'role': self.role.value,
                'is_active': self.is_active
            },
            'performance': asdict(self.performance),
            'portfolio_state': self.portfolio_state,
            'market_state': self.market_state,
            'active_strategy': asdict(self.active_strategy) if self.active_strategy else None,
            'strategies': {k: asdict(v) for k, v in self.strategies.items()},
            'metrics': self.metrics,
            'recent_decisions': self.decision_history[-10:] if self.decision_history else [],
            'validation_metrics': self.validation_metrics
        }


class PriceActionValidator:
    """Advanced price action pattern validator for M5 BOS and M1 retest patterns"""
    
    def __init__(self):
        self.pip_calculators = {
            'EURUSD': 0.0001, 'GBPUSD': 0.0001, 'AUDUSD': 0.0001, 'NZDUSD': 0.0001,
            'USDCAD': 0.0001, 'USDCHF': 0.0001,
            'USDJPY': 0.01, 'EURJPY': 0.01, 'GBPJPY': 0.01,
            'XAUUSD': 0.01, 'XAGUSD': 0.001,  # Gold and Silver
            'BTCUSD': 1.0, 'ETHUSD': 0.01     # Crypto
        }
        
    def get_pip_value(self, symbol: str) -> float:
        """Get pip value for symbol"""
        # Extract base symbol without broker suffix
        clean_symbol = symbol.upper().replace('.', '').replace('_', '')[:6]
        
        for base_symbol, pip_value in self.pip_calculators.items():
            if clean_symbol.startswith(base_symbol[:6]):
                return pip_value
        
        # Default for unknown symbols (assume major forex)
        return 0.0001 if 'JPY' not in clean_symbol else 0.01
    
    def calculate_pips(self, symbol: str, price1: float, price2: float) -> float:
        """Calculate pip distance between two prices"""
        pip_value = self.get_pip_value(symbol)
        return abs(price1 - price2) / pip_value
    
    def validate_m5_bos(self, signal_data: Dict[str, Any], strategy_config: StrategyConfig) -> bool:
        """Validate M5 Break of Structure pattern with advanced criteria"""
        try:
            symbol = signal_data.get('symbol', '')
            direction = signal_data.get('direction', '').upper()
            price_levels = signal_data.get('price_levels', {})
            volume_data = signal_data.get('volume', {})
            momentum_data = signal_data.get('momentum', {})
            
            # Required price levels for BOS validation
            required_levels = ['previous_high', 'previous_low', 'current_price', 'structure_break_level']
            if not all(level in price_levels for level in required_levels):
                logger.warning(f"M5 BOS validation failed: Missing price levels for {symbol}")
                return False
            
            # 1. Structure break validation
            current_price = price_levels['current_price']
            structure_level = price_levels['structure_break_level']
            
            if direction == 'BUY':
                # Bullish BOS: price should break above previous high
                previous_high = price_levels['previous_high']
                if current_price <= previous_high:
                    return False
                
                # Check structure break distance
                break_pips = self.calculate_pips(symbol, current_price, structure_level)
                if break_pips < strategy_config.bos_min_structure_break_pips:
                    logger.debug(f"BOS break insufficient: {break_pips} pips < {strategy_config.bos_min_structure_break_pips}")
                    return False
                    
            elif direction == 'SELL':
                # Bearish BOS: price should break below previous low
                previous_low = price_levels['previous_low']
                if current_price >= previous_low:
                    return False
                
                # Check structure break distance
                break_pips = self.calculate_pips(symbol, structure_level, current_price)
                if break_pips < strategy_config.bos_min_structure_break_pips:
                    logger.debug(f"BOS break insufficient: {break_pips} pips < {strategy_config.bos_min_structure_break_pips}")
                    return False
            
            # 2. Volume confirmation
            if volume_data:
                current_volume = volume_data.get('current_volume', 0)
                avg_volume = volume_data.get('avg_volume_20', 0)
                
                if avg_volume > 0:
                    volume_ratio = current_volume / avg_volume
                    if volume_ratio < strategy_config.bos_volume_confirmation_multiplier:
                        logger.debug(f"BOS volume insufficient: {volume_ratio:.2f} < {strategy_config.bos_volume_confirmation_multiplier}")
                        return False
            
            # 3. Momentum confirmation
            if momentum_data:
                momentum_score = momentum_data.get('momentum_score', 0)
                if abs(momentum_score) < strategy_config.bos_momentum_threshold:
                    logger.debug(f"BOS momentum insufficient: {abs(momentum_score):.3f} < {strategy_config.bos_momentum_threshold}")
                    return False
            
            # 4. Market structure context validation
            market_structure = signal_data.get('market_structure', {})
            if market_structure:
                # Check if we're in a trending market (BOS works best in trends)
                trend_strength = market_structure.get('trend_strength', 0)
                if trend_strength < 0.3:  # Weak trend
                    logger.debug(f"BOS trend strength insufficient: {trend_strength:.2f}")
                    return False
            
            logger.info(f"M5 BOS validation passed for {symbol} {direction}")
            return True
            
        except Exception as e:
            logger.error(f"M5 BOS validation error: {str(e)}")
            return False
    
    def validate_m1_retest(self, signal_data: Dict[str, Any], strategy_config: StrategyConfig) -> bool:
        """Validate M1 break-and-retest pattern with 0.8 pip dynamic validation"""
        try:
            symbol = signal_data.get('symbol', '')
            direction = signal_data.get('direction', '').upper()
            price_levels = signal_data.get('price_levels', {})
            volume_data = signal_data.get('volume', {})
            retest_quality = signal_data.get('retest_quality', {})
            
            # Required levels for retest validation
            required_levels = ['break_level', 'retest_level', 'current_price']
            if not all(level in price_levels for level in required_levels):
                logger.warning(f"M1 retest validation failed: Missing price levels for {symbol}")
                return False
            
            break_level = price_levels['break_level']
            retest_level = price_levels['retest_level']
            current_price = price_levels['current_price']
            
            # 1. Dynamic 0.8 pip deviation validation
            retest_deviation_pips = self.calculate_pips(symbol, break_level, retest_level)
            
            if retest_deviation_pips > strategy_config.retest_max_deviation_pips:
                logger.debug(f"Retest deviation too high: {retest_deviation_pips:.2f} pips > {strategy_config.retest_max_deviation_pips}")
                return False
            
            # 2. Retest quality scoring
            quality_factors = []
            
            # Factor 1: Proximity to break level (closer = better)
            proximity_score = max(0, 1 - (retest_deviation_pips / strategy_config.retest_max_deviation_pips))
            quality_factors.append(proximity_score * 0.4)  # 40% weight
            
            # Factor 2: Volume decline during retest (indicates weak selling/buying pressure)
            if volume_data:
                break_volume = volume_data.get('break_volume', 0)
                retest_volume = volume_data.get('retest_volume', 0)
                
                if break_volume > 0:
                    volume_decline_ratio = retest_volume / break_volume
                    if volume_decline_ratio <= strategy_config.retest_volume_decline_ratio:
                        quality_factors.append(0.3)  # 30% weight for proper volume decline
                    else:
                        quality_factors.append(0.1)  # Low score for high retest volume
                else:
                    quality_factors.append(0.2)  # Neutral if no break volume data
            else:
                quality_factors.append(0.2)  # Neutral if no volume data
            
            # Factor 3: Price action pattern at retest
            if retest_quality:
                pattern_score = retest_quality.get('pattern_score', 0.5)
                quality_factors.append(pattern_score * 0.2)  # 20% weight
            else:
                quality_factors.append(0.1)  # Low score if no pattern analysis
            
            # Factor 4: Time factor (quicker retest generally better)
            time_factor = retest_quality.get('time_factor', 0.5)
            quality_factors.append(time_factor * 0.1)  # 10% weight
            
            # Calculate overall retest quality score
            overall_quality = sum(quality_factors)
            
            if overall_quality < strategy_config.retest_quality_min_score:
                logger.debug(f"Retest quality insufficient: {overall_quality:.2f} < {strategy_config.retest_quality_min_score}")
                return False
            
            # 3. Direction-specific validation
            if direction == 'BUY':
                # For bullish retest, current price should be above break level
                if current_price <= break_level:
                    logger.debug(f"Bullish retest failed: current price {current_price} <= break level {break_level}")
                    return False
            elif direction == 'SELL':
                # For bearish retest, current price should be below break level
                if current_price >= break_level:
                    logger.debug(f"Bearish retest failed: current price {current_price} >= break level {break_level}")
                    return False
            
            # 4. Multi-timeframe confirmation (if available)
            mtf_confirmation = signal_data.get('mtf_confirmation', {})
            if mtf_confirmation:
                higher_tf_trend = mtf_confirmation.get('higher_tf_trend', 'neutral')
                if direction == 'BUY' and higher_tf_trend == 'bearish':
                    logger.debug("Bullish retest conflicts with bearish higher timeframe trend")
                    return False
                elif direction == 'SELL' and higher_tf_trend == 'bullish':
                    logger.debug("Bearish retest conflicts with bullish higher timeframe trend")
                    return False
            
            logger.info(f"M1 retest validation passed for {symbol} {direction} (quality: {overall_quality:.2f}, deviation: {retest_deviation_pips:.2f} pips)")
            return True
            
        except Exception as e:
            logger.error(f"M1 retest validation error: {str(e)}")
            return False