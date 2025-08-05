"""
Signal-Based MT5 Connector using Common folder
Fixes the EA communication issue
"""

import json
import os
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Use COMMON folder that EA can access with FILE_COMMON flag
COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
SIGNAL_FILE = COMMON_PATH / "signal.json"
RESPONSE_FILE = COMMON_PATH / "response.json"

# Ensure common directory exists
COMMON_PATH.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalConnectorCommon:
    """MT5 Signal Connector using Common folder"""
    
    def __init__(self):
        self.signal_id = 0
        logger.info(f"[INIT] Using Common folder: {COMMON_PATH}")
        logger.info(f"[INIT] Signal file: {SIGNAL_FILE}")
        self.clear_old_files()
        
    def clear_old_files(self):
        """Clear any old signal/response files"""
        try:
            if SIGNAL_FILE.exists():
                SIGNAL_FILE.unlink()
            if RESPONSE_FILE.exists():
                RESPONSE_FILE.unlink()
            logger.info("[CLEANUP] Old files cleared")
        except Exception as e:
            logger.error(f"[ERROR] Cleanup failed: {e}")
    
    def write_signal(self, signal: Dict[str, Any]) -> int:
        """Write signal to common folder"""
        try:
            self.signal_id += 1
            signal['id'] = self.signal_id
            signal['timestamp'] = datetime.now().isoformat()
            signal['status'] = 'pending'
            
            # Write to temp file first
            temp_file = SIGNAL_FILE.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(signal, f, indent=2)
            
            # Atomic rename
            temp_file.replace(SIGNAL_FILE)
            
            logger.info(f"[SIGNAL] Written #{self.signal_id} to {SIGNAL_FILE}")
            logger.info(f"[SIGNAL] Action: {signal.get('action')}")
            return self.signal_id
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to write signal: {e}")
            return -1
    
    async def wait_for_response(self, signal_id: int, timeout: float = 5.0) -> Optional[Dict]:
        """Wait for EA response"""
        start_time = time.time()
        
        logger.info(f"[WAIT] Waiting for response to signal #{signal_id}...")
        
        while time.time() - start_time < timeout:
            try:
                if RESPONSE_FILE.exists():
                    with open(RESPONSE_FILE, 'r') as f:
                        response = json.load(f)
                    
                    if response.get('signal_id') == signal_id:
                        logger.info(f"[RESPONSE] Received: {response}")
                        RESPONSE_FILE.unlink()  # Clean up
                        return response
                        
            except Exception as e:
                logger.debug(f"Waiting: {e}")
            
            await asyncio.sleep(0.1)
        
        logger.warning(f"[TIMEOUT] No response after {timeout}s")
        logger.warning(f"[CHECK] Make sure EA is running and FILE_COMMON is enabled")
        return None
    
    async def test_connection(self):
        """Test EA connection"""
        print("\n" + "=" * 60)
        print("TESTING EA CONNECTION")
        print("=" * 60)
        
        # Test 1: Get account info
        print("\n1. Requesting account info...")
        signal = {'action': 'GET_ACCOUNT_INFO'}
        signal_id = self.write_signal(signal)
        
        if signal_id > 0:
            response = await self.wait_for_response(signal_id, timeout=3.0)
            if response and response.get('status') == 'success':
                print(f"   SUCCESS! Connected to account: {response.get('account')}")
                print(f"   Balance: EUR {response.get('balance', 0):.2f}")
                print(f"   Equity: EUR {response.get('equity', 0):.2f}")
                return True
            else:
                print("   FAILED - No response from EA")
                print("\n   Troubleshooting:")
                print("   1. Is EA attached to a chart? (Should see smiley face)")
                print("   2. Is 'Allow automated trading' enabled?")
                print("   3. Check EA Experts tab for any errors")
                print(f"   4. Check if signal file exists: {SIGNAL_FILE}")
                return False
        
        return False


async def main():
    """Test the common folder connector"""
    connector = SignalConnectorCommon()
    
    print("MT5 Signal Connector - Common Folder Version")
    print("This should work with the EA!")
    
    # Test connection
    success = await connector.test_connection()
    
    if success:
        print("\n" + "=" * 60)
        print("CONNECTION SUCCESSFUL!")
        print("EA is responding correctly")
        print("You can now trade without connection conflicts!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("CONNECTION FAILED")
        print("Please check the EA setup")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())