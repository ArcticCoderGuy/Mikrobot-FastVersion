#!/usr/bin/env python3
"""
Test different phone number formats for iMessage
"""

import subprocess
from datetime import datetime

def test_number_formats():
    """Test different number formats"""
    
    print("📱 TESTING DIFFERENT NUMBER FORMATS")
    print("=" * 40)
    
    # Different formats to try
    number_formats = [
        "+358440606044",    # International with +
        "358440606044",     # International without +
        "0440606044",       # Finnish national format
        "+358 44 060 6044", # With spaces
        "044-060-6044",     # With dashes
        "+358 (44) 060-6044" # Mixed format
    ]
    
    for i, number in enumerate(number_formats, 1):
        print(f"\n🧪 Test {i}: Format '{number}'")
        
        try:
            test_message = f"📱 Test {i}: {number} @ {datetime.now().strftime('%H:%M:%S')}"
            
            applescript = f'''
            tell application "Messages"
                set targetService to 1st service whose service type = iMessage
                set targetBuddy to buddy "{number}" of targetService
                send "{test_message}" to targetBuddy
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Format {number} - SUCCESS")
            else:
                print(f"❌ Format {number} - FAILED: {result.stderr}")
        
        except Exception as e:
            print(f"❌ Format {number} - ERROR: {e}")
    
    print("\n" + "=" * 40)
    print("📱 Check your phone - see which format worked!")
    print("If none worked, check:")
    print("1. Is the number added to your Contacts?")
    print("2. Is iMessage enabled on your phone?")  
    print("3. Is your Mac logged into the same Apple ID?")
    print("4. Try adding the number to Contacts first")

if __name__ == "__main__":
    test_number_formats()