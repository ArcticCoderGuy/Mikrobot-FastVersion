"""
MIKROBOT V6 LOPULLINEN BCHUSD TESTI
Tarkista että v6 tunnistaa BCHUSD oikein CFD_CRYPTO:ksi
"""

import json
import time
import os
from datetime import datetime

def test_v6_final():
    """Lopullinen v6 testi"""
    
    print("MIKROBOT FASTVERSION V6 - LOPULLINEN BCHUSD TESTI")
    print("=" * 65)
    print("BUILD: 20250103-006 - BCHUSD CRYPTO DETECTION FIXED")
    print("Odotettu tulos:")
    print("- DIRECT MATCH: BCHUSD -> CFD_CRYPTO")
    print("- Asset Class: CFD_CRYPTO") 
    print("- Universal Pip Value: 0.10 (EI 1.0!)")
    print("- Lot Size: ~1.0 (EI 100!)")
    print("=" * 65)
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Poista vanhat signaalit
    if os.path.exists(signal_file):
        os.remove(signal_file)
    
    # Odota EA:n käynnistymistä
    print("\nOdotetaan v6 EA:n käynnistymistä...")
    time.sleep(5)
    
    # LOPULLINEN TESTI: BUY signaali
    print("\nLOPULLINEN TESTI: BCHUSD BUY SIGNAALI")
    print("-" * 50)
    
    final_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS", 
        "direction": "BUY",
        "entry_price": 449.75,
        "confidence": 0.98,
        "atr_pips": 8,
        "ylipip_trigger": 0.6,
        "strategy": "MIKROBOT_V6_FINAL_TEST",
        "test_id": "BCHUSD_CRYPTO_FIXED"
    }
    
    with open(signal_file, 'w', encoding='ascii') as f:
        json.dump(final_signal, f, ensure_ascii=True)
    
    print("V6 FINAL signaali lähetetty:")
    print(f"- Symbol: BCHUSD")
    print(f"- Direction: BUY") 
    print(f"- Price: 449.75")
    print(f"- ATR: 8 pips")
    
    # Odota reaktiota
    print("\nOdotetaan v6 BCHUSD tunnistusta...")
    for i in range(8):
        time.sleep(1)
        if not os.path.exists(signal_file):
            print(f"SUCCESS: v6 käsitteli signaalin {i+1} sekunnissa!")
            break
        print(f"Odotus: {i+1}/8 sekuntia...")
    else:
        print("Signaali ei vielä käsitelty")
    
    print("\n" + "=" * 65)
    print("V6 LOPULLINEN TARKISTUS - ODOTETUT VIESTIT:")
    print("=" * 65)
    print("1. 'BUILD: 20250103-006 - BCHUSD CRYPTO DETECTION FIXED'")
    print("2. 'ClassifyAssetFixed: Processing symbol: BCHUSD'")
    print("3. 'DIRECT MATCH: BCHUSD -> CFD_CRYPTO'")
    print("4. 'Asset Class: CFD_CRYPTO' (EI CFD_SHARES!)")
    print("5. 'Universal Pip Value: 0.10' (EI 1.0!)")
    print("6. 'CRYPTO OTHER (BCH): pip_value = point * 10 = 0.10'")
    print("7. 'Universal BUY Setup v6:'")
    print("8. '  Asset Class: CFD_CRYPTO'")
    print("9. '  Lot Size: ~1.0' (EI 100 TAI 5!)")
    print("10. 'SUCCESS: BUY order executed'")
    
    print("\nJOS NAET YLLA OLEVAT VIESTIT:")
    print("SUCCESS: V6 TOIMII TAYDELLISESTI!")
    print("SUCCESS: BCHUSD tunnistetaan CFD_CRYPTO:ksi")
    print("SUCCESS: Pip value on oikea: 0.10")
    print("SUCCESS: Lot size on jarkeva: ~1.0")
    print("SUCCESS: Universal Pip System VALMIS!")

if __name__ == "__main__":
    test_v6_final()