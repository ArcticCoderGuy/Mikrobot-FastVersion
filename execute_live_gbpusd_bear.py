#!/usr/bin/env python3
"""
EMERGENCY GBPUSD BEAR EXECUTION
Execute the current 4-phase GBPUSD BEAR signal with YLIPIP trigger
"""

import sys
import json
import re
import MetaTrader5 as mt5
from datetime import datetime

# ASCII-only output enforcement
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    """Ensure ASCII-only output"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def read_signal_file():
    """Read and parse the signal file with proper encoding"""
    try:
        signal_path = r"C:\Users\HP\AppData\Roaming\MetaQuotes\Terminal\Common\Files\mikrobot_4phase_signal.json"
        
        with open(signal_path, 'rb') as f:
            content = f.read()
        
        # Handle UTF-16LE encoding with null bytes
        content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
        content_str = re.sub(r'[^\x20-\x7E{}":,.\-\s]', '', content_str)
        
        # Clean up extra spaces in JSON
        content_str = re.sub(r'\s+', ' ', content_str)
        content_str = content_str.strip()
        
        ascii_print(f"Raw signal content: {content_str[:200]}...")
        
        signal_data = json.loads(content_str)
        return signal_data
        
    except Exception as e:
        ascii_print(f"ERROR reading signal file: {e}")
        return None

def calculate_position_size(account_balance, atr_pips, symbol):
    """Calculate position size using 0.55% risk"""
    risk_percentage = 0.0055  # 0.55%
    risk_amount = account_balance * risk_percentage
    
    # USD pairs pip value
    if "USD" in symbol:
        usd_per_pip_per_lot = 10
    else:
        usd_per_pip_per_lot = 10
    
    lot_size = risk_amount / (atr_pips * usd_per_pip_per_lot)
    return round(lot_size, 2)

def execute_trade(signal):
    """Execute the GBPUSD BEAR trade"""
    if not mt5.initialize():
        ascii_print("FAILED to initialize MT5")
        return False
    
    try:
        # Get account info
        account_info = mt5.account_info()
        if not account_info:
            ascii_print("FAILED to get account info")
            return False
        
        ascii_print(f"Account Balance: {account_info.balance} EUR")
        ascii_print(f"Free Margin: {account_info.margin_free} EUR")
        
        symbol = signal['symbol']
        current_price = float(signal['current_price'])
        
        # Calculate ATR-based position size
        atr_pips = 8  # Default ATR for GBPUSD
        lot_size = calculate_position_size(account_info.balance, atr_pips, symbol)
        
        ascii_print(f"Calculated lot size: {lot_size} (Risk: 0.55%)")
        
        # BEAR trade parameters
        order_type = mt5.ORDER_TYPE_SELL
        entry_price = current_price
        
        # Dynamic stops based on signal structure
        stop_loss = entry_price + (atr_pips * 0.0001)  # Above entry for BEAR
        take_profit = entry_price - (atr_pips * 2 * 0.0001)  # Below entry for BEAR
        
        ascii_print(f"Entry: {entry_price}")
        ascii_print(f"Stop Loss: {stop_loss}")
        ascii_print(f"Take Profit: {take_profit}")
        
        # Prepare order request with FOK filling
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": order_type,
            "price": entry_price,
            "sl": stop_loss,
            "tp": take_profit,
            "deviation": 10,
            "magic": 20250805,
            "comment": "MIKROBOT_4PHASE_BEAR_YLIPIP",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK  # Fill or Kill
        }
        
        ascii_print("Executing GBPUSD BEAR trade with FOK filling...")
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            ascii_print(f"Order FAILED: {result.retcode} - {result.comment}")
            return False
        
        ascii_print("=== TRADE EXECUTED SUCCESSFULLY ===")
        ascii_print(f"Order ticket: {result.order}")
        ascii_print(f"Volume: {result.volume}")
        ascii_print(f"Price: {result.price}")
        ascii_print(f"Ask: {result.ask}")
        ascii_print(f"Bid: {result.bid}")
        
        return True
        
    except Exception as e:
        ascii_print(f"ERROR executing trade: {e}")
        return False
    
    finally:
        mt5.shutdown()

def main():
    ascii_print("=== EMERGENCY GBPUSD BEAR EXECUTION ===")
    ascii_print(f"Timestamp: {datetime.now()}")
    
    # Read current signal
    signal = read_signal_file()
    if not signal:
        ascii_print("FAILED to read signal file")
        return
    
    # Validate signal
    if signal.get('symbol') != 'GBPUSD':
        ascii_print(f"WARNING: Signal is for {signal.get('symbol')}, not GBPUSD")
    
    if not signal.get('phase_4_ylipip', {}).get('triggered'):
        ascii_print("WARNING: YLIPIP not triggered yet")
        return
    
    ascii_print(f"Signal: {signal['symbol']} {signal['trade_direction']}")
    ascii_print(f"YLIPIP Target: {signal['phase_4_ylipip']['target']}")
    ascii_print(f"Current Price: {signal['current_price']}")
    ascii_print(f"YLIPIP Triggered: {signal['phase_4_ylipip']['triggered']}")
    
    # Execute the trade
    success = execute_trade(signal)
    
    if success:
        ascii_print("=== TRADE EXECUTION COMPLETE ===")
        ascii_print("Monitoring for additional signals...")
    else:
        ascii_print("=== TRADE EXECUTION FAILED ===")

if __name__ == "__main__":
    main()