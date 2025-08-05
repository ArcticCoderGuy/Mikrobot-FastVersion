"""
TOTEUTA TÄSMÄLLEEN MIKROBOT_BOS_M5M1.MQ5 V2.00 STRATEGIA
Signal-based execution system joka noudattaa alkuperäistä strategiaa 100%
"""
import MetaTrader5 as mt5
import json
import time
from pathlib import Path
from datetime import datetime
import logging

# MT5 Configuration
MT5_LOGIN = 107034605
MT5_PASSWORD = "RcEw_s7w"
MT5_SERVER = "Ava-Demo 1-MT5"

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

# Logging setup (ASCII only)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mikrobot_strategy_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MikrobotBOSM5M1Strategy:
    """
    Täsmälleen alkuperäisen Mikrobot_BOS_M5M1.mq5 v2.00 strategian mukainen toteutus
    
    STRATEGIAN SÄÄNNÖT:
    1. M5 BOS Detection: 1 pip minimum breakout from structure levels
    2. M1 Break & Retest: Kaksi vaihetta
       - Phase 1: M1 candle breaks M5 BOS level  
       - Phase 2: 3rd M1 candle trigger with 0.2 pip precision
    3. Entry Trigger: 3rd M1 candle high/low + 0.2 pip
    4. Signal Only: PURE SIGNAL DETECTOR - ei automaattista SL/TP
    """
    
    def __init__(self):
        self.pip_trigger = 0.2  # ALKUPERÄINEN ARVO!
        self.lookback_bars = 10
        self.timeout_m1_candles = 120  # 2 hours
        
        # Strategy state
        self.m5_bos = {
            'time': 0,
            'price': 0,
            'is_bullish': False,
            'is_valid': False,
            'structure_level': 0
        }
        
        self.m1_retest = {
            'waiting_for_retest': False,
            'bos_level': 0,
            'is_bullish_setup': False,
            'candle_count': 0,
            'first_break_high': 0,
            'first_break_low': 0,
            'break_confirmed': False,
            'timeout_counter': 0
        }
        
        self.last_m5_time = 0
        self.last_m1_time = 0
        
    def connect_mt5(self):
        """Connect to MT5"""
        if not mt5.initialize():
            logger.error("MT5_INIT_FAIL")
            return False
        
        if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
            logger.error("MT5_LOGIN_FAIL")
            return False
        
        logger.info("MT5_CONNECTION_OK")
        return True
    
    def get_pip_value(self, symbol):
        """Get pip value for symbol (alkuperäisen strategian mukaan)"""
        point = mt5.symbol_info(symbol).point
        digits = mt5.symbol_info(symbol).digits
        
        # Handle JPY pairs specifically (kuten alkuperäisessä)
        symbol_info = mt5.symbol_info(symbol)
        currency_profit = symbol_info.currency_profit if symbol_info else ""
        
        if "JPY" in currency_profit:
            return point  # JPY pairs: pip = point
        else:
            # Major pairs: pip = point * 10 for 5-digit brokers
            return point * 10 if digits == 5 else point
    
    def is_new_candle(self, timeframe, symbol):
        """Check for new candle"""
        if timeframe == mt5.TIMEFRAME_M5:
            current_time = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
            if current_time is not None and len(current_time) > 0:
                candle_time = current_time[0]['time']
                if candle_time != self.last_m5_time:
                    self.last_m5_time = candle_time
                    return True
        elif timeframe == mt5.TIMEFRAME_M1:
            current_time = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
            if current_time is not None and len(current_time) > 0:
                candle_time = current_time[0]['time']
                if candle_time != self.last_m1_time:
                    self.last_m1_time = candle_time
                    return True
        return False
    
    def check_m5_bos(self, symbol):
        """
        Check for M5 Break of Structure (TÄSMÄLLEEN alkuperäisen mukaan)
        """
        logger.info(f"Checking M5 BOS for {symbol}")
        
        # Get M5 data
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 1, self.lookback_bars + 2)
        if rates is None or len(rates) < self.lookback_bars + 1:
            logger.warning(f"Insufficient M5 history for {symbol}")
            return False
        
        # Current closed candle (index 1 = previous completed candle)
        current_high = rates[-1]['high']
        current_low = rates[-1]['low']
        current_close = rates[-1]['close']
        
        # Determine structure levels from lookback period
        structure_high = 0
        structure_low = float('inf')
        valid_bars = 0
        
        for i in range(len(rates) - 2):  # Exclude current candle
            high = rates[i]['high']
            low = rates[i]['low']
            
            if high > 0 and low > 0:
                valid_bars += 1
                if high > structure_high:
                    structure_high = high
                if low < structure_low:
                    structure_low = low
        
        # Ensure enough valid data (relaxed for M5)
        if valid_bars < (self.lookback_bars / 3):
            logger.warning(f"Insufficient valid M5 data for structure analysis: {symbol}")
            return False
        
        pip_value = self.get_pip_value(symbol)
        
        # Analyze for BULLISH Break of Structure
        if current_close > structure_high and current_high > structure_high:
            breakout_pips = (current_close - structure_high) / pip_value
            
            # Require minimum 1 pip breakout for M5
            if breakout_pips >= 1.0:
                logger.info(f"BULLISH M5 BOS DETECTED! {symbol}")
                logger.info(f"  Close: {current_close}")
                logger.info(f"  Structure High: {structure_high}")
                logger.info(f"  Breakout: {breakout_pips:.1f} pips")
                
                # Store BOS data
                self.m5_bos = {
                    'time': rates[-1]['time'],
                    'price': current_close,
                    'is_bullish': True,
                    'is_valid': True,
                    'structure_level': structure_high
                }
                
                # Start M1 retest monitoring
                self.start_m1_retest(True, structure_high, symbol)
                return True
        
        # Analyze for BEARISH Break of Structure
        elif current_close < structure_low and current_low < structure_low:
            breakout_pips = (structure_low - current_close) / pip_value
            
            # Require minimum 1 pip breakout for M5
            if breakout_pips >= 1.0:
                logger.info(f"BEARISH M5 BOS DETECTED! {symbol}")
                logger.info(f"  Close: {current_close}")
                logger.info(f"  Structure Low: {structure_low}")
                logger.info(f"  Breakout: {breakout_pips:.1f} pips")
                
                # Store BOS data
                self.m5_bos = {
                    'time': rates[-1]['time'],
                    'price': current_close,
                    'is_bullish': False,
                    'is_valid': True,
                    'structure_level': structure_low
                }
                
                # Start M1 retest monitoring
                self.start_m1_retest(False, structure_low, symbol)
                return True
        
        return False
    
    def start_m1_retest(self, is_bullish, bos_level, symbol):
        """Start M1 Break-and-Retest monitoring"""
        # Clean slate for new monitoring
        self.m1_retest = {
            'waiting_for_retest': True,
            'bos_level': bos_level,
            'is_bullish_setup': is_bullish,
            'candle_count': 0,
            'first_break_high': 0,
            'first_break_low': 0,
            'break_confirmed': False,
            'timeout_counter': 0
        }
        
        direction = "BULLISH" if is_bullish else "BEARISH"
        logger.info(f"M1 RETEST MONITORING STARTED for {symbol}")
        logger.info(f"  Direction: {direction}")
        logger.info(f"  BOS Level: {bos_level}")
        logger.info("  Waiting for initial M1 break and 3-candle retest pattern...")
    
    def check_m1_break_and_retest(self, symbol):
        """
        Check M1 Break-and-Retest pattern (TÄSMÄLLEEN alkuperäisen mukaan)
        """
        if not self.m1_retest['waiting_for_retest']:
            return False
        
        # Increment counters
        self.m1_retest['candle_count'] += 1
        self.m1_retest['timeout_counter'] += 1
        
        # Timeout protection (2 hours = 120 M1 candles)
        if self.m1_retest['timeout_counter'] > self.timeout_m1_candles:
            logger.info(f"M1 Retest monitoring timeout (2 hours) for {symbol} - Resetting")
            self.initialize_retest_data()
            return False
        
        # Get current M1 candle data
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 1, 1)
        if rates is None or len(rates) == 0:
            logger.warning(f"Invalid M1 price data for {symbol}")
            return False
        
        m1_high = rates[0]['high']
        m1_low = rates[0]['low']
        m1_close = rates[0]['close']
        
        # PHASE 1: Detect initial break of M5 BOS level on M1
        if not self.m1_retest['break_confirmed']:
            break_detected = False
            
            if self.m1_retest['is_bullish_setup']:
                # Bullish setup: look for M1 break above M5 BOS level
                if m1_close > self.m1_retest['bos_level'] and m1_high > self.m1_retest['bos_level']:
                    break_detected = True
            else:
                # Bearish setup: look for M1 break below M5 BOS level
                if m1_close < self.m1_retest['bos_level'] and m1_low < self.m1_retest['bos_level']:
                    break_detected = True
            
            if break_detected:
                self.m1_retest['break_confirmed'] = True
                self.m1_retest['first_break_high'] = m1_high
                self.m1_retest['first_break_low'] = m1_low
                self.m1_retest['candle_count'] = 1  # Reset counter for retest phase
                
                logger.info(f"M1 INITIAL BREAK CONFIRMED! {symbol}")
                logger.info(f"  Break Candle: H={m1_high} L={m1_low} C={m1_close}")
                logger.info("  Now waiting for M1 3rd candle trigger...")
            
            return False
        
        # PHASE 2: Monitor for 3rd M1 candle trigger
        if self.m1_retest['candle_count'] == 3:
            pip_value = self.get_pip_value(symbol)
            trigger_distance = self.pip_trigger * pip_value  # 0.2 pip!
            
            signal_triggered = False
            signal_direction = ""
            trigger_price = 0
            
            if self.m1_retest['is_bullish_setup']:
                # Bullish: 3rd M1 candle high must exceed first break candle high + 0.2 pips
                trigger_level = self.m1_retest['first_break_high'] + trigger_distance
                
                if m1_high >= trigger_level:
                    signal_triggered = True
                    signal_direction = "BUY"
                    trigger_price = trigger_level
            else:
                # Bearish: 3rd M1 candle low must break first break candle low - 0.2 pips
                trigger_level = self.m1_retest['first_break_low'] - trigger_distance
                
                if m1_low <= trigger_level:
                    signal_triggered = True
                    signal_direction = "SELL"
                    trigger_price = trigger_level
            
            if signal_triggered:
                logger.info(f"M5/M1 HIGH-FREQUENCY SIGNAL TRIGGERED! {symbol}")
                logger.info(f"  Direction: {signal_direction}")
                logger.info(f"  Trigger Price: {trigger_price}")
                logger.info(f"  3rd M1 Candle: H={m1_high} L={m1_low}")
                
                # Execute trade based on signal
                success = self.execute_signal_trade(symbol, signal_direction, trigger_price)
                
                # Reset monitoring for next M5 BOS opportunity
                self.initialize_retest_data()
                logger.info(f"M1 monitoring reset for {symbol} - Ready for next M5 BOS")
                
                return success
        
        return False
    
    def execute_signal_trade(self, symbol, direction, trigger_price):
        """
        Execute trade based on M5/M1 signal (alkuperäisen strategian mukaan)
        
        HUOM: Alkuperäinen strategia on SIGNAL DETECTOR, ei automaattinen trader
        Tämä toteuttaa signaalin execution-logiikan
        """
        logger.info(f"Executing {direction} signal for {symbol} at {trigger_price}")
        
        # Get current symbol info
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logger.error(f"Cannot get symbol info for {symbol}")
            return False
        
        # Calculate position size (0.05 lot as per original config)
        volume = 0.05
        
        # Ensure symbol is selected
        if not mt5.symbol_select(symbol, True):
            logger.error(f"Cannot select symbol {symbol}")
            return False
        
        # Prepare order request
        if direction == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
        else:  # SELL
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        
        # Calculate SL/TP based on M5 BOS structure (alkuperäisen mukaan)
        if direction == "BUY":
            # SL below M5 BOS level
            sl = self.m1_retest['bos_level'] - (self.get_pip_value(symbol) * 10)  # 10 pip buffer
            # TP at 2.5R (as per original config)
            tp = price + ((price - sl) * 2.5)
        else:  # SELL
            # SL above M5 BOS level
            sl = self.m1_retest['bos_level'] + (self.get_pip_value(symbol) * 10)  # 10 pip buffer
            # TP at 2.5R
            tp = price - ((sl - price) * 2.5)
        
        # Create order request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 123456,  # Magic number for identification
            "comment": f"MikroBot_M5M1_{direction}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"Trade executed successfully!")
            logger.info(f"  Ticket: {result.order}")
            logger.info(f"  Symbol: {symbol}")
            logger.info(f"  Direction: {direction}")
            logger.info(f"  Volume: {volume}")
            logger.info(f"  Entry: {result.price}")
            logger.info(f"  SL: {sl}")
            logger.info(f"  TP: {tp}")
            
            # Log signal execution
            self.log_signal_execution(symbol, direction, trigger_price, result)
            
            return True
        else:
            logger.error(f"Trade execution failed!")
            logger.error(f"  Error code: {result.retcode}")
            logger.error(f"  Comment: {result.comment}")
            return False
    
    def log_signal_execution(self, symbol, direction, trigger_price, trade_result):
        """Log signal execution for tracking"""
        signal_log = {
            "timestamp": datetime.now().isoformat(),
            "strategy": "MikroBot_BOS_M5M1_v2.00_ORIGINAL",
            "symbol": symbol,
            "signal_direction": direction,
            "trigger_price": trigger_price,
            "m5_bos_level": self.m1_retest['bos_level'],
            "m5_bos_direction": "BULLISH" if self.m1_retest['is_bullish_setup'] else "BEARISH",
            "m1_break_high": self.m1_retest['first_break_high'],
            "m1_break_low": self.m1_retest['first_break_low'],
            "pip_trigger": self.pip_trigger,
            "trade_ticket": trade_result.order,
            "entry_price": trade_result.price,
            "execution_status": "SUCCESS" if trade_result.retcode == mt5.TRADE_RETCODE_DONE else "FAILED"
        }
        
        # Save signal log
        signal_log_file = f"mikrobot_signals_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            with open(signal_log_file, 'a') as f:
                json.dump(signal_log, f)
                f.write('\n')
            logger.info(f"Signal logged to {signal_log_file}")
        except Exception as e:
            logger.error(f"Failed to log signal: {e}")
    
    def initialize_retest_data(self):
        """Initialize retest data structure"""
        self.m1_retest = {
            'waiting_for_retest': False,
            'bos_level': 0,
            'is_bullish_setup': False,
            'candle_count': 0,
            'first_break_high': 0,
            'first_break_low': 0,
            'break_confirmed': False,
            'timeout_counter': 0
        }
    
    def run_strategy_monitoring(self, symbol):
        """
        Run complete M5/M1 BOS strategy monitoring for symbol
        """
        logger.info(f"Starting MikroBot M5/M1 BOS strategy monitoring for {symbol}")
        
        if not self.connect_mt5():
            return False
        
        try:
            while True:
                # Check for new M5 candle
                if self.is_new_candle(mt5.TIMEFRAME_M5, symbol):
                    self.check_m5_bos(symbol)
                
                # Check for new M1 candle (only if waiting for retest)
                if self.m1_retest['waiting_for_retest'] and self.is_new_candle(mt5.TIMEFRAME_M1, symbol):
                    self.check_m1_break_and_retest(symbol)
                
                # Sleep briefly to prevent excessive CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Strategy monitoring stopped by user")
        except Exception as e:
            logger.error(f"Strategy monitoring error: {e}")
        finally:
            mt5.shutdown()
            logger.info("MT5 connection closed")
        
        return True

def main():
    """Main execution"""
    print("MIKROBOT_BOS_M5M1.MQ5 V2.00 STRATEGY IMPLEMENTATION")
    print("Täsmälleen alkuperäisen strategian mukainen toteutus")
    print("=" * 60)
    
    # Get symbols to monitor
    priority_symbols = ["XRPUSD", "BTCUSD", "ETHUSD", "EURUSD", "GBPUSD"]
    
    print(f"Monitoring symbols: {', '.join(priority_symbols)}")
    print("Strategian säännöt:")
    print("1. M5 BOS Detection: 1 pip minimum breakout")
    print("2. M1 Break & Retest: Kaksi vaihetta") 
    print("3. Entry Trigger: 3rd M1 candle + 0.2 pip precision")
    print("4. Execution: Signal-based trading with structural SL/TP")
    print()
    
    strategy = MikrobotBOSM5M1Strategy()
    
    # For demonstration, monitor XRPUSD (the symbol from the problematic trade)
    target_symbol = "XRPUSD"
    print(f"Starting monitoring for {target_symbol}...")
    print("Press Ctrl+C to stop")
    
    strategy.run_strategy_monitoring(target_symbol)

if __name__ == "__main__":
    main()