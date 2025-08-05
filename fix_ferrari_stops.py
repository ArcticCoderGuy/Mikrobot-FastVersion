#!/usr/bin/env python3
"""
Fix Ferrari.IT position stops - Invalid stops error resolution
"""

import MetaTrader5 as mt5

def fix_ferrari_stops():
    print("FIXING FERRARI.IT STOP LOSS/TAKE PROFIT")
    print("=" * 40)
    
    if not mt5.initialize():
        print("ERROR: MT5 initialization failed")
        return False
    
    # Get Ferrari position
    positions = mt5.positions_get(symbol="_FERRARI.IT")
    if not positions:
        print("ERROR: No Ferrari position found")
        mt5.shutdown()
        return False
    
    ferrari_pos = positions[0]
    print(f"Ferrari Position Found:")
    print(f"  Ticket: {ferrari_pos.ticket}")
    print(f"  Entry: €{ferrari_pos.price_open:.2f}")
    print(f"  Current: €{ferrari_pos.price_current:.2f}")
    print(f"  Current SL: {ferrari_pos.sl}")
    print(f"  Current TP: {ferrari_pos.tp}")
    
    # Get symbol info for proper stop levels
    symbol_info = mt5.symbol_info("_FERRARI.IT")
    if symbol_info is None:
        print("ERROR: Cannot get Ferrari symbol info")
        mt5.shutdown()
        return False
    
    print(f"Symbol Info:")
    print(f"  Min Stop Level: {symbol_info.stops_level}")
    print(f"  Point: {symbol_info.point}")
    print(f"  Tick Size: {symbol_info.trade_tick_size}")
    
    # Calculate proper stops with minimum distance
    entry_price = ferrari_pos.price_open
    min_distance = symbol_info.stops_level * symbol_info.point
    
    # For CFD stocks, use larger stops
    stop_distance = max(0.60, min_distance * 2)  # At least 60 cents or 2x min
    
    sl_price = entry_price - stop_distance
    tp_price = entry_price + (stop_distance * 2)  # 1:2 RR
    
    print(f"Calculated Stops:")
    print(f"  Stop Distance: €{stop_distance:.2f}")
    print(f"  New SL: €{sl_price:.2f}")
    print(f"  New TP: €{tp_price:.2f}")
    
    # Apply corrected stops
    modify_request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": "_FERRARI.IT",
        "position": ferrari_pos.ticket,
        "sl": sl_price,
        "tp": tp_price,
    }
    
    print("Applying corrected stops...")
    result = mt5.order_send(modify_request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print("SUCCESS: Ferrari stops corrected!")
        print(f"SL: €{sl_price:.2f}")
        print(f"TP: €{tp_price:.2f}")
    else:
        print(f"FAILED: {result.retcode} - {result.comment}")
        
        # Try with even larger distance
        larger_distance = stop_distance * 2
        sl_price = entry_price - larger_distance
        tp_price = entry_price + larger_distance
        
        modify_request["sl"] = sl_price
        modify_request["tp"] = tp_price
        
        print(f"Trying larger distance: €{larger_distance:.2f}")
        result = mt5.order_send(modify_request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print("SUCCESS: Ferrari stops set with larger distance!")
        else:
            print(f"Still failed: {result.comment}")
    
    mt5.shutdown()
    return result.retcode == mt5.TRADE_RETCODE_DONE

if __name__ == "__main__":
    fix_ferrari_stops()