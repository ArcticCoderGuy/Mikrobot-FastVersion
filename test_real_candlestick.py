#!/usr/bin/env python3
"""
Test real candlestick chart generation
"""

import asyncio
from src.mikrobot_v2.charts.real_candlestick_chart import generate_real_candlestick_chart
from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier

async def test_real_candlestick():
    """Test real candlestick chart generation"""
    
    print("📊 TESTING REAL CANDLESTICK CHART")
    print("🕯️ OIKEAT KYNTTILÄT + MARKET STRUCTURE")
    print("=" * 50)
    
    # Generate real candlestick chart for EURUSD
    print("💱 Generating real EURUSD candlestick chart...")
    chart_path = await generate_real_candlestick_chart("EURUSD", "Phase 1 - BOS")
    
    if chart_path:
        print(f"✅ Real candlestick chart generated: {chart_path}")
        
        # Send iMessage with real candlestick chart
        message = f"""🔥 MIKROBOT - OIKEAT KYNTTILÄT! 🕯️

✅ TODELLINEN CANDLESTICK CHART:
💱 EURUSD - Alpha Vantage data
📊 50 oikeaa kynttilää (5min)
🎯 Market Structure (HH/HL/LH/LL)
⚡ BOS detection merkintä

🕯️ CHART NÄYTTÄÄ:
• Oikeat vihreät/punaiset kynttilät ✅
• Market structure ympyrät ✅
• Volume data ✅
• Professional trading platform tyyli ✅

🔥 EI ENÄÄ SIMULAATIOTA!
Sama kuin oikeat trading chartit! 

⚡ Lightning Bolt Phase 1 havaittu!"""
        
        success = imessage_notifier.send_imessage(message, image_path=chart_path)
        
        if success:
            print("✅ Real candlestick chart sent via iMessage!")
            print("📊 Chart shows:")
            print("   • Real OHLC candlesticks")
            print("   • Market structure points (HH, HL, LH, LL)")
            print("   • BOS detection arrow")
            print("   • Volume analysis")
            print("   • Professional trading platform appearance")
        else:
            print("❌ Failed to send iMessage")
    
    else:
        print("❌ Failed to generate real candlestick chart")

if __name__ == "__main__":
    asyncio.run(test_real_candlestick())