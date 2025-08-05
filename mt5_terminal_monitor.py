from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
MT5 Terminal Monitor - Advanced Toolbox State Analysis
Real-time monitoring of MT5 terminal interface and toolbox contents
"""

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
import winreg
from dataclasses import dataclass, asdict
import psutil
import win32gui
import win32process
import win32con

@dataclass
class ExpertInfo:
    """Expert Advisor information"""
    name: str
    status: str
    parameters: Dict[str, Any]
    last_update: datetime
    magic_number: Optional[int] = None
    chart_id: Optional[int] = None

@dataclass
class TerminalState:
    """Complete MT5 terminal state"""
    connection_status: str
    account_info: Dict[str, Any]
    experts: List[ExpertInfo]
    journal_entries: List[Dict[str, Any]]
    open_positions: List[Dict[str, Any]]
    orders: List[Dict[str, Any]]
    symbols_watched: List[str]
    last_update: datetime

class MT5TerminalMonitor:
    """Advanced MT5 Terminal State Monitor"""
    
    def __init__(self):
        self.terminal_state = None
        self.monitoring = False
        self.update_interval = 1.0  # seconds
        self.log_file = Path("mt5_terminal_monitor.log")
        self.experts_cache = []
        self.journal_cache = []
        self.mt5_process = None
        self.terminal_window = None
        
    def initialize(self) -> bool:
        """Initialize MT5 connection and monitoring"""
        print("ROCKET Initializing MT5 Terminal Monitor...")
        
        if not mt5.initialize():
            error = mt5.last_error()
            print(f"ERROR MT5 initialization failed: {error}")
            return False
            
        # Find MT5 process and window
        self._find_mt5_process()
        self._find_terminal_window()
        
        print("OK MT5 Terminal Monitor initialized successfully")
        return True
    
    def _find_mt5_process(self):
        """Find MT5 process information"""
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if 'terminal64.exe' in proc.info['name'].lower() or 'metatrader' in proc.info['name'].lower():
                    self.mt5_process = proc
                    print(f" Found MT5 process: PID {proc.info['pid']}")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def _find_terminal_window(self):
        """Find MT5 terminal window handle"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                if 'MetaTrader' in window_text or 'MT5' in window_text:
                    windows.append((hwnd, window_text, class_name))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            self.terminal_window = windows[0][0]
            print(f" Found MT5 window: {windows[0][1]}")
        else:
            print("WARNING  MT5 window not found")
    
    def get_terminal_info(self) -> Dict[str, Any]:
        """Get comprehensive MT5 terminal information"""
        terminal_info = mt5.terminal_info()
        if not terminal_info:
            return {}
            
        return {
            'company': terminal_info.company,
            'name': terminal_info.name,
            'language': terminal_info.language,
            'path': terminal_info.path,
            'data_path': terminal_info.data_path,
            'commondata_path': terminal_info.commondata_path,
            'build': terminal_info.build,
            'maxbars': terminal_info.maxbars,
            'cpu_cores': terminal_info.cpu_cores,
            'disk_space': terminal_info.disk_space,
            'physical_memory': terminal_info.physical_memory,
            'community_account': terminal_info.community_account,
            'community_connection': terminal_info.community_connection,
            'connected': terminal_info.connected,
            'dlls_allowed': terminal_info.dlls_allowed,
            'trade_allowed': terminal_info.trade_allowed,
            'tradeapi_disabled': terminal_info.tradeapi_disabled,
            'email_enabled': terminal_info.email_enabled,
            'ftp_enabled': terminal_info.ftp_enabled,
            'notifications_enabled': terminal_info.notifications_enabled,
            'mqid': terminal_info.mqid,
            'ping_last': terminal_info.ping_last,
            'community_balance': terminal_info.community_balance
        }
    
    def get_experts_status(self) -> List[ExpertInfo]:
        """Get status of running Expert Advisors"""
        experts = []
        
        # Get all open charts
        charts = []
        try:
            # This is a workaround since MT5 Python API doesn't directly expose chart list
            # We'll check for common symbols and see if they have charts
            symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD']
            
            for symbol in symbols:
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info and symbol_info.visible:
                    # Try to get chart-specific information
                    expert_info = ExpertInfo(
                        name=f"Expert on {symbol}",
                        status="Running" if symbol_info.visible else "Stopped",
                        parameters={
                            'symbol': symbol,
                            'spread': symbol_info.spread,
                            'digits': symbol_info.digits,
                            'trade_mode': symbol_info.trade_mode
                        },
                        last_update=datetime.now()
                    )
                    experts.append(expert_info)
        except Exception as e:
            print(f"WARNING  Error getting experts status: {e}")
        
        return experts
    
    def get_journal_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent journal entries"""
        journal_entries = []
        
        try:
            # Check for recent trades and orders as journal activity indicators
            positions = mt5.positions_get()
            if positions:
                for pos in positions:
                    entry = {
                        'timestamp': datetime.fromtimestamp(pos.time),
                        'type': 'Position',
                        'message': f"Position {pos.ticket}: {pos.symbol} {pos.type_name} {pos.volume} lots",
                        'symbol': pos.symbol,
                        'ticket': pos.ticket,
                        'profit': pos.profit
                    }
                    journal_entries.append(entry)
            
            # Get recent orders
            orders = mt5.orders_get()
            if orders:
                for order in orders:
                    entry = {
                        'timestamp': datetime.fromtimestamp(order.time_setup),
                        'type': 'Order',
                        'message': f"Order {order.ticket}: {order.symbol} {order.type_name} {order.volume_initial} lots",
                        'symbol': order.symbol,
                        'ticket': order.ticket,
                        'price': order.price_open
                    }
                    journal_entries.append(entry)
            
            # Sort by timestamp
            journal_entries.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            print(f"WARNING  Error getting journal entries: {e}")
        
        return journal_entries[:limit]
    
    def get_toolbox_state(self) -> Dict[str, Any]:
        """Get complete toolbox state information"""
        try:
            # Get positions (Trade tab)
            positions = mt5.positions_get()
            positions_data = []
            if positions:
                for pos in positions:
                    positions_data.append({
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': pos.type_name,
                        'volume': pos.volume,
                        'price_open': pos.price_open,
                        'price_current': pos.price_current,
                        'profit': pos.profit,
                        'time': datetime.fromtimestamp(pos.time),
                        'comment': pos.comment,
                        'magic': pos.magic
                    })
            
            # Get pending orders (Trade tab)
            orders = mt5.orders_get()
            orders_data = []
            if orders:
                for order in orders:
                    orders_data.append({
                        'ticket': order.ticket,
                        'symbol': order.symbol,
                        'type': order.type_name,
                        'volume': order.volume_initial,
                        'price_open': order.price_open,
                        'time_setup': datetime.fromtimestamp(order.time_setup),
                        'comment': order.comment,
                        'magic': order.magic
                    })
            
            # Get account history (Account History tab)
            history_orders = mt5.history_orders_get(
                datetime.now() - timedelta(days=1),
                datetime.now()
            )
            history_data = []
            if history_orders:
                for order in history_orders[-50:]:  # Last 50 orders
                    history_data.append({
                        'ticket': order.ticket,
                        'symbol': order.symbol,
                        'type': order.type_name,
                        'volume': order.volume_initial,
                        'price_open': order.price_open,
                        'time_setup': datetime.fromtimestamp(order.time_setup),
                        'time_done': datetime.fromtimestamp(order.time_done) if order.time_done else None,
                        'comment': order.comment,
                        'state': order.state_name
                    })
            
            return {
                'positions': positions_data,
                'orders': orders_data,
                'history': history_data,
                'experts': [asdict(expert) for expert in self.get_experts_status()],
                'journal': self.get_journal_entries(),
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"ERROR Error getting toolbox state: {e}")
            return {}
    
    def find_mt5_log_files(self) -> List[Path]:
        """Find MT5 log files in the system"""
        log_files = []
        
        # Get terminal info for paths
        terminal_info = mt5.terminal_info()
        if terminal_info:
            data_path = Path(terminal_info.data_path)
            
            # Common log file locations
            log_paths = [
                data_path / "Logs",
                data_path / "MQL5" / "Logs",
                data_path / "Terminal" / "Logs",
                Path.home() / "AppData" / "Roaming" / "MetaQuotes" / "Terminal" / "Common" / "Logs"
            ]
            
            for log_path in log_paths:
                if log_path.exists():
                    for log_file in log_path.glob("*.log"):
                        log_files.append(log_file)
                        print(f" Found log file: {log_file}")
        
        return log_files
    
    def read_recent_logs(self, lines: int = 50) -> List[str]:
        """Read recent entries from MT5 log files"""
        log_entries = []
        
        log_files = self.find_mt5_log_files()
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    file_lines = f.readlines()
                    recent_lines = file_lines[-lines:] if len(file_lines) > lines else file_lines
                    
                    for line in recent_lines:
                        if line.strip():
                            log_entries.append(f"[{log_file.name}] {line.strip()}")
                            
            except Exception as e:
                print(f"WARNING  Could not read {log_file}: {e}")
        
        return log_entries
    
    def get_mt5_registry_info(self) -> Dict[str, Any]:
        """Get MT5 configuration from Windows registry"""
        registry_info = {}
        
        try:
            # Common MT5 registry paths
            registry_paths = [
                r"SOFTWARE\MetaQuotes\Terminal",
                r"SOFTWARE\WOW6432Node\MetaQuotes\Terminal"
            ]
            
            for reg_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                        try:
                            value, regtype = winreg.QueryValueEx(key, "DataPath")
                            registry_info["data_path"] = value
                        except FileNotFoundError:
                            pass
                        
                        try:
                            value, regtype = winreg.QueryValueEx(key, "StartPath")
                            registry_info["start_path"] = value
                        except FileNotFoundError:
                            pass
                            
                except FileNotFoundError:
                    continue
                    
        except Exception as e:
            print(f"WARNING  Could not read registry: {e}")
        
        return registry_info
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.monitoring:
            print("WARNING  Monitoring already started")
            return
        
        self.monitoring = True
        
        def monitor_loop():
            print(" Starting real-time MT5 terminal monitoring...")
            
            while self.monitoring:
                try:
                    # Update terminal state
                    toolbox_state = self.get_toolbox_state()
                    terminal_info = self.get_terminal_info()
                    
                    current_state = TerminalState(
                        connection_status="Connected" if terminal_info.get('connected', False) else "Disconnected",
                        account_info=mt5.account_info()._asdict() if mt5.account_info() else {},
                        experts=self.get_experts_status(),
                        journal_entries=self.get_journal_entries(20),
                        open_positions=toolbox_state.get('positions', []),
                        orders=toolbox_state.get('orders', []),
                        symbols_watched=[],
                        last_update=datetime.now()
                    )
                    
                    self.terminal_state = current_state
                    
                    # Print status update
                    self._print_status_update(current_state)
                    
                    time.sleep(self.update_interval)
                    
                except Exception as e:
                    print(f"ERROR Monitoring error: {e}")
                    time.sleep(5)  # Wait longer on error
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        print("OK Real-time monitoring started")
    
    def _print_status_update(self, state: TerminalState):
        """Print formatted status update"""
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
        
        print("=" * 80)
        print("ROCKET MT5 TERMINAL MONITOR - REAL-TIME STATUS")
        print("=" * 80)
        print(f" Last Update: {state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Connection: {state.connection_status}")
        
        if state.account_info:
            acc = state.account_info
            print(f"MONEY Account: {acc.get('login')} | Balance: ${acc.get('balance', 0):,.2f} | Equity: ${acc.get('equity', 0):,.2f}")
        
        print(f"\nCHART TOOLBOX STATUS:")
        print(f"  GRAPH_UP Open Positions: {len(state.open_positions)}")
        print(f"   Pending Orders: {len(state.orders)}")
        print(f"   Active Experts: {len(state.experts)}")
        print(f"   Recent Journal: {len(state.journal_entries)} entries")
        
        # Show experts details
        if state.experts:
            print(f"\n EXPERTS (Asiantuntijat):")
            for expert in state.experts[:5]:  # Show first 5
                print(f"   {expert.name} - {expert.status}")
        
        # Show recent positions
        if state.open_positions:
            print(f"\nGRAPH_UP OPEN POSITIONS:")
            for pos in state.open_positions[:5]:  # Show first 5
                profit_sign = "+" if pos['profit'] >= 0 else ""
                print(f"   {pos['symbol']} {pos['type']} {pos['volume']} lots - {profit_sign}${pos['profit']:.2f}")
        
        # Show recent journal entries
        if state.journal_entries:
            print(f"\n JOURNAL (Lehti) - Recent Entries:")
            for entry in state.journal_entries[:3]:  # Show first 3
                print(f"   [{entry['timestamp'].strftime('%H:%M:%S')}] {entry['type']}: {entry['message']}")
        
        print(f"\n{'=' * 80}")
        print("Press Ctrl+C to stop monitoring")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        print(" Monitoring stopped")
    
    def get_current_state(self) -> Optional[TerminalState]:
        """Get current terminal state"""
        return self.terminal_state
    
    def export_state_to_json(self, filename: str = "mt5_terminal_state.json"):
        """Export current state to JSON file"""
        if not self.terminal_state:
            print("ERROR No state data available")
            return
        
        try:
            # Convert dataclass to dict
            state_dict = asdict(self.terminal_state)
            
            # Convert datetime objects to strings
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                return obj
            
            state_dict = convert_datetime(state_dict)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, indent=2, ensure_ascii=False)
                
            print(f"OK State exported to {filename}")
            
        except Exception as e:
            print(f"ERROR Export failed: {e}")
    
    def shutdown(self):
        """Shutdown monitor and MT5 connection"""
        self.stop_monitoring()
        mt5.shutdown()
        print("OK MT5 Terminal Monitor shutdown complete")

def main():
    """Main function"""
    monitor = MT5TerminalMonitor()
    
    if not monitor.initialize():
        print("ERROR Failed to initialize MT5 Terminal Monitor")
        return
    
    try:
        # Get initial state
        print("\nCHART Getting initial terminal state...")
        
        # Show terminal information
        terminal_info = monitor.get_terminal_info()
        print(f"\n  TERMINAL INFO:")
        print(f"  Company: {terminal_info.get('company', 'Unknown')}")
        print(f"  Build: {terminal_info.get('build', 'Unknown')}")
        print(f"  Data Path: {terminal_info.get('data_path', 'Unknown')}")
        print(f"  Connected: {terminal_info.get('connected', False)}")
        print(f"  Trade Allowed: {terminal_info.get('trade_allowed', False)}")
        print(f"  DLLs Allowed: {terminal_info.get('dlls_allowed', False)}")
        
        # Show toolbox state
        toolbox_state = monitor.get_toolbox_state()
        print(f"\n TOOLBOX STATE:")
        print(f"  Open Positions: {len(toolbox_state.get('positions', []))}")
        print(f"  Pending Orders: {len(toolbox_state.get('orders', []))}")
        print(f"  History Orders: {len(toolbox_state.get('history', []))}")
        
        # Show recent logs
        print(f"\n RECENT LOG ENTRIES:")
        recent_logs = monitor.read_recent_logs(10)
        for log_entry in recent_logs[-5:]:  # Show last 5
            print(f"  {log_entry}")
        
        # Start real-time monitoring
        print(f"\n Starting real-time monitoring...")
        monitor.start_monitoring()
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n Stopping monitor...")
            
    except Exception as e:
        print(f"ERROR Error: {e}")
    finally:
        monitor.shutdown()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()