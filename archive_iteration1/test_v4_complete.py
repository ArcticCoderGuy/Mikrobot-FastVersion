"""
MIKROBOT FASTVERSION V4 - LOPULLINEN TESTI
Testaa että v4 EA toimii 100% BCHUSD M5:llä
"""

import json
import time
import os
from datetime import datetime

def test_v4_functionality():
    """Testaa v4 EA toimivuus"""
    
    print("MIKROBOT FASTVERSION V4 - TOIMIVUUSTESTI")
    print("=" * 60)
    print("EA: MikrobotFastversion_v4")
    print("Symboli: BCHUSD")
    print("Timeframe: M5")
    print("BUILD: 20250103-004")
    print("=" * 60)
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Poista vanhat signaalit
    if os.path.exists(signal_file):
        os.remove(signal_file)
        print("Vanhat signaalit poistettu")
    
    # TESTI 1: BUY signaali
    print("\nTESTI 1: BUY SIGNAALI")
    print("-" * 40)
    
    buy_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "BUY",
        "entry_price": 443.75,
        "confidence": 0.92,
        "atr_pips": 10,
        "ylipip_trigger": 0.6,
        "strategy": "MIKROBOT_FASTVERSION",
        "test_id": "V4_TEST_001"
    }
    
    # Tallenna BUY signaali
    with open(signal_file, 'w', encoding='ascii') as f:
        json.dump(buy_signal, f, indent=2, ensure_ascii=True)
    
    print("BUY signaali lahetetty:")
    print(f"- Hinta: 443.75")
    print(f"- ATR: 10 pips")
    print(f"- Confidence: 92%")
    
    # Odota EA reaktiota
    print("\nOdotetaan EA reaktiota...")
    for i in range(8):
        time.sleep(1)
        if not os.path.exists(signal_file):
            print(f"SUCCESS: EA kasitteli BUY signaalin {i+1} sekunnissa!")
            break
        print(f"Odotus: {i+1}/8 sekuntia...")
    else:
        print("HUOM: BUY signaali ei viela kasitelty")
    
    time.sleep(2)  # Pieni tauko
    
    # TESTI 2: SELL signaali
    print("\nTESTI 2: SELL SIGNAALI")
    print("-" * 40)
    
    sell_signal = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "BCHUSD",
        "timeframe": "M5",
        "signal_type": "M5_BOS",
        "direction": "SELL",
        "entry_price": 444.25,
        "confidence": 0.89,
        "atr_pips": 12,
        "ylipip_trigger": 0.6,
        "strategy": "MIKROBOT_FASTVERSION",
        "test_id": "V4_TEST_002"
    }
    
    # Tallenna SELL signaali
    with open(signal_file, 'w', encoding='ascii') as f:
        json.dump(sell_signal, f, indent=2, ensure_ascii=True)
    
    print("SELL signaali lahetetty:")
    print(f"- Hinta: 444.25")
    print(f"- ATR: 12 pips")
    print(f"- Confidence: 89%")
    
    # Odota EA reaktiota
    print("\nOdotetaan EA reaktiota...")
    for i in range(8):
        time.sleep(1)
        if not os.path.exists(signal_file):
            print(f"SUCCESS: EA kasitteli SELL signaalin {i+1} sekunnissa!")
            break
        print(f"Odotus: {i+1}/8 sekuntia...")
    else:
        print("HUOM: SELL signaali ei viela kasitelty")
    
    # YHTEENVETO
    print("\n" + "=" * 60)
    print("TESTAUKSEN YHTEENVETO")
    print("=" * 60)
    print("\nTARKISTA MT5 EXPERTS-VALILEHTI:")
    print("- 'Signal received, parsing...'")
    print("- 'Parsed - Direction: BUY, M5_BOS: true'")
    print("- 'Executing BUY order...'")
    print("- 'BUY: Price=xxx SL=xxx TP=xxx Lots=xxx'")
    print("- 'BUY order executed: xxx' TAI 'BUY order failed: xxx'")
    print("\nJa vastaavat SELL viestit")
    
    print("\nTARKISTA TRADE-VALILEHTI:")
    print("- Mahdolliset avautuneet BCHUSD positiot")
    print("- Order ticket numerot")
    print("- Stop Loss ja Take Profit tasot")
    
    return True

def verify_ea_status():
    """Tarkista EA status"""
    print("\n\nEA STATUS TARKISTUS:")
    print("=" * 60)
    print("1. Chartin oikeassa ylakulmassa: 'MikrobotFastversion_v4'")
    print("2. AutoTrading nappi: VIHREA")
    print("3. EA hymyilee (ei surullinen naama)")
    print("4. Journal: 'Expert MikrobotFastversion_v4 loaded successfully'")
    print("\nJOS EA EI TOIMI:")
    print("- Tarkista AutoTrading on paalla")
    print("- Tarkista EA asetukset (F7 chartissa)")
    print("- Tarkista 'Allow algorithmic trading' on valittu")

if __name__ == "__main__":
    success = test_v4_functionality()
    
    if success:
        verify_ea_status()
        print("\n\nV4 EA TESTAUS VALMIS!")
        print("Tarkista MT5 lokit ja vahvista toiminta.")
    else:
        print("\n\nTESTI EPAONNISTUI!")
        print("Tarkista EA asennus.")