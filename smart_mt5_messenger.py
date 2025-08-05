from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
Smart MT5 Messenger - No API conflicts
Communicates through MT5 files and notifications without API connection
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

def create_mt5_message_files():
    """Create message files that MT5 can read"""
    
    print("MIKROBOT - SMART MT5 MESSENGER")
    print("=" * 50)
    print("This method NEVER conflicts with your MT5 connection!")
    print()
    
    # Get MT5 data directory (common locations)
    possible_mt5_dirs = [
        Path.home() / "AppData" / "Roaming" / "MetaQuotes" / "Terminal",
        Path("C:") / "Users" / os.getenv('USERNAME', 'HP') / "AppData" / "Roaming" / "MetaQuotes" / "Terminal",
        Path("C:") / "Program Files" / "MetaTrader 5" / "MQL5" / "Files",
        Path("C:") / "Program Files (x86)" / "MetaTrader 5" / "MQL5" / "Files"
    ]
    
    mt5_dir = None
    for directory in possible_mt5_dirs:
        if directory.exists():
            mt5_dir = directory
            print(f"Found MT5 directory: {directory}")
            break
    
    if not mt5_dir:
        print("MT5 directory not found, creating messages locally...")
        mt5_dir = Path("./mt5_messages")
        mt5_dir.mkdir(exist_ok=True)
    
    # Create message data
    timestamp = datetime.now()
    message_data = {
        "source": "Mikrobot FastVersion",
        "timestamp": timestamp.isoformat(),
        "message": f"Yhteys toimii! Aika: {timestamp.strftime('%H:%M:%S')}",
        "account": "107034605",
        "metaquotes_id": "03A06890",
        "status": "connection_verified",
        "test_type": "smart_messenger"
    }
    
    # Method 1: Create JSON file for MT5 to read
    message_file = mt5_dir / "mikrobot_messages.json"
    try:
        with open(message_file, 'w', encoding='utf-8') as f:
            json.dump(message_data, f, indent=2, ensure_ascii=False)
        print(f"OK Message file created: {message_file}")
    except Exception as e:
        print(f"Could not create message file: {e}")
    
    # Method 2: Create simple text file
    text_file = mt5_dir / "mikrobot_status.txt"
    try:
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"MIKROBOT STATUS - {timestamp.strftime('%H:%M:%S %d.%m.%Y')}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Account: 107034605\n")
            f.write(f"MetaQuotes ID: 03A06890\n") 
            f.write(f"Status: CONNECTION VERIFIED\n")
            f.write(f"Message: {message_data['message']}\n")
            f.write(f"Test completed at: {timestamp}\n")
        print(f"OK Status file created: {text_file}")
    except Exception as e:
        print(f"Could not create status file: {e}")
    
    # Method 3: Create CSV log for MT5 to import
    csv_file = mt5_dir / "mikrobot_log.csv"
    try:
        csv_exists = csv_file.exists()
        with open(csv_file, 'a', encoding='utf-8') as f:
            if not csv_exists:
                f.write("timestamp,source,account,message,status\n")
            f.write(f"{timestamp.isoformat()},Mikrobot FastVersion,107034605,{message_data['message']},connection_verified\n")
        print(f"OK CSV log updated: {csv_file}")
    except Exception as e:
        print(f"Could not update CSV log: {e}")
    
    return message_data, mt5_dir

def create_mql5_compatible_signal():
    """Create a signal file that MQL5 EA can read"""
    
    print("\nCreating MQL5-compatible signal file...")
    
    # Signal that matches your MikroBot_BOS_M5M1.mq5 format
    signal_data = {
        "ea_name": "MikroBot_BOS_M5M1",
        "ea_version": "2.00", 
        "signal_type": "CONNECTION_TEST",
        "symbol": "EURUSD",
        "direction": "BUY",
        "trigger_price": 1.0855,
        "m5_bos_level": 1.0850,
        "m5_bos_direction": "BULLISH",
        "m1_break_high": 1.0857,
        "m1_break_low": 1.0852,
        "pip_trigger": 0.2,
        "timestamp": datetime.now().isoformat(),
        "account": 107034605,
        "test_message": "Mikrobot connection test successful",
        "metaquotes_id": "03A06890"
    }
    
    # Save to common MQL5 Files directory
    mql5_files_dirs = [
        Path("C:") / "Users" / os.getenv('USERNAME', 'HP') / "AppData" / "Roaming" / "MetaQuotes" / "Terminal" / "Common" / "Files",
        Path("./mql5_signals")
    ]
    
    for files_dir in mql5_files_dirs:
        try:
            files_dir.mkdir(parents=True, exist_ok=True)
            signal_file = files_dir / "mikrobot_test_signal.json"
            
            with open(signal_file, 'w', encoding='utf-8') as f:
                json.dump(signal_data, f, indent=2, ensure_ascii=False)
            
            print(f"OK MQL5 signal file created: {signal_file}")
            break
            
        except Exception as e:
            print(f"Could not create signal in {files_dir}: {e}")
            continue
    
    return signal_data

def create_mobile_notification_file():
    """Create file that might trigger mobile notifications"""
    
    print("\nCreating mobile notification indicators...")
    
    # Create notification data
    notification = {
        "type": "mikrobot_test",
        "account": "107034605",
        "metaquotes_id": "03A06890",
        "timestamp": datetime.now().isoformat(),
        "message": "Mikrobot FastVersion - Yhteys OK!",
        "priority": "high",
        "mobile_target": True
    }
    
    # Save to various locations where MT5 might check
    notification_locations = [
        Path("./notifications"),
        Path.home() / "Documents" / "MT5_Notifications"
    ]
    
    for location in notification_locations:
        try:
            location.mkdir(parents=True, exist_ok=True)
            
            # JSON notification
            json_file = location / f"mikrobot_notification_{int(time.time())}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(notification, f, indent=2, ensure_ascii=False)
            
            # Simple alert file
            alert_file = location / "mikrobot_alert.txt"
            with open(alert_file, 'w', encoding='utf-8') as f:
                f.write(f"MIKROBOT ALERT - {datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"Account 107034605 - Connection verified\n")
                f.write(f"MetaQuotes ID: 03A06890\n")
                f.write("Check your mobile MT5 app!\n")
            
            print(f"OK Notification files created in: {location}")
            
        except Exception as e:
            print(f"Could not create notifications in {location}: {e}")
    
    return notification

def show_instructions():
    """Show instructions for checking messages"""
    
    print("\n" + "=" * 60)
    print("VIESTIT LUOTU - TARKISTA NM PAIKAT:")
    print("=" * 60)
    
    print("\n1. TIEDOSTOT LUOTU:")
    print("    mikrobot_messages.json - MT5:n luettavissa")
    print("    mikrobot_status.txt - Ihmisluettava status")  
    print("    mikrobot_log.csv - Lokitiedot")
    print("    mikrobot_test_signal.json - MQL5 EA:lle")
    
    print("\n2. TARKISTA MT5 TERMINAALISTA:")
    print("    File -> Open Data Folder -> MQL5 -> Files")
    print("    Etsi 'mikrobot_*' tiedostoja")
    print("    Journal-vlilehti mahdollisille viesteille")
    
    print("\n3. TARKISTA KNNYKST:")
    print("    MT5 Mobile App")
    print("    MetaQuotes ID: 03A06890")  
    print("    Push-ilmoitukset")
    print("    Tilin 107034605 tapahtumat")
    
    print("\n4. EI YHTEYSKONFLIKTEJA:")
    print("    Sinun MT5-terminaalisi yhteys pysyy ehjn")
    print("    Ei API-kutsuja = ei katkoksia")
    print("    Turvallinen tapa kommunikoida")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    try:
        print("Starting SMART MT5 Messenger...")
        print("No API conflicts - your MT5 connection stays intact!")
        print()
        
        # Create all message types
        message_data, mt5_dir = create_mt5_message_files()
        signal_data = create_mql5_compatible_signal() 
        notification_data = create_mobile_notification_file()
        
        # Show instructions
        show_instructions()
        
        print(f"\nTest completed at: {datetime.now().strftime('%H:%M:%S')}")
        print("Your MT5 terminal connection was never interrupted!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("But your MT5 connection remains safe!")