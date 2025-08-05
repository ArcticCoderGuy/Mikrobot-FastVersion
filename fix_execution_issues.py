"""
URGENT FIX FOR EXECUTION ISSUES
Fixes the "Unsupported filling mode" and "Invalid stops" errors
"""
import MetaTrader5 as mt5
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

class ExecutionFixer:
    """Fix MT5 execution issues"""
    
    def __init__(self):
        self.symbol_specs = {}
        
    def get_symbol_specifications(self, symbol):
        """Get proper symbol specifications for execution"""
        if not mt5.initialize():
            return None
            
        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            mt5.shutdown()
            return None
            
        specs = {
            'digits': symbol_info.digits,
            'point': symbol_info.point,
            'min_lot': symbol_info.volume_min,
            'max_lot': symbol_info.volume_max,
            'lot_step': symbol_info.volume_step,
            'stops_level': symbol_info.stops_level,
            'filling_mode': symbol_info.filling_mode,
            'spread': symbol_info.spread,
            'tick_size': symbol_info.trade_tick_size,
            'tick_value': symbol_info.trade_tick_value
        }
        
        mt5.shutdown()
        return specs
    
    def fix_position_size(self, symbol, requested_size):
        """Fix position size to be within broker limits"""
        specs = self.get_symbol_specifications(symbol)
        if not specs:
            return 0.01  # Fallback
            
        # Ensure size is within min/max limits
        size = max(specs['min_lot'], min(requested_size, specs['max_lot']))
        
        # Round to lot step
        if specs['lot_step'] > 0:
            size = round(size / specs['lot_step']) * specs['lot_step']
            
        # Final validation
        if size < specs['min_lot']:
            size = specs['min_lot']
        elif size > specs['max_lot']:
            size = specs['max_lot']
            
        return round(size, 2)
    
    def fix_stop_levels(self, symbol, entry_price, sl_price, tp_price, trade_type):
        """Fix stop loss and take profit levels"""
        specs = self.get_symbol_specifications(symbol)
        if not specs:
            return sl_price, tp_price
            
        # Get current market prices
        if not mt5.initialize():
            return sl_price, tp_price
            
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            mt5.shutdown()
            return sl_price, tp_price
            
        # Calculate minimum distance
        min_stop_distance = specs['stops_level'] * specs['point']
        if min_stop_distance == 0:
            min_stop_distance = 10 * specs['point']  # Default 10 points
            
        current_price = tick.bid if trade_type == mt5.ORDER_TYPE_SELL else tick.ask
        
        # Fix stop loss
        if sl_price > 0:
            if trade_type == mt5.ORDER_TYPE_BUY:
                # Buy trade: SL must be below current price
                max_sl = current_price - min_stop_distance
                sl_price = min(sl_price, max_sl)
            else:
                # Sell trade: SL must be above current price
                min_sl = current_price + min_stop_distance
                sl_price = max(sl_price, min_sl)
                
        # Fix take profit
        if tp_price > 0:
            if trade_type == mt5.ORDER_TYPE_BUY:
                # Buy trade: TP must be above current price
                min_tp = current_price + min_stop_distance
                tp_price = max(tp_price, min_tp)
            else:
                # Sell trade: TP must be below current price
                max_tp = current_price - min_stop_distance
                tp_price = min(tp_price, max_tp)
                
        # Round to proper digits
        sl_price = round(sl_price, specs['digits'])
        tp_price = round(tp_price, specs['digits'])
        
        mt5.shutdown()
        return sl_price, tp_price
    
    def get_proper_filling_mode(self, symbol):
        """Get proper filling mode for symbol"""
        specs = self.get_symbol_specifications(symbol)
        if not specs:
            return mt5.ORDER_FILLING_IOC  # Default
            
        # Check what filling modes are supported
        filling_mode = specs['filling_mode']
        
        # Priority order: FOK > IOC > Return
        if filling_mode & mt5.SYMBOL_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK
        elif filling_mode & mt5.SYMBOL_FILLING_IOC:
            return mt5.ORDER_FILLING_IOC
        else:
            return mt5.ORDER_FILLING_RETURN
    
    def create_fixed_trade_request(self, signal):
        """Create properly formatted trade request"""
        symbol = signal['symbol']
        direction = signal['trade_direction']
        current_price = signal['current_price']
        
        # Get account balance
        if not mt5.initialize():
            return None
            
        account = mt5.account_info()
        if not account:
            mt5.shutdown()
            return None
            
        # Calculate proper position size
        risk_amount = account.balance * 0.0055  # 0.55%
        
        # Symbol-specific ATR configs (fixed values)
        atr_configs = {
            'GBPJPY': 8, 'EURJPY': 8, 'USDJPY': 8,
            'EURUSD': 6, 'GBPUSD': 6, 'AUDUSD': 6,
            'GOLD': 12, 'PLATINUM': 15,
            'BTCUSD': 150, 'ETHUSD': 100, 'BCHUSD': 10
        }
        
        atr_pips = atr_configs.get(symbol, 10)
        
        # Get symbol specs for proper calculation
        specs = self.get_symbol_specifications(symbol)
        if not specs:
            mt5.shutdown()
            return None
            
        # Calculate lot size based on tick value
        risk_per_pip = atr_pips * specs['tick_value']
        if risk_per_pip > 0:
            lot_size = risk_amount / risk_per_pip
        else:
            lot_size = 0.1  # Fallback
            
        # Fix position size
        lot_size = self.fix_position_size(symbol, lot_size)
        
        # Determine trade type
        trade_type = mt5.ORDER_TYPE_BUY if direction == 'BULL' else mt5.ORDER_TYPE_SELL
        
        # Calculate SL and TP
        if direction == 'BULL':
            sl_price = current_price - (atr_pips * specs['point'])
            tp_price = current_price + (atr_pips * 2 * specs['point'])  # 2:1 RR
        else:
            sl_price = current_price + (atr_pips * specs['point'])
            tp_price = current_price - (atr_pips * 2 * specs['point'])
            
        # Fix stop levels
        sl_price, tp_price = self.fix_stop_levels(symbol, current_price, sl_price, tp_price, trade_type)
        
        # Get proper filling mode
        filling_mode = self.get_proper_filling_mode(symbol)
        
        # Create request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": trade_type,
            "price": current_price,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": 20,
            "magic": 999888,
            "comment": f"Fixed-{direction}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        mt5.shutdown()
        
        ascii_print(f"FIXED TRADE REQUEST FOR {symbol}:")
        ascii_print(f"  Volume: {lot_size} lots (fixed)")
        ascii_print(f"  SL: {sl_price} (fixed)")
        ascii_print(f"  TP: {tp_price} (fixed)")
        ascii_print(f"  Filling Mode: {filling_mode} (proper)")
        
        return request
    
    def test_current_signal(self):
        """Test fix on current signal"""
        try:
            signal_file = 'C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'
            with open(signal_file, 'rb') as f:
                content = f.read()
            
            content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
            import re
            content_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', content_str)
            signal = json.loads(content_str)
            
            ascii_print(f"Testing fix on: {signal.get('symbol', 'Unknown')}")
            
            # Create fixed request
            request = self.create_fixed_trade_request(signal)
            
            if request:
                ascii_print("FIXED REQUEST CREATED SUCCESSFULLY!")
                ascii_print("This should resolve:")
                ascii_print("+ Unsupported filling mode errors")
                ascii_print("+ Invalid stops errors") 
                ascii_print("+ Position sizing issues")
                return request
            else:
                ascii_print("Failed to create fixed request")
                return None
                
        except Exception as e:
            ascii_print(f"Error: {e}")
            return None

def main():
    """Main execution fixing routine"""
    ascii_print("URGENT EXECUTION ISSUE FIXER")
    ascii_print("=" * 50)
    
    fixer = ExecutionFixer()
    
    # Test the fix
    fixed_request = fixer.test_current_signal()
    
    if fixed_request:
        ascii_print("\nFIXES IMPLEMENTED:")
        ascii_print("+ Proper filling mode detection")
        ascii_print("+ Valid stop level calculations")
        ascii_print("+ Broker-compliant position sizing")
        ascii_print("+ Symbol specification validation")
        ascii_print("")
        ascii_print("NEXT STEP: Update your EA to use these fixes!")
    else:
        ascii_print("Fix implementation failed - check MT5 connection")

if __name__ == "__main__":
    main()