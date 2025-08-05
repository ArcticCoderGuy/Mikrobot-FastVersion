"""
TARKISTA EA KAANTAMINEN
Yksinkertainen skripti joka tarkistaa onko EA valmis
"""
import os
from pathlib import Path

def check_ea_compilation():
    """Tarkista onko EA kaannetty onnistuneesti"""
    
    print("MIKROBOT FASTVERSION EA - COMPILATION CHECK")
    print("=" * 50)
    
    ea_dir = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Experts")
    
    # Tarkista tiedostot
    source_file = ea_dir / "MikrobotFastversionEA.mq5"
    compiled_file = ea_dir / "MikrobotFastversionEA.ex5"
    
    print("1. TARKISTETAAN TIEDOSTOT...")
    
    if source_file.exists():
        size = source_file.stat().st_size
        print(f"SUCCESS: Lahdekoodi loytyy ({size} bytes)")
        source_ok = True
    else:
        print("ERROR: Lahdekoodi puuttuu")
        source_ok = False
    
    if compiled_file.exists():
        size = compiled_file.stat().st_size
        print(f"SUCCESS: Kaannetty EA loytyy ({size} bytes)")
        compiled_ok = True
    else:
        print("WARNING: Kaannetty EA puuttuu (.ex5)")
        compiled_ok = False
    
    print(f"\n2. TULOS...")
    
    if source_ok and compiled_ok:
        print("SUCCESS: EA on valmis kayttoon!")
        print("- Lahdekoodi: OK")
        print("- Kaannetty tiedosto: OK")
        print("- EA nakyy MT5:n Navigator-paneelissa")
        print("\nVoit nyt:")
        print("1. Avata MT5:n")
        print("2. Avata Navigator (Ctrl+N)")
        print("3. Laajentaa 'Expert Advisors'")
        print("4. Vetaa 'MikrobotFastversionEA' charttiin")
        return True
        
    elif source_ok and not compiled_ok:
        print("WARNING: EA tarvitsee kaantamisen")
        print("- Lahdekoodi: OK")
        print("- Kaannetty tiedosto: PUUTTUU")
        print("\nTee naita toimenpiteita:")
        print("1. Avaa MT5")
        print("2. Paina F4 (avaa MetaEditor)")
        print("3. Loyda ja avaa MikrobotFastversionEA.mq5")
        print("4. Paina F7 (kaanna)")
        print("5. Sulje MetaEditor")
        print("6. Kaynnista tama skripti uudelleen")
        return False
        
    else:
        print("ERROR: EA tiedostoja puuttuu")
        print("Tarkista asennus")
        return False

if __name__ == "__main__":
    success = check_ea_compilation()
    
    if success:
        print(f"\nREADY: EA on kayttovalmis!")
    else:
        print(f"\nTODO: Kaanna EA MetaEditorissa")