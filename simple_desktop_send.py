#!/usr/bin/env python3
"""
Simple desktop method - save to Desktop and send
"""
import subprocess
import shutil
import os
from datetime import datetime
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart

def simple_desktop_send():
    """Copy chart to Desktop and send via Messages"""
    
    print("🖥️ DESKTOP METHOD")
    print("=" * 40)
    
    # Generate chart
    print("📊 Generating chart...")
    chart_path = generate_pattern_chart("EURUSD", "DESKTOP TEST", 1.16400)
    
    if not chart_path or not os.path.exists(chart_path):
        print("❌ Chart generation failed")
        return
    
    # Copy to Desktop with simple name
    desktop_path = os.path.expanduser("~/Desktop/lightning_bolt_chart.png")
    shutil.copy2(chart_path, desktop_path)
    print(f"✅ Copied to Desktop: {desktop_path}")
    
    # Send via Messages using simpler AppleScript
    applescript = f'''
    tell application "Messages"
        activate
        
        -- Find or create conversation
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "+358440606044" of targetService
        
        -- Send text
        send "⚡ LIGHTNING BOLT DETECTED!" to targetBuddy
        
        -- Wait a moment
        delay 1
        
        -- Send the desktop file
        set desktopFile to (path to desktop as text) & "lightning_bolt_chart.png"
        set imageFile to POSIX file "/Users/markuskaprio/Desktop/lightning_bolt_chart.png" as alias
        send imageFile to targetBuddy
        
        -- Confirmation
        send "📊 Chart sent from Desktop!" to targetBuddy
    end tell
    '''
    
    print("\n📱 Sending via Messages...")
    result = subprocess.run(['osascript', '-e', applescript], 
                          capture_output=True, text=True, timeout=20)
    
    if result.returncode == 0:
        print("✅ SUCCESS!")
        print("\n📱 Check your devices for:")
        print("   1. Lightning Bolt alert")
        print("   2. Chart image") 
        print("   3. Confirmation message")
    else:
        print(f"❌ Failed: {result.stderr}")
    
    print(f"\n📊 Desktop file: {desktop_path}")
    print(f"   Size: {os.path.getsize(desktop_path)} bytes")

if __name__ == "__main__":
    simple_desktop_send()