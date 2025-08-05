"""
LAHETA PUHDAS TESTISIGNAALI
Korjaa merkisto-ongelmat ja laheta selkea signaali
"""

import json
import os
from datetime import datetime

def send_clean_signal():
    """Laheta puhdas ASCII-signaali"""
    
    print("LAHETETAAN PUHDAS TESTISIGNAALI...")
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Yksinkertainen, puhdas signaali
    clean_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "BUY",
        "entry_price": 442.50,
        "confidence": 0.88,
        "atr_pips": 9,
        "ylipip_trigger": 0.6,
        "strategy": "MIKROBOT_FASTVERSION",
        "test": "CLEAN_SIGNAL_TEST"
    }
    
    try:
        # Kirjoita ASCII-muodossa
        with open(signal_file, 'w', encoding='ascii') as f:
            json.dump(clean_signal, f, indent=2, ensure_ascii=True)
        
        print("SUCCESS: Puhdas signaali lahetetty!")
        print(f"Tiedosto: {signal_file}")
        print(f"Signaali: BUY @ 442.50")
        print("\nSignaalin sisalto:")
        print(json.dumps(clean_signal, indent=2, ensure_ascii=True))
        
    except Exception as e:
        print(f"VIRHE: {e}")
        return False
    
    return True

def clear_old_signals():
    """Poista vanhat signaalit"""
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    if os.path.exists(signal_file):
        try:
            os.remove(signal_file)
            print("Vanha signaali poistettu")
        except:
            pass

if __name__ == "__main__":
    print("MIKROBOT PUHDAS SIGNAALI TESTI")
    print("=" * 50)
    
    # Poista vanhat signaalit ensin
    clear_old_signals()
    
    # Laheta uusi puhdas signaali
    if send_clean_signal():
        print("\nOdota 5 sekuntia ja tarkista MT5 Experts-valilehti")
        print("Pitaisi nahda selkea viesti ilman kiinaa!")