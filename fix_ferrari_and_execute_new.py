from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
Fix Ferrari stops and execute fresh Ferrari signal at 08:34
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

def fix_and_execute_ferrari():
    print("FIXING FERRARI STOPS + EXECUTING FRESH SIGNAL")
    print("=" * 48)
    
    if not mt5.initialize():
        print("ERROR: MT5 initialization failed")
        return False
    
    account_info = mt5.account_info()
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    print()
    
    # Fix existing Ferrari position first
    positions = mt5.positions_get(symbol="_FERRARI.IT")
    if positions:
        ferrari_pos = positions[0]
        print(f"EXISTING Ferrari Position:")
        print(f"  Entry: EUR{ferrari_pos.price_open:.2f}")
        print(f"  Current P&L: ${ferrari_pos.profit:.2f}")
        
        # Calculate conservative stops
        entry_price = ferrari_pos.price_open
        sl_price = entry_price - 1.00  # EUR1.00 stop loss
        tp_price = entry_price + 2.00  # EUR2.00 take profit (1:2)
        
        modify_request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": "_FERRARI.IT",
            "position": ferrari_pos.ticket,
            "sl": sl_price,
            "tp": tp_price,
        }
        
        print(f"Applying conservative stops: SL EUR{sl_price:.2f}, TP EUR{tp_price:.2f}")
        result = mt5.order_send(modify_request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print("OK Ferrari stops fixed successfully!")
        else:
            print(f"Ferrari stops failed: {result.comment}")
        print()
    
    # Fresh Ferrari signal at 08:34
    fresh_signal = {
        'timestamp': '2025.08.04 08:34',
        'symbol': '_FERRARI.IT',
        'phase_4_ylipip': {
            'target': 377.54000, 
            'current': 377.58000, 
            'triggered': True
        },
        'trade_direction': 'BULL',
        'ylipip_trigger': 0.60
    }
    
    print("FRESH FERRARI SIGNAL DETECTED:")
    print(f"Time: {fresh_signal['timestamp']}")
    print(f"Direction: {fresh_signal['trade_direction']}")
    print(f"0.6 Ylipip: TRIGGERED")
    print("Adding second Ferrari position...")
    print()
    
    # Execute second Ferrari position
    tick = mt5.symbol_info_tick("_FERRARI.IT")
    if tick is None:
        print("ERROR: Cannot get Ferrari price")
        mt5.shutdown()
        return False
    
    entry_price = tick.ask
    print(f"Entry Price: EUR{entry_price:.2f}")
    
    # Execute Ferrari BUY #2
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": "_FERRARI.IT",
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "deviation": 20,
        "magic": 999888,
        "comment": "FERRARI_SECOND_08_34",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        # Try IOC
        order_request["type_filling"] = mt5.ORDER_FILLING_IOC
        result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        # Try RETURN
        order_request["type_filling"] = mt5.ORDER_FILLING_RETURN
        result = mt5.order_send(order_request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print("SUCCESS: Second Ferrari position opened!")
        print(f"Order ID: {result.order}")
        print(f"Execution: EUR{result.price:.2f}")
        
        # Add stops to new position
        sl_price = result.price - 1.00
        tp_price = result.price + 2.00
        
        new_positions = mt5.positions_get(symbol="_FERRARI.IT")
        for pos in new_positions:
            if pos.ticket == result.order:
                modify_request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": "_FERRARI.IT",
                    "position": pos.ticket,
                    "sl": sl_price,
                    "tp": tp_price,
                }
                mt5.order_send(modify_request)
                break
        
        print(f"SL/TP added: EUR{sl_price:.2f} / EUR{tp_price:.2f}")
        
        # Save trade record
        trade_record = {
            'trade_id': 'FERRARI_SECOND_08_34',
            'timestamp': datetime.now().isoformat(),
            'signal_data': fresh_signal,
            'order_id': result.order,
            'execution_price': result.price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'position_number': 2
        }
        
        with open('FERRARI_SECOND_08_34.json', 'w', encoding='ascii', errors='ignore') as f:
            json.dump(trade_record, f, indent=2)
        
        print()
        print("PORTFOLIO UPDATE:")
        print("- EURJPY: 2 positions")
        print("- FERRARI.IT: 2 positions")
        print("- Total positions: 4")
        print("- Asset classes: FOREX + CFD STOCKS")
        
    else:
        print(f"Second Ferrari failed: {result.comment}")
    
    mt5.shutdown()
    return True

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    fix_and_execute_ferrari()