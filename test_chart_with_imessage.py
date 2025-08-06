#!/usr/bin/env python3
"""
Test chart generation and iMessage with image
"""

import asyncio
from datetime import datetime
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart
from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier

async def test_chart_message():
    """Test chart generation and iMessage delivery"""
    
    print("📊 TESTING CHART GENERATION + iMESSAGE")
    print("=" * 40)
    
    # Generate test chart
    print("📊 Generating chart...")
    chart_path = generate_pattern_chart("EURUSD", "Phase 1 - BOS", 1.16318)
    
    if chart_path:
        print(f"✅ Chart generated: {chart_path}")
        
        # Send iMessage with chart
        print("📱 Sending iMessage with chart...")
        
        message = f"""🔥 MIKROBOT CHART TEST ⚡

📊 EURUSD Phase 1 Detection
💰 Price: 1.16318
⚡ BOS Pattern Detected
🕐 {datetime.now().strftime('%H:%M:%S')}

📈 Chart mukana - näet pattern!
🎯 Confidence: 85%

Testaa "Pass EURUSD" tai "Fail EURUSD" """
        
        success = imessage_notifier.send_imessage(message, image_path=chart_path)
        
        if success:
            print("✅ iMessage + chart sent successfully!")
            print(f"📊 Chart saved at: {chart_path}")
        else:
            print("❌ Failed to send iMessage")
    
    else:
        print("❌ Chart generation failed")

if __name__ == "__main__":
    asyncio.run(test_chart_message())