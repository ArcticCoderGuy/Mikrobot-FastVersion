"""
MIKROBOT V7 ATR INTEGRATION TEST
Tarkista että v7 käyttää ATR Dynamic Positioning -systeemiä
"""

import json
import time
import os
from datetime import datetime

def test_v7_atr_integration():
    """V7 ATR integration testi"""
    
    print("MIKROBOT FASTVERSION V7 - ATR DYNAMIC POSITIONING TEST")
    print("=" * 70)
    print("BUILD: 20250103-007 - ATR DYNAMIC POSITIONING INTEGRATED")
    print("Odotettu tulos:")
    print("- DIRECT MATCH: BCHUSD -> CFD_CRYPTO")
    print("- Asset Class: CFD_CRYPTO") 
    print("- Universal Pip Value: 0.10")
    print("- ATR Dynamic Lot Size: ~0.5-1.0 (EI 5.0!)")
    print("- ATR-based SL/TP calculation")
    print("=" * 70)
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Poista vanhat signaalit
    if os.path.exists(signal_file):
        os.remove(signal_file)
    
    # Odota EA:n käynnistymistä
    print("\nOdotetaan v7 EA:n käynnistymistä...")
    time.sleep(5)
    
    # V7 ATR INTEGRATION TEST: BUY signaali
    print("\nV7 ATR INTEGRATION TEST: BCHUSD BUY SIGNAALI")
    print("-" * 55)
    
    v7_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS", 
        "direction": "BUY",
        "entry_price": 541.50,
        "confidence": 0.98,
        "atr_pips": 8,
        "ylipip_trigger": 0.6,
        "strategy": "MIKROBOT_V7_ATR_TEST",
        "test_id": "BCHUSD_ATR_DYNAMIC",
        "build_version": "20250103-007"
    }
    
    with open(signal_file, 'w', encoding='ascii') as f:
        json.dump(v7_signal, f, ensure_ascii=True)
    
    print("V7 ATR signaali lähetetty:")
    print(f"- Symbol: BCHUSD")
    print(f"- Direction: BUY") 
    print(f"- Price: 541.50")
    print(f"- ATR: 8 pips")
    print(f"- Build: 20250103-007")
    
    # Odota reaktiota
    print("\nOdotetaan v7 ATR integration tunnistusta...")
    for i in range(10):
        time.sleep(1)
        if not os.path.exists(signal_file):
            print(f"SUCCESS: v7 käsitteli signaalin {i+1} sekunnissa!")
            break
        print(f"Odotus: {i+1}/10 sekuntia...")
    else:
        print("Signaali ei vielä käsitelty")
    
    print("\n" + "=" * 70)
    print("V7 ATR INTEGRATION TARKISTUS - ODOTETUT VIESTIT:")
    print("=" * 70)
    print("1. 'BUILD: 20250103-007 - ATR DYNAMIC POSITIONING INTEGRATED'")
    print("2. 'ClassifyAssetFixed: Processing symbol: BCHUSD'")
    print("3. 'DIRECT MATCH: BCHUSD -> CFD_CRYPTO'")
    print("4. 'Asset Class: CFD_CRYPTO'")
    print("5. 'Universal Pip Value: 0.10'")
    print("6. 'ATR Dynamic Positioning: ENABLED'")
    print("7. 'ATR Validation: 8.0 pips (VALID - within 4-15 range)'")
    print("8. 'Dynamic Lot Calculation: Risk 0.55%, Balance $98998'")
    print("9. 'ATR Dynamic Lot Size: 0.5' (EI 5.0!)")
    print("10. 'Universal BUY Setup v7:'")
    print("11. '  Asset Class: CFD_CRYPTO'")
    print("12. '  ATR Dynamic Lot: 0.5'")
    print("13. '  SL Distance: 8 pips (ATR-based)'")
    print("14. 'SUCCESS: BUY order executed with ATR positioning'")
    
    print("\nJOS NAET YLLA OLEVAT VIESTIT:")
    print("SUCCESS: V7 ATR INTEGRATION TOIMII!")
    print("SUCCESS: BCHUSD lot-koko korjattu: 0.5 (ei 5.0)")
    print("SUCCESS: ATR Dynamic Positioning AKTIIVINEN!")
    print("SUCCESS: Universal Pip System + ATR = VALMIS!")

if __name__ == "__main__":
    test_v7_atr_integration()