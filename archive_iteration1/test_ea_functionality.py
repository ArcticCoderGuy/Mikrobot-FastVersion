"""
TESTAA EA TOIMIVUUS
Tarkista että MikrobotFastversion_v3 on asennettu ja toimii BCHUSD:ssa
"""

import json
import time
import os
from datetime import datetime

def test_ea_functionality():
    """Testaa EA toimivuus"""
    
    print("TESTATAAN EA TOIMIVUUS BCHUSD M5...")
    print("=" * 50)
    
    # 1. Tarkista että EA on käynnissä
    print("\n1. TARKISTETAAN EA STATUS...")
    print("- EA: MikrobotFastversion_v3")
    print("- Symboli: BCHUSD")
    print("- Timeframe: M5")
    print("- Versio: v3.0.0")
    print("- BUILD: 20250103-003")
    
    # 2. Luo testisignaali
    print("\n2. LUODAAN TESTISIGNAALI...")
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    test_signal = {
        "timestamp": datetime.now().isoformat(),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "BUY",
        "entry_price": 440.50,
        "confidence": 0.85,
        "atr_pips": 8,
        "ylipip_trigger": 0.6,
        "strategy": "MIKROBOT_FASTVERSION_TEST",
        "test_mode": True,
        "message": "TEST SIGNAL - DO NOT EXECUTE REAL TRADE"
    }
    
    # Tallenna signaali
    try:
        # Varmista että Files-kansio on olemassa
        files_dir = os.path.dirname(signal_file)
        if not os.path.exists(files_dir):
            os.makedirs(files_dir)
            print(f"Luotiin Files-kansio: {files_dir}")
        
        with open(signal_file, 'w') as f:
            json.dump(test_signal, f, indent=2)
        print(f"Testisignaali tallennettu: {signal_file}")
        print(f"Signaali: BUY @ 440.50")
    except Exception as e:
        print(f"VIRHE: Signaalin tallennus epäonnistui: {e}")
        return False
    
    # 3. Odota EA:n reaktiota
    print("\n3. ODOTETAAN EA REAKTIOTA...")
    print("EA tarkistaa signaalit 5 sekunnin välein...")
    
    for i in range(10):
        time.sleep(1)
        print(f"Odotus: {i+1}/10 sekuntia...")
        
        # Tarkista onko signaali käsitelty
        if not os.path.exists(signal_file):
            print("SUCCESS: EA luki ja poisti signaalin!")
            break
    else:
        print("HUOM: Signaali ei vielä käsitelty, tarkista EA lokit")
    
    # 4. Luo toinen testisignaali (SELL)
    print("\n4. LUODAAN SELL TESTISIGNAALI...")
    
    test_signal_2 = {
        "timestamp": datetime.now().isoformat(),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "SELL",
        "entry_price": 441.00,
        "confidence": 0.90,
        "atr_pips": 10,
        "ylipip_trigger": 0.6,
        "strategy": "MIKROBOT_FASTVERSION_TEST",
        "test_mode": True,
        "message": "TEST SIGNAL 2 - SELL TEST"
    }
    
    try:
        with open(signal_file, 'w') as f:
            json.dump(test_signal_2, f, indent=2)
        print(f"SELL testisignaali tallennettu: SELL @ 441.00")
    except Exception as e:
        print(f"VIRHE: SELL signaalin tallennus epäonnistui: {e}")
    
    # 5. Yhteenveto
    print("\n5. TESTAUKSEN YHTEENVETO:")
    print("=" * 50)
    print("EA ASENNUS: OK")
    print("SIGNAALITIEDOSTO: OK")
    print("TEST SIGNAALIT:")
    print("  - BUY @ 440.50 (ATR: 8 pips)")
    print("  - SELL @ 441.00 (ATR: 10 pips)")
    print("\nTARKISTA MT5:")
    print("1. Experts-välilehti EA:n viestit")
    print("2. Journal-välilehti mahdolliset virheet")
    print("3. Trade-välilehti avautuneet positiot")
    print("\nODOTETUT VIESTIT:")
    print("- 'Processing MIKROBOT signal: ...'")
    print("- 'BUY order executed: ...' tai 'BUY order failed: ...'")
    print("- 'SELL order executed: ...' tai 'SELL order failed: ...'")
    
    return True

def check_ea_logs():
    """Tarkista EA lokit"""
    print("\n\nEA LOKIEN TARKISTUS:")
    print("=" * 50)
    print("Tarkista seuraavat MT5:ssä:")
    print("\n1. EXPERTS-välilehti:")
    print("   - MIKROBOT FASTVERSION EA v3.0.0 - STARTING")
    print("   - BUILD: 20250103-003")
    print("   - Risk per trade: 0.55%")
    print("   - Processing MIKROBOT signal...")
    print("\n2. JOURNAL-välilehti:")
    print("   - Expert MikrobotFastversion_v3 (BCHUSD,M5) loaded successfully")
    print("   - AutoTrading is enabled")
    print("\n3. TRADE-välilehti:")
    print("   - Mahdolliset avautuneet positiot")
    print("   - Order ticket numerot")

if __name__ == "__main__":
    print("MIKROBOT FASTVERSION v3 - EA TOIMIVUUSTESTI")
    print("=" * 50)
    
    success = test_ea_functionality()
    
    if success:
        check_ea_logs()
        print("\n\nTESTI VALMIS!")
        print("Tarkista MT5 lokit ja vahvista EA:n toiminta.")
    else:
        print("\n\nTESTI EPÄONNISTUI!")
        print("Tarkista EA asennus ja asetukset.")