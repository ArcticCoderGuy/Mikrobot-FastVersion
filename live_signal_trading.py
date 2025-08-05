"""
Live Signal Trading using existing EA connection
NO CONNECTION CONFLICTS - You can monitor on terminal AND mobile!
"""

import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
import logging

# Use existing mikrobot signal system - CORRECTED PATHS
MQL5_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files")
SIGNAL_FILE = MQL5_PATH / "mikrobot_fastversion_signal.json"
STATUS_FILE = MQL5_PATH / "mikrobot_status.txt"
MESSAGE_FILE = MQL5_PATH / "mikrobot_message.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveSignalTrader:
    """Trade via signals - no MT5 connection needed!"""
    
    def __init__(self):
        self.signal_id = 0
        logger.info("[INIT] Live Signal Trader - No connection conflicts!")
        logger.info(f"[INIT] Using signal file: {SIGNAL_FILE}")
        
    async def check_ea_status(self):
        """Check if EA is responding"""
        if STATUS_FILE.exists():
            with open(STATUS_FILE, 'r') as f:
                status = f.read()
            
            if "CONNECTION VERIFIED" in status:
                logger.info("[STATUS] EA Connection verified!")
                return True
        
        logger.error("[ERROR] EA not responding - check MT5")
        return False
    
    def send_trading_signal(self, action: str, symbol: str, volume: float, 
                          order_type: str, sl: float = 0, tp: float = 0):
        """Send trading signal to EA"""
        self.signal_id += 1
        
        signal = {
            "id": self.signal_id,
            "timestamp": datetime.now().isoformat(),
            "command": "TRADE",
            "action": action,
            "symbol": symbol,
            "volume": volume,
            "order_type": order_type,
            "sl": sl,
            "tp": tp,
            "magic": 20250802,
            "comment": f"Mikrobot #{self.signal_id}"
        }
        
        # Write signal
        with open(SIGNAL_FILE, 'w') as f:
            json.dump(signal, f, indent=2)
        
        logger.info(f"[SIGNAL] Sent: {action} {symbol} {volume} lots")
        return self.signal_id
    
    async def demo_trading_session(self):
        """Demo trading session - you can watch in MT5!"""
        print("\n" + "=" * 60)
        print("LIVE SIGNAL TRADING - NO CONNECTION CONFLICTS!")
        print("=" * 60)
        print("You can now monitor trades on:")
        print("- Windows MT5 Terminal")
        print("- iPhone MT5 App")
        print("- Both at the same time!")
        print("=" * 60)
        
        # Check EA status
        if not await self.check_ea_status():
            print("\nERROR: EA not responding")
            print("Please check that an EA is running in MT5")
            return
        
        print("\nEA Connection verified!")
        print("Starting demo trading...")
        
        # Demo: Send some signals
        symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        
        for i in range(3):
            symbol = symbols[i % len(symbols)]
            
            # Send buy signal
            print(f"\n[{i+1}] Sending BUY signal for {symbol}...")
            signal_id = self.send_trading_signal(
                action="OPEN",
                symbol=symbol,
                volume=0.01,
                order_type="BUY"
            )
            
            # Wait a bit
            await asyncio.sleep(5)
            
            # Check for response
            if MESSAGE_FILE.exists():
                with open(MESSAGE_FILE, 'r') as f:
                    response = json.load(f)
                print(f"EA Response: {response.get('message', 'No message')}")
        
        print("\n" + "=" * 60)
        print("Demo complete!")
        print("Check your MT5 terminal for the trades")
        print("They should be visible on mobile too!")
        print("=" * 60)


async def main():
    """Main function"""
    trader = LiveSignalTrader()
    
    # Run demo
    await trader.demo_trading_session()


if __name__ == "__main__":
    print("MIKROBOT LIVE SIGNAL TRADING")
    print("This solves the two-user connection problem!")
    
    asyncio.run(main())