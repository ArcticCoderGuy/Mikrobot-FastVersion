"""
V8 STUPID EA TEST
Test that v8 EA only detects patterns and sends signals to Python
"""

import time
import os
import json
from datetime import datetime

def test_v8_stupid_ea():
    """Test v8 STUPID EA pattern detection"""
    
    print("MIKROBOT V8 STUPID EA TEST")
    print("=" * 60)
    print("BUILD: 20250103-008")
    print("TESTING: M5 pattern detection → Python signal")
    print("EXPECTATION: EA sends signal, Python does thinking")
    print("=" * 60)
    
    # File paths
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/m5_pattern_signal.json"
    command_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/python_execution_command.json"
    
    # Clean up old files
    for file_path in [signal_file, command_file]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Cleaned up: {os.path.basename(file_path)}")
    
    print("\nWaiting for v8 STUPID EA to detect M5 patterns...")
    print("EA should be watching BCHUSD chart and detecting patterns")
    print("Looking for signal file creation...")
    
    # Wait for signal from EA
    start_time = time.time()
    signal_detected = False
    
    for i in range(30):  # Wait up to 30 seconds
        if os.path.exists(signal_file):
            print(f"\nSUCCESS: v8 EA sent signal after {i+1} seconds!")
            signal_detected = True
            
            # Read the signal
            try:
                with open(signal_file, 'r') as f:
                    signal_content = f.read()
                    
                print(f"SIGNAL CONTENT: {signal_content}")
                
                # Parse signal
                signal_data = json.loads(signal_content)
                print(f"PARSED SIGNAL:")
                print(f"  Symbol: {signal_data.get('symbol')}")
                print(f"  Pattern: {signal_data.get('pattern')}")
                print(f"  Price: {signal_data.get('current_price')}")
                print(f"  Source: {signal_data.get('source')}")
                print(f"  Build: {signal_data.get('build_version')}")
                
            except Exception as e:
                print(f"Error parsing signal: {e}")
                
            break