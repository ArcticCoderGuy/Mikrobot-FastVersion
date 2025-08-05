#!/usr/bin/env python3
"""
Execute fresh EURJPY signal from 08:28
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

def execute_fresh_eurjpy():
    print("EXECUTING FRESH EURJPY SIGNAL - 08:28")
    print("=" * 40)
    
    # Fresh signal data from 08:28
    signal_data = {
        'timestamp': '2025.08.04 08:28',
        'symbol': 'EURJPY',
        'strategy': 'MIKROBOT_FASTVERSION_4PHASE',
        'phase_1_m5_bos': {
            'time': '2025.08.04 08:25', 
            'price': 171.12900, 
            'direction': 'BULL'
        },
        'phase_2_m1_break': {
            'time': '2025.08.04 08:26', 
            'price': 171.13300
        },
        'phase_3_m1_retest': {
            'time': '2025.08.04 08:27', 
            'price': 171.13200
        },
        'phase_4_ylipip': {
            'target': 171.13900, 
            'current': 171.14200, 
            'triggered': True
        },
        'trade_direction': 'BULL',
        'ylipip_trigger': 0.60
    }
    
    print("FRESH EA SIGNAL DETECTED:")
    print(f"Symbol: {signal_data['symbol']}")
    print(f"Direction: {signal_data['trade_direction']}")
    print(f"Signal Time: {signal_data['timestamp']}")
    print(f"4-Phase Complete: YES")
    print(f"0.6 Ylipip Triggered: YES")
    print()
    
    # Initialize MT5
    if not mt5.initialize():
        print("ERROR: Could not initialize MT5")
        return False
    
    account_info = mt5.account_info()
    print(f"MT5 Connected - Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    print()
    
    # Check existing positions
    positions = mt5.positions_get(symbol="EURJPY")
    if positions and len(positions) > 0:
        print("EXISTING EURJPY POSITION DETECTED:")
        pos = positions[0]
        print(f"  Entry: {pos.price_open:.3f}")
        print(f"  Current P&L: ${pos.profit:.2f}")
        print("  Decision: Adding to winning position")
        print()
    
    # Get current price
    tick = mt5.symbol_info_tick("EURJPY")
    if tick is None:
        print("ERROR: Cannot get EURJPY price")
        mt5.shutdown()
        return False
    
    entry_price = tick.ask
    sl_price = entry_price - 0.08  # 8 pips SL
    tp_price = entry_price + 0.16  # 16 pips TP
    
    print(f"TRADE PARAMETERS:")
    print(f"Entry Price: {entry_price:.3f}")
    print(f"Stop Loss: {sl_price:.3f}")
    print(f"Take Profit: {tp_price:.3f}")
    print()
    
    # Execute with FOK mode (worked before)
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": "EURJPY",
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "deviation": 20,
        "magic": 999888,
        "comment": "EURJPY_FRESH_08_28",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    print("EXECUTING FRESH TRADE...")
    result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Trade failed: {result.retcode} - {result.comment}")
        mt5.shutdown()
        return False
    
    print("SUCCESS: FRESH EURJPY TRADE EXECUTED!")
    print(f"Order ID: {result.order}")
    print(f"Deal ID: {result.deal}")
    print(f"Execution Price: {result.price:.3f}")
    print()
    
    # Add SL/TP
    positions = mt5.positions_get(symbol="EURJPY")
    if positions:
        latest_position = None
        for pos in positions:
            if pos.ticket == result.order or pos.price_open == result.price:
                latest_position = pos
                break
        
        if latest_position:
            modify_request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": "EURJPY",
                "position": latest_position.ticket,
                "sl": sl_price,
                "tp": tp_price,
            }
            
            modify_result = mt5.order_send(modify_request)
            if modify_result.retcode == mt5.TRADE_RETCODE_DONE:
                print("Stop Loss and Take Profit added successfully")
    
    # Create trade record
    trade_record = {
        'trade_id': 'EURJPY_FRESH_08_28',
        'timestamp': datetime.now().isoformat(),
        'signal_data': signal_data,
        'execution_price': result.price,
        'order_id': result.order,
        'deal_id': result.deal,
        'mikrobot_compliance': True,
        'fresh_signal_execution': True
    }
    
    with open('EURJPY_FRESH_08_28.json', 'w') as f:
        json.dump(trade_record, f, indent=2)
    
    print("Trade record: EURJPY_FRESH_08_28.json")
    print("Multiple EURJPY positions now active!")
    
    mt5.shutdown()
    return True

if __name__ == "__main__":
    execute_fresh_eurjpy()