"""
BCHUSD M5 TESTING - CURRENT EA v3 STATUS
Testataan nykyinen EA v3 BCHUSD M5 kaupankäynti
"""

import json
import time
import os
from datetime import datetime

def test_bchusd_m5_current():
    """Test current BCHUSD M5 trading with EA v3"""
    
    print("BCHUSD M5 TRADING TEST - EA v3 CURRENT STATUS")
    print("=" * 60)
    print("Testing EA v3 (MikrobotFastversionEA.mq5) with BCHUSD M5")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    # Multiple possible signal file locations
    signal_files = [
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_fastversion_signal.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/Files/mikrobot_fastversion_signal.json"
    ]
    
    print("STEP 1: Cleaning old signals...")
    for signal_file in signal_files:
        if os.path.exists(signal_file):
            try:
                os.remove(signal_file)
                print(f"Removed: {signal_file}")
            except Exception as e:
                print(f"Failed to remove {signal_file}: {e}")
    
    # Wait for EA initialization
    print("\nSTEP 2: Waiting for EA initialization...")
    time.sleep(3)
    
    print("\nSTEP 3: Creating BCHUSD M5 BOS signal...")
    
    # Create M5 BOS signal for BCHUSD
    test_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "BUY",
        "entry_price": 540.25,  # Current approx BCHUSD price
        "confidence": 0.92,
        "atr_pips": 8,
        "ylipip_trigger": 0.6,
        "stop_loss": 532.0,     # ~8 pip SL
        "take_profit": 556.0,   # ~16 pip TP (1:2 RR)
        "lot_size": 1.0,        # CFD_CRYPTO standard lot
        "strategy": "MIKROBOT_FASTVERSION_M5_BOS",
        "test_id": "BCHUSD_M5_CURRENT_TEST",
        "magic_number": 999888,
        "comment": "BCHUSD_M5_BOS_TEST",
        "source": "PYTHON_CURRENT_TEST"
    }
    
    print("Signal Details:")
    print(f"  Symbol: {test_signal['symbol']}")
    print(f"  Timeframe: {test_signal['timeframe']}")
    print(f"  Signal Type: {test_signal['signal_type']}")
    print(f"  Direction: {test_signal['direction']}")
    print(f"  Entry: {test_signal['entry_price']}")
    print(f"  Stop Loss: {test_signal['stop_loss']}")
    print(f"  Take Profit: {test_signal['take_profit']}")
    print(f"  Lot Size: {test_signal['lot_size']}")
    print(f"  Confidence: {test_signal['confidence']}")
    
    # Try to write to multiple locations
    signal_written = False
    active_signal_file = None
    
    for signal_file in signal_files:
        try:
            os.makedirs(os.path.dirname(signal_file), exist_ok=True)
            
            with open(signal_file, 'w') as f:
                json.dump(test_signal, f, indent=2)
            
            print(f"\nSignal written to: {signal_file}")
            signal_written = True
            active_signal_file = signal_file
            break
            
        except Exception as e:
            print(f"Failed to write to {signal_file}: {e}")
            continue
    
    if not signal_written:
        print("CRITICAL: Could not write signal to any location!")
        return False
    
    print(f"\nSTEP 4: Monitoring EA response...")
    print("Watching for EA to process the signal...")
    
    # Monitor for EA response (check if signal file gets processed)
    start_time = time.time()
    max_wait_time = 30  # 30 seconds max wait
    
    while time.time() - start_time < max_wait_time:
        if not os.path.exists(active_signal_file):
            print("Signal file consumed by EA - Signal processed!")
            break
        
        # Check for status file
        status_files = [
            "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_status.json",
            "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_status.json"
        ]
        
        for status_file in status_files:
            if os.path.exists(status_file):
                try:
                    with open(status_file, 'r') as f:
                        status = json.load(f)
                    print(f"EA Status: {status}")
                    break
                except:
                    pass
        
        print(".", end="", flush=True)
        time.sleep(1)
    
    print("\n")
    
    # Final check
    if os.path.exists(active_signal_file):
        print("WARNING: Signal file still exists - EA may not be processing signals")
        print("Possible issues:")
        print("  1. EA not running on BCHUSD M5 chart")
        print("  2. EA parameters blocking BCHUSD trading")
        print("  3. MT5 connection issues")
        print("  4. Signal format not compatible with current EA")
        
        # Try to read the file to see if it was modified
        try:
            with open(active_signal_file, 'r') as f:
                remaining_signal = json.load(f)
            print(f"  Signal still in file: {remaining_signal.get('test_id', 'Unknown')}")
        except:
            print("  Could not read remaining signal file")
    else:
        print("SUCCESS: Signal consumed - EA is active and processing!")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("Signal created successfully")
    print("Signal written to file system")
    print("EA response:", "PROCESSED" if not os.path.exists(active_signal_file) else "NO RESPONSE")
    print("=" * 60)
    
    return not os.path.exists(active_signal_file)

if __name__ == "__main__":
    success = test_bchusd_m5_current()
    
    if success:
        print("\nTEST PASSED: EA is processing BCHUSD signals!")
    else:
        print("\nTEST ISSUES: EA may not be responding to signals")
        print("\nNext steps to diagnose:")
        print("1. Check MT5 terminal - is EA running on BCHUSD M5?")
        print("2. Check MT5 Expert tab for error messages")
        print("3. Verify EA input parameters allow BCHUSD trading")
        print("4. Check if EnableCFDCrypto = true in EA settings")