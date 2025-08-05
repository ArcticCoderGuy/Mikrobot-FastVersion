"""
Hansei (反省) - Self-Reflection Module
Japanese concept of reflective self-improvement applied to trading system
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import statistics
import json
from .mcp_controller import MCPAgent, MCPMessage, AgentRole, MessageType

logger = logging.getLogger(__name__)


class ReflectionLevel(Enum):
    """Levels of reflection depth"""
    IMMEDIATE = "immediate"      # Real-time decision reflection
    TACTICAL = "tactical"        # Short-term pattern analysis
    STRATEGIC = "strategic"      # Long-term system improvement
    PHILOSOPHICAL = "philosophical"  # Core principle examination


@dataclass
class ReflectionEntry:
    """Single reflection entry"""
    timestamp: datetime
    level: ReflectionLevel
    context: str
    observation: str
    analysis: str
    insight: str
    action_plan: Optional[str] = None
    confidence: float = 0.0
    implemented: bool = False


class HanseiAgent(MCPAgent):
    """
    Hansei (Self-Reflection) Agent
    Continuously analyzes system performance and suggests improvements
    Following Japanese Kaizen philosophy
    """
    
    def __init__(self):
        super().__init__("hansei_agent", AgentRole.HANSEI_REFLECTOR)
        
        # Reflection storage
        self.reflections: List[ReflectionEntry] = []
        self.insights_database: Dict[str, List[str]] = {
            'successful_patterns': [],
            'failure_patterns': [],
            'improvement_opportunities': [],
            'system_weaknesses': [],
            'market_adaptations': []
        }
        
        # Reflection configuration
        self.reflection_config = {
            'immediate_threshold': 0.1,    # Reflect on decisions with low confidence
            'tactical_interval': 3600,     # Hourly tactical reflection
            'strategic_interval': 86400,   # Daily strategic reflection
            'philosophical_interval': 604800,  # Weekly philosophical reflection
            'min_data_points': 10,         # Minimum data for meaningful reflection
            'confidence_threshold': 0.7    # Threshold for action implementation
        }
        
        # Last reflection timestamps
        self.last_reflections = {
            ReflectionLevel.TACTICAL: datetime.utcnow(),
            ReflectionLevel.STRATEGIC: datetime.utcnow(),
            ReflectionLevel.PHILOSOPHICAL: datetime.utcnow()
        }
        
        # Performance tracking for reflection
        self.performance_history = []
    
    async def handle_message(self, message: MCPMessage) -> Optional[MCPMessage]:
        """Handle MCP messages for reflection triggers"""
        method = message.method
        params = message.params
        
        if method == "reflect_on_decision":
            return await self._reflect_on_decision(params)
        elif method == "reflect_on_trade":
            return await self._reflect_on_trade(params)
        elif method == "periodic_reflection":
            return await self._periodic_reflection(params.get('level', 'tactical'))
        elif method == "get_insights":
            return await self._get_insights(params)
        elif method == "implement_insight":
            return await self._implement_insight(params)
        elif method == "ping":
            return MCPMessage(
                id=f"pong_{message.id}",
                method="pong",
                params={'hansei_status': 'reflecting'},
                type=MessageType.RESPONSE
            )
        
        return None
    
    async def _reflect_on_decision(self, params: Dict[str, Any]) -> MCPMessage:
        """Immediate reflection on a decision"""
        decision_data = params.get('decision_data', {})
        confidence = params.get('confidence', 0.5)
        
        # Only reflect on low-confidence decisions
        if confidence > self.reflection_config['immediate_threshold']:
            return MCPMessage(
                id=f"reflection_{datetime.utcnow().timestamp()}",
                method="reflection_skipped",
                params={'reason': 'High confidence decision'},
                type=MessageType.RESPONSE
            )
        
        # Analyze the decision
        analysis = self._analyze_decision(decision_data, confidence)
        
        # Create reflection entry
        reflection = ReflectionEntry(
            timestamp=datetime.utcnow(),
            level=ReflectionLevel.IMMEDIATE,
            context=f"Decision: {decision_data.get('type', 'unknown')}",
            observation=f"Low confidence decision ({confidence:.2f})",
            analysis=analysis['analysis'],
            insight=analysis['insight'],
            action_plan=analysis.get('action_plan'),
            confidence=analysis.get('confidence', 0.5)
        )
        
        self.reflections.append(reflection)
        
        return MCPMessage(
            id=f"reflection_{datetime.utcnow().timestamp()}",
            method="immediate_reflection",
            params={
                'reflection': self._reflection_to_dict(reflection),
                'requires_action': reflection.confidence > self.reflection_config['confidence_threshold']
            },
            type=MessageType.RESPONSE
        )
    
    async def _reflect_on_trade(self, params: Dict[str, Any]) -> MCPMessage:
        """Reflect on completed trade"""
        trade_data = params.get('trade_data', {})
        
        # Add to performance history
        self.performance_history.append({
            'timestamp': datetime.utcnow(),
            'pnl': trade_data.get('pnl', 0),
            'win': trade_data.get('pnl', 0) > 0,
            'probability': trade_data.get('probability', 0.5),
            'actual_outcome': trade_data.get('result', 'unknown'),
            'trade_data': trade_data
        })
        
        # Analyze trade outcome vs prediction
        analysis = self._analyze_trade_outcome(trade_data)
        
        # Create reflection
        reflection = ReflectionEntry(
            timestamp=datetime.utcnow(),
            level=ReflectionLevel.IMMEDIATE,
            context=f"Trade: {trade_data.get('symbol')} {trade_data.get('direction')}",
            observation=analysis['observation'],
            analysis=analysis['analysis'],
            insight=analysis['insight'],
            confidence=analysis['confidence']
        )
        
        self.reflections.append(reflection)
        
        # Update insights database
        if reflection.confidence > 0.7:
            if trade_data.get('pnl', 0) > 0:
                self.insights_database['successful_patterns'].append(analysis['pattern'])
            else:
                self.insights_database['failure_patterns'].append(analysis['pattern'])
        
        return MCPMessage(
            id=f"trade_reflection_{datetime.utcnow().timestamp()}",
            method="trade_reflection",
            params={'reflection': self._reflection_to_dict(reflection)},
            type=MessageType.RESPONSE
        )
    
    async def _periodic_reflection(self, level: str) -> MCPMessage:
        """Perform periodic reflection at specified level"""
        reflection_level = ReflectionLevel(level)
        
        # Check if it's time for this reflection
        last_reflection = self.last_reflections.get(reflection_level)
        interval = self.reflection_config.get(f'{level}_interval', 3600)
        
        if (datetime.utcnow() - last_reflection).total_seconds() < interval:
            return MCPMessage(
                id=f"reflection_skip_{datetime.utcnow().timestamp()}",
                method="reflection_skipped",
                params={'reason': 'Too early for reflection'},
                type=MessageType.RESPONSE
            )
        
        # Perform reflection based on level
        if reflection_level == ReflectionLevel.TACTICAL:
            reflection = await self._tactical_reflection()
        elif reflection_level == ReflectionLevel.STRATEGIC:
            reflection = await self._strategic_reflection()
        elif reflection_level == ReflectionLevel.PHILOSOPHICAL:
            reflection = await self._philosophical_reflection()
        else:
            return MCPMessage(
                id=f"reflection_error_{datetime.utcnow().timestamp()}",
                method="reflection_error",
                params={'error': 'Unknown reflection level'},
                type=MessageType.ERROR
            )
        
        self.reflections.append(reflection)
        self.last_reflections[reflection_level] = datetime.utcnow()
        
        return MCPMessage(
            id=f"periodic_reflection_{datetime.utcnow().timestamp()}",
            method="periodic_reflection_complete",
            params={'reflection': self._reflection_to_dict(reflection)},
            type=MessageType.RESPONSE
        )
    
    async def _tactical_reflection(self) -> ReflectionEntry:
        """Hourly tactical reflection on recent performance"""
        recent_trades = [t for t in self.performance_history 
                        if (datetime.utcnow() - t['timestamp']).total_seconds() < 3600]
        
        if len(recent_trades) < 3:
            return ReflectionEntry(
                timestamp=datetime.utcnow(),
                level=ReflectionLevel.TACTICAL,
                context="Hourly performance review",
                observation="Insufficient trade data",
                analysis="Need more trades for meaningful tactical analysis",
                insight="Continue monitoring, maintain current strategy",
                confidence=0.3
            )
        
        # Analyze recent performance
        win_rate = sum(1 for t in recent_trades if t['win']) / len(recent_trades)
        avg_pnl = statistics.mean([t['pnl'] for t in recent_trades])
        accuracy = self._calculate_prediction_accuracy(recent_trades)
        
        # Generate insights
        observation = f"Last hour: {len(recent_trades)} trades, {win_rate:.1%} win rate, {avg_pnl:.2f} avg PnL"
        
        if win_rate < 0.5:
            analysis = "Below-average win rate suggests strategy adjustments needed"
            insight = "Review signal quality thresholds and risk parameters"
            confidence = 0.8
        elif accuracy < 0.6:
            analysis = "Prediction accuracy is low, ML model may need retraining"
            insight = "Trigger ML model recalibration with recent market data"
            confidence = 0.7
        else:
            analysis = "Performance within acceptable range"
            insight = "Continue current approach, monitor for changes"
            confidence = 0.5
        
        return ReflectionEntry(
            timestamp=datetime.utcnow(),
            level=ReflectionLevel.TACTICAL,
            context="Hourly performance review",
            observation=observation,
            analysis=analysis,
            insight=insight,
            confidence=confidence
        )
    
    async def _strategic_reflection(self) -> ReflectionEntry:
        """Daily strategic reflection on system performance"""
        daily_trades = [t for t in self.performance_history 
                       if (datetime.utcnow() - t['timestamp']).total_seconds() < 86400]
        
        if len(daily_trades) < self.reflection_config['min_data_points']:
            return ReflectionEntry(
                timestamp=datetime.utcnow(),
                level=ReflectionLevel.STRATEGIC,
                context="Daily strategy review",
                observation="Insufficient data for strategic analysis",
                analysis="Need more trading activity for strategic insights",
                insight="Consider adjusting signal sensitivity or market conditions",
                confidence=0.4
            )
        
        # Strategic analysis
        total_pnl = sum(t['pnl'] for t in daily_trades)
        daily_win_rate = sum(1 for t in daily_trades if t['win']) / len(daily_trades)
        
        # Risk-reward analysis
        winning_trades = [t for t in daily_trades if t['win']]
        losing_trades = [t for t in daily_trades if not t['win']]
        
        avg_win = statistics.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(statistics.mean([t['pnl'] for t in losing_trades])) if losing_trades else 0
        
        risk_reward = avg_win / avg_loss if avg_loss > 0 else float('inf')
        
        # Generate strategic insight
        observation = f"Daily summary: {len(daily_trades)} trades, {total_pnl:.2f} PnL, {daily_win_rate:.1%} win rate"
        
        if total_pnl < 0:
            analysis = "Negative daily performance indicates systematic issues"
            insight = "Review risk management parameters and signal quality filters"
            confidence = 0.9
        elif risk_reward < 1.5:
            analysis = "Risk-reward ratio below optimal threshold"
            insight = "Adjust take-profit levels or improve entry timing"
            confidence = 0.8
        else:
            analysis = "Strategic performance acceptable"
            insight = "Continue current strategy with minor optimizations"
            confidence = 0.6
        
        return ReflectionEntry(
            timestamp=datetime.utcnow(),
            level=ReflectionLevel.STRATEGIC,
            context="Daily strategy review",
            observation=observation,
            analysis=analysis,
            insight=insight,
            confidence=confidence,
            action_plan=f"Review parameters if confidence > {self.reflection_config['confidence_threshold']}"
        )
    
    async def _philosophical_reflection(self) -> ReflectionEntry:
        """Weekly philosophical reflection on core principles"""
        weekly_trades = [t for t in self.performance_history 
                        if (datetime.utcnow() - t['timestamp']).total_seconds() < 604800]
        
        # Deep philosophical analysis
        observation = "Weekly examination of fundamental trading principles"
        
        if len(weekly_trades) > 50:
            # Analyze consistency with FoxBox principles
            consistency_score = self._evaluate_principle_consistency(weekly_trades)
            
            if consistency_score < 0.7:
                analysis = "System behavior deviating from FoxBox deterministic principles"
                insight = "Realign system with core deterministic decision-making principles"
                confidence = 0.9
            else:
                analysis = "System maintaining philosophical alignment"
                insight = "Continue adherence to FoxBox principles, seek continuous improvement"
                confidence = 0.6
        else:
            analysis = "Insufficient data for deep philosophical reflection"
            insight = "Focus on gathering more performance data for meaningful analysis"
            confidence = 0.3
        
        return ReflectionEntry(
            timestamp=datetime.utcnow(),
            level=ReflectionLevel.PHILOSOPHICAL,
            context="Weekly principle alignment review",
            observation=observation,
            analysis=analysis,
            insight=insight,
            confidence=confidence
        )
    
    def _analyze_decision(self, decision_data: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        """Analyze a specific decision"""
        decision_type = decision_data.get('type', 'unknown')
        
        analysis = f"Decision confidence ({confidence:.2f}) below threshold, reviewing factors"
        
        if decision_type == 'trade_entry':
            insight = "Consider additional confirmation signals or tighter filters"
        elif decision_type == 'risk_assessment':
            insight = "Review risk calculation methodology and parameters"
        else:
            insight = "Examine decision logic and available data quality"
        
        return {
            'analysis': analysis,
            'insight': insight,
            'confidence': 0.7,
            'action_plan': 'Monitor subsequent similar decisions'
        }
    
    def _analyze_trade_outcome(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trade outcome vs prediction"""
        predicted_prob = trade_data.get('probability', 0.5)
        actual_result = trade_data.get('pnl', 0) > 0
        
        # Prediction accuracy assessment
        if (predicted_prob > 0.6 and actual_result) or (predicted_prob < 0.4 and not actual_result):
            observation = "Prediction aligned with outcome"
            analysis = "Model prediction accuracy confirmed"
            insight = "Current predictive model performing well"
            confidence = 0.8
            pattern = "accurate_prediction"
        else:
            observation = "Prediction misaligned with outcome"
            analysis = "Model prediction accuracy needs improvement"
            insight = "Review feature engineering and model parameters"
            confidence = 0.9
            pattern = "prediction_error"
        
        return {
            'observation': observation,
            'analysis': analysis,
            'insight': insight,
            'confidence': confidence,
            'pattern': pattern
        }
    
    def _calculate_prediction_accuracy(self, trades: List[Dict[str, Any]]) -> float:
        """Calculate prediction accuracy"""
        correct_predictions = 0
        
        for trade in trades:
            predicted_prob = trade.get('probability', 0.5)
            actual_win = trade.get('win', False)
            
            if (predicted_prob > 0.5 and actual_win) or (predicted_prob < 0.5 and not actual_win):
                correct_predictions += 1
        
        return correct_predictions / len(trades) if trades else 0.0
    
    def _evaluate_principle_consistency(self, trades: List[Dict[str, Any]]) -> float:
        """Evaluate consistency with FoxBox principles"""
        # Simplified consistency evaluation
        factors = []
        
        # Deterministic decision making (consistent parameters)
        # Risk management adherence
        # Signal quality maintenance
        
        # For now, return a placeholder score
        return 0.8
    
    def _reflection_to_dict(self, reflection: ReflectionEntry) -> Dict[str, Any]:
        """Convert reflection to dictionary"""
        return {
            'timestamp': reflection.timestamp.isoformat(),
            'level': reflection.level.value,
            'context': reflection.context,
            'observation': reflection.observation,
            'analysis': reflection.analysis,
            'insight': reflection.insight,
            'action_plan': reflection.action_plan,
            'confidence': reflection.confidence,
            'implemented': reflection.implemented
        }
    
    async def _get_insights(self, params: Dict[str, Any]) -> MCPMessage:
        """Get accumulated insights"""
        category = params.get('category', 'all')
        
        if category == 'all':
            insights = self.insights_database
        else:
            insights = {category: self.insights_database.get(category, [])}
        
        return MCPMessage(
            id=f"insights_{datetime.utcnow().timestamp()}",
            method="insights_data",
            params={'insights': insights, 'reflection_count': len(self.reflections)},
            type=MessageType.RESPONSE
        )
    
    async def _implement_insight(self, params: Dict[str, Any]) -> MCPMessage:
        """Mark insight as implemented"""
        insight_id = params.get('insight_id')
        
        # In a real implementation, this would track specific insights
        # and their implementation status
        
        return MCPMessage(
            id=f"implement_{datetime.utcnow().timestamp()}",
            method="insight_implemented",
            params={'insight_id': insight_id, 'implemented': True},
            type=MessageType.RESPONSE
        )