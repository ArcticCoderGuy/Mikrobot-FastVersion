#!/usr/bin/env python3
"""
Execute USDCAD BULL signal at 08:36 - Major pair expansion
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

def execute_usdcad_bull():
    print("EXECUTING USDCAD BULL SIGNAL - 08:36")
    print("=" * 38)
    print("MAJOR PAIR EXPANSION: USDCAD")
    
    if not mt5.initialize():
        return False
    
    account_info = mt5.account_info()
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    
    # USDCAD signal
    tick = mt5.symbol_info_tick("USDCAD")
    if tick is None:
        print("ERROR: Cannot get USDCAD price")
        mt5.shutdown()
        return False
    
    entry_price = tick.ask  # BUY
    sl_price = entry_price - 0.0008  # 8 pips SL
    tp_price = entry_price + 0.0016  # 16 pips TP
    
    print(f"USDCAD BUY: {entry_price:.5f}")
    print(f"SL: {sl_price:.5f}, TP: {tp_price:.5f}")
    
    # Execute USDCAD BUY
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": "USDCAD",
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "deviation": 20,
        "magic": 999888,
        "comment": "USDCAD_BULL_08_36",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        order_request["type_filling"] = mt5.ORDER_FILLING_IOC
        result = mt5.order_send(order_request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"SUCCESS: USDCAD executed at {result.price:.5f}")
        
        # Add SL/TP
        positions = mt5.positions_get(symbol="USDCAD")
        for pos in positions:
            if pos.ticket == result.order:
                modify_request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": "USDCAD",
                    "position": pos.ticket,
                    "sl": sl_price,
                    "tp": tp_price,
                }
                mt5.order_send(modify_request)
                break
        
        trade_record = {
            'trade_id': 'USDCAD_BULL_08_36',
            'timestamp': datetime.now().isoformat(),
            'symbol': 'USDCAD',
            'action': 'BUY',
            'execution_price': result.price,
            'order_id': result.order,
            'major_pair_expansion': True
        }
        
        with open('USDCAD_BULL_08_36.json', 'w') as f:
            json.dump(trade_record, f, indent=2)
        
        print("USDCAD trade record: USDCAD_BULL_08_36.json")
        print("MAJOR PAIR EXPANSION SUCCESSFUL!")
        
    else:
        print(f"USDCAD failed: {result.comment}")
    
    mt5.shutdown()
    return result.retcode == mt5.TRADE_RETCODE_DONE

if __name__ == "__main__":
    execute_usdcad_bull()