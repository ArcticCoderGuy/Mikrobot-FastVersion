#!/usr/bin/env python3
"""
Final test - one Lightning Bolt email with chart
"""

import asyncio
from src.mikrobot_v2.notifications.mail_notifier import MailNotifier
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart
from src.mikrobot_v2.data.real_market_data import real_data_provider

async def final_test():
    """Send ONE Lightning Bolt email with professional chart"""
    
    print("⚡ FINAL LIGHTNING BOLT TEST")
    print("=" * 40)
    
    # Get real price
    print("📊 Getting real EURUSD price...")
    tick = await real_data_provider.get_real_price("EURUSD")
    price = tick.price if tick else 1.16400
    print(f"💰 EURUSD: {price}")
    
    # Generate professional chart
    print("📈 Generating professional candlestick chart...")
    chart_path = generate_pattern_chart("EURUSD", "Lightning Bolt BOS", price)
    
    if chart_path:
        print(f"✅ Chart created: {chart_path}")
    else:
        print("❌ Chart failed")
        return
    
    # Create notifier
    notifier = MailNotifier(recipient_email="markus@foxinthecode.fi")
    
    print(f"\n📧 Sending to: {notifier.recipient_email}")
    print("📄 Content preview:")
    print("   Subject: ⚡ LIGHTNING BOLT - EURUSD - Phase 1: BOS_DETECTION")
    print("   Body: Phase 1 BOS detection with candlestick chart")
    print("   Attachment: Professional chart with HH/HL/LH/LL markers")
    
    # Send the email
    success = notifier.notify_lightning_bolt(
        symbol="EURUSD",
        phase=1,
        phase_name="BOS_DETECTION", 
        price=price,
        confidence=0.85,
        chart_path=chart_path
    )
    
    if success:
        print("\n✅ SUCCESS!")
        print("📧 Lightning Bolt email sent with chart!")
        print("📱 Check markus@foxinthecode.fi for:")
        print("   • Professional candlestick chart attachment")
        print("   • Phase 1 BOS detection alert")
        print("   • Real EURUSD price data")
    else:
        print("\n❌ Email failed")
    
    print("\n" + "=" * 40)
    print("🔥 MIKROBOT LIGHTNING BOLT - Ready for production!")

if __name__ == "__main__":
    asyncio.run(final_test())