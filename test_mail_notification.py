#!/usr/bin/env python3
"""
Test Mail notification with chart
"""

import os
from src.mikrobot_v2.notifications.mail_notifier import mail_notifier
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart

def test_mail():
    """Test email notification with chart"""
    
    print("📧 MAIL NOTIFICATION TEST")
    print("=" * 40)
    
    # First send test without chart
    print("\n1️⃣ Testing text-only email...")
    if mail_notifier.test_notification():
        print("✅ Test email sent!")
    else:
        print("❌ Test email failed")
    
    # Generate chart
    print("\n2️⃣ Generating chart for email...")
    chart_path = generate_pattern_chart("EURUSD", "MAIL TEST", 1.16400)
    
    if chart_path and os.path.exists(chart_path):
        print(f"✅ Chart generated: {chart_path}")
        print(f"📏 Size: {os.path.getsize(chart_path)} bytes")
        
        # Send Phase 1 notification with chart
        print("\n3️⃣ Sending Phase 1 BOS notification with chart...")
        if mail_notifier.notify_lightning_bolt(
            symbol="EURUSD",
            phase=1,
            phase_name="BOS_DETECTION",
            price=1.16400,
            confidence=0.85,
            chart_path=chart_path
        ):
            print("✅ Phase 1 email with chart sent!")
        else:
            print("❌ Phase 1 email failed")
        
        # Send Phase 3 Entry notification
        print("\n4️⃣ Sending Phase 3 ENTRY notification with chart...")
        if mail_notifier.notify_lightning_bolt(
            symbol="EURUSD", 
            phase=3,
            phase_name="YLIPIP_ENTRY",
            price=1.16450,
            confidence=0.92,
            chart_path=chart_path
        ):
            print("✅ Phase 3 ENTRY email sent!")
        else:
            print("❌ Phase 3 email failed")
    else:
        print("❌ Chart generation failed")
    
    print("\n" + "=" * 40)
    print("📧 Check your email for:")
    print("   1. Test message")
    print("   2. Phase 1 BOS alert with chart")
    print("   3. Phase 3 ENTRY signal with chart")
    print("\n📱 Charts should appear as proper attachments!")

if __name__ == "__main__":
    test_mail()