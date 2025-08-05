"""
FINAL POSITION MANAGER
Sets SL/TP for unprotected positions using market-based approach
Based on M5/M1 BOS Strategy principles
"""

import MetaTrader5 as mt5
from datetime import datetime
import time

# Account details
ACCOUNT = 107034605
PASSWORD = "RcEw_s7w"
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

def get_current_price(symbol):
    """Get current bid/ask prices"""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None
    return {'bid': tick.bid, 'ask': tick.ask, 'spread': tick.ask - tick.bid}

def calculate_market_based_levels(symbol, entry_price, position_type):
    """Calculate SL/TP based on current market and reasonable distances"""
    
    current_price = get_current_price(symbol)
    if not current_price:
        return None, None, "Cannot get current price"
    
    # Get symbol info for precision
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        return None, None, "Cannot get symbol info"
    
    point = symbol_info.point
    digits = symbol_info.digits
    
    # Calculate current P&L distance
    if position_type == 0:  # BUY
        current_market = current_price['bid']
        pnl_distance = current_market - entry_price
    else:  # SELL
        current_market = current_price['ask']
        pnl_distance = entry_price - current_market
    
    # Determine reasonable SL distance based on symbol and current situation
    if 'BTC' in symbol:
        base_distance = 100  # $100 for Bitcoin
    elif 'ETH' in symbol:
        base_distance = 30   # $30 for Ethereum
    elif 'XRP' in symbol or 'LTC' in symbol:
        base_distance = 0.05 if 'XRP' in symbol else 5  # $0.05 for XRP, $5 for LTC
    else:
        base_distance = 50 * point  # 50 points for forex
    
    # Adjust distance based on current P&L
    if pnl_distance > 0:  # Position in profit
        # Use smaller SL distance, maybe break-even or small profit lock
        sl_distance = max(base_distance * 0.5, abs(pnl_distance) * 0.3)
    else:  # Position in loss
        # Use reasonable SL to limit further losses
        sl_distance = max(base_distance, abs(pnl_distance) * 1.5)
    
    # Calculate final levels
    if position_type == 0:  # BUY
        stop_loss = entry_price - sl_distance
        take_profit = entry_price + (sl_distance * 2.5)  # 2.5:1 R:R
    else:  # SELL
        stop_loss = entry_price + sl_distance
        take_profit = entry_price - (sl_distance * 2.5)  # 2.5:1 R:R
    
    # Round to proper precision
    stop_loss = round(stop_loss, digits)
    take_profit = round(take_profit, digits)
    
    return stop_loss, take_profit, None

def set_position_levels_safe(ticket, sl, tp):
    """Set SL and TP with error handling"""
    try:
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return False, "Position not found"
        
        pos = position[0]
        
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": pos.symbol,
            "position": ticket,
            "sl": sl,
            "tp": tp,
            "magic": pos.magic,
            "comment": "Final_BOS_Protection"
        }
        
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True, "Success"
        elif result.retcode == 10016:
            return False, "Invalid stops (too close to market)"
        elif result.retcode == 10021:
            return False, "Market closed"
        else:
            return False, f"Error {result.retcode}: {result.comment}"
            
    except Exception as e:
        return False, str(e)

def close_position_safe(ticket):
    """Close a position safely"""
    try:
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return False, "Position not found"
        
        pos = position[0]
        
        # Get current price
        current_price = get_current_price(pos.symbol)
        if not current_price:
            return False, "Cannot get current price"
        
        # Determine close order type and price
        if pos.type == mt5.ORDER_TYPE_BUY:
            order_type = mt5.ORDER_TYPE_SELL
            price = current_price['bid']
        else:
            order_type = mt5.ORDER_TYPE_BUY
            price = current_price['ask']
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": order_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": pos.magic,
            "comment": "Risk_Management_Close"
        }
        
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True, f"Closed at {price:.5f}"
        else:
            return False, f"Error {result.retcode}: {result.comment}"
            
    except Exception as e:
        return False, str(e)

def main():
    """Main position management function"""
    print("="*60)
    print("FINAL POSITION MANAGER")
    print("M5/M1 BOS Strategy Protection & Risk Management")
    print("="*60)
    
    if not connect_mt5():
        return
    
    # Get account status
    account = mt5.account_info()
    print(f"Account: {account.login}")
    print(f"Balance: ${account.balance:.2f}")
    print(f"Equity: ${account.equity:.2f}")
    print(f"Free Margin: ${account.margin_free:.2f}")
    
    # Calculate current risk
    unrealized_pnl = account.equity - account.balance
    print(f"Unrealized P&L: ${unrealized_pnl:.2f}")
    print()
    
    # Get all positions
    positions = mt5.positions_get()
    if not positions:
        print("No positions found")
        return
    
    print(f"Total positions: {len(positions)}")
    
    # Analyze positions
    unprotected = []
    severe_loss = []
    
    for pos in positions:
        if pos.sl == 0.0 or pos.tp == 0.0:
            unprotected.append(pos)
        if pos.profit < -100:  # Losing more than $100
            severe_loss.append(pos)
    
    print(f"Unprotected positions: {len(unprotected)}")
    print(f"Positions with severe loss (>$100): {len(severe_loss)}")
    print()
    
    # Handle severe loss positions first
    if severe_loss:
        print("SEVERE LOSS POSITIONS:")
        total_severe_loss = sum(pos.profit for pos in severe_loss)
        print(f"Total severe loss: ${total_severe_loss:.2f}")
        print()
        
        print("Options for severe loss positions:")
        print("1. Close immediately to stop further losses")
        print("2. Set wide stop losses and hope for recovery")
        print("3. Leave as is (not recommended)")
        print()
        
        # For automated risk management, close positions losing >$150
        very_bad_positions = [pos for pos in severe_loss if pos.profit < -150]
        
        if very_bad_positions:
            print(f"Auto-closing {len(very_bad_positions)} positions losing >$150...")
            for pos in very_bad_positions:
                print(f"Closing {pos.ticket} ({pos.symbol}): ${pos.profit:.2f}")
                success, message = close_position_safe(pos.ticket)
                if success:
                    print(f"  SUCCESS: {message}")
                else:
                    print(f"  FAILED: {message}")
                time.sleep(0.5)
            print()
    
    # Protect remaining unprotected positions
    if unprotected:
        print("PROTECTING UNPROTECTED POSITIONS:")
        print("-" * 40)
        
        protection_success = 0
        protection_failed = 0
        
        for i, pos in enumerate(unprotected, 1):
            # Skip if already closed
            current_positions = mt5.positions_get(ticket=pos.ticket)
            if not current_positions:
                continue
            
            print(f"Position {i}: {pos.ticket} ({pos.symbol})")
            print(f"  Entry: {pos.price_open:.5f}")
            print(f"  Current P&L: ${pos.profit:.2f}")
            
            # Calculate protection levels
            sl, tp, error = calculate_market_based_levels(
                pos.symbol, pos.price_open, pos.type
            )
            
            if error:
                print(f"  FAILED: {error}")
                protection_failed += 1
                continue
            
            print(f"  Proposed SL: {sl:.5f}")
            print(f"  Proposed TP: {tp:.5f}")
            
            # Apply protection
            success, message = set_position_levels_safe(pos.ticket, sl, tp)
            
            if success:
                print(f"  SUCCESS: Protection applied")
                protection_success += 1
            else:
                print(f"  FAILED: {message}")
                protection_failed += 1
                
                # If protection fails due to distance, try closing if losing
                if "too close" in message.lower() and pos.profit < -50:
                    print(f"  Attempting to close losing position...")
                    close_success, close_message = close_position_safe(pos.ticket)
                    if close_success:
                        print(f"  CLOSED: {close_message}")
                    else:
                        print(f"  CLOSE FAILED: {close_message}")
            
            print()
            time.sleep(0.3)
        
        print("PROTECTION SUMMARY:")
        print(f"Successfully protected: {protection_success}")
        print(f"Failed to protect: {protection_failed}")
        print()
    
    # Final account status
    account = mt5.account_info()
    positions = mt5.positions_get()
    
    print("FINAL STATUS:")
    print(f"Balance: ${account.balance:.2f}")
    print(f"Equity: ${account.equity:.2f}")
    print(f"Active positions: {len(positions) if positions else 0}")
    
    if positions:
        protected_count = sum(1 for pos in positions if pos.sl != 0.0 and pos.tp != 0.0)
        print(f"Protected positions: {protected_count}/{len(positions)}")
        
        current_pnl = sum(pos.profit for pos in positions)
        print(f"Total unrealized P&L: ${current_pnl:.2f}")
    
    print()
    print("RECOMMENDATIONS:")
    print("1. Monitor protected positions for break-even opportunities")
    print("2. Manually review any remaining unprotected positions")
    print("3. Consider reducing position sizes for future trades")
    print("4. Implement proper risk management from trade entry")
    
    mt5.shutdown()
    print("\nPosition management complete!")

if __name__ == "__main__":
    main()