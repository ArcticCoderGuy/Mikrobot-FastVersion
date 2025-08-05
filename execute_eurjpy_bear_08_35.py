#!/usr/bin/env python3
"""
CRITICAL: Execute EURJPY BEAR signal at 08:35
This is a SELL signal - trend reversal detected
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

def execute_eurjpy_bear():
    print("EXECUTING EURJPY BEAR SIGNAL - 08:35")
    print("=" * 40)
    print("TREND REVERSAL DETECTED - SELL SIGNAL")
    
    # EURJPY BEAR signal at 08:35
    bear_signal = {
        'timestamp': '2025.08.04 08:35',
        'symbol': 'EURJPY',
        'phase_1_m5_bos': {
            'direction': 'BEAR'  # KEY: Direction changed to BEAR
        },
        'phase_4_ylipip': {
            'target': 171.04800, 
            'current': 171.04800, 
            'triggered': True
        },
        'trade_direction': 'BEAR',  # SELL signal
        'ylipip_trigger': 0.60
    }
    
    print("EURJPY BEAR SIGNAL ANALYSIS:")
    print(f"Time: {bear_signal['timestamp']}")
    print(f"Direction: {bear_signal['trade_direction']} (SELL)")
    print(f"Target: {bear_signal['phase_4_ylipip']['target']}")
    print(f"0.6 Ylipip: TRIGGERED")
    print("This will HEDGE existing BULL positions!")
    print()
    
    if not mt5.initialize():
        print("ERROR: MT5 failed")
        return False
    
    account_info = mt5.account_info()
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    
    # Check existing EURJPY positions
    eurjpy_positions = mt5.positions_get(symbol="EURJPY")
    print(f"Existing EURJPY positions: {len(eurjpy_positions) if eurjpy_positions else 0}")
    
    if eurjpy_positions:
        total_eurjpy_pnl = sum(pos.profit for pos in eurjpy_positions)
        print(f"Current EURJPY P&L: ${total_eurjpy_pnl:.2f}")
        print("Adding BEAR (SELL) position as hedge...")
    print()
    
    # Get current EURJPY price
    tick = mt5.symbol_info_tick("EURJPY")
    if tick is None:
        print("ERROR: Cannot get EURJPY price")
        mt5.shutdown()
        return False
    
    entry_price = tick.bid  # SELL at bid price
    sl_price = entry_price + 0.08  # Stop loss ABOVE entry for SELL
    tp_price = entry_price - 0.16  # Take profit BELOW entry for SELL
    
    print(f"EURJPY BEAR TRADE PARAMETERS:")
    print(f"Entry Price: {entry_price:.3f} (SELL)")
    print(f"Stop Loss: {sl_price:.3f} (above entry)")
    print(f"Take Profit: {tp_price:.3f} (below entry)")
    print(f"Risk: ${abs(sl_price - entry_price) * 100 * 0.01:.2f}")
    print()
    
    # Execute EURJPY SELL (BEAR)
    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": "EURJPY",
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_SELL,  # SELL order for BEAR
        "deviation": 20,
        "magic": 999888,
        "comment": "EURJPY_BEAR_08_35",
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    print("EXECUTING EURJPY SELL...")
    result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"FOK failed, trying IOC: {result.comment}")
        order_request["type_filling"] = mt5.ORDER_FILLING_IOC
        result = mt5.order_send(order_request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"IOC failed, trying RETURN: {result.comment}")
        order_request["type_filling"] = mt5.ORDER_FILLING_RETURN
        result = mt5.order_send(order_request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print("SUCCESS: EURJPY BEAR (SELL) EXECUTED!")
        print(f"Order ID: {result.order}")
        print(f"Deal ID: {result.deal}")
        print(f"Execution Price: {result.price:.3f}")
        print()
        
        # Add SL/TP to SELL position
        positions = mt5.positions_get(symbol="EURJPY")
        for pos in positions:
            if pos.ticket == result.order and pos.type == 1:  # SELL position
                modify_request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": "EURJPY",
                    "position": pos.ticket,
                    "sl": sl_price,
                    "tp": tp_price,
                }
                
                modify_result = mt5.order_send(modify_request)
                if modify_result.retcode == mt5.TRADE_RETCODE_DONE:
                    print("BEAR position SL/TP added successfully!")
                break
        
        # Create BEAR trade record
        bear_trade_record = {
            'trade_id': 'EURJPY_BEAR_08_35',
            'timestamp': datetime.now().isoformat(),
            'signal_data': bear_signal,
            'symbol': 'EURJPY',
            'action': 'SELL',
            'direction': 'BEAR',
            'execution_price': result.price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'order_id': result.order,
            'deal_id': result.deal,
            'strategy': 'HEDGE_EXISTING_BULLS',
            'mikrobot_compliance': True,
            'trend_reversal': True
        }
        
        with open('EURJPY_BEAR_08_35.json', 'w') as f:
            json.dump(bear_trade_record, f, indent=2)
        
        print("HEDGING STRATEGY IMPLEMENTED:")
        print("- Previous EURJPY BULL positions")
        print("- New EURJPY BEAR position (hedge)")
        print("- Risk reduced through opposite direction")
        print()
        print("Trade record: EURJPY_BEAR_08_35.json")
        print("TREND REVERSAL SUCCESSFULLY CAPTURED!")
        
    else:
        print(f"EURJPY BEAR failed: {result.comment}")
    
    # Final position summary
    final_positions = mt5.positions_get()
    print()
    print("FINAL POSITION SUMMARY:")
    eurjpy_bulls = 0
    eurjpy_bears = 0
    
    for pos in final_positions:
        if pos.symbol == "EURJPY":
            if pos.type == 0:  # BUY
                eurjpy_bulls += 1
            else:  # SELL
                eurjpy_bears += 1
    
    print(f"EURJPY BULLS (BUY): {eurjpy_bulls}")
    print(f"EURJPY BEARS (SELL): {eurjpy_bears}")
    print(f"Total EURJPY positions: {eurjpy_bulls + eurjpy_bears}")
    print("HEDGING STRATEGY: ACTIVE" if eurjpy_bears > 0 else "HEDGING STRATEGY: INACTIVE")
    
    mt5.shutdown()
    return result.retcode == mt5.TRADE_RETCODE_DONE

if __name__ == "__main__":
    execute_eurjpy_bear()