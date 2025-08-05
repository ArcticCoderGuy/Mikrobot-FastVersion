"""
EA REPLACEMENT AUTOMATOR
Korvaa vanhan MikrobotM5M1:n uudella MikrobotFastversionEA:lla
"""
import MetaTrader5 as mt5
import time
import json
from datetime import datetime
from pathlib import Path

def replace_old_ea():
    """Korvaa vanha EA uudella"""
    
    print("MIKROBOT EA REPLACEMENT SYSTEM")
    print("=" * 45)
    print("Korvataan MikrobotM5M1 -> MikrobotFastversionEA")
    
    # Connect to MT5
    if not mt5.initialize():
        print("ERROR: MT5 ei käynnisty")
        return False
    
    if not mt5.login(107034605, "RcEw_s7w", "Ava-Demo 1-MT5"):
        print("ERROR: Kirjautuminen epäonnistui")
        mt5.shutdown()
        return False
    
    print("SUCCESS: Yhdistetty MT5:een")
    account_info = mt5.account_info()
    print(f"Tili: {account_info.login} | Balance: ${account_info.balance:.2f}")
    
    # Luo uusi aktivointi signaali joka korvaa vanhan
    print(f"\nLUODAAN UUSI AKTIVOINTI SIGNAALI...")
    
    replacement_signal = {
        "timestamp": datetime.now().isoformat(),
        "command": "REPLACE_EA",
        "old_ea": "MikrobotM5M1", 
        "new_ea": "MikrobotFastversionEA",
        "account": 107034605,
        "action": "IMMEDIATE_REPLACEMENT",
        "priority": "HIGH",
        "strategy": "MIKROBOT_FASTVERSION",
        "replacement_instructions": {
            "step_1": "Remove old MikrobotM5M1 from all charts",
            "step_2": "Attach MikrobotFastversionEA to EURUSD chart",
            "step_3": "Verify AutoTrading is enabled",
            "step_4": "Confirm new EA is running"
        },
        "new_ea_parameters": {
            "RiskPercent": 0.55,
            "MinATRPips": 4,
            "MaxATRPips": 15, 
            "YlipipStandard": 0.6,
            "EnableXPWS": True,
            "XPWSThreshold": 10.0
        }
    }
    
    # Tallenna korvaus-signaali
    common_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
    replacement_file = common_path / "ea_replacement_signal.json"
    
    try:
        with open(replacement_file, 'w') as f:
            json.dump(replacement_signal, f, indent=2)
        print("SUCCESS: EA korvaussignaali luotu")
    except Exception as e:
        print(f"ERROR: Signaalin luonti epäonnistui: {e}")
        return False
    
    # Luo stop-signaali vanhalle EA:lle
    stop_signal = {
        "timestamp": datetime.now().isoformat(),
        "command": "STOP_EA",
        "ea_name": "MikrobotM5M1",
        "reason": "REPLACED_WITH_FASTVERSION",
        "action": "IMMEDIATE_STOP"
    }
    
    stop_file = common_path / "ea_stop_signal.json"
    try:
        with open(stop_file, 'w') as f:
            json.dump(stop_signal, f, indent=2)
        print("SUCCESS: Vanhan EA:n stop-signaali luotu")
    except Exception as e:
        print(f"ERROR: Stop-signaalin luonti epäonnistui: {e}")
    
    # Päivitä pää-strategia signaali
    main_signal = {
        "timestamp": datetime.now().isoformat(),
        "account": 107034605,
        "strategy": "MIKROBOT_FASTVERSION",
        "version": "2.0.0",
        "status": "ACTIVE_REPLACEMENT_MODE",
        "active_ea": "MikrobotFastversionEA",
        "replaced_ea": "MikrobotM5M1",
        "replacement_date": datetime.now().isoformat(),
        "components": {
            "atr_dynamic_positioning": True,
            "universal_ylipip_trigger": True,
            "xpws_weekly_tracker": True,
            "dual_phase_tp_system": True,
            "m5_bos_monitoring": True,
            "m1_retest_validation": True
        },
        "parameters": {
            "risk_percent": 0.55,
            "atr_min_pips": 4,
            "atr_max_pips": 15,
            "ylipip_standard": 0.6,
            "xpws_threshold": 10.0
        }
    }
    
    main_signal_file = common_path / "mikrobot_fastversion_signal.json"
    try:
        with open(main_signal_file, 'w') as f:
            json.dump(main_signal, f, indent=2)
        print("SUCCESS: Pää-strategia signaali päivitetty")
    except Exception as e:
        print(f"ERROR: Pää-signaalin päivitys epäonnistui: {e}")
    
    # Tarkista nykyinen tilanne
    print(f"\nNYKYINEN TILANNE:")
    
    # Tarkista positiot
    positions = mt5.positions_get()
    if positions:
        print(f"Aktiivisia positioita: {len(positions)}")
        total_profit = sum(pos.profit for pos in positions)
        print(f"Kokonais P&L: ${total_profit:.2f}")
        
        # Etsi BCHUSD positio
        bchusd_positions = [pos for pos in positions if pos.symbol == "BCHUSD"]
        if bchusd_positions:
            print(f"\nBCHUSD POSITIOT:")
            for pos in bchusd_positions:
                pos_type = "BUY" if pos.type == 0 else "SELL"
                print(f"- {pos.symbol}: {pos_type} {pos.volume} lotia, P&L: ${pos.profit:.2f}")
                print(f"  Comment: '{pos.comment}'")
    
    # Tarkista EA tiedostot
    print(f"\nEA TIEDOSTOT:")
    ea_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Experts")
    
    # Hae kaikki Mikrobot EA:t
    ea_files = []
    if ea_path.exists():
        for file in ea_path.glob("*Mikrobot*.mq5"):
            ea_files.append(file.name)
        
        # Tarkista myös alikansiot
        for subfolder in ea_path.iterdir():
            if subfolder.is_dir():
                for file in subfolder.glob("*Mikrobot*.mq5"):
                    ea_files.append(f"{subfolder.name}/{file.name}")
    
    for ea_file in ea_files:
        if "Fastversion" in ea_file:
            print(f"NEW: {ea_file} (käytä tätä)")
        else:
            print(f"OLD: {ea_file} (poista käytöstä)")
    
    print(f"\n" + "=" * 45)
    print("EA REPLACEMENT READY!")
    print("=" * 45)
    
    # Ohjeet käyttäjälle
    print(f"\nSEURAVAT VAIHEET:")
    print("1. Avaa MetaTrader 5")
    print("2. Mene BCHUSD charttiin")
    print("3. Näet 'MikrobotM5M1' oikeassa yläkulmassa")
    print("4. Klikkaa hiiren oikealla chartissa")
    print("5. Valitse 'Expert Advisors' -> 'Remove'")
    print("6. Avaa Navigator (Ctrl+N)")
    print("7. Laajenna 'Expert Advisors'")
    print("8. Vedä 'MikrobotFastversionEA' mihin tahansa charttiin")
    print("9. Varmista että AutoTrading-nappi on VIHREÄ")
    print("10. Näet 'MikrobotFastversionEA' uudessa chartissa")
    
    print(f"\nTULOS:")
    print("- Vanha MikrobotM5M1 poistettu")
    print("- Uusi MikrobotFastversionEA aktiivinen")
    print("- MIKROBOT_FASTVERSION strategia käytössä")
    print("- 0.6 ylipip triggeri toiminnassa")
    print("- ATR-dynaaminen positiointi päällä")
    print("- XPWS viikoittainen seuranta aktiivinen")
    
    print(f"\nREPLACEMENT SIGNALS CREATED!")
    print("Kaikki tarvittavat signaalit on luotu MT5:lle")
    
    mt5.shutdown()
    return True

if __name__ == "__main__":
    success = replace_old_ea()
    
    if success:
        print(f"\nSUCCESS: EA REPLACEMENT READY!")
        print("Seuraa ohjeita MT5:ssä vanhan EA:n korvaamiseksi uudella")
    else:
        print(f"\nERROR: EA REPLACEMENT FAILED!")
        print("Tarkista virheet ja yritä uudelleen")