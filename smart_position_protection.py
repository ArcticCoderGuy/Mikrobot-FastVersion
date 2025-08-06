"""
SMART POSITION PROTECTION
Set proper SL/TP levels respecting broker requirements
M5/M1 BOS Strategy with dynamic distance calculation
"""

import MetaTrader5 as mt5
from datetime import datetime
import time

# Account details
ACCOUNT = 95244786
PASSWORD = "Ua@tOnLp"
SERVER = "Ava-Demo 1-MT5"

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

def get_symbol_info(symbol):
    """Get symbol information including minimum distances"""
    info = mt5.symbol_info(symbol)
    if info is None:
        return None
    
    return {
        'point': info.point,
        'digits': info.digits,
        'stops_level': info.stops_level,
        'freeze_level': info.freeze_level,
        'trade_tick_size': info.trade_tick_size,
        'trade_tick_value': info.trade_tick_value
    }

def get_current_price(symbol):
    """Get current bid/ask prices"""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None
    return {'bid': tick.bid, 'ask': tick.ask}

def calculate_safe_levels(symbol, entry_price, position_type, current_price):
    """Calculate safe SL/TP levels respecting broker requirements"""
    symbol_info = get_symbol_info(symbol)
    if not symbol_info:
        return None, None, "Cannot get symbol info"
    
    point = symbol_info['point']
    stops_level = symbol_info['stops_level']
    
    # Minimum distance in price terms
    min_distance = stops_level * point
    
    # Use current market price for distance calculation
    if position_type == 0:  # BUY position
        market_price = current_price['bid']
    else:  # SELL position
        market_price = current_price['ask']
    
    # Calculate safer distances based on broker requirements
    # Use at least 3x the minimum required distance for safety
    safe_distance = max(min_distance * 3, 50 * point)  # At least 50 points
    
    if position_type == 0:  # BUY position
        # For BUY: SL below entry, TP above entry
        stop_loss = entry_price - safe_distance
        take_profit = entry_price + (safe_distance * 2.5)  # 2.5:1 R:R
        
        # Ensure SL is far enough from current market
        if market_price - stop_loss < min_distance:
            stop_loss = market_price - min_distance
            take_profit = entry_price + ((entry_price - stop_loss) * 2.5)
    
    else:  # SELL position
        # For SELL: SL above entry, TP below entry
        stop_loss = entry_price + safe_distance
        take_profit = entry_price - (safe_distance * 2.5)  # 2.5:1 R:R
        
        # Ensure SL is far enough from current market
        if stop_loss - market_price < min_distance:
            stop_loss = market_price + min_distance
            take_profit = entry_price - ((stop_loss - entry_price) * 2.5)
    
    # Round to symbol's point precision
    digits = symbol_info['digits']
    stop_loss = round(stop_loss, digits)
    take_profit = round(take_profit, digits)
    
    return stop_loss, take_profit, None

def set_position_levels(ticket, sl, tp):
    """Set SL and TP for a position with validation"""
    try:
        # Get position info
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return False, "Position not found"
        
        pos = position[0]
        
        # Get current market price for validation
        current_price = get_current_price(pos.symbol)
        if not current_price:
            return False, "Cannot get current price"
        
        symbol_info = get_symbol_info(pos.symbol)
        if not symbol_info:
            return False, "Cannot get symbol info"
        
        min_distance = symbol_info['stops_level'] * symbol_info['point']
        
        # Validate distances
        if pos.type == 0:  # BUY position
            if current_price['bid'] - sl < min_distance:
                return False, f"SL too close to market (min: {min_distance})"
        else:  # SELL position
            if sl - current_price['ask'] < min_distance:
                return False, f"SL too close to market (min: {min_distance})"
        
        # Prepare modification request
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": pos.symbol,
            "position": ticket,
            "sl": sl,
            "tp": tp,
            "magic": pos.magic,
            "comment": "Smart_BOS_Protection"
        }
        
        # Send modification
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True, "Success"
        else:
            return False, f"Error {result.retcode}: {result.comment}"
            
    except Exception as e:
        return False, str(e)

def analyze_and_protect_positions():
    """Analyze and protect all unprotected positions"""
    
    # Get all positions
    positions = mt5.positions_get()
    if not positions:
        print("No positions found")
        return
    
    print(f"Found {len(positions)} positions")
    
    # Separate protected and unprotected
    unprotected = []
    for pos in positions:
        if pos.sl == 0.0 or pos.tp == 0.0:
            unprotected.append(pos)
    
    print(f"Unprotected positions: {len(unprotected)}")
    
    if not unprotected:
        print("All positions already protected!")
        return
    
    # Show current exposure
    total_exposure = sum(abs(pos.profit) for pos in unprotected)
    print(f"Current exposure: ${total_exposure:.2f}")
    print()
    
    # Process each unprotected position
    success_count = 0
    error_count = 0
    
    print("Applying smart protection...")
    print("-" * 60)
    
    for i, pos in enumerate(unprotected, 1):
        print(f"Position {i}/{len(unprotected)}: {pos.ticket} ({pos.symbol})")
        
        # Get current market price
        current_price = get_current_price(pos.symbol)
        if not current_price:
            print(f"  Status: FAILED - Cannot get current price")
            error_count += 1
            continue
        
        # Calculate safe levels
        sl, tp, error = calculate_safe_levels(
            pos.symbol, pos.price_open, pos.type, current_price
        )
        
        if error:
            print(f"  Status: FAILED - {error}")
            error_count += 1
            continue
        
        # Show calculated levels
        print(f"  Entry: {pos.price_open:.5f}")
        print(f"  Current: {current_price['bid']:.5f}/{current_price['ask']:.5f}")
        print(f"  SL: {sl:.5f}")
        print(f"  TP: {tp:.5f}")
        
        # Apply protection
        success, message = set_position_levels(pos.ticket, sl, tp)
        
        if success:
            print(f"  Status: SUCCESS")
            success_count += 1
        else:
            print(f"  Status: FAILED - {message}")
            error_count += 1
        
        print()
        time.sleep(0.2)  # Small delay
    
    # Summary
    print("="*60)
    print("PROTECTION SUMMARY")
    print(f"Successfully protected: {success_count}")
    print(f"Failed: {error_count}")
    print(f"Protection rate: {(success_count/(success_count+error_count)*100):.1f}%")
    
    return success_count, error_count

def close_problematic_positions():
    """Option to close positions that cannot be protected"""
    
    positions = mt5.positions_get()
    if not positions:
        return
    
    # Find positions still without protection and in significant loss
    problematic = []
    for pos in positions:
        if pos.sl == 0.0 and pos.profit < -50:  # No SL and losing >$50
            problematic.append(pos)
    
    if not problematic:
        print("No problematic positions found")
        return
    
    print(f"\nFound {len(problematic)} problematic positions (no SL, significant loss):")
    
    total_loss = sum(pos.profit for pos in problematic)
    print(f"Total loss from problematic positions: ${total_loss:.2f}")
    
    for pos in problematic[:5]:  # Show top 5
        print(f"  {pos.ticket}: {pos.symbol} ${pos.profit:.2f}")
    
    print("\nRecommendation: Close these positions to limit further losses")
    print("Or set manual stop losses in MT5 terminal")

def main():
    """Main function"""
    print("="*60)
    print("SMART POSITION PROTECTION")
    print("M5/M1 BOS Strategy with Broker-Safe Levels")
    print("="*60)
    
    if not connect_mt5():
        return
    
    # Get account info
    account = mt5.account_info()
    print(f"Account Balance: ${account.balance:.2f}")
    print(f"Account Equity: ${account.equity:.2f}")
    print(f"Free Margin: ${account.margin_free:.2f}")
    print()
    
    # Apply protection
    success_count, error_count = analyze_and_protect_positions()
    
    # If many failures, suggest alternatives
    if error_count > success_count:
        print("\nMANY POSITIONS COULD NOT BE AUTO-PROTECTED")
        print("This is likely due to:")
        print("1. Positions too close to current market price")
        print("2. Broker minimum distance requirements")
        print("3. Weekend/market closed restrictions")
        print()
        print("RECOMMENDATIONS:")
        print("1. Manually set SL/TP in MT5 terminal")
        print("2. Close losing positions to limit risk")
        print("3. Wait for market to move away from entry prices")
        
        close_problematic_positions()
    
    # Final account status
    account = mt5.account_info()
    print(f"\nFinal Account Status:")
    print(f"Balance: ${account.balance:.2f}")
    print(f"Equity: ${account.equity:.2f}")
    print(f"Unrealized P&L: ${account.equity - account.balance:.2f}")
    
    mt5.shutdown()
    print("\nSmart protection complete!")

if __name__ == "__main__":
    main()