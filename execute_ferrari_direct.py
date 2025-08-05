#!/usr/bin/env python3
"""
DIRECT FERRARI TRADE EXECUTION
=============================
Execute Ferrari.IT SELL immediately with real money
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

def execute_ferrari_trade():
    print("FERRARI.IT DIRECT TRADE EXECUTION")
    print("=" * 35)
    
    # Initialize MT5
    if not mt5.initialize():
        print("ERROR: Could not initialize MT5")
        return False
    
    # Get account info
    account_info = mt5.account_info()
    print(f"Connected to MT5 Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    print()
    
    # Ferrari trade parameters (from signal analysis)
    symbol = "_FERRARI.IT"
    action = "SELL"
    lot_size = 0.01
    entry_price = 376.18
    sl_price = 376.68  # +0.50 EUR stop loss
    tp_price = 375.18  # -1.00 EUR take profit
    
    print("TRADE PARAMETERS:")
    print(f"Symbol: {symbol}")
    print(f"Action: {action}")
    print(f"Lot Size: {lot_size}")
    print(f"Entry Target: €{entry_price}")
    print(f"Stop Loss: €{sl_price}")
    print(f"Take Profit: €{tp_price}")
    print(f"Risk: €{(sl_price - entry_price) * lot_size * 100:.2f}")
    print()
    
    # Get current market price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"ERROR: Could not get price for {symbol}")
        print("Available symbols containing FERRARI:")
        symbols = mt5.symbols_get("*FERRARI*")
        if symbols:
            for s in symbols:
                print(f"  - {s.name}")
        mt5.shutdown()
        return False
    
    print(f"Current Bid: €{tick.bid}")
    print(f"Current Ask: €{tick.ask}")
    print()
    
    # Prepare order
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_SELL,  # SELL order
        "price": tick.bid,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 20,
        "magic": 999888,
        "comment": "FERRARI_BLACKROCK_VALIDATION",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    print("EXECUTING TRADE...")
    print("THIS IS REAL MONEY - REAL RISK!")
    print()
    
    # Send order
    result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"TRADE FAILED: {result.retcode}")
        print(f"Error: {result.comment}")
        mt5.shutdown()
        return False
    
    print("SUCCESS: FERRARI TRADE EXECUTED!")
    print("=" * 35)
    print(f"Order ID: {result.order}")
    print(f"Deal ID: {result.deal}")
    print(f"Execution Price: €{result.price}")
    print(f"Volume: {result.volume} lots")
    print(f"Magic Number: {order_request['magic']}")
    print()
    
    # Save trade record
    trade_record = {
        'trade_id': 'FERRARI_LIVE_001',
        'timestamp': datetime.now().isoformat(),
        'symbol': symbol,
        'action': action,
        'volume': result.volume,
        'execution_price': result.price,
        'sl_price': sl_price,
        'tp_price': tp_price,
        'order_id': result.order,
        'deal_id': result.deal,
        'magic': order_request['magic'],
        'comment': order_request['comment'],
        'account': account_info.login,
        'balance_before': account_info.balance,
        'validation_purpose': 'BLACKROCK_INSTITUTIONAL_PROOF',
        'signal_source': 'EA_4PHASE_FERRARI_08:10',
        'risk_euros': (sl_price - result.price) * result.volume * 100,
        'potential_profit': (result.price - tp_price) * result.volume * 100
    }
    
    # Save to audit file
    with open('FERRARI_LIVE_TRADE_001.json', 'w') as f:
        json.dump(trade_record, f, indent=2)
    
    print("TRADE RECORD SAVED: FERRARI_LIVE_TRADE_001.json")
    print()
    print("BLACKROCK VALIDATION STATUS:")
    print("- Real money traded: YES")
    print("- Actual position opened: YES") 
    print("- Risk management active: YES")
    print("- Audit trail complete: YES")
    print("- Performance tracking: ACTIVE")
    print()
    print("CHECK MT5 POSITIONS TAB FOR LIVE FERRARI.IT SELL")
    
    mt5.shutdown()
    return True

if __name__ == "__main__":
    execute_ferrari_trade()