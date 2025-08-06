#!/usr/bin/env python3
"""
Create a custom shortcut for sending images via iMessage
"""
import subprocess
import os
from datetime import datetime

def create_imessage_shortcut():
    """Create shortcut for sending images"""
    
    print("🔧 CREATING IMESSAGE SHORTCUT")
    print("=" * 40)
    
    # Create shortcut definition
    shortcut_script = '''
    tell application "Shortcuts Events"
        set newShortcut to make new shortcut with properties {name:"Send Chart to Markus"}
        
        tell newShortcut
            -- Add actions
            make new "Send Message" action with properties {recipient:"+358440606044"}
        end tell
    end tell
    '''
    
    # Alternative: Use shortcuts CLI
    print("\n📱 Setting up direct send method...")
    
    # Get latest chart
    chart_dir = "/Users/markuskaprio/Desktop/Claude Code Projektit/MikrobotFastversion/charts"
    charts = sorted([f for f in os.listdir(chart_dir) if f.endswith('.png')])
    
    if not charts:
        print("❌ No charts found")
        return
        
    latest_chart = os.path.join(chart_dir, charts[-1])
    print(f"📊 Using: {charts[-1]}")
    
    # Method: Use open command with Messages
    print("\n🚀 Sending via open command...")
    
    # Open Messages with the file
    cmd = f'open -a Messages "{latest_chart}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Opened in Messages")
        
        # Now automate sending
        send_script = '''
        tell application "System Events"
            tell process "Messages"
                delay 2
                -- Type recipient
                keystroke "+358440606044"
                delay 1
                keystroke tab
                delay 1
                -- Type message
                keystroke "📊 Lightning Bolt Chart"
                delay 1
                -- Send
                key code 36
            end tell
        end tell
        '''
        
        result2 = subprocess.run(['osascript', '-e', send_script], 
                               capture_output=True, text=True, timeout=15)
        
        if result2.returncode == 0:
            print("✅ Message sent!")
        else:
            print(f"Send error: {result2.stderr}")
    else:
        print(f"❌ Open failed: {result.stderr}")

if __name__ == "__main__":
    create_imessage_shortcut()