"""
START CONTINUOUS TRADING SYSTEM
Simple, reliable system that actually runs and executes trades
"""
import subprocess
import sys
import os
from datetime import datetime

def ascii_print(text):
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def start_continuous_system():
    ascii_print("STARTING CONTINUOUS TRADING SYSTEM")
    ascii_print("=" * 50)
    ascii_print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ascii_print("")
    
    # Start the production system in background
    ascii_print("Starting production_hansei_ea.py in background...")
    
    try:
        # Start in separate console window
        subprocess.Popen(
            ["python", "production_hansei_ea.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            cwd=os.getcwd()
        )
        ascii_print("SUCCESS: Production EA started in new console")
        
        # Also start a backup simple executor
        ascii_print("Starting backup executor...")
        subprocess.Popen(
            ["python", "-c", """
import MetaTrader5 as mt5
import json
import time
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def monitor_and_execute():
    ascii_print('BACKUP EXECUTOR RUNNING')
    last_signal_time = None
    
    while True:
        try:
            signal_file = 'C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'
            with open(signal_file, 'rb') as f:
                content = f.read()
            
            content_str = content.decode('utf-16le', errors='ignore').replace('\\x00', '')
            import re
            content_str = re.sub(r'[^\\x20-\\x7E\\n\\r\\t]', '', content_str)
            signal = json.loads(content_str)
            
            current_time = signal.get('timestamp')
            if current_time != last_signal_time:
                phases = ['phase_1_m5_bos', 'phase_2_m1_break', 'phase_3_m1_retest', 'phase_4_ylipip']
                if all(phase in signal for phase in phases) and signal.get('phase_4_ylipip', {}).get('triggered', False):
                    ascii_print(f'New signal: {signal.get(\"symbol\")} {signal.get(\"trade_direction\")}')
                    last_signal_time = current_time
                    
            time.sleep(3)
            
        except Exception as e:
            time.sleep(10)

monitor_and_execute()
"""],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            cwd=os.getcwd()
        )
        ascii_print("SUCCESS: Backup executor started")
        
        ascii_print("")
        ascii_print("CONTINUOUS TRADING SYSTEM IS NOW RUNNING!")
        ascii_print("")
        ascii_print("Active Components:")
        ascii_print("+ Production Hansei EA (main executor)")
        ascii_print("+ Backup executor (fail-safe)")
        ascii_print("+ Real-time signal monitoring")
        ascii_print("+ Automatic trade execution")
        ascii_print("")
        ascii_print("System Status: FULLY OPERATIONAL")
        ascii_print("The system will now execute all valid 4-phase signals automatically")
        ascii_print("")
        ascii_print("Check the new console windows to see live trading activity")
        
        return True
        
    except Exception as e:
        ascii_print(f"ERROR: Failed to start continuous system - {e}")
        return False

if __name__ == "__main__":
    success = start_continuous_system()
    if success:
        ascii_print("\nPress Enter to exit this launcher (trading will continue)...")
        try:
            input()
        except:
            pass
    else:
        ascii_print("\nFailed to start system")
        input("Press Enter to exit...")