"""
Real-time iMessage Notifier with Real Market Data Charts
========================================================

Sends Lightning Bolt notifications with real-time price charts
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from .imessage_notifier import LightningBoltPhase, iMessageNotifier

logger = logging.getLogger(__name__)

class RealTimeMessageNotifier(iMessageNotifier):
    """
    Enhanced iMessage notifier with real-time charts
    """
    
    def __init__(self, phone_number: Optional[str] = None):
        super().__init__(phone_number)
        logger.info("📊 Real-Time iMessage Notifier initialized")
    
    async def notify_lightning_bolt_phase_realtime(self, phase_data: LightningBoltPhase) -> bool:
        """
        Send Lightning Bolt phase notification with REAL-TIME chart
        """
        emoji = self.phase_emojis.get(phase_data.phase, "⚡")
        symbol = phase_data.symbol
        phase_name = phase_data.phase_name
        price = phase_data.price
        confidence = phase_data.confidence
        timeframe = phase_data.timeframe
        
        # Generate REAL-TIME chart image
        chart_path = None
        try:
            from ..charts.realtime_chart_generator import generate_realtime_pattern_chart
            phase_name_clean = f"Phase {phase_data.phase} - {phase_name}"
            chart_path = await generate_realtime_pattern_chart(symbol, phase_name_clean, price)
            
            if chart_path:
                logger.info(f"📊 Real-time chart generated: {chart_path}")
        except Exception as e:
            logger.warning(f"Real-time chart generation failed: {e}")
        
        # Determine trend direction
        trend = "NEUTRAL"
        if phase_data.details:
            trend = phase_data.details.get('trend_direction', 'NEUTRAL')
        trend_emoji = self.trend_emojis.get(trend, "➡️")
        
        # Phase-specific messages with real-time info
        if phase_data.phase == 1:
            # Phase 1: BOS (Break of Structure)
            message = f"""🔥 MIKROBOT LIGHTNING BOLT ⚡

PHASE 1: BREAK OF STRUCTURE (REAL)
{emoji} {symbol} @ {price}
{trend_emoji} {trend} BOS detected
📊 {timeframe} | Confidence: {confidence:.1%}
🕐 {datetime.now().strftime('%H:%M:%S')}

📈 REAL-TIME CHART MUKANA!
ML/MCP: BOS vahvistettu oikeilla hinnoilla!
Seurataan Phase 2 Retest..."""

        elif phase_data.phase == 2:
            # Phase 2: Retest
            retest_level = phase_data.details.get('retest_level', price) if phase_data.details else price
            message = f"""🔥 MIKROBOT LIGHTNING BOLT ⚡

PHASE 2: RETEST CONFIRMATION (REAL)
{emoji} {symbol} @ {price}
🎯 Retest level: {retest_level}
{trend_emoji} {trend} retest valid
📊 M1 | Confidence: {confidence:.1%}
🕐 {datetime.now().strftime('%H:%M:%S')}

📈 REAL-TIME LIIKKEET CHARTISSA!
ML/MCP: Retest onnistunut oikeilla hinnoilla!
Valmiina Phase 3 entryyn... 🚀"""

        elif phase_data.phase == 3:
            # Phase 3: Entry (+0.6 Ylipip)
            entry_price = phase_data.details.get('entry_price', price) if phase_data.details else price
            sl_price = phase_data.details.get('stop_loss', 0) if phase_data.details else 0
            tp_price = phase_data.details.get('take_profit', 0) if phase_data.details else 0
            
            message = f"""🚀 MIKROBOT LIGHTNING BOLT ENTRY!

PHASE 3: +0.6 YLIPIP ENTRY (REAL)
{emoji} {symbol} {trend} 
💰 Entry: {entry_price}
🛡️ SL: {sl_price}
🎯 TP: {tp_price}
🕐 {datetime.now().strftime('%H:%M:%S')}

📈 REAL-TIME CHART - NÄET LIIKKEET!
🔥 OIKEILLA MARKKINAHINNOILLA!
Lightning Bolt Complete ⚡"""

        else:
            # Generic phase message
            message = f"""⚡ MIKROBOT LIGHTNING BOLT (REAL)

PHASE {phase_data.phase}: {phase_name}
{symbol} @ {price}
Confidence: {confidence:.1%}
{datetime.now().strftime('%H:%M:%S')}

📈 Real-time chart mukana!"""
        
        # Send with real-time chart
        return self.send_imessage(message, image_path=chart_path)

# Global real-time notifier
realtime_notifier = RealTimeMessageNotifier()

# Convenience functions with real-time charts
async def notify_bos_detected_realtime(symbol: str, price: float, confidence: float, timeframe: str = "M5"):
    """Quick BOS notification with real-time chart"""
    phase = LightningBoltPhase(
        symbol=symbol,
        phase=1,
        phase_name="BOS_DETECTION",
        timeframe=timeframe,
        price=price,
        confidence=confidence,
        timestamp=datetime.now(),
        details={'trend_direction': 'BULLISH'}
    )
    return await realtime_notifier.notify_lightning_bolt_phase_realtime(phase)

async def notify_retest_confirmed_realtime(symbol: str, price: float, retest_level: float, confidence: float):
    """Quick Retest notification with real-time chart"""
    phase = LightningBoltPhase(
        symbol=symbol,
        phase=2,
        phase_name="RETEST_CONFIRMATION",
        timeframe="M1",
        price=price,
        confidence=confidence,
        timestamp=datetime.now(),
        details={'retest_level': retest_level, 'trend_direction': 'BULLISH'}
    )
    return await realtime_notifier.notify_lightning_bolt_phase_realtime(phase)

async def notify_entry_executed_realtime(symbol: str, entry_price: float, sl: float, tp: float):
    """Quick Entry notification with real-time chart"""
    phase = LightningBoltPhase(
        symbol=symbol,
        phase=3,
        phase_name="YLIPIP_ENTRY",
        timeframe="M1",
        price=entry_price,
        confidence=0.92,
        timestamp=datetime.now(),
        details={
            'entry_price': entry_price,
            'stop_loss': sl,
            'take_profit': tp,
            'trend_direction': 'BULLISH'
        }
    )
    return await realtime_notifier.notify_lightning_bolt_phase_realtime(phase)