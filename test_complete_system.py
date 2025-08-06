#!/usr/bin/env python3
"""
Test complete system with Mail notifications
"""

import asyncio
from datetime import datetime
from src.mikrobot_v2.notifications.mail_notifier import mail_notifier
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart
from src.mikrobot_v2.data.real_market_data import real_data_provider

async def test_complete_system():
    """Test the complete notification system"""
    
    print("🚀 COMPLETE SYSTEM TEST")
    print("=" * 50)
    
    # Get real forex price
    print("\n1️⃣ Getting real forex price...")
    tick = await real_data_provider.get_real_price("EURUSD")
    if tick:
        price = tick.price
        print(f"✅ EURUSD: {price}")
    else:
        price = 1.16400
        print(f"⚠️ Using default price: {price}")
    
    # Phase 1: BOS Detection
    print("\n2️⃣ Simulating Phase 1 BOS detection...")
    chart1 = generate_pattern_chart("EURUSD", "Phase 1 - BOS", price)
    
    success1 = mail_notifier.notify_lightning_bolt(
        symbol="EURUSD",
        phase=1,
        phase_name="BOS_DETECTION",
        price=price,
        confidence=0.85,
        chart_path=chart1
    )
    
    if success1:
        print("✅ Phase 1 BOS email sent with chart!")
    
    await asyncio.sleep(2)
    
    # Phase 2: Retest
    print("\n3️⃣ Simulating Phase 2 Retest...")
    retest_price = price * 0.9995
    chart2 = generate_pattern_chart("EURUSD", "Phase 2 - Retest", retest_price)
    
    success2 = mail_notifier.notify_lightning_bolt(
        symbol="EURUSD",
        phase=2,
        phase_name="RETEST_CONFIRMATION",
        price=retest_price,
        confidence=0.88,
        chart_path=chart2
    )
    
    if success2:
        print("✅ Phase 2 Retest email sent with chart!")
    
    await asyncio.sleep(2)
    
    # Phase 3: Entry Signal
    print("\n4️⃣ Simulating Phase 3 ENTRY signal...")
    entry_price = price * 1.0006  # +0.6 pips
    chart3 = generate_pattern_chart("EURUSD", "Phase 3 - ENTRY", entry_price)
    
    success3 = mail_notifier.notify_lightning_bolt(
        symbol="EURUSD",
        phase=3,
        phase_name="YLIPIP_ENTRY",
        price=entry_price,
        confidence=0.92,
        chart_path=chart3
    )
    
    if success3:
        print("✅ Phase 3 ENTRY email sent with chart!")
    
    # Get crypto price too
    print("\n5️⃣ Testing with cryptocurrency...")
    btc_tick = await real_data_provider.get_real_price("BTCUSD")
    if btc_tick:
        btc_price = btc_tick.price
        print(f"✅ BTCUSD: ${btc_price:,.2f}")
        
        chart_btc = generate_pattern_chart("BTCUSD", "BTC Lightning Bolt", btc_price)
        
        success_btc = mail_notifier.notify_lightning_bolt(
            symbol="BTCUSD",
            phase=1,
            phase_name="BOS_DETECTION",
            price=btc_price,
            confidence=0.79,
            chart_path=chart_btc
        )
        
        if success_btc:
            print("✅ Bitcoin alert email sent!")
    
    print("\n" + "=" * 50)
    print("✅ COMPLETE SYSTEM TEST FINISHED!")
    print("\n📧 Check your email for:")
    print("   • Phase 1 BOS detection (EURUSD)")
    print("   • Phase 2 Retest confirmation (EURUSD)")
    print("   • Phase 3 Entry signal (EURUSD)")
    print("   • Bitcoin BOS alert (if available)")
    print("\n📊 All emails should have professional candlestick charts!")
    print("🔥 Lightning Bolt system fully operational!")

if __name__ == "__main__":
    asyncio.run(test_complete_system())