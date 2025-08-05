"""
UNIFIED BCHUSD M5 TEST - READY FOR ANY EA VERSION
Tests all possible signal filenames to work with any EA version
"""

import json
import time
import os
from datetime import datetime

def test_unified_bchusd_signal():
    """Send BCHUSD signal to ALL possible files for maximum compatibility"""
    
    print("UNIFIED BCHUSD M5 TEST - ALL EA VERSIONS COMPATIBLE")
    print("=" * 60)
    print("Testing with ALL signal filenames:")
    print("- mikrobot_fastversion_signal.json (EA v7)")
    print("- mikrobot_4phase_signal.json (EA v8_Fixed)")
    print("- mikrobot_signal.json (EA v3/v4)")
    print("=" * 60)
    
    # All possible signal file locations
    signal_files = [
        # EA v7 and current working version
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json",
        
        # EA v8_Fixed Stupid version  
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json",
        
        # EA v3/v4 version
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_signal.json",
        
        # Backup locations
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/Files/mikrobot_fastversion_signal.json"
    ]
    
    # Clean all old signals
    print("STEP 1: Cleaning all old signals...")
    for signal_file in signal_files:
        if os.path.exists(signal_file):
            try:
                os.remove(signal_file)
                print(f"Cleaned: {os.path.basename(signal_file)}")
            except Exception as e:
                print(f"Could not clean {os.path.basename(signal_file)}: {e}")
    
    # Create unified BCHUSD M5 BOS signal
    print("\nSTEP 2: Creating unified BCHUSD M5 BOS signal...")
    
    unified_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "BUY",
        "entry_price": 541.00,
        "confidence": 0.93,
        "atr_pips": 8,
        "ylipip_trigger": 0.6,
        "stop_loss": 533.0,
        "take_profit": 557.0,
        "lot_size": 1.0,
        "strategy": "UNIFIED_MIKROBOT_TEST",
        "test_id": "BCHUSD_UNIFIED_ALL_EAS",
        "magic_number": 999888,
        "comment": "BCHUSD_UNIFIED_TEST",
        "source": "PYTHON_UNIFIED_SYSTEM",
        
        # Additional fields for different EA versions
        "action": "BUY",          # For some EA versions
        "volume": 1.0,            # Alternative lot field
        "sl": 533.0,              # Alternative SL field
        "tp": 557.0,              # Alternative TP field
        "order_type": "MARKET",   # For market orders
        "phase": "ENTRY"          # For 4-phase system
    }
    
    print("Signal Details:")
    print(f"  Symbol: {unified_signal['symbol']}")
    print(f"  Direction: {unified_signal['direction']}")
    print(f"  Entry: {unified_signal['entry_price']}")
    print(f"  Stop Loss: {unified_signal['stop_loss']}")
    print(f"  Take Profit: {unified_signal['take_profit']}")
    print(f"  Lot Size: {unified_signal['lot_size']}")
    print(f"  Confidence: {unified_signal['confidence']}")
    
    # Write to ALL signal files
    print(f"\nSTEP 3: Writing signal to ALL possible files...")
    signals_written = []
    
    for signal_file in signal_files:
        try:
            os.makedirs(os.path.dirname(signal_file), exist_ok=True)
            
            with open(signal_file, 'w') as f:
                json.dump(unified_signal, f, indent=2)
            
            signals_written.append(signal_file)
            print(f"SUCCESS: {os.path.basename(signal_file)}")
            
        except Exception as e:
            print(f"FAILED: {os.path.basename(signal_file)} - {e}")
    
    if not signals_written:
        print("CRITICAL ERROR: Could not write to any signal file!")
        return False
    
    print(f"\nSTEP 4: Monitoring EA response ({len(signals_written)} files written)...")
    print("Watching for ANY EA to consume ANY signal file...")
    
    # Monitor all files for consumption
    start_time = time.time()
    max_wait_time = 20  # 20 seconds
    
    while time.time() - start_time < max_wait_time:
        files_consumed = []
        files_remaining = []
        
        for signal_file in signals_written:
            if not os.path.exists(signal_file):
                files_consumed.append(os.path.basename(signal_file))
            else:
                files_remaining.append(os.path.basename(signal_file))
        
        if files_consumed:
            print(f"\nSUCCESS: EA consumed signal from: {', '.join(files_consumed)}")
            if files_remaining:
                print(f"Remaining: {', '.join(files_remaining)}")
            return True
        
        print(".", end="", flush=True)
        time.sleep(1)
    
    print(f"\nWARNING: No EA consumed any signal after {max_wait_time} seconds")
    print("Files still present:")
    for signal_file in signals_written:
        if os.path.exists(signal_file):
            print(f"  - {os.path.basename(signal_file)}")
    
    return False

def show_post_test_instructions():
    """Show instructions for EA version switching"""
    
    print("\n" + "=" * 60)
    print("POST-TEST INSTRUCTIONS")
    print("=" * 60)
    print("If test shows NO EA response:")
    print("1. Check MT5 terminal - which EA is actually running?")
    print("2. Check EA parameters - is EnableCFDCrypto = true?")
    print("3. Check MT5 Expert tab for error messages")
    print()
    print("To switch to v8_Fixed Stupid EA:")
    print("1. Remove current EA from BCHUSD M5 chart")
    print("2. Drag MikrobotStupidv8_Fixed.mq5 to BCHUSD M5 chart")
    print("3. Set parameters: EnableDebug = true, YlipipTrigger = 0.6")
    print("4. Run this test again")
    print()
    print("Expected behavior:")
    print("- v8_Fixed Stupid EA: Detects M5 patterns, sends to Python MCP")
    print("- Python ML/MCP: Processes signal, makes trading decision")
    print("- Signal flows: EA -> Python -> EA (if decision = trade)")
    print("=" * 60)

if __name__ == "__main__":
    print("STARTING UNIFIED BCHUSD M5 TEST...")
    print("This test works with ANY EA version!")
    print("timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    success = test_unified_bchusd_signal()
    
    if success:
        print("\nTEST RESULT: SUCCESS - EA is active and processing BCHUSD signals!")
        print("Your EA is working correctly!")
    else:
        print("\nTEST RESULT: NO RESPONSE - EA may not be active on BCHUSD M5")
        show_post_test_instructions()
    
    print(f"\nTest completed at: {datetime.now().strftime('%H:%M:%S')}")