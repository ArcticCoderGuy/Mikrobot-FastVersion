#!/usr/bin/env python3
"""
Execute EURJPY signal from 08:30 - Third position
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

def execute_eurjpy_08_30():
    print("EXECUTING EURJPY SIGNAL - 08:30 (THIRD POSITION)")
    print("=" * 48)
    
    # Latest signal at 08:30
    signal_data = {
        'timestamp': '2025.08.04 08:30',
        'symbol': 'EURJPY',
        'phase_4_ylipip': {'triggered': True},
        'ylipip_trigger': 0.60,
        'trade_direction': 'BULL'
    }
    
    if not mt5.initialize():
        print("ERROR: MT5 initialization failed")
        return False
    
    account_info = mt5.account_info()
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    
    # Check existing positions
    positions = mt5.positions_get(symbol="EURJPY")
    print(f"Existing EURJPY positions: {len(positions) if positions else 0}")
    
    if positions:
        total_pnl = sum(pos.profit for pos in positions)
        print(f"Combined P&L: ${total_pnl:.2f}")
        print("Adding third position to portfolio...")
    
    # Execute third EURJPY position
    tick = mt5.symbol_info_tick("EURJPY")
    entry_price = tick.ask
    
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": "EURJPY",
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "deviation": 20,
        "magic": 999888,
        "comment": "EURJPY_08_30_THIRD",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    result = mt5.order_send(order_request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"SUCCESS: Third EURJPY position opened!")
        print(f"Order ID: {result.order}")
        print(f"Execution: {result.price:.3f}")
        
        # Add SL/TP
        sl_price = result.price - 0.08
        tp_price = result.price + 0.16
        
        positions = mt5.positions_get(symbol="EURJPY")
        for pos in positions:
            if abs(pos.price_open - result.price) < 0.001:
                modify_request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": "EURJPY",
                    "position": pos.ticket,
                    "sl": sl_price,
                    "tp": tp_price,
                }
                mt5.order_send(modify_request)
                break
        
        trade_record = {
            'trade_id': 'EURJPY_THIRD_08_30',
            'timestamp': datetime.now().isoformat(),
            'order_id': result.order,
            'execution_price': result.price,
            'position_number': 3
        }
        
        with open('EURJPY_THIRD_08_30.json', 'w') as f:
            json.dump(trade_record, f, indent=2)
        
        print("Third EURJPY position successfully added!")
    else:
        print(f"Failed: {result.comment}")
    
    mt5.shutdown()
    return result.retcode == mt5.TRADE_RETCODE_DONE

if __name__ == "__main__":
    execute_eurjpy_08_30()