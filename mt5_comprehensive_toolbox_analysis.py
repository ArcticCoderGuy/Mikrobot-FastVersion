from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
MT5 Comprehensive Toolbox Analysis
Complete analysis and monitoring of MT5 terminal state with real-time capabilities
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json
from pathlib import Path
import time
import os
import sqlite3
from typing import Dict, List, Any, Optional

class MT5ToolboxAnalyzer:
    """Comprehensive MT5 Toolbox State Analyzer"""
    
    def __init__(self):
        self.data_collected = {
            'terminal_info': {},
            'account_info': {},
            'positions': [],
            'orders': [],
            'experts': [],
            'journal_entries': [],
            'log_entries': [],
            'signal_files': []
        }
    
    def initialize(self) -> bool:
        """Initialize MT5 connection"""
        try:
            if not mt5.initialize():
                error = mt5.last_error()
                print(f"[ERROR] MT5 initialization failed: {error}")
                return False
            print("[OK] MT5 connection established")
            return True
        except Exception as e:
            print(f"[ERROR] MT5 initialization error: {e}")
            return False
    
    def collect_terminal_info(self) -> Dict[str, Any]:
        """Collect comprehensive terminal information"""
        try:
            terminal_info = mt5.terminal_info()
            if not terminal_info:
                return {}
            
            info = {
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
                'connected': terminal_info.connected,
                'dlls_allowed': terminal_info.dlls_allowed,
                'trade_allowed': terminal_info.trade_allowed,
                'email_enabled': terminal_info.email_enabled,
                'notifications_enabled': terminal_info.notifications_enabled,
                'mqid': terminal_info.mqid,
                'ping_last': terminal_info.ping_last,
                'community_balance': terminal_info.community_balance
            }
            
            self.data_collected['terminal_info'] = info
            return info
            
        except Exception as e:
            print(f"[ERROR] Failed to collect terminal info: {e}")
            return {}
    
    def collect_account_info(self) -> Dict[str, Any]:
        """Collect account information"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                return {}
            
            info = {
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
            
            self.data_collected['account_info'] = info
            return info
            
        except Exception as e:
            print(f"[ERROR] Failed to collect account info: {e}")
            return {}
    
    def collect_positions_and_orders(self) -> tuple:
        """Collect open positions and pending orders"""
        positions = []
        orders = []
        
        try:
            # Get positions
            mt5_positions = mt5.positions_get()
            if mt5_positions:
                for pos in mt5_positions:
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
                        'time': datetime.fromtimestamp(pos.time).isoformat(),
                        'comment': pos.comment,
                        'magic': pos.magic,
                        'identifier': pos.identifier
                    }
                    positions.append(position_info)
            
            # Get orders
            mt5_orders = mt5.orders_get()
            if mt5_orders:
                for order in mt5_orders:
                    order_info = {
                        'ticket': order.ticket,
                        'symbol': order.symbol,
                        'type': order.type_name,
                        'volume': order.volume_initial,
                        'price_open': order.price_open,
                        'sl': order.sl,
                        'tp': order.tp,
                        'time_setup': datetime.fromtimestamp(order.time_setup).isoformat(),
                        'comment': order.comment,
                        'magic': order.magic
                    }
                    orders.append(order_info)
            
            self.data_collected['positions'] = positions
            self.data_collected['orders'] = orders
            
        except Exception as e:
            print(f"[ERROR] Failed to collect positions/orders: {e}")
        
        return positions, orders
    
    def analyze_experts(self, positions: List[Dict], orders: List[Dict]) -> List[Dict]:
        """Analyze Expert Advisors based on magic numbers and file system"""
        experts = {}
        
        try:
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
                        'status': 'Active',
                        'positions_count': 0,
                        'orders_count': 0,
                        'total_profit': 0,
                        'total_volume': 0,
                        'last_activity': pos['time']
                    }
                
                experts[key]['positions_count'] += 1
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
                        'status': 'Active',
                        'positions_count': 0,
                        'orders_count': 0,
                        'total_profit': 0,
                        'total_volume': 0,
                        'last_activity': order['time_setup']
                    }
                
                experts[key]['orders_count'] += 1
                experts[key]['total_volume'] += order['volume']
            
            # Check file system for EA files
            terminal_info = self.data_collected.get('terminal_info', {})
            if terminal_info.get('data_path'):
                data_path = Path(terminal_info['data_path'])
                experts_dir = data_path / 'MQL5' / 'Experts'
                if experts_dir.exists():
                    ea_files = list(experts_dir.glob('*.ex5'))
                    for ea_file in ea_files:
                        file_info = {
                            'name': ea_file.name,
                            'file_path': str(ea_file),
                            'size': ea_file.stat().st_size,
                            'modified': datetime.fromtimestamp(ea_file.stat().st_mtime).isoformat(),
                            'status': 'Installed',
                            'symbol': 'Multiple',
                            'magic': 'File_Only',
                            'positions_count': 0,
                            'orders_count': 0,
                            'total_profit': 0,
                            'total_volume': 0
                        }
                        experts[f"file_{ea_file.name}"] = file_info
            
            expert_list = list(experts.values())
            self.data_collected['experts'] = expert_list
            
        except Exception as e:
            print(f"[ERROR] Failed to analyze experts: {e}")
            expert_list = []
        
        return expert_list
    
    def collect_log_entries(self, days: int = 1, max_lines: int = 50) -> List[str]:
        """Collect recent log entries from MT5 log files"""
        log_entries = []
        
        try:
            terminal_info = self.data_collected.get('terminal_info', {})
            if not terminal_info.get('data_path'):
                return []
            
            logs_dir = Path(terminal_info['data_path']) / 'logs'
            if not logs_dir.exists():
                return []
            
            # Get recent log files
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            for single_date in [start_date + timedelta(days=x) for x in range(days + 1)]:
                date_str = single_date.strftime('%Y%m%d')
                log_file = logs_dir / f"{date_str}.log"
                
                if log_file.exists():
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            # Take recent lines from this file
                            recent_lines = lines[-max_lines:] if len(lines) > max_lines else lines
                            
                            for line in recent_lines:
                                cleaned_line = line.strip()
                                if cleaned_line and len(cleaned_line) > 10:
                                    log_entries.append({
                                        'date': date_str,
                                        'content': cleaned_line,
                                        'file': log_file.name
                                    })
                    except Exception as e:
                        print(f"[WARNING] Could not read {log_file}: {e}")
            
            # Sort by most recent and limit
            log_entries = log_entries[-max_lines:]
            self.data_collected['log_entries'] = log_entries
            
        except Exception as e:
            print(f"[ERROR] Failed to collect log entries: {e}")
        
        return log_entries
    
    def collect_signal_files(self) -> List[Dict]:
        """Collect and parse signal files"""
        signal_files = []
        
        try:
            terminal_info = self.data_collected.get('terminal_info', {})
            if not terminal_info.get('commondata_path'):
                return []
            
            files_dir = Path(terminal_info['commondata_path']) / 'Files'
            if not files_dir.exists():
                return []
            
            # Find signal files
            signal_patterns = ['*signal*.json', '*Signal*.json', '*SIGNAL*.json']
            found_files = []
            
            for pattern in signal_patterns:
                found_files.extend(files_dir.glob(pattern))
            
            for signal_file in found_files:
                try:
                    with open(signal_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Clean and parse content
                        if '{' in content and '}' in content:
                            # Extract JSON part
                            start = content.find('{')
                            end = content.rfind('}') + 1
                            json_part = content[start:end]
                            
                            # Clean up spacing issues
                            cleaned_json = json_part.replace(' ', '').replace('\n', '').replace('\r', '')
                            
                            try:
                                signal_data = json.loads(cleaned_json)
                                signal_info = {
                                    'file_name': signal_file.name,
                                    'file_path': str(signal_file),
                                    'file_size': signal_file.stat().st_size,
                                    'modified': datetime.fromtimestamp(signal_file.stat().st_mtime).isoformat(),
                                    'parsed_data': signal_data,
                                    'symbol': signal_data.get('symbol', 'N/A'),
                                    'strategy': signal_data.get('strategy', 'N/A'),
                                    'timestamp': signal_data.get('timestamp', 'N/A'),
                                    'direction': signal_data.get('trade_direction', 'N/A')
                                }
                                signal_files.append(signal_info)
                                
                            except json.JSONDecodeError:
                                # Store raw content if parsing fails
                                signal_info = {
                                    'file_name': signal_file.name,
                                    'file_path': str(signal_file),
                                    'file_size': signal_file.stat().st_size,
                                    'modified': datetime.fromtimestamp(signal_file.stat().st_mtime).isoformat(),
                                    'raw_content': json_part[:500],  # First 500 chars
                                    'parse_error': 'JSON decode failed'
                                }
                                signal_files.append(signal_info)
                
                except Exception as e:
                    print(f"[WARNING] Could not read signal file {signal_file}: {e}")
            
            self.data_collected['signal_files'] = signal_files
            
        except Exception as e:
            print(f"[ERROR] Failed to collect signal files: {e}")
        
        return signal_files
    
    def display_comprehensive_analysis(self):
        """Display comprehensive analysis results"""
        print("\n" + "=" * 80)
        print("MT5 COMPREHENSIVE TOOLBOX ANALYSIS")
        print("=" * 80)
        print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Terminal Information
        terminal_info = self.data_collected.get('terminal_info', {})
        if terminal_info:
            print(f"\n[TERMINAL INFO]")
            print(f"  Company: {terminal_info.get('company', 'N/A')}")
            print(f"  Build: {terminal_info.get('build', 'N/A')}")
            print(f"  Connected: {terminal_info.get('connected', False)}")
            print(f"  Trade Allowed: {terminal_info.get('trade_allowed', False)}")
            print(f"  DLLs Allowed: {terminal_info.get('dlls_allowed', False)}")
            print(f"  Ping: {terminal_info.get('ping_last', 0)}ms")
            print(f"  Data Path: {terminal_info.get('data_path', 'N/A')}")
        
        # Account Information
        account_info = self.data_collected.get('account_info', {})
        if account_info:
            print(f"\n[ACCOUNT INFO]")
            print(f"  Login: {account_info.get('login', 'N/A')}")
            print(f"  Server: {account_info.get('server', 'N/A')}")
            print(f"  Balance: ${account_info.get('balance', 0):,.2f}")
            print(f"  Equity: ${account_info.get('equity', 0):,.2f}")
            print(f"  Free Margin: ${account_info.get('margin_free', 0):,.2f}")
            print(f"  Margin Level: {account_info.get('margin_level', 0):.2f}%")
        
        # Trade Tab Analysis
        positions = self.data_collected.get('positions', [])
        orders = self.data_collected.get('orders', [])
        
        print(f"\n[TRADE TAB ANALYSIS]")
        print(f"  Open Positions: {len(positions)}")
        print(f"  Pending Orders: {len(orders)}")
        
        if positions:
            total_profit = sum(pos['profit'] for pos in positions)
            print(f"  Total P&L: ${total_profit:.2f}")
            print(f"  Positions Details:")
            for i, pos in enumerate(positions[:5]):  # Show first 5
                profit_sign = "+" if pos['profit'] >= 0 else ""
                print(f"    [{i+1}] #{pos['ticket']} {pos['symbol']} {pos['type']} {pos['volume']} lots")
                print(f"        Price: {pos['price_open']} -> {pos['price_current']} | P&L: {profit_sign}${pos['profit']:.2f}")
        
        if orders:
            print(f"  Order Details:")
            for i, order in enumerate(orders[:3]):  # Show first 3
                print(f"    [{i+1}] #{order['ticket']} {order['symbol']} {order['type']} {order['volume']} lots")
                print(f"        Target Price: {order['price_open']} | SL: {order['sl']} | TP: {order['tp']}")
        
        # Experts Tab Analysis
        experts = self.data_collected.get('experts', [])
        print(f"\n[EXPERTS TAB ANALYSIS]")
        print(f"  Total Experts/EAs Found: {len(experts)}")
        
        active_experts = [e for e in experts if e.get('positions_count', 0) > 0 or e.get('orders_count', 0) > 0]
        installed_experts = [e for e in experts if 'file_path' in e]
        
        print(f"  Active Experts (with positions/orders): {len(active_experts)}")
        print(f"  Installed EA Files: {len(installed_experts)}")
        
        if active_experts:
            print(f"  Active Expert Details:")
            for expert in active_experts:
                print(f"    - {expert['name']} (Magic: {expert['magic']})")
                print(f"      Positions: {expert.get('positions_count', 0)} | Orders: {expert.get('orders_count', 0)}")
                print(f"      Total P&L: ${expert.get('total_profit', 0):.2f}")
        
        if installed_experts:
            print(f"  Installed EA Files:")
            for expert in installed_experts[:5]:
                print(f"    - {expert['name']} ({expert.get('size', 0)} bytes)")
        
        # Journal Tab Analysis
        log_entries = self.data_collected.get('log_entries', [])
        print(f"\n[JOURNAL TAB ANALYSIS]")
        print(f"  Recent Log Entries: {len(log_entries)}")
        
        if log_entries:
            print(f"  Recent Activity:")
            for entry in log_entries[-5:]:  # Show last 5
                content = entry['content'][:80] + "..." if len(entry['content']) > 80 else entry['content']
                print(f"    [{entry['date']}] {content}")
        
        # Signal Files Analysis
        signal_files = self.data_collected.get('signal_files', [])
        print(f"\n[SIGNAL FILES ANALYSIS]")
        print(f"  Signal Files Found: {len(signal_files)}")
        
        if signal_files:
            print(f"  Signal Details:")
            for signal in signal_files:
                print(f"    - {signal['file_name']}")
                if 'parsed_data' in signal:
                    print(f"      Symbol: {signal.get('symbol', 'N/A')} | Strategy: {signal.get('strategy', 'N/A')}")
                    print(f"      Direction: {signal.get('direction', 'N/A')} | Time: {signal.get('timestamp', 'N/A')}")
                    
                    # Show special data if available
                    if 'parsed_data' in signal and 'phase_4_ylipip' in signal['parsed_data']:
                        ylipip = signal['parsed_data']['phase_4_ylipip']
                        print(f"      Ylipip Triggered: {ylipip.get('triggered', False)}")
                else:
                    print(f"      Size: {signal['file_size']} bytes | Parse Error: {signal.get('parse_error', 'Unknown')}")
        
        print(f"\n{'=' * 80}")
    
    def export_analysis_report(self, filename: str = None) -> str:
        """Export comprehensive analysis to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"mt5_toolbox_analysis_{timestamp}.json"
        
        try:
            # Add metadata
            report_data = {
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_version': '1.0',
                'mt5_terminal_state': self.data_collected
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"\n[EXPORT] Analysis report saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"[ERROR] Failed to export analysis: {e}")
            return ""
    
    def run_full_analysis(self) -> bool:
        """Run complete MT5 toolbox analysis"""
        print("Starting MT5 Comprehensive Toolbox Analysis...")
        
        if not self.initialize():
            return False
        
        try:
            # Collect all data
            print("[1/6] Collecting terminal information...")
            self.collect_terminal_info()
            
            print("[2/6] Collecting account information...")
            self.collect_account_info()
            
            print("[3/6] Collecting positions and orders...")
            positions, orders = self.collect_positions_and_orders()
            
            print("[4/6] Analyzing Expert Advisors...")
            self.analyze_experts(positions, orders)
            
            print("[5/6] Collecting log entries...")
            self.collect_log_entries()
            
            print("[6/6] Collecting signal files...")
            self.collect_signal_files()
            
            # Display results
            self.display_comprehensive_analysis()
            
            # Export report
            self.export_analysis_report()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Analysis failed: {e}")
            return False
        finally:
            mt5.shutdown()

def main():
    """Main function"""
    analyzer = MT5ToolboxAnalyzer()
    success = analyzer.run_full_analysis()
    
    if success:
        print(f"\n[SUCCESS] MT5 Toolbox Analysis completed successfully!")
    else:
        print(f"\n[FAILED] MT5 Toolbox Analysis failed!")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()