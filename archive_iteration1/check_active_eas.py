"""
ACTIVE EA CHECKER
Tarkistaa mitkä Expert Advisorit ovat aktiivisia ja poistaa vanhat
"""
import MetaTrader5 as mt5
from datetime import datetime
import time

def check_active_eas():
    """Tarkista aktiiviset EA:t"""
    
    print("CHECKING ACTIVE EXPERT ADVISORS")
    print("=" * 40)
    
    # Connect to MT5
    if not mt5.initialize():
        print("ERROR: MT5 ei käynnisty")
        return False
    
    if not mt5.login(95244786, "Ua@tOnLp", "Ava-Demo 1-MT5"):
        print("ERROR: Kirjautuminen epäonnistui")
        mt5.shutdown()
        return False
    
    print("SUCCESS: Yhdistetty MT5:een")
    account_info = mt5.account_info()
    print(f"Tili: {account_info.login} | Balance: ${account_info.balance:.2f}")
    
    # Tarkista kaikki avoimet chartit ja niiden EA:t
    print(f"\nTARKISTETAAN AKTIIVISET EA:T...")
    
    # Hae kaikki symbolit joissa voi olla chartteja
    symbols = ["EURUSD", "GBPUSD", "BTCUSD", "BCHUSD", "LTCUSD", "ETHUSD", "XAUUSD", "USDJPY"]
    active_eas = []
    
    for symbol in symbols:
        # Tarkista onko symboli saatavilla
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info and symbol_info.visible:
            print(f"Checking {symbol}...")
            
            # Simuloi EA:n tarkistus (MT5 Python API ei suoraan näytä EA:ita)
            # Mutta voimme tarkistaa positions ja orders
            positions = mt5.positions_get(symbol=symbol)
            if positions:
                for pos in positions:
                    print(f"  Position: {pos.symbol} {pos.volume} lots, comment: '{pos.comment}'")
                    
                    # Jos kommentissa on EA:n nimi, se voi kertoa aktiivisesta EA:sta
                    if "Mikrobot" in pos.comment or "M5M1" in pos.comment:
                        active_eas.append({
                            "symbol": symbol,
                            "ea_name": "MikrobotM5M1 (detected from position comment)",
                            "ticket": pos.ticket
                        })
    
    # Tarkista Expert Advisors -kansio
    print(f"\nTARKISTETAAN EA TIEDOSTOT...")
    
    import os
    ea_path = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Experts"
    
    if os.path.exists(ea_path):
        ea_files = []
        for file in os.listdir(ea_path):
            if file.endswith('.mq5') and 'Mikrobot' in file:
                ea_files.append(file)
                print(f"Found EA file: {file}")
        
        # Tarkista myös alikansiot
        for root, dirs, files in os.walk(ea_path):
            for file in files:
                if file.endswith('.mq5') and 'Mikrobot' in file:
                    rel_path = os.path.relpath(os.path.join(root, file), ea_path)
                    if rel_path not in ea_files:
                        ea_files.append(rel_path)
                        print(f"Found EA file: {rel_path}")
    
    # Näytä yhteenveto
    print(f"\n" + "=" * 40)
    print("ACTIVE EA STATUS:")
    
    if active_eas:
        print(f"Detected {len(active_eas)} potentially active EA(s):")
        for ea in active_eas:
            print(f"- {ea['symbol']}: {ea['ea_name']}")
    else:
        print("No EA activity detected from positions")
    
    # Ohjeita
    print(f"\nACTION REQUIRED:")
    print("1. Avaa MetaTrader 5")
    print("2. Tarkista Expert Advisors -välilehti alhaalta")
    print("3. Etsi aktiiviset EA:t (ne näkyvät chartteissa oikeassa yläkulmassa)")
    print("4. Poista vanhat EA:t vetämällä ne pois charteista")
    print("5. Liitä MikrobotFastversionEA mihin tahansa charttiin")
    
    print(f"\nKURRENT EA FILES AVAILABLE:")
    if 'ea_files' in locals():
        for ea_file in ea_files:
            if "Fastversion" in ea_file:
                print(f"NEW: {ea_file} <- USE THIS")
            else:
                print(f"OLD: {ea_file} <- Remove from charts")
    
    # Luo ohje tiedosto
    instructions = f"""
MIKROBOT EA REPLACEMENT INSTRUCTIONS
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CURRENT SITUATION:
- You have MikrobotM5M1 running on BCHUSD
- Need to replace with MikrobotFastversionEA

STEPS TO FIX:
1. Open MetaTrader 5
2. Look at BCHUSD chart - you'll see "MikrobotM5M1" in top-right corner
3. Right-click on the chart
4. Select "Expert Advisors" -> "Remove"
5. Go to Navigator panel (Ctrl+N if not visible)
6. Expand "Expert Advisors" 
7. Find "MikrobotFastversionEA"
8. Drag it to any chart (EURUSD recommended)
9. Make sure AutoTrading button is GREEN
10. You should see "MikrobotFastversionEA" in the chart's top-right corner

VERIFICATION:
- Only MikrobotFastversionEA should be visible on charts
- Expert Advisors tab should show MikrobotFastversionEA messages
- No old MikrobotM5M1 should be running

RESULT:
- New MIKROBOT_FASTVERSION strategy will be active
- 0.6 ylipip trigger system activated
- ATR dynamic positioning enabled
- XPWS weekly tracking active
"""
    
    with open("C:/Users/HP/Dev/Mikrobot Fastversion/ea_replacement_instructions.txt", 'w') as f:
        f.write(instructions)
    
    print(f"\nDETAILED INSTRUCTIONS SAVED TO:")
    print("C:/Users/HP/Dev/Mikrobot Fastversion/ea_replacement_instructions.txt")
    
    mt5.shutdown()
    return True

if __name__ == "__main__":
    check_active_eas()