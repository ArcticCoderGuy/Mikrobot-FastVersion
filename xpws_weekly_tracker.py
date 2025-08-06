"""
XPWS WEEKLY PROFIT TRACKING SYSTEM
MIKROBOT_FASTVERSION.md Implementation
Per-Symbol Weekly Profit Tracking with Automatic 1:2 R:R Activation
"""
import MetaTrader5 as mt5
import json
from pathlib import Path
from datetime import datetime, timedelta
import sqlite3

class XPWSWeeklyTracker:
    """
    XPWS (Extra-Profit-Weekly-Strategy) System
    - Track weekly profit per symbol independently
    - Auto-activate 1:2 R:R mode at 10% weekly profit
    - Monday weekly reset
    - Per-symbol tracking and memory
    """
    
    def __init__(self):
        self.profit_threshold = 10.0  # 10% weekly profit threshold
        self.common_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
        self.db_path = self.common_path / "xpws_tracking.db"
        self.init_database()
        
    def init_database(self):
        """Initialize XPWS tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS xpws_tracking (
                symbol TEXT PRIMARY KEY,
                week_start DATE,
                initial_balance REAL,
                current_balance REAL,
                weekly_profit_percent REAL,
                xpws_active BOOLEAN,
                activation_time TEXT,
                last_update TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS xpws_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                ticket INTEGER,
                open_time TEXT,
                close_time TEXT,
                profit REAL,
                volume REAL,
                trade_type TEXT,
                xpws_mode BOOLEAN,
                week_start DATE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_week_start(self, date=None):
        """Get Monday of current week (XPWS reset day)"""
        if date is None:
            date = datetime.now()
        
        # Find Monday of current week
        days_since_monday = date.weekday()  # Monday = 0
        week_start = date - timedelta(days=days_since_monday)
        return week_start.date()
    
    def calculate_weekly_profit_for_symbol(self, symbol, account_balance):
        """Calculate weekly profit percentage for specific symbol"""
        week_start = self.get_week_start()
        
        # Get trades for this symbol this week
        deals = mt5.history_deals_get(
            datetime.combine(week_start, datetime.min.time()),
            datetime.now()
        )
        
        if not deals:
            return 0.0, 0.0
        
        # Filter trades for this symbol
        symbol_profit = 0.0
        trade_count = 0
        
        for deal in deals:
            if deal.symbol == symbol and deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
                symbol_profit += deal.profit
                trade_count += 1
        
        # Calculate profit percentage
        if account_balance > 0:
            profit_percent = (symbol_profit / account_balance) * 100
        else:
            profit_percent = 0.0
            
        return profit_percent, symbol_profit
    
    def update_symbol_tracking(self, symbol, account_balance):
        """Update XPWS tracking for symbol"""
        week_start = self.get_week_start()
        profit_percent, symbol_profit = self.calculate_weekly_profit_for_symbol(symbol, account_balance)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if symbol exists for current week
        cursor.execute('''
            SELECT * FROM xpws_tracking 
            WHERE symbol = ? AND week_start = ?
        ''', (symbol, week_start))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            xpws_active = profit_percent >= self.profit_threshold
            activation_time = existing[5] if existing[5] else None
            
            # Set activation time if just activated
            if xpws_active and not existing[4]:  # Just activated
                activation_time = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE xpws_tracking 
                SET current_balance = ?, weekly_profit_percent = ?, 
                    xpws_active = ?, activation_time = ?, last_update = ?
                WHERE symbol = ? AND week_start = ?
            ''', (account_balance, profit_percent, xpws_active, 
                  activation_time, datetime.now().isoformat(), symbol, week_start))
        else:
            # Create new record for this week
            xpws_active = profit_percent >= self.profit_threshold
            activation_time = datetime.now().isoformat() if xpws_active else None
            
            cursor.execute('''
                INSERT INTO xpws_tracking 
                (symbol, week_start, initial_balance, current_balance, 
                 weekly_profit_percent, xpws_active, activation_time, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, week_start, account_balance, account_balance,
                  profit_percent, xpws_active, activation_time, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            "symbol": symbol,
            "weekly_profit_percent": round(profit_percent, 2),
            "xpws_active": xpws_active,
            "profit_threshold": self.profit_threshold,
            "symbol_profit": round(symbol_profit, 2),
            "week_start": str(week_start)
        }
    
    def is_xpws_active(self, symbol):
        """Check if XPWS mode is active for symbol"""
        week_start = self.get_week_start()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT xpws_active FROM xpws_tracking 
            WHERE symbol = ? AND week_start = ?
        ''', (symbol, week_start))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else False
    
    def get_risk_reward_ratio(self, symbol):
        """Get appropriate R:R ratio based on XPWS status"""
        if self.is_xpws_active(symbol):
            return 2.0  # 1:2 R:R in XPWS mode
        else:
            return 1.0  # 1:1 R:R in standard mode
    
    def reset_weekly_tracking(self):
        """Reset tracking for new week (Monday)"""
        current_week = self.get_week_start()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Archive old week data and reset
        cursor.execute('''
            UPDATE xpws_tracking 
            SET xpws_active = FALSE, weekly_profit_percent = 0.0, activation_time = NULL
            WHERE week_start < ?
        ''', (current_week,))
        
        conn.commit()
        conn.close()
        
        return f"Weekly tracking reset for week starting {current_week}"
    
    def get_xpws_status_report(self, account_balance):
        """Generate comprehensive XPWS status report"""
        if not mt5.initialize():
            return None
            
        # Get active symbols
        positions = mt5.positions_get()
        symbols = set()
        
        if positions:
            symbols.update([pos.symbol for pos in positions])
        
        # Add some common symbols for tracking
        common_symbols = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "SPX500"]
        symbols.update(common_symbols)
        
        status_report = {
            "timestamp": datetime.now().isoformat(),
            "week_start": str(self.get_week_start()),
            "account_balance": account_balance,
            "profit_threshold": self.profit_threshold,
            "symbols": {},
            "active_xpws_count": 0,
            "total_weekly_profit": 0.0
        }
        
        for symbol in symbols:
            symbol_status = self.update_symbol_tracking(symbol, account_balance)
            status_report["symbols"][symbol] = symbol_status
            
            if symbol_status["xpws_active"]:
                status_report["active_xpws_count"] += 1
            
            status_report["total_weekly_profit"] += symbol_status.get("symbol_profit", 0)
        
        return status_report
    
    def save_xpws_status(self, account_balance):
        """Save XPWS status to JSON file for MT5 EA"""
        status_report = self.get_xpws_status_report(account_balance)
        if not status_report:
            return False
            
        status_file = self.common_path / "xpws_status.json"
        
        try:
            with open(status_file, 'w') as f:
                json.dump(status_report, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving XPWS status: {e}")
            return False
    
    def log_trade_for_xpws(self, symbol, ticket, profit, volume, trade_type):
        """Log trade for XPWS tracking"""
        week_start = self.get_week_start()
        xpws_mode = self.is_xpws_active(symbol)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO xpws_trades 
            (symbol, ticket, open_time, profit, volume, trade_type, xpws_mode, week_start)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, ticket, datetime.now().isoformat(), profit, volume, 
              trade_type, xpws_mode, week_start))
        
        conn.commit()
        conn.close()
        
        return f"Trade logged: {symbol} | {trade_type} | Profit: ${profit} | XPWS: {xpws_mode}"

if __name__ == "__main__":
    # Test XPWS Weekly Tracking
    xpws_tracker = XPWSWeeklyTracker()
    
    if mt5.initialize():
        # Connect to account
        login = 95244786
        password = "Ua@tOnLp"
        server = "Ava-Demo 1-MT5"
        
        if mt5.login(login, password, server):
            account_info = mt5.account_info()
            account_balance = account_info.balance if account_info else 10000
            
            print("SUCCESS: XPWS Weekly Tracking System Test")
            print(f"Account: {login} | Balance: ${account_balance}")
            
            # Generate status report
            status_report = xpws_tracker.get_xpws_status_report(account_balance)
            
            if status_report:
                print(f"\nXPWS Status Report - Week: {status_report['week_start']}")
                print(f"Active XPWS pairs: {status_report['active_xpws_count']}")
                print(f"Total weekly profit: ${status_report['total_weekly_profit']:.2f}")
                
                print(f"\nSymbol Status:")
                for symbol, data in status_report["symbols"].items():
                    xpws_status = "XPWS" if data["xpws_active"] else "STD"
                    rr_ratio = "1:2" if data["xpws_active"] else "1:1"
                    print(f"  {symbol:8} | {xpws_status} | {data['weekly_profit_percent']:6.2f}% | {rr_ratio}")
                
                # Save status file
                if xpws_tracker.save_xpws_status(account_balance):
                    print(f"\nSUCCESS: XPWS status saved to: {xpws_tracker.common_path / 'xpws_status.json'}")
            
        mt5.shutdown()
    else:
        print("ERROR: Failed to initialize MT5")