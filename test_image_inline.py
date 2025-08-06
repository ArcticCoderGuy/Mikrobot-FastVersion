#!/usr/bin/env python3
"""
Test inline image sending to iMessage
"""
import subprocess
import os
from datetime import datetime

def test_inline_image():
    """Test different methods to send inline image"""
    
    # Use latest chart
    chart_dir = "/Users/markuskaprio/Desktop/Claude Code Projektit/MikrobotFastversion/charts"
    chart_files = [f for f in os.listdir(chart_dir) if f.endswith('.png')]
    if not chart_files:
        print("❌ No chart files found")
        return
    
    latest_chart = os.path.join(chart_dir, sorted(chart_files)[-1])
    print(f"📊 Using chart: {latest_chart}")
    
    # Method 1: Copy to clipboard, then use GUI automation
    print("\n🔥 METHOD 1: Clipboard + GUI automation")
    
    try:
        # Copy image to clipboard
        clipboard_cmd = f'osascript -e "set the clipboard to (read (POSIX file \\"{latest_chart}\\") as JPEG picture)"'
        result1 = subprocess.run(clipboard_cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(f"Clipboard result: {result1.returncode}")
        
        # Activate Messages and paste
        applescript = '''
        tell application "Messages" to activate
        delay 1
        tell application "System Events"
            tell process "Messages"
                -- Find the conversation with +358440606044
                delay 1
                -- Send a quick text first
                keystroke "INLINE IMAGE TEST - kuva tulossa!"
                key code 36
                delay 1
                -- Paste image
                keystroke "v" using command down
                delay 1
                key code 36
            end tell
        end tell
        '''
        
        result2 = subprocess.run(['osascript', '-e', applescript], 
                               capture_output=True, text=True, timeout=20)
        print(f"GUI automation result: {result2.returncode}")
        if result2.stderr:
            print(f"Error: {result2.stderr}")
            
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    print("\n🔥 METHOD 2: Simple message + file attachment")
    # Try the old file method but with different attachment approach
    applescript2 = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "+358440606044" of targetService
        send "FILE ATTACHMENT TEST" to targetBuddy
        
        -- Try different attachment method
        set imageFile to POSIX file "{latest_chart}" as alias
        send imageFile to targetBuddy
    end tell
    '''
    
    try:
        result3 = subprocess.run(['osascript', '-e', applescript2], 
                               capture_output=True, text=True, timeout=15)
        print(f"File attachment result: {result3.returncode}")
        if result3.stderr:
            print(f"Error: {result3.stderr}")
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")

if __name__ == "__main__":
    test_inline_image()