#!/usr/bin/env python3
"""
Force image sending test
"""

import subprocess
import os
from datetime import datetime
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart

def force_image_test():
    """Force send image to verify it works"""
    
    print("🔥 FORCE IMAGE SENDING TEST")
    print("=" * 40)
    
    # Generate fresh chart
    print("📊 Generating fresh chart...")
    chart_path = generate_pattern_chart("EURUSD", "FORCE TEST", 1.16400)
    
    if chart_path and os.path.exists(chart_path):
        print(f"✅ Chart: {chart_path}")
        print(f"📏 Size: {os.path.getsize(chart_path)} bytes")
        
        # Manual AppleScript with debug
        message_text = f"🔥 FORCE IMAGE TEST\\n\\n📊 Chart tulossa pakolla!\\n🕐 {datetime.now().strftime('%H:%M:%S')}\\n\\nJos tämä ei toimi, macOS esto on syynä."
        
        applescript = f'''
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy "+358440606044" of targetService
            
            -- Send text first
            send "{message_text}" to targetBuddy
            
            -- Send image as file properly
            set theFile to (POSIX file "{chart_path}") as alias
            send theFile to targetBuddy
            
            -- Confirm
            send "📊 Image sent!" to targetBuddy
        end tell
        '''
        
        print("📱 Executing force send...")
        
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            print("✅ FORCE SEND SUCCESSFUL!")
            print("📱 Check your phone for:")
            print("   1. Text message")
            print("   2. Chart image")  
            print("   3. Confirmation message")
        else:
            print(f"❌ FORCE SEND FAILED: {result.stderr}")
            
        # Also show what the chart looks like
        print(f"\n📊 Chart details:")
        print(f"   File: {os.path.basename(chart_path)}")
        print(f"   Path: {chart_path}")
        print(f"   Exists: {os.path.exists(chart_path)}")
        print(f"   Size: {os.path.getsize(chart_path)} bytes")
        
    else:
        print("❌ Chart generation failed")

if __name__ == "__main__":
    force_image_test()