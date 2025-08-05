"""
Test v3 EA with direct trade signal
"""

import json
import time
from datetime import datetime

def create_v3_trade_signal():
    """Create a trade signal that v3 EA can execute directly"""
    
    print("Creating v3 EA trade signal for BCHUSD")
    print("=" * 50)
    
    # v3 EA expects signals in the mikrobot_fastversion_signal.json format
    signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "signal_type": "EXECUTE",  # v3 can execute directly
        "direction": "BUY",
        "entry_price": 542.15,
        "stop_loss": 530.0,  # ~12 pip SL
        "take_profit": 560.0,  # ~18 pip TP
        "lot_size": 1.0,  # 1 lot for BCHUSD CFD_CRYPTO
        "atr_pips": 8,
        "confidence": 0.95,
        "source": "V3_TEST",
        "comment": "V3_BCHUSD_TEST_TRADE",
        "magic_number": 123456
    }
    
    # Write to the signal file
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_fastversion_signal.json"
    
    with open(signal_file, 'w') as f:
        json.dump(signal, f, indent=2)
    
    print(f"Signal created: {signal_file}")
    print(f"Signal details:")
    print(f"  Symbol: {signal['symbol']}")
    print(f"  Direction: {signal['direction']}")
    print(f"  Entry: {signal['entry_price']}")
    print(f"  SL: {signal['stop_loss']}")
    print(f"  TP: {signal['take_profit']}")
    print(f"  Lot: {signal['lot_size']}")
    
    print("\nMonitor MT5 Experts tab for trade execution!")
    
    # Also create a backup signal file
    backup_signal = signal.copy()
    backup_signal["force_execute"] = True
    
    backup_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/v3_execute_trade.json"
    with open(backup_file, 'w') as f:
        json.dump(backup_signal, f, indent=2)
    
    print(f"Backup signal created: {backup_file}")
    
    return True

if __name__ == "__main__":
    create_v3_trade_signal()
    print("\nWaiting for v3 EA to process signal...")
    time.sleep(5)
    print("Check MT5 Experts and Journal tabs for activity!")