"""
LAHETA YKSINKERTAINEN SIGNAALI
Testaa yksinkertaisella signaalilla
"""

import os
from datetime import datetime

def send_simple_buy_signal():
    """Laheta yksinkertainen BUY signaali"""
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Hyvin yksinkertainen signaali
    simple_signal = '''{"timestamp":"2025-08-03 18:58:00","symbol":"BCHUSD","timeframe":"M5","signal_type":"M5_BOS","direction":"BUY","entry_price":445.00,"confidence":0.90,"atr_pips":10,"ylipip_trigger":0.6,"strategy":"MIKROBOT_FASTVERSION","test":"SIMPLE_BUY_TEST"}'''
    
    try:
        with open(signal_file, 'w', encoding='ascii') as f:
            f.write(simple_signal)
        
        print("YKSINKERTAINEN BUY SIGNAALI LAHETETTY!")
        print("Signaali:")
        print(simple_signal)
        print("\nOdota 5 sekuntia ja tarkista MT5")
        
    except Exception as e:
        print(f"VIRHE: {e}")
        return False
    
    return True

def send_simple_sell_signal():
    """Laheta yksinkertainen SELL signaali"""
    
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    
    # Odota hetki
    import time
    time.sleep(8)
    
    # Hyvin yksinkertainen SELL signaali
    simple_signal = '''{"timestamp":"2025-08-03 18:58:10","symbol":"BCHUSD","timeframe":"M5","signal_type":"M5_BOS","direction":"SELL","entry_price":446.00,"confidence":0.85,"atr_pips":12,"ylipip_trigger":0.6,"strategy":"MIKROBOT_FASTVERSION","test":"SIMPLE_SELL_TEST"}'''
    
    try:
        with open(signal_file, 'w', encoding='ascii') as f:
            f.write(simple_signal)
        
        print("\nYKSINKERTAINEN SELL SIGNAALI LAHETETTY!")
        print("Signaali:")
        print(simple_signal)
        
    except Exception as e:
        print(f"VIRHE: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("YKSINKERTAISET TESTISIGNAALIT")
    print("=" * 50)
    
    # Poista vanhat signaalit
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/mikrobot_fastversion_signal.json"
    if os.path.exists(signal_file):
        os.remove(signal_file)
    
    # Laheta BUY
    if send_simple_buy_signal():
        # Laheta SELL
        send_simple_sell_signal()
    
    print("\nTarkista MT5 Experts-valilehti!")
    print("Pitaisi nahda:")
    print("- 'Parsed - Direction: BUY, M5_BOS: true'")
    print("- 'Executing BUY order...'")
    print("- 'Parsed - Direction: SELL, M5_BOS: true'") 
    print("- 'Executing SELL order...'")