from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
DIRECT MT5 TRADING - Suora yhteys tiliin 107034605
Palaa alkuperiseen suoraan yhteytt kyttvn metodiin
"""

import MetaTrader5 as mt5
import asyncio
import logging
from datetime import datetime
import time
import random

# MT5 Configuration
MT5_LOGIN = 107034605
MT5_PASSWORD = "RcEw_s7w"
MT5_SERVER = "Ava-Demo 1-MT5"

# Trading parameters
CRYPTO_SYMBOLS = ["BTCUSD", "ETHUSD", "XRPUSD", "ADAUSD"]
POSITION_SIZE = 0.05
MAGIC_NUMBER = 20250802

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectMT5Trader:
    """Suora MT5 yhteys - ei signaaleja"""
    
    def __init__(self):
        self.connected = False
        self.trades_made = 0
        
    def connect_mt5(self):
        """Yhdist MT5:een"""
        try:
            logger.info("Yhdistetn MT5:een...")
            
            if not mt5.initialize():
                logger.error(f"MT5 init failed: {mt5.last_error()}")
                return False
            
            # Kirjaudu tilille
            authorized = mt5.login(
                login=MT5_LOGIN,
                password=MT5_PASSWORD,
                server=MT5_SERVER
            )
            
            if not authorized:
                logger.error(f"Login failed: {mt5.last_error()}")
                return False
            
            # Tarkista tili
            account = mt5.account_info()
            if account:
                logger.info(f"OK Yhdistetty tiliin: {account.login}")
                logger.info(f"MONEY Saldo: EUR{account.balance:.2f}")
                logger.info(f"GRAPH_UP Equity: EUR{account.equity:.2f}")
                
                # Tarkista historia
                positions = mt5.positions_get()
                if positions:
                    logger.info(f"CHART Avoimia positioita: {len(positions)}")
                else:
                    logger.info("CHART Ei avoimia positioita")
                
                self.connected = True
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Yhteys eponnistui: {e}")
            return False
    
    def place_order(self, symbol, order_type, volume):
        """Tee kauppa suoraan MT5:een"""
        try:
            # Hae nykyinen hinta
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                logger.error(f"Ei hintatietoa symbolille {symbol}")
                return False
            
            # Valitse hinta
            if order_type == mt5.ORDER_TYPE_BUY:
                price = tick.ask
                sl = price * 0.99  # 1% stop loss
                tp = price * 1.02  # 2% take profit
            else:
                price = tick.bid
                sl = price * 1.01  # 1% stop loss  
                tp = price * 0.98  # 2% take profit
            
            # Kauppaehto
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": MAGIC_NUMBER,
                "comment": f"Direct Trade {self.trades_made + 1}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Lhet kauppa
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.trades_made += 1
                order_type_str = "BUY" if order_type == mt5.ORDER_TYPE_BUY else "SELL"
                logger.info(f"OK KAUPPA #{self.trades_made}: {order_type_str} {symbol} @ {price:.5f}")
                logger.info(f"   Tiket: {result.order} | SL: {sl:.5f} | TP: {tp:.5f}")
                return True
            else:
                logger.error(f"ERROR Kauppa eponnistui: {result.comment} (code: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"Kauppavirhe: {e}")
            return False
    
    async def trading_session(self):
        """Kaupankyntisessio"""
        if not self.connected:
            logger.error("Ei yhteytt MT5:een!")
            return
        
        logger.info("\nROCKET ALOITETAAN SUORA KAUPANKYNTI")
        logger.info("=" * 50)
        logger.info("Tili: 107034605")
        logger.info("Symbolit: BTC, ETH, XRP, ADA")
        logger.info("Volume: 0.05 lots")
        logger.info("=" * 50)
        
        try:
            while True:
                # Valitse symboli
                symbol = random.choice(CRYPTO_SYMBOLS)
                
                # Valitse suunta
                order_type = mt5.ORDER_TYPE_BUY if random.random() > 0.5 else mt5.ORDER_TYPE_SELL
                
                # Tee kauppa
                success = self.place_order(symbol, order_type, POSITION_SIZE)
                
                if success:
                    logger.info(f"CHART Kauppoja yhteens: {self.trades_made}")
                
                # Odota 45 sekuntia
                await asyncio.sleep(45)
                
        except KeyboardInterrupt:
            logger.info(f"\n Kaupankynti lopetettu")
            logger.info(f"Yhteens {self.trades_made} kauppaa")
        
        finally:
            mt5.shutdown()
            logger.info("MT5 yhteys suljettu")

async def main():
    print("DIRECT MT5 TRADING")
    print("Suora yhteys tiliin 107034605")
    print("Ei signaaleja - suoraan MT5 API:in")
    print()
    
    trader = DirectMT5Trader()
    
    if trader.connect_mt5():
        print("Yhteys OK - aloitetaan kaupankynti")
        print("Paina Ctrl+C lopettaaksesi\n")
        await trader.trading_session()
    else:
        print("Yhteys eponnistui")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(main())