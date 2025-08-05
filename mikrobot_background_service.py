from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
MIKROBOT BACKGROUND SERVICE - 24/7 TRADING
==========================================
Continuous monitoring and execution of EA 4-phase signals
Full MIKROBOT_FASTVERSION.md compliance
"""

import MetaTrader5 as mt5
import json
import time
import os
from datetime import datetime
from pathlib import Path

class MikrobotBackgroundService:
    def __init__(self):
        self.signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
        self.last_signal_timestamp = None
        self.trade_log = []
        self.service_start_time = datetime.now()
        
    def log_message(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.trade_log.append(log_entry)
        
        # Keep last 100 log entries
        if len(self.trade_log) > 100:
            self.trade_log = self.trade_log[-100:]
    
    def initialize_service(self):
        """Initialize MT5 and service"""
        if not mt5.initialize():
            self.log_message("ERROR: Could not initialize MT5")
            return False
        
        account_info = mt5.account_info()
        self.log_message("MIKROBOT BACKGROUND SERVICE STARTED")
        self.log_message(f"Account: {account_info.login}")
        self.log_message(f"Balance: ${account_info.balance:.2f}")
        self.log_message(f"Server: {account_info.server}")
        self.log_message("Monitoring EA 4-phase signals...")
        self.log_message("MIKROBOT_FASTVERSION.md compliance: ACTIVE")
        return True
    
    def read_ea_signal(self):
        """Read and validate EA signal"""
        try:
            if not self.signal_file.exists():
                return None
                
            with open(self.signal_file, 'r', encoding='utf-16-le') as f:
                content = f.read()
                
            # Clean Unicode issues
            import re
            content = re.sub(r'\x00', '', content)
            content = re.sub(r' +', ' ', content)
            
            signal_data = json.loads(content)
            
            # Check if new signal
            if signal_data.get('timestamp') == self.last_signal_timestamp:
                return None
                
            # Validate 4-phase completion
            if (signal_data.get('phase_4_ylipip', {}).get('triggered') == True and
                signal_data.get('ylipip_trigger') == 0.60):
                return signal_data
                
        except Exception as e:
            self.log_message(f"Signal read error: {e}")
            
        return None
    
    def execute_signal_trade(self, signal_data):
        """Execute trade from EA signal"""
        symbol = signal_data['symbol']
        direction = signal_data['trade_direction']
        
        self.log_message(f"NEW 4-PHASE SIGNAL: {symbol} {direction}")
        self.log_message(f"Signal time: {signal_data['timestamp']}")
        
        # Get current price
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            self.log_message(f"ERROR: Cannot get price for {symbol}")
            return False
        
        # Calculate trade parameters
        if direction == 'BULL':
            order_type = mt5.ORDER_TYPE_BUY
            entry_price = tick.ask
        else:
            order_type = mt5.ORDER_TYPE_SELL
            entry_price = tick.bid
        
        # Position sizing - conservative 0.01 lots
        lot_size = 0.01
        
        # Calculate stops based on symbol type
        if 'JPY' in symbol:
            sl_distance = 0.08  # 8 pips for JPY pairs
        elif symbol.startswith('_'):  # CFD stocks
            sl_distance = 0.80  # 80 points for stocks
        else:
            sl_distance = 0.0008  # 8 pips for major pairs
        
        if direction == 'BULL':
            sl_price = entry_price - sl_distance
            tp_price = entry_price + (sl_distance * 2)  # 1:2 RR
        else:
            sl_price = entry_price + sl_distance
            tp_price = entry_price - (sl_distance * 2)
        
        self.log_message(f"Entry: {entry_price:.5f}, SL: {sl_price:.5f}, TP: {tp_price:.5f}")
        
        # Execute trade - try FOK first (works for most)
        order_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": order_type,
            "deviation": 20,
            "magic": 999888,
            "comment": f"{symbol}_MIKROBOT_AUTO",
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        result = mt5.order_send(order_request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log_message(f"FOK failed, trying IOC: {result.comment}")
            order_request["type_filling"] = mt5.ORDER_FILLING_IOC
            result = mt5.order_send(order_request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log_message(f"IOC failed, trying RETURN: {result.comment}")
            order_request["type_filling"] = mt5.ORDER_FILLING_RETURN
            result = mt5.order_send(order_request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.log_message(f"TRADE FAILED: {result.comment}")
            return False
        
        self.log_message(f"TRADE EXECUTED: Order {result.order}, Deal {result.deal}")
        self.log_message(f"Execution price: {result.price:.5f}")
        
        # Add SL/TP
        positions = mt5.positions_get(symbol=symbol)
        if positions:
            # Find the position we just created
            for pos in positions:
                if abs(pos.price_open - result.price) < 0.001:  # Match by price
                    modify_request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": symbol,
                        "position": pos.ticket,
                        "sl": sl_price,
                        "tp": tp_price,
                    }
                    
                    modify_result = mt5.order_send(modify_request)
                    if modify_result.retcode == mt5.TRADE_RETCODE_DONE:
                        self.log_message("SL/TP added successfully")
                        break
        
        # Save trade record
        trade_record = {
            'trade_id': f'{symbol}_AUTO_{int(time.time())}',
            'timestamp': datetime.now().isoformat(),
            'signal_data': signal_data,
            'execution_price': result.price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'order_id': result.order,
            'deal_id': result.deal,
            'mikrobot_compliance': True
        }
        
        with open(f'{symbol}_AUTO_{int(time.time())}.json', 'w') as f:
            json.dump(trade_record, f, indent=2)
        
        self.last_signal_timestamp = signal_data['timestamp']
        self.log_message(f"Trade record saved: {trade_record['trade_id']}.json")
        
        return True
    
    def monitor_positions(self):
        """Monitor and log position status"""
        positions = mt5.positions_get()
        if not positions:
            return
        
        total_pnl = sum(pos.profit for pos in positions)
        self.log_message(f"Active positions: {len(positions)}, Total P&L: ${total_pnl:.2f}")
        
        for pos in positions:
            pnl_status = "+" if pos.profit >= 0 else ""
            self.log_message(f"  {pos.symbol}: {pnl_status}${pos.profit:.2f}")
    
    def run_service(self):
        """Main service loop"""
        if not self.initialize_service():
            return
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                
                # Check for new signals
                signal_data = self.read_ea_signal()
                if signal_data:
                    self.execute_signal_trade(signal_data)
                
                # Monitor positions every 10 cycles (50 seconds)
                if cycle_count % 10 == 0:
                    self.monitor_positions()
                
                # Status update every 60 cycles (5 minutes)
                if cycle_count % 60 == 0:
                    runtime = datetime.now() - self.service_start_time
                    self.log_message(f"Service running for {runtime}")
                    cycle_count = 0  # Reset counter
                
                time.sleep(5)  # 5-second monitoring cycle
                
        except KeyboardInterrupt:
            self.log_message("Service stopped by user")
        except Exception as e:
            self.log_message(f"Service error: {e}")
        finally:
            mt5.shutdown()
            self.log_message("MT5 connection closed")
            
            # Save final log
            with open('mikrobot_service_log.txt', 'w', encoding='ascii', errors='ignore') as f:
                f.write('\n'.join(self.trade_log))

def main():
    service = MikrobotBackgroundService()
    service.run_service()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()