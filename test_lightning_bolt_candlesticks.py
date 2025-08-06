#!/usr/bin/env python3
"""
Test Lightning Bolt notification with professional candlesticks
"""

import asyncio
from src.mikrobot_v2.notifications.imessage_notifier import notify_bos_detected
from src.mikrobot_v2.data.real_market_data import get_real_tick

async def test_lightning_bolt_candlesticks():
    """Test Lightning Bolt with professional candlestick charts"""
    
    print("⚡ TESTING LIGHTNING BOLT + CANDLESTICK CHARTS")
    print("=" * 50)
    
    # Get real EURUSD price
    print("💱 Getting real EURUSD price...")
    eurusd_tick = await get_real_tick("EURUSD")
    
    if eurusd_tick:
        print(f"✅ Real EURUSD: {eurusd_tick.price:.5f}")
        
        # Send Lightning Bolt notification with professional candlestick chart
        print("⚡ Sending Lightning Bolt BOS detection with candlestick chart...")
        
        success = notify_bos_detected(
            symbol="EURUSD",
            price=eurusd_tick.price,
            confidence=0.92,
            timeframe="M5"
        )
        
        if success:
            print("✅ Lightning Bolt + candlestick chart sent!")
            print("📊 Message includes:")
            print("   • Lightning Bolt Phase 1 text")
            print("   • Professional candlestick chart")  
            print("   • Market structure (HH/HL/LH/LL)")
            print("   • BOS detection arrow")
            print("   • Real current price endpoint")
            print("   • Volume analysis")
            print("")
            print("🕯️ Chart should look like real trading platform!")
        else:
            print("❌ Failed to send Lightning Bolt notification")
    
    else:
        print("❌ Could not get real EURUSD price")

if __name__ == "__main__":
    asyncio.run(test_lightning_bolt_candlesticks())