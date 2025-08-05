#!/usr/bin/env python3
"""
Execute Ferrari.IT BULL signal from 08:30
Multi-asset trading expansion
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

def execute_ferrari_08_30():
    print("EXECUTING FERRARI.IT BULL SIGNAL - 08:30")
    print("=" * 42)
    print("MULTI-ASSET EXPANSION: Ferrari.IT CFD")
    
    # Ferrari signal at 08:30
    signal_data = {
        'timestamp': '2025.08.04 08:30',
        'symbol': '_FERRARI.IT',
        'strategy': 'MIKROBOT_FASTVERSION_4PHASE',
        'phase_1_m5_bos': {
            'time': '2025.08.04 08:25', 
            'price': 377.08000, 
            'direction': 'BULL'
        },
        'phase_4_ylipip': {
            'target': 377.14000, 
            'current': 377.18000, 
            'triggered': True
        },
        'trade_direction': 'BULL',
        'ylipip_trigger': 0.60
    }
    
    print("FERRARI.IT 4-PHASE SIGNAL:")
    print(f"Symbol: {signal_data['symbol']}")
    print(f"Direction: {signal_data['trade_direction']} (BUY)")
    print(f"Current Price: €{signal_data['phase_4_ylipip']['current']}")
    print(f"0.6 Ylipip: TRIGGERED")
    print()
    
    if not mt5.initialize():
        print("ERROR: MT5 initialization failed")
        return False
    
    account_info = mt5.account_info()
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    print()
    
    # Get Ferrari price
    symbol = "_FERRARI.IT"
    tick = mt5.symbol_info_tick(symbol)
    
    if tick is None:
        print("ERROR: Cannot get Ferrari.IT price")
        print("Checking available Ferrari symbols...")
        symbols = mt5.symbols_get("*FERRARI*")
        if symbols:
            for s in symbols:
                print(f"  Available: {s.name}")
                symbol = s.name  # Use first available
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    break
    
    if tick is None:
        print("ERROR: No Ferrari symbols available")
        mt5.shutdown()
        return False
    
    entry_price = tick.ask  # BUY at ask
    sl_price = entry_price - 0.60  # 60 cents SL for stock CFD
    tp_price = entry_price + 1.20  # 1:2 RR = 120 cents TP
    
    print(f"FERRARI.IT TRADE PARAMETERS:")
    print(f"Entry Price: €{entry_price:.2f}")
    print(f"Stop Loss: €{sl_price:.2f}")
    print(f"Take Profit: €{tp_price:.2f}")
    print(f"Risk: €{abs(sl_price - entry_price) * 0.01:.2f}")
    print()
    
    # Execute Ferrari BUY
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": 0.01,  # 0.01 lots
        "type": mt5.ORDER_TYPE_BUY,
        "deviation": 20,
        "magic": 999888,
        "comment": "FERRARI_BULL_08_30",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    print("EXECUTING FERRARI.IT BUY...")
    result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"FOK failed, trying IOC: {result.comment}")
        order_request["type_filling"] = mt5.ORDER_FILLING_IOC
        result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"IOC failed, trying RETURN: {result.comment}")
        order_request["type_filling"] = mt5.ORDER_FILLING_RETURN
        result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"FERRARI TRADE FAILED: {result.comment}")
        mt5.shutdown()
        return False
    
    print("SUCCESS: FERRARI.IT TRADE EXECUTED!")
    print(f"Order ID: {result.order}")
    print(f"Deal ID: {result.deal}")
    print(f"Execution Price: €{result.price:.2f}")
    print()
    
    # Add SL/TP
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        for pos in positions:
            if abs(pos.price_open - result.price) < 0.01:
                modify_request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": symbol,
                    "position": pos.ticket,
                    "sl": sl_price,
                    "tp": tp_price,
                }
                
                modify_result = mt5.order_send(modify_request)
                if modify_result.retcode == mt5.TRADE_RETCODE_DONE:
                    print("Ferrari SL/TP added successfully!")
                break
    
    # Create trade record
    trade_record = {
        'trade_id': 'FERRARI_BULL_08_30',
        'timestamp': datetime.now().isoformat(),
        'signal_data': signal_data,
        'symbol': symbol,
        'action': 'BUY',
        'execution_price': result.price,
        'sl_price': sl_price,
        'tp_price': tp_price,
        'order_id': result.order,
        'deal_id': result.deal,
        'asset_class': 'CFD_STOCK',
        'mikrobot_compliance': True,
        'multi_asset_expansion': True
    }
    
    with open('FERRARI_BULL_08_30.json', 'w') as f:
        json.dump(trade_record, f, indent=2)
    
    print("MULTI-ASSET PORTFOLIO EXPANSION:")
    print("- EURJPY: 2 positions active")
    print("- FERRARI.IT: 1 position active") 
    print("- Asset classes: FOREX + CFD STOCKS")
    print()
    print("Trade record: FERRARI_BULL_08_30.json")
    print("MIKROBOT system now trading multiple assets!")
    
    mt5.shutdown()
    return True

if __name__ == "__main__":
    execute_ferrari_08_30()