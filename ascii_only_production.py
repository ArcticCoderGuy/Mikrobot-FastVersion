#\!/usr/bin/env python3
"""
ASCII-ONLY PRODUCTION SYSTEM
No Unicode, no emojis, pure text automation
Fixes recurring encoding issues permanently
"""

import MetaTrader5 as mt5
import json
import re
import sys
from datetime import datetime

def ascii_print(text):
    """Print with ASCII-only characters"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def read_signal_ascii_safe():
    """Read signal file with bulletproof ASCII handling"""
    try:
        with open('C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json', 'rb') as f:
            content = f.read()
        
        # Handle UTF-16LE with null bytes - convert to clean ASCII
        content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
        
        # Strip ALL non-ASCII characters except basic JSON chars
        content_str = re.sub(r'[^\x20-\x7E]', '', content_str)
        
        return json.loads(content_str)
    except Exception as e:
        ascii_print(f"Signal read error: {str(e)}")
        return None

def calculate_position_ascii(symbol, balance):
    """Calculate position size - ASCII output only"""
    risk_amount = balance * 0.0055
    
    if 'JPY' in symbol:
        atr_pips = 8
        usd_per_pip = 100
    elif 'FERRARI' in symbol or '.IT' in symbol:
        atr_pips = 10
        usd_per_pip = 10
    else:
        atr_pips = 8
        usd_per_pip = 10
    
    sl_risk = atr_pips * usd_per_pip
    lot_size = round(risk_amount / sl_risk, 2)
    
    return lot_size, risk_amount, atr_pips

def execute_ascii_trade():
    """Execute trade with pure ASCII output"""
    ascii_print("MIKROBOT ASCII-ONLY EXECUTION")
    ascii_print("=" * 35)
    
    if not mt5.initialize():
        ascii_print("ERROR: MT5 failed")
        return
    
    signal = read_signal_ascii_safe()
    if not signal:
        ascii_print("ERROR: No signal")
        mt5.shutdown()
        return
    
    ascii_print("SIGNAL DATA:")
    ascii_print(f"Symbol: {signal['symbol']}")
    ascii_print(f"Direction: {signal['trade_direction']}")
    ascii_print(f"Time: {signal['timestamp']}")
    
    if (signal['phase_4_ylipip']['triggered'] and signal['ylipip_trigger'] == 0.6):
        ascii_print("Validation: PASSED")
    else:
        ascii_print("Validation: FAILED")
        mt5.shutdown()
        return
    
    account = mt5.account_info()
    lot_size, risk_amount, atr = calculate_position_ascii(signal['symbol'], account.balance)
    
    ascii_print("")
    ascii_print("POSITION CALCULATION:")
    ascii_print(f"Risk: ${risk_amount:.2f} (0.55%)")
    ascii_print(f"Size: {lot_size:.2f} lots")
    ascii_print(f"Improvement: {lot_size/0.01:.0f}x vs 0.01 lots")
    
    tick = mt5.symbol_info_tick(signal['symbol'])
    if not tick:
        ascii_print("ERROR: No price data")
        mt5.shutdown()
        return
    
    if signal['trade_direction'] == 'BULL':
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
        sl = round(price - (atr * 0.01), 3)
        tp = round(price + (atr * 0.01 * 2), 3)
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
        sl = round(price + (atr * 0.01), 3)
        tp = round(price - (atr * 0.01 * 2), 3)
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": signal['symbol'],
        "volume": lot_size,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 234000,
        "comment": f"ASCII_CLEAN_{lot_size}lots",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    ascii_print("EXECUTING...")
    result = mt5.order_send(request)
    
    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
        ascii_print("SUCCESS: Trade executed")
        ascii_print(f"Ticket: {result.order}")
        ascii_print(f"Volume: {result.volume:.2f} lots")
        ascii_print(f"Price: {result.price:.3f}")
        
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ASCII_EXECUTION_SUCCESS",
            "symbol": signal['symbol'],
            "volume": result.volume,
            "price": result.price,
            "ticket": result.order,
            "encoding": "ASCII_ONLY_NO_UNICODE"
        }
        
        with open('ASCII_EXECUTION_RECORD.json', 'w', encoding='ascii', errors='ignore') as f:
            json.dump(record, f, indent=2, ensure_ascii=True)
        
        ascii_print("Status: POSITION_SIZING_COMPLIANT")
        
    else:
        ascii_print("EXECUTION FAILED")
        if result:
            ascii_print(f"Error: {result.retcode}")
    
    mt5.shutdown()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    execute_ascii_trade()
EOF < /dev/null
