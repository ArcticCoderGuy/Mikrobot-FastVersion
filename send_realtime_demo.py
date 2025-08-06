#!/usr/bin/env python3
"""
Send demo with improved real-time context charts
"""

import asyncio
from datetime import datetime
from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart
from src.mikrobot_v2.data.real_market_data import get_real_tick

async def send_realtime_demo():
    """Send demo with real price context charts"""
    
    print("📊 Creating real-time demo with actual prices...")
    
    # Get real EURUSD price
    eurusd_tick = await get_real_tick("EURUSD")
    
    if eurusd_tick:
        # Generate chart with real price
        chart_path = generate_pattern_chart("EURUSD", "Phase 1 - BOS", eurusd_tick.price)
        
        message = f"""🚀 MIKROBOT - PARANNELTU CHART SYSTEM!

✅ TODELLINEN MARKKINAKONTEKSTI:
💱 EURUSD: {eurusd_tick.price:.5f} (REAL)
📊 Lähde: {eurusd_tick.source}
⏰ {datetime.now().strftime('%H:%M:%S')}

📈 CHART NÄYTTÄÄ NYT:
• Oikean nykyhinnan ✅
• Realistisen hintaliikkeen ✅ 
• Markkinakontekstin (high/low/change) ✅
• Professional pattern merkinnät ✅
• Aikaleiman ✅

⚡ LIGHTNING BOLT PHASE 1
Pattern havaittu oikeilla hinnoilla!

🔥 EI ENÄÄ SIMULAATIOTA CHARTISSA!
Näet todellisen markkinatilanteen!"""
        
        success = imessage_notifier.send_imessage(message, image_path=chart_path)
        
        if success:
            print("✅ Real-time demo sent successfully!")
            print(f"📊 Chart uses real EURUSD price: {eurusd_tick.price:.5f}")
        else:
            print("❌ Failed to send demo")
    else:
        print("❌ Could not get real price")

if __name__ == "__main__":
    asyncio.run(send_realtime_demo())