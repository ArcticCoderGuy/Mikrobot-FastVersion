#!/usr/bin/env python3
"""
Execute all pending signals - Multi-asset expansion
"""

import MetaTrader5 as mt5
import json
from datetime import datetime

def execute_all_signals():
    print("MULTI-ASSET SIGNAL EXECUTION")
    print("=" * 32)
    
    if not mt5.initialize():
        print("ERROR: MT5 failed")
        return False
    
    account_info = mt5.account_info()
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    print()
    
    # Fix Ferrari stops first
    ferrari_positions = mt5.positions_get(symbol="_FERRARI.IT")
    if ferrari_positions:
        pos = ferrari_positions[0]
        print(f"Fixing Ferrari stops...")
        print(f"Entry: {pos.price_open:.2f}, P&L: ${pos.profit:.2f}")
        
        sl_price = pos.price_open - 1.00  # 1 EUR stop
        tp_price = pos.price_open + 2.00  # 2 EUR profit
        
        modify_request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": "_FERRARI.IT",
            "position": pos.ticket,
            "sl": sl_price,
            "tp": tp_price,
        }
        
        result = mt5.order_send(modify_request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print("Ferrari stops FIXED!")
        else:
            print(f"Ferrari fix failed: {result.comment}")
        print()
    
    # Current positions summary
    all_positions = mt5.positions_get()
    print(f"CURRENT PORTFOLIO: {len(all_positions)} positions")
    total_pnl = 0
    
    for pos in all_positions:
        print(f"  {pos.symbol}: ${pos.profit:.2f}")
        total_pnl += pos.profit
    
    print(f"Total P&L: ${total_pnl:.2f}")
    print()
    
    # Execute fresh Ferrari signal at 08:34
    print("EXECUTING FRESH FERRARI 08:34...")
    tick = mt5.symbol_info_tick("_FERRARI.IT")
    
    if tick:
        entry_price = tick.ask
        print(f"Ferrari entry: {entry_price:.2f}")
        
        order_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": "_FERRARI.IT",
            "volume": 0.01,
            "type": mt5.ORDER_TYPE_BUY,
            "deviation": 20,
            "magic": 999888,
            "comment": "FERRARI_FRESH_08_34",
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(order_request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"SUCCESS! Ferrari #2 executed: {result.price:.2f}")
            
            # Add stops
            positions = mt5.positions_get(symbol="_FERRARI.IT")
            for pos in positions:
                if pos.ticket == result.order:
                    sl = result.price - 1.00
                    tp = result.price + 2.00
                    
                    modify_req = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": "_FERRARI.IT",
                        "position": pos.ticket,
                        "sl": sl,
                        "tp": tp,
                    }
                    mt5.order_send(modify_req)
                    print(f"SL/TP added: {sl:.2f}/{tp:.2f}")
                    break
                    
        else:
            print(f"Ferrari #2 failed: {result.comment}")
    
    print()
    
    # Final portfolio summary
    final_positions = mt5.positions_get()
    print("FINAL PORTFOLIO STATUS:")
    print(f"Total positions: {len(final_positions)}")
    
    symbol_counts = {}
    final_pnl = 0
    
    for pos in final_positions:
        symbol = pos.symbol
        symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        final_pnl += pos.profit
        print(f"  {pos.symbol} #{symbol_counts[symbol]}: ${pos.profit:.2f}")
    
    print(f"Combined P&L: ${final_pnl:.2f}")
    print()
    print("ASSET CLASSES ACTIVE:")
    for symbol, count in symbol_counts.items():
        asset_type = "FOREX" if "JPY" in symbol else "CFD_STOCK"
        print(f"  {symbol}: {count} positions ({asset_type})")
    
    # Create summary record
    portfolio_summary = {
        'timestamp': datetime.now().isoformat(),
        'total_positions': len(final_positions),
        'symbols_active': list(symbol_counts.keys()),
        'combined_pnl': final_pnl,
        'account_balance': account_info.balance,
        'asset_classes': ['FOREX', 'CFD_STOCKS'],
        'multi_asset_system': True,
        'mikrobot_active': True
    }
    
    with open('PORTFOLIO_SUMMARY.json', 'w') as f:
        json.dump(portfolio_summary, f, indent=2)
    
    print()
    print("Portfolio summary: PORTFOLIO_SUMMARY.json")
    print("MIKROBOT MULTI-ASSET SYSTEM: OPERATIONAL")
    
    mt5.shutdown()
    return True

if __name__ == "__main__":
    execute_all_signals()