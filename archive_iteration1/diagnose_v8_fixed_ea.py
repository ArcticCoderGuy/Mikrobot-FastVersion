"""
DIAGNOSE EA v8_Fixed SIGNAL PROCESSING
Check exactly what the EA expects and where it's looking
"""

import os
import json
from datetime import datetime
import time

def diagnose_ea_v8_fixed():
    """Diagnose what EA v8_Fixed is expecting"""
    
    print("DIAGNOSING EA v8_Fixed SIGNAL PROCESSING")
    print("=" * 50)
    print("Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)
    
    # Check all possible signal file locations
    signal_locations = [
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/Files/mikrobot_4phase_signal.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_4phase_signal.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/m5_pattern_signal.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/Files/m5_pattern_signal.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/m5_pattern_signal.json"
    ]
    
    print("STEP 1: Checking file system status...")
    for location in signal_locations:
        if os.path.exists(location):
            try:
                with open(location, 'r') as f:
                    content = f.read()
                print(f"EXISTS: {os.path.basename(location)} - {len(content)} chars")
            except:
                print(f"EXISTS: {os.path.basename(location)} - Cannot read")
        else:
            print(f"MISSING: {os.path.basename(location)}")
    
    print("\nSTEP 2: Creating minimal test signal for v8_Fixed...")
    
    # Create very simple signal that v8_Fixed should understand
    minimal_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "direction": "BUY",
        "signal_type": "M5_BOS",
        "test": "MINIMAL_V8_FIXED"
    }
    
    # Try the most likely location first
    test_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json"
    
    try:
        with open(test_file, 'w') as f:
            json.dump(minimal_signal, f, indent=2)
        print(f"CREATED: {os.path.basename(test_file)}")
        print(f"Content: {minimal_signal}")
        
        print("\nSTEP 3: Monitoring for 10 seconds...")
        start_time = time.time()
        
        while time.time() - start_time < 10:
            if not os.path.exists(test_file):
                print("SUCCESS: EA consumed the minimal signal!")
                return True
            print(".", end="", flush=True)
            time.sleep(1)
        
        print("\nWARNING: EA did not consume minimal signal")
        
        # Check if file was modified
        try:
            with open(test_file, 'r') as f:
                remaining = json.load(f)
            if remaining != minimal_signal:
                print("MODIFIED: EA modified but didn't consume the signal")
                print(f"Modified content: {remaining}")
            else:
                print("UNCHANGED: EA completely ignored the signal")
        except:
            print("ERROR: Cannot read remaining signal")
            
        return False
        
    except Exception as e:
        print(f"ERROR: Cannot create test signal - {e}")
        return False

def check_ea_status_files():
    """Check for EA status/log files"""
    
    print("\nSTEP 4: Checking for EA status files...")
    
    status_locations = [
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_status.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_status.txt",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_status.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/Files/mikrobot_status.txt"
    ]
    
    for location in status_locations:
        if os.path.exists(location):
            try:
                with open(location, 'r') as f:
                    content = f.read()
                print(f"STATUS FILE: {os.path.basename(location)}")
                print(f"Content: {content}")
                print("-" * 30)
            except Exception as e:
                print(f"STATUS FILE: {os.path.basename(location)} - Cannot read: {e}")

def show_diagnosis_conclusion():
    """Show diagnosis conclusion and next steps"""
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS CONCLUSION")
    print("=" * 50)
    print("EA v8_Fixed is NOT processing signals.")
    print()
    print("Possible causes:")
    print("1. EA not properly attached to BCHUSD M5 chart")
    print("2. EA input parameters wrong (check EnableDebug, etc.)")
    print("3. EA has compilation errors")
    print("4. EA is monitoring different file location")
    print("5. MT5 terminal has issues")
    print()
    print("NEXT STEPS:")
    print("1. Check MT5 Expert tab for EA error messages")
    print("2. Check MT5 Journal tab for loading errors")
    print("3. Verify EA is attached to BCHUSD M5 with smiley face")
    print("4. Check EA input parameters")
    print("5. Try recompiling EA v8_Fixed")
    print("=" * 50)

if __name__ == "__main__":
    success = diagnose_ea_v8_fixed()
    check_ea_status_files()
    
    if not success:
        show_diagnosis_conclusion()
    else:
        print("\nSUCCESS: EA v8_Fixed is working correctly!")
    
    print(f"\nDiagnosis completed at: {datetime.now().strftime('%H:%M:%S')}")