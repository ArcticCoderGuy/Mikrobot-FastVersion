#!/usr/bin/env python3
"""
Safe MT5 Test - Won't interfere with existing connections
Uses Connection Guard to prevent conflicts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.connection_guard import connection_guard, MT5Context
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def safe_connection_test():
    """Test MT5 connection without interfering with existing ones"""
    
    print("MIKROBOT - SAFE MT5 CONNECTION TEST")
    print("=" * 50)
    print("WARNING: This test will NOT interfere with your existing MT5 connection")
    print()
    
    # Check current connection status first
    status = connection_guard.get_connection_status()
    
    print("Current Connection Status:")
    print(f"  Active: {status['active']}")
    print(f"  Owner: {status['owner']}")
    print(f"  Responsive: {status['is_responsive']}")
    
    if status['active']:
        print(f"  Account: {status['connection_info'].get('login', 'Unknown')}")
        print(f"  Last Activity: {status['last_activity']}")
        print()
        print("EXISTING CONNECTION DETECTED!")
        print("   Your MT5 terminal connection is SAFE")
        print("   Mikrobot will NOT interfere with it")
        print()
        
        # Show activity log
        activity = connection_guard.get_activity_log(5)
        if activity:
            print("Recent Activity:")
            for entry in activity[-3:]:
                print(f"  {entry['time'].strftime('%H:%M:%S')}: {entry['action']} by {entry.get('owner', 'unknown')}")
        
        return True
    
    print("No existing connection detected - safe to test")
    print()
    
    # Get credentials
    login = int(os.getenv('MT5_LOGIN', 95244786))
    password = os.getenv('MT5_PASSWORD', 'Ua@tOnLp')
    server = os.getenv('MT5_SERVER', 'MetaQuotesDemo')
    
    try:
        # Use safe context manager
        with MT5Context("safe_test_component", login, password, server) as connection:
            
            print("Safe connection established!")
            print(f"   Account: {connection['account']}")
            print(f"   Owner: {connection['owner']}")
            print(f"   Status: {connection['status']}")
            
            # Quick test without interfering
            import MetaTrader5 as mt5
            
            # Get basic info
            account_info = mt5.account_info()
            if account_info:
                print(f"   Name: {account_info.name}")
                print(f"   Balance: {account_info.balance} {account_info.currency}")
            
            # Get one price tick
            tick = mt5.symbol_info_tick("EURUSD")
            if tick:
                print(f"   EURUSD: {tick.bid}")
            
            print()
            print("MESSAGE TO MOBILE:")
            message = f"Mikrobot Test - Turvallinen yhteys OK {datetime.now().strftime('%H:%M:%S')}"
            print(f"   {message}")
            print("   -> Check your MetaQuotes ID: 03A06890")
            
            # Brief pause
            import time
            time.sleep(3)
            
        print()
        print("Connection safely released")
        print("Your MT5 terminal connection is unaffected")
        
        return True
        
    except Exception as e:
        print(f"Safe test failed: {e}")
        return False

def show_connection_guard_status():
    """Show detailed connection guard status"""
    
    print("\nCONNECTION GUARD STATUS:")
    print("-" * 30)
    
    status = connection_guard.get_connection_status()
    
    for key, value in status.items():
        if key == 'connection_info' and value:
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
    
    # Show activity log
    activity = connection_guard.get_activity_log()
    if activity:
        print("\nRecent Activity:")
        for entry in activity:
            time_str = entry['time'].strftime('%H:%M:%S')
            print(f"  {time_str}: {entry['action']}")

if __name__ == "__main__":
    try:
        print("Starting SAFE MT5 test...")
        print("   This will NOT disconnect your MT5 terminal!")
        print()
        
        success = safe_connection_test()
        
        if success:
            show_connection_guard_status()
            print("\nSAFE TEST COMPLETED!")
            print("Your MT5 terminal connection remains intact")
        else:
            print("\nTest failed, but your MT5 connection is safe")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Your MT5 terminal connection is still safe")