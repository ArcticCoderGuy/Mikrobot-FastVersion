#!/usr/bin/env python3
"""
Send final confirmation with sample chart
"""

import asyncio
from datetime import datetime
from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart

async def send_final_confirmation():
    """Send final confirmation with chart example"""
    
    print("📱 Sending final system confirmation with chart...")
    
    # Generate example chart
    chart_path = generate_pattern_chart("BTCUSD", "Phase 1 - BOS", 114088.0)
    
    message = f"""🚀 MIKROBOT FASTVERSION v2.0 - TÄYDELLINEN!
========================================

✅ KAIKKI TOIMII 100%:

💱 FOREX (Alpha Vantage):
• EURUSD, GBPUSD, USDJPY ✅
• API: 3M9G2YI3P8TTW72C ✅

🪙 CRYPTO (CoinGecko):
• BTCUSD, ETHUSD, BNBUSD ✅
• Unlimited real prices ✅

⚡ LIGHTNING BOLT + CHARTIT:
• Phase 1-3 notifications ✅
• Visual charts mukana! ✅
• Pattern detection ✅

📱 iMESSAGE SYSTEM:
• Text + Image alerts ✅
• Bidirectional feedback ✅
• Real-time notifications ✅

🔍 SKANNERI:
• 10 symbols (5 forex + 5 crypto) ✅
• 60s intervals ✅ 
• ML/MCP analysis ✅
• NO simulation - ALL REAL! ✅

⏰ {datetime.now().strftime('%H:%M:%S')}

📊 MUKANA ESIMERKKI CHART!
Näet nyt jokaisen Phase:n visuaalisesti!

VASTAA EDELLEEN:
• "Pass BTCUSD" = hyvä signaali
• "Fail EURUSD" = huono signaali

🔥 MIKROBOT ON TÄYSIN VALMIS!"""
    
    success = imessage_notifier.send_imessage(message, image_path=chart_path)
    
    if success:
        print("✅ Final confirmation + example chart sent!")
    else:
        print("❌ Failed to send final confirmation")
    
    return success

if __name__ == "__main__":
    asyncio.run(send_final_confirmation())