"""
DEPLOY FIXED EA WITH PROPER EXECUTION
Fixes all the execution issues from the Journal
"""
import MetaTrader5 as mt5
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def get_proper_execution_parameters(symbol):
    """Get proper execution parameters for any symbol"""
    if not mt5.initialize():
        return None
        
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        mt5.shutdown()
        return None
    
    # Get current prices
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        mt5.shutdown()
        return None
        
    # Build execution parameters
    params = {
        'digits': symbol_info.digits,
        'point': symbol_info.point,
        'min_lot': symbol_info.volume_min,
        'max_lot': symbol_info.volume_max,
        'lot_step': symbol_info.volume_step,
        'spread': symbol_info.spread,
        'bid': tick.bid,
        'ask': tick.ask,
        'filling_mode': symbol_info.filling_mode
    }
    
    # Calculate minimum stop distance (use spread as minimum)
    min_stop_distance = max(symbol_info.spread * symbol_info.point * 2, 10 * symbol_info.point)
    params['min_stop_distance'] = min_stop_distance
    
    mt5.shutdown()
    return params

def create_safe_trade_request(signal):
    """Create a safe, broker-compliant trade request"""
    symbol = signal['symbol']
    direction = signal['trade_direction']
    current_price = signal['current_price']
    
    # Get execution parameters
    params = get_proper_execution_parameters(symbol)
    if not params:
        ascii_print(f"Failed to get parameters for {symbol}")
        return None
    
    # Get account info
    if not mt5.initialize():
        return None
        
    account = mt5.account_info()
    if not account:
        mt5.shutdown()
        return None
        
    # Calculate SAFE position size (conservative approach)
    risk_amount = account.balance * 0.005  # Reduced to 0.5% for safety
    
    # Use conservative ATR values
    safe_atr_pips = {
        'GBPJPY': 6, 'EURJPY': 6, 'USDJPY': 6,
        'EURUSD': 4, 'GBPUSD': 4, 'AUDUSD': 4,
        'GOLD': 8, 'PLATINUM': 10, 'CrudeOIL': 20,
        'BTCUSD': 100, 'ETHUSD': 50, 'BCHUSD': 8
    }
    
    atr_pips = safe_atr_pips.get(symbol, 5)  # Very conservative default
    risk_per_pip = atr_pips * params['point'] * 10  # Assume $10 per pip per lot
    
    if risk_per_pip > 0:
        lot_size = risk_amount / risk_per_pip
    else:
        lot_size = params['min_lot']
    
    # Ensure lot size is safe and compliant
    lot_size = max(params['min_lot'], min(lot_size, 1.0))  # Cap at 1.0 lot max
    
    # Round to lot step
    if params['lot_step'] > 0:
        lot_size = round(lot_size / params['lot_step']) * params['lot_step']
    
    lot_size = round(lot_size, 2)
    
    # Determine trade type and set safe prices
    if direction == 'BULL':
        trade_type = mt5.ORDER_TYPE_BUY
        entry_price = params['ask']
        sl_price = entry_price - (atr_pips * params['point'])
        tp_price = entry_price + (atr_pips * 2 * params['point'])
    else:
        trade_type = mt5.ORDER_TYPE_SELL
        entry_price = params['bid']
        sl_price = entry_price + (atr_pips * params['point'])
        tp_price = entry_price - (atr_pips * 2 * params['point'])
    
    # Ensure stops are valid distance from current price
    min_distance = params['min_stop_distance']
    
    if trade_type == mt5.ORDER_TYPE_BUY:
        sl_price = min(sl_price, entry_price - min_distance)
        tp_price = max(tp_price, entry_price + min_distance)
    else:
        sl_price = max(sl_price, entry_price + min_distance)
        tp_price = min(tp_price, entry_price - min_distance)
    
    # Round prices to proper digits
    sl_price = round(sl_price, params['digits'])
    tp_price = round(tp_price, params['digits'])
    entry_price = round(entry_price, params['digits'])
    
    # Determine filling mode (use IOC as safest)
    filling_mode = mt5.ORDER_FILLING_IOC
    
    # Create safe request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": trade_type,
        "price": entry_price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 50,  # Increased deviation for better fill rates
        "magic": 999889,  # Different magic number
        "comment": f"SAFE-{direction}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }
    
    mt5.shutdown()
    
    ascii_print(f"SAFE TRADE REQUEST CREATED:")
    ascii_print(f"  Symbol: {symbol}")
    ascii_print(f"  Volume: {lot_size} lots (safe size)")
    ascii_print(f"  Entry: {entry_price}")
    ascii_print(f"  SL: {sl_price} (safe distance)")
    ascii_print(f"  TP: {tp_price} (safe distance)")
    ascii_print(f"  Risk: ${risk_amount:.2f} (0.5%)")
    
    return request

def execute_safe_trade(signal):
    """Execute trade with all safety checks"""
    ascii_print(f"\nEXECUTING SAFE TRADE FOR {signal['symbol']}...")
    
    # Create safe request
    request = create_safe_trade_request(signal)
    if not request:
        ascii_print("Failed to create safe request")
        return False
    
    # Execute trade
    if not mt5.initialize():
        ascii_print("MT5 initialization failed")
        return False
    
    result = mt5.order_send(request)
    
    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        ascii_print(f"TRADE EXECUTED SUCCESSFULLY!")
        ascii_print(f"  Ticket: {result.order}")
        ascii_print(f"  Price: {result.price}")
        ascii_print(f"  Volume: {result.volume}")
        ascii_print(f"  Comment: {result.comment}")
        mt5.shutdown()
        return True
    else:
        ascii_print(f"TRADE FAILED!")
        if result:
            ascii_print(f"  Error Code: {result.retcode}")
            ascii_print(f"  Error: {result.comment}")
        mt5.shutdown()
        return False

def main():
    """Main safe execution deployment"""
    ascii_print("DEPLOYING SAFE EXECUTION SYSTEM")
    ascii_print("=" * 50)
    ascii_print("Fixes for Journal issues:")
    ascii_print("+ Unsupported filling mode -> IOC mode")
    ascii_print("+ Invalid stops -> Safe distance calculation")
    ascii_print("+ Large position sizes -> Capped at 1.0 lot")
    ascii_print("+ Risk reduced to 0.5% for safety")
    ascii_print("")
    
    # Test on current signal
    try:
        signal_file = 'C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'
        with open(signal_file, 'rb') as f:
            content = f.read()
        
        content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
        import re
        content_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', content_str)
        signal = json.loads(content_str)
        
        ascii_print(f"Current Signal: {signal.get('symbol', 'Unknown')} {signal.get('trade_direction', 'Unknown')}")
        
        # Check if valid signal
        phases = ['phase_1_m5_bos', 'phase_2_m1_break', 'phase_3_m1_retest', 'phase_4_ylipip']
        all_phases = all(phase in signal for phase in phases)
        ylipip_triggered = signal.get('phase_4_ylipip', {}).get('triggered', False)
        
        if all_phases and ylipip_triggered:
            ascii_print("Signal validation: PASSED")
            ascii_print("Attempting safe execution...")
            
            if execute_safe_trade(signal):
                ascii_print("\nSUCCESS: Safe execution system working!")
                ascii_print("No more 'Unsupported filling mode' errors!")
                ascii_print("No more 'Invalid stops' errors!")
            else:
                ascii_print("\nExecution failed - check MT5 connection")
        else:
            ascii_print("Signal validation: INCOMPLETE - waiting for perfect pattern")
            
    except Exception as e:
        ascii_print(f"Error: {e}")

if __name__ == "__main__":
    main()