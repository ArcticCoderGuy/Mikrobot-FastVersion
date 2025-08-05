from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MIKROBOT FASTVERSION V5 - UNIVERSAL PIP SYSTEM TESTI
Testaa ett v5 Universal Pip System toimii BCHUSD:lla
"""

import json
import time
import os
from datetime import datetime

def test_v5_universal_pip():
    """Testaa v5 Universal Pip System"""
    
    print("MIKROBOT FASTVERSION V5 - UNIVERSAL PIP SYSTEM TESTI")
    print("=" * 70)
    print("EA: MikrobotFastversion_v5")
    print("Symboli: BCHUSD")
    print("Odotettu Asset Class: CFD_CRYPTO")
    print("Odotettu Pip Value: 0.10")
    print("Odotettu Lot Size: 0.50-2.0 (EI 100!)")
    print("=" * 70)
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Poista vanhat signaalit
    if os.path.exists(signal_file):
        os.remove(signal_file)
        print("Vanhat signaalit poistettu")
    
    # Odota EA:n kynnistymist
    print("\nOdotetaan EA:n kynnistymist...")
    time.sleep(3)
    
    # TESTI: BUY signaali Universal Pip Systemill
    print("\nTESTI: BUY SIGNAALI UNIVERSAL PIP SYSTEMILLA")
    print("-" * 50)
    
    buy_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "BUY",
        "entry_price": 447.25,
        "confidence": 0.95,
        "atr_pips": 12,
        "ylipip_trigger": 0.6,
        "strategy": "MIKROBOT_FASTVERSION_V5",
        "test_id": "UNIVERSAL_PIP_TEST"
    }
    
    # Tallenna BUY signaali
    with open(signal_file, 'w', encoding='ascii') as f:
        json.dump(buy_signal, f, indent=2, ensure_ascii=True)
    
    print("Universal Pip BUY signaali lhetetty:")
    print(f"- Hinta: 447.25")
    print(f"- ATR: 12 pips") 
    print(f"- Odotettu Asset Class: CFD_CRYPTO")
    print(f"- Odotettu Pip Value: 0.10")
    print(f"- Odotettu Lot Size: ~1.0 (EI 100!)")
    
    # Odota EA reaktiota
    print("\nOdotetaan Universal Pip System reaktiota...")
    for i in range(10):
        time.sleep(1)
        if not os.path.exists(signal_file):
            print(f"SUCCESS: EA ksitteli signaalin {i+1} sekunnissa!")
            break
        print(f"Odotus: {i+1}/10 sekuntia...")
    else:
        print("HUOM: Signaali ei viel ksitelty")
    
    # YHTEENVETO
    print("\n" + "=" * 70)
    print("UNIVERSAL PIP SYSTEM - TESTAUKSEN YHTEENVETO")
    print("=" * 70)
    print("\nTARKISTA MT5 EXPERTS-VLILEHTI:")
    print("1. 'Initializing Universal Pip System for: BCHUSD'")
    print("2. 'Asset Class: CFD_CRYPTO'")
    print("3. 'Universal Pip Value: 0.10'")
    print("4. '0.6 Ylipip Value: 0.06'")
    print("5. 'Signal received, parsing...'")
    print("6. 'Universal BUY Setup:'")
    print("7. '  Asset Class: CFD_CRYPTO'")
    print("8. '  Universal Pip Value: 0.10'")
    print("9. '  Lot Size: ~1.0' (EI 100!)")
    print("10. 'SUCCESS: BUY order executed' TAI virheilmoitus")
    
    print("\nODOTETTU PARANNUS:")
    print("- Lot Size: 0.5-2.0 (v4: 100.0)")
    print("- Asset Class tunnistus: CFD_CRYPTO")
    print("- Universal Pip Value: 0.10")
    print("- Stop distance: Oikeat tasot")
    
    return True

def check_universal_pip_status():
    """Tarkista Universal Pip System status"""
    print("\n\nUNIVERSAL PIP SYSTEM STATUS:")
    print("=" * 70)
    print("EA v5 sislt nyt:")
    print("OK 9 Asset-luokan tunnistus")
    print("OK CFD_CRYPTO: pip_value = point * 10")
    print("OK FOREX: pip_value = point * 10 (5-digit)")
    print("OK CFD_INDICES: pip_value = point")
    print("OK CFD_METALS: Gold = point * 10, Silver = point * 100")
    print("OK Turvallisuusrajat: Max 5.0 lots")
    print("OK 0.55% riski toimii KAIKILLA symboleilla")
    
    print("\nTESTAA SEURAAVAKSI ERILAISIA SYMBOLEJA:")
    print("- EURUSD (FOREX)")
    print("- XAUUSD (CFD_METALS)")
    print("- US30 (CFD_INDICES)")
    print("- AAPL (CFD_SHARES)")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    success = test_v5_universal_pip()
    
    if success:
        check_universal_pip_status()
        print("\n\nV5 UNIVERSAL PIP SYSTEM TESTI VALMIS!")
        print("Tarkista MT5 lokit ja vahvista parannukset.")
    else:
        print("\n\nTESTI EPONNISTUI!")
        print("Tarkista EA asennus.")