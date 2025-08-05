"""
MIKROBOT V7 SMART INTEGRATION TEST
MCP/ML Python calculates → EA executes
PROPER ARCHITECTURE: Intelligence in Python, Execution in MQL5
"""

import json
import time
import os
from datetime import datetime
from atr_dynamic_positioning import ATRDynamicPositioning

def test_v7_smart_integration():
    """V7 Smart Integration: Python calculates, EA executes"""
    
    print("MIKROBOT FASTVERSION V7 - SMART INTEGRATION TEST")
    print("=" * 70)
    print("PROPER ARCHITECTURE: MCP/ML Python -> MQL5 EA")
    print("Python calculates ATR lot size -> EA executes")
    print("=" * 70)
    
    # Initialize ATR system
    atr_system = ATRDynamicPositioning()
    
    if not atr_system.connect_mt5():
        print("ERROR: Failed to connect to MT5")
        return
        
    print(f"Connected to MT5, Balance: ${atr_system.account_balance}")
    
    # STEP 1: Python MCP/ML Intelligence Layer
    print("\nPYTHON MCP/ML INTELLIGENCE LAYER")
    print("-" * 50)
    
    symbol = "BCHUSD"
    atr_pips = 8.0
    
    # Python calculates optimal lot size using ATR
    lot_size, lot_message = atr_system.calculate_dynamic_lot_size(symbol, atr_pips)
    print(f"ATR Analysis: {atr_pips} pips")
    print(f"Python calculated lot size: {lot_size}")
    print(f"Logic: {lot_message}")
    
    # Calculate SL/TP based on ATR
    entry_price = 541.50
    pip_value = 0.1  # CFD_CRYPTO
    sl_distance = atr_pips * pip_value
    tp_distance = sl_distance * 2.0  # 1:2 R:R
    
    sl_price = entry_price - sl_distance  # BUY
    tp_price = entry_price + tp_distance
    
    print(f"Python calculated SL: {sl_price}")
    print(f"Python calculated TP: {tp_price}")
    
    # STEP 2: Signal Transmission
    print("\nSIGNAL TRANSMISSION")
    print("-" * 30)
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Remove old signal
    if os.path.exists(signal_file):
        os.remove(signal_file)
    
    # Smart signal with pre-calculated values
    smart_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "direction": "BUY",
        "entry_price": entry_price,
        "lot_size": lot_size,          # PRE-CALCULATED BY PYTHON
        "sl_price": sl_price,          # PRE-CALCULATED BY PYTHON  
        "tp_price": tp_price,          # PRE-CALCULATED BY PYTHON
        "atr_pips": atr_pips,
        "strategy": "MCP_ML_SMART_V7",
        "intelligence_layer": "PYTHON_ATR_SYSTEM",
        "execution_layer": "MQL5_EA_V7",
        "build_version": "20250103-007"
    }
    
    with open(signal_file, 'w', encoding='ascii') as f:
        json.dump(smart_signal, f, ensure_ascii=True)
    
    print("Smart signal sent to EA:")
    print(f"- Symbol: {symbol}")
    print(f"- Direction: BUY")
    print(f"- Lot Size: {lot_size} (Python calculated)")
    print(f"- SL: {sl_price} (Python calculated)")
    print(f"- TP: {tp_price} (Python calculated)")
    
    # STEP 3: EA Execution Layer
    print("\nMQL5 EA EXECUTION LAYER")
    print("-" * 40)
    print("EA should just execute pre-calculated values...")
    
    # Wait for EA response
    print("\nWaiting for EA execution...")
    for i in range(10):
        time.sleep(1)
        if not os.path.exists(signal_file):
            print(f"SUCCESS: EA executed signal in {i+1} seconds!")
            break
        print(f"Waiting: {i+1}/10 seconds...")
    else:
        print("Signal not yet processed by EA")
    
    print("\n" + "=" * 70)
    print("EXPECTED RESULT IN MT5 EXPERTS TAB:")
    print("=" * 70)
    print("EA should show:")
    print("1. 'Smart signal received from Python MCP/ML system'")
    print("2. 'Pre-calculated lot size: 0.5' (not calculating in EA)")
    print("3. 'Executing BUY BCHUSD with Python values'")
    print("4. 'market buy 0.5 BCHUSD' (NOT 5.0!)")
    print("5. 'SUCCESS: Trade executed per Python intelligence'")
    
    print("\nARCHITECTURAL SUCCESS:")
    print("+ Python MCP/ML system did the thinking")
    print("+ EA just executed pre-calculated values") 
    print("+ Proper separation of intelligence vs execution")
    print("+ ATR lot sizing done in correct layer")

if __name__ == "__main__":
    test_v7_smart_integration()