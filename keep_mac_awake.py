#!/usr/bin/env python3
"""
Keep Mac Awake During Trading
============================

Prevents Mac from going to sleep/screensaver while trading overnight.
"""

import subprocess
import sys
import signal
import time

def keep_mac_awake():
    """Keep Mac awake using caffeinate command"""
    
    print("☕ CAFFEINATE: Keeping Mac awake for overnight trading")
    print("🌙 Your Mac will stay awake until trading stops")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        # Use caffeinate to prevent sleep
        # -d = prevent display sleep
        # -i = prevent idle sleep  
        # -u = prevent user idle system sleep
        process = subprocess.Popen([
            'caffeinate', 
            '-d',  # prevent display sleep
            '-i',  # prevent idle sleep
            '-u',  # prevent user idle system sleep
            '-s'   # prevent system sleep
        ])
        
        print("✅ Mac sleep prevention ACTIVE")
        print("📊 Trading can continue safely overnight")
        
        # Keep running until interrupted
        while True:
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping Mac awake mode...")
        process.terminate()
        print("✅ Mac can now sleep normally")
        
    except Exception as e:
        print(f"❌ Error keeping Mac awake: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = keep_mac_awake()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n✅ Mac awake mode stopped")
        sys.exit(0)