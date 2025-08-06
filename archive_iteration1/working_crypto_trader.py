from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
TOIMIVA KRYPTO TRADER - Korjaa fill policy ja symboliongelmat
"""

import MetaTrader5 as mt5
import asyncio
import logging
from datetime import datetime
import time
import random

# MT5 Configuration
MT5_LOGIN = 95244786
MT5_PASSWORD = "Ua@tOnLp"
MT5_SERVER = "Ava-Demo 1-MT5"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkingCryptoTrader:
    
    def __init__(self):
        self.connected = False
        self.trades_made = 0
        self.available_symbols = []
        
    def connect_and_setup(self):
        """Yhdist ja selvit kytettviss olevat symbolit"""
        try:
            logger.info("Yhdistetn MT5:een...")
            
            if not mt5.initialize():
                logger.error(f"MT5 init failed: {mt5.last_error()}")
                return False
            
            authorized = mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
            if not authorized:
                logger.error(f"Login failed: {mt5.last_error()}")
                return False
            
            account = mt5.account_info()
            logger.info(f"OK Yhdistetty tiliin: {account.login}")
            logger.info(f"MONEY Saldo: EUR{account.balance:.2f}")
            
            # Etsi kytettviss olevat symbolit
            self.find_tradeable_symbols()
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Yhteys eponnistui: {e}")
            return False
    
    def find_tradeable_symbols(self):
        """Etsi kaikki kaupankyntiin soveltuvat symbolit"""
        logger.info("Etsitn kytettviss olevia symboleja...")
        
        # Hae kaikki symbolit
        all_symbols = mt5.symbols_get()
        
        # Testaa erilaisia crypto-symboleita
        test_symbols = [
            "BTCUSD", "ETHUSD", "XRPUSD", "ADAUSD", "LTCUSD",
            "Bitcoin", "Ethereum", "Ripple", "EURUSD", "GBPUSD", 
            "USDJPY", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF"
        ]
        
        self.available_symbols = []
        
        for symbol in test_symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is not None:
                if mt5.symbol_select(symbol, True):
                    tick = mt5.symbol_info_tick(symbol)
                    if tick and tick.ask > 0:
                        self.available_symbols.append(symbol)
                        logger.info(f"OK {symbol} - Hinta: {tick.ask:.5f}")
        
        if not self.available_symbols:
            logger.warning("Ei lytynyt crypto-symboleita, etsitn mit tahansa...")
            # Jos ei cryptoja, kyt forex-pareja
            for symbol_obj in all_symbols[:20]:  # Testaa 20 ensimmist
                symbol = symbol_obj.name
                if mt5.symbol_select(symbol, True):
                    tick = mt5.symbol_info_tick(symbol)
                    if tick and tick.ask > 0:
                        self.available_symbols.append(symbol)
                        logger.info(f"OK {symbol} - Hinta: {tick.ask:.5f}")
                        if len(self.available_symbols) >= 5:
                            break
        
        logger.info(f"CHART Kytettviss {len(self.available_symbols)} symbolia:")
        for symbol in self.available_symbols:
            logger.info(f"   - {symbol}")
    
    def place_market_order(self, symbol, order_type, volume):
        """Tee market order korjatulla fill policylla"""
        try:
            # Hae symbolin tiedot
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                logger.error(f"Ei symbolitietoja: {symbol}")
                return False
            
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                logger.error(f"Ei hintatietoa: {symbol}")
                return False
            
            # Valitse hinta ja suunta
            if order_type == mt5.ORDER_TYPE_BUY:
                price = tick.ask
                type_str = "BUY"
            else:
                price = tick.bid
                type_str = "SELL"
            
            # Korjattu kauppapyynt
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "deviation": 50,  # Suurempi poikkeama
                "magic": 20250802,
                "comment": f"Weekend {type_str} {self.trades_made + 1}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,  # Fill or Kill
            }
            
            # Jos FOK ei toimi, kokeile muita
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                # Kokeile eri fill mode
                request["type_filling"] = mt5.ORDER_FILLING_IOC
                result = mt5.order_send(request)
                
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    # Kokeile ilman fill modea
                    del request["type_filling"]
                    result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.trades_made += 1
                logger.info(f"OK KAUPPA #{self.trades_made}: {type_str} {symbol} @ {price:.5f}")
                logger.info(f"   Tiketti: {result.order}")
                return True
            else:
                logger.error(f"ERROR Kauppa eponnistui: {result.comment} (code: {result.retcode})")
                return False
                
        except Exception as e:
            logger.error(f"Kauppavirhe: {e}")
            return False
    
    async def trading_session(self):
        """Kaupankyntisessio toimivilla symboleilla"""
        if not self.connected or not self.available_symbols:
            logger.error("Ei yhteytt tai symboleita!")
            return
        
        logger.info(f"\nROCKET ALOITETAAN KAUPANKYNTI {len(self.available_symbols)} SYMBOLILLA")
        logger.info("=" * 60)
        
        try:
            while True:
                # Valitse satunnainen kytettviss oleva symboli
                symbol = random.choice(self.available_symbols)
                
                # Valitse suunta
                order_type = mt5.ORDER_TYPE_BUY if random.random() > 0.5 else mt5.ORDER_TYPE_SELL
                
                # Tee kauppa
                logger.info(f"\nYritetn kauppaa: {symbol}")
                success = self.place_market_order(symbol, order_type, 0.01)  # Pienempi volume
                
                if success:
                    logger.info(f"CHART Onnistuneita kauppoja: {self.trades_made}")
                else:
                    logger.warning(f"Kauppa eponnistui symbolilla {symbol}")
                
                # Nyt avoimet positiot
                positions = mt5.positions_get()
                if positions:
                    logger.info(f"GRAPH_UP Avoimia positioita: {len(positions)}")
                    total_profit = sum([pos.profit for pos in positions])
                    logger.info(f"MONEY Yhteisvoitto: EUR{total_profit:.2f}")
                
                # Odota 30 sekuntia
                await asyncio.sleep(30)
                
        except KeyboardInterrupt:
            logger.info(f"\n Kaupankynti lopetettu")
            logger.info(f"Yhteens {self.trades_made} onnistunutta kauppaa")
            
            # Nyt lopputilanne
            positions = mt5.positions_get()
            if positions:
                logger.info(f"CHART Avoimia positioita lopussa: {len(positions)}")
                for pos in positions:
                    logger.info(f"   {pos.symbol}: {pos.profit:.2f} EUR")
        
        finally:
            mt5.shutdown()
            logger.info("MT5 yhteys suljettu")

async def main():
    print("WORKING CRYPTO TRADER")
    print("Korjaa fill policy ja lyt toimivat symbolit")
    print()
    
    trader = WorkingCryptoTrader()
    
    if trader.connect_and_setup():
        print(f"Lytyi {len(trader.available_symbols)} symbolia")
        print("Aloitetaan kaupankynti...")
        print("Paina Ctrl+C lopettaaksesi\n")
        await trader.trading_session()
    else:
        print("Setup eponnistui")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(main())