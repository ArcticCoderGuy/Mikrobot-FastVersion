"""
Dynamic Risk Manager
Implements dynamic position sizing and risk management based on validation confidence
Integrates M5 BOS + M1 retest validation confidence for position sizing optimization
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
import statistics
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MarketCondition(Enum):
    """Market condition classifications"""
    OPTIMAL = "optimal"
    FAVORABLE = "favorable"
    NEUTRAL = "neutral"
    UNFAVORABLE = "unfavorable"
    DANGEROUS = "dangerous"


@dataclass
class RiskParameters:
    """Dynamic risk parameters"""
    base_risk_percent: float = 0.01  # 1% base risk
    max_risk_percent: float = 0.02   # 2% maximum risk
    min_risk_percent: float = 0.002  # 0.2% minimum risk
    confidence_multiplier: float = 1.0
    market_condition_multiplier: float = 1.0
    validation_quality_multiplier: float = 1.0
    drawdown_protection_multiplier: float = 1.0
    session_multiplier: float = 1.0
    final_risk_percent: float = 0.01
    stop_loss_pips: float = 0.0
    take_profit_pips: float = 0.0
    risk_reward_ratio: float = 2.0
    position_size_lots: float = 0.01


@dataclass
class PositionSizingResult:
    """Position sizing calculation result"""
    symbol: str
    trace_id: str
    validation_confidence: float
    risk_parameters: RiskParameters
    position_size_lots: float
    stop_loss_price: float
    take_profit_price: float
    expected_loss_usd: float
    expected_profit_usd: float
    risk_reward_ratio: float
    confidence_grade: str
    risk_level: RiskLevel
    market_condition: MarketCondition
    adjustments_applied: List[str]
    calculation_details: Dict[str, Any]
    timestamp: datetime


class DynamicRiskManager:
    """
    Dynamic position sizing and risk management system
    
    Features:
    - Confidence-based position sizing
    - Multi-factor risk adjustment
    - Market condition analysis
    - Drawdown protection
    - Session-based adjustments
    - Performance tracking
    """
    
    def __init__(self, account_balance: float = 10000.0):
        self.account_balance = account_balance
        
        # Risk management configuration
        self.risk_config = {
            'max_daily_risk': 0.05,      # 5% max daily risk
            'max_account_risk': 0.20,    # 20% max account risk
            'max_concurrent_trades': 3,
            'drawdown_limit': 0.10,      # 10% drawdown limit
            'confidence_threshold': 0.75,
            'min_confidence_for_trade': 0.6
        }
        
        # Dynamic multipliers based on validation confidence
        self.confidence_multipliers = {
            0.95: 1.5,   # Exceptional confidence
            0.90: 1.3,   # Very high confidence
            0.85: 1.2,   # High confidence
            0.80: 1.1,   # Good confidence
            0.75: 1.0,   # Baseline confidence
            0.70: 0.8,   # Moderate confidence
            0.65: 0.6,   # Lower confidence
            0.60: 0.4,   # Minimum confidence
        }
        
        # Market condition multipliers
        self.market_condition_multipliers = {
            MarketCondition.OPTIMAL: 1.3,
            MarketCondition.FAVORABLE: 1.1,
            MarketCondition.NEUTRAL: 1.0,
            MarketCondition.UNFAVORABLE: 0.7,
            MarketCondition.DANGEROUS: 0.3
        }
        
        # Session-based multipliers
        self.session_multipliers = {
            'london': 1.2,
            'new_york': 1.2,
            'overlap': 1.3,
            'tokyo': 0.9,
            'sydney': 0.8,
            'weekend': 0.5
        }
        
        # Pattern-specific risk adjustments
        self.pattern_risk_adjustments = {
            'M5_BOS': {
                'base_multiplier': 1.1,
                'high_volume_boost': 0.2,
                'momentum_boost': 0.15
            },
            'M1_BREAK_RETEST': {
                'base_multiplier': 1.0,
                'retest_quality_boost': 0.25,
                'deviation_penalty': 0.3
            }
        }
        
        # Performance tracking
        self.risk_metrics = {
            'total_positions_sized': 0,
            'avg_risk_per_trade': 0.0,
            'avg_confidence_traded': 0.0,
            'high_confidence_trades': 0,
            'risk_adjusted_trades': 0,
            'drawdown_protected_trades': 0
        }
        
        # Position sizing history
        self.sizing_history: List[PositionSizingResult] = []
        
        # Current portfolio state
        self.portfolio_state = {
            'current_drawdown': 0.0,
            'daily_risk_used': 0.0,
            'active_trades': 0,
            'total_exposure': 0.0,
            'recent_performance': []
        }
    
    def calculate_position_size(self, 
                              symbol: str,
                              direction: str,
                              entry_price: float,
                              stop_loss_price: float,
                              take_profit_price: float,
                              validation_confidence: float,
                              validation_details: Dict[str, Any],
                              market_data: Dict[str, Any],
                              trace_id: str) -> PositionSizingResult:
        """
        Calculate dynamic position size based on validation confidence and risk factors
        
        Args:
            symbol: Trading symbol
            direction: BUY or SELL
            entry_price: Entry price level
            stop_loss_price: Stop loss price level
            take_profit_price: Take profit price level
            validation_confidence: Combined validation confidence (0.0-1.0)
            validation_details: Detailed validation results
            market_data: Current market conditions
            trace_id: Trace ID for tracking
        
        Returns:
            PositionSizingResult with complete position sizing details
        """
        
        try:
            # Initialize risk parameters
            risk_params = RiskParameters()
            adjustments_applied = []
            
            # 1. Base risk assessment
            if validation_confidence < self.risk_config['min_confidence_for_trade']:
                # Reject trade if confidence too low
                return self._create_rejected_result(
                    symbol, trace_id, validation_confidence, 
                    f"Confidence {validation_confidence:.2f} below minimum {self.risk_config['min_confidence_for_trade']}"
                )
            
            # 2. Confidence-based risk adjustment
            confidence_multiplier = self._calculate_confidence_multiplier(validation_confidence)
            risk_params.confidence_multiplier = confidence_multiplier
            adjustments_applied.append(f"Confidence multiplier: {confidence_multiplier:.2f}")
            
            # 3. Market condition assessment and adjustment
            market_condition = self._assess_market_conditions(market_data)
            market_multiplier = self.market_condition_multipliers[market_condition]
            risk_params.market_condition_multiplier = market_multiplier
            adjustments_applied.append(f"Market condition ({market_condition.value}): {market_multiplier:.2f}")
            
            # 4. Validation quality adjustment
            validation_quality_multiplier = self._calculate_validation_quality_multiplier(validation_details)
            risk_params.validation_quality_multiplier = validation_quality_multiplier
            adjustments_applied.append(f"Validation quality: {validation_quality_multiplier:.2f}")
            
            # 5. Drawdown protection adjustment
            drawdown_multiplier = self._calculate_drawdown_protection_multiplier()
            risk_params.drawdown_protection_multiplier = drawdown_multiplier
            if drawdown_multiplier < 1.0:\n                adjustments_applied.append(f\"Drawdown protection: {drawdown_multiplier:.2f}\")\n            \n            # 6. Session-based adjustment\n            session = market_data.get('current_session', 'neutral')\n            session_multiplier = self.session_multipliers.get(session, 1.0)\n            risk_params.session_multiplier = session_multiplier\n            adjustments_applied.append(f\"Session ({session}): {session_multiplier:.2f}\")\n            \n            # 7. Calculate final risk percentage\n            final_risk_percent = (\n                risk_params.base_risk_percent * \n                confidence_multiplier * \n                market_multiplier * \n                validation_quality_multiplier * \n                drawdown_multiplier * \n                session_multiplier\n            )\n            \n            # Apply risk limits\n            final_risk_percent = max(risk_params.min_risk_percent, \n                                   min(risk_params.max_risk_percent, final_risk_percent))\n            risk_params.final_risk_percent = final_risk_percent\n            \n            # 8. Calculate position sizing details\n            pip_value = self._get_pip_value(symbol)\n            stop_loss_pips = abs(entry_price - stop_loss_price) / pip_value\n            take_profit_pips = abs(take_profit_price - entry_price) / pip_value\n            \n            risk_params.stop_loss_pips = stop_loss_pips\n            risk_params.take_profit_pips = take_profit_pips\n            risk_params.risk_reward_ratio = take_profit_pips / max(stop_loss_pips, 0.1)\n            \n            # Calculate position size in lots\n            risk_amount_usd = self.account_balance * final_risk_percent\n            pip_value_usd = self._calculate_pip_value_usd(symbol)\n            position_size_lots = risk_amount_usd / (stop_loss_pips * pip_value_usd)\n            \n            # Apply position size limits\n            max_position_size = self._calculate_max_position_size(symbol)\n            position_size_lots = min(position_size_lots, max_position_size)\n            risk_params.position_size_lots = position_size_lots\n            \n            # 9. Calculate expected P&L\n            expected_loss_usd = stop_loss_pips * pip_value_usd * position_size_lots\n            expected_profit_usd = take_profit_pips * pip_value_usd * position_size_lots\n            \n            # 10. Risk level classification\n            risk_level = self._classify_risk_level(final_risk_percent, validation_confidence)\n            confidence_grade = self._get_confidence_grade(validation_confidence)\n            \n            # Create result\n            result = PositionSizingResult(\n                symbol=symbol,\n                trace_id=trace_id,\n                validation_confidence=validation_confidence,\n                risk_parameters=risk_params,\n                position_size_lots=round(position_size_lots, 2),\n                stop_loss_price=stop_loss_price,\n                take_profit_price=take_profit_price,\n                expected_loss_usd=round(expected_loss_usd, 2),\n                expected_profit_usd=round(expected_profit_usd, 2),\n                risk_reward_ratio=round(risk_params.risk_reward_ratio, 2),\n                confidence_grade=confidence_grade,\n                risk_level=risk_level,\n                market_condition=market_condition,\n                adjustments_applied=adjustments_applied,\n                calculation_details={\n                    'pip_value': pip_value,\n                    'pip_value_usd': pip_value_usd,\n                    'risk_amount_usd': risk_amount_usd,\n                    'account_balance': self.account_balance,\n                    'validation_details': validation_details\n                },\n                timestamp=datetime.utcnow()\n            )\n            \n            # Update metrics and history\n            self._update_risk_metrics(result)\n            self.sizing_history.append(result)\n            \n            # Keep history limited\n            if len(self.sizing_history) > 1000:\n                self.sizing_history = self.sizing_history[-1000:]\n            \n            logger.info(f\"Position sized for {symbol}: {position_size_lots} lots, \"\n                       f\"risk: {final_risk_percent:.2%}, confidence: {validation_confidence:.2f}\")\n            \n            return result\n            \n        except Exception as e:\n            logger.error(f\"Position sizing error for {trace_id}: {str(e)}\")\n            return self._create_error_result(symbol, trace_id, validation_confidence, str(e))\n    \n    def _calculate_confidence_multiplier(self, confidence: float) -> float:\n        \"\"\"Calculate risk multiplier based on validation confidence\"\"\"\n        # Find closest confidence threshold\n        confidence_thresholds = sorted(self.confidence_multipliers.keys(), reverse=True)\n        \n        for threshold in confidence_thresholds:\n            if confidence >= threshold:\n                return self.confidence_multipliers[threshold]\n        \n        # Below minimum confidence - very conservative\n        return 0.3\n    \n    def _assess_market_conditions(self, market_data: Dict[str, Any]) -> MarketCondition:\n        \"\"\"Assess current market conditions for risk adjustment\"\"\"\n        try:\n            volatility = market_data.get('volatility_level', 'medium')\n            news_risk = market_data.get('news_risk', 'normal')\n            trend_strength = market_data.get('trend_strength', 0.5)\n            session = market_data.get('current_session', 'neutral')\n            \n            # Calculate condition score\n            condition_score = 0.5  # Neutral baseline\n            \n            # Volatility adjustment\n            if volatility == 'low':\n                condition_score += 0.1\n            elif volatility == 'high':\n                condition_score -= 0.2\n            \n            # News risk adjustment\n            if news_risk == 'high':\n                condition_score -= 0.3\n            elif news_risk == 'medium':\n                condition_score -= 0.1\n            \n            # Trend strength adjustment\n            if trend_strength > 0.7:\n                condition_score += 0.2\n            elif trend_strength < 0.3:\n                condition_score -= 0.1\n            \n            # Session adjustment\n            if session in ['london', 'new_york', 'overlap']:\n                condition_score += 0.1\n            \n            # Classify condition\n            if condition_score >= 0.8:\n                return MarketCondition.OPTIMAL\n            elif condition_score >= 0.6:\n                return MarketCondition.FAVORABLE\n            elif condition_score >= 0.4:\n                return MarketCondition.NEUTRAL\n            elif condition_score >= 0.2:\n                return MarketCondition.UNFAVORABLE\n            else:\n                return MarketCondition.DANGEROUS\n                \n        except Exception as e:\n            logger.error(f\"Market condition assessment error: {str(e)}\")\n            return MarketCondition.NEUTRAL\n    \n    def _calculate_validation_quality_multiplier(self, validation_details: Dict[str, Any]) -> float:\n        \"\"\"Calculate multiplier based on validation quality details\"\"\"\n        try:\n            multiplier = 1.0\n            \n            # Strategic validation quality\n            strategic_result = validation_details.get('strategic_result', {})\n            strategic_confidence = strategic_result.get('confidence', 0.75)\n            \n            if strategic_confidence > 0.9:\n                multiplier += 0.1\n            elif strategic_confidence < 0.7:\n                multiplier -= 0.1\n            \n            # Technical validation quality\n            technical_result = validation_details.get('technical_result', {})\n            technical_confidence = technical_result.get('confidence', 0.75)\n            \n            if technical_confidence > 0.9:\n                multiplier += 0.1\n            elif technical_confidence < 0.7:\n                multiplier -= 0.1\n            \n            # Pattern-specific adjustments\n            validation_data = technical_result.get('validation_details', {})\n            \n            # M5 BOS specific adjustments\n            if 'structure_analysis' in validation_data:\n                structure = validation_data['structure_analysis']\n                if structure.get('structure_significance') == 'high':\n                    multiplier += 0.15\n                elif structure.get('structure_significance') == 'low':\n                    multiplier -= 0.1\n            \n            # M1 retest specific adjustments\n            if 'deviation_analysis' in validation_data:\n                deviation = validation_data['deviation_analysis']\n                deviation_pips = deviation.get('deviation_pips', 1.0)\n                if deviation_pips <= 0.3:  # Very tight retest\n                    multiplier += 0.2\n                elif deviation_pips > 0.7:  # Loose retest\n                    multiplier -= 0.15\n            \n            return max(0.5, min(1.5, multiplier))  # Clamp between 0.5 and 1.5\n            \n        except Exception as e:\n            logger.error(f\"Validation quality multiplier calculation error: {str(e)}\")\n            return 1.0\n    \n    def _calculate_drawdown_protection_multiplier(self) -> float:\n        \"\"\"Calculate multiplier based on current drawdown protection needs\"\"\"\n        current_drawdown = self.portfolio_state['current_drawdown']\n        \n        if current_drawdown <= 0.02:  # Less than 2% drawdown\n            return 1.0\n        elif current_drawdown <= 0.05:  # 2-5% drawdown\n            return 0.8\n        elif current_drawdown <= 0.08:  # 5-8% drawdown\n            return 0.6\n        else:  # Over 8% drawdown\n            return 0.4\n    \n    def _get_pip_value(self, symbol: str) -> float:\n        \"\"\"Get pip value for symbol\"\"\"\n        clean_symbol = symbol.upper().replace('.', '').replace('_', '')[:6]\n        \n        if 'JPY' in clean_symbol:\n            return 0.01\n        elif any(metal in clean_symbol for metal in ['XAU', 'XAG', 'GOLD', 'SILVER']):\n            return 0.01\n        elif any(crypto in clean_symbol for crypto in ['BTC', 'ETH']):\n            return 1.0 if 'BTC' in clean_symbol else 0.01\n        else:\n            return 0.0001  # Default forex\n    \n    def _calculate_pip_value_usd(self, symbol: str) -> float:\n        \"\"\"Calculate pip value in USD for standard lot\"\"\"\n        # Simplified calculation - in production would use real-time rates\n        clean_symbol = symbol.upper().replace('.', '').replace('_', '')[:6]\n        \n        if 'JPY' in clean_symbol:\n            return 10.0  # For JPY pairs, 1 pip = $10 for 1 standard lot\n        elif clean_symbol.startswith(('XAU', 'GOLD')):\n            return 10.0  # Gold: 1 pip = $10\n        elif clean_symbol.startswith(('XAG', 'SILVER')):\n            return 50.0  # Silver: 1 pip = $50\n        else:\n            return 10.0  # Standard forex: 1 pip = $10 for 1 standard lot\n    \n    def _calculate_max_position_size(self, symbol: str) -> float:\n        \"\"\"Calculate maximum allowed position size\"\"\"\n        # Base on account balance and symbol-specific limits\n        base_max = self.account_balance / 1000  # $1000 per 0.01 lot\n        \n        # Symbol-specific limits\n        if 'BTC' in symbol.upper():\n            return min(base_max, 0.1)  # Max 0.1 lot for BTC\n        elif any(metal in symbol.upper() for metal in ['XAU', 'XAG', 'GOLD', 'SILVER']):\n            return min(base_max, 1.0)  # Max 1.0 lot for metals\n        else:\n            return min(base_max, 2.0)  # Max 2.0 lots for forex\n    \n    def _classify_risk_level(self, risk_percent: float, confidence: float) -> RiskLevel:\n        \"\"\"Classify risk level based on risk percentage and confidence\"\"\"\n        if risk_percent <= 0.005 and confidence >= 0.8:\n            return RiskLevel.VERY_LOW\n        elif risk_percent <= 0.01 and confidence >= 0.75:\n            return RiskLevel.LOW\n        elif risk_percent <= 0.015 and confidence >= 0.7:\n            return RiskLevel.MEDIUM\n        elif risk_percent <= 0.02 and confidence >= 0.65:\n            return RiskLevel.HIGH\n        else:\n            return RiskLevel.VERY_HIGH\n    \n    def _get_confidence_grade(self, confidence: float) -> str:\n        \"\"\"Convert confidence to letter grade\"\"\"\n        if confidence >= 0.95:\n            return 'A+'\n        elif confidence >= 0.90:\n            return 'A'\n        elif confidence >= 0.85:\n            return 'B+'\n        elif confidence >= 0.80:\n            return 'B'\n        elif confidence >= 0.75:\n            return 'C+'\n        elif confidence >= 0.70:\n            return 'C'\n        elif confidence >= 0.65:\n            return 'D'\n        else:\n            return 'F'\n    \n    def _update_risk_metrics(self, result: PositionSizingResult):\n        \"\"\"Update risk management metrics\"\"\"\n        self.risk_metrics['total_positions_sized'] += 1\n        \n        # Update averages\n        total = self.risk_metrics['total_positions_sized']\n        current_avg_risk = self.risk_metrics['avg_risk_per_trade']\n        current_avg_confidence = self.risk_metrics['avg_confidence_traded']\n        \n        self.risk_metrics['avg_risk_per_trade'] = (\n            (current_avg_risk * (total - 1)) + result.risk_parameters.final_risk_percent\n        ) / total\n        \n        self.risk_metrics['avg_confidence_traded'] = (\n            (current_avg_confidence * (total - 1)) + result.validation_confidence\n        ) / total\n        \n        # Count high confidence trades\n        if result.validation_confidence >= 0.8:\n            self.risk_metrics['high_confidence_trades'] += 1\n        \n        # Count risk adjusted trades\n        if result.risk_parameters.confidence_multiplier != 1.0:\n            self.risk_metrics['risk_adjusted_trades'] += 1\n        \n        # Count drawdown protected trades\n        if result.risk_parameters.drawdown_protection_multiplier < 1.0:\n            self.risk_metrics['drawdown_protected_trades'] += 1\n    \n    def _create_rejected_result(self, symbol: str, trace_id: str, confidence: float, reason: str) -> PositionSizingResult:\n        \"\"\"Create result for rejected trade\"\"\"\n        return PositionSizingResult(\n            symbol=symbol,\n            trace_id=trace_id,\n            validation_confidence=confidence,\n            risk_parameters=RiskParameters(),\n            position_size_lots=0.0,\n            stop_loss_price=0.0,\n            take_profit_price=0.0,\n            expected_loss_usd=0.0,\n            expected_profit_usd=0.0,\n            risk_reward_ratio=0.0,\n            confidence_grade=self._get_confidence_grade(confidence),\n            risk_level=RiskLevel.VERY_HIGH,\n            market_condition=MarketCondition.DANGEROUS,\n            adjustments_applied=[f\"Trade rejected: {reason}\"],\n            calculation_details={'rejected': True, 'reason': reason},\n            timestamp=datetime.utcnow()\n        )\n    \n    def _create_error_result(self, symbol: str, trace_id: str, confidence: float, error: str) -> PositionSizingResult:\n        \"\"\"Create result for calculation error\"\"\"\n        return PositionSizingResult(\n            symbol=symbol,\n            trace_id=trace_id,\n            validation_confidence=confidence,\n            risk_parameters=RiskParameters(),\n            position_size_lots=0.0,\n            stop_loss_price=0.0,\n            take_profit_price=0.0,\n            expected_loss_usd=0.0,\n            expected_profit_usd=0.0,\n            risk_reward_ratio=0.0,\n            confidence_grade='F',\n            risk_level=RiskLevel.VERY_HIGH,\n            market_condition=MarketCondition.DANGEROUS,\n            adjustments_applied=[f\"Calculation error: {error}\"],\n            calculation_details={'error': True, 'error_message': error},\n            timestamp=datetime.utcnow()\n        )\n    \n    def update_portfolio_state(self, current_drawdown: float, daily_risk_used: float, \n                             active_trades: int, total_exposure: float):\n        \"\"\"Update current portfolio state for risk calculations\"\"\"\n        self.portfolio_state.update({\n            'current_drawdown': current_drawdown,\n            'daily_risk_used': daily_risk_used,\n            'active_trades': active_trades,\n            'total_exposure': total_exposure\n        })\n    \n    def get_risk_metrics(self) -> Dict[str, Any]:\n        \"\"\"Get comprehensive risk management metrics\"\"\"\n        total_sized = self.risk_metrics['total_positions_sized']\n        \n        return {\n            'risk_metrics': self.risk_metrics,\n            'risk_config': self.risk_config,\n            'portfolio_state': self.portfolio_state,\n            'performance_ratios': {\n                'high_confidence_rate': (self.risk_metrics['high_confidence_trades'] / max(total_sized, 1)),\n                'risk_adjustment_rate': (self.risk_metrics['risk_adjusted_trades'] / max(total_sized, 1)),\n                'drawdown_protection_rate': (self.risk_metrics['drawdown_protected_trades'] / max(total_sized, 1))\n            },\n            'recent_sizing_history': [asdict(result) for result in self.sizing_history[-10:]],\n            'account_balance': self.account_balance\n        }\n    \n    def get_risk_report(self) -> Dict[str, Any]:\n        \"\"\"Generate comprehensive risk management report\"\"\"\n        metrics = self.get_risk_metrics()\n        \n        # Risk management grade\n        avg_confidence = self.risk_metrics['avg_confidence_traded']\n        high_conf_rate = metrics['performance_ratios']['high_confidence_rate']\n        \n        if avg_confidence >= 0.8 and high_conf_rate >= 0.6:\n            risk_grade = 'A'\n        elif avg_confidence >= 0.75 and high_conf_rate >= 0.4:\n            risk_grade = 'B'\n        elif avg_confidence >= 0.7 and high_conf_rate >= 0.2:\n            risk_grade = 'C'\n        else:\n            risk_grade = 'D'\n        \n        # Risk recommendations\n        recommendations = []\n        \n        if avg_confidence < 0.75:\n            recommendations.append(f\"Average confidence {avg_confidence:.2f} below optimal 0.75+ threshold\")\n        \n        if self.portfolio_state['current_drawdown'] > 0.05:\n            recommendations.append(f\"Current drawdown {self.portfolio_state['current_drawdown']:.1%} requires conservative sizing\")\n        \n        if metrics['performance_ratios']['risk_adjustment_rate'] < 0.3:\n            recommendations.append(\"Low risk adjustment rate - consider more dynamic sizing\")\n        \n        return {\n            'risk_management_grade': risk_grade,\n            'avg_confidence_traded': round(avg_confidence, 3),\n            'avg_risk_per_trade': round(self.risk_metrics['avg_risk_per_trade'], 4),\n            'recommendations': recommendations,\n            'detailed_metrics': metrics,\n            'system_health': {\n                'within_risk_limits': self.portfolio_state['daily_risk_used'] < self.risk_config['max_daily_risk'],\n                'drawdown_acceptable': self.portfolio_state['current_drawdown'] < self.risk_config['drawdown_limit'],\n                'position_sizing_active': self.risk_metrics['total_positions_sized'] > 0\n            }\n        }"