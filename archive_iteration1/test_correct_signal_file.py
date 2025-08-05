"""
Test sending signal to CORRECT file for EA v3
EA v3 expects: mikrobot_signal.json (NOT mikrobot_fastversion_signal.json)
"""

import json
import time
from datetime import datetime

def test_correct_signal_file():
    """Send signal to the file EA v3 actually expects"""
    
    print("TESTING CORRECT SIGNAL FILE FOR EA v3")
    print("=" * 50)
    print("EA v3 expects: mikrobot_signal.json")
    print("Previous test used: mikrobot_fastversion_signal.json")
    print("=" * 50)
    
    # CORRECT signal file for EA v3
    correct_signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_signal.json"
    
    # Create BCHUSD M5 BOS signal
    signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "BUY",
        "entry_price": 540.25,
        "confidence": 0.92,
        "atr_pips": 8,
        "ylipip_trigger": 0.6,
        "stop_loss": 532.0,
        "take_profit": 556.0,
        "lot_size": 1.0,
        "strategy": "MIKROBOT_CORRECT_FILE_TEST",
        "test_id": "EA_V3_CORRECT_FILE",
        "magic_number": 999888,
        "comment": "BCHUSD_CORRECT_FILE_TEST",
        "source": "PYTHON_CORRECT_FILE_TEST"
    }
    
    print("Creating signal for CORRECT EA v3 file...")
    print(f"File: {correct_signal_file}")
    print(f"Signal: {signal['symbol']} {signal['direction']} at {signal['entry_price']}")
    
    try:
        with open(correct_signal_file, 'w') as f:
            json.dump(signal, f, indent=2)
        
        print("SUCCESS: Signal written to CORRECT file!")
        print("Monitoring for EA response...")
        
        # Monitor if file gets consumed
        start_time = time.time()
        max_wait = 15  # 15 seconds
        
        while time.time() - start_time < max_wait:
            if not os.path.exists(correct_signal_file):
                print("SUCCESS: EA consumed the signal from CORRECT file!")
                return True
            print(".", end="", flush=True)
            time.sleep(1)
        
        print("\nWARNING: Signal file still exists after 15 seconds")
        return False
        
    except Exception as e:
        print(f"ERROR: Could not write to correct file: {e}")
        return False

if __name__ == "__main__":
    import os
    
    result = test_correct_signal_file()
    
    if result:
        print("\nCONCLUSION: EA v3 responds to mikrobot_signal.json")
        print("SOLUTION: Update Python ML/MCP system to use correct filename")
    else:
        print("\nCONCLUSION: Issue may be deeper than filename mismatch")
        print("Check: 1) EA running? 2) EnableCFDCrypto = true? 3) MT5 connection?")