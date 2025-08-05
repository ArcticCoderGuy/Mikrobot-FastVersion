"""
Direct trade test - Create signal that EA should process
"""

import json
import time
import os

def create_direct_trade_signal():
    print("LUODAAN SUORA KAUPANKÄYNTISIGNAALI EALLE")
    print("=" * 50)
    
    # Simuloi että EA olisi itse lähettänyt tämän Phase 4 signaalin
    signal_data = {
        "timestamp": "2025.08.03 22:50:00",
        "symbol": "BCHUSD", 
        "strategy": "MIKROBOT_FASTVERSION_4PHASE",
        "phase_1_m5_bos": {
            "time": "2025.08.03 19:35",
            "price": 542.17,
            "direction": "BULL"
        },
        "phase_2_m1_break": {
            "time": "2025.08.03 19:37",
            "price": 542.17
        },
        "phase_3_m1_retest": {
            "time": "2025.08.03 19:38", 
            "price": 542.12
        },
        "phase_4_ylipip": {
            "target": 542.17006,
            "current": 542.18,
            "triggered": True
        },
        "trade_direction": "BULL",
        "current_price": 542.18,
        "ylipip_trigger": 0.6,
        "source": "MIKROBOT_FASTVERSION_COMPLIANT_v8",
        "intelligence_needed": "PYTHON_MCP_ML_ATR_RISK",
        "build_version": "20250103-008F"
    }
    
    # Tallenna signaalitiedosto
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json"
    with open(signal_file, 'w') as f:
        json.dump(signal_data, f, indent=2)
    
    print(f"SIGNAALI LUOTU: {signal_file}")
    
    # Pieni tauko
    time.sleep(1)
    
    # Luo Python-vastauskäsky kauppaa varten
    trade_response = {
        "command": "EXECUTE_TRADE",
        "symbol": "BCHUSD",
        "direction": "BUY",
        "lot_size": 1.0,
        "entry_price": 542.18,
        "stop_loss": 534.18,
        "take_profit": 562.18,
        "strategy": "MIKROBOT_FASTVERSION_4PHASE", 
        "risk_percent": 0.55,
        "atr_calculated": 8.0,
        "confidence": 0.95,
        "timestamp": "2025.08.03 22:50:05",
        "source": "PYTHON_MCP_ML_INTELLIGENCE",
        "comment": "MIKROBOT_4PHASE_DIRECT_TEST"
    }
    
    # Tallenna kaupankäyntikäsky
    command_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/python_execution_command.json"
    with open(command_file, 'w') as f:
        json.dump(trade_response, f, indent=2)
    
    print(f"KAUPANKÄYNTIKOMENTO LUOTU: {command_file}")
    print("")
    print("NOPEA TESTI - Katso Asiantuntijat-välilehteä:")
    print("1. EA pitäisi havaita Phase 4 signaalin")
    print("2. EA pitäisi suorittaa Python-kaupan")
    print("3. Uusi kauppa pitäisi näkyä Kaupat-välilehdessä")
    
    return True

if __name__ == "__main__":
    create_direct_trade_signal()