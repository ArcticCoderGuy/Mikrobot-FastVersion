#!/usr/bin/env python3
"""
MCP Monitoring Dashboard - Real-time unified monitoring
Shows actual trading execution, system status, and coordination health
"""
import sys
import json
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
from pathlib import Path
import os

# ASCII-only encoding enforcement
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    """Enforce ASCII-only output"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

class MCPMonitoringDashboard:
    """Unified monitoring dashboard for all MCP-coordinated systems"""
    
    def __init__(self):
        self.signal_dir = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
        self.mt5_initialized = False
        
    def initialize_mt5(self) -> bool:
        """Initialize MT5 connection"""
        if not mt5.initialize():
            return False
        self.mt5_initialized = True
        return True
        
    def get_real_trading_status(self) -> dict:
        """Get ACTUAL trading status from MT5"""
        if not self.mt5_initialized:
            return {'status': 'DISCONNECTED', 'error': 'MT5 not initialized'}
            
        try:
            # Account info
            account_info = mt5.account_info()
            if not account_info:
                return {'status': 'ERROR', 'error': 'No account info'}
                
            # Recent trades (last hour)
            from_date = datetime.now() - timedelta(hours=1)
            deals = mt5.history_deals_get(from_date, datetime.now())
            
            # Current positions
            positions = mt5.positions_get()
            
            # Pending orders
            orders = mt5.orders_get()
            
            return {
                'status': 'CONNECTED',
                'account': {
                    'login': account_info.login,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'profit': account_info.profit,
                    'margin': account_info.margin,
                    'free_margin': account_info.margin_free
                },
                'recent_deals': len(deals) if deals else 0,
                'deals_detail': [
                    {
                        'ticket': deal.ticket,
                        'symbol': deal.symbol,
                        'type': 'BUY' if deal.type == 0 else 'SELL',
                        'volume': deal.volume,
                        'price': deal.price,
                        'time': datetime.fromtimestamp(deal.time).strftime('%H:%M:%S'),
                        'profit': deal.profit
                    } for deal in (deals[-10:] if deals else [])
                ],
                'current_positions': len(positions) if positions else 0,
                'positions_detail': [
                    {
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': 'BUY' if pos.type == 0 else 'SELL',
                        'volume': pos.volume,
                        'price_open': pos.price_open,
                        'profit': pos.profit,
                        'sl': pos.sl,
                        'tp': pos.tp
                    } for pos in (positions if positions else [])
                ],
                'pending_orders': len(orders) if orders else 0
            }
            
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}
            
    def get_signal_monitoring_status(self) -> dict:
        """Check signal file monitoring status"""
        try:
            signal_files = list(self.signal_dir.glob("mikrobot*.json"))
            
            status = {
                'signal_files_found': len(signal_files),
                'files': [],
                'latest_signal': None
            }
            
            for file in signal_files:
                file_stat = file.stat()
                file_info = {
                    'name': file.name,
                    'size': file_stat.st_size,
                    'modified': datetime.fromtimestamp(file_stat.st_mtime).strftime('%H:%M:%S'),
                    'readable': True
                }
                
                # Try to read the file
                try:
                    with open(file, 'rb') as f:
                        content = f.read()
                    
                    # Handle UTF-16LE
                    if content.startswith(b'\\xff\\xfe'):
                        content_str = content.decode('utf-16le', errors='ignore')
                    else:
                        content_str = content.decode('utf-8', errors='ignore')
                    
                    # Clean content
                    content_str = content_str.replace('\\x00', '')
                    content_str = ''.join(char for char in content_str if ord(char) < 128 or char in '{}":,.-')
                    
                    signal_data = json.loads(content_str)
                    file_info['content'] = {
                        'timestamp': signal_data.get('timestamp', 'N/A'),
                        'symbol': signal_data.get('symbol', 'N/A'),
                        'direction': signal_data.get('trade_direction', 'N/A'),
                        'ylipip_triggered': signal_data.get('phase_4_ylipip', {}).get('triggered', False)
                    }
                    
                    # Update latest signal
                    if not status['latest_signal'] or file_stat.st_mtime > status['latest_signal'].get('mtime', 0):
                        status['latest_signal'] = {
                            'file': file.name,
                            'mtime': file_stat.st_mtime,
                            'data': file_info['content']
                        }
                        
                except Exception as e:
                    file_info['readable'] = False
                    file_info['error'] = str(e)
                    
                status['files'].append(file_info)
                
            return status
            
        except Exception as e:
            return {'error': str(e)}
            
    def get_coordination_health(self) -> dict:
        """Check MCP coordination health"""
        health = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'components': {}
        }
        
        # Check MT5 connection
        health['components']['mt5'] = {
            'status': 'CONNECTED' if self.mt5_initialized else 'DISCONNECTED',
            'details': 'MT5 API connection active' if self.mt5_initialized else 'MT5 connection failed'
        }
        
        # Check signal monitoring
        signal_status = self.get_signal_monitoring_status()
        health['components']['signal_monitoring'] = {
            'status': 'ACTIVE' if signal_status.get('signal_files_found', 0) > 0 else 'INACTIVE',
            'details': f"Found {signal_status.get('signal_files_found', 0)} signal files"
        }
        
        # Check orchestrator process (if log file exists)
        orchestrator_log = Path('mcp_orchestrator.log')
        health['components']['orchestrator'] = {
            'status': 'UNKNOWN',
            'details': 'Log file not found'
        }
        
        if orchestrator_log.exists():
            try:
                # Check if log was updated recently (within last 5 minutes)
                log_mtime = orchestrator_log.stat().st_mtime
                if time.time() - log_mtime < 300:  # 5 minutes
                    health['components']['orchestrator'] = {
                        'status': 'ACTIVE',
                        'details': 'Recent log activity detected'
                    }
                else:
                    health['components']['orchestrator'] = {
                        'status': 'STALE',
                        'details': 'Log not updated recently'
                    }
            except Exception as e:
                health['components']['orchestrator'] = {
                    'status': 'ERROR',
                    'details': str(e)
                }
                
        return health
        
    def display_dashboard(self):
        """Display comprehensive dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        ascii_print("=" * 80)
        ascii_print("  MCP TRADING ORCHESTRATOR - UNIFIED MONITORING DASHBOARD")
        ascii_print("=" * 80)
        ascii_print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        ascii_print("")
        
        # Trading Status
        ascii_print("1. REAL TRADING STATUS")
        ascii_print("-" * 40)
        trading_status = self.get_real_trading_status()
        
        if trading_status['status'] == 'CONNECTED':
            account = trading_status['account']
            ascii_print(f"MT5 Account: {account['login']}")
            ascii_print(f"Balance: ${account['balance']:.2f}")
            ascii_print(f"Equity: ${account['equity']:.2f}")
            ascii_print(f"Profit: ${account['profit']:.2f}")
            ascii_print(f"Free Margin: ${account['free_margin']:.2f}")
            ascii_print("")
            
            ascii_print(f"Recent Deals (1hr): {trading_status['recent_deals']}")
            if trading_status['deals_detail']:
                for deal in trading_status['deals_detail'][-5:]:
                    ascii_print(f"  {deal['time']} | {deal['symbol']} {deal['type']} {deal['volume']} @ {deal['price']} | P&L: ${deal['profit']:.2f}")
            ascii_print("")
            
            ascii_print(f"Current Positions: {trading_status['current_positions']}")
            if trading_status['positions_detail']:
                for pos in trading_status['positions_detail']:
                    ascii_print(f"  #{pos['ticket']} | {pos['symbol']} {pos['type']} {pos['volume']} @ {pos['price_open']} | P&L: ${pos['profit']:.2f}")
            
        else:
            ascii_print(f"STATUS: {trading_status['status']}")
            if 'error' in trading_status:
                ascii_print(f"ERROR: {trading_status['error']}")
                
        ascii_print("")
        
        # Signal Monitoring
        ascii_print("2. SIGNAL MONITORING STATUS")
        ascii_print("-" * 40)
        signal_status = self.get_signal_monitoring_status()
        
        if 'error' not in signal_status:
            ascii_print(f"Signal Files Found: {signal_status['signal_files_found']}")
            
            if signal_status['latest_signal']:
                latest = signal_status['latest_signal']
                ascii_print(f"Latest Signal: {latest['file']}")
                ascii_print(f"  Symbol: {latest['data']['symbol']}")
                ascii_print(f"  Direction: {latest['data']['direction']}")
                ascii_print(f"  YLIPIP Triggered: {latest['data']['ylipip_triggered']}")
                ascii_print(f"  Timestamp: {latest['data']['timestamp']}")
            else:
                ascii_print("No valid signals found")
                
            ascii_print("")
            ascii_print("Signal Files:")
            for file_info in signal_status['files']:
                status_icon = "OK" if file_info['readable'] else "ERR"
                ascii_print(f"  [{status_icon}] {file_info['name']} | Modified: {file_info['modified']}")
                
        else:
            ascii_print(f"ERROR: {signal_status['error']}")
            
        ascii_print("")
        
        # Coordination Health
        ascii_print("3. MCP COORDINATION HEALTH")
        ascii_print("-" * 40)
        health = self.get_coordination_health()
        
        for component, status in health['components'].items():
            status_icon = {
                'CONNECTED': '[ONLINE]',
                'ACTIVE': '[ACTIVE]',
                'DISCONNECTED': '[OFFLINE]',
                'INACTIVE': '[INACTIVE]',
                'STALE': '[STALE]',
                'ERROR': '[ERROR]',
                'UNKNOWN': '[UNKNOWN]'
            }.get(status['status'], '[?]')
            
            ascii_print(f"{status_icon} {component.upper()}: {status['details']}")
            
        ascii_print("")
        ascii_print("=" * 80)
        ascii_print("Press Ctrl+C to stop monitoring")
        
    def run_continuous_monitoring(self):
        """Run continuous monitoring dashboard"""
        try:
            # Initialize MT5
            self.initialize_mt5()
            
            while True:
                self.display_dashboard()
                time.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            ascii_print("\nMonitoring stopped by user")
        finally:
            if self.mt5_initialized:
                mt5.shutdown()

def main():
    """Main entry point"""
    dashboard = MCPMonitoringDashboard()
    dashboard.run_continuous_monitoring()

if __name__ == "__main__":
    main()