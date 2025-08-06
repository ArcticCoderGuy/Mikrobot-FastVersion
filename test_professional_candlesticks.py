#!/usr/bin/env python3
"""
Test professional candlestick chart generation
"""

import asyncio
from src.mikrobot_v2.charts.realistic_candlestick_chart import generate_professional_candlestick_chart
from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier

async def test_professional_candlesticks():
    """Test professional candlestick chart"""
    
    print("🕯️ TESTING PROFESSIONAL CANDLESTICK CHART")
    print("📊 KUTEN OIKEASSA TRADING PLATFORMISSA")
    print("=" * 50)
    
    # Generate professional candlestick chart for EURUSD
    print("💱 Creating professional EURUSD chart...")
    chart_path = await generate_professional_candlestick_chart(
        symbol="EURUSD", 
        pattern_phase="Phase 1 - BOS", 
        current_price=1.16368
    )
    
    if chart_path:
        print(f"✅ Professional candlestick chart created: {chart_path}")
        
        # Send the REAL candlestick chart via iMessage
        message = f"""🔥 MIKROBOT - OIKEAT CANDLESTICKIT! 🕯️

✅ PROFESSIONAL TRADING CHART:
💱 EURUSD @ 1.16368 (REAL PRICE)
🕯️ 50 realistista 5min kynttilää
🎯 Market Structure: HH/HL/LH/LL
⚡ BOS Break of Structure

📊 CHART ON KUIN OIKEASSA TRADING PLATFORMISSA:
• Vihreät/punaiset candlestickit ✅
• Market structure ympyrät (kuten kuvassa) ✅  
• Professional dark theme ✅
• Volume analysis ✅
• BOS detection nuoli ✅

🔥 TÄYSIN KUTEN TRADINGVIEW!
Sama look & feel kuin oikeissa trading charteissa!

⚡ Lightning Bolt Pattern havaittu!
Tossa BOS jonka merkannut charttiin joskus, voidaan käydä tämä !-vitse"""
        
        success = imessage_notifier.send_imessage(message, image_path=chart_path)
        
        if success:
            print("✅ Professional candlestick chart sent!")
            print("🕯️ Chart features:")
            print("   • Real current price as endpoint")
            print("   • Realistic candlestick movements")
            print("   • Market structure points with circles")
            print("   • Professional TradingView-style colors")
            print("   • BOS detection arrow")
            print("   • Volume bars")
            print("   • Grid and professional formatting")
        else:
            print("❌ Failed to send iMessage")
    
    else:
        print("❌ Failed to generate professional candlestick chart")

if __name__ == "__main__":
    asyncio.run(test_professional_candlesticks())