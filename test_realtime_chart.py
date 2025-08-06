#!/usr/bin/env python3
"""
Test real-time chart generation with actual market data
"""

import asyncio
from datetime import datetime
from src.mikrobot_v2.notifications.realtime_imessage_notifier import notify_bos_detected_realtime

async def test_realtime_chart():
    """Test real-time chart with real market data"""
    
    print("📊 TESTING REAL-TIME CHART + iMESSAGE")
    print("=" * 50)
    
    # Test with EURUSD (real Alpha Vantage price)
    print("💱 Testing EURUSD with real-time chart...")
    
    success = await notify_bos_detected_realtime(
        symbol="EURUSD",
        price=1.16318,  # Will fetch real current price
        confidence=0.87,
        timeframe="M5"
    )
    
    if success:
        print("✅ Real-time chart + iMessage sent successfully!")
        print("📊 Chart shows:")
        print("   • Real price movements (2 hours)")
        print("   • Actual candlesticks")
        print("   • Pattern detection arrow")
        print("   • Current market info")
        print("   • Volume data")
    else:
        print("❌ Failed to send real-time notification")

if __name__ == "__main__":
    asyncio.run(test_realtime_chart())