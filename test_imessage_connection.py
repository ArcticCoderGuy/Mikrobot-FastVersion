#!/usr/bin/env python3
"""
Test iMessage connection and AppleScript
"""

import subprocess
from datetime import datetime
from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier

def test_imessage_connection():
    """Test iMessage connection"""
    
    print("📱 TESTING iMESSAGE CONNECTION")
    print("=" * 40)
    print(f"📞 Your number: {imessage_notifier.phone_number}")
    
    # Test 1: Simple AppleScript
    print("\n🧪 Test 1: Simple AppleScript test...")
    
    try:
        applescript = '''
        tell application "Messages"
            return "AppleScript OK"
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ AppleScript works!")
        else:
            print(f"❌ AppleScript error: {result.stderr}")
            
    except Exception as e:
        print(f"❌ AppleScript exception: {e}")
    
    # Test 2: Check Messages app
    print("\n🧪 Test 2: Check Messages app...")
    
    try:
        applescript = '''
        tell application "System Events"
            return (exists process "Messages")
        end tell
        '''
        
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            is_running = result.stdout.strip()
            print(f"📱 Messages app running: {is_running}")
            
            if is_running == "false":
                print("⚠️ Messages app ei ole käynnissä - käynnistä se!")
        
    except Exception as e:
        print(f"❌ Error checking Messages: {e}")
    
    # Test 3: Send test message
    print("\n🧪 Test 3: Sending test message...")
    
    test_message = f"""🔧 MIKROBOT iMESSAGE TEST

✅ Connection test 
📱 Number: +358440606044
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

Jos saat tämän, iMessage toimii! 📱"""
    
    success = imessage_notifier.send_imessage(test_message)
    
    if success:
        print("✅ Test message sent!")
        print("📱 Check your phone for the message")
    else:
        print("❌ Test message failed")
    
    print("\n" + "=" * 40)
    print("TROUBLESHOOTING:")
    print("1. Varmista että Messages app on käynnissä")
    print("2. Tarkista että iMessage on käytössä")
    print("3. Varmista että numero +358440606044 on oikein")
    print("4. Tarkista että koneesi on kirjautunut iMessage:een")

if __name__ == "__main__":
    test_imessage_connection()