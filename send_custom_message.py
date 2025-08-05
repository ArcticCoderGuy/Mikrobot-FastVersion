from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
Send Custom Message to MT5 - Test viestijrjestelm
"""

import json
import time
from datetime import datetime
from pathlib import Path

def send_custom_message():
    """Send custom message to MT5 via files"""
    
    print("MIKROBOT - CUSTOM MESSAGE SENDER")
    print("=" * 50)
    
    # Your custom message
    custom_message = "Pekka ja Aulikki menivt saunaan ja Pekka avasi kaljapullon johon Auni sanoi; ota nyt mielummin Paulaner:ia"
    
    print(f"Sending message: {custom_message}")
    print()
    
    # Create message directory
    msg_dir = Path("./mt5_messages")
    msg_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now()
    
    # 1. Create custom message file
    try:
        message_data = {
            "source": "Mikrobot FastVersion",
            "timestamp": timestamp.isoformat(),
            "custom_message": custom_message,
            "account": "107034605",
            "metaquotes_id": "03A06890",
            "message_type": "custom_test",
            "sender": "Claude/Mikrobot"
        }
        
        # Save as JSON
        with open(msg_dir / "custom_message.json", 'w', encoding='utf-8') as f:
            json.dump(message_data, f, indent=2, ensure_ascii=False)
        print("OK - Custom message JSON created")
        
        # Save as readable text
        with open(msg_dir / "custom_message.txt", 'w', encoding='utf-8') as f:
            f.write(f"MIKROBOT VIESTI - {timestamp.strftime('%H:%M:%S %d.%m.%Y')}\n")
            f.write("=" * 60 + "\n")
            f.write(f"Vastaanottaja: MetaQuotes ID 03A06890\n")
            f.write(f"Tili: 107034605\n")
            f.write(f"Aika: {timestamp}\n")
            f.write("\nVIESTI:\n")
            f.write(f"{custom_message}\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("Lhettj: Mikrobot FastVersion\n")
        print("OK - Custom message TXT created")
        
    except Exception as e:
        print(f"Error creating custom message: {e}")
        return False
    
    # 2. Copy to MT5 directory
    try:
        mt5_files_dir = Path.home() / "AppData" / "Roaming" / "MetaQuotes" / "Terminal" / "Common" / "Files"
        
        if mt5_files_dir.exists():
            # Copy JSON
            target_json = mt5_files_dir / "custom_message.json"
            target_json.write_text(
                (msg_dir / "custom_message.json").read_text(encoding='utf-8'),
                encoding='utf-8'
            )
            
            # Copy TXT
            target_txt = mt5_files_dir / "custom_message.txt"
            target_txt.write_text(
                (msg_dir / "custom_message.txt").read_text(encoding='utf-8'),
                encoding='utf-8'
            )
            
            print(f"OK - Files copied to MT5 directory: {mt5_files_dir}")
        else:
            print("MT5 directory not found, files only in local directory")
            
    except Exception as e:
        print(f"Error copying to MT5 directory: {e}")
    
    # 3. Create alert file with timestamp
    try:
        alert_file = msg_dir / f"alert_{int(timestamp.timestamp())}.txt"
        with open(alert_file, 'w', encoding='utf-8') as f:
            f.write(f"MIKROBOT ALERT - {timestamp.strftime('%H:%M:%S')}\n")
            f.write("UUSI VIESTI SAAPUNUT\n")
            f.write(f"Tarkista: custom_message.txt\n")
            f.write(f"MetaQuotes ID: 03A06890\n")
        
        print(f"OK - Alert file created: {alert_file.name}")
        
    except Exception as e:
        print(f"Error creating alert: {e}")
    
    return True

def show_message_locations():
    """Show where to find the message"""
    
    print("\n" + "=" * 60)
    print("VIESTI LHETETTY!")
    print("=" * 60)
    
    print("\n1. TARKISTA NM PAIKAT:")
    print("   Local: ./mt5_messages/custom_message.txt")
    print("   MT5:   C:\\Users\\HP\\AppData\\Roaming\\MetaQuotes\\Terminal\\Common\\Files\\")
    
    print("\n2. MT5 TERMINAALI:")
    print("   - File -> Open Data Folder -> MQL5 -> Files")
    print("   - Etsi: custom_message.txt ja custom_message.json")
    
    print("\n3. KNNYKK:")
    print("   - MT5 Mobile App")
    print("   - MetaQuotes ID: 03A06890")
    print("   - Tili: 107034605")
    
    print("\n4. VIESTI:")
    print('   "Pekka ja Aulikki menivt saunaan ja Pekka avasi')
    print('    kaljapullon johon Auni sanoi; ota nyt mielummin Paulaner:ia"')
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    try:
        success = send_custom_message()
        
        if success:
            show_message_locations()
            print(f"\nViesti lhetetty: {datetime.now().strftime('%H:%M:%S')}")
            print("Tarkista MT5-terminaalisi Files-kansio!")
        else:
            print("\nViestin lhetys eponnistui")
            
    except Exception as e:
        print(f"Virhe: {e}")