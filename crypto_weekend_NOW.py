"""
WEEKEND CRYPTO TRADING - KÄYNNISTYY HETI
Account 107034605 - Viikonloppu kaupankäynti
"""

import json
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
import random
import time

# Signal files - CORRECTED PATH
MQL5_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files")
SIGNAL_FILE = MQL5_PATH / "mikrobot_fastversion_signal.json"

# Trading parameters
CRYPTO_SYMBOLS = ["BTCUSD", "ETHUSD", "XRPUSD", "ADAUSD", "LTCUSD"]
POSITION_SIZE = 0.05
TRADE_INTERVAL = 45  # sekuntia

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class CryptoWeekendTrader:
    
    def __init__(self):
        self.signal_id = 0
        self.trades_made = 0
        self.start_time = datetime.now()
        
    def send_trade_signal(self, symbol, direction):
        """Lähetä kauppasignaali"""
        self.signal_id += 1
        self.trades_made += 1
        
        signal = {
            "id": self.signal_id,
            "timestamp": datetime.now().isoformat(),
            "command": "TRADE",
            "action": "OPEN",
            "symbol": symbol,
            "order_type": direction,
            "volume": POSITION_SIZE,
            "magic": 20250802,
            "comment": f"Weekend Crypto {self.trades_made}"
        }
        
        with open(SIGNAL_FILE, 'w') as f:
            json.dump(signal, f, indent=2)
        
        logger.info(f"[TRADE {self.trades_made}] {direction} {symbol} - {POSITION_SIZE} lots")
    
    async def trading_loop(self):
        """Kaupankäynti silmukka"""
        logger.info("MIKROBOT WEEKEND CRYPTO - KÄYNNISTYY")
        logger.info("=" * 50)
        logger.info("Account: 107034605")
        logger.info("Symbols: BTC, ETH, XRP, ADA, LTC")
        logger.info("Volume: 0.05 lots per trade")
        logger.info("Interval: 45 seconds")
        logger.info("=" * 50)
        
        try:
            while True:
                # Valitse satunnainen symboli
                symbol = random.choice(CRYPTO_SYMBOLS)
                
                # Valitse suunta (60% BUY, 40% SELL viikonloppuna)
                direction = "BUY" if random.random() > 0.4 else "SELL"
                
                # Lähetä kauppasignaali
                self.send_trade_signal(symbol, direction)
                
                # Status update
                runtime = (datetime.now() - self.start_time).total_seconds() / 3600
                logger.info(f"[STATUS] Runtime: {runtime:.1f}h | Trades: {self.trades_made}")
                
                # Odota seuraavaa kauppaa
                await asyncio.sleep(TRADE_INTERVAL)
                
        except KeyboardInterrupt:
            runtime = (datetime.now() - self.start_time).total_seconds() / 3600
            logger.info("\nSTOP - Session complete")
            logger.info(f"Runtime: {runtime:.1f} hours")
            logger.info(f"Trades made: {self.trades_made}")
            logger.info("Check your MT5 for all trades!")

async def main():
    print("MIKROBOT CRYPTO WEEKEND")
    print("Automated trading starts NOW")
    print("Press Ctrl+C to stop")
    print("")
    
    trader = CryptoWeekendTrader()
    await trader.trading_loop()

if __name__ == "__main__":
    asyncio.run(main())