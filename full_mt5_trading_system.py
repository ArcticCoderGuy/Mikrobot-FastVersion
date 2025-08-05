#!/usr/bin/env python3
"""
FULL MT5 TRADING SYSTEM - CONTINUOUS OPERATIONS
==============================================
Monitor all MT5 tradeable symbols for 4-phase signals
Execute trades with MIKROBOT_FASTVERSION.md compliance
"""

import MetaTrader5 as mt5
import json
import time
from datetime import datetime
from pathlib import Path

class FullMT5TradingSystem:
    def __init__(self):
        self.signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
        self.last_signal_timestamp = None
        self.active_positions = {}
        self.trade_count = 0
        
    def initialize_mt5(self):
        """Initialize MT5 connection"""
        if not mt5.initialize():
            print("ERROR: Could not initialize MT5")
            return False
        
        account_info = mt5.account_info()
        print(f"MT5 TRADING SYSTEM INITIALIZED")
        print(f"Account: {account_info.login}")
        print(f"Balance: ${account_info.balance:.2f}")
        print(f"Server: {account_info.server}")
        print()
        return True
    
    def get_all_tradeable_symbols(self):
        """Get all available symbols in MT5"""
        symbols = mt5.symbols_get()
        if symbols is None:
            return []
        
        tradeable_symbols = []
        for symbol in symbols:
            # Filter for liquid, tradeable symbols
            if (symbol.visible and 
                symbol.volume_min <= 0.01 and
                symbol.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL):
                tradeable_symbols.append({
                    'name': symbol.name,
                    'description': symbol.description,
                    'currency_base': symbol.currency_base,
                    'currency_profit': symbol.currency_profit,
                    'point': symbol.point,
                    'volume_min': symbol.volume_min
                })
        
        return tradeable_symbols
    
    def read_ea_signal(self):
        """Read and parse EA 4-phase signal"""
        try:
            if not self.signal_file.exists():
                return None
                
            with open(self.signal_file, 'r', encoding='utf-16-le') as f:
                content = f.read()
                
            # Clean up Unicode issues
            import re
            content = re.sub(r'\x00', '', content)  # Remove null bytes
            content = re.sub(r' +', ' ', content)   # Normalize spaces
            
            signal_data = json.loads(content)
            
            # Check if this is a new signal
            if signal_data.get('timestamp') == self.last_signal_timestamp:
                return None  # Already processed
                
            # Validate 4-phase completion
            if (signal_data.get('phase_4_ylipip', {}).get('triggered') == True and
                signal_data.get('ylipip_trigger') == 0.60):
                return signal_data
                
        except Exception as e:
            print(f"Signal read error: {e}")
            
        return None
    
    def calculate_position_size(self, symbol, risk_usd=8.0):
        """Calculate position size based on risk"""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return 0.01  # Default minimum
            
        # Use minimum volume for safety
        return max(symbol_info.volume_min, 0.01)
    
    def determine_filling_mode(self, symbol):
        """Determine compatible filling mode for symbol"""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return mt5.ORDER_FILLING_RETURN
            
        # Try FOK first (worked for EURJPY), then IOC, then RETURN
        filling_modes = [
            mt5.ORDER_FILLING_FOK,
            mt5.ORDER_FILLING_IOC,
            mt5.ORDER_FILLING_RETURN
        ]
        
        return filling_modes[0]  # Start with FOK
    
    def calculate_stops(self, symbol, entry_price, direction, atr_distance=0.08):
        """Calculate stop loss and take profit"""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return entry_price, entry_price
            
        # Adjust for different symbol types
        if 'JPY' in symbol:
            pip_value = 0.01
            sl_distance = atr_distance  # 8 pips for JPY
        elif symbol.startswith('_'):  # CFD stocks like Ferrari
            pip_value = 1.0
            sl_distance = atr_distance * 10  # 0.80 EUR for stocks
        elif 'USD' in symbol or 'EUR' in symbol:
            pip_value = 0.0001
            sl_distance = atr_distance  # 8 pips for major pairs
        else:
            pip_value = symbol_info.point * 10
            sl_distance = atr_distance
        
        if direction == 'BUY':
            sl_price = entry_price - sl_distance
            tp_price = entry_price + (sl_distance * 2)  # 1:2 RR
        else:  # SELL
            sl_price = entry_price + sl_distance
            tp_price = entry_price - (sl_distance * 2)
            
        return sl_price, tp_price
    
    def execute_trade(self, signal_data):
        """Execute trade based on EA signal"""
        symbol = signal_data['symbol']
        direction = signal_data['trade_direction']
        
        print(f"EXECUTING TRADE: {symbol} {direction}")
        print(f"Signal Time: {signal_data['timestamp']}")
        print(f"4-Phase Complete: YES")
        print(f"0.6 Ylipip Triggered: YES")
        
        # Get current price
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print(f"ERROR: Cannot get price for {symbol}")
            return False
        
        # Determine trade parameters
        if direction == 'BULL':
            order_type = mt5.ORDER_TYPE_BUY
            entry_price = tick.ask
        else:
            order_type = mt5.ORDER_TYPE_SELL
            entry_price = tick.bid
        
        # Calculate position size and stops
        lot_size = self.calculate_position_size(symbol)
        sl_price, tp_price = self.calculate_stops(symbol, entry_price, 'BUY' if direction == 'BULL' else 'SELL')
        filling_mode = self.determine_filling_mode(symbol)
        
        print(f"Entry Price: {entry_price}")
        print(f"Stop Loss: {sl_price}")
        print(f"Take Profit: {tp_price}")
        print(f"Position Size: {lot_size}")
        
        # Try multiple execution strategies
        execution_strategies = [
            # Strategy 1: Full order with SL/TP
            {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": entry_price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 999888,
                "comment": f"{symbol}_MIKROBOT_4PHASE",
                "type_filling": filling_mode,
            },
            # Strategy 2: Market order only
            {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "deviation": 20,
                "magic": 999888,
                "comment": f"{symbol}_MIKROBOT_SIMPLE",
                "type_filling": filling_mode,
            }
        ]
        
        result = None
        for i, order_request in enumerate(execution_strategies):
            print(f"Trying execution strategy {i+1}...")
            result = mt5.order_send(order_request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"SUCCESS with strategy {i+1}!")
                break
            else:
                print(f"Strategy {i+1} failed: {result.retcode} - {result.comment}")
        
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"ALL EXECUTION STRATEGIES FAILED for {symbol}")
            return False
        
        # Add SL/TP if market order was used
        if 'sl' not in order_request:
            print("Adding Stop Loss and Take Profit...")
            positions = mt5.positions_get(symbol=symbol)
            if positions and len(positions) > 0:
                position = positions[-1]
                
                modify_request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": symbol,
                    "position": position.ticket,
                    "sl": sl_price,
                    "tp": tp_price,
                }
                
                modify_result = mt5.order_send(modify_request)
                if modify_result.retcode == mt5.TRADE_RETCODE_DONE:
                    print("Stop Loss and Take Profit added successfully")
        
        # Record successful trade
        self.trade_count += 1
        trade_record = {
            'trade_id': f'{symbol}_TRADE_{self.trade_count:03d}',
            'timestamp': datetime.now().isoformat(),
            'signal_timestamp': signal_data['timestamp'],
            'symbol': symbol,
            'direction': direction,
            'volume': result.volume,
            'execution_price': result.price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'order_id': result.order,
            'deal_id': result.deal,
            'mikrobot_compliance': True,
            'four_phase_complete': True,
            'ylipip_0_6_triggered': True
        }
        
        # Save trade record
        with open(f'{symbol}_TRADE_{self.trade_count:03d}.json', 'w') as f:
            json.dump(trade_record, f, indent=2)
        
        self.active_positions[symbol] = trade_record
        self.last_signal_timestamp = signal_data['timestamp']
        
        print(f"TRADE EXECUTED SUCCESSFULLY!")
        print(f"Order ID: {result.order}")
        print(f"Deal ID: {result.deal}")
        print(f"Trade Record: {trade_record['trade_id']}.json")
        print()
        
        return True
    
    def monitor_positions(self):
        """Monitor active positions"""
        positions = mt5.positions_get()
        if not positions:
            return
        
        print(f"ACTIVE POSITIONS: {len(positions)}")
        for pos in positions:
            print(f"  {pos.symbol}: {pos.volume} lots, P&L: ${pos.profit:.2f}")
    
    def run_continuous_trading(self):
        """Main trading loop"""
        if not self.initialize_mt5():
            return
        
        print("FULL MT5 TRADING SYSTEM - CONTINUOUS OPERATIONS")
        print("=" * 50)
        print("Monitoring for EA 4-phase signals...")
        print("MIKROBOT_FASTVERSION.md compliance: ACTIVE")
        print()
        
        # Get all tradeable symbols
        symbols = self.get_all_tradeable_symbols()
        print(f"Monitoring {len(symbols)} tradeable symbols")
        print()
        
        try:
            while True:
                # Check for new EA signal
                signal_data = self.read_ea_signal()
                
                if signal_data:
                    print(f"NEW 4-PHASE SIGNAL DETECTED!")
                    print(f"Symbol: {signal_data['symbol']}")
                    print(f"Direction: {signal_data['trade_direction']}")
                    print(f"Timestamp: {signal_data['timestamp']}")
                    print()
                    
                    # Execute trade
                    self.execute_trade(signal_data)
                
                # Monitor existing positions
                self.monitor_positions()
                
                # Wait before next check
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\nTrading system stopped by user")
        except Exception as e:
            print(f"System error: {e}")
        finally:
            mt5.shutdown()
            print("MT5 connection closed")

def main():
    trading_system = FullMT5TradingSystem()
    trading_system.run_continuous_trading()

if __name__ == "__main__":
    main()