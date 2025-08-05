"""
Simulate ylipip trigger reaching target to test Phase 4
"""

import time
import json
import os

def simulate_phase4_trigger():
    print("SIMULOIDAAN VAIHE 4 - 0.6 YLIPIP TRIGGER")
    print("=" * 60)
    
    # Luo signaalitiedosto joka simuloi Phase 4:n laukaisua
    signal_data = {
        "timestamp": "2025.08.03 22:47:00",
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
            "current": 542.175,  # Ylittää tason!
            "triggered": True
        },
        "trade_direction": "BULL",
        "current_price": 542.175,
        "ylipip_trigger": 0.6,
        "source": "MIKROBOT_FASTVERSION_COMPLIANT_v8", 
        "intelligence_needed": "PYTHON_MCP_ML_ATR_RISK",
        "build_version": "20250103-008F"
    }
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json"
    
    with open(signal_file, 'w') as f:
        json.dump(signal_data, f, indent=2)
    
    print(f"Phase 4 signaali luotu: {signal_file}")
    print(f"Hinta 542.175 ylittaa ylipip-tason 542.17006!")
    
    # Odota hetki ja luo Python-kaupankäyntikomento
    time.sleep(2)
    
    trade_command = {
        "command": "EXECUTE_TRADE",
        "symbol": "BCHUSD",
        "direction": "BUY", 
        "lot_size": 1.0,
        "entry_price": 542.175,
        "stop_loss": 534.175,
        "take_profit": 562.175,
        "strategy": "MIKROBOT_FASTVERSION_4PHASE",
        "risk_percent": 0.55,
        "atr_calculated": 8.0,
        "confidence": 0.92,
        "timestamp": "2025.08.03 22:47:15",
        "source": "PYTHON_MCP_ML_INTELLIGENCE",
        "comment": "MIKROBOT_4PHASE_TESTIKAUPPA_SIMULAATIO"
    }
    
    command_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/python_execution_command.json"
    
    with open(command_file, 'w') as f:
        json.dump(trade_command, f, indent=2)
        
    print(f"Python-kauppakomento luotu: {command_file}")
    print("EA pitaisi nyt suorittaa testikauppa!")
    
    print("\nSeuraa Asiantuntijat-valilehtea nahdaksesi:")
    print("1. PHASE 4 COMPLETE viesti")
    print("2. SENDING PYTHON SIGNAL viesti") 
    print("3. EXECUTING PYTHON CALCULATED TRADE viesti")
    print("4. Uusi kauppa Kaupat-välilehdessä")

if __name__ == "__main__":
    simulate_phase4_trigger()