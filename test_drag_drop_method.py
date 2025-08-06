#!/usr/bin/env python3
"""
Test drag & drop method for sending images
"""

import subprocess
import os
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart

def test_drag_drop():
    """Test drag & drop method"""
    
    print("🖱️ TESTING DRAG & DROP METHOD")
    print("=" * 40)
    
    # Generate chart
    chart_path = generate_pattern_chart("BTCUSD", "Phase 1", 114000)
    
    if chart_path and os.path.exists(chart_path):
        print(f"✅ Chart: {chart_path}")
        
        # Alternative method: Use System Events to drag file
        applescript = f'''
        tell application "Messages" to activate
        delay 1
        
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy "+358440606044" of targetService
            send "🖱️ DRAG DROP TEST - Image tulossa..." to targetBuddy
        end tell
        
        delay 2
        
        tell application "System Events"
            tell process "Messages"
                keystroke "v" using {{command down}}
                delay 1
            end tell
        end tell
        '''
        
        # First copy file to clipboard
        copy_script = f'''
        set the clipboard to (read (POSIX file "{chart_path}") as JPEG picture)
        '''
        
        print("📋 Copying image to clipboard...")
        result1 = subprocess.run(['osascript', '-e', copy_script], 
                                capture_output=True, text=True)
        
        if result1.returncode == 0:
            print("✅ Image copied to clipboard")
            
            print("📱 Sending via paste...")
            result2 = subprocess.run(['osascript', '-e', applescript], 
                                   capture_output=True, text=True)
            
            if result2.returncode == 0:
                print("✅ Drag drop method sent!")
            else:
                print(f"❌ Drag drop failed: {result2.stderr}")
        else:
            print(f"❌ Clipboard copy failed: {result1.stderr}")
            
        # Also try direct file insertion
        print("\n📎 Trying direct file method...")
        
        direct_script = f'''
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy "+358440606044" of targetService
            send "📎 DIRECT FILE TEST" to targetBuddy
            
            set theFile to POSIX file "{chart_path}"
            send theFile to targetBuddy
        end tell
        '''
        
        result3 = subprocess.run(['osascript', '-e', direct_script], 
                               capture_output=True, text=True)
        
        if result3.returncode == 0:
            print("✅ Direct file method sent!")
        else:
            print(f"❌ Direct file failed: {result3.stderr}")

if __name__ == "__main__":
    test_drag_drop()