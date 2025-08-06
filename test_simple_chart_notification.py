#!/usr/bin/env python3
"""
Simple test: Lightning Bolt notification with chart
"""

import asyncio
from datetime import datetime
from src.mikrobot_v2.notifications.imessage_notifier import notify_bos_detected

async def test_simple_notification():
    """Simple Lightning Bolt test with chart"""
    
    print("⚡ SIMPLE LIGHTNING BOLT + CHART TEST")
    print("=" * 40)
    
    # Send Lightning Bolt notification - should include chart
    print("📱 Sending Lightning Bolt BOS notification...")
    
    success = notify_bos_detected(
        symbol="EURUSD",
        price=1.16318,
        confidence=0.91,
        timeframe="M5"  
    )
    
    if success:
        print("✅ Lightning Bolt notification sent!")
        print("📊 Should include:")
        print("   • Phase 1 BOS message")
        print("   • Professional candlestick chart")
        print("   • Market structure")
        print("   • BOS detection arrow")
        
        print("\n📱 Tarkista puhelimestasi:")
        print("1. Tuleeko teksti?")
        print("2. Tuleeko kuva?")
        print("3. Jos ei kuvaa - kuvat saattavat olla iCloud:ssa")
        
    else:
        print("❌ Lightning Bolt notification failed")

if __name__ == "__main__":
    asyncio.run(test_simple_notification())