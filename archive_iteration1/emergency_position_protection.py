"""
EMERGENCY POSITION PROTECTION
Set Stop Loss and Take Profit for all unprotected positions
Based on M5/M1 BOS Strategy Rules
"""

import MetaTrader5 as mt5
from datetime import datetime
import time

# Account details
ACCOUNT = 95244786
PASSWORD = "Ua@tOnLp"
SERVER = "Ava-Demo 1-MT5"

# M5/M1 BOS Strategy Parameters
STRATEGY_CONFIG = {
    "sl_pips_default": 20,      # Default SL in pips
    "tp_ratio": 2.5,            # TP:SL ratio
    "pip_precision": 0.2,       # 0.2 pip precision
    "max_sl_pips": 50,          # Maximum SL distance
    "min_sl_pips": 10,          # Minimum SL distance
}

# Pip values for different symbols
PIP_VALUES = {
    "BTCUSD": 1.0,
    "ETHUSD": 0.1,
    "XRPUSD": 0.0001,
    "LTCUSD": 0.1,
    "EURUSD": 0.0001,
    "GBPUSD": 0.0001,
    "USDJPY": 0.01,
    "AUDUSD": 0.0001
}

def connect_mt5():
    """Connect to MT5"""
    if not mt5.initialize():
        print(f"MT5 initialization failed: {mt5.last_error()}")
        return False
    
    authorized = mt5.login(login=ACCOUNT, password=PASSWORD, server=SERVER)
    if not authorized:
        print(f"Login failed: {mt5.last_error()}")
        return False
    
    print(f"Connected to account {ACCOUNT}")
    return True

def get_pip_value(symbol):
    """Get pip value for symbol"""
    return PIP_VALUES.get(symbol, 0.0001)

def calculate_bos_levels(symbol, entry_price, position_type):
    """Calculate M5/M1 BOS strategy levels"""
    pip_value = get_pip_value(symbol)
    
    # Get recent M5 data for structure analysis
    try:
        m5_rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
        if m5_rates is None or len(m5_rates) < 10:
            # Use default levels if no data
            return calculate_default_levels(entry_price, position_type, pip_value)
        
        # Find recent highs and lows
        recent_highs = [rate['high'] for rate in m5_rates[-10:]]
        recent_lows = [rate['low'] for rate in m5_rates[-10:]]
        
        if position_type == 0:  # BUY position
            # SL below recent low
            support_level = min(recent_lows)
            sl_distance = max(entry_price - support_level, STRATEGY_CONFIG['min_sl_pips'] * pip_value)
            sl_distance = min(sl_distance, STRATEGY_CONFIG['max_sl_pips'] * pip_value)
            
            stop_loss = entry_price - sl_distance
            take_profit = entry_price + (sl_distance * STRATEGY_CONFIG['tp_ratio'])
            
        else:  # SELL position
            # SL above recent high
            resistance_level = max(recent_highs)
            sl_distance = max(resistance_level - entry_price, STRATEGY_CONFIG['min_sl_pips'] * pip_value)
            sl_distance = min(sl_distance, STRATEGY_CONFIG['max_sl_pips'] * pip_value)
            
            stop_loss = entry_price + sl_distance
            take_profit = entry_price - (sl_distance * STRATEGY_CONFIG['tp_ratio'])
        
        return stop_loss, take_profit, sl_distance / pip_value
        
    except Exception as e:
        print(f"Error calculating BOS levels for {symbol}: {e}")
        return calculate_default_levels(entry_price, position_type, pip_value)

def calculate_default_levels(entry_price, position_type, pip_value):
    """Calculate default levels when market data unavailable"""
    sl_pips = STRATEGY_CONFIG['sl_pips_default']
    tp_pips = sl_pips * STRATEGY_CONFIG['tp_ratio']
    
    if position_type == 0:  # BUY
        stop_loss = entry_price - (sl_pips * pip_value)
        take_profit = entry_price + (tp_pips * pip_value)
    else:  # SELL
        stop_loss = entry_price + (sl_pips * pip_value)
        take_profit = entry_price - (tp_pips * pip_value)
    
    return stop_loss, take_profit, sl_pips

def set_position_levels(ticket, sl, tp):
    """Set SL and TP for a position"""
    try:
        # Get position info
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return False, "Position not found"
        
        pos = position[0]
        
        # Prepare modification request
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": pos.symbol,
            "position": ticket,
            "sl": sl,
            "tp": tp,
            "magic": pos.magic,
            "comment": "M5M1_BOS_Protection"
        }
        
        # Send modification
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True, "Success"
        else:
            return False, f"Error {result.retcode}: {result.comment}"
            
    except Exception as e:
        return False, str(e)

def main():
    """Main protection function"""
    print("="*60)
    print("EMERGENCY POSITION PROTECTION")
    print("M5/M1 BOS Strategy Risk Management")
    print("="*60)
    
    if not connect_mt5():
        return
    
    # Get all positions
    positions = mt5.positions_get()
    if not positions:
        print("No positions found")
        return
    
    print(f"Found {len(positions)} positions")
    
    # Analyze unprotected positions
    unprotected = []
    protected = []
    
    for pos in positions:
        if pos.sl == 0.0 or pos.tp == 0.0:
            unprotected.append(pos)
        else:
            protected.append(pos)
    
    print(f"Unprotected positions: {len(unprotected)}")
    print(f"Protected positions: {len(protected)}")
    print()
    
    if not unprotected:
        print("All positions are already protected!")
        return
    
    # Show risk analysis
    total_exposure = sum(abs(pos.profit) for pos in unprotected)
    print(f"RISK ANALYSIS:")
    print(f"- Unprotected positions: {len(unprotected)}")
    print(f"- Current total exposure: ${total_exposure:.2f}")
    print(f"- Positions without SL: {sum(1 for pos in unprotected if pos.sl == 0.0)}")
    print(f"- Positions without TP: {sum(1 for pos in unprotected if pos.tp == 0.0)}")
    print()
    
    # Auto-apply protection (critical safety measure)
    print("CRITICAL: Setting protective levels for all unprotected positions")
    print("This will apply M5/M1 BOS strategy rules:")
    print("- Stop Loss based on recent structure levels")
    print("- Take Profit at 2.5:1 risk/reward ratio")
    print("- 0.2 pip precision alignment")
    print()
    print("AUTO-APPLYING PROTECTION (Risk Management Critical)")
    print()
    
    # Apply protection
    success_count = 0
    error_count = 0
    
    print("\nApplying protection...")
    print("-" * 60)
    
    for i, pos in enumerate(unprotected, 1):
        print(f"Position {i}/{len(unprotected)}: {pos.ticket} ({pos.symbol})")
        
        # Calculate optimal levels
        sl, tp, sl_pips = calculate_bos_levels(pos.symbol, pos.price_open, pos.type)
        
        # Round to pip precision
        pip_value = get_pip_value(pos.symbol)
        precision_factor = STRATEGY_CONFIG['pip_precision'] * pip_value
        sl = round(sl / precision_factor) * precision_factor
        tp = round(tp / precision_factor) * precision_factor
        
        print(f"  Entry: {pos.price_open:.5f}")
        print(f"  SL: {sl:.5f} ({sl_pips:.1f} pips)")
        print(f"  TP: {tp:.5f} ({sl_pips * STRATEGY_CONFIG['tp_ratio']:.1f} pips)")
        
        # Apply levels
        success, message = set_position_levels(pos.ticket, sl, tp)
        
        if success:
            print(f"  Status: SUCCESS")
            success_count += 1
        else:
            print(f"  Status: FAILED - {message}")
            error_count += 1
        
        print()
        time.sleep(0.1)  # Small delay between modifications
    
    # Final summary
    print("="*60)
    print("PROTECTION SUMMARY")
    print(f"Successfully protected: {success_count} positions")
    print(f"Failed: {error_count} positions")
    print(f"Total processed: {len(unprotected)} positions")
    print()
    
    if success_count > 0:
        print("Your positions are now protected with M5/M1 BOS strategy levels!")
        print("- Stop Loss: Based on recent market structure")
        print("- Take Profit: 2.5:1 risk/reward ratio")
        print("- All levels aligned to 0.2 pip precision")
    
    if error_count > 0:
        print(f"WARNING: {error_count} positions could not be protected")
        print("Please check these positions manually")
    
    # Show account status
    account = mt5.account_info()
    print(f"\nAccount Status:")
    print(f"Balance: ${account.balance:.2f}")
    print(f"Equity: ${account.equity:.2f}")
    print(f"Free Margin: ${account.margin_free:.2f}")
    
    mt5.shutdown()
    print("\nProtection complete!")

if __name__ == "__main__":
    main()