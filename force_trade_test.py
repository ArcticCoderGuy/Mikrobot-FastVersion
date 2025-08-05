"""
Force trade test - Luo suora kauppakomento EA:lle
"""

import json
import time
import os

def force_bchusd_trade():
    print("PAKOTETAAN BCHUSD TESTIKAUPPA")
    print("=" * 40)
    
    # Luo suora kauppakomento joka ohittaa 4-vaiheen ja pakottaa kaupan
    trade_command = {
        "command": "EXECUTE_TRADE_NOW",
        "symbol": "BCHUSD",
        "direction": "BUY", 
        "lot_size": 1.0,
        "entry_price": 542.0,
        "stop_loss": 530.0,
        "take_profit": 560.0,
        "strategy": "FORCE_TEST_TRADE",
        "risk_percent": 0.55,
        "confidence": 1.0,
        "timestamp": "2025.08.03 22:55:00",
        "source": "PYTHON_FORCE_TEST",
        "comment": "BCHUSD_FORCE_TEST_TRADE",
        "magic_number": 999888,
        "force_execute": True
    }
    
    # Tallenna useampaan paikkaan varmuuden vuoksi
    files = [
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/python_execution_command.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/force_trade_command.json",
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_trade_signal.json"
    ]
    
    for file_path in files:
        with open(file_path, 'w') as f:
            json.dump(trade_command, f, indent=2)
        print(f"LUOTU: {os.path.basename(file_path)}")
    
    print("\nTEST TRADE CREATED!")
    print("Katso Asiantuntijat-valilehdesta:")
    print("1. Kaupankaynnin aloitus")
    print("2. Kaupat-valilehdesta uusi BCHUSD kauppa")
    print("3. Positiot-valilehdesta avoin positio")
    
    return True

if __name__ == "__main__":
    force_bchusd_trade()