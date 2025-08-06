#!/usr/bin/env python3
"""
Test iMessage image sending
"""

import subprocess
import os
from datetime import datetime
from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart

def test_imessage_image():
    """Test sending image via iMessage"""
    
    print("📊 TESTING iMESSAGE IMAGE SENDING")
    print("=" * 40)
    
    # Generate test chart
    print("📊 Generating test chart...")
    chart_path = generate_pattern_chart("EURUSD", "Phase 1", 1.16318)
    
    if chart_path and os.path.exists(chart_path):
        print(f"✅ Chart generated: {chart_path}")
        print(f"📏 File size: {os.path.getsize(chart_path)} bytes")
        
        # Test different AppleScript approaches
        approaches = [
            "Method 1: Direct file path",
            "Method 2: POSIX file",
            "Method 3: Attachment method"
        ]
        
        for i, approach in enumerate(approaches, 1):
            print(f"\n🧪 {approach}")
            
            try:
                if i == 1:
                    # Method 1: Direct path
                    applescript = f'''
                    tell application "Messages"
                        set targetService to 1st service whose service type = iMessage
                        set targetBuddy to buddy "+358440606044" of targetService
                        send "📊 Test {i}: Direct path" to targetBuddy
                        send "{chart_path}" to targetBuddy
                    end tell
                    '''
                
                elif i == 2:
                    # Method 2: POSIX file
                    applescript = f'''
                    tell application "Messages"
                        set targetService to 1st service whose service type = iMessage  
                        set targetBuddy to buddy "+358440606044" of targetService
                        send "📊 Test {i}: POSIX file" to targetBuddy
                        set imageFile to POSIX file "{chart_path}"
                        send imageFile to targetBuddy
                    end tell
                    '''
                
                elif i == 3:
                    # Method 3: File as attachment
                    applescript = f'''
                    tell application "Messages"
                        set targetService to 1st service whose service type = iMessage
                        set targetBuddy to buddy "+358440606044" of targetService
                        send "📊 Test {i}: Attachment method" to targetBuddy
                        set theAttachment to POSIX file "{chart_path}" as alias
                        send theAttachment to targetBuddy
                    end tell
                    '''
                
                result = subprocess.run(['osascript', '-e', applescript], 
                                      capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    print(f"✅ Method {i} - SUCCESS")
                else:
                    print(f"❌ Method {i} - FAILED: {result.stderr}")
            
            except Exception as e:
                print(f"❌ Method {i} - ERROR: {e}")
        
        # Test manual file check
        print(f"\n🔍 Manual file check:")
        print(f"File exists: {os.path.exists(chart_path)}")
        print(f"File readable: {os.access(chart_path, os.R_OK)}")
        print(f"File path: {chart_path}")
        
    else:
        print("❌ Failed to generate chart")

if __name__ == "__main__":
    test_imessage_image()