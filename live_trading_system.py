#!/usr/bin/env python3
"""
LIVE TRADING SYSTEM - REAL DEPLOYMENT
=====================================
Real money, real trades, real results for BlackRock validation
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
import MetaTrader5 as mt5

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('live_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveTradingSystem:
    def __init__(self):
        self.signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
        self.response_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_live_response.json")
        self.trades_log = Path("live_trades.json")
        self.last_signal_time = None
        self.active_positions = {}
        
        # Load existing trades
        if self.trades_log.exists():
            with open(self.trades_log, 'r') as f:
                self.trade_history = json.load(f)
        else:
            self.trade_history = []
    
    def connect_mt5(self):
        """Connect to MetaTrader 5"""
        if not mt5.initialize():
            logger.error("MT5 initialization failed")
            return False
        
        account_info = mt5.account_info()
        if account_info is None:
            logger.error("Failed to get account info")
            return False
            
        logger.info(f"Connected to MT5 - Account: {account_info.login}, Balance: ${account_info.balance:.2f}")
        return True
    
    def parse_signal(self, signal_text):
        """Parse the EA signal with encoding fix"""
        try:
            # Fix Unicode spacing issues
            import re
            clean_text = re.sub(r' +', ' ', signal_text)
            clean_text = clean_text.replace(' : ', ':').replace(' , ', ',').replace(' } ', '}').replace(' { ', '{')
            
            # Parse JSON
            signal_data = json.loads(clean_text)
            return signal_data
        except Exception as e:
            logger.error(f"Signal parsing error: {e}")
            return None
    
    def calculate_trade_params(self, signal):
        """Calculate precise trade parameters"""
        symbol = signal['symbol']
        direction = signal['trade_direction']
        current_price = float(signal['current_price'])
        
        # Asset class detection
        if symbol.startswith('_') and '.IT' in symbol:
            # Italian stock CFD
            asset_class = 'CFD_STOCK'
            pip_value = 0.01  # €0.01 per point
            min_sl_points = 50  # 50 points minimum
        elif symbol in ['USDCAD', 'EURUSD', 'GBPUSD']:
            # Forex
            asset_class = 'FOREX'
            pip_value = 0.0001
            min_sl_points = 8
        else:
            # Default
            asset_class = 'UNKNOWN'
            pip_value = 0.01
            min_sl_points = 20
        
        # Calculate stops based on retest distance
        if 'phase_3_m1_retest' in signal:
            retest_price = float(signal['phase_3_m1_retest']['price'])
            price_distance = abs(current_price - retest_price)
            sl_distance = max(price_distance, min_sl_points * pip_value)
        else:
            sl_distance = min_sl_points * pip_value
        
        # Trade parameters
        if direction == 'BEAR':
            action = 'SELL'
            sl_price = current_price + sl_distance
            tp_price = current_price - (sl_distance * 2)  # 1:2 RR
        else:  # BULL
            action = 'BUY'
            sl_price = current_price - sl_distance
            tp_price = current_price + (sl_distance * 2)  # 1:2 RR
        
        # Conservative position sizing
        lot_size = 0.01  # Very small for validation
        
        return {
            'symbol': symbol,
            'action': action,
            'lot_size': lot_size,
            'entry_price': current_price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'asset_class': asset_class,
            'sl_distance': sl_distance,
            'pip_value': pip_value
        }
    
    def execute_trade(self, trade_params):
        """Execute real trade via MT5"""
        try:
            symbol = trade_params['symbol']
            action = trade_params['action']
            lot_size = trade_params['lot_size']
            sl_price = trade_params['sl_price']
            tp_price = trade_params['tp_price']
            
            # Get symbol info
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found")
                return None
            
            # Prepare request
            if action == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask
            else:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 999888,
                "comment": "LIVE_TRADING_SYSTEM",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Trade failed: {result.retcode} - {result.comment}")
                return None
            
            logger.info(f"TRADE EXECUTED: {action} {symbol} {lot_size} lots @ {result.price}")
            logger.info(f"Order ID: {result.order}, Deal ID: {result.deal}")
            
            return {
                'success': True,
                'order_id': result.order,
                'deal_id': result.deal,
                'price': result.price,
                'volume': result.volume,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return None
    
    def monitor_positions(self):
        """Monitor and log active positions"""
        positions = mt5.positions_get()
        if positions is None:
            return
        
        for pos in positions:
            if pos.magic == 999888:  # Our trades
                position_id = f"{pos.symbol}_{pos.ticket}"
                
                profit = pos.profit
                pips = (pos.price_current - pos.price_open) / (0.0001 if 'USD' in pos.symbol else 0.01)
                if pos.type == 1:  # SELL
                    pips = -pips
                
                position_info = {
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'open_price': pos.price_open,
                    'current_price': pos.price_current,
                    'profit_usd': profit,
                    'profit_pips': pips,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'open_time': datetime.fromtimestamp(pos.time).isoformat()
                }
                
                self.active_positions[position_id] = position_info
                
                logger.info(f"Position {pos.symbol}: {profit:.2f} USD ({pips:.1f} pips)")
    
    def save_trade_record(self, signal, trade_params, execution_result):
        """Save complete trade record for audit"""
        trade_record = {
            'trade_id': len(self.trade_history) + 1,
            'timestamp': datetime.now().isoformat(),
            'signal_source': signal,
            'trade_parameters': trade_params,
            'execution_result': execution_result,
            'status': 'EXECUTED' if execution_result and execution_result.get('success') else 'FAILED'
        }
        
        self.trade_history.append(trade_record)
        
        # Save to file
        with open(self.trades_log, 'w') as f:
            json.dump(self.trade_history, f, indent=2)
        
        logger.info(f"Trade record saved: TRADE_{trade_record['trade_id']:03d}")
    
    def process_new_signal(self):
        """Process fresh EA signals"""
        if not self.signal_file.exists():
            return False
        
        try:
            with open(self.signal_file, 'r', encoding='utf-8', errors='ignore') as f:
                signal_text = f.read().strip()
            
            if not signal_text:
                return False
            
            signal = self.parse_signal(signal_text)
            if not signal:
                return False
            
            signal_time = signal.get('timestamp')
            if signal_time == self.last_signal_time:
                return False  # Already processed
            
            self.last_signal_time = signal_time
            
            # Check if all 4 phases complete
            if not signal.get('phase_4_ylipip', {}).get('triggered'):
                logger.info("Signal incomplete - waiting for Phase 4")
                return False
            
            logger.info(f"NEW SIGNAL: {signal['symbol']} {signal['trade_direction']} @ {signal['current_price']}")
            
            # Calculate trade parameters
            trade_params = self.calculate_trade_params(signal)
            logger.info(f"Trade params: {trade_params['action']} {trade_params['symbol']} {trade_params['lot_size']} lots")
            
            # Execute trade
            execution_result = self.execute_trade(trade_params)
            
            # Save record
            self.save_trade_record(signal, trade_params, execution_result)
            
            return True
            
        except Exception as e:
            logger.error(f"Signal processing error: {e}")
            return False
    
    def run(self):
        """Main trading loop"""
        logger.info("LIVE TRADING SYSTEM STARTING")
        logger.info("=" * 40)
        
        if not self.connect_mt5():
            logger.error("Failed to connect to MT5")
            return
        
        logger.info("SYSTEM OPERATIONAL - Monitoring for signals...")
        
        try:
            while True:
                # Process new signals
                if self.process_new_signal():
                    logger.info("Signal processed - monitoring positions...")
                
                # Monitor positions
                self.monitor_positions()
                
                # Wait before next check
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            logger.info("System stopped by user")
        except Exception as e:
            logger.error(f"System error: {e}")
        finally:
            mt5.shutdown()
            logger.info("MT5 connection closed")

if __name__ == "__main__":
    system = LiveTradingSystem()
    system.run()