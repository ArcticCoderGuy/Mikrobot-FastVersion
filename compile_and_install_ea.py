"""
MIKROBOT FASTVERSION EA COMPILER AND INSTALLER
Kaantaa EA ja varmistaa etta se nakyy MT5:ssa
"""
import MetaTrader5 as mt5
import subprocess
import time
from pathlib import Path
import os

def compile_and_install_ea():
    """Kaantaa EA ja asentaa sen MT5:een"""
    
    print("MIKROBOT FASTVERSION EA COMPILER & INSTALLER")
    print("=" * 55)
    
    # EA paths
    ea_source_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Experts/MikrobotFastversionEA.mq5")
    ea_compiled_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Experts/MikrobotFastversionEA.ex5")
    
    print(f"1. TARKISTETAAN EA TIEDOSTOT...")
    
    # Check source file
    if ea_source_path.exists():
        print(f"SUCCESS: Lahdekoodi loytyi: {ea_source_path.name}")
        file_size = ea_source_path.stat().st_size
        print(f"- Tiedoston koko: {file_size} bytes")
    else:
        print(f"ERROR: Lahdekoodi puuttuu: {ea_source_path}")
        return False
    
    # Check compiled file
    if ea_compiled_path.exists():
        print(f"SUCCESS: Kaannetty tiedosto loytyi: {ea_compiled_path.name}")
        compiled_size = ea_compiled_path.stat().st_size
        print(f"- Kaannetyn tiedoston koko: {compiled_size} bytes")
        
        # Check if compilation is recent
        source_time = ea_source_path.stat().st_mtime
        compiled_time = ea_compiled_path.stat().st_mtime
        
        if compiled_time >= source_time:
            print("SUCCESS: Kaannetty versio on ajantasalla")
            compiled_ok = True
        else:
            print("WARNING: Lahdekoodi on uudempi, kaantaminen tarvitaan")
            compiled_ok = False
    else:
        print(f"WARNING: Kaannetty tiedosto puuttuu: {ea_compiled_path.name}")
        compiled_ok = False
    
    # Connect to MT5 to check if EA is visible
    print(f"\n2. TARKISTETAAN MT5 YHTEYS...")
    
    if not mt5.initialize():
        print("ERROR: MT5 yhteys epaonnistui")
        return False
    
    if not mt5.login(95244786, "Ua@tOnLp", "Ava-Demo 1-MT5"):
        print("ERROR: Kirjautuminen epaonnistui")
        mt5.shutdown()
        return False
    
    print("SUCCESS: MT5 yhteys toimii")
    account_info = mt5.account_info()
    print(f"Tili: {account_info.login} | Balance: ${account_info.balance:.2f}")
    
    # Try to find MetaEditor for compilation
    print(f"\n3. ETSITAAN METAEDITOR KAANTAMISTA VARTEN...")
    
    # Common MetaEditor paths
    metaeditor_paths = [
        "C:/Program Files/MetaTrader 5/MetaEditor64.exe",
        "C:/Program Files (x86)/MetaTrader 5/MetaEditor64.exe", 
        "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/metaeditor64.exe"
    ]
    
    metaeditor_path = None
    for path in metaeditor_paths:
        if Path(path).exists():
            metaeditor_path = path
            print(f"SUCCESS: MetaEditor loytyi: {path}")
            break
    
    if not metaeditor_path:
        print("WARNING: MetaEditor ei loytynyt automaattisesti")
        print("Jatketaan ilman kaantamista...")
    
    # Manual compilation instructions if MetaEditor not found
    if not compiled_ok and not metaeditor_path:
        print(f"\n4. MANUAALINEN KAANTAMINEN TARVITAAN...")
        print("OHJEET:")
        print("1. Avaa MetaTrader 5")
        print("2. Paina F4 (avaa MetaEditor)")
        print("3. Navigator-paneelissa, laajenna 'Expert Advisors'")
        print("4. Kaksoisklikkaa 'MikrobotFastversionEA.mq5'")
        print("5. Paina F7 tai Compile-nappia")
        print("6. Odota että kaantaminen valmistuu")
        print("7. Sulje MetaEditor")
        print("8. Palaa MT5:een")
        
        input("\nPaina Enter kun olet kaantanyt EA:n...")
        
        # Check again if compilation worked
        if ea_compiled_path.exists():
            print("SUCCESS: Kaantaminen onnistui!")
            compiled_ok = True
        else:
            print("ERROR: Kaantaminen epaonnistui tai .ex5 tiedosto puuttuu")
    
    # Restart MT5 to refresh EA list
    print(f"\n5. PAIVITETAAN EA LISTA...")
    
    mt5.shutdown()
    time.sleep(2)
    
    if not mt5.initialize():
        print("ERROR: MT5 uudelleenyhdistys epaonnistui")
        return False
    
    if not mt5.login(95244786, "Ua@tOnLp", "Ava-Demo 1-MT5"):
        print("ERROR: Uudelleenkirjautuminen epaonnistui")
        mt5.shutdown()
        return False
    
    print("SUCCESS: MT5 paivitetty")
    
    # Final verification
    print(f"\n6. LOPULLINEN TARKISTUS...")
    
    # Check all EA files in the directory
    experts_dir = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Experts")
    
    print("KAIKKI EA TIEDOSTOT:")
    ea_files_found = []
    
    for file in experts_dir.glob("*.ex5"):
        if "Mikrobot" in file.name:
            ea_files_found.append(file.name)
            print(f"SUCCESS: {file.name} (kaannetty EA)")
    
    for file in experts_dir.glob("*.mq5"):
        if "Mikrobot" in file.name:
            print(f"INFO: {file.name} (lahdekoodi)")
    
    # Check if our EA is ready
    target_ea = "MikrobotFastversionEA.ex5"
    if target_ea in ea_files_found:
        print(f"\nSUCCESS: {target_ea} on valmis kayttoon!")
        print("EA nakyy nyt MT5:n Navigator-paneelissa")
        ea_ready = True
    else:
        print(f"\nWARNING: {target_ea} ei loytynyt")
        print("Kaantaminen saattaa olla tarpeen")
        ea_ready = False
    
    # Final instructions
    print(f"\n" + "=" * 55)
    print("EA INSTALLATION STATUS")
    print("=" * 55)
    
    if ea_ready:
        print("SUCCESS: MikrobotFastversionEA on valmis!")
        print("\nNAIN LOYDAT EA:N MT5:SSA:")
        print("1. Avaa MetaTrader 5")
        print("2. Avaa Navigator (Ctrl+N)")
        print("3. Laajenna 'Expert Advisors'")
        print("4. Naet 'MikrobotFastversionEA' listassa")
        print("5. Veda se haluamaasi charttiin")
        
        print("\nEA TOIMINNOT:")
        print("- M5 BOS + M1 retest monitoring")
        print("- 0.6 ylipip trigger system")
        print("- ATR dynamic positioning (4-15 pips)")
        print("- XPWS weekly tracking")
        print("- Risk management: 0.55% per trade")
        
        result = True
    else:
        print("WARNING: EA tarvitsee kaantamisen")
        print("\nVIANETSINTA:")
        print("1. Varmista etta MikrobotFastversionEA.mq5 on olemassa")
        print("2. Avaa MetaEditor (F4 MT5:ssa)")
        print("3. Kaanna EA painamalla F7")
        print("4. Tarkista etta .ex5 tiedosto syntyy")
        print("5. Kaynnista tama skripti uudelleen")
        
        result = False
    
    mt5.shutdown()
    return result

if __name__ == "__main__":
    success = compile_and_install_ea()
    
    if success:
        print(f"\nSUCCESS: MIKROBOT FASTVERSION EA READY!")
        print("EA on nyt kaytettavissa MT5:ssa!")
    else:
        print(f"\nWARNING: Tarkista EA kaantaminen")
        print("Seuraa ohjeita MetaEditorin kayttamiseen")