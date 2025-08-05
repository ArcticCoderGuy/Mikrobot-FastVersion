"""
MQL5 Signal Processor
Enhanced processing for MikroBot_BOS_M5M1.mq5 signals with ML/MCP analysis
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import numpy as np
from dataclasses import dataclass
from ..core.mcp_controller import MCPAgent, MCPMessage, AgentRole, MessageType

logger = logging.getLogger(__name__)


@dataclass
class MQL5SignalData:
    """MQL5 signal data structure matching MikroBot EA output"""
    ea_name: str
    ea_version: str
    signal_type: str
    symbol: str
    direction: str
    trigger_price: float
    m5_bos_level: float
    m5_bos_direction: str
    m1_break_high: float
    m1_break_low: float
    pip_trigger: float
    timestamp: str
    primary_timeframe: str
    confirmation_timeframe: str
    signal_frequency: str
    account: int
    
    # Enhanced fields (added by our system)
    raw_quality_score: Optional[float] = None
    ml_enhancement_data: Optional[Dict[str, Any]] = None
    market_context: Optional[Dict[str, Any]] = None


class MQL5SignalProcessor(MCPAgent):
    """
    Processes MQL5 signals from MikroBot_BOS_M5M1.mq5 and enhances them with ML/MCP analysis
    """
    
    def __init__(self):
        super().__init__("mql5_signal_processor", AgentRole.SIGNAL_VALIDATOR)
        
        # Signal processing metrics
        self.processing_metrics = {
            'total_mql5_signals': 0,
            'enhanced_signals': 0,
            'quality_improvements': 0,
            'ml_enhancements': 0,
            'avg_processing_time_ms': 0.0
        }
        
        # Quality enhancement algorithms
        self.quality_enhancer = MQL5QualityEnhancer()
        self.ml_enhancer = MQL5MLEnhancer()
        self.context_analyzer = MQL5ContextAnalyzer()
    
    async def handle_message(self, message: MCPMessage) -> Optional[MCPMessage]:
        """Handle MCP messages for MQL5 signal processing"""
        method = message.method
        params = message.params
        
        if method == "process_mql5_signal":
            return await self._process_mql5_signal(params)
        elif method == "enhance_signal_quality":
            return await self._enhance_signal_quality(params)
        elif method == "get_processing_metrics":
            return await self._get_processing_metrics()
        elif method == "ping":
            return MCPMessage(
                id=f"pong_{message.id}",
                method="pong",
                params={'mql5_processor_status': 'active'},
                type=MessageType.RESPONSE
            )
        
        return None
    
    async def _process_mql5_signal(self, params: Dict[str, Any]) -> MCPMessage:
        """Process incoming MQL5 signal with ML/MCP enhancements"""
        try:
            start_time = datetime.utcnow()
            
            # Parse MQL5 signal data
            mql5_signal = self._parse_mql5_signal(params.get('signal_data', {}))
            
            if not mql5_signal:
                return MCPMessage(
                    id=f"mql5_error_{datetime.utcnow().timestamp()}",
                    method="mql5_processing_error",
                    params={'error': 'Invalid MQL5 signal data'},
                    type=MessageType.ERROR
                )
            
            # Phase 1: Quality Analysis Enhancement
            quality_analysis = await self.quality_enhancer.analyze_signal_quality(mql5_signal)
            mql5_signal.raw_quality_score = quality_analysis['overall_score']
            
            # Phase 2: ML-based Signal Enhancement
            ml_enhancement = await self.ml_enhancer.enhance_signal(mql5_signal, quality_analysis)
            mql5_signal.ml_enhancement_data = ml_enhancement
            
            # Phase 3: Market Context Analysis
            market_context = await self.context_analyzer.analyze_market_context(mql5_signal)
            mql5_signal.market_context = market_context
            
            # Phase 4: Create Enhanced Signal
            enhanced_signal = self._create_enhanced_signal(mql5_signal, quality_analysis, ml_enhancement, market_context)
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_processing_metrics(processing_time)
            
            return MCPMessage(
                id=f"mql5_enhanced_{datetime.utcnow().timestamp()}",
                method="mql5_signal_enhanced",
                params={
                    'original_signal': self._signal_to_dict(mql5_signal),
                    'enhanced_signal': enhanced_signal,
                    'quality_analysis': quality_analysis,
                    'ml_enhancement': ml_enhancement,
                    'market_context': market_context,
                    'processing_time_ms': round(processing_time, 2)
                },
                type=MessageType.RESPONSE
            )
            
        except Exception as e:
            logger.error(f"MQL5 signal processing error: {str(e)}")
            return MCPMessage(
                id=f"mql5_error_{datetime.utcnow().timestamp()}",
                method="mql5_processing_error",
                params={'error': str(e)},
                type=MessageType.ERROR
            )
    
    def _parse_mql5_signal(self, signal_data: Dict[str, Any]) -> Optional[MQL5SignalData]:
        """Parse MQL5 signal data into structured format"""
        try:
            # Validate required fields
            required_fields = [
                'ea_name', 'symbol', 'direction', 'trigger_price', 
                'm5_bos_level', 'm1_break_high', 'm1_break_low'
            ]
            
            for field in required_fields:
                if field not in signal_data:
                    logger.error(f"Missing required field: {field}")
                    return None
            
            # Create MQL5SignalData object
            return MQL5SignalData(
                ea_name=signal_data.get('ea_name', 'MikroBot_BOS_M5M1'),
                ea_version=signal_data.get('ea_version', '2.00'),
                signal_type=signal_data.get('signal_type', 'M5_M1_BOS_RETEST'),
                symbol=signal_data['symbol'],
                direction=signal_data['direction'],
                trigger_price=float(signal_data['trigger_price']),
                m5_bos_level=float(signal_data['m5_bos_level']),
                m5_bos_direction=signal_data.get('m5_bos_direction', signal_data['direction']),
                m1_break_high=float(signal_data['m1_break_high']),
                m1_break_low=float(signal_data['m1_break_low']),
                pip_trigger=float(signal_data.get('pip_trigger', 0.2)),
                timestamp=signal_data.get('timestamp', datetime.utcnow().isoformat()),
                primary_timeframe=signal_data.get('primary_timeframe', 'M5'),
                confirmation_timeframe=signal_data.get('confirmation_timeframe', 'M1'),
                signal_frequency=signal_data.get('signal_frequency', 'HIGH'),
                account=int(signal_data.get('account', 0))
            )
            
        except Exception as e:
            logger.error(f"MQL5 signal parsing error: {str(e)}")
            return None
    
    def _create_enhanced_signal(self, mql5_signal: MQL5SignalData, 
                               quality_analysis: Dict[str, Any],
                               ml_enhancement: Dict[str, Any],
                               market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create enhanced signal for U-Cell pipeline"""
        # Calculate enhanced confidence
        base_confidence = quality_analysis['overall_score']
        ml_confidence = ml_enhancement.get('confidence_boost', 0.0)
        context_adjustment = market_context.get('context_score', 0.0)
        
        enhanced_confidence = min(0.99, base_confidence + ml_confidence + context_adjustment)
        
        # Create enhanced price levels
        enhanced_price_levels = {
            'entry': mql5_signal.trigger_price,
            'stop_loss': self._calculate_enhanced_sl(mql5_signal, ml_enhancement),
            'take_profit': self._calculate_enhanced_tp(mql5_signal, ml_enhancement),
            'current_price': mql5_signal.trigger_price,
            'previous_high': mql5_signal.m1_break_high,
            'previous_low': mql5_signal.m1_break_low,
            'break_level': mql5_signal.m5_bos_level,
            'retest_level': mql5_signal.trigger_price
        }
        
        # Enhanced signal structure for U-Cell pipeline
        return {
            'symbol': mql5_signal.symbol,
            'timeframe': 'M1',  # Final confirmation timeframe
            'pattern_type': 'M1_BREAK_RETEST',
            'direction': mql5_signal.direction,
            'price_levels': enhanced_price_levels,
            'volume': self._estimate_volume_data(mql5_signal, market_context),
            'timestamp': mql5_signal.timestamp,
            'metadata': {
                'source': 'mql5_mikrobot',
                'ea_version': mql5_signal.ea_version,
                'original_quality': quality_analysis['overall_score'],
                'enhanced_confidence': enhanced_confidence,
                'ml_improvements': ml_enhancement.get('improvements', []),
                'market_conditions': market_context.get('conditions', {}),
                'pip_trigger': mql5_signal.pip_trigger,
                'signal_frequency': mql5_signal.signal_frequency
            },
            # Enhanced fields for U-Cell processing
            'momentum': ml_enhancement.get('momentum_data', {}),
            'retest_quality': {
                'pattern_score': quality_analysis.get('pattern_strength', 0.5),
                'time_factor': quality_analysis.get('timing_score', 0.5)
            },
            'market_session': market_context.get('session', 'unknown'),
            'volatility_level': market_context.get('volatility', 'medium'),
            'news_risk': market_context.get('news_risk', 'normal')
        }
    
    def _calculate_enhanced_sl(self, signal: MQL5SignalData, ml_data: Dict[str, Any]) -> float:
        """Calculate enhanced stop loss based on ML analysis"""
        base_sl_distance = abs(signal.m1_break_high - signal.m1_break_low) * 1.2
        
        # ML adjustments
        volatility_multiplier = ml_data.get('volatility_adjustment', 1.0)
        risk_multiplier = ml_data.get('risk_adjustment', 1.0)
        
        adjusted_distance = base_sl_distance * volatility_multiplier * risk_multiplier
        
        if signal.direction == 'BUY':
            return signal.trigger_price - adjusted_distance
        else:
            return signal.trigger_price + adjusted_distance
    
    def _calculate_enhanced_tp(self, signal: MQL5SignalData, ml_data: Dict[str, Any]) -> float:
        """Calculate enhanced take profit based on ML analysis"""
        base_tp_distance = abs(signal.m1_break_high - signal.m1_break_low) * 2.5
        
        # ML adjustments
        trend_strength = ml_data.get('trend_strength', 1.0)
        momentum_multiplier = ml_data.get('momentum_adjustment', 1.0)
        
        adjusted_distance = base_tp_distance * trend_strength * momentum_multiplier
        
        if signal.direction == 'BUY':
            return signal.trigger_price + adjusted_distance
        else:
            return signal.trigger_price - adjusted_distance
    
    def _estimate_volume_data(self, signal: MQL5SignalData, context: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate volume data for signal processing"""
        return {
            'current_volume': context.get('estimated_volume', 1000),
            'avg_volume_20': context.get('avg_volume', 800),
            'break_volume': context.get('break_volume', 1200),
            'retest_volume': context.get('retest_volume', 600)
        }
    
    def _signal_to_dict(self, signal: MQL5SignalData) -> Dict[str, Any]:
        """Convert signal to dictionary"""
        return {
            'ea_name': signal.ea_name,
            'ea_version': signal.ea_version,
            'signal_type': signal.signal_type,
            'symbol': signal.symbol,
            'direction': signal.direction,
            'trigger_price': signal.trigger_price,
            'm5_bos_level': signal.m5_bos_level,
            'm5_bos_direction': signal.m5_bos_direction,
            'm1_break_high': signal.m1_break_high,
            'm1_break_low': signal.m1_break_low,
            'pip_trigger': signal.pip_trigger,
            'timestamp': signal.timestamp,
            'raw_quality_score': signal.raw_quality_score
        }
    
    def _update_processing_metrics(self, processing_time_ms: float):
        """Update processing metrics"""
        self.processing_metrics['total_mql5_signals'] += 1
        
        # Update average processing time
        current_avg = self.processing_metrics['avg_processing_time_ms']
        total = self.processing_metrics['total_mql5_signals']
        
        self.processing_metrics['avg_processing_time_ms'] = (
            (current_avg * (total - 1)) + processing_time_ms
        ) / total
    
    async def _get_processing_metrics(self) -> MCPMessage:
        """Get processing metrics"""
        return MCPMessage(
            id=f"metrics_{datetime.utcnow().timestamp()}",
            method="mql5_processing_metrics",
            params={'metrics': self.processing_metrics},
            type=MessageType.RESPONSE
        )


class MQL5QualityEnhancer:
    """Enhances MQL5 signal quality analysis"""
    
    async def analyze_signal_quality(self, signal: MQL5SignalData) -> Dict[str, Any]:
        """Analyze and score MQL5 signal quality"""
        quality_factors = []
        
        # Factor 1: Break strength analysis
        break_strength = self._analyze_break_strength(signal)
        quality_factors.append(break_strength * 0.3)
        
        # Factor 2: Retest precision
        retest_precision = self._analyze_retest_precision(signal)
        quality_factors.append(retest_precision * 0.3)
        
        # Factor 3: Pattern timing
        timing_score = self._analyze_pattern_timing(signal)
        quality_factors.append(timing_score * 0.2)
        
        # Factor 4: Pip trigger efficiency
        trigger_efficiency = self._analyze_trigger_efficiency(signal)
        quality_factors.append(trigger_efficiency * 0.2)
        
        overall_score = sum(quality_factors)
        
        return {
            'overall_score': round(overall_score, 3),
            'break_strength': break_strength,
            'retest_precision': retest_precision,
            'timing_score': timing_score,
            'trigger_efficiency': trigger_efficiency,
            'pattern_strength': round(overall_score, 2),
            'quality_grade': self._get_quality_grade(overall_score)
        }
    
    def _analyze_break_strength(self, signal: MQL5SignalData) -> float:
        """Analyze the strength of the M5 BOS break"""
        # Distance from M5 BOS level to M1 break levels
        if signal.direction == 'BUY':
            break_distance = signal.m1_break_high - signal.m5_bos_level
        else:
            break_distance = signal.m5_bos_level - signal.m1_break_low
        
        # Convert to pips for scoring
        pip_value = 0.0001 if 'JPY' not in signal.symbol else 0.01
        break_pips = abs(break_distance) / pip_value
        
        # Score based on break distance (more distance = stronger break)
        if break_pips >= 5:
            return 0.9
        elif break_pips >= 3:
            return 0.7
        elif break_pips >= 1:
            return 0.5
        else:
            return 0.3
    
    def _analyze_retest_precision(self, signal: MQL5SignalData) -> float:
        """Analyze precision of the retest pattern"""
        # Range of the M1 break candle
        m1_range = signal.m1_break_high - signal.m1_break_low
        
        # Distance from trigger to M5 BOS level
        trigger_distance = abs(signal.trigger_price - signal.m5_bos_level)
        
        # Precision ratio (smaller distance = higher precision)
        if m1_range > 0:
            precision_ratio = trigger_distance / m1_range
            if precision_ratio <= 0.2:
                return 0.9  # Very precise
            elif precision_ratio <= 0.5:
                return 0.7  # Good precision
            elif precision_ratio <= 1.0:
                return 0.5  # Moderate precision
            else:
                return 0.3  # Low precision
        
        return 0.5  # Default if calculation fails
    
    def _analyze_pattern_timing(self, signal: MQL5SignalData) -> float:
        """Analyze timing quality of the pattern"""
        # High-frequency signals (0.2 pip trigger) get timing bonus
        if signal.pip_trigger <= 0.5:
            return 0.8  # Excellent timing for tight triggers
        elif signal.pip_trigger <= 1.0:
            return 0.6  # Good timing
        else:
            return 0.4  # Standard timing
    
    def _analyze_trigger_efficiency(self, signal: MQL5SignalData) -> float:
        """Analyze efficiency of the pip trigger"""
        # Smaller pip triggers are more efficient for M1 precision
        if signal.pip_trigger <= 0.2:
            return 0.9  # Ultra-precise
        elif signal.pip_trigger <= 0.5:
            return 0.7  # High precision
        elif signal.pip_trigger <= 1.0:
            return 0.5  # Standard
        else:
            return 0.3  # Lower precision
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert score to quality grade"""
        if score >= 0.8:
            return 'EXCELLENT'
        elif score >= 0.7:
            return 'GOOD'
        elif score >= 0.6:
            return 'FAIR'
        elif score >= 0.5:
            return 'ACCEPTABLE'
        else:
            return 'POOR'


class MQL5MLEnhancer:
    """ML-based enhancements for MQL5 signals"""
    
    async def enhance_signal(self, signal: MQL5SignalData, quality: Dict[str, Any]) -> Dict[str, Any]:
        """Apply ML enhancements to MQL5 signal"""
        # Placeholder for ML enhancement logic
        return {
            'confidence_boost': 0.1 if quality['overall_score'] > 0.7 else 0.0,
            'volatility_adjustment': 1.0,
            'risk_adjustment': 1.0,
            'trend_strength': 1.0,
            'momentum_adjustment': 1.0,
            'momentum_data': {
                'momentum_score': 0.7,
                'rsi': 55,
                'macd_signal': 1
            },
            'improvements': ['timing_optimization', 'risk_adjustment']
        }


class MQL5ContextAnalyzer:
    """Market context analysis for MQL5 signals"""
    
    async def analyze_market_context(self, signal: MQL5SignalData) -> Dict[str, Any]:
        """Analyze market context for signal"""
        # Placeholder for context analysis
        return {
            'session': self._get_trading_session(),
            'volatility': 'medium',
            'news_risk': 'normal',
            'context_score': 0.0,
            'conditions': {
                'market_open': True,
                'liquidity': 'normal'
            },
            'estimated_volume': 1000,
            'avg_volume': 800
        }
    
    def _get_trading_session(self) -> str:
        """Determine current trading session"""
        hour = datetime.utcnow().hour
        if 0 <= hour < 8:
            return 'asian'
        elif 8 <= hour < 16:
            return 'european'
        else:
            return 'american'