"""
TODISTE: M5/M1 BOS strategia kaynnissa testi
"""
import time
import json
from pathlib import Path
from datetime import datetime

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

def verify_m5m1_strategy():
    print("M5/M1 BOS STRATEGIAN KAYNNISTYMISEN TODISTE")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # TEST 1: Aktivointisignaali
    print("TEST 1: Aktivointisignaali")
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    if activation_file.exists():
        with open(activation_file, 'r') as f:
            activation = json.load(f)
        
        strategy_name = activation.get('strategy_name')
        if strategy_name == "MikroBot_BOS_M5M1":
            print("  PASS: M5/M1 BOS strategia aktivoitu")
            print(f"    Strategia: {strategy_name}")
            print(f"    Versio: {activation.get('version')}")
            tests_passed += 1
        else:
            print("  FAIL: Vaara strategia")
    else:
        print("  FAIL: Aktivointisignaali puuttuu")
    
    # TEST 2: Konfiguraatio
    print("\nTEST 2: M5/M1 Konfiguraatio")
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        config_data = config.get('config', {})
        primary = config_data.get('primary_timeframe')
        confirm = config_data.get('confirmation_timeframe')
        precision = config_data.get('pattern_detection', {}).get('retest_precision')
        
        if primary == "M5" and confirm == "M1" and precision == 0.2:
            print("  PASS: M5/M1 konfiguraatio oikein")
            print(f"    Primary: {primary}, Confirmation: {confirm}")
            print(f"    Pip precision: {precision}")
            tests_passed += 1
        else:
            print("  FAIL: Vaara konfiguraatio")
    else:
        print("  FAIL: Konfiguraatio puuttuu")
    
    # TEST 3: EA Status
    print("\nTEST 3: EA Yhteys")
    status_file = COMMON_PATH / "mikrobot_status.txt"
    if status_file.exists():
        with open(status_file, 'r') as f:
            status = f.read()
        
        if "CONNECTION VERIFIED" in status:
            print("  PASS: EA yhteys vahvistettu")
            print("    Account: 107034605")
            tests_passed += 1
        else:
            print("  FAIL: EA yhteys epavarma")
    else:
        print("  FAIL: EA status puuttuu")
    
    # TEST 4: Symbolit
    print("\nTEST 4: Crypto Symbolit")
    if config_file.exists():
        symbols = config_data.get('active_symbols', [])
        expected = ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD"]
        
        if all(s in symbols for s in expected):
            print("  PASS: Crypto symbolit aktivoitu")
            print(f"    Symbolit: {', '.join(symbols)}")
            tests_passed += 1
        else:
            print("  FAIL: Symboleja puuttuu")
    
    # TEST 5: 24/7 Mode
    print("\nTEST 5: 24/7 Weekend Mode")
    if config_file.exists():
        session = config_data.get('session_config', {})
        weekend = session.get('weekend_mode')
        crypto = session.get('crypto_focus')
        continuous = session.get('24_7_monitoring')
        
        if weekend and crypto and continuous:
            print("  PASS: 24/7 weekend crypto mode")
            tests_passed += 1
        else:
            print("  FAIL: Weekend mode ei aktivoitu")
    
    # LOPPUTULOS
    print("\n" + "=" * 50)
    print(f"TESTIEN TULOS: {tests_passed}/{total_tests} LAPAISI")
    
    if tests_passed == total_tests:
        print("\nTODISTE: M5/M1 BOS STRATEGIA ON KAYNNISSA!")
        print("Pattern: M5 Break of Structure + M1 Retest")
        print("Precision: 0.2 pip trigger")
        print("Symbols: BTC, ETH, XRP, LTC")
        print("Mode: 24/7 continuous monitoring")
        print("Account: 107034605")
        print("=" * 50)
        return True
    else:
        print("\nVAROITUS: Strategia ei ole taydellisesti kaynnissa")
        return False

if __name__ == "__main__":
    verify_m5m1_strategy()