#!/usr/bin/env python3
"""
URGENT GBPJPY BEAR EXECUTION
===========================
GBPJPY M5 BOS signal triggered with YLIPIP at 07:41
Signal details:
- Symbol: GBPJPY
- Direction: BEAR
- M5 BOS: 195.61600
- Current: 195.60800
- YLIPIP: TRIGGERED
"""

import MetaTrader5 as mt5
import json
import time
from datetime import datetime

def ascii_print(text):
    """ASCII-only print to avoid encoding issues"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def calculate_gbpjpy_position_size(account_balance, risk_percent=0.55):
    """Calculate proper position size for GBPJPY based on ATR"""
    risk_amount = account_balance * (risk_percent / 100)  # 0.55% risk
    atr_pips = 10  # ATR in pips for GBPJPY
    
    # GBPJPY: 1 pip = 0.01, pip value = $0.051 per lot approximately
    # For JPY pairs, pip value = (0.01 / current_rate) * base_currency_amount
    usd_per_pip_per_lot = 0.051  # Approximate for GBPJPY
    
    lot_size = risk_amount / (atr_pips * usd_per_pip_per_lot)
    return round(min(lot_size, 5.0), 2)  # Cap at 5 lots for safety

def execute_gbpjpy_bear():
    """Execute GBPJPY BEAR trade based on signal"""
    
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
    
    # Calculate position size
    lot_size = calculate_gbpjpy_position_size(balance)
    risk_amount = balance * 0.0055
    
    ascii_print(f"GBPJPY POSITION SIZE: {lot_size} lots")
    ascii_print(f"Risk Amount: ${risk_amount:.2f} (0.55%)")
    
    # Signal parameters
    symbol = "GBPJPY"
    m5_bos = 195.61600
    current_price = 195.60800  # From signal
    direction = "BEAR"  # SELL
    
    # Calculate stops based on signal (BEAR = SELL)
    entry_price = current_price
    stop_loss = m5_bos + 0.00100  # 10 pips above BOS (for SELL, SL is above entry)
    take_profit = current_price - 0.00300  # 30 pips target (for SELL, TP is below entry)
    
    ascii_print(f"")
    ascii_print(f"GBPJPY BEAR TRADE PARAMETERS:")
    ascii_print(f"  Entry: {entry_price}")
    ascii_print(f"  Stop Loss: {stop_loss}")
    ascii_print(f"  Take Profit: {take_profit}")
    ascii_print(f"  Lot Size: {lot_size}")
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
        "comment": "GBPJPY_BEAR_YLIPIP_URGENT",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    
    # Execute trade
    ascii_print("EXECUTING GBPJPY BEAR TRADE...")
    result = mt5.order_send(request)
    
    if result is None:
        ascii_print("FAILED: order_send returned None")
        return False
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        ascii_print(f"FAILED: {result.retcode} - {result.comment}")
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
        "signal_type": "M5_BOS_YLIPIP",
        "m5_bos_price": m5_bos,
        "entry_price": float(result.price),
        "lot_size": float(result.volume),
        "risk_amount": risk_amount,
        "risk_percent": 0.55,
        "ticket": result.order,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "account_balance": balance,
        "executed_at": "07:41_YLIPIP_TRIGGER",
        "status": "EXECUTED_URGENTLY"
    }
    
    with open("GBPJPY_BEAR_URGENT_PROOF.json", "w") as f:
        json.dump(proof, f, indent=2, ensure_ascii=True)
    
    ascii_print(f"")
    ascii_print(f"PROOF SAVED: GBPJPY_BEAR_URGENT_PROOF.json")
    ascii_print(f"GBPJPY BEAR TRADE EXECUTED SUCCESSFULLY!")
    
    return True

if __name__ == "__main__":
    ascii_print("URGENT GBPJPY BEAR EXECUTION")
    ascii_print("=" * 40)
    
    success = execute_gbpjpy_bear()
    
    if success:
        ascii_print("MONEY-MAKING TRADE EXECUTED!")
    else:
        ascii_print("TRADE EXECUTION FAILED!")
        
    # Cleanup
    mt5.shutdown()