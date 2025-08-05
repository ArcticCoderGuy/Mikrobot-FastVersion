from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
MT5 Toolbox Simple Monitor
Simplified real-time monitoring of MT5 Toolbox without Windows GUI dependencies
"""

import MetaTrader5 as mt5
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from pathlib import Path

class MT5SimpleMonitor:
    """Simplified MT5 Terminal Monitor"""
    
    def __init__(self):
        self.monitoring = False
        self.update_interval = 2.0  # 2 second updates
        self.last_positions = []
        self.last_orders = []
        self.journal_entries = []
        
    def initialize_mt5(self) -> bool:
        """Initialize MT5 connection"""
        try:
            if not mt5.initialize():
                error = mt5.last_error()
                print(f"ERROR MT5 initialization failed: {error}")
                return False
            
            print("OK MT5 connection established")
            return True
            
        except Exception as e:
            print(f"ERROR MT5 initialization error: {e}")
            return False
    
    def get_terminal_info(self) -> Dict[str, Any]:
        """Get MT5 terminal information"""
        try:
            terminal_info = mt5.terminal_info()
            if not terminal_info:
                return {}
            
            return {
                'company': terminal_info.company,
                'name': terminal_info.name,
                'path': terminal_info.path,
                'data_path': terminal_info.data_path,
                'build': terminal_info.build,
                'connected': terminal_info.connected,
                'dlls_allowed': terminal_info.dlls_allowed,
                'trade_allowed': terminal_info.trade_allowed,
                'email_enabled': terminal_info.email_enabled,
                'notifications_enabled': terminal_info.notifications_enabled,
                'ping_last': terminal_info.ping_last,
                'community_balance': terminal_info.community_balance
            }
        except Exception as e:
            print(f"WARNING  Error getting terminal info: {e}")
            return {}
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                return {}
            
            return {
                'login': account_info.login,
                'server': account_info.server,
                'name': account_info.name,
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'margin_free': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'leverage': account_info.leverage,
                'currency': account_info.currency,
                'company': account_info.company,
                'trade_allowed': account_info.trade_allowed
            }
        except Exception as e:
            print(f"WARNING  Error getting account info: {e}")
            return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get open positions"""
        try:
            positions = mt5.positions_get()
            if not positions:
                return []
            
            position_list = []
            for pos in positions:
                position_info = {
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': pos.type_name,
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'commission': pos.commission,
                    'time': datetime.fromtimestamp(pos.time),
                    'comment': pos.comment,
                    'magic': pos.magic,
                    'identifier': pos.identifier
                }
                position_list.append(position_info)
            
            return position_list
            
        except Exception as e:
            print(f"WARNING  Error getting positions: {e}")
            return []
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get pending orders"""
        try:
            orders = mt5.orders_get()
            if not orders:
                return []
            
            order_list = []
            for order in orders:
                order_info = {
                    'ticket': order.ticket,
                    'symbol': order.symbol,
                    'type': order.type_name,
                    'volume': order.volume_initial,
                    'price_open': order.price_open,
                    'sl': order.sl,
                    'tp': order.tp,
                    'time_setup': datetime.fromtimestamp(order.time_setup),
                    'comment': order.comment,
                    'magic': order.magic
                }
                order_list.append(order_info)
            
            return order_list
            
        except Exception as e:
            print(f"WARNING  Error getting orders: {e}")
            return []
    
    def get_history_orders(self, days: int = 1) -> List[Dict[str, Any]]:
        """Get recent history orders"""
        try:
            start_time = datetime.now() - timedelta(days=days)
            end_time = datetime.now()
            
            history_orders = mt5.history_orders_get(start_time, end_time)
            if not history_orders:
                return []
            
            history_list = []
            for order in history_orders[-20:]:  # Last 20 orders
                order_info = {
                    'ticket': order.ticket,
                    'symbol': order.symbol,
                    'type': order.type_name,
                    'volume': order.volume_initial,
                    'price_open': order.price_open,
                    'time_setup': datetime.fromtimestamp(order.time_setup),
                    'time_done': datetime.fromtimestamp(order.time_done) if order.time_done else None,
                    'comment': order.comment,
                    'state': order.state_name,
                    'magic': order.magic
                }
                history_list.append(order_info)
            
            return history_list
            
        except Exception as e:
            print(f"WARNING  Error getting history orders: {e}")
            return []
    
    def detect_experts(self, positions: List[Dict], orders: List[Dict]) -> List[Dict[str, Any]]:
        """Detect running Expert Advisors based on magic numbers and symbols"""
        experts = {}
        
        # Group by magic number and symbol
        for pos in positions:
            magic = pos['magic']
            symbol = pos['symbol']
            key = f"{symbol}_{magic}"
            
            if key not in experts:
                experts[key] = {
                    'name': f"Expert_{symbol}_{magic}" if magic != 0 else f"Manual_{symbol}",
                    'symbol': symbol,
                    'magic': magic,
                    'status': 'Running',
                    'positions': [],
                    'orders': [],
                    'total_profit': 0,
                    'total_volume': 0
                }
            
            experts[key]['positions'].append(pos)
            experts[key]['total_profit'] += pos['profit']
            experts[key]['total_volume'] += pos['volume']
        
        for order in orders:
            magic = order['magic']
            symbol = order['symbol']
            key = f"{symbol}_{magic}"
            
            if key not in experts:
                experts[key] = {
                    'name': f"Expert_{symbol}_{magic}" if magic != 0 else f"Manual_{symbol}",
                    'symbol': symbol,
                    'magic': magic,
                    'status': 'Running',
                    'positions': [],
                    'orders': [],
                    'total_profit': 0,
                    'total_volume': 0
                }
            
            experts[key]['orders'].append(order)
            experts[key]['total_volume'] += order['volume']
        
        return list(experts.values())
    
    def generate_journal_entries(self, positions: List[Dict], orders: List[Dict]) -> List[Dict[str, Any]]:
        """Generate journal entries based on changes"""
        entries = []
        current_time = datetime.now()
        
        # Compare with previous positions
        current_tickets = {pos['ticket'] for pos in positions}
        previous_tickets = {pos['ticket'] for pos in self.last_positions}
        
        # New positions
        new_positions = current_tickets - previous_tickets
        for pos in positions:
            if pos['ticket'] in new_positions:
                entry = {
                    'timestamp': current_time,
                    'level': 'INFO',
                    'source': 'Trade',
                    'message': f"Position opened: #{pos['ticket']} {pos['symbol']} {pos['type']} {pos['volume']} lots at {pos['price_open']}"
                }
                entries.append(entry)
        
        # Closed positions
        closed_positions = previous_tickets - current_tickets
        if closed_positions:
            entry = {
                'timestamp': current_time,
                'level': 'INFO',
                'source': 'Trade',
                'message': f"{len(closed_positions)} position(s) closed"
            }
            entries.append(entry)
        
        # Compare with previous orders
        current_order_tickets = {order['ticket'] for order in orders}
        previous_order_tickets = {order['ticket'] for order in self.last_orders}
        
        # New orders
        new_orders = current_order_tickets - previous_order_tickets
        for order in orders:
            if order['ticket'] in new_orders:
                entry = {
                    'timestamp': current_time,
                    'level': 'INFO',
                    'source': 'Trade',
                    'message': f"Order placed: #{order['ticket']} {order['symbol']} {order['type']} {order['volume']} lots at {order['price_open']}"
                }
                entries.append(entry)
        
        # Update last states
        self.last_positions = positions.copy()
        self.last_orders = orders.copy()
        
        return entries
    
    def read_recent_log_entries(self, lines: int = 5) -> List[str]:
        """Read recent entries from today's log file"""
        try:
            terminal_info = self.get_terminal_info()
            if not terminal_info.get('data_path'):
                return []
            
            data_path = Path(terminal_info['data_path'])
            logs_dir = data_path / 'logs'
            
            if not logs_dir.exists():
                return []
            
            # Get today's log file
            today = datetime.now().strftime('%Y%m%d')
            log_file = logs_dir / f"{today}.log"
            
            if not log_file.exists():
                # Try to find the most recent log file
                log_files = list(logs_dir.glob('*.log'))
                if not log_files:
                    return []
                log_file = max(log_files, key=lambda x: x.stat().st_mtime)
            
            # Read recent lines
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                # Clean and filter lines
                cleaned_lines = []
                for line in recent_lines:
                    line = line.strip()
                    if line and len(line) > 10:  # Filter out very short lines
                        cleaned_lines.append(line)
                
                return cleaned_lines
                
        except Exception as e:
            print(f"WARNING  Error reading log entries: {e}")
            return []
    
    def display_toolbox_state(self, terminal_info: Dict, account_info: Dict, positions: List[Dict], 
                            orders: List[Dict], experts: List[Dict], journal_entries: List[Dict],
                            log_entries: List[str]):
        """Display current toolbox state"""
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 100)
        print("ROCKET MT5 TOOLBOX MONITOR - REAL-TIME STATE")
        print("=" * 100)
        print(f" Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Connection and Terminal Info
        connected = terminal_info.get('connected', False)
        status_icon = "" if connected else ""
        print(f" Connection: {status_icon} {'CONNECTED' if connected else 'DISCONNECTED'}")
        
        if terminal_info.get('ping_last'):
            print(f" Ping: {terminal_info['ping_last']}ms")
        
        # Account Information
        if account_info:
            print(f"MONEY Account: {account_info.get('login', 'N/A')} | Server: {account_info.get('server', 'N/A')}")
            print(f" Balance: ${account_info.get('balance', 0):,.2f} | Equity: ${account_info.get('equity', 0):,.2f} | Free Margin: ${account_info.get('margin_free', 0):,.2f}")
            
            margin_level = account_info.get('margin_level', 0)
            if margin_level > 0:
                print(f"CHART Margin Level: {margin_level:.1f}%")
        
        # Experts Tab (Asiantuntijat)
        print(f"\n EXPERTS TAB (Asiantuntijat) - {len(experts)} Active Expert(s)")
        print("-" * 70)
        if experts:
            for expert in experts[:10]:  # Show first 10
                status_icon = "" if expert['status'] == 'Running' else ""
                print(f"  {status_icon} {expert['name']}")
                print(f"    Symbol: {expert['symbol']} | Magic: {expert['magic']}")
                print(f"    Positions: {len(expert['positions'])} | Orders: {len(expert['orders'])} | P&L: ${expert['total_profit']:.2f}")
        else:
            print("  No active experts detected")
        
        # Trade Tab - Open Positions
        print(f"\nGRAPH_UP TRADE TAB - Open Positions ({len(positions)})")
        print("-" * 70)
        if positions:
            total_profit = sum(pos['profit'] for pos in positions)
            print(f"CHART Total P&L: ${total_profit:.2f}")
            
            for pos in positions[:10]:  # Show first 10
                profit_icon = "" if pos['profit'] >= 0 else ""
                print(f"  {profit_icon} #{pos['ticket']} {pos['symbol']} {pos['type']} {pos['volume']} lots")
                print(f"    Open: {pos['price_open']} -> Current: {pos['price_current']} | P&L: ${pos['profit']:.2f}")
                if pos['comment']:
                    print(f"    Comment: {pos['comment']}")
        else:
            print("  No open positions")
        
        # Trade Tab - Pending Orders
        if orders:
            print(f"\n PENDING ORDERS ({len(orders)})")
            print("-" * 70)
            for order in orders[:5]:  # Show first 5
                print(f"   #{order['ticket']} {order['symbol']} {order['type']} {order['volume']} lots at {order['price_open']}")
                if order['sl'] > 0:
                    print(f"    SL: {order['sl']} | TP: {order['tp']}")
        
        # Journal Tab (Lehti) - Recent Activity
        print(f"\n JOURNAL TAB (Lehti) - Recent Activity")
        print("-" * 70)
        
        # Show generated journal entries
        if journal_entries:
            for entry in journal_entries[-5:]:  # Show last 5
                level_icon = "" if entry['level'] == 'ERROR' else "WARNING" if entry['level'] == 'WARNING' else ""
                time_str = entry['timestamp'].strftime('%H:%M:%S')
                print(f"  {level_icon} [{time_str}] {entry['source']}: {entry['message']}")
        
        # Show actual log entries
        if log_entries:
            print(f"\n Recent Log Entries:")
            for log_entry in log_entries[-3:]:  # Show last 3
                # Try to parse timestamp from log entry
                if len(log_entry) > 20:
                    print(f"   {log_entry[:80]}..." if len(log_entry) > 80 else f"   {log_entry}")
        
        print(f"\n{'=' * 100}")
        print("Press Ctrl+C to stop monitoring")
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if not self.initialize_mt5():
            print("ERROR Failed to initialize MT5")
            return
        
        print(" Starting MT5 Toolbox monitoring...")
        self.monitoring = True
        
        try:
            while self.monitoring:
                # Get current state
                terminal_info = self.get_terminal_info()
                account_info = self.get_account_info()
                positions = self.get_positions()
                orders = self.get_orders()
                experts = self.detect_experts(positions, orders)
                journal_entries = self.generate_journal_entries(positions, orders)
                log_entries = self.read_recent_log_entries(5)
                
                # Add to journal history
                self.journal_entries.extend(journal_entries)
                # Keep only last 50 entries
                if len(self.journal_entries) > 50:
                    self.journal_entries = self.journal_entries[-50:]
                
                # Display state
                self.display_toolbox_state(
                    terminal_info, account_info, positions, orders, 
                    experts, self.journal_entries, log_entries
                )
                
                # Wait before next update
                time.sleep(self.update_interval)
        
        except KeyboardInterrupt:
            print(f"\n Monitoring stopped by user")
        except Exception as e:
            print(f"ERROR Monitoring error: {e}")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        mt5.shutdown()
        print("OK MT5 monitoring stopped")
    
    def export_current_state(self):
        """Export current state to JSON"""
        try:
            terminal_info = self.get_terminal_info()
            account_info = self.get_account_info()
            positions = self.get_positions()
            orders = self.get_orders()
            experts = self.detect_experts(positions, orders)
            log_entries = self.read_recent_log_entries(10)
            
            state_data = {
                'timestamp': datetime.now().isoformat(),
                'terminal_info': terminal_info,
                'account_info': account_info,
                'positions': positions,
                'orders': orders,
                'experts': experts,
                'journal_entries': [
                    {
                        'timestamp': entry['timestamp'].isoformat() if isinstance(entry['timestamp'], datetime) else str(entry['timestamp']),
                        'level': entry['level'],
                        'source': entry['source'],
                        'message': entry['message']
                    } for entry in self.journal_entries
                ],
                'log_entries': log_entries
            }
            
            filename = f"mt5_toolbox_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"OK State exported to {filename}")
            
        except Exception as e:
            print(f"ERROR Export failed: {e}")

def main():
    """Main function"""
    print("MT5 Toolbox Simple Monitor")
    print("=" * 50)
    
    monitor = MT5SimpleMonitor()
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
    except Exception as e:
        print(f"ERROR Monitor failed: {e}")
    finally:
        # Export final state
        monitor.export_current_state()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()