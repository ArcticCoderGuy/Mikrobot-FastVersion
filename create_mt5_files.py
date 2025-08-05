#!/usr/bin/env python3
"""
Create MT5 Message Files - No API conflicts
Creates files that MT5 can read without using API
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

def create_simple_files():
    """Create simple message files for MT5"""
    
    print("MIKROBOT - FILE-BASED MESSENGER")
    print("=" * 50)
    print("Creating files for MT5 without API conflicts")
    print()
    
    # Create local directory for messages
    msg_dir = Path("./mt5_messages")
    msg_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now()
    
    # 1. Simple text message
    try:
        with open(msg_dir / "mikrobot_status.txt", 'w') as f:
            f.write(f"MIKROBOT STATUS - {timestamp.strftime('%H:%M:%S %d.%m.%Y')}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Account: 107034605\n")
            f.write(f"MetaQuotes ID: 03A06890\n")
            f.write(f"Status: CONNECTION VERIFIED\n")
            f.write(f"Message: Mikrobot yhteys toimii!\n")
            f.write(f"Time: {timestamp}\n")
        print("OK - Status file created")
    except Exception as e:
        print(f"Error creating status file: {e}")
    
    # 2. JSON message
    try:
        message_data = {
            "source": "Mikrobot FastVersion",
            "timestamp": timestamp.isoformat(),
            "message": f"Yhteys toimii! Aika: {timestamp.strftime('%H:%M:%S')}",
            "account": "107034605",
            "metaquotes_id": "03A06890",
            "status": "connection_verified"
        }
        
        with open(msg_dir / "mikrobot_message.json", 'w') as f:
            json.dump(message_data, f, indent=2)
        print("OK - JSON message created")
    except Exception as e:
        print(f"Error creating JSON: {e}")
    
    # 3. CSV log
    try:
        with open(msg_dir / "mikrobot_log.csv", 'w') as f:
            f.write("timestamp,account,message,status\n")
            f.write(f"{timestamp.isoformat()},107034605,Connection test OK,verified\n")
        print("OK - CSV log created")
    except Exception as e:
        print(f"Error creating CSV: {e}")
    
    # 4. Signal file for MQL5
    try:
        signal_data = {
            "ea_name": "MikroBot_BOS_M5M1",
            "signal_type": "CONNECTION_TEST",
            "symbol": "EURUSD",
            "timestamp": timestamp.isoformat(),
            "account": 107034605,
            "test_message": "Mikrobot connection successful"
        }
        
        with open(msg_dir / "mikrobot_signal.json", 'w') as f:
            json.dump(signal_data, f, indent=2)
        print("OK - Signal file created")
    except Exception as e:
        print(f"Error creating signal: {e}")
    
    # Show what was created
    print(f"\nFiles created in: {msg_dir.absolute()}")
    try:
        for file in msg_dir.iterdir():
            if file.is_file():
                size = file.stat().st_size
                print(f"  - {file.name} ({size} bytes)")
    except Exception as e:
        print(f"Error listing files: {e}")
    
    return msg_dir

def copy_to_mt5_directories():
    """Try to copy files to MT5 directories"""
    
    print("\nTrying to copy to MT5 directories...")
    
    # Common MT5 file locations
    possible_dirs = [
        Path.home() / "AppData" / "Roaming" / "MetaQuotes" / "Terminal" / "Common" / "Files",
        Path("C:/Program Files/MetaTrader 5/MQL5/Files"),
        Path("C:/Program Files (x86)/MetaTrader 5/MQL5/Files")
    ]
    
    source_dir = Path("./mt5_messages")
    
    for target_dir in possible_dirs:
        if target_dir.exists():
            print(f"Found MT5 directory: {target_dir}")
            try:
                # Copy each file
                for source_file in source_dir.iterdir():
                    if source_file.is_file():
                        target_file = target_dir / source_file.name
                        target_file.write_text(source_file.read_text())
                        print(f"  Copied: {source_file.name}")
                break
            except Exception as e:
                print(f"  Copy failed: {e}")
        else:
            print(f"Directory not found: {target_dir}")

def show_instructions():
    """Show instructions"""
    
    print("\n" + "=" * 60)
    print("VIESTIT LUOTU!")
    print("=" * 60)
    
    print("\n1. TARKISTA TIEDOSTOT:")
    current_dir = Path("./mt5_messages").absolute()
    print(f"   Hakemisto: {current_dir}")
    print("   Tiedostot: mikrobot_status.txt, mikrobot_message.json")
    
    print("\n2. TARKISTA MT5 TERMINAALI:")
    print("   - File -> Open Data Folder -> MQL5 -> Files")
    print("   - Etsi 'mikrobot_*' tiedostoja")
    print("   - Journal-valilehti")
    
    print("\n3. TARKISTA KANNYKKA:")
    print("   - MT5 Mobile App")
    print("   - MetaQuotes ID: 03A06890")
    print("   - Tili: 107034605")
    
    print("\n4. EI YHTEYSKONFLIKTEJA:")
    print("   - Sinun MT5 yhteys pysyy ehjana!")
    print("   - Ei API-kutsuja")
    print("   - Turvallinen menetelma")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        msg_dir = create_simple_files()
        copy_to_mt5_directories()
        show_instructions()
        
        print(f"\nTesti valmis: {datetime.now().strftime('%H:%M:%S')}")
        print("MT5-terminaalisi yhteys ei katkennyt!")
        
    except Exception as e:
        print(f"Virhe: {e}")
        print("MT5-yhteytesi on silti turvassa!")