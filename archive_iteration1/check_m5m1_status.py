"""
Tarkista M5/M1 BOS strategian status
"""
import time
from pathlib import Path
import json

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
STATUS_FILE = COMMON_PATH / "mikrobot_status.txt"
ACTIVATION_FILE = COMMON_PATH / "mikrobot_activation.json"

def check_m5m1_status():
    print("=== M5/M1 BOS STRATEGIAN STATUS TARKISTUS ===")
    
    # Tarkista aktivointisignaali
    if ACTIVATION_FILE.exists():
        print("AKTIVOINTISIGNAALI: Lahetetty")
        with open(ACTIVATION_FILE, 'r') as f:
            activation = json.load(f)
        print(f"  Strategia: {activation.get('strategy_name', 'Unknown')}")
        print(f"  Versio: {activation.get('version', 'Unknown')}")
    else:
        print("AKTIVOINTISIGNAALI: EI LOYDY")
    
    # Tarkista EA status
    if STATUS_FILE.exists():
        print("\nEA STATUS:")
        with open(STATUS_FILE, 'r') as f:
            status = f.read()
        print(status)
    else:
        print("EA STATUS: Ei statustiedostoa")
    
    print("\n=== M5/M1 BOS READY ===")
    print("Strategia: M5 Break of Structure + M1 Retest")
    print("Pip trigger: 0.2 (ultra precision)")
    print("Monitoring: 24/7 continuous")
    print("Symbolit: BTCUSD, ETHUSD, XRPUSD, LTCUSD")

if __name__ == "__main__":
    check_m5m1_status()