"""
U-Cell 2: ML Analysis
Deep analysis using TensorFlow/Scikit-learn for signal validation and probability calculation
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
from . import UCell, CellInput, CellOutput
import logging
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)


class MLAnalysisCell(UCell):
    """
    ML-based signal analysis using Claude Code integration
    - Pattern probability calculation
    - SL/TP optimization
    - Market condition analysis
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        super().__init__(cell_id="U2", name="ML Analysis")
        self.model_path = model_path or Path("models/signal_classifier.pkl")
        self.scaler_path = Path("models/feature_scaler.pkl")
        self.model = None
        self.scaler = None
        self._load_models()
        
        # Feature engineering parameters
        self.feature_config = {
            'price_features': ['rsi', 'macd', 'bb_position', 'atr'],
            'pattern_features': ['pattern_strength', 'volume_profile', 'trend_alignment'],
            'market_features': ['volatility', 'session', 'correlation']
        }
    
    def _load_models(self):
        """Load pre-trained ML models"""
        try:
            if self.model_path.exists():
                self.model = joblib.load(self.model_path)
                logger.info("ML model loaded successfully")
            else:
                logger.warning("ML model not found, using rule-based fallback")
            
            if self.scaler_path.exists():
                self.scaler = joblib.load(self.scaler_path)
        except Exception as e:
            logger.error(f"Model loading error: {str(e)}")
    
    def validate_input(self, cell_input: CellInput) -> bool:
        """Validate input from Signal Validation cell"""
        required_keys = ['symbol', 'pattern_type', 'direction', 'price_levels', 'pip_data']
        return all(key in cell_input.data for key in required_keys)
    
    def process(self, cell_input: CellInput) -> CellOutput:
        """Process signal through ML analysis"""
        data = cell_input.data
        
        try:
            # Extract features for ML model
            features = self._extract_features(data)
            
            # Get ML predictions
            if self.model:
                probability, confidence = self._get_ml_prediction(features)
            else:
                # Fallback to rule-based analysis
                probability, confidence = self._rule_based_analysis(data)
            
            # Optimize SL/TP levels
            optimized_levels = self._optimize_levels(
                data['price_levels'],
                probability,
                data['pip_data']
            )
            
            # Market condition assessment
            market_conditions = self._assess_market_conditions(data)
            
            # Prepare output
            analysis_result = {
                'symbol': data['symbol'],
                'pattern_type': data['pattern_type'],
                'direction': data['direction'],
                'probability': round(probability, 4),
                'confidence': round(confidence, 4),
                'original_levels': data['price_levels'],
                'optimized_levels': optimized_levels,
                'pip_data': data['pip_data'],
                'market_conditions': market_conditions,
                'recommendation': self._get_recommendation(probability, confidence),
                'ml_features': features
            }
            
            # Decision logic
            if probability >= 0.65 and confidence >= 0.70:
                status = 'success'
                next_cell = 'U3'  # Risk Engine
            else:
                status = 'rejected'
                next_cell = None
            
            return CellOutput(
                timestamp=datetime.utcnow(),
                status=status,
                data=analysis_result,
                next_cell=next_cell,
                trace_id=cell_input.trace_id
            )
            
        except Exception as e:
            logger.error(f"ML analysis error: {str(e)}")
            return CellOutput(
                timestamp=datetime.utcnow(),
                status='failed',
                data={},
                trace_id=cell_input.trace_id,
                errors=[str(e)]
            )
    
    def _extract_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract features for ML model"""
        features = []
        
        # Price action features
        pip_data = data['pip_data']
        features.extend([
            pip_data['sl_pips'],
            pip_data['tp_pips'],
            pip_data['risk_reward']
        ])
        
        # Pattern features
        pattern_strength = 0.8 if data['pattern_type'] == 'M1_BREAK_RETEST' else 0.7
        features.append(pattern_strength)
        
        # Direction encoding
        direction_encoded = 1 if data['direction'] == 'BUY' else -1
        features.append(direction_encoded)
        
        # Add dummy features if model expects more
        while len(features) < 10:
            features.append(0.5)
        
        return np.array(features).reshape(1, -1)
    
    def _get_ml_prediction(self, features: np.ndarray) -> Tuple[float, float]:
        """Get ML model prediction"""
        try:
            if self.scaler:
                features = self.scaler.transform(features)
            
            # Get probability prediction
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(features)[0]
                probability = proba[1]  # Probability of success
                # Confidence based on prediction certainty
                confidence = max(proba)
            else:
                prediction = self.model.predict(features)[0]
                probability = prediction
                confidence = 0.75  # Default confidence
            
            return probability, confidence
            
        except Exception as e:
            logger.error(f"ML prediction error: {str(e)}")
            return 0.5, 0.5
    
    def _rule_based_analysis(self, data: Dict[str, Any]) -> Tuple[float, float]:
        """Fallback rule-based analysis"""
        pip_data = data['pip_data']
        
        # Base probability on risk-reward and pattern type
        base_prob = 0.5
        
        # Risk-reward adjustment
        if pip_data['risk_reward'] >= 2.0:
            base_prob += 0.15
        elif pip_data['risk_reward'] >= 1.5:
            base_prob += 0.10
        else:
            base_prob -= 0.10
        
        # Pattern type adjustment
        if data['pattern_type'] == 'M1_BREAK_RETEST':
            base_prob += 0.10
        
        # Reasonable pip distance check
        if 10 <= pip_data['sl_pips'] <= 50:
            base_prob += 0.05
        
        # Confidence based on data quality
        confidence = 0.7 if base_prob > 0.6 else 0.6
        
        return min(max(base_prob, 0.0), 1.0), confidence
    
    def _optimize_levels(self, price_levels: Dict[str, float], 
                        probability: float, pip_data: Dict[str, float]) -> Dict[str, float]:
        """Optimize SL/TP levels based on ML analysis"""
        optimized = price_levels.copy()
        
        # Adjust based on probability
        if probability > 0.75:
            # High probability - can use tighter SL
            sl_adjustment = 0.95
            tp_adjustment = 1.05
        elif probability > 0.65:
            # Medium probability - standard levels
            sl_adjustment = 1.0
            tp_adjustment = 1.0
        else:
            # Lower probability - wider SL
            sl_adjustment = 1.05
            tp_adjustment = 0.95
        
        # Apply adjustments
        entry = price_levels['entry']
        sl_distance = abs(entry - price_levels['stop_loss']) * sl_adjustment
        tp_distance = abs(price_levels['take_profit'] - entry) * tp_adjustment
        
        if price_levels['stop_loss'] < entry:  # Buy trade
            optimized['stop_loss'] = entry - sl_distance
            optimized['take_profit'] = entry + tp_distance
        else:  # Sell trade
            optimized['stop_loss'] = entry + sl_distance
            optimized['take_profit'] = entry - tp_distance
        
        return optimized
    
    def _assess_market_conditions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess current market conditions"""
        # Simplified market condition assessment
        return {
            'volatility': 'normal',  # Would calculate from ATR/price data
            'trend_strength': 'moderate',  # Would calculate from MA alignment
            'session': self._get_trading_session(),
            'market_phase': 'trending'  # Would determine from price action
        }
    
    def _get_trading_session(self) -> str:
        """Determine current trading session"""
        from datetime import datetime
        hour = datetime.utcnow().hour
        
        if 0 <= hour < 8:
            return 'asian'
        elif 8 <= hour < 16:
            return 'european'
        else:
            return 'american'
    
    def _get_recommendation(self, probability: float, confidence: float) -> str:
        """Generate trade recommendation"""
        if probability >= 0.75 and confidence >= 0.80:
            return 'STRONG_TRADE'
        elif probability >= 0.65 and confidence >= 0.70:
            return 'TRADE'
        elif probability >= 0.55:
            return 'WEAK_TRADE'
        else:
            return 'NO_TRADE'