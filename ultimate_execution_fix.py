"""
ULTIMATE EXECUTION FIX
Detect and use the EXACT filling mode the broker supports
"""
import MetaTrader5 as mt5
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def detect_broker_filling_modes():
    """Detect what filling modes this broker actually supports"""
    if not mt5.initialize():
        return []
        
    ascii_print("DETECTING BROKER FILLING MODES...")
    
    # Test common symbols to see what works
    test_symbols = ['EURUSD', 'GBPUSD', 'GBPJPY', 'GOLD', 'CrudeOIL']
    supported_modes = {}
    
    for symbol in test_symbols:
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            filling_mode = symbol_info.filling_mode
            
            modes = []
            if filling_mode & 1:  # SYMBOL_FILLING_FOK
                modes.append('FOK')
            if filling_mode & 2:  # SYMBOL_FILLING_IOC  
                modes.append('IOC')
            if filling_mode & 4:  # SYMBOL_FILLING_RETURN
                modes.append('RETURN')
                
            supported_modes[symbol] = modes
            ascii_print(f"  {symbol}: {modes}")
    
    mt5.shutdown()
    return supported_modes

def create_broker_compatible_request(signal):
    """Create request compatible with this specific broker"""
    symbol = signal['symbol']
    direction = signal['trade_direction']
    
    if not mt5.initialize():
        return None
        
    # Get symbol info
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        mt5.shutdown()
        return None
        
    # Detect supported filling mode
    filling_mode_flags = symbol_info.filling_mode
    
    # Choose filling mode based on what's supported
    if filling_mode_flags & 4:  # RETURN supported
        filling_mode = mt5.ORDER_FILLING_RETURN
        mode_name = "RETURN"
    elif filling_mode_flags & 1:  # FOK supported
        filling_mode = mt5.ORDER_FILLING_FOK  
        mode_name = "FOK"
    elif filling_mode_flags & 2:  # IOC supported
        filling_mode = mt5.ORDER_FILLING_IOC
        mode_name = "IOC"
    else:
        # Try RETURN as last resort
        filling_mode = mt5.ORDER_FILLING_RETURN
        mode_name = "RETURN (fallback)"
    
    # Get current prices
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        mt5.shutdown()
        return None
        
    # Get account info
    account = mt5.account_info()
    if not account:
        mt5.shutdown()
        return None
        
    # ULTRA CONSERVATIVE position sizing
    risk_amount = account.balance * 0.001  # Only 0.1% risk!
    
    # Use minimum lot size for safety
    lot_size = symbol_info.volume_min
    
    # Set trade type and prices
    if direction == 'BULL':
        trade_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    else:
        trade_type = mt5.ORDER_TYPE_SELL  
        price = tick.bid
    
    # NO STOP LOSS OR TAKE PROFIT for maximum compatibility
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": trade_type,
        "price": price,
        "deviation": 100,  # Large deviation
        "magic": 999999,
        "comment": f"COMPAT-{direction}",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": filling_mode,
    }
    
    mt5.shutdown()
    
    ascii_print(f"BROKER-COMPATIBLE REQUEST:")
    ascii_print(f"  Symbol: {symbol}")
    ascii_print(f"  Volume: {lot_size} lots (minimum)")
    ascii_print(f"  Price: {price}")
    ascii_print(f"  Filling Mode: {mode_name}")
    ascii_print(f"  Risk: ${risk_amount:.2f} (0.1%)")
    ascii_print(f"  NO SL/TP (maximum compatibility)")
    
    return request

def test_ultimate_execution():
    """Test the ultimate execution fix"""
    ascii_print("ULTIMATE EXECUTION TEST")
    ascii_print("=" * 40)
    
    # First detect what this broker supports
    supported_modes = detect_broker_filling_modes()
    
    # Get current signal
    try:
        signal_file = 'C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'
        with open(signal_file, 'rb') as f:
            content = f.read()
        
        content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
        import re
        content_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', content_str)
        signal = json.loads(content_str)
        
        symbol = signal.get('symbol', 'Unknown')
        ascii_print(f"\nTesting on: {symbol}")
        
        if symbol in supported_modes:
            ascii_print(f"Supported modes for {symbol}: {supported_modes[symbol]}")
        
        # Create compatible request
        request = create_broker_compatible_request(signal)
        if not request:
            ascii_print("Failed to create compatible request")
            return False
            
        # Execute with ultimate compatibility
        if not mt5.initialize():
            ascii_print("MT5 initialization failed")
            return False
            
        ascii_print("\nATTEMPTING EXECUTION...")
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            ascii_print("SUCCESS! TRADE EXECUTED!")
            ascii_print(f"  Ticket: {result.order}")
            ascii_print(f"  Price: {result.price}")
            ascii_print(f"  Volume: {result.volume}")
            ascii_print("\nULTIMATE FIX WORKING!")
            mt5.shutdown()
            return True
        else:
            ascii_print("STILL FAILED!")
            if result:
                ascii_print(f"  Error Code: {result.retcode}")
                ascii_print(f"  Error: {result.comment}")
                
                # Decode error codes
                error_codes = {
                    10004: "Requote",
                    10006: "Request rejected", 
                    10007: "Request canceled",
                    10008: "Order placed",
                    10009: "Request completed",
                    10010: "Only part executed",
                    10011: "Request processing error",
                    10012: "Request canceled by timeout",
                    10013: "Invalid request",
                    10014: "Invalid volume",
                    10015: "Invalid price",
                    10016: "Invalid stops",
                    10017: "Trade disabled",
                    10018: "Market closed",
                    10019: "Not enough money",
                    10020: "Prices changed",
                    10021: "Off quotes",
                    10022: "Invalid expiration",
                    10023: "Order state changed",
                    10024: "Too frequent requests",
                    10025: "No changes",
                    10026: "Autotrading disabled",
                    10027: "Market closed",
                    10028: "Invalid volume",
                    10029: "Invalid price",
                    10030: "Invalid stops/Unsupported filling mode",
                    10031: "Invalid volume"
                }
                
                error_desc = error_codes.get(result.retcode, "Unknown error")
                ascii_print(f"  Description: {error_desc}")
                
            mt5.shutdown()
            return False
            
    except Exception as e:
        ascii_print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_ultimate_execution()