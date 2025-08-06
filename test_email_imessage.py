#!/usr/bin/env python3
"""
Test iMessage with email address instead of phone number
"""

import subprocess
from datetime import datetime

def test_email_imessage():
    """Test sending to email instead of phone"""
    
    print("📧 TESTING iMESSAGE WITH EMAIL")
    print("=" * 40)
    
    # You can try different email formats
    email_addresses = [
        "markus@example.com",  # Replace with your Apple ID email
        "your_apple_id@icloud.com",  # Replace with your actual email
    ]
    
    print("⚠️ HUOM: Korvaa email osoitteet oikeilla!")
    print("Anna Apple ID email osoitteesi:")
    
    # Let user input their email
    try:
        user_email = input("📧 Anna Apple ID email: ").strip()
        if user_email:
            email_addresses = [user_email]
    except:
        print("Using default test emails...")
    
    for email in email_addresses:
        print(f"\n📧 Testing email: {email}")
        
        try:
            test_message = f"""📧 EMAIL iMESSAGE TEST

✅ Lähetetty email:iin sen sijaan että numeroon
📱 Jos saat tämän, email iMessage toimii!
🕐 {datetime.now().strftime('%H:%M:%S')}

🔧 Kokeile lisätä +358440606044 Contacts:iin"""
            
            safe_message = test_message.replace('"', '\\"').replace('\n', '\\n')
            
            applescript = f'''
            tell application "Messages"
                set targetService to 1st service whose service type = iMessage
                set targetBuddy to buddy "{email}" of targetService
                send "{safe_message}" to targetBuddy
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Email {email} - SUCCESS")
            else:
                print(f"❌ Email {email} - FAILED: {result.stderr}")
        
        except Exception as e:
            print(f"❌ Email {email} - ERROR: {e}")
    
    print("\n" + "=" * 40)
    print("NEXT STEPS:")
    print("1. Jos email toimi - numero ongelma")
    print("2. Jos email ei toiminut - iMessage/Apple ID ongelma")
    print("3. Kokeile lisätä +358440606044 Contacts:iin")
    print("4. Varmista että kone + puhelin = sama Apple ID")

if __name__ == "__main__":
    test_email_imessage()