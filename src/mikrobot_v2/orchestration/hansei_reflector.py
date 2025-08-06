"""
Hansei Reflector - Advanced Self-Reflection System
==================================================

Enhanced Hansei (反省) reflection system for continuous improvement:
- Tactical reflection (real-time optimization)
- Strategic reflection (daily/weekly analysis)  
- Philosophical reflection (system evolution)

Based on Japanese philosophy of deep self-reflection and continuous improvement.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import statistics

logger = logging.getLogger(__name__)

class ReflectionType(Enum):
    TACTICAL = "TACTICAL"       # Real-time trade analysis
    STRATEGIC = "STRATEGIC"     # Daily/weekly performance
    PHILOSOPHICAL = "PHILOSOPHICAL"  # System evolution

class InsightLevel(Enum):
    SURFACE = "SURFACE"         # Observable patterns
    DEEP = "DEEP"              # Root cause analysis  
    TRANSCENDENT = "TRANSCENDENT"  # System-level wisdom

@dataclass
class TradingInsight:
    """Individual trading insight from reflection"""
    type: ReflectionType
    level: InsightLevel
    description: str
    data_points: List[float]
    confidence: float
    actionable: bool
    optimization_potential: float
    timestamp: datetime

@dataclass
class PerformanceMetrics:
    """Performance data for reflection analysis"""
    trades_executed: int
    success_rate: float
    average_profit: float
    max_drawdown: float
    sharpe_ratio: float
    pattern_accuracy: Dict[str, float]
    symbol_performance: Dict[str, float]
    time_based_performance: Dict[str, float]

class HanseiReflector:
    """
    Advanced Hansei reflection system for autonomous improvement
    
    Implements three levels of reflection:
    1. Tactical - Real-time trade optimization
    2. Strategic - Performance pattern analysis
    3. Philosophical - System evolution insights
    """
    
    def __init__(self, mcp_controller=None):
        self.mcp = mcp_controller
        self.reflection_history: List[TradingInsight] = []
        self.performance_data: List[PerformanceMetrics] = []
        
        # Reflection intervals
        self.tactical_interval = 300    # 5 minutes
        self.strategic_interval = 3600  # 1 hour  
        self.philosophical_interval = 86400  # 24 hours
        
        # Insight thresholds
        self.insight_confidence_threshold = 0.7
        self.optimization_threshold = 0.15  # 15% improvement potential
        
        # Learning memory
        self.pattern_memory: Dict[str, List[float]] = {}
        self.optimization_results: Dict[str, float] = {}
        
        self.reflection_running = False
        
        logger.info("🧠 Hansei Reflector initialized")
    
    async def start_reflection_cycles(self):
        """Start all reflection cycles"""
        self.reflection_running = True
        
        # Start concurrent reflection tasks
        tasks = [
            asyncio.create_task(self._tactical_reflection_loop()),
            asyncio.create_task(self._strategic_reflection_loop()),
            asyncio.create_task(self._philosophical_reflection_loop())
        ]
        
        logger.info("🔄 Hansei reflection cycles started")
        await asyncio.gather(*tasks)
    
    async def _tactical_reflection_loop(self):
        """Tactical reflection - Real-time optimization"""
        while self.reflection_running:
            try:
                await asyncio.sleep(self.tactical_interval)
                insights = await self._perform_tactical_reflection()
                
                if insights:
                    await self._apply_tactical_optimizations(insights)
                    
            except Exception as e:
                logger.error(f"Tactical reflection error: {e}")
                await asyncio.sleep(60)
    
    async def _strategic_reflection_loop(self):
        """Strategic reflection - Performance analysis"""
        while self.reflection_running:
            try:
                await asyncio.sleep(self.strategic_interval)
                insights = await self._perform_strategic_reflection()
                
                if insights:
                    await self._apply_strategic_optimizations(insights)
                    
            except Exception as e:
                logger.error(f"Strategic reflection error: {e}")
                await asyncio.sleep(300)
    
    async def _philosophical_reflection_loop(self):
        """Philosophical reflection - System evolution"""
        while self.reflection_running:
            try:
                await asyncio.sleep(self.philosophical_interval)
                insights = await self._perform_philosophical_reflection()
                
                if insights:
                    await self._apply_philosophical_optimizations(insights)
                    
            except Exception as e:
                logger.error(f"Philosophical reflection error: {e}")
                await asyncio.sleep(3600)
    
    async def _perform_tactical_reflection(self) -> List[TradingInsight]:
        """Perform tactical reflection on recent trades"""
        insights = []
        
        try:
            # Get recent performance data
            if not self.mcp:
                return insights
                
            stats = self.mcp.get_system_stats()
            
            # Analyze recent trade success patterns
            recent_success_rate = stats.get('success_rate', 0)
            if recent_success_rate < 60:  # Below 60% success rate
                
                insight = TradingInsight(
                    type=ReflectionType.TACTICAL,
                    level=InsightLevel.SURFACE,
                    description=f"Recent success rate declining: {recent_success_rate:.1f}%",
                    data_points=[recent_success_rate],
                    confidence=0.8,
                    actionable=True,
                    optimization_potential=0.2,
                    timestamp=datetime.now()
                )
                insights.append(insight)
                
                logger.info(f"💭 Tactical insight: Low success rate detected")
            
            # Analyze signal confidence patterns
            active_signals = stats.get('active_signals', 0)
            if active_signals > 5:  # Too many concurrent signals
                
                insight = TradingInsight(
                    type=ReflectionType.TACTICAL,
                    level=InsightLevel.DEEP,
                    description=f"Signal overload detected: {active_signals} active signals",
                    data_points=[active_signals],
                    confidence=0.85,
                    actionable=True,
                    optimization_potential=0.25,
                    timestamp=datetime.now()
                )
                insights.append(insight)
                
                logger.info(f"💭 Tactical insight: Signal overload")
            
            # Store insights
            for insight in insights:
                self.reflection_history.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Tactical reflection error: {e}")
            return []
    
    async def _perform_strategic_reflection(self) -> List[TradingInsight]:
        """Perform strategic reflection on trading patterns"""
        insights = []
        
        try:
            if not self.mcp:
                return insights
            
            stats = self.mcp.get_system_stats()
            daily_performance = stats.get('daily_performance', {})
            
            if not daily_performance:
                return insights
            
            # Analyze daily performance trends
            recent_days = list(daily_performance.keys())[-7:]  # Last 7 days
            profit_trend = [daily_performance[day]['profit'] for day in recent_days if day in daily_performance]
            
            if len(profit_trend) >= 3:
                # Calculate trend
                avg_profit = statistics.mean(profit_trend)
                profit_std = statistics.stdev(profit_trend) if len(profit_trend) > 1 else 0
                
                # Declining performance insight
                if avg_profit < 0 and profit_std > abs(avg_profit) * 0.5:
                    insight = TradingInsight(
                        type=ReflectionType.STRATEGIC,
                        level=InsightLevel.DEEP,
                        description=f"Inconsistent daily performance: avg {avg_profit:.2f}, std {profit_std:.2f}",
                        data_points=profit_trend,
                        confidence=0.75,
                        actionable=True,
                        optimization_potential=0.3,
                        timestamp=datetime.now()
                    )
                    insights.append(insight)
                    logger.info(f"💭 Strategic insight: Performance inconsistency")
                
                # Positive trend insight
                elif avg_profit > 0 and len([p for p in profit_trend[-3:] if p > 0]) >= 2:
                    insight = TradingInsight(
                        type=ReflectionType.STRATEGIC,
                        level=InsightLevel.SURFACE,
                        description=f"Positive performance trend: avg {avg_profit:.2f}",
                        data_points=profit_trend,
                        confidence=0.8,
                        actionable=False,
                        optimization_potential=0.1,
                        timestamp=datetime.now()
                    )
                    insights.append(insight)
                    logger.info(f"💭 Strategic insight: Positive trend")
            
            # Store insights
            for insight in insights:
                self.reflection_history.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Strategic reflection error: {e}")
            return []
    
    async def _perform_philosophical_reflection(self) -> List[TradingInsight]:
        """Perform philosophical reflection on system evolution"""
        insights = []
        
        try:
            # Analyze long-term system evolution
            total_insights = len(self.reflection_history)
            
            if total_insights < 10:
                return insights  # Need minimum data for philosophical reflection
            
            # Analyze insight patterns over time
            tactical_insights = [i for i in self.reflection_history if i.type == ReflectionType.TACTICAL]
            strategic_insights = [i for i in self.reflection_history if i.type == ReflectionType.STRATEGIC]
            
            # System learning capacity insight
            if len(tactical_insights) > 20:
                recent_tactical = tactical_insights[-10:]
                older_tactical = tactical_insights[-20:-10]
                
                recent_avg_confidence = statistics.mean([i.confidence for i in recent_tactical])
                older_avg_confidence = statistics.mean([i.confidence for i in older_tactical])
                
                learning_improvement = recent_avg_confidence - older_avg_confidence
                
                if learning_improvement > 0.05:  # 5% improvement in insight confidence
                    insight = TradingInsight(
                        type=ReflectionType.PHILOSOPHICAL,
                        level=InsightLevel.TRANSCENDENT,
                        description=f"System learning capacity improving: {learning_improvement:.3f} confidence gain",
                        data_points=[recent_avg_confidence, older_avg_confidence],
                        confidence=0.9,
                        actionable=False,
                        optimization_potential=0.0,
                        timestamp=datetime.now()
                    )
                    insights.append(insight)
                    logger.info(f"💭 Philosophical insight: Learning capacity improvement")
                
                elif learning_improvement < -0.05:  # Declining learning
                    insight = TradingInsight(
                        type=ReflectionType.PHILOSOPHICAL,
                        level=InsightLevel.TRANSCENDENT,
                        description=f"System learning plateau detected: {learning_improvement:.3f} confidence decline",
                        data_points=[recent_avg_confidence, older_avg_confidence],
                        confidence=0.85,
                        actionable=True,
                        optimization_potential=0.4,
                        timestamp=datetime.now()
                    )
                    insights.append(insight)
                    logger.info(f"💭 Philosophical insight: Learning plateau")
            
            # System consciousness evolution insight
            actionable_insights = [i for i in self.reflection_history if i.actionable]
            optimization_rate = len(actionable_insights) / max(total_insights, 1)
            
            if optimization_rate > 0.7:  # High optimization frequency
                insight = TradingInsight(
                    type=ReflectionType.PHILOSOPHICAL,
                    level=InsightLevel.TRANSCENDENT,
                    description=f"High system adaptability: {optimization_rate:.2f} actionable insight ratio",
                    data_points=[optimization_rate],
                    confidence=0.95,
                    actionable=False,
                    optimization_potential=0.05,
                    timestamp=datetime.now()
                )
                insights.append(insight)
                logger.info(f"💭 Philosophical insight: High adaptability")
            
            # Store insights
            for insight in insights:
                self.reflection_history.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Philosophical reflection error: {e}")
            return []
    
    async def _apply_tactical_optimizations(self, insights: List[TradingInsight]):
        """Apply tactical optimizations from insights"""
        for insight in insights:
            if not insight.actionable or insight.optimization_potential < self.optimization_threshold:
                continue
            
            try:
                if "success rate declining" in insight.description:
                    # Increase signal confidence threshold
                    optimization = {
                        'type': 'confidence_threshold',
                        'value': 0.8,  # Increase from default 0.75
                        'reason': 'Tactical: Low success rate'
                    }
                    await self._send_optimization_to_mcp(optimization)
                    
                elif "signal overload" in insight.description:
                    # Reduce concurrent signal limit
                    optimization = {
                        'type': 'signal_limit',
                        'value': 3,  # Reduce concurrent signals
                        'reason': 'Tactical: Signal overload'
                    }
                    await self._send_optimization_to_mcp(optimization)
                
                logger.info(f"⚡ Applied tactical optimization: {insight.description}")
                
            except Exception as e:
                logger.error(f"Tactical optimization error: {e}")
    
    async def _apply_strategic_optimizations(self, insights: List[TradingInsight]):
        """Apply strategic optimizations from insights"""
        for insight in insights:
            if not insight.actionable or insight.optimization_potential < self.optimization_threshold:
                continue
            
            try:
                if "inconsistent daily performance" in insight.description:
                    # Adjust risk management
                    optimization = {
                        'type': 'risk_adjustment',
                        'value': 0.005,  # Reduce risk from 0.01 to 0.005
                        'reason': 'Strategic: Performance inconsistency'
                    }
                    await self._send_optimization_to_mcp(optimization)
                
                logger.info(f"📊 Applied strategic optimization: {insight.description}")
                
            except Exception as e:
                logger.error(f"Strategic optimization error: {e}")
    
    async def _apply_philosophical_optimizations(self, insights: List[TradingInsight]):
        """Apply philosophical optimizations from insights"""
        for insight in insights:
            if not insight.actionable or insight.optimization_potential < 0.3:  # Higher threshold
                continue
            
            try:
                if "learning plateau" in insight.description:
                    # Trigger system evolution
                    optimization = {
                        'type': 'system_evolution',
                        'value': {
                            'increase_exploration': True,
                            'adjust_learning_rate': 1.2,
                            'enable_advanced_patterns': True
                        },
                        'reason': 'Philosophical: Learning plateau detected'
                    }
                    await self._send_optimization_to_mcp(optimization)
                
                logger.info(f"🧠 Applied philosophical optimization: {insight.description}")
                
            except Exception as e:
                logger.error(f"Philosophical optimization error: {e}")
    
    async def _send_optimization_to_mcp(self, optimization: Dict):
        """Send optimization to MCP controller"""
        if self.mcp:
            from .mcp_v2_controller import MCPMessage, MessageType
            
            message = MCPMessage(
                id=f"hansei_{int(datetime.now().timestamp())}",
                type=MessageType.REFLECTION,
                sender="hansei_reflector",
                recipient="mcp_controller",
                payload={
                    'insights': [],
                    'optimizations': [optimization]
                },
                timestamp=datetime.now(),
                priority=4
            )
            
            await self.mcp.send_message(message)
    
    def get_reflection_summary(self) -> Dict[str, Any]:
        """Get summary of reflection insights"""
        total_insights = len(self.reflection_history)
        
        if total_insights == 0:
            return {'total_insights': 0}
        
        tactical_count = len([i for i in self.reflection_history if i.type == ReflectionType.TACTICAL])
        strategic_count = len([i for i in self.reflection_history if i.type == ReflectionType.STRATEGIC])
        philosophical_count = len([i for i in self.reflection_history if i.type == ReflectionType.PHILOSOPHICAL])
        
        actionable_count = len([i for i in self.reflection_history if i.actionable])
        avg_confidence = statistics.mean([i.confidence for i in self.reflection_history])
        avg_optimization_potential = statistics.mean([i.optimization_potential for i in self.reflection_history])
        
        return {
            'total_insights': total_insights,
            'tactical_insights': tactical_count,
            'strategic_insights': strategic_count,
            'philosophical_insights': philosophical_count,
            'actionable_insights': actionable_count,
            'average_confidence': avg_confidence,
            'average_optimization_potential': avg_optimization_potential,
            'last_reflection': self.reflection_history[-1].timestamp.isoformat() if self.reflection_history else None
        }
    
    def stop_reflection(self):
        """Stop reflection cycles"""
        self.reflection_running = False
        logger.info("🛑 Hansei reflection stopped")