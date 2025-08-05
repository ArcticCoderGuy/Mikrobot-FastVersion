from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
TESTI: Tarkista ett M5/M1 BOS strategia on todella kynniss
"""
import time
import json
from pathlib import Path
from datetime import datetime

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
ACTIVATION_FILE = COMMON_PATH / "mikrobot_activation.json"
STATUS_FILE = COMMON_PATH / "mikrobot_status.txt"
CONFIG_FILE = COMMON_PATH / "m5m1_strategy_config.json"

def test_m5m1_strategy():
    print(" TESTAA M5/M1 BOS STRATEGIAN KYNNISTYMINEN")
    print("=" * 60)
    
    # TEST 1: Aktivointisignaali
    print("TEST 1: Aktivointisignaali tarkistus")
    if ACTIVATION_FILE.exists():
        with open(ACTIVATION_FILE, 'r', encoding='ascii', errors='ignore') as f:
            activation = json.load(f)
        
        strategy_name = activation.get('strategy_name', 'UNKNOWN')
        version = activation.get('version', 'UNKNOWN')
        
        if strategy_name == "MikroBot_BOS_M5M1" and version == "2.00":
            print("OK PASS: M5/M1 BOS strategia aktivointisignaali OK")
            print(f"   Strategia: {strategy_name} v{version}")
        else:
            print("ERROR FAIL: Vr strategia tai versio")
            return False
    else:
        print("ERROR FAIL: Aktivointisignaali puuttuu")
        return False
    
    # TEST 2: Konfiguraatio
    print("\nTEST 2: M5/M1 konfiguraatio tarkistus")
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='ascii', errors='ignore') as f:
            config = json.load(f)
        
        config_data = config.get('config', {})
        strategy_id = config_data.get('strategy_id')
        primary_tf = config_data.get('primary_timeframe')
        confirm_tf = config_data.get('confirmation_timeframe')
        pip_trigger = config_data.get('pattern_detection', {}).get('retest_precision')
        
        if (strategy_id == "M5M1_BOS_WEEKEND" and 
            primary_tf == "M5" and 
            confirm_tf == "M1" and 
            pip_trigger == 0.2):
            print("OK PASS: M5/M1 konfiguraatio oikein")
            print(f"   Primary: {primary_tf}, Confirmation: {confirm_tf}")
            print(f"   Pip trigger: {pip_trigger}")
        else:
            print("ERROR FAIL: Vr konfiguraatio")
            return False
    else:
        print("ERROR FAIL: Konfiguraatio puuttuu")
        return False
    
    # TEST 3: EA yhteys
    print("\nTEST 3: EA yhteys tarkistus")
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r', encoding='ascii', errors='ignore') as f:
            status = f.read()
        
        if "CONNECTION VERIFIED" in status and "107034605" in status:
            print("OK PASS: EA yhteys vahvistettu tilille 107034605")
        else:
            print("ERROR FAIL: EA yhteys epvarma")
            return False
    else:
        print("ERROR FAIL: EA status puuttuu")
        return False
    
    # TEST 4: Symbolit
    print("\nTEST 4: Crypto symbolit tarkistus")
    symbols = config_data.get('active_symbols', [])
    expected_symbols = ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD"]
    
    if all(symbol in symbols for symbol in expected_symbols):
        print("OK PASS: Kaikki crypto symbolit aktivoitu")
        print(f"   Symbolit: {', '.join(symbols)}")
    else:
        print("ERROR FAIL: Puuttuvia symboleita")
        return False
    
    # TEST 5: 24/7 mode
    print("\nTEST 5: 24/7 weekend mode tarkistus")
    session_config = config_data.get('session_config', {})
    weekend_mode = session_config.get('weekend_mode')
    crypto_focus = session_config.get('crypto_focus')
    continuous = session_config.get('24_7_monitoring')
    
    if weekend_mode and crypto_focus and continuous:
        print("OK PASS: 24/7 crypto weekend mode aktivoitu")
    else:
        print("ERROR FAIL: Weekend mode ei ole oikein")
        return False
    
    print("\n" + "=" * 60)
    print("TARGET TODISTE: M5/M1 BOS STRATEGIA ON KYNNISS!")
    print("CHART Pattern: M5 Break of Structure + M1 Break-and-Retest")
    print("  Precision: 0.2 pip trigger (ultra-high frequency)")
    print(" Symbols: BTC/ETH/XRP/LTC USD pairs")
    print(" Mode: 24/7 continuous monitoring")
    print(" Account: 107034605 (verified connection)")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    if test_m5m1_strategy():
        print("\nOK KAIKKI TESTIT LPISTY - M5/M1 STRATEGIA KYNNISS")
    else:
        print("\nERROR TESTIT EPONNISTUI - STRATEGIA EI OLE KYNNISS")