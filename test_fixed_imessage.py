#!/usr/bin/env python3
"""
Test fixed iMessage system
"""

from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier

def test_feedback_message():
    """Test iMessage with feedback instructions"""
    
    message = """⚡ LIGHTNING BOLT - PHASE 1

🔍 ML/MCP DETECTED:
📈 EURUSD - BULLISH BOS
💰 Price: 1.0856
📊 Timeframe: M5
🎯 Confidence: 85.0%

👀 CHECK EURUSD CHART NOW!
⚡ M5 Break of Structure confirmed
🔄 Watch for M1 retest...

🔥 ML Trust: HIGH
📱 Reply: Pass EURUSD or Fail EURUSD

🕐 12:33:45"""
    
    print("📱 Testing feedback-enabled iMessage...")
    success = imessage_notifier.send_imessage(message)
    
    if success:
        print("✅ Fixed iMessage sent successfully!")
        print("📱 Check your phone for the alert")
        print("💡 You can now reply with 'Pass EURUSD' or 'Fail EURUSD'")
    else:
        print("❌ iMessage failed")
    
    return success

if __name__ == "__main__":
    test_feedback_message()