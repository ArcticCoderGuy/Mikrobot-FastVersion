#!/usr/bin/env python3
"""
Test improved chart with real price context
"""

import asyncio
from datetime import datetime
from src.mikrobot_v2.notifications.imessage_notifier import notify_bos_detected
from src.mikrobot_v2.data.real_market_data import get_real_tick

async def test_improved_chart():
    """Test improved chart with real market context"""
    
    print("📊 TESTING IMPROVED CHART WITH REAL CONTEXT")
    print("=" * 50)
    
    # Get real EURUSD price first
    print("💱 Getting real EURUSD price...")
    eurusd_tick = await get_real_tick("EURUSD")
    
    if eurusd_tick:
        print(f"✅ Real EURUSD: {eurusd_tick.price:.5f} from {eurusd_tick.source}")
        
        # Send notification with real price
        print("📱 Sending Lightning Bolt notification with real price context...")
        
        success = notify_bos_detected(
            symbol="EURUSD",
            price=eurusd_tick.price,  # Use REAL current price
            confidence=0.89,
            timeframe="M5"
        )
        
        if success:
            print("✅ Improved chart + iMessage sent!")
            print("📊 Chart now shows:")
            print(f"   • Real current price: {eurusd_tick.price:.5f}")
            print("   • Realistic price movement context")
            print("   • Market high/low/change info")
            print("   • Professional pattern annotation")
            print("   • Current timestamp")
        else:
            print("❌ Failed to send notification")
    
    else:
        print("❌ Could not get real EURUSD price")
    
    # Also test with crypto
    print("\n🪙 Testing with real BTCUSD...")
    btc_tick = await get_real_tick("BTCUSD")
    
    if btc_tick:
        print(f"✅ Real BTCUSD: ${btc_tick.price:,.2f} from {btc_tick.source}")
        
        success2 = notify_bos_detected(
            symbol="BTCUSD", 
            price=btc_tick.price,
            confidence=0.91,
            timeframe="M5"
        )
        
        if success2:
            print("✅ BTC chart + iMessage sent!")

if __name__ == "__main__":
    asyncio.run(test_improved_chart())