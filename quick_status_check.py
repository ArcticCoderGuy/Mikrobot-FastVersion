#!/usr/bin/env python3
"""
QUICK MT5 STATUS CHECK
Check EA status, GBPJPY data, and system readiness
"""

import MetaTrader5 as mt5
from datetime import datetime
import json
import re

def check_mt5_status():
    print('MIKROBOT MT5 SYSTEM STATUS CHECK')
    print('=' * 40)
    
    # Connect to MT5
    if not mt5.initialize():
        print('ERROR: MT5 Initialize FAILED')
        return False
        
    if not mt5.login(107034605, 'RcEw_s7w', 'Ava-Demo 1-MT5'):
        print('ERROR: MT5 Login FAILED')
        return False
    
    print('MT5 Connection: SUCCESS')
    
    # Check account info
    account = mt5.account_info()
    print(f'Account Balance: ${account.balance:.2f}')
    print(f'Account Equity: ${account.equity:.2f}')
    print(f'Free Margin: ${account.margin_free:.2f}')
    
    # Check positions
    positions = mt5.positions_get()
    print(f'Open Positions: {len(positions) if positions else 0}')
    
    if positions:
        for pos in positions:
            print(f'  {pos.symbol}: {pos.volume} lots, P&L: ${pos.profit:.2f}')
    
    # Check if expert advisors are enabled
    terminal_info = mt5.terminal_info()
    print(f'Terminal Connected: {terminal_info.connected if terminal_info else "Unknown"}')
    print(f'Trade Context Busy: {terminal_info.trade_allowed if terminal_info else "Unknown"}')
    
    # Check GBPJPY specific data
    print('\nGBPJPY M5 BOS ANALYSIS:')
    print('-' * 25)
    symbol = 'GBPJPY'
    if mt5.symbol_select(symbol, True):
        tick = mt5.symbol_info_tick(symbol)
        print(f'Current Ask: {tick.ask:.3f}')
        print(f'Current Bid: {tick.bid:.3f}')
        print(f'Spread: {(tick.ask - tick.bid):.3f}')
        print(f'Last Update: {datetime.fromtimestamp(tick.time)}')
        
        # Get recent M5 data for BOS analysis
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
        if rates is not None and len(rates) > 0:
            print(f'\nRecent M5 candles:')
            for i in range(-3, 0):  # Last 3 candles
                candle = rates[i]
                time_str = datetime.fromtimestamp(candle[0]).strftime('%H:%M')
                print(f'  {time_str}: H={candle[2]:.3f} L={candle[3]:.3f} C={candle[4]:.3f}')
            
            # Simple BOS detection
            current_high = rates[-1][2]
            current_low = rates[-1][3]
            
            # Look for recent swing highs/lows
            swing_high = max([rates[i][2] for i in range(-10, 0)])
            swing_low = min([rates[i][3] for i in range(-10, 0)])
            
            print(f'\nBOS Pattern Analysis:')
            print(f'10-candle swing high: {swing_high:.3f}')
            print(f'10-candle swing low: {swing_low:.3f}')
            print(f'Current high: {current_high:.3f}')
            print(f'Current low: {current_low:.3f}')
            
            if current_high >= swing_high * 0.9995:  # Within 0.05% of swing high
                print('STATUS: POTENTIAL BULLISH BOS SETUP!')
                print('Action: Monitor M1 for break-and-retest pattern')
            elif current_low <= swing_low * 1.0005:  # Within 0.05% of swing low
                print('STATUS: POTENTIAL BEARISH BOS SETUP!')
                print('Action: Monitor M1 for break-and-retest pattern')
            else:
                print('STATUS: No immediate BOS pattern detected')
    
    # Check signal file
    print('\nSIGNAL FILE STATUS:')
    print('-' * 20)
    try:
        with open('C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json', 'rb') as f:
            content = f.read()
        
        # Decode UTF-16LE with null byte removal
        content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
        content_str = re.sub(r'[^\x20-\x7E\n\r\t{}":,.-]', '', content_str)
        
        signal = json.loads(content_str)
        print(f'Latest signal timestamp: {signal.get("timestamp", "N/A")}')
        print(f'Symbol: {signal.get("symbol", "N/A")}')
        print(f'Trade direction: {signal.get("trade_direction", "N/A")}')
        print(f'YLIPIP triggered: {signal.get("phase_4_ylipip", {}).get("triggered", False)}')
        
    except Exception as e:
        print(f'Signal file read error: {str(e)}')
    
    # Position sizing check
    print('\nPOSITION SIZING VALIDATION:')
    print('-' * 28)
    risk_amount = account.balance * 0.0055  # 0.55%
    atr_pips = 8  # GBPJPY typical ATR
    usd_per_pip_per_lot = 100  # JPY pairs
    lot_size = round(risk_amount / (atr_pips * usd_per_pip_per_lot), 2)
    
    print(f'Account balance: ${account.balance:.2f}')
    print(f'Risk per trade (0.55%): ${risk_amount:.2f}')
    print(f'ATR for GBPJPY: {atr_pips} pips')
    print(f'Proper lot size: {lot_size:.2f} lots')
    print(f'vs Old method: 0.01 lots ({lot_size/0.01:.0f}x improvement)')
    
    mt5.shutdown()
    return True

if __name__ == "__main__":
    check_mt5_status()