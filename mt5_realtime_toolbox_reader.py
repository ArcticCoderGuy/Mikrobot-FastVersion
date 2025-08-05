from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
MT5 Real-time Toolbox Reader
Advanced real-time monitoring of MT5 Toolbox tabs (Journal, Experts, etc.)
"""

import MetaTrader5 as mt5
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import sqlite3
from pathlib import Path
import os
import psutil
import win32gui
import win32con
import win32api
import win32process
from dataclasses import dataclass, asdict
import queue
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mt5_toolbox_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JournalEntry:
    """Journal entry structure"""
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR, DEBUG
    source: str  # Terminal, Expert, Trade, etc.
    message: str
    details: Optional[Dict[str, Any]] = None

@dataclass
class ExpertStatus:
    """Expert Advisor status"""
    name: str
    symbol: str
    status: str  # Running, Stopped, Error
    last_activity: datetime
    parameters: Dict[str, Any]
    performance: Dict[str, float]
    errors: List[str]

@dataclass
class TradeInfo:
    """Trade information"""
    ticket: int
    symbol: str
    type: str
    volume: float
    open_price: float
    current_price: float
    profit: float
    timestamp: datetime
    comment: str
    magic: int

class MT5ToolboxMonitor:
    """Real-time MT5 Toolbox Monitor"""
    
    def __init__(self):
        self.monitoring = False
        self.update_interval = 0.5  # 500ms updates
        self.journal_entries = queue.Queue(maxsize=1000)
        self.expert_statuses = {}
        self.trade_history = []
        self.last_journal_time = datetime.now() - timedelta(hours=1)
        self.last_position_count = 0
        self.last_order_count = 0
        
        # Initialize database for persistent storage
        self.db_path = "mt5_toolbox_data.db"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for storing toolbox data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Journal entries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS journal_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        level TEXT NOT NULL,
                        source TEXT NOT NULL,
                        message TEXT NOT NULL,
                        details TEXT
                    )
                ''')
                
                # Expert status table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS expert_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        name TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        status TEXT NOT NULL,
                        parameters TEXT,
                        performance TEXT,
                        errors TEXT
                    )
                ''')
                
                # Trade information table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        ticket INTEGER PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        type TEXT NOT NULL,
                        volume REAL NOT NULL,
                        open_price REAL NOT NULL,
                        current_price REAL,
                        profit REAL,
                        comment TEXT,
                        magic INTEGER
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def initialize_mt5(self) -> bool:
        """Initialize MT5 connection"""
        try:
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"MT5 initialization failed: {error}")
                return False
            
            logger.info("MT5 connection established")
            return True
            
        except Exception as e:
            logger.error(f"MT5 initialization error: {e}")
            return False
    
    def get_journal_entries(self) -> List[JournalEntry]:
        """Extract journal entries from various sources"""
        entries = []
        
        try:
            # Check for new positions (appears in journal)
            positions = mt5.positions_get()
            current_position_count = len(positions) if positions else 0
            
            if current_position_count != self.last_position_count:
                if current_position_count > self.last_position_count:
                    # New position opened
                    for pos in positions:
                        if datetime.fromtimestamp(pos.time) > self.last_journal_time:
                            entry = JournalEntry(
                                timestamp=datetime.fromtimestamp(pos.time),
                                level="INFO",
                                source="Trade",
                                message=f"Position opened: {pos.symbol} {pos.type_name} {pos.volume} lots at {pos.price_open}",
                                details={
                                    'ticket': pos.ticket,
                                    'symbol': pos.symbol,
                                    'type': pos.type_name,
                                    'volume': pos.volume,
                                    'price': pos.price_open,
                                    'magic': pos.magic,
                                    'comment': pos.comment
                                }
                            )
                            entries.append(entry)
                else:
                    # Position closed
                    entry = JournalEntry(
                        timestamp=datetime.now(),
                        level="INFO",
                        source="Trade",
                        message=f"Position(s) closed. Active positions: {current_position_count}",
                        details={'position_count': current_position_count}
                    )
                    entries.append(entry)
                
                self.last_position_count = current_position_count
            
            # Check for new orders
            orders = mt5.orders_get()
            current_order_count = len(orders) if orders else 0
            
            if current_order_count != self.last_order_count:
                if current_order_count > self.last_order_count:
                    # New order placed
                    for order in orders:
                        if datetime.fromtimestamp(order.time_setup) > self.last_journal_time:
                            entry = JournalEntry(
                                timestamp=datetime.fromtimestamp(order.time_setup),
                                level="INFO",
                                source="Trade",
                                message=f"Order placed: {order.symbol} {order.type_name} {order.volume_initial} lots at {order.price_open}",
                                details={
                                    'ticket': order.ticket,
                                    'symbol': order.symbol,
                                    'type': order.type_name,
                                    'volume': order.volume_initial,
                                    'price': order.price_open,
                                    'magic': order.magic,
                                    'comment': order.comment
                                }
                            )
                            entries.append(entry)
                
                self.last_order_count = current_order_count
            
            # Check account information changes
            account_info = mt5.account_info()
            if account_info:
                # Create periodic account status entries
                if datetime.now().second % 30 == 0:  # Every 30 seconds
                    entry = JournalEntry(
                        timestamp=datetime.now(),
                        level="DEBUG",
                        source="Account",
                        message=f"Account status: Balance ${account_info.balance:,.2f}, Equity ${account_info.equity:,.2f}, Free Margin ${account_info.margin_free:,.2f}",
                        details={
                            'balance': account_info.balance,
                            'equity': account_info.equity,
                            'margin': account_info.margin,
                            'free_margin': account_info.margin_free,
                            'margin_level': account_info.margin_level if hasattr(account_info, 'margin_level') else 0
                        }
                    )
                    entries.append(entry)
            
            # Check for connection status
            terminal_info = mt5.terminal_info()
            if terminal_info:
                if not terminal_info.connected and datetime.now().second % 10 == 0:  # Every 10 seconds if disconnected
                    entry = JournalEntry(
                        timestamp=datetime.now(),
                        level="ERROR",
                        source="Terminal",
                        message="Connection lost to trading server",
                        details={'connected': False, 'ping': terminal_info.ping_last}
                    )
                    entries.append(entry)
            
            # Update last journal time
            if entries:
                self.last_journal_time = max(entry.timestamp for entry in entries)
            
        except Exception as e:
            error_entry = JournalEntry(
                timestamp=datetime.now(),
                level="ERROR",
                source="Monitor",
                message=f"Error reading journal entries: {e}",
                details={'error': str(e)}
            )
            entries.append(error_entry)
        
        return entries
    
    def get_expert_statuses(self) -> Dict[str, ExpertStatus]:
        """Get Expert Advisor statuses"""
        experts = {}
        
        try:
            # Get symbol information to check for experts
            symbols = mt5.symbols_get()
            if symbols:
                for symbol in symbols[:20]:  # Check first 20 symbols
                    if symbol.visible:
                        # Check if there are any positions or orders for this symbol
                        positions = mt5.positions_get(symbol=symbol.name)
                        orders = mt5.orders_get(symbol=symbol.name)
                        
                        if positions or orders:
                            # Assume there might be an expert running
                            expert_name = f"Expert_{symbol.name}"
                            
                            # Calculate performance metrics
                            total_profit = sum(pos.profit for pos in positions) if positions else 0
                            position_count = len(positions) if positions else 0
                            order_count = len(orders) if orders else 0
                            
                            expert_status = ExpertStatus(
                                name=expert_name,
                                symbol=symbol.name,
                                status="Running" if (positions or orders) else "Idle",
                                last_activity=datetime.now(),
                                parameters={
                                    'symbol': symbol.name,
                                    'spread': symbol.spread,
                                    'digits': symbol.digits,
                                    'point': symbol.point
                                },
                                performance={
                                    'total_profit': total_profit,
                                    'position_count': position_count,
                                    'order_count': order_count,
                                    'spread': symbol.spread
                                },
                                errors=[]
                            )
                            
                            experts[expert_name] = expert_status
            
            # Check for any errors or warnings
            last_error = mt5.last_error()
            if last_error[0] != 0:  # Non-zero error code
                error_entry = f"MT5 Error {last_error[0]}: {last_error[1]}"
                for expert in experts.values():
                    expert.errors.append(error_entry)
            
        except Exception as e:
            logger.error(f"Error getting expert statuses: {e}")
        
        return experts
    
    def get_trade_information(self) -> List[TradeInfo]:
        """Get current trade information"""
        trades = []
        
        try:
            # Get open positions
            positions = mt5.positions_get()
            if positions:
                for pos in positions:
                    trade = TradeInfo(
                        ticket=pos.ticket,
                        symbol=pos.symbol,
                        type=pos.type_name,
                        volume=pos.volume,
                        open_price=pos.price_open,
                        current_price=pos.price_current,
                        profit=pos.profit,
                        timestamp=datetime.fromtimestamp(pos.time),
                        comment=pos.comment,
                        magic=pos.magic
                    )
                    trades.append(trade)
            
            # Get pending orders
            orders = mt5.orders_get()
            if orders:
                for order in orders:
                    trade = TradeInfo(
                        ticket=order.ticket,
                        symbol=order.symbol,
                        type=order.type_name,
                        volume=order.volume_initial,
                        open_price=order.price_open,
                        current_price=order.price_current if hasattr(order, 'price_current') else order.price_open,
                        profit=0,  # Pending orders don't have profit yet
                        timestamp=datetime.fromtimestamp(order.time_setup),
                        comment=order.comment,
                        magic=order.magic
                    )
                    trades.append(trade)
        
        except Exception as e:
            logger.error(f"Error getting trade information: {e}")
        
        return trades
    
    def save_to_database(self, entries: List[JournalEntry], experts: Dict[str, ExpertStatus], trades: List[TradeInfo]):
        """Save data to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Save journal entries
                for entry in entries:
                    cursor.execute('''
                        INSERT INTO journal_entries (timestamp, level, source, message, details)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        entry.timestamp.isoformat(),
                        entry.level,
                        entry.source,
                        entry.message,
                        json.dumps(entry.details, ensure_ascii=True) if entry.details else None
                    ))
                
                # Save expert statuses
                for expert in experts.values():
                    cursor.execute('''
                        INSERT OR REPLACE INTO expert_status 
                        (timestamp, name, symbol, status, parameters, performance, errors)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        datetime.now().isoformat(),
                        expert.name,
                        expert.symbol,
                        expert.status,
                        json.dumps(expert.parameters, ensure_ascii=True),
                        json.dumps(expert.performance, ensure_ascii=True),
                        json.dumps(expert.errors, ensure_ascii=True)
                    ))
                
                # Save trades
                for trade in trades:
                    cursor.execute('''
                        INSERT OR REPLACE INTO trades 
                        (ticket, timestamp, symbol, type, volume, open_price, current_price, profit, comment, magic)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        trade.ticket,
                        trade.timestamp.isoformat(),
                        trade.symbol,
                        trade.type,
                        trade.volume,
                        trade.open_price,
                        trade.current_price,
                        trade.profit,
                        trade.comment,
                        trade.magic
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Database save error: {e}")
    
    def display_toolbox_state(self, entries: List[JournalEntry], experts: Dict[str, ExpertStatus], trades: List[TradeInfo]):
        """Display current toolbox state"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 100)
        print("ROCKET MT5 REAL-TIME TOOLBOX MONITOR")
        print("=" * 100)
        print(f" Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Connection status
        terminal_info = mt5.terminal_info()
        if terminal_info:
            status = " CONNECTED" if terminal_info.connected else " DISCONNECTED"
            print(f" Connection Status: {status} | Ping: {terminal_info.ping_last}ms")
        
        # Account information
        account_info = mt5.account_info()
        if account_info:
            print(f"MONEY Account: {account_info.login} | Balance: ${account_info.balance:,.2f} | Equity: ${account_info.equity:,.2f}")
        
        # Experts Tab (Asiantuntijat)
        print(f"\n EXPERTS TAB (Asiantuntijat) - {len(experts)} Expert(s)")
        print("-" * 50)
        if experts:
            for expert in list(experts.values())[:5]:  # Show first 5
                status_icon = "" if expert.status == "Running" else "" if expert.status == "Idle" else ""
                print(f"  {status_icon} {expert.name} ({expert.symbol})")
                print(f"    Status: {expert.status} | Positions: {expert.performance.get('position_count', 0)} | Profit: ${expert.performance.get('total_profit', 0):.2f}")
                if expert.errors:
                    print(f"    WARNING  Errors: {len(expert.errors)}")
        else:
            print("  No active experts detected")
        
        # Trade Tab
        print(f"\nGRAPH_UP TRADE TAB - {len(trades)} Active Trade(s)")
        print("-" * 50)
        if trades:
            for trade in trades[:10]:  # Show first 10
                profit_icon = "" if trade.profit >= 0 else ""
                print(f"  {profit_icon} #{trade.ticket} {trade.symbol} {trade.type} {trade.volume} lots")
                print(f"    Price: {trade.open_price} -> {trade.current_price} | Profit: ${trade.profit:.2f}")
                if trade.comment:
                    print(f"    Comment: {trade.comment}")
        else:
            print("  No active trades")
        
        # Journal Tab (Lehti)
        print(f"\n JOURNAL TAB (Lehti) - Recent Entries")
        print("-" * 50)
        if entries:
            for entry in entries[-10:]:  # Show last 10 entries
                level_icon = "" if entry.level == "ERROR" else "WARNING" if entry.level == "WARNING" else ""
                print(f"  {level_icon} [{entry.timestamp.strftime('%H:%M:%S')}] {entry.source}: {entry.message}")
        else:
            print("  No recent journal entries")
        
        print(f"\n{'=' * 100}")
        print("Press Ctrl+C to stop monitoring | Data saved to mt5_toolbox_data.db")
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.monitoring:
            logger.warning("Monitoring already started")
            return
        
        if not self.initialize_mt5():
            logger.error("Failed to initialize MT5")
            return
        
        self.monitoring = True
        logger.info("Starting real-time MT5 toolbox monitoring...")
        
        try:
            while self.monitoring:
                # Get current data
                journal_entries = self.get_journal_entries()
                expert_statuses = self.get_expert_statuses()
                trade_info = self.get_trade_information()
                
                # Update internal state
                self.expert_statuses = expert_statuses
                self.trade_history = trade_info
                
                # Add journal entries to queue
                for entry in journal_entries:
                    try:
                        self.journal_entries.put_nowait(entry)
                    except queue.Full:
                        # Remove oldest entry if queue is full
                        try:
                            self.journal_entries.get_nowait()
                            self.journal_entries.put_nowait(entry)
                        except queue.Empty:
                            pass
                
                # Save to database
                self.save_to_database(journal_entries, expert_statuses, trade_info)
                
                # Display current state
                self.display_toolbox_state(journal_entries, expert_statuses, trade_info)
                
                # Wait before next update
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        mt5.shutdown()
        logger.info("MT5 toolbox monitoring stopped")
    
    def export_data(self, filename: str = "mt5_toolbox_export.json"):
        """Export collected data to JSON file"""
        try:
            # Get all journal entries from queue
            all_entries = []
            while not self.journal_entries.empty():
                try:
                    entry = self.journal_entries.get_nowait()
                    all_entries.append(asdict(entry))
                except queue.Empty:
                    break
            
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'journal_entries': all_entries,
                'expert_statuses': {k: asdict(v) for k, v in self.expert_statuses.items()},
                'trade_history': [asdict(t) for t in self.trade_history]
            }
            
            # Convert datetime objects to strings
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                return obj
            
            export_data = convert_datetime(export_data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data exported to {filename}")
            
        except Exception as e:
            logger.error(f"Export failed: {e}")

def main():
    """Main function"""
    print(" MT5 Real-time Toolbox Monitor")
    print("=" * 50)
    
    monitor = MT5ToolboxMonitor()
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
    except Exception as e:
        logger.error(f"Monitor failed: {e}")
    finally:
        # Export data on exit
        monitor.export_data()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()