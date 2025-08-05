"""
TESTAA V5 BCHUSD KORJAUS
Tarkista että BCHUSD tunnistetaan nyt CFD_CRYPTO:ksi
"""

import json
import time
import os
from datetime import datetime

def test_bchusd_classification():
    """Testaa BCHUSD luokittelu korjaus"""
    
    print("TESTAA V5 BCHUSD ASSET CLASSIFICATION KORJAUS")
    print("=" * 60)
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Poista vanhat signaalit
    if os.path.exists(signal_file):
        os.remove(signal_file)
    
    # Luo testisignaali BCHUSD tunnistusta varten
    test_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5", 
        "signal_type": "M5_BOS",
        "direction": "BUY",
        "entry_price": 448.50,
        "test": "BCHUSD_CLASSIFICATION_TEST"
    }
    
    with open(signal_file, 'w', encoding='ascii') as f:
        json.dump(test_signal, f, ensure_ascii=True)
    
    print("BCHUSD klassifiointitesti signaali lähetetty")
    print("\nOdotetaan EA:n reaktiota...")
    
    # Odota EA reaktiota
    for i in range(8):
        time.sleep(1)
        if not os.path.exists(signal_file):
            print(f"EA käsitteli signaalin {i+1} sekunnissa!")
            break
        print(f"Odotus: {i+1}/8...")
    else:
        print("Signaali ei vielä käsitelty")
    
    print("\n" + "=" * 60)
    print("TARKISTA MT5 EXPERTS-VÄLILEHTI:")
    print("=" * 60)
    print("\nODOTETTU KORJAUS:")
    print("ENNEN: Asset Class: CFD_SHARES")
    print("JÄLKEEN: Asset Class: CFD_CRYPTO")
    print("\nODOTETTU PIP VALUE:")
    print("ENNEN: Universal Pip Value: 1.0") 
    print("JÄLKEEN: Universal Pip Value: 0.10")
    
    print("\nEDOTETTU LOT SIZE:")
    print("V4: ~100 lots (liian iso)")
    print("V5: ~1.0 lots (oikea koko)")
    
    print("\nETSI NÄITÄ VIESTEJÄ:")
    print("1. 'CRYPTO pattern found: BCH in BCHUSD'")  
    print("2. 'Asset Class: CFD_CRYPTO'")
    print("3. 'Universal Pip Value: 0.10'")
    print("4. 'Universal BUY Setup:'")
    print("5. 'Lot Size: ~1.0' (ei 100!)")

if __name__ == "__main__":
    test_bchusd_classification()