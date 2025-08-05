from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
48H CRYPTO STRATEGY - Sinun strategiasi automatisoituna
Account 107034605 - Viikonloppu crypto trading
"""

import MetaTrader5 as mt5
import asyncio
import logging
from datetime import datetime, timezone, timedelta
import random

# MT5 Configuration
MT5_LOGIN = 107034605
MT5_PASSWORD = "RcEw_s7w"
MT5_SERVER = "Ava-Demo 1-MT5"

# Trading Strategy Parameters
CRYPTO_SYMBOLS = ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD"]
POSITION_SIZE = 0.05  # Aggressiivisempi koko viikonloppuna
MAGIC_NUMBER = 20250802

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(f'crypto_48h_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Crypto48HStrategy:
    """48 tunnin crypto strategia"""
    
    def __init__(self):
        self.connected = False
        self.start_time = datetime.now(timezone.utc)
        self.end_time = self.start_time + timedelta(hours=48)
        self.trades_made = 0
        self.winning_trades = 0
        self.starting_balance = 0.0
        self.session_profit = 0.0
        
    def connect_mt5(self):
        """Yhdist MT5"""
        try:
            if not mt5.initialize():
                return False
            
            authorized = mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
            if not authorized:
                return False
            
            account = mt5.account_info()
            self.starting_balance = account.equity
            self.connected = True
            
            logger.info(f"ROCKET 48H CRYPTO STRATEGY KYNNISTYY")
            logger.info(f"CHART Tili: {account.login}")
            logger.info(f"MONEY Alkusaldo: EUR{account.equity:.2f}")
            logger.info(f" Aloitus: {self.start_time.strftime('%H:%M:%S %d.%m.%Y')}")
            logger.info(f" Lopetus: {self.end_time.strftime('%H:%M:%S %d.%m.%Y')}")
            logger.info(f"TARGET Symbolit: {', '.join(CRYPTO_SYMBOLS)}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Yhteys eponnistui: {e}")
            return False
    
    def analyze_crypto_momentum(self, symbol):
        """Analysoi crypto momentum - sinun strategiasi"""
        try:
            # Hae viimeisimmt hinnat
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
            if rates is None or len(rates) < 10:
                return "HOLD"
            
            # Yksinkertainen momentum analyysi
            recent_prices = [rate['close'] for rate in rates[-10:]]
            current_price = recent_prices[-1]
            avg_price = sum(recent_prices) / len(recent_prices)
            
            # Volatiliteetti
            price_changes = [abs(recent_prices[i] - recent_prices[i-1]) for i in range(1, len(recent_prices))]
            volatility = sum(price_changes) / len(price_changes) / current_price
            
            # Trendi
            if current_price > avg_price * 1.002:  # 0.2% yli keskiarvon
                if volatility > 0.001:  # Riittvsti liikett
                    return "BUY"
            elif current_price < avg_price * 0.998:  # 0.2% alle keskiarvon
                if volatility > 0.001:
                    return "SELL"
            
            return "HOLD"
            
        except Exception as e:
            logger.error(f"Analyysi eponnistui {symbol}: {e}")
            return "HOLD"
    
    def place_crypto_order(self, symbol, direction):
        """Tee crypto kauppa"""
        try:
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                return False
            
            if direction == "BUY":
                price = tick.ask
                order_type = mt5.ORDER_TYPE_BUY
                sl = price * 0.99   # 1% stop loss
                tp = price * 1.025  # 2.5% take profit (aggressiivinen)
            else:
                price = tick.bid
                order_type = mt5.ORDER_TYPE_SELL
                sl = price * 1.01   # 1% stop loss
                tp = price * 0.975  # 2.5% take profit
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": POSITION_SIZE,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 50,
                "magic": MAGIC_NUMBER,
                "comment": f"48H {direction} #{self.trades_made + 1}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.trades_made += 1
                logger.info(f"OK KAUPPA #{self.trades_made}: {direction} {symbol} @ {price:.5f}")
                logger.info(f"   SL: {sl:.5f} | TP: {tp:.5f} | Tiketti: {result.order}")
                return True
            else:
                logger.warning(f"ERROR {symbol} {direction} eponnistui: {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"Kauppa virhe: {e}")
            return False
    
    def check_session_performance(self):
        """Tarkista session suorituskyky"""
        try:
            account = mt5.account_info()
            if not account:
                return
            
            current_equity = account.equity
            self.session_profit = current_equity - self.starting_balance
            session_return = (self.session_profit / self.starting_balance) * 100
            
            # Laske avoimien positioiden tulos
            positions = mt5.positions_get()
            open_profit = sum([pos.profit for pos in positions]) if positions else 0
            
            # Laske voittavat kaupat historiasta  
            elapsed_hours = (datetime.now(timezone.utc) - self.start_time).total_seconds() / 3600
            
            logger.info(f"\nCHART SESSION STATUS ({elapsed_hours:.1f}h / 48h)")
            logger.info(f"MONEY Alkusaldo: EUR{self.starting_balance:.2f}")
            logger.info(f"MONEY Nyt: EUR{current_equity:.2f}")
            logger.info(f"GRAPH_UP Session P&L: EUR{self.session_profit:.2f} ({session_return:+.2f}%)")
            logger.info(f"CHART Kauppoja: {self.trades_made}")
            logger.info(f" Avoimia: {len(positions) if positions else 0}")
            logger.info(f" Avoimet P&L: EUR{open_profit:.2f}")
            
            # Viikkoprojektio
            if elapsed_hours > 0:
                hourly_return = self.session_profit / elapsed_hours
                weekly_projection = hourly_return * 168
                logger.info(f"CHART Viikkoprojektio: EUR{weekly_projection:.2f}")
                
                if weekly_projection >= 10000:
                    logger.info("TARGET 10KEUR TAVOITE SAAVUTETTAVISSA!")
                else:
                    progress = (weekly_projection / 10000) * 100
                    logger.info(f"TARGET Tavoite edistyminen: {progress:.1f}%")
            
        except Exception as e:
            logger.error(f"Suorituskyvyn tarkistus eponnistui: {e}")
    
    async def trading_cycle(self):
        """Yksi kaupankyntikierros"""
        try:
            logger.info(f"\n ANALYSOIDAAN CRYPTO MARKKINOITA...")
            
            # Analysoi jokainen crypto symboli
            for symbol in CRYPTO_SYMBOLS:
                direction = self.analyze_crypto_momentum(symbol)
                
                if direction in ["BUY", "SELL"]:
                    # Tarkista ett ei ole jo positiota
                    positions = mt5.positions_get(symbol=symbol)
                    if not positions or len(positions) == 0:
                        logger.info(f"TARGET {symbol} signaali: {direction}")
                        success = self.place_crypto_order(symbol, direction)
                        if success:
                            await asyncio.sleep(2)  # Pieni tauko onnistuneen kaupan jlkeen
                    else:
                        logger.info(f" {symbol} - Positio jo auki")
                else:
                    logger.info(f" {symbol} - Ei signaalia (HOLD)")
                
                await asyncio.sleep(1)  # Pieni tauko symbolien vlill
                
        except Exception as e:
            logger.error(f"Kaupankyntikierros eponnistui: {e}")
    
    async def main_48h_loop(self):
        """48 tunnin psilmukka"""
        logger.info("ROCKET 48H CRYPTO STRATEGY ALKAA!")
        
        try:
            cycle = 0
            while datetime.now(timezone.utc) < self.end_time:
                cycle += 1
                
                current_time = datetime.now(timezone.utc)
                remaining = self.end_time - current_time
                remaining_hours = remaining.total_seconds() / 3600
                
                logger.info(f"\n>>> KIERROS {cycle} - {remaining_hours:.1f}h jljell <<<")
                
                # Kaupankyntikierros
                await self.trading_cycle()
                
                # Status pivitys joka 5. kierros
                if cycle % 5 == 0:
                    self.check_session_performance()
                
                # Odota 3 minuuttia seuraavaan kierrokseen
                logger.info(" Seuraava analyysi 3 minuutin pst...")
                await asyncio.sleep(180)  # 3 minuuttia
                
        except KeyboardInterrupt:
            logger.info("\n MANUAALINEN PYSYTYS")
        except Exception as e:
            logger.error(f"Psilmukka virhe: {e}")
        finally:
            await self.session_summary()
    
    async def session_summary(self):
        """48h session yhteenveto"""
        try:
            account = mt5.account_info()
            final_equity = account.equity if account else self.starting_balance
            total_profit = final_equity - self.starting_balance
            total_return = (total_profit / self.starting_balance) * 100
            
            duration = datetime.now(timezone.utc) - self.start_time
            hours = duration.total_seconds() / 3600
            
            logger.info("\n" + " 48H CRYPTO STRATEGY PTTYNYT " + "=" * 30)
            logger.info(f" Kesto: {hours:.1f} tuntia")
            logger.info(f"MONEY Aloitussaldo: EUR{self.starting_balance:.2f}")
            logger.info(f"MONEY Lopetussaldo: EUR{final_equity:.2f}")
            logger.info(f"GRAPH_UP Kokonaisvoitto: EUR{total_profit:.2f} ({total_return:+.2f}%)")
            logger.info(f"TARGET Kauppoja yhteens: {self.trades_made}")
            
            # Viikkoprojektio
            if hours > 0:
                hourly_return = total_profit / hours
                weekly_projection = hourly_return * 168
                logger.info(f"CHART Viikkoprojektio: EUR{weekly_projection:.2f}")
                
                target_achievement = (weekly_projection / 10000) * 100
                logger.info(f"TARGET 10kEUR tavoite: {target_achievement:.1f}% toteutuma")
            
            # Validointi
            if total_profit > 0 and hours >= 12:
                logger.info("\nOK STRATEGIA ONNISTUI!")
                logger.info("- Positiivinen tuotto saavutettu")
                logger.info("- Automaatio toimi moitteettomasti")
                logger.info("- 48h crypto kaupankynti validoitu")
            else:
                logger.info("\nWARNING STRATEGIA OSITTAIN ONNISTUNUT")
                logger.info("- Tekninen toteutus onnistui")
                logger.info("- Strategia kaipaa hienost")
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Yhteenveto eponnistui: {e}")
        finally:
            mt5.shutdown()

async def main():
    print("48H CRYPTO STRATEGY")
    print("Sinun strategiasi automatisoituna!")
    print("=" * 50)
    print("Tili: 107034605")
    print("Kesto: 48 tuntia")
    print("Symbolit: BTC, ETH, XRP, LTC")
    print("Analyysi: 3 min vlein")
    print("=" * 50)
    print()
    
    strategy = Crypto48HStrategy()
    
    if strategy.connect_mt5():
        print("OK Yhteys OK - Aloitetaan 48h strategia!")
        print("Paina Ctrl+C pysyttksesi")
        print()
        await strategy.main_48h_loop()
    else:
        print("ERROR Yhteys eponnistui")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(main())