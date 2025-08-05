"""
U-Cell 1: Signal Validation
Validates incoming webhook signals for M5 BOS and M1 Break-and-Retest patterns
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from . import UCell, CellInput, CellOutput
import logging
import statistics
import time

logger = logging.getLogger(__name__)


class SignalValidationCell(UCell):
    """
    Enhanced U-Cell #1: Signal Validation with advanced price action recognition
    - Real-time M5 Break of Structure (BOS) pattern recognition <50ms
    - M1 Break-and-Retest quality scoring with 0.8 pip dynamic validation
    - Volume and momentum confirmation algorithms
    - False break filtration system
    - Multi-asset support (forex, crypto, indices, stocks)
    """
    
    def __init__(self):
        super().__init__(cell_id="U1", name="Enhanced Signal Validation")
        
        # Enhanced validation fields
        self.required_fields = [
            'symbol', 'timeframe', 'pattern_type', 'price_levels',
            'volume', 'timestamp', 'direction'
        ]
        self.valid_patterns = ['M5_BOS', 'M1_BREAK_RETEST', 'M5_BREAK_RETEST', 'M1_BOS']
        self.valid_timeframes = ['M1', 'M5', 'M15', 'H1']
        
        # Advanced pattern recognition engine
        self.pattern_engine = AdvancedPatternEngine()
        self.false_break_filter = FalseBreakFilter()
        
        # Performance tracking
        self.validation_metrics = {
            'total_validations': 0,
            'bos_patterns_detected': 0,
            'retest_patterns_detected': 0,
            'false_breaks_filtered': 0,
            'avg_processing_time_ms': 0.0,
            'pattern_accuracy_scores': [],
            'validation_success_rate': 0.0
        }
        
        # Dynamic thresholds based on market conditions
        self.dynamic_thresholds = {
            'volatility_adjustment': 1.0,
            'session_multiplier': 1.0,
            'news_risk_factor': 1.0
        }
    
    def validate_input(self, cell_input: CellInput) -> bool:
        """Validate signal structure and required fields"""
        data = cell_input.data
        
        # Check required fields
        for field in self.required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate pattern type
        if data.get('pattern_type') not in self.valid_patterns:
            logger.warning(f"Invalid pattern type: {data.get('pattern_type')}")
            return False
        
        # Validate timeframe
        if data.get('timeframe') not in self.valid_timeframes:
            logger.warning(f"Invalid timeframe: {data.get('timeframe')}")
            return False
        
        # Validate price levels structure
        price_levels = data.get('price_levels', {})
        required_levels = ['entry', 'stop_loss', 'take_profit']
        for level in required_levels:
            if level not in price_levels:
                logger.warning(f"Missing price level: {level}")
                return False
        
        return True
    
    def process(self, cell_input: CellInput) -> CellOutput:
        """Process and validate signal patterns"""
        data = cell_input.data
        
        try:
            # Extract signal components
            symbol = data['symbol']
            pattern_type = data['pattern_type']
            direction = data['direction']
            price_levels = data['price_levels']
            
            # Validate M5 BOS pattern
            if pattern_type == 'M5_BOS':
                validation_result = self._validate_bos_pattern(data)
            # Validate M1 Break-and-Retest
            elif pattern_type == 'M1_BREAK_RETEST':
                validation_result = self._validate_break_retest(data)
            else:
                validation_result = {'valid': False, 'reason': 'Unknown pattern'}
            
            if validation_result['valid']:
                # Calculate pip distances
                pip_data = self._calculate_pip_distances(symbol, price_levels)
                
                output_data = {
                    'symbol': symbol,
                    'pattern_type': pattern_type,
                    'direction': direction,
                    'price_levels': price_levels,
                    'pip_data': pip_data,
                    'validation': validation_result,
                    'timestamp': data['timestamp']
                }
                
                return CellOutput(
                    timestamp=datetime.utcnow(),
                    status='success',
                    data=output_data,
                    next_cell='U2',  # ML Analysis
                    trace_id=cell_input.trace_id
                )
            else:
                return CellOutput(
                    timestamp=datetime.utcnow(),
                    status='rejected',
                    data={'reason': validation_result.get('reason', 'Pattern validation failed')},
                    trace_id=cell_input.trace_id,
                    errors=[validation_result.get('reason', 'Invalid pattern')]
                )
                
        except Exception as e:
            logger.error(f"Signal validation error: {str(e)}")
            return CellOutput(
                timestamp=datetime.utcnow(),
                status='failed',
                data={},
                trace_id=cell_input.trace_id,
                errors=[str(e)]
            )
    
    def _validate_bos_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced M5 BOS pattern validation with advanced recognition"""
        validation_start = time.perf_counter()
        
        try:
            symbol = data['symbol']
            direction = data['direction']
            price_levels = data['price_levels']
            volume_data = data.get('volume', {})
            momentum_data = data.get('momentum', {})
            
            # 1. Advanced structure break analysis
            structure_analysis = self.pattern_engine.analyze_structure_break(
                symbol=symbol,
                direction=direction,
                price_levels=price_levels,
                timeframe='M5'
            )
            
            if not structure_analysis['valid_break']:
                return {
                    'valid': False, 
                    'reason': 'Invalid structure break',
                    'analysis': structure_analysis
                }
            
            # 2. Volume confirmation
            volume_confirmation = self.pattern_engine.validate_volume_confirmation(
                volume_data, 'BOS'
            )
            
            # 3. Momentum analysis
            momentum_score = self.pattern_engine.calculate_momentum_score(
                momentum_data, direction
            )
            
            # 4. False break filtration
            false_break_risk = self.false_break_filter.assess_false_break_risk(
                data, 'M5_BOS'
            )
            
            if false_break_risk > 0.7:  # High false break risk
                self.validation_metrics['false_breaks_filtered'] += 1
                return {
                    'valid': False,
                    'reason': 'High false break probability',
                    'false_break_risk': false_break_risk
                }
            
            # 5. Calculate overall confidence
            confidence_factors = {
                'structure_strength': structure_analysis['break_strength'],
                'volume_confirmation': volume_confirmation['score'],
                'momentum_score': momentum_score,
                'false_break_safety': 1.0 - false_break_risk
            }
            
            # Weighted confidence calculation
            overall_confidence = (
                confidence_factors['structure_strength'] * 0.35 +
                confidence_factors['volume_confirmation'] * 0.25 +
                confidence_factors['momentum_score'] * 0.25 +
                confidence_factors['false_break_safety'] * 0.15
            )
            
            # Apply dynamic adjustments
            adjusted_confidence = self._apply_dynamic_adjustments(
                overall_confidence, data
            )
            
            validation_result = {
                'valid': adjusted_confidence >= 0.75,
                'confidence': round(adjusted_confidence, 3),
                'structure_analysis': structure_analysis,
                'volume_confirmation': volume_confirmation,
                'momentum_score': round(momentum_score, 3),
                'false_break_risk': round(false_break_risk, 3),
                'confidence_factors': confidence_factors
            }
            
            if validation_result['valid']:
                self.validation_metrics['bos_patterns_detected'] += 1
            
            return validation_result
            
        except Exception as e:
            logger.error(f"BOS pattern validation error: {str(e)}")
            return {'valid': False, 'reason': f'Validation error: {str(e)}'}
        
        finally:
            # Track processing time for <50ms target
            processing_time = (time.perf_counter() - validation_start) * 1000
            self._update_processing_metrics(processing_time)
    
    def _validate_break_retest(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced M1 break-and-retest validation with 0.8 pip dynamic threshold"""
        validation_start = time.perf_counter()
        
        try:
            symbol = data['symbol']
            direction = data['direction']
            price_levels = data['price_levels']
            volume_data = data.get('volume', {})
            retest_quality_data = data.get('retest_quality', {})
            
            # 1. 0.8 pip dynamic deviation validation
            deviation_analysis = self.pattern_engine.analyze_retest_deviation(
                symbol=symbol,
                price_levels=price_levels,
                max_deviation_pips=0.8 * self.dynamic_thresholds['volatility_adjustment']
            )
            
            if not deviation_analysis['within_threshold']:
                return {
                    'valid': False,
                    'reason': f"Retest deviation too high: {deviation_analysis['deviation_pips']:.2f} pips",
                    'deviation_analysis': deviation_analysis
                }
            
            # 2. Multi-factor retest quality scoring
            quality_analysis = self.pattern_engine.calculate_retest_quality(
                symbol=symbol,
                direction=direction,
                price_levels=price_levels,
                volume_data=volume_data,
                retest_quality_data=retest_quality_data
            )
            
            # 3. Volume pattern analysis (declining volume is positive)
            volume_pattern = self.pattern_engine.analyze_retest_volume_pattern(
                volume_data
            )
            
            # 4. Time-based quality assessment
            time_quality = self.pattern_engine.assess_retest_timing(
                data.get('timing_data', {})
            )
            
            # 5. Multi-timeframe confirmation
            mtf_confirmation = self.pattern_engine.validate_mtf_alignment(
                data.get('mtf_confirmation', {}), direction
            )
            
            # 6. Calculate comprehensive retest score
            retest_factors = {
                'deviation_quality': 1.0 - (deviation_analysis['deviation_pips'] / 0.8),
                'pattern_quality': quality_analysis['overall_score'],
                'volume_pattern': volume_pattern['score'],
                'timing_quality': time_quality['score'],
                'mtf_alignment': mtf_confirmation['score']
            }
            
            # Weighted retest score calculation
            overall_retest_score = (
                retest_factors['deviation_quality'] * 0.30 +
                retest_factors['pattern_quality'] * 0.25 +
                retest_factors['volume_pattern'] * 0.20 +
                retest_factors['timing_quality'] * 0.15 +
                retest_factors['mtf_alignment'] * 0.10
            )
            
            # Apply session and news adjustments
            adjusted_score = self._apply_dynamic_adjustments(
                overall_retest_score, data
            )
            
            validation_result = {
                'valid': adjusted_score >= 0.75,
                'confidence': round(adjusted_score, 3),
                'deviation_analysis': deviation_analysis,
                'quality_analysis': quality_analysis,
                'volume_pattern': volume_pattern,
                'timing_quality': time_quality,
                'mtf_confirmation': mtf_confirmation,
                'retest_factors': retest_factors,
                'retest_quality_score': round(overall_retest_score, 3)
            }
            
            if validation_result['valid']:
                self.validation_metrics['retest_patterns_detected'] += 1
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Retest pattern validation error: {str(e)}")
            return {'valid': False, 'reason': f'Validation error: {str(e)}'}
        
        finally:
            # Track processing time for <50ms target
            processing_time = (time.perf_counter() - validation_start) * 1000
            self._update_processing_metrics(processing_time)
    
    def _calculate_pip_distances(self, symbol: str, price_levels: Dict[str, float]) -> Dict[str, float]:
        """Calculate pip distances for SL and TP"""
        # Determine pip value based on symbol
        if 'JPY' in symbol:
            pip_value = 0.01
        else:
            pip_value = 0.0001
        
        entry = price_levels['entry']
        sl = price_levels['stop_loss']
        tp = price_levels['take_profit']
        
        sl_pips = abs(entry - sl) / pip_value
        tp_pips = abs(tp - entry) / pip_value
        risk_reward = tp_pips / sl_pips if sl_pips > 0 else 0
        
        return {
            'sl_pips': round(sl_pips, 1),
            'tp_pips': round(tp_pips, 1),
            'risk_reward': round(risk_reward, 2),
            'pip_value': pip_value
        }
    
    def _apply_dynamic_adjustments(self, base_score: float, data: Dict[str, Any]) -> float:
        """Apply dynamic adjustments based on market conditions"""
        adjusted_score = base_score
        
        # Session-based adjustments
        session = data.get('market_session', 'unknown')
        if session in ['london', 'new_york', 'overlap']:
            adjusted_score *= 1.1  # Boost for major sessions
        elif session in ['tokyo', 'sydney']:
            adjusted_score *= 0.95  # Slight reduction for Asian sessions
        
        # Volatility adjustments
        volatility = data.get('volatility_level', 'medium')
        if volatility == 'high':
            adjusted_score *= 0.9  # Reduce confidence in high volatility
        elif volatility == 'low':
            adjusted_score *= 1.05  # Increase confidence in stable conditions
        
        # News risk adjustments
        news_risk = data.get('news_risk', 'normal')
        if news_risk == 'high':
            adjusted_score *= 0.8  # Significant reduction for high news risk
        elif news_risk == 'medium':
            adjusted_score *= 0.95
        
        return min(adjusted_score, 1.0)  # Cap at 1.0
    
    def _update_processing_metrics(self, processing_time_ms: float):
        """Update processing time metrics"""
        self.validation_metrics['total_validations'] += 1
        
        # Update average processing time
        current_avg = self.validation_metrics['avg_processing_time_ms']
        total_validations = self.validation_metrics['total_validations']
        
        self.validation_metrics['avg_processing_time_ms'] = (
            (current_avg * (total_validations - 1)) + processing_time_ms
        ) / total_validations
        
        # Log performance warnings if processing is slow
        if processing_time_ms > 50:  # Target <50ms
            logger.warning(f"Signal validation processing time exceeded target: {processing_time_ms:.2f}ms")
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get comprehensive validation metrics"""
        success_rate = 0.0
        if self.validation_metrics['total_validations'] > 0:
            successful_validations = (
                self.validation_metrics['bos_patterns_detected'] +
                self.validation_metrics['retest_patterns_detected']
            )
            success_rate = successful_validations / self.validation_metrics['total_validations']
        
        return {
            **self.validation_metrics,
            'validation_success_rate': round(success_rate, 3),
            'performance_target_met': self.validation_metrics['avg_processing_time_ms'] < 50.0
        }


class AdvancedPatternEngine:
    """Advanced pattern recognition engine for BOS and retest patterns"""
    
    def __init__(self):
        self.pip_calculators = {
            'EURUSD': 0.0001, 'GBPUSD': 0.0001, 'AUDUSD': 0.0001, 'NZDUSD': 0.0001,
            'USDCAD': 0.0001, 'USDCHF': 0.0001,
            'USDJPY': 0.01, 'EURJPY': 0.01, 'GBPJPY': 0.01,
            'XAUUSD': 0.01, 'XAGUSD': 0.001,
            'BTCUSD': 1.0, 'ETHUSD': 0.01, 'ADAUSD': 0.0001
        }
    
    def get_pip_value(self, symbol: str) -> float:
        """Get pip value for symbol with broker suffix handling"""
        clean_symbol = symbol.upper().replace('.', '').replace('_', '').replace('#', '')[:6]
        
        for base_symbol, pip_value in self.pip_calculators.items():
            if clean_symbol.startswith(base_symbol):
                return pip_value
        
        # Smart defaults based on symbol characteristics
        if any(crypto in clean_symbol for crypto in ['BTC', 'ETH', 'ADA', 'DOT']):
            return 1.0 if 'BTC' in clean_symbol else 0.01
        elif 'JPY' in clean_symbol:
            return 0.01
        elif any(metal in clean_symbol for metal in ['XAU', 'XAG', 'GOLD', 'SILVER']):
            return 0.01
        else:
            return 0.0001  # Default forex
    
    def calculate_pips(self, symbol: str, price1: float, price2: float) -> float:
        """Calculate pip distance between prices"""
        pip_value = self.get_pip_value(symbol)
        return abs(price1 - price2) / pip_value
    
    def analyze_structure_break(self, symbol: str, direction: str, price_levels: Dict[str, Any], timeframe: str) -> Dict[str, Any]:
        """Analyze structure break strength and validity"""
        try:
            current_price = price_levels.get('current_price', 0)
            previous_high = price_levels.get('previous_high', 0)
            previous_low = price_levels.get('previous_low', 0)
            structure_level = price_levels.get('structure_break_level', 0)
            
            analysis = {
                'valid_break': False,
                'break_strength': 0.0,
                'break_distance_pips': 0.0,
                'structure_significance': 'low'
            }
            
            if direction.upper() == 'BUY':
                if current_price > previous_high and structure_level > 0:
                    analysis['valid_break'] = True
                    analysis['break_distance_pips'] = self.calculate_pips(symbol, current_price, structure_level)
                    
                    # Calculate break strength (more distance = stronger break)
                    if analysis['break_distance_pips'] >= 10:
                        analysis['break_strength'] = min(0.9, 0.6 + (analysis['break_distance_pips'] - 10) * 0.02)
                        analysis['structure_significance'] = 'high'
                    elif analysis['break_distance_pips'] >= 5:
                        analysis['break_strength'] = 0.6 + (analysis['break_distance_pips'] - 5) * 0.04
                        analysis['structure_significance'] = 'medium'
                    else:
                        analysis['break_strength'] = 0.3 + analysis['break_distance_pips'] * 0.06
                        analysis['structure_significance'] = 'low'
            
            elif direction.upper() == 'SELL':
                if current_price < previous_low and structure_level > 0:
                    analysis['valid_break'] = True
                    analysis['break_distance_pips'] = self.calculate_pips(symbol, structure_level, current_price)
                    
                    if analysis['break_distance_pips'] >= 10:
                        analysis['break_strength'] = min(0.9, 0.6 + (analysis['break_distance_pips'] - 10) * 0.02)
                        analysis['structure_significance'] = 'high'
                    elif analysis['break_distance_pips'] >= 5:
                        analysis['break_strength'] = 0.6 + (analysis['break_distance_pips'] - 5) * 0.04
                        analysis['structure_significance'] = 'medium'
                    else:
                        analysis['break_strength'] = 0.3 + analysis['break_distance_pips'] * 0.06
                        analysis['structure_significance'] = 'low'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Structure break analysis error: {str(e)}")
            return {'valid_break': False, 'break_strength': 0.0, 'break_distance_pips': 0.0}
    
    def validate_volume_confirmation(self, volume_data: Dict[str, Any], pattern_type: str) -> Dict[str, Any]:
        """Validate volume confirmation for pattern"""
        try:
            current_volume = volume_data.get('current_volume', 0)
            avg_volume = volume_data.get('avg_volume_20', 0)
            
            confirmation = {
                'confirmed': False,
                'score': 0.0,
                'volume_ratio': 0.0
            }
            
            if avg_volume > 0:
                confirmation['volume_ratio'] = current_volume / avg_volume
                
                if pattern_type == 'BOS':
                    # BOS requires volume spike (1.5x+ average)
                    if confirmation['volume_ratio'] >= 1.5:
                        confirmation['confirmed'] = True
                        confirmation['score'] = min(0.9, 0.5 + (confirmation['volume_ratio'] - 1.5) * 0.2)
                    else:
                        confirmation['score'] = max(0.1, confirmation['volume_ratio'] * 0.3)
                        
                elif pattern_type == 'RETEST':
                    # Retest prefers declining volume (0.7x or less)
                    if confirmation['volume_ratio'] <= 0.7:
                        confirmation['confirmed'] = True
                        confirmation['score'] = min(0.8, 0.8 - (confirmation['volume_ratio'] - 0.3) * 0.5)
                    else:
                        confirmation['score'] = max(0.2, 0.8 - confirmation['volume_ratio'] * 0.3)
            else:
                confirmation['score'] = 0.5  # Neutral if no volume data
            
            return confirmation
            
        except Exception as e:
            logger.error(f"Volume confirmation error: {str(e)}")
            return {'confirmed': False, 'score': 0.0, 'volume_ratio': 0.0}
    
    def calculate_momentum_score(self, momentum_data: Dict[str, Any], direction: str) -> float:
        """Calculate momentum score for direction"""
        try:
            momentum_score = momentum_data.get('momentum_score', 0)
            rsi = momentum_data.get('rsi', 50)
            macd_signal = momentum_data.get('macd_signal', 0)
            
            # Base momentum score
            base_score = abs(momentum_score) if momentum_score else 0.5
            
            # RSI confirmation
            rsi_score = 0.5
            if direction.upper() == 'BUY':
                if rsi > 50:
                    rsi_score = min(0.8, 0.5 + (rsi - 50) * 0.006)  # 0.5 to 0.8 for RSI 50-100
                else:
                    rsi_score = max(0.2, 0.5 - (50 - rsi) * 0.006)  # 0.2 to 0.5 for RSI 0-50
            elif direction.upper() == 'SELL':
                if rsi < 50:
                    rsi_score = min(0.8, 0.5 + (50 - rsi) * 0.006)
                else:
                    rsi_score = max(0.2, 0.5 - (rsi - 50) * 0.006)
            
            # MACD confirmation
            macd_score = 0.5
            if macd_signal != 0:
                if (direction.upper() == 'BUY' and macd_signal > 0) or (direction.upper() == 'SELL' and macd_signal < 0):
                    macd_score = min(0.8, 0.5 + abs(macd_signal) * 0.1)
                else:
                    macd_score = max(0.2, 0.5 - abs(macd_signal) * 0.1)
            
            # Combined momentum score
            combined_score = (base_score * 0.5 + rsi_score * 0.3 + macd_score * 0.2)
            return min(1.0, max(0.0, combined_score))
            
        except Exception as e:
            logger.error(f"Momentum calculation error: {str(e)}")
            return 0.5
    
    def analyze_retest_deviation(self, symbol: str, price_levels: Dict[str, Any], max_deviation_pips: float) -> Dict[str, Any]:
        """Analyze retest deviation from break level"""
        try:
            break_level = price_levels.get('break_level', 0)
            retest_level = price_levels.get('retest_level', 0)
            
            if break_level == 0 or retest_level == 0:
                return {'within_threshold': False, 'deviation_pips': 999.0, 'deviation_ratio': 1.0}
            
            deviation_pips = self.calculate_pips(symbol, break_level, retest_level)
            deviation_ratio = deviation_pips / max_deviation_pips
            
            return {
                'within_threshold': deviation_pips <= max_deviation_pips,
                'deviation_pips': round(deviation_pips, 2),
                'deviation_ratio': round(deviation_ratio, 3),
                'quality_score': max(0.0, 1.0 - deviation_ratio) if deviation_ratio <= 1.0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Retest deviation analysis error: {str(e)}")
            return {'within_threshold': False, 'deviation_pips': 999.0, 'deviation_ratio': 1.0}
    
    def calculate_retest_quality(self, symbol: str, direction: str, price_levels: Dict[str, Any], 
                               volume_data: Dict[str, Any], retest_quality_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive retest quality score"""
        try:
            quality_factors = []
            
            # Factor 1: Price proximity to break level
            deviation_analysis = self.analyze_retest_deviation(symbol, price_levels, 0.8)
            quality_factors.append(deviation_analysis['quality_score'] * 0.4)
            
            # Factor 2: Volume pattern (declining is better)
            volume_confirmation = self.validate_volume_confirmation(volume_data, 'RETEST')
            quality_factors.append(volume_confirmation['score'] * 0.3)
            
            # Factor 3: Pattern quality from technical analysis
            pattern_score = retest_quality_data.get('pattern_score', 0.5)
            quality_factors.append(pattern_score * 0.2)
            
            # Factor 4: Speed of retest (faster often better)
            time_factor = retest_quality_data.get('time_factor', 0.5)
            quality_factors.append(time_factor * 0.1)
            
            overall_score = sum(quality_factors)
            
            return {
                'overall_score': round(overall_score, 3),
                'deviation_quality': deviation_analysis['quality_score'],
                'volume_quality': volume_confirmation['score'],
                'pattern_quality': pattern_score,
                'timing_quality': time_factor,
                'quality_grade': self._get_quality_grade(overall_score)
            }
            
        except Exception as e:
            logger.error(f"Retest quality calculation error: {str(e)}")
            return {'overall_score': 0.0, 'quality_grade': 'F'}
    
    def analyze_retest_volume_pattern(self, volume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze volume pattern during retest phase"""
        try:
            break_volume = volume_data.get('break_volume', 0)
            retest_volume = volume_data.get('retest_volume', 0)
            avg_volume = volume_data.get('avg_volume_20', 0)
            
            analysis = {
                'score': 0.5,
                'pattern': 'neutral',
                'volume_decline_ratio': 0.0
            }
            
            if break_volume > 0 and retest_volume > 0:
                analysis['volume_decline_ratio'] = retest_volume / break_volume
                
                if analysis['volume_decline_ratio'] <= 0.5:
                    analysis['score'] = 0.9
                    analysis['pattern'] = 'excellent_decline'
                elif analysis['volume_decline_ratio'] <= 0.7:
                    analysis['score'] = 0.7
                    analysis['pattern'] = 'good_decline'
                elif analysis['volume_decline_ratio'] <= 0.9:
                    analysis['score'] = 0.5
                    analysis['pattern'] = 'moderate_decline'
                else:
                    analysis['score'] = 0.2
                    analysis['pattern'] = 'insufficient_decline'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Volume pattern analysis error: {str(e)}")
            return {'score': 0.5, 'pattern': 'unknown', 'volume_decline_ratio': 0.0}
    
    def assess_retest_timing(self, timing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess timing quality of retest"""
        try:
            break_time = timing_data.get('break_timestamp')
            retest_time = timing_data.get('retest_timestamp')
            
            if not break_time or not retest_time:
                return {'score': 0.5, 'timing_grade': 'unknown'}
            
            # Calculate time difference
            if isinstance(break_time, str):
                break_time = datetime.fromisoformat(break_time.replace('Z', '+00:00'))
            if isinstance(retest_time, str):
                retest_time = datetime.fromisoformat(retest_time.replace('Z', '+00:00'))
            
            time_diff = abs((retest_time - break_time).total_seconds()) / 60  # minutes
            
            # Optimal retest timing scoring
            if time_diff <= 30:  # Within 30 minutes
                score = 0.9
                grade = 'excellent'
            elif time_diff <= 60:  # Within 1 hour
                score = 0.7
                grade = 'good'
            elif time_diff <= 120:  # Within 2 hours
                score = 0.5
                grade = 'fair'
            elif time_diff <= 240:  # Within 4 hours
                score = 0.3
                grade = 'poor'
            else:
                score = 0.1
                grade = 'very_poor'
            
            return {
                'score': score,
                'timing_grade': grade,
                'time_diff_minutes': round(time_diff, 1)
            }
            
        except Exception as e:
            logger.error(f"Timing assessment error: {str(e)}")
            return {'score': 0.5, 'timing_grade': 'unknown'}
    
    def validate_mtf_alignment(self, mtf_data: Dict[str, Any], direction: str) -> Dict[str, Any]:
        """Validate multi-timeframe alignment"""
        try:
            higher_tf_trend = mtf_data.get('higher_tf_trend', 'neutral')
            trend_strength = mtf_data.get('trend_strength', 0.5)
            
            alignment = {
                'score': 0.5,
                'aligned': False,
                'trend_strength': trend_strength
            }
            
            if higher_tf_trend == 'neutral':
                alignment['score'] = 0.5
                alignment['aligned'] = True
            elif (direction.upper() == 'BUY' and higher_tf_trend == 'bullish') or \
                 (direction.upper() == 'SELL' and higher_tf_trend == 'bearish'):
                alignment['score'] = 0.7 + (trend_strength * 0.2)
                alignment['aligned'] = True
            else:
                alignment['score'] = 0.3 - (trend_strength * 0.2)
                alignment['aligned'] = False
            
            return alignment
            
        except Exception as e:
            logger.error(f"MTF alignment validation error: {str(e)}")
            return {'score': 0.5, 'aligned': False, 'trend_strength': 0.5}
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 0.9:
            return 'A+'
        elif score >= 0.8:
            return 'A'
        elif score >= 0.7:
            return 'B+'
        elif score >= 0.6:
            return 'B'
        elif score >= 0.5:
            return 'C'
        elif score >= 0.4:
            return 'D'
        else:
            return 'F'


class FalseBreakFilter:
    """Advanced false break filtration system"""
    
    def __init__(self):
        self.false_break_indicators = [
            'low_volume_break',
            'immediate_reversal',
            'weak_momentum',
            'news_driven_spike',
            'thin_liquidity',
            'weekend_gap'
        ]
    
    def assess_false_break_risk(self, signal_data: Dict[str, Any], pattern_type: str) -> float:
        """Assess probability of false break"""
        try:
            risk_factors = []
            
            # Factor 1: Volume analysis
            volume_data = signal_data.get('volume', {})
            current_volume = volume_data.get('current_volume', 0)
            avg_volume = volume_data.get('avg_volume_20', 0)
            
            if avg_volume > 0:
                volume_ratio = current_volume / avg_volume
                if volume_ratio < 0.8:  # Low volume break
                    risk_factors.append(0.3)
                elif volume_ratio < 1.2:
                    risk_factors.append(0.1)
                else:
                    risk_factors.append(0.0)
            else:
                risk_factors.append(0.2)  # Unknown volume = moderate risk
            
            # Factor 2: Price action after break
            price_action = signal_data.get('price_action_post_break', {})
            if price_action:
                reversal_strength = price_action.get('reversal_strength', 0)
                if reversal_strength > 0.5:
                    risk_factors.append(0.4)  # Strong reversal = high false break risk
                else:
                    risk_factors.append(reversal_strength * 0.2)
            else:
                risk_factors.append(0.1)
            
            # Factor 3: Market context
            market_context = signal_data.get('market_context', {})
            news_events = market_context.get('high_impact_news_nearby', False)
            if news_events:
                risk_factors.append(0.25)  # News-driven moves more likely to reverse
            else:
                risk_factors.append(0.0)
            
            # Factor 4: Time context
            timing = signal_data.get('timing_context', {})
            is_weekend_gap = timing.get('weekend_gap', False)
            thin_liquidity = timing.get('thin_liquidity_period', False)
            
            if is_weekend_gap:
                risk_factors.append(0.3)
            elif thin_liquidity:
                risk_factors.append(0.2)
            else:
                risk_factors.append(0.0)
            
            # Calculate overall false break risk
            overall_risk = min(1.0, sum(risk_factors))
            
            return round(overall_risk, 3)
            
        except Exception as e:
            logger.error(f"False break risk assessment error: {str(e)}")
            return 0.5  # Moderate risk if assessment fails