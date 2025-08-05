"""
Signal-Based MT5 Connector
Solves the two-user connection conflict
"""

import json
import os
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Signal file path - MT5 can access this location
SIGNAL_FILE = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/signal.json")
RESPONSE_FILE = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files/response.json")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalBasedMT5Connector:
    """Communicate with MT5 via signal files - no connection conflicts!"""
    
    def __init__(self):
        self.signal_id = 0
        self.ensure_directories()
        
    def ensure_directories(self):
        """Ensure signal directories exist"""
        SIGNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        
    def write_signal(self, signal: Dict[str, Any]) -> int:
        """Write trading signal for MT5 EA to execute"""
        try:
            self.signal_id += 1
            signal['id'] = self.signal_id
            signal['timestamp'] = datetime.now().isoformat()
            signal['status'] = 'pending'
            
            # Atomic write to prevent corruption
            temp_file = SIGNAL_FILE.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(signal, f, indent=2)
            
            # Atomic rename
            temp_file.replace(SIGNAL_FILE)
            
            logger.info(f"[SIGNAL] Written signal #{self.signal_id}: {signal['action']}")
            return self.signal_id
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to write signal: {e}")
            return -1
    
    async def wait_for_response(self, signal_id: int, timeout: float = 5.0) -> Optional[Dict]:
        """Wait for MT5 EA to process signal and respond"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if RESPONSE_FILE.exists():
                    with open(RESPONSE_FILE, 'r') as f:
                        response = json.load(f)
                    
                    if response.get('signal_id') == signal_id:
                        logger.info(f"[RESPONSE] Received for signal #{signal_id}: {response['status']}")
                        # Clear response file
                        RESPONSE_FILE.unlink()
                        return response
                        
            except Exception as e:
                logger.debug(f"Waiting for response: {e}")
            
            await asyncio.sleep(0.1)  # Check every 100ms
        
        logger.warning(f"[TIMEOUT] No response for signal #{signal_id}")
        return None
    
    async def place_order(self, symbol: str, action: str, volume: float, 
                         sl: Optional[float] = None, tp: Optional[float] = None) -> Dict:
        """Place order via signal file"""
        signal = {
            'action': 'PLACE_ORDER',
            'symbol': symbol,
            'order_type': action.upper(),  # BUY or SELL
            'volume': volume,
            'sl': sl,
            'tp': tp,
            'magic': 20250802,
            'comment': 'Mikrobot Signal'
        }
        
        signal_id = self.write_signal(signal)
        if signal_id > 0:
            response = await self.wait_for_response(signal_id)
            return response or {'status': 'timeout', 'signal_id': signal_id}
        
        return {'status': 'error', 'message': 'Failed to write signal'}
    
    async def get_account_info(self) -> Optional[Dict]:
        """Request account info via signal"""
        signal = {
            'action': 'GET_ACCOUNT_INFO'
        }
        
        signal_id = self.write_signal(signal)
        if signal_id > 0:
            response = await self.wait_for_response(signal_id, timeout=2.0)
            return response
        
        return None
    
    async def get_positions(self) -> Optional[Dict]:
        """Request open positions via signal"""
        signal = {
            'action': 'GET_POSITIONS'
        }
        
        signal_id = self.write_signal(signal)
        if signal_id > 0:
            response = await self.wait_for_response(signal_id, timeout=2.0)
            return response
        
        return None
    
    async def close_position(self, ticket: int) -> Dict:
        """Close position via signal"""
        signal = {
            'action': 'CLOSE_POSITION',
            'ticket': ticket
        }
        
        signal_id = self.write_signal(signal)
        if signal_id > 0:
            response = await self.wait_for_response(signal_id)
            return response or {'status': 'timeout', 'signal_id': signal_id}
        
        return {'status': 'error', 'message': 'Failed to write signal'}
    
    def clear_signals(self):
        """Clear any pending signals"""
        try:
            if SIGNAL_FILE.exists():
                SIGNAL_FILE.unlink()
            if RESPONSE_FILE.exists():
                RESPONSE_FILE.unlink()
            logger.info("[CLEANUP] Signal files cleared")
        except Exception as e:
            logger.error(f"[ERROR] Failed to clear signals: {e}")


async def test_signal_connector():
    """Test the signal-based connector"""
    connector = SignalBasedMT5Connector()
    
    print("Signal-Based MT5 Connector Test")
    print("=" * 50)
    print("This connector solves the two-user conflict!")
    print("You can monitor trades on terminal AND mobile")
    print("=" * 50)
    
    # Clear any old signals
    connector.clear_signals()
    
    # Test 1: Get account info
    print("\n1. Testing account info request...")
    info = await connector.get_account_info()
    if info:
        print(f"   Account: {info.get('account')}")
        print(f"   Balance: €{info.get('balance', 0):.2f}")
        print(f"   Status: {info.get('status')}")
    else:
        print("   No response - Make sure EA is running in MT5")
    
    # Test 2: Get positions
    print("\n2. Testing positions request...")
    positions = await connector.get_positions()
    if positions:
        print(f"   Open positions: {positions.get('count', 0)}")
        print(f"   Status: {positions.get('status')}")
    else:
        print("   No response - Make sure EA is running in MT5")
    
    # Test 3: Place a test order (small size)
    print("\n3. Testing order placement...")
    print("   Would place: BUY EURUSD 0.01 lots")
    print("   (Uncomment to test with real order)")
    
    # Uncomment to test real order:
    # result = await connector.place_order('EURUSD', 'BUY', 0.01)
    # print(f"   Result: {result}")
    
    print("\n" + "=" * 50)
    print("IMPORTANT: Install the MQL5 Expert Advisor")
    print("to complete the signal processing loop!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_signal_connector())