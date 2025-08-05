#!/usr/bin/env python3
"""
MT5 TERMINAL DIRECT ACCESS - FINAL SOLUTION
Complete access to MT5 terminal logs, Expert Advisor status, and trading activity
NO win32gui dependency - Pure filesystem monitoring with real-time updates
SOLVES Unicode issues permanently with proper UTF-16LE handling
"""

import os
import sys
import time
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import MetaTrader5 as mt5

def ascii_print(text):
    """ASCII-only print to prevent Unicode issues permanently"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def read_mt5_log(file_path):
    """Read MT5 UTF-16LE log file and return clean ASCII lines"""
    try:
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        # Decode UTF-16LE properly
        try:
            decoded = raw_content.decode('utf-16le', errors='ignore')
        except:
            decoded = raw_content.decode('utf-8', errors='ignore')
        
        # Clean content: remove null bytes and keep only ASCII printable + tabs/newlines
        cleaned = decoded.replace('\x00', '')
        cleaned = re.sub(r'[^\x20-\x7E\n\r\t]', ' ', cleaned)
        
        # Split into lines and filter
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        return lines
        
    except Exception as e:
        ascii_print(f"Error reading {file_path}: {e}")
        return []

def parse_log_entry(line):
    """Parse MT5 log entry: ID TYPE TIME MESSAGE"""
    parts = line.split('\t')
    if len(parts) >= 4:
        return {
            'id': parts[0].strip(),
            'type': parts[1].strip(),
            'time': parts[2].strip(),
            'message': '\t'.join(parts[3:]).strip()
        }
    return None

class MT5TerminalDirectAccess:
    """Direct filesystem access to MT5 terminal - COMPLETE SOLUTION"""
    
    def __init__(self):
        self.data_path = None
        self.monitoring = False
        self.last_terminal_pos = 0
        self.last_expert_pos = 0
        
        # Setup ASCII stdout
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    
    def initialize(self) -> bool:
        """Initialize MT5 and get file paths"""
        ascii_print("=" * 70)
        ascii_print("MT5 TERMINAL DIRECT ACCESS - INITIALIZING")
        ascii_print("=" * 70)
        
        if not mt5.initialize():
            error = mt5.last_error()
            ascii_print(f"ERROR: MT5 connection failed: {error}")
            return False
        
        terminal_info = mt5.terminal_info()
        if not terminal_info:
            ascii_print("ERROR: Cannot get terminal info")
            return False
        
        self.data_path = Path(terminal_info.data_path)
        
        ascii_print("SUCCESS: MT5 Direct Access initialized")
        ascii_print(f"Terminal Path: {self.data_path}")
        ascii_print(f"Terminal Logs: {self.data_path / 'logs'}")
        ascii_print(f"Expert Logs: {self.data_path / 'MQL5' / 'Logs'}")
        ascii_print(f"Signal Files: {self.data_path / 'MQL5' / 'Files'}")
        
        return True
    
    def get_current_log_files(self):
        """Get today's log file paths"""
        today = datetime.now().strftime('%Y%m%d')
        return {
            'terminal': self.data_path / 'logs' / f'{today}.log',
            'expert': self.data_path / 'MQL5' / 'Logs' / f'{today}.log'
        }
    
    def read_terminal_activity(self, recent_lines=20):
        """Read recent terminal log activity"""
        log_files = self.get_current_log_files()
        terminal_log = log_files['terminal']
        
        if not terminal_log.exists():
            return []
        
        lines = read_mt5_log(terminal_log)
        activities = []
        
        for line in lines[-recent_lines:]:
            entry = parse_log_entry(line)
            if entry:
                activities.append({
                    'time': entry['time'][:8],  # HH:MM:SS
                    'type': entry['type'],
                    'message': entry['message'],
                    'source': 'terminal'
                })
        
        return activities
    
    def read_expert_activity(self, recent_lines=30):
        """Read recent Expert Advisor activity"""
        log_files = self.get_current_log_files()
        expert_log = log_files['expert']
        
        if not expert_log.exists():
            return []
        
        lines = read_mt5_log(expert_log)
        activities = []
        
        for line in lines[-recent_lines:]:
            entry = parse_log_entry(line)
            if entry and len(entry['message'].split('\t')) >= 2:
                # Expert format: EA_NAME MESSAGE
                message_parts = entry['message'].split('\t', 1)
                ea_name = message_parts[0].strip()
                message = message_parts[1].strip() if len(message_parts) > 1 else message_parts[0]
                
                # Extract symbol from EA name if present
                symbol = 'Unknown'
                if '(' in ea_name and ')' in ea_name:
                    symbol_part = ea_name.split('(')[1].split(',')[0].split(')')[0]
                    symbol = symbol_part if symbol_part else 'Unknown'
                
                # Categorize activity
                activity_type = 'general'
                if 'BOS' in message.upper():
                    activity_type = 'bos_detection'
                elif 'YLIPIP' in message.upper():
                    activity_type = 'ylipip_trigger'
                elif 'PHASE' in message.upper():
                    activity_type = 'phase_complete'
                elif 'SIGNAL' in message.upper():
                    activity_type = 'signal_sent'
                elif 'TRADE' in message.upper() or 'EXECUTING' in message.upper():
                    activity_type = 'trade_execution'
                
                activities.append({
                    'time': entry['time'][:8],
                    'ea_name': ea_name.split('(')[0].strip(),
                    'symbol': symbol,
                    'message': message,
                    'activity_type': activity_type,
                    'source': 'expert'
                })
        
        return activities
    
    def read_signal_files(self):
        """Read all signal files"""
        signal_dir = self.data_path / 'MQL5' / 'Files'
        if not signal_dir.exists():
            return []
        
        signals = []
        for signal_file in signal_dir.glob('*signal*.json'):
            try:
                with open(signal_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().replace('\x00', '').replace('\ufeff', '')
                
                # Extract JSON
                if '{' in content and '}' in content:
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    json_part = content[start:end]
                    
                    try:
                        signal_data = json.loads(json_part)
                        signal_data['file_name'] = signal_file.name
                        signal_data['file_time'] = datetime.fromtimestamp(
                            signal_file.stat().st_mtime
                        ).strftime('%H:%M:%S')
                        signals.append(signal_data)
                    except json.JSONDecodeError:
                        signals.append({
                            'file_name': signal_file.name,
                            'error': 'JSON parse failed',
                            'content_preview': json_part[:100]
                        })
                        
            except Exception as e:
                ascii_print(f"Error reading {signal_file.name}: {e}")
        
        return signals
    
    def get_mt5_live_data(self):
        """Get live MT5 data via API"""
        try:
            # Account info
            account_info = mt5.account_info()
            account_data = {}
            if account_info:
                account_data = {
                    'login': account_info.login,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'margin_free': account_info.margin_free,
                    'profit': account_info.profit
                }
            
            # Positions
            positions = mt5.positions_get()
            positions_data = []
            if positions:
                for pos in positions:
                    positions_data.append({
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': pos.type,
                        'volume': pos.volume,
                        'price_open': pos.price_open,
                        'price_current': pos.price_current,
                        'profit': pos.profit,
                        'comment': pos.comment,
                        'magic': pos.magic
                    })
            
            # Orders
            orders = mt5.orders_get()
            orders_data = []
            if orders:
                for order in orders:
                    orders_data.append({
                        'ticket': order.ticket,
                        'symbol': order.symbol,
                        'type': order.type,
                        'volume': order.volume_initial,
                        'price_open': order.price_open,
                        'comment': order.comment,
                        'magic': order.magic
                    })
            
            return {
                'account': account_data,
                'positions': positions_data,
                'orders': orders_data
            }
            
        except Exception as e:
            ascii_print(f"Error getting MT5 live data: {e}")
            return {'account': {}, 'positions': [], 'orders': []}
    
    def get_complete_status(self):
        """Get complete terminal status"""
        terminal_activity = self.read_terminal_activity(15)
        expert_activity = self.read_expert_activity(25)
        signal_files = self.read_signal_files()
        live_data = self.get_mt5_live_data()
        
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'terminal_activity': terminal_activity,
            'expert_activity': expert_activity,
            'signal_files': signal_files,
            'account': live_data['account'],
            'positions': live_data['positions'],
            'orders': live_data['orders']
        }
    
    def display_status(self, status):
        """Display formatted terminal status"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        ascii_print("=" * 70)
        ascii_print("MT5 TERMINAL DIRECT ACCESS - LIVE STATUS")
        ascii_print("=" * 70)
        ascii_print(f"Last Update: {status['timestamp']}")
        
        # Account Summary
        account = status['account']
        if account:
            ascii_print(f"Account {account.get('login', 'N/A')}: Balance=${account.get('balance', 0):,.2f} | Equity=${account.get('equity', 0):,.2f} | P&L=${account.get('profit', 0):,.2f}")
        
        # Trading Summary
        positions = status['positions']
        orders = status['orders']
        ascii_print(f"Open Positions: {len(positions)} | Pending Orders: {len(orders)}")
        
        # Show positions
        if positions:
            ascii_print("\nOPEN POSITIONS:")
            for i, pos in enumerate(positions[:5]):
                profit_sign = "+" if pos['profit'] >= 0 else ""
                ascii_print(f"  {i+1}. #{pos['ticket']} {pos['symbol']} Type:{pos['type']} {pos['volume']} lots | P&L: {profit_sign}${pos['profit']:.2f}")
        
        # Expert Activity (Most Important)
        expert_activity = status['expert_activity']
        if expert_activity:
            ascii_print("\nEXPERT ADVISOR ACTIVITY:")
            for activity in expert_activity[-8:]:  # Last 8 activities
                ea_name = activity['ea_name'][:20]  # Truncate EA name
                symbol = activity['symbol'][:10]
                message = activity['message'][:50]  # Truncate message
                time_str = activity['time']
                
                # Add activity type indicator
                type_indicator = ""
                if activity['activity_type'] == 'bos_detection':
                    type_indicator = "[BOS]"
                elif activity['activity_type'] == 'ylipip_trigger':
                    type_indicator = "[YLIPIP]"
                elif activity['activity_type'] == 'phase_complete':
                    type_indicator = "[PHASE]"
                elif activity['activity_type'] == 'signal_sent':
                    type_indicator = "[SIGNAL]"
                elif activity['activity_type'] == 'trade_execution':
                    type_indicator = "[TRADE]"
                
                ascii_print(f"  [{time_str}] {type_indicator} {ea_name} ({symbol}): {message}")
        
        # Terminal Activity
        terminal_activity = status['terminal_activity']
        if terminal_activity:
            ascii_print("\nTERMINAL ACTIVITY:")
            for activity in terminal_activity[-4:]:  # Last 4 activities
                time_str = activity['time']
                message = activity['message'][:60]
                ascii_print(f"  [{time_str}] {message}")
        
        # Signal Files
        signal_files = status['signal_files']
        if signal_files:
            ascii_print(f"\nSIGNAL FILES: {len(signal_files)} files")
            for signal in signal_files[:3]:  # Show first 3
                if 'error' not in signal:
                    symbol = signal.get('symbol', 'N/A')
                    action = signal.get('action', signal.get('trade_direction', 'N/A'))
                    strategy = signal.get('strategy', 'N/A')[:20]
                    file_time = signal.get('file_time', 'N/A')
                    ascii_print(f"  [{file_time}] {signal['file_name']}: {symbol} {action} ({strategy})")
        
        ascii_print("=" * 70)
        ascii_print("Press Ctrl+C to stop monitoring")
    
    def start_realtime_monitoring(self, update_interval=3.0):
        """Start real-time monitoring"""
        ascii_print("Starting real-time MT5 terminal monitoring...")
        ascii_print(f"Update interval: {update_interval} seconds")
        
        try:
            while True:
                # Get complete status
                status = self.get_complete_status()
                
                # Display status
                self.display_status(status)
                
                # Wait for next update
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            ascii_print("\nStopping monitoring...")
        except Exception as e:
            ascii_print(f"Monitoring error: {e}")
    
    def export_status(self, filename=None):
        """Export current status to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"mt5_terminal_status_{timestamp}.json"
        
        try:
            status = self.get_complete_status()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=True)
            
            ascii_print(f"Status exported to: {filename}")
            return filename
            
        except Exception as e:
            ascii_print(f"Export failed: {e}")
            return None
    
    def shutdown(self):
        """Shutdown"""
        mt5.shutdown()
        ascii_print("MT5 Terminal Direct Access shutdown complete")

def main():
    """Main function"""
    monitor = MT5TerminalDirectAccess()
    
    if not monitor.initialize():
        ascii_print("FAILED to initialize MT5 Terminal Direct Access")
        return
    
    try:
        # Show initial status
        ascii_print("\nReading initial terminal status...")
        initial_status = monitor.get_complete_status()
        
        ascii_print(f"\n=== INITIAL STATUS ===")
        ascii_print(f"Terminal Activities: {len(initial_status['terminal_activity'])}")
        ascii_print(f"Expert Activities: {len(initial_status['expert_activity'])}")
        ascii_print(f"Open Positions: {len(initial_status['positions'])}")
        ascii_print(f"Signal Files: {len(initial_status['signal_files'])}")
        
        # Export initial status
        export_file = monitor.export_status()
        
        # Show some recent expert activity
        expert_activity = initial_status['expert_activity']
        if expert_activity:
            ascii_print(f"\nRecent Expert Activity (last 5):")
            for activity in expert_activity[-5:]:
                ascii_print(f"  [{activity['time']}] {activity['ea_name']} ({activity['symbol']}): {activity['message'][:50]}")
        
        ascii_print(f"\nStarting real-time monitoring in 3 seconds...")
        time.sleep(3)
        
        # Start real-time monitoring
        monitor.start_realtime_monitoring(update_interval=3.0)
        
    except Exception as e:
        ascii_print(f"Error: {e}")
    finally:
        monitor.shutdown()

if __name__ == "__main__":
    main()