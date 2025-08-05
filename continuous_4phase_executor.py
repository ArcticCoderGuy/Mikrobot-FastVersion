#!/usr/bin/env python3
"""
CONTINUOUS 4-PHASE SIGNAL EXECUTOR
Real-time monitoring and execution of all 4-phase signals with YLIPIP triggers
"""

import sys
import json
import re
import time
import MetaTrader5 as mt5
from datetime import datetime
import threading
import os

# ASCII-only output enforcement
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    """Ensure ASCII-only output"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {ascii_text}")

class FourPhaseExecutor:
    def __init__(self):
        self.signal_path = r"C:\Users\HP\AppData\Roaming\MetaQuotes\Terminal\Common\Files\mikrobot_4phase_signal.json"
        self.last_processed = {}
        self.running = True
        
        # Initialize MT5
        if not mt5.initialize():
            ascii_print("FAILED to initialize MT5")
            sys.exit(1)
        
        ascii_print("=== CONTINUOUS 4-PHASE EXECUTOR STARTED ===")
        
    def read_signal_file(self):
        """Read and parse the signal file with proper encoding"""
        try:
            if not os.path.exists(self.signal_path):
                return None
                
            with open(self.signal_path, 'rb') as f:
                content = f.read()
            
            # Handle UTF-16LE encoding with null bytes
            content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
            content_str = re.sub(r'[^\x20-\x7E{}":,.\-\s]', '', content_str)
            
            # Clean up extra spaces in JSON
            content_str = re.sub(r'\s+', ' ', content_str)
            content_str = content_str.strip()
            
            if not content_str:
                return None
                
            signal_data = json.loads(content_str)
            return signal_data
            
        except Exception as e:
            ascii_print(f"WARNING: Error reading signal file: {e}")
            return None

    def calculate_position_size(self, account_balance, symbol):
        """Calculate position size using 0.55% risk and dynamic ATR"""
        risk_percentage = 0.0055  # 0.55%
        risk_amount = account_balance * risk_percentage
        
        # ATR values by symbol
        atr_map = {
            'EURUSD': 8, 'GBPUSD': 8, 'USDCAD': 8, 'AUDUSD': 8,
            'EURJPY': 12, 'GBPJPY': 15, 'USDJPY': 10,
            'EURGBP': 6, 'NZDUSD': 8, 'USDCHF': 8
        }
        
        atr_pips = atr_map.get(symbol, 8)
        
        # Pip values
        if 'JPY' in symbol:
            pip_value = 100  # JPY pairs
        else:
            pip_value = 10   # USD pairs
        
        lot_size = risk_amount / (atr_pips * pip_value)
        return round(max(0.01, min(lot_size, 50.0)), 2), atr_pips

    def execute_trade(self, signal):
        """Execute trade based on signal"""
        try:
            # Get account info
            account_info = mt5.account_info()
            if not account_info:
                ascii_print("FAILED to get account info")
                return False
            
            symbol = signal['symbol']
            current_price = float(signal['current_price'])
            direction = signal['trade_direction']
            
            # Calculate position size
            lot_size, atr_pips = self.calculate_position_size(account_info.balance, symbol)
            
            ascii_print(f"Executing {symbol} {direction} - Lot Size: {lot_size} (ATR: {atr_pips})")
            
            # Determine order type
            if direction == 'BULL':
                order_type = mt5.ORDER_TYPE_BUY
                stop_loss = current_price - (atr_pips * (0.01 if 'JPY' in symbol else 0.0001))
                take_profit = current_price + (atr_pips * 2 * (0.01 if 'JPY' in symbol else 0.0001))
            else:  # BEAR
                order_type = mt5.ORDER_TYPE_SELL
                stop_loss = current_price + (atr_pips * (0.01 if 'JPY' in symbol else 0.0001))
                take_profit = current_price - (atr_pips * 2 * (0.01 if 'JPY' in symbol else 0.0001))
            
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": current_price,
                "sl": stop_loss,
                "tp": take_profit,
                "deviation": 20,
                "magic": 20250805,
                "comment": f"MIKROBOT_4PHASE_{direction}_AUTO",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK
            }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                ascii_print(f"Order FAILED: {result.retcode} - {result.comment}")
                return False
            
            ascii_print(f"SUCCESS: {symbol} {direction} - Ticket: {result.order} - Price: {result.price}")
            return True
            
        except Exception as e:
            ascii_print(f"ERROR executing trade: {e}")
            return False

    def process_signal(self, signal):
        """Process and validate signal for execution"""
        if not signal:
            return False
        
        # Check if YLIPIP is triggered
        if not signal.get('phase_4_ylipip', {}).get('triggered'):
            return False
        
        # Create unique identifier for this signal
        signal_id = f"{signal['symbol']}_{signal['timestamp']}_{signal['trade_direction']}"
        
        # Check if already processed
        if signal_id in self.last_processed:
            return False
        
        ascii_print(f"NEW SIGNAL: {signal['symbol']} {signal['trade_direction']} - YLIPIP TRIGGERED")
        ascii_print(f"M5 BOS: {signal['phase_1_m5_bos']['time']} @ {signal['phase_1_m5_bos']['price']}")
        ascii_print(f"M1 Break: {signal['phase_2_m1_break']['time']} @ {signal['phase_2_m1_break']['price']}")
        ascii_print(f"M1 Retest: {signal['phase_3_m1_retest']['time']} @ {signal['phase_3_m1_retest']['price']}")
        ascii_print(f"YLIPIP: {signal['phase_4_ylipip']['target']} (Current: {signal['current_price']})")
        
        # Execute the trade
        success = self.execute_trade(signal)
        
        # Mark as processed regardless of success
        self.last_processed[signal_id] = datetime.now()
        
        # Clean old processed signals (keep last 100)
        if len(self.last_processed) > 100:
            oldest_keys = sorted(self.last_processed.keys(), 
                               key=lambda k: self.last_processed[k])[:50]
            for key in oldest_keys:
                del self.last_processed[key]
        
        return success

    def monitor_signals(self):
        """Main monitoring loop"""
        ascii_print("Monitoring for 4-phase signals with YLIPIP triggers...")
        
        while self.running:
            try:
                signal = self.read_signal_file()
                if signal:
                    self.process_signal(signal)
                
                time.sleep(1)  # Check every second
                
            except KeyboardInterrupt:
                ascii_print("Stopping signal monitor...")
                self.running = False
                break
            except Exception as e:
                ascii_print(f"Monitor error: {e}")
                time.sleep(5)
        
        mt5.shutdown()
        ascii_print("Signal monitor stopped")

def main():
    executor = FourPhaseExecutor()
    
    try:
        executor.monitor_signals()
    except KeyboardInterrupt:
        ascii_print("Shutting down...")
        executor.running = False

if __name__ == "__main__":
    main()