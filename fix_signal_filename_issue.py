"""
FIX SIGNAL FILENAME ISSUE - SOLUTION
EA expects: mikrobot_fastversion_signal.json
Python was sending to wrong files after v7!

UPDATE ALL PYTHON ML/MCP FILES TO USE CORRECT FILENAME
"""

import json
from datetime import datetime

def create_working_bchusd_signal():
    """Create BCHUSD signal with CORRECT filename for current EA"""
    
    print("CREATING WORKING BCHUSD M5 SIGNAL")
    print("=" * 45)
    print("SOLUTION: Use mikrobot_fastversion_signal.json")
    print("=" * 45)
    
    # CORRECT signal file that EA actually monitors
    CORRECT_SIGNAL_FILE = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Working BCHUSD M5 BOS signal
    working_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "BUY",
        "entry_price": 540.75,
        "confidence": 0.91,
        "atr_pips": 8,
        "ylipip_trigger": 0.6,
        "stop_loss": 532.5,
        "take_profit": 557.0,
        "lot_size": 1.0,
        "strategy": "MIKROBOT_FASTVERSION_WORKING",
        "test_id": "BCHUSD_WORKING_SOLUTION",
        "magic_number": 999888,
        "comment": "BCHUSD_WORKING_TRADE",
        "source": "PYTHON_SOLUTION_FIX"
    }
    
    try:
        with open(CORRECT_SIGNAL_FILE, 'w') as f:
            json.dump(working_signal, f, indent=2)
        
        print("SUCCESS: Working BCHUSD signal created!")
        print(f"File: {CORRECT_SIGNAL_FILE}")
        print(f"Signal: {working_signal['symbol']} {working_signal['direction']} @ {working_signal['entry_price']}")
        print("\nEA should process this signal within seconds!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def show_solution_summary():
    """Show what needs to be fixed in Python ML/MCP system"""
    
    print("\n" + "=" * 60)
    print("SOLUTION SUMMARY - FIX PYTHON ML/MCP SYSTEM")
    print("=" * 60)
    print()
    print("PROBLEM:")
    print("  After v7, Python ML/MCP system switched to wrong signal files:")
    print("  - mikrobot_signal.json (EA ignores)")
    print("  - m5_pattern_signal.json (EA ignores)")  
    print("  - Various other names (EA ignores)")
    print()
    print("SOLUTION:")
    print("  Update ALL Python ML/MCP files to use:")
    print("  -> mikrobot_fastversion_signal.json")
    print()
    print("FILES TO UPDATE:")
    print("  1. live_signal_trading.py")
    print("  2. signal_based_trading_system.py") 
    print("  3. Any MCP orchestrator signal generators")
    print("  4. ML model signal output files")
    print()
    print("CHANGE:")
    print('  OLD: SIGNAL_FILE = COMMON_PATH / "mikrobot_signal.json"')
    print('  NEW: SIGNAL_FILE = COMMON_PATH / "mikrobot_fastversion_signal.json"')
    print()
    print("LOCATION:")
    print("  D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/")
    print("  (NOT Common/Files/)")
    print("=" * 60)

if __name__ == "__main__":
    # Test the working signal
    success = create_working_bchusd_signal()
    
    # Show the complete solution
    show_solution_summary()
    
    if success:
        print("\nTEST: Working BCHUSD signal sent!")
        print("Check MT5 - EA should execute this trade!")
    else:
        print("\nERROR: Could not send test signal")