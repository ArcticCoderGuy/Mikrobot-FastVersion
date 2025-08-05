#!/usr/bin/env python3
"""
MT5 Direct Filesystem Monitor - DIRECT ACCESS TO TERMINAL LOGS
NO win32gui dependency - Pure filesystem monitoring with ASCII-only output
Real-time access to MT5 terminal logs, Expert Advisor status, and trading activity
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
from dataclasses import dataclass, asdict
import MetaTrader5 as mt5

# ASCII-only encoding setup
def ascii_print(text):
    """Ensure ASCII-only output to prevent Unicode issues permanently"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def read_utf16_log(file_path: Path) -> List[str]:
    """Read UTF-16LE encoded MT5 log files and return ASCII-only lines"""
    lines = []
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Decode UTF-16LE and clean up
        content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
        # Remove all non-ASCII characters
        content_str = re.sub(r'[^\x20-\x7E\n\r]', '', content_str)
        
        # Split into lines and clean
        for line in content_str.split('\n'):
            clean_line = line.strip()
            if clean_line:
                lines.append(clean_line)
                
    except Exception as e:
        ascii_print(f"Error reading log file {file_path}: {e}")
    
    return lines

@dataclass
class MT5FilePaths:
    """MT5 file paths container"""
    data_path: str
    common_path: str
    terminal_logs: str
    expert_logs: str
    signal_files: str
    
class MT5DirectMonitor:
    """Direct filesystem-based MT5 terminal monitor - NO external dependencies"""
    
    def __init__(self):
        self.monitoring = False
        self.paths = None
        self.last_terminal_log_size = 0
        self.last_expert_log_size = 0
        self.expert_states = {}
        self.trading_activity = []
        self.monitoring_thread = None
        
        # Setup ASCII-only stdout
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    
    def initialize(self) -> bool:
        """Initialize MT5 connection and find file paths"""
        ascii_print("=== MT5 DIRECT FILESYSTEM MONITOR ===")
        ascii_print("Initializing MT5 connection...")
        
        if not mt5.initialize():
            error = mt5.last_error()
            ascii_print(f"ERROR: MT5 initialization failed: {error}")
            return False
        
        # Get terminal paths
        terminal_info = mt5.terminal_info()
        if not terminal_info:
            ascii_print("ERROR: Could not get terminal info")
            return False
        
        # Setup file paths
        data_path = Path(terminal_info.data_path)
        common_path = Path(terminal_info.commondata_path)
        
        self.paths = MT5FilePaths(
            data_path=str(data_path),
            common_path=str(common_path),
            terminal_logs=str(data_path / 'logs'),
            expert_logs=str(data_path / 'MQL5' / 'Logs'),
            signal_files=str(data_path / 'MQL5' / 'Files')
        )
        
        ascii_print("SUCCESS: MT5 Direct Monitor initialized")
        ascii_print(f"Data Path: {self.paths.data_path}")
        ascii_print(f"Terminal Logs: {self.paths.terminal_logs}")
        ascii_print(f"Expert Logs: {self.paths.expert_logs}")
        ascii_print(f"Signal Files: {self.paths.signal_files}")
        
        return True
    
    def get_latest_log_files(self) -> Dict[str, Path]:
        """Get today's log files"""
        today = datetime.now().strftime('%Y%m%d')
        
        terminal_log = Path(self.paths.terminal_logs) / f"{today}.log"
        expert_log = Path(self.paths.expert_logs) / f"{today}.log"
        
        return {
            'terminal': terminal_log if terminal_log.exists() else None,
            'expert': expert_log if expert_log.exists() else None
        }
    
    def read_recent_terminal_activity(self, lines: int = 50) -> List[Dict[str, Any]]:
        """Read recent terminal log activity"""
        log_files = self.get_latest_log_files()
        terminal_log = log_files['terminal']
        
        if not terminal_log or not terminal_log.exists():
            return []
        
        try:
            log_lines = read_utf16_log(terminal_log)
            recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
            
            activities = []
            for line in recent_lines:
                if not line.strip():
                    continue
                
                # Parse log line format: ID TYPE TIME MESSAGE
                parts = line.split('\t')
                if len(parts) >= 4:
                    entry = {
                        'id': parts[0].strip(),
                        'type': parts[1].strip(),
                        'time': parts[2].strip(),
                        'message': parts[3].strip(),
                        'timestamp': datetime.now().isoformat(),
                        'source': 'terminal'
                    }
                    activities.append(entry)
            
            return activities
            
        except Exception as e:
            ascii_print(f"Error reading terminal activity: {e}")
            return []
    
    def read_recent_expert_activity(self, lines: int = 100) -> List[Dict[str, Any]]:
        """Read recent Expert Advisor activity"""
        log_files = self.get_latest_log_files()
        expert_log = log_files['expert']
        
        if not expert_log or not expert_log.exists():
            return []
        
        try:
            log_lines = read_utf16_log(expert_log)
            recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
            
            activities = []
            for line in recent_lines:
                if not line.strip():
                    continue
                
                # Parse expert log line format: ID TYPE TIME EA_NAME MESSAGE
                parts = line.split('\t')
                if len(parts) >= 5:
                    ea_name = parts[3].strip()
                    message = parts[4].strip()
                    
                    entry = {
                        'id': parts[0].strip(),
                        'type': parts[1].strip(),
                        'time': parts[2].strip(),
                        'ea_name': ea_name,
                        'message': message,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'expert'
                    }
                    
                    # Extract key information
                    if 'BOS' in message.upper():
                        entry['activity_type'] = 'BOS_DETECTION'
                    elif 'YLIPIP' in message.upper():
                        entry['activity_type'] = 'YLIPIP_TRIGGER'
                    elif 'PHASE' in message.upper():
                        entry['activity_type'] = 'PHASE_COMPLETE'
                    elif 'SIGNAL' in message.upper():
                        entry['activity_type'] = 'SIGNAL_SENT'
                    elif 'TRADE' in message.upper():
                        entry['activity_type'] = 'TRADE_EXECUTION'
                    else:
                        entry['activity_type'] = 'GENERAL'
                    
                    activities.append(entry)
            
            return activities
            
        except Exception as e:
            ascii_print(f"Error reading expert activity: {e}")
            return []
    
    def read_signal_files(self) -> List[Dict[str, Any]]:
        """Read all signal files"""
        signal_dir = Path(self.paths.signal_files)
        if not signal_dir.exists():
            return []
        
        signals = []
        for signal_file in signal_dir.glob('*signal*.json'):
            try:
                with open(signal_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Clean up the content for JSON parsing
                cleaned_content = content.replace('\x00', '').replace('\ufeff', '')
                
                # Try to extract JSON
                if '{' in cleaned_content and '}' in cleaned_content:
                    start = cleaned_content.find('{')
                    end = cleaned_content.rfind('}') + 1
                    json_part = cleaned_content[start:end]
                    
                    try:
                        signal_data = json.loads(json_part)
                        signal_data['file_name'] = signal_file.name
                        signal_data['file_modified'] = datetime.fromtimestamp(
                            signal_file.stat().st_mtime
                        ).isoformat()
                        signals.append(signal_data)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, create basic entry
                        signals.append({
                            'file_name': signal_file.name,
                            'content': json_part[:200] + '...' if len(json_part) > 200 else json_part,
                            'file_modified': datetime.fromtimestamp(
                                signal_file.stat().st_mtime
                            ).isoformat(),
                            'parse_error': True
                        })
                        
            except Exception as e:
                ascii_print(f"Error reading signal file {signal_file.name}: {e}")
        
        return signals
    
    def get_mt5_positions_and_orders(self) -> Dict[str, Any]:
        """Get current MT5 positions and orders via API"""
        try:
            # Get positions
            positions = mt5.positions_get()
            positions_data = []
            if positions:
                for pos in positions:
                    pos_data = {
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': pos.type,  # Use pos.type instead of pos.type_name
                        'volume': pos.volume,
                        'price_open': pos.price_open,
                        'price_current': pos.price_current,
                        'profit': pos.profit,
                        'time': datetime.fromtimestamp(pos.time).isoformat(),
                        'comment': pos.comment,
                        'magic': pos.magic
                    }
                    positions_data.append(pos_data)
            
            # Get orders
            orders = mt5.orders_get()
            orders_data = []
            if orders:
                for order in orders:
                    order_data = {
                        'ticket': order.ticket,
                        'symbol': order.symbol,
                        'type': order.type,
                        'volume': order.volume_initial,
                        'price_open': order.price_open,
                        'time_setup': datetime.fromtimestamp(order.time_setup).isoformat(),
                        'comment': order.comment,
                        'magic': order.magic
                    }
                    orders_data.append(order_data)
            
            # Get account info
            account_info = mt5.account_info()
            account_data = {}
            if account_info:
                account_data = {
                    'login': account_info.login,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'margin_free': account_info.margin_free,
                    'margin_used': account_info.margin,
                    'profit': account_info.profit
                }
            
            return {
                'positions': positions_data,
                'orders': orders_data,
                'account': account_data
            }
            
        except Exception as e:
            ascii_print(f"Error getting MT5 data: {e}")
            return {'positions': [], 'orders': [], 'account': {}}
    
    def get_complete_terminal_state(self) -> Dict[str, Any]:
        """Get complete terminal state from all sources"""
        terminal_activity = self.read_recent_terminal_activity(20)
        expert_activity = self.read_recent_expert_activity(50)
        signal_files = self.read_signal_files()
        mt5_data = self.get_mt5_positions_and_orders()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'terminal_activity': terminal_activity,
            'expert_activity': expert_activity,
            'signal_files': signal_files,
            'positions': mt5_data['positions'],
            'orders': mt5_data['orders'],
            'account': mt5_data['account'],
            'monitoring_status': 'active' if self.monitoring else 'stopped'
        }
    
    def print_terminal_status(self, state: Dict[str, Any]):
        """Print formatted terminal status"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        ascii_print("=" * 80)
        ascii_print("MT5 DIRECT FILESYSTEM MONITOR - REAL-TIME STATUS")
        ascii_print("=" * 80)
        ascii_print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Account info
        account = state.get('account', {})
        if account:
            ascii_print(f"Account {account.get('login', 'N/A')}: Balance=${account.get('balance', 0):,.2f} | Equity=${account.get('equity', 0):,.2f}")
        
        # Positions and orders
        positions = state.get('positions', [])
        orders = state.get('orders', [])
        ascii_print(f"Open Positions: {len(positions)} | Pending Orders: {len(orders)}")
        
        # Show recent positions
        if positions:
            ascii_print("\nOPEN POSITIONS:")
            for i, pos in enumerate(positions[:5]):
                profit_sign = "+" if pos['profit'] >= 0 else ""
                ascii_print(f"  {i+1}. #{pos['ticket']} {pos['symbol']} Type:{pos['type']} {pos['volume']} lots - {profit_sign}${pos['profit']:.2f}")
        
        # Recent Expert Activity
        expert_activity = state.get('expert_activity', [])
        if expert_activity:
            ascii_print("\nEXPERT ADVISOR ACTIVITY (Recent):")
            for activity in expert_activity[-5:]:  # Last 5
                time_str = activity.get('time', '')[:8]  # HH:MM:SS
                ea_name = activity.get('ea_name', '').split('(')[0]  # EA name without symbol
                message = activity.get('message', '')[:60]  # Truncate message
                ascii_print(f"  [{time_str}] {ea_name}: {message}")
        
        # Recent Terminal Activity
        terminal_activity = state.get('terminal_activity', [])
        if terminal_activity:
            ascii_print("\nTERMINAL ACTIVITY (Recent):")
            for activity in terminal_activity[-3:]:  # Last 3
                time_str = activity.get('time', '')[:8]
                message = activity.get('message', '')[:70]
                ascii_print(f"  [{time_str}] {message}")
        
        # Signal Files
        signal_files = state.get('signal_files', [])
        if signal_files:
            ascii_print(f"\nSIGNAL FILES: {len(signal_files)} files")
            for signal in signal_files[:3]:  # Show first 3
                if not signal.get('parse_error', False):
                    symbol = signal.get('symbol', 'N/A')
                    direction = signal.get('trade_direction', 'N/A')
                    strategy = signal.get('strategy', 'N/A')
                    ascii_print(f"  {signal['file_name']}: {symbol} {direction} ({strategy})")
        
        ascii_print("=" * 80)
        ascii_print("Press Ctrl+C to stop monitoring")
    
    def start_monitoring(self, update_interval: float = 2.0):
        """Start real-time monitoring"""
        if self.monitoring:
            ascii_print("WARNING: Monitoring already started")
            return
        
        self.monitoring = True
        
        def monitor_loop():
            ascii_print("Starting real-time MT5 filesystem monitoring...")
            
            while self.monitoring:
                try:
                    # Get complete terminal state
                    state = self.get_complete_terminal_state()
                    
                    # Print status
                    self.print_terminal_status(state)
                    
                    # Wait for next update
                    time.sleep(update_interval)
                    
                except KeyboardInterrupt:
                    ascii_print("\nStopping monitor...")
                    break
                except Exception as e:
                    ascii_print(f"Monitoring error: {e}")
                    time.sleep(5)  # Wait longer on error
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
        
        ascii_print("Real-time monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
        ascii_print("Monitoring stopped")
    
    def export_state_to_file(self, filename: str = None):
        """Export current state to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"mt5_terminal_state_{timestamp}.json"
        
        try:
            state = self.get_complete_terminal_state()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=True)
            
            ascii_print(f"Terminal state exported to {filename}")
            return filename
            
        except Exception as e:
            ascii_print(f"Export failed: {e}")
            return None
    
    def shutdown(self):
        """Shutdown monitor"""
        self.stop_monitoring()
        mt5.shutdown()
        ascii_print("MT5 Direct Monitor shutdown complete")

def main():
    """Main function"""
    monitor = MT5DirectMonitor()
    
    if not monitor.initialize():
        ascii_print("FAILED to initialize MT5 Direct Monitor")
        return
    
    try:
        # Show initial state
        ascii_print("\nGetting initial terminal state...")
        initial_state = monitor.get_complete_terminal_state()
        
        ascii_print("\n=== INITIAL TERMINAL STATE ===")
        ascii_print(f"Expert Activities: {len(initial_state.get('expert_activity', []))}")
        ascii_print(f"Terminal Activities: {len(initial_state.get('terminal_activity', []))}")
        ascii_print(f"Open Positions: {len(initial_state.get('positions', []))}")
        ascii_print(f"Pending Orders: {len(initial_state.get('orders', []))}")
        ascii_print(f"Signal Files: {len(initial_state.get('signal_files', []))}")
        
        # Export initial state
        export_file = monitor.export_state_to_file()
        ascii_print(f"Initial state exported to: {export_file}")
        
        # Start real-time monitoring
        ascii_print("\nStarting real-time monitoring (2 second updates)...")
        monitor.start_monitoring(update_interval=2.0)
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            ascii_print("\nShutting down...")
            
    except Exception as e:
        ascii_print(f"Error: {e}")
    finally:
        monitor.shutdown()

if __name__ == "__main__":
    main()