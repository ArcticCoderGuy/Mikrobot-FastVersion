"""
Lightning Bolt Strategy - Complete Implementation
================================================

3-Phase Lightning Bolt Pattern:
- Phase 1: M5 BOS (Break of Structure) 
- Phase 2: M1 Break-and-Retest confirmation
- Phase 3: Entry at +0.6 Ylipip above/below retest completion

Based on course materials and professional trading education.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

from ..core.mt5_direct_connector import Candle, Tick, OrderType
from ..notifications.imessage_notifier import (
    imessage_notifier, notify_bos_detected, notify_retest_confirmed, 
    notify_entry_executed, LightningBoltPhase
)

logger = logging.getLogger(__name__)

class TrendDirection(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIDEWAYS = "SIDEWAYS"

class PatternPhase(Enum):
    WAITING = "WAITING"
    M5_BOS_DETECTED = "M5_BOS_DETECTED"
    M1_RETEST_CONFIRMED = "M1_RETEST_CONFIRMED"
    ENTRY_TRIGGERED = "ENTRY_TRIGGERED"

@dataclass
class StructureLevel:
    """Support/Resistance level for BOS detection"""
    price: float
    time: datetime
    strength: int  # Number of touches
    type: str  # "SUPPORT" or "RESISTANCE"

@dataclass
class BOSPattern:
    """Break of Structure pattern data"""
    symbol: str
    direction: TrendDirection
    break_level: float
    break_time: datetime
    retest_target: float
    confidence: float
    phase: PatternPhase

@dataclass
class LightningBoltSignal:
    """Complete Lightning Bolt trading signal"""
    symbol: str
    direction: TrendDirection
    entry_price: float
    stop_loss: float
    take_profit: float
    ylipip_offset: float
    confidence: float
    phase: PatternPhase
    timestamp: datetime

class YlipipCalculator:
    """Calculate Ylipip values for different asset classes"""
    
    YLIPIP_VALUES = {
        # Forex pairs (in pips, multiply by point size)
        "EURUSD": 0.6 * 0.0001,
        "GBPUSD": 0.6 * 0.0001, 
        "USDJPY": 0.6 * 0.01,
        "USDCHF": 0.6 * 0.0001,
        "AUDUSD": 0.6 * 0.0001,
        "USDCAD": 0.6 * 0.0001,
        "NZDUSD": 0.6 * 0.0001,
        
        # Top 10 Crypto CFDs (in price points)
        "BTCUSD": 0.6 * 10.0,    # 6 points
        "ETHUSD": 0.6 * 1.0,     # 0.6 points
        "BNBUSD": 0.6 * 0.1,     # 0.06 points
        "XRPUSD": 0.6 * 0.001,   # 0.0006 points
        "SOLUSD": 0.6 * 0.01,    # 0.006 points
        "ADAUSD": 0.6 * 0.001,   # 0.0006 points
        "AVAXUSD": 0.6 * 0.01,   # 0.006 points
        "DOTUSD": 0.6 * 0.01,    # 0.006 points
        "LINKUSD": 0.6 * 0.01,   # 0.006 points
        "LTCUSD": 0.6 * 0.1,     # 0.06 points
        
        # Index CFDs (in index points)
        "SPX500": 0.6 * 1.0,     # 0.6 points
        "NAS100": 0.6 * 1.0,     # 0.6 points
        "UK100": 0.6 * 1.0,      # 0.6 points
        "GER40": 0.6 * 1.0,      # 0.6 points
        "FRA40": 0.6 * 1.0,      # 0.6 points
        "AUS200": 0.6 * 1.0,     # 0.6 points
        "JPN225": 0.6 * 10.0,    # 6 points
    }
    
    @classmethod
    def get_ylipip(cls, symbol: str) -> float:
        """Get 0.6 Ylipip value for symbol"""
        return cls.YLIPIP_VALUES.get(symbol, 0.6 * 0.0001)  # Default to forex

class StructureAnalyzer:
    """Market structure analysis for HH/HL/LH/LL patterns"""
    
    def __init__(self):
        self.lookback_periods = 50  # Increased for better structure detection
        self.min_structure_strength = 5  # Much higher minimum strength
        self.min_break_strength = 0.0005  # Minimum 5 pips break for forex
    
    def identify_structure_levels(self, candles: List[Candle]) -> List[StructureLevel]:
        """Identify key support/resistance levels"""
        if len(candles) < self.lookback_periods:
            return []
        
        levels = []
        
        # Find swing highs and lows
        for i in range(self.lookback_periods, len(candles) - self.lookback_periods):
            candle = candles[i]
            
            # Check for swing high
            is_swing_high = True
            for j in range(i - self.lookback_periods, i + self.lookback_periods + 1):
                if j != i and candles[j].high > candle.high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                level = StructureLevel(
                    price=candle.high,
                    time=candle.time,
                    strength=self._calculate_level_strength(candles, candle.high, "RESISTANCE"),
                    type="RESISTANCE"
                )
                levels.append(level)
            
            # Check for swing low
            is_swing_low = True
            for j in range(i - self.lookback_periods, i + self.lookback_periods + 1):
                if j != i and candles[j].low < candle.low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                level = StructureLevel(
                    price=candle.low,
                    time=candle.time,
                    strength=self._calculate_level_strength(candles, candle.low, "SUPPORT"),
                    type="SUPPORT"
                )
                levels.append(level)
        
        # Filter by strength and remove duplicates
        strong_levels = [l for l in levels if l.strength >= self.min_structure_strength]
        return self._remove_duplicate_levels(strong_levels)
    
    def _calculate_level_strength(self, candles: List[Candle], price: float, level_type: str) -> int:
        """Calculate how many times a level has been tested"""
        touches = 0
        tolerance = price * 0.001  # 0.1% tolerance
        
        for candle in candles:
            if level_type == "RESISTANCE":
                if abs(candle.high - price) <= tolerance:
                    touches += 1
            elif level_type == "SUPPORT":
                if abs(candle.low - price) <= tolerance:
                    touches += 1
        
        return touches
    
    def _remove_duplicate_levels(self, levels: List[StructureLevel]) -> List[StructureLevel]:
        """Remove duplicate levels that are too close"""
        if not levels:
            return []
        
        unique_levels = []
        for level in sorted(levels, key=lambda x: x.strength, reverse=True):
            is_duplicate = False
            for existing in unique_levels:
                if abs(level.price - existing.price) / existing.price < 0.001:  # 0.1% tolerance
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_levels.append(level)
        
        return unique_levels
    
    def detect_trend_direction(self, candles: List[Candle]) -> TrendDirection:
        """Analyze HH/HL/LH/LL pattern to determine trend"""
        if len(candles) < 10:
            return TrendDirection.SIDEWAYS
        
        recent_candles = candles[-10:]  # Last 10 candles
        highs = [c.high for c in recent_candles]
        lows = [c.low for c in recent_candles]
        
        # Count higher highs and higher lows
        hh_count = sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])
        hl_count = sum(1 for i in range(1, len(lows)) if lows[i] > lows[i-1])
        
        # Count lower highs and lower lows  
        lh_count = sum(1 for i in range(1, len(highs)) if highs[i] < highs[i-1])
        ll_count = sum(1 for i in range(1, len(lows)) if lows[i] < lows[i-1])
        
        # Determine trend based on pattern
        bullish_score = hh_count + hl_count
        bearish_score = lh_count + ll_count
        
        if bullish_score > bearish_score + 2:
            return TrendDirection.BULLISH
        elif bearish_score > bullish_score + 2:
            return TrendDirection.BEARISH
        else:
            return TrendDirection.SIDEWAYS

class LightningBoltStrategy:
    """
    Complete Lightning Bolt Strategy Implementation
    
    Phase 1: M5 BOS Detection
    Phase 2: M1 Break-and-Retest Confirmation
    Phase 3: Entry at +0.6 Ylipip
    """
    
    def __init__(self, mt5_connector):
        self.mt5 = mt5_connector
        self.structure_analyzer = StructureAnalyzer()
        self.ylipip_calc = YlipipCalculator()
        
        # Pattern tracking
        self.active_patterns: Dict[str, BOSPattern] = {}
        self.trade_signals: List[LightningBoltSignal] = []
        
        # Strategy settings - STRICTER FOR REAL TRADING
        self.min_confidence = 0.85  # Higher threshold to reduce noise
        self.max_risk_per_trade = 0.0015  # 0.15% risk
        self.rr_ratio = 2.0  # 1:2 Risk/Reward
        
        # Signal filtering
        self.signal_cooldown = {}  # Track last signal time per symbol
        self.cooldown_minutes = 15  # No repeat signals for 15 minutes
        self.recent_signals = set()  # Track recent signals to avoid duplicates
        
        logger.info("⚡ Lightning Bolt Strategy initialized")
    
    def _is_symbol_in_cooldown(self, symbol: str) -> bool:
        """Check if symbol is in cooldown period"""
        if symbol not in self.signal_cooldown:
            return False
        
        time_since_last = datetime.now() - self.signal_cooldown[symbol]
        return time_since_last.total_seconds() < (self.cooldown_minutes * 60)
    
    def _add_symbol_to_cooldown(self, symbol: str):
        """Add symbol to cooldown period"""
        self.signal_cooldown[symbol] = datetime.now()
    
    async def analyze_symbol(self, symbol: str) -> Optional[LightningBoltSignal]:
        """Analyze symbol for Lightning Bolt pattern with strict filtering"""
        
        # Check cooldown first to avoid spam
        if self._is_symbol_in_cooldown(symbol):
            return None
        
        try:
            # Get M5 and M1 candles
            m5_candles = await self.mt5.get_candles(symbol, "M5", 100)
            m1_candles = await self.mt5.get_candles(symbol, "M1", 200)
            
            if not m5_candles or not m1_candles:
                return None
            
            # Phase 1: M5 BOS Detection
            bos_pattern = await self._detect_m5_bos(symbol, m5_candles)
            if not bos_pattern:
                return None
            
            # Phase 2: M1 Break-and-Retest Confirmation
            if bos_pattern.phase == PatternPhase.M5_BOS_DETECTED:
                retest_confirmed = await self._confirm_m1_retest(symbol, m1_candles, bos_pattern)
                if retest_confirmed:
                    bos_pattern.phase = PatternPhase.M1_RETEST_CONFIRMED
            
            # Phase 3: Entry Signal Generation
            if bos_pattern.phase == PatternPhase.M1_RETEST_CONFIRMED:
                signal = await self._generate_entry_signal(symbol, bos_pattern)
                if signal:
                    self.trade_signals.append(signal)
                    logger.info(f"⚡ LIGHTNING BOLT SIGNAL: {symbol} {signal.direction.value} @ {signal.entry_price}")
                    return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Analysis error for {symbol}: {e}")
            return None
    
    async def _detect_m5_bos(self, symbol: str, candles: List[Candle]) -> Optional[BOSPattern]:
        """Phase 1: Detect M5 Break of Structure - STRICT VALIDATION"""
        
        # Need sufficient candles for proper analysis
        if len(candles) < 100:
            return None
        
        # Identify structure levels with strict criteria
        levels = self.structure_analyzer.identify_structure_levels(candles)
        if not levels or len(levels) < 3:  # Need at least 3 strong levels
            return None
        
        # Get current trend direction
        trend = self.structure_analyzer.detect_trend_direction(candles)
        if trend == TrendDirection.SIDEWAYS:
            return None
        
        # Check only the LATEST candle for BOS (not last 5)
        latest_candle = candles[-1]  # Only most recent candle
        
        # Get strongest levels only
        strong_levels = sorted(levels, key=lambda x: x.strength, reverse=True)[:3]
        
        for level in strong_levels:
                
            # Bullish BOS - break above resistance with STRONG confirmation
            if (trend == TrendDirection.BULLISH and 
                level.type == "RESISTANCE" and
                latest_candle.close > level.price):
                
                # Must be a STRONG break (minimum 5 pips for forex)
                break_distance = latest_candle.close - level.price
                min_break = self.structure_analyzer.min_break_strength
                if 'JPY' in symbol:
                    min_break *= 100  # Adjust for JPY pairs
                
                if break_distance < min_break:
                    continue  # Not a strong enough break
                
                # Calculate confidence with stricter criteria
                confidence = self._calculate_bos_confidence(latest_candle, level, trend)
                if confidence >= self.min_confidence:
                    
                    # Add to cooldown BEFORE creating pattern to prevent spam
                    self._add_symbol_to_cooldown(symbol)
                    
                    pattern = BOSPattern(
                        symbol=symbol,
                        direction=TrendDirection.BULLISH,
                        break_level=level.price,
                        break_time=latest_candle.time,
                        retest_target=level.price,
                        confidence=confidence,
                        phase=PatternPhase.M5_BOS_DETECTED
                    )
                    
                    self.active_patterns[symbol] = pattern
                    logger.info(f"📈 VALID M5 BOS: {symbol} bullish @ {level.price} (confidence: {confidence:.1%})")
                    
                    # 📱 Send iMessage notification for Phase 1
                    notify_bos_detected(
                        symbol=symbol,
                        price=level.price,
                        confidence=confidence,
                        timeframe="M5"
                    )
                    
                    return pattern
                
            # Bearish BOS - break below support with STRONG confirmation  
            elif (trend == TrendDirection.BEARISH and
                  level.type == "SUPPORT" and
                  latest_candle.close < level.price):
                
                # Must be a STRONG break (minimum 5 pips for forex)
                break_distance = level.price - latest_candle.close
                min_break = self.structure_analyzer.min_break_strength
                if 'JPY' in symbol:
                    min_break *= 100  # Adjust for JPY pairs
                
                if break_distance < min_break:
                    continue  # Not a strong enough break
                
                # Calculate confidence with stricter criteria
                confidence = self._calculate_bos_confidence(latest_candle, level, trend)
                if confidence >= self.min_confidence:
                    
                    # Add to cooldown BEFORE creating pattern to prevent spam
                    self._add_symbol_to_cooldown(symbol)
                    
                    pattern = BOSPattern(
                        symbol=symbol,
                        direction=TrendDirection.BEARISH,
                        break_level=level.price,
                        break_time=latest_candle.time,
                        retest_target=level.price,
                        confidence=confidence,
                        phase=PatternPhase.M5_BOS_DETECTED
                    )
                    
                    self.active_patterns[symbol] = pattern
                    logger.info(f"📉 VALID M5 BOS: {symbol} bearish @ {level.price} (confidence: {confidence:.1%})")
                    
                    # 📱 Send iMessage notification for Phase 1 (Bearish)
                    notify_bos_detected(
                        symbol=symbol,
                        price=level.price,
                        confidence=confidence,
                        timeframe="M5"
                    )
                    
                    return pattern
        
        return None
    
    async def _confirm_m1_retest(self, symbol: str, m1_candles: List[Candle], bos_pattern: BOSPattern) -> bool:
        """Phase 2: Confirm M1 Break-and-Retest"""
        
        # Look for retest in recent M1 candles (after BOS time)
        retest_candles = [c for c in m1_candles if c.time > bos_pattern.break_time]
        
        if len(retest_candles) < 3:  # Need at least 3 M1 candles after BOS
            return False
        
        retest_tolerance = bos_pattern.break_level * 0.0005  # 0.05% tolerance
        
        for candle in retest_candles:
            
            # Bullish retest - price returns to test broken resistance (now support)
            if (bos_pattern.direction == TrendDirection.BULLISH and
                candle.low <= bos_pattern.break_level + retest_tolerance and
                candle.low >= bos_pattern.break_level - retest_tolerance and
                candle.close > bos_pattern.break_level):
                
                logger.info(f"✅ M1 RETEST CONFIRMED: {symbol} bullish retest @ {candle.low}")
                
                # 📱 Send iMessage notification for Phase 2 (Bullish Retest)
                notify_retest_confirmed(
                    symbol=symbol,
                    price=candle.close,
                    retest_level=bos_pattern.break_level,
                    confidence=bos_pattern.confidence
                )
                
                return True
            
            # Bearish retest - price returns to test broken support (now resistance)
            elif (bos_pattern.direction == TrendDirection.BEARISH and
                  candle.high >= bos_pattern.break_level - retest_tolerance and
                  candle.high <= bos_pattern.break_level + retest_tolerance and
                  candle.close < bos_pattern.break_level):
                
                logger.info(f"✅ M1 RETEST CONFIRMED: {symbol} bearish retest @ {candle.high}")
                
                # 📱 Send iMessage notification for Phase 2 (Bearish Retest)
                notify_retest_confirmed(
                    symbol=symbol,
                    price=candle.close,
                    retest_level=bos_pattern.break_level,
                    confidence=bos_pattern.confidence
                )
                
                return True
        
        return False
    
    async def _generate_entry_signal(self, symbol: str, bos_pattern: BOSPattern) -> Optional[LightningBoltSignal]:
        """Phase 3: Generate entry signal with ATR position sizing and 0.328 Fib stop loss"""
        
        # Get current tick
        current_tick = await self.mt5.get_current_tick(symbol)
        if not current_tick:
            return None
        
        # Import ATR position sizer
        from ..utils.atr_position_sizer import ATRPositionSizer
        
        # Initialize ATR sizer if not exists
        if not hasattr(self, 'atr_sizer'):
            self.atr_sizer = ATRPositionSizer(self.mt5)
        
        # Calculate entry price with Ylipip offset
        ylipip_offset = self.ylipip_calc.get_ylipip(symbol)
        
        if bos_pattern.direction == TrendDirection.BULLISH:
            entry_price = bos_pattern.retest_target + ylipip_offset
            
            # Check if current price allows entry
            if current_tick.ask <= entry_price + (ylipip_offset * 0.5):
                
                # Calculate ATR-based position sizing with 0.328 Fib stop
                position_info = await self.atr_sizer.calculate_position_size(
                    symbol=symbol,
                    entry_price=entry_price,
                    direction="BUY"
                )
                
                signal = LightningBoltSignal(
                    symbol=symbol,
                    direction=TrendDirection.BULLISH,
                    entry_price=entry_price,
                    stop_loss=position_info['stop_loss'],
                    take_profit=position_info['take_profit'],
                    ylipip_offset=ylipip_offset,
                    confidence=bos_pattern.confidence,
                    phase=PatternPhase.ENTRY_TRIGGERED,
                    timestamp=datetime.now()
                )
                
                # Add ATR info to signal
                signal.atr_info = position_info
                
                logger.info(f"⚡ BULLISH ATR Signal: {symbol} @ {entry_price}")
                logger.info(f"   📊 ATR Position Size: {position_info['position_size']} lots")
                logger.info(f"   🛡️ Fib 0.328 Stop: {position_info['stop_loss']}")
                
                # 📱 Send iMessage notification for Phase 3 (Bullish Entry)
                notify_entry_executed(
                    symbol=symbol,
                    entry_price=entry_price,
                    sl=position_info['stop_loss'],
                    tp=position_info['take_profit'],
                    volume=position_info['position_size']
                )
                
                return signal
        
        elif bos_pattern.direction == TrendDirection.BEARISH:
            entry_price = bos_pattern.retest_target - ylipip_offset
            
            # Check if current price allows entry
            if current_tick.bid >= entry_price - (ylipip_offset * 0.5):
                
                # Calculate ATR-based position sizing with 0.328 Fib stop
                position_info = await self.atr_sizer.calculate_position_size(
                    symbol=symbol,
                    entry_price=entry_price,
                    direction="SELL"
                )
                
                signal = LightningBoltSignal(
                    symbol=symbol,
                    direction=TrendDirection.BEARISH,
                    entry_price=entry_price,
                    stop_loss=position_info['stop_loss'],
                    take_profit=position_info['take_profit'],
                    ylipip_offset=ylipip_offset,
                    confidence=bos_pattern.confidence,
                    phase=PatternPhase.ENTRY_TRIGGERED,
                    timestamp=datetime.now()
                )
                
                # Add ATR info to signal
                signal.atr_info = position_info
                
                logger.info(f"⚡ BEARISH ATR Signal: {symbol} @ {entry_price}")
                logger.info(f"   📊 ATR Position Size: {position_info['position_size']} lots")
                logger.info(f"   🛡️ Fib 0.328 Stop: {position_info['stop_loss']}")
                
                # 📱 Send iMessage notification for Phase 3 (Bearish Entry)
                notify_entry_executed(
                    symbol=symbol,
                    entry_price=entry_price,
                    sl=position_info['stop_loss'],
                    tp=position_info['take_profit'],
                    volume=position_info['position_size']
                )
                
                return signal
        
        return None
    
    def _calculate_bos_confidence(self, candle: Candle, level: StructureLevel, trend: TrendDirection) -> float:
        """Calculate confidence score for BOS pattern - STRICTER SCORING"""
        confidence = 0.3  # Lower base confidence - must earn it!
        
        # Level strength is CRITICAL (must be tested multiple times)
        if level.strength < 3:
            return 0.0  # Reject weak levels immediately
        elif level.strength >= 7:
            confidence += 0.4  # Strong level
        elif level.strength >= 5:
            confidence += 0.25  # Medium level
        else:
            confidence += 0.1  # Weak level
        
        # Break strength must be significant
        if trend == TrendDirection.BULLISH:
            break_strength = (candle.close - level.price) / level.price
        else:
            break_strength = (level.price - candle.close) / level.price
        
        # Require stronger breaks for confidence
        if break_strength < 0.0003:  # Less than 3 pips
            return 0.0
        elif break_strength >= 0.001:  # 10+ pips
            confidence += 0.3
        elif break_strength >= 0.0005:  # 5+ pips
            confidence += 0.2
        else:
            confidence += 0.1
        
        # Candle must be decisive (strong body vs wick)
        candle_range = candle.high - candle.low
        if candle_range > 0:
            body_ratio = abs(candle.close - candle.open) / candle_range
            if body_ratio >= 0.7:  # Strong body
                confidence += 0.15
            elif body_ratio >= 0.5:  # Medium body
                confidence += 0.08
            else:
                confidence -= 0.05  # Weak body reduces confidence
        
        # Trend direction alignment
        if trend == TrendDirection.BULLISH and candle.close > candle.open:
            confidence += 0.05  # Bullish candle in bullish trend
        elif trend == TrendDirection.BEARISH and candle.close < candle.open:
            confidence += 0.05  # Bearish candle in bearish trend
        
        return min(confidence, 1.0)
    
    async def scan_all_symbols(self) -> List[LightningBoltSignal]:
        """Scan all active symbols for Lightning Bolt patterns"""
        signals = []
        
        for symbol in self.mt5.active_symbols:
            try:
                signal = await self.analyze_symbol(symbol)
                if signal:
                    signals.append(signal)
                    
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
        
        return signals
    
    def get_active_patterns(self) -> Dict[str, BOSPattern]:
        """Get currently active BOS patterns"""
        return self.active_patterns.copy()
    
    def clear_old_patterns(self, max_age_hours: int = 4):
        """Clear patterns older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for symbol, pattern in self.active_patterns.items():
            if pattern.break_time < cutoff_time:
                to_remove.append(symbol)
        
        for symbol in to_remove:
            del self.active_patterns[symbol]
            logger.info(f"🧹 Cleared old pattern for {symbol}")