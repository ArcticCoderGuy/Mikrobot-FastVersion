#!/usr/bin/env python3
"""
MT5 Simple Toolbox Reader - ASCII only, no Unicode issues
"""

import MetaTrader5 as mt5
from datetime import datetime
import json
from pathlib import Path
import time

def main():
    print('MT5 Toolbox State Reader - ASCII Version')
    print('=' * 60)

    # Initialize MT5
    if mt5.initialize():
        print('[OK] MT5 Connected')
        
        # Get basic info
        terminal_info = mt5.terminal_info()
        account_info = mt5.account_info()
        
        if terminal_info:
            print(f'[INFO] Terminal: {terminal_info.company} Build {terminal_info.build}')
            print(f'[INFO] Connected: {terminal_info.connected}')
            print(f'[INFO] Trade Allowed: {terminal_info.trade_allowed}')
            print(f'[INFO] Ping: {terminal_info.ping_last}ms')
        
        if account_info:
            print(f'[ACCOUNT] Login: {account_info.login}')
            print(f'[ACCOUNT] Balance: ${account_info.balance:,.2f}')
            print(f'[ACCOUNT] Equity: ${account_info.equity:,.2f}')
            print(f'[ACCOUNT] Free Margin: ${account_info.margin_free:,.2f}')
        
        # Check positions (Trade Tab)
        positions = mt5.positions_get()
        print(f'\n[TRADE TAB] Open Positions: {len(positions) if positions else 0}')
        if positions:
            for i, pos in enumerate(positions[:5]):  # Show first 5
                profit_sign = "+" if pos.profit >= 0 else ""
                print(f'  [{i+1}] #{pos.ticket} {pos.symbol} {pos.type_name} {pos.volume} lots')
                print(f'      Price: {pos.price_open} -> {pos.price_current} | P&L: {profit_sign}${pos.profit:.2f}')
        
        # Check orders (Trade Tab)
        orders = mt5.orders_get()
        print(f'\n[TRADE TAB] Pending Orders: {len(orders) if orders else 0}')
        if orders:
            for i, order in enumerate(orders[:3]):  # Show first 3
                print(f'  [{i+1}] #{order.ticket} {order.symbol} {order.type_name} {order.volume_initial} lots at {order.price_open}')
        
        # Check for Expert files and activity
        print(f'\n[EXPERTS TAB] Expert Advisors:')
        if terminal_info and terminal_info.data_path:
            data_path = Path(terminal_info.data_path)
            experts_dir = data_path / 'MQL5' / 'Experts'
            if experts_dir.exists():
                expert_files = list(experts_dir.glob('*.ex5'))
                print(f'  Found {len(expert_files)} compiled EAs')
                for ea in expert_files[:5]:
                    print(f'    - {ea.name}')
        
        # Check recent log entries (Journal Tab)
        print(f'\n[JOURNAL TAB] Recent Activity:')
        if terminal_info and terminal_info.data_path:
            logs_dir = Path(terminal_info.data_path) / 'logs'
            if logs_dir.exists():
                today = datetime.now().strftime('%Y%m%d')
                log_file = logs_dir / f'{today}.log'
                if log_file.exists():
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            recent_lines = lines[-5:] if len(lines) > 5 else lines
                            for line in recent_lines:
                                if line.strip():
                                    print(f'  LOG: {line.strip()[:80]}')
                    except:
                        print('  [ERROR] Could not read log file')
        
        # Check for signal files
        print(f'\n[SIGNAL FILES] Recent Signals:')
        common_files = Path(terminal_info.commondata_path) / 'Files'
        if common_files.exists():
            signal_files = list(common_files.glob('*signal*.json'))
            print(f'  Found {len(signal_files)} signal files')
            for signal_file in signal_files:
                try:
                    with open(signal_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Clean up the content and try to parse
                        cleaned_content = content.replace(' ', '').replace('\n', '').replace('\r', '')
                        # Extract the JSON part
                        if '{' in cleaned_content and '}' in cleaned_content:
                            start = cleaned_content.find('{')
                            end = cleaned_content.rfind('}') + 1
                            json_part = cleaned_content[start:end]
                            try:
                                signal_data = json.loads(json_part)
                                print(f'    Signal: {signal_data.get("symbol", "N/A")} {signal_data.get("strategy", "N/A")}')
                                if 'timestamp' in signal_data:
                                    print(f'      Time: {signal_data["timestamp"]}')
                                if 'trade_direction' in signal_data:
                                    print(f'      Direction: {signal_data["trade_direction"]}')
                                if 'current_price' in signal_data:
                                    print(f'      Price: {signal_data["current_price"]}')
                                if 'phase_4_ylipip' in signal_data:
                                    ylipip = signal_data['phase_4_ylipip']
                                    print(f'      Ylipip Triggered: {ylipip.get("triggered", False)}')
                            except Exception as e:
                                print(f'    Raw content: {json_part[:100]}...')
                except Exception as e:
                    print(f'    [ERROR] Could not read {signal_file.name}: {e}')
        
        mt5.shutdown()
        print(f'\n[OK] Analysis complete at {datetime.now().strftime("%H:%M:%S")}')
    else:
        print('[ERROR] Failed to connect to MT5')

if __name__ == "__main__":
    main()