#!/usr/bin/env python3
"""
Debug chart sending in Lightning Bolt notifications
"""

import asyncio
import os
from datetime import datetime
from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart

async def debug_chart_sending():
    """Debug why charts aren't being sent"""
    
    print("🔍 DEBUGGING CHART SENDING")
    print("=" * 40)
    
    # Step 1: Generate chart manually
    print("📊 Step 1: Generating chart manually...")
    chart_path = generate_pattern_chart("EURUSD", "Phase 1", 1.16318)
    
    if chart_path:
        print(f"✅ Chart generated: {chart_path}")
        print(f"📁 File exists: {os.path.exists(chart_path)}")
        print(f"📏 File size: {os.path.getsize(chart_path)} bytes")
        
        # Step 2: Send with manual call
        print("\n📱 Step 2: Sending with manual iMessage call...")
        
        message = f"""🔍 MANUAL CHART TEST

📊 Chart should be attached
📱 Testing image sending
🕐 {datetime.now().strftime('%H:%M:%S')}

Debug test - chart manually generated"""
        
        success = imessage_notifier.send_imessage(message, image_path=chart_path)
        print(f"📱 Manual send result: {success}")
        
        # Step 3: Check what happens in notify_lightning_bolt_phase
        print("\n⚡ Step 3: Testing notify_lightning_bolt_phase...")
        
        from src.mikrobot_v2.notifications.imessage_notifier import LightningBoltPhase
        
        phase_data = LightningBoltPhase(
            symbol="EURUSD",
            phase=1,
            phase_name="BOS_DETECTION", 
            timeframe="M5",
            price=1.16318,
            confidence=0.89,
            timestamp=datetime.now(),
            details={'trend_direction': 'BULLISH'}
        )
        
        # Call the actual notification method
        success2 = imessage_notifier.notify_lightning_bolt_phase(phase_data)
        print(f"⚡ Lightning Bolt notification result: {success2}")
        
    else:
        print("❌ Failed to generate chart")

if __name__ == "__main__":
    asyncio.run(debug_chart_sending())