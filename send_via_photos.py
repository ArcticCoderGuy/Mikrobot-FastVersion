#!/usr/bin/env python3
"""
Send image via Photos app integration
"""
import subprocess
import os
from datetime import datetime
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart

def send_via_photos():
    """Import to Photos and share from there"""
    
    print("📸 PHOTOS APP METHOD")
    print("=" * 40)
    
    # Generate chart
    print("📊 Generating chart...")
    chart_path = generate_pattern_chart("EURUSD", "PHOTOS TEST", 1.16400)
    
    if not chart_path or not os.path.exists(chart_path):
        print("❌ Chart generation failed")
        return
        
    print(f"✅ Chart: {chart_path}")
    
    # Method 1: Import to Photos first
    print("\n📸 Importing to Photos app...")
    
    import_script = f'''
    tell application "Photos"
        activate
        delay 1
        import POSIX file "{chart_path}" without skip check duplicates
        delay 2
    end tell
    '''
    
    result = subprocess.run(['osascript', '-e', import_script], 
                          capture_output=True, text=True, timeout=15)
    
    if result.returncode == 0:
        print("✅ Imported to Photos")
    else:
        print(f"❌ Import failed: {result.stderr}")
    
    # Method 2: Direct share sheet approach
    print("\n📤 Trying share sheet method...")
    
    share_script = f'''
    do shell script "open -a Messages"
    delay 2
    
    tell application "System Events"
        tell process "Messages"
            -- New message
            keystroke "n" using command down
            delay 1
            
            -- Enter phone number
            keystroke "+358440606044"
            delay 1
            key code 36 -- Enter
            delay 1
            
            -- Type message
            keystroke "📊 LIGHTNING BOLT CHART (Photos method)"
            key code 36 -- Send
            delay 1
            
            -- Open file dialog to attach image
            keystroke "f" using {{command down, shift down}}
            delay 2
            
            -- Navigate to chart file
            keystroke "g" using {{command down, shift down}}
            delay 1
            keystroke "{chart_path}"
            delay 1
            key code 36 -- Enter
            delay 2
            key code 36 -- Select file
            delay 2
            key code 36 -- Send
        end tell
    end tell
    '''
    
    result2 = subprocess.run(['osascript', '-e', share_script], 
                           capture_output=True, text=True, timeout=30)
    
    if result2.returncode == 0:
        print("✅ Share sheet method completed")
    else:
        print(f"Share result: {result2.stderr}")

if __name__ == "__main__":
    send_via_photos()