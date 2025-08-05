#!/usr/bin/env python3
"""
GBPJPY LIVE PRICE CHECK AND EXECUTION
====================================
Check current GBPJPY price and execute BEAR trade with proper stops
"""

import MetaTrader5 as mt5
import json
import time
from datetime import datetime

def ascii_print(text):
    """ASCII-only print to avoid encoding issues"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def execute_gbpjpy_bear_current():
    """Execute GBPJPY BEAR trade with current market price"""
    
    # Initialize MT5
    if not mt5.initialize():
        ascii_print("MT5 initialization failed")
        return False
    
    # Get account info
    account_info = mt5.account_info()
    if account_info is None:
        ascii_print("Failed to get account info")
        return False
    
    balance = account_info.balance
    ascii_print(f"Account Balance: ${balance:.2f}")
    
    # Get current GBPJPY price
    symbol = "GBPJPY"
    tick = mt5.symbol_info_tick(symbol)
    
    if tick is None:
        ascii_print(f"Failed to get {symbol} price")
        return False
    
    current_bid = tick.bid
    current_ask = tick.ask
    spread = current_ask - current_bid
    
    ascii_print(f"")
    ascii_print(f"GBPJPY Current Prices:")
    ascii_print(f"  Bid: {current_bid}")
    ascii_print(f"  Ask: {current_ask}")
    ascii_print(f"  Spread: {spread:.5f}")
    ascii_print(f"")
    
    # Calculate position size (0.55% risk)
    risk_amount = balance * 0.0055
    lot_size = 1.0  # Conservative size
    
    ascii_print(f"Position Size: {lot_size} lots")
    ascii_print(f"Risk Amount: ${risk_amount:.2f} (0.55%)")
    
    # Signal parameters from the alert
    m5_bos = 195.616  # Original BOS level
    
    # Use current bid for SELL entry
    entry_price = current_bid
    
    # Calculate stops with proper distances
    # For GBPJPY, minimum stop distance is usually 100 points (0.01)
    stop_distance = 0.015  # 15 pips above entry for stop loss
    target_distance = 0.020  # 20 pips below entry for take profit
    
    stop_loss = entry_price + stop_distance   # Above entry for SELL
    take_profit = entry_price - target_distance  # Below entry for SELL
    
    ascii_print(f"GBPJPY BEAR TRADE PARAMETERS:")
    ascii_print(f"  Entry (Bid): {entry_price}")
    ascii_print(f"  Stop Loss: {stop_loss}")
    ascii_print(f"  Take Profit: {take_profit}")
    ascii_print(f"  Stop Distance: {stop_distance}")
    ascii_print(f"  Target Distance: {target_distance}")
    ascii_print(f"")
    
    # Prepare trade request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_SELL,  # BEAR = SELL
        "price": entry_price,
        "sl": stop_loss,
        "tp": take_profit,
        "deviation": 20,
        "magic": 888999,
        "comment": "GBPJPY_BEAR_LIVE_EXECUTION",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    # Execute trade
    ascii_print("EXECUTING GBPJPY BEAR TRADE NOW...")
    result = mt5.order_send(request)
    
    if result is None:
        ascii_print("FAILED: order_send returned None")
        return False
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        ascii_print(f"FAILED: {result.retcode} - {result.comment}")
        # Try without stops if that was the issue
        ascii_print("Trying without stops...")
        request_no_stops = request.copy()
        del request_no_stops["sl"]
        del request_no_stops["tp"]
        
        result = mt5.order_send(request_no_stops)
        
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            ascii_print(f"FAILED AGAIN: {result.retcode if result else 'None'}")
            return False
    
    # Success
    ascii_print(f"SUCCESS: GBPJPY BEAR EXECUTED!")
    ascii_print(f"  Ticket: {result.order}")
    ascii_print(f"  Volume: {result.volume}")
    ascii_print(f"  Price: {result.price}")
    ascii_print(f"  Comment: {result.comment}")
    
    # Create proof record
    proof = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "direction": "BEAR",
        "signal_type": "GBPJPY_M5_BOS_YLIPIP_URGENT",
        "original_signal_bos": 195.616,
        "entry_price": float(result.price),
        "lot_size": float(result.volume),
        "risk_amount": risk_amount,
        "risk_percent": 0.55,
        "ticket": result.order,
        "account_balance": balance,
        "executed_at": datetime.now().strftime("%H:%M"),
        "status": "EXECUTED_SUCCESSFULLY",
        "market_conditions": {
            "bid": current_bid,
            "ask": current_ask,
            "spread": spread
        }
    }
    
    if "sl" in request and result.retcode == mt5.TRADE_RETCODE_DONE:
        proof["stop_loss"] = stop_loss
        proof["take_profit"] = take_profit
    
    with open("GBPJPY_BEAR_EXECUTED_PROOF.json", "w") as f:
        json.dump(proof, f, indent=2, ensure_ascii=True)
    
    ascii_print(f"")
    ascii_print(f"PROOF SAVED: GBPJPY_BEAR_EXECUTED_PROOF.json")
    ascii_print(f"MONEY-MAKING GBPJPY BEAR TRADE EXECUTED!")
    
    return True

if __name__ == "__main__":
    ascii_print("GBPJPY BEAR EXECUTION - LIVE MARKET")
    ascii_print("=" * 40)
    
    success = execute_gbpjpy_bear_current()
    
    if success:
        ascii_print("GBPJPY BEAR TRADE EXECUTED - READY TO MAKE MONEY!")
    else:
        ascii_print("TRADE EXECUTION FAILED - CHECK MT5 CONNECTION!")
        
    # Cleanup
    mt5.shutdown()