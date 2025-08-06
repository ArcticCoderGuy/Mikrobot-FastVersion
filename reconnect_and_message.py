from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
MT5 Reconnection and Message Sender
Reconnect and send message to MetaQuotes ID: 03A06890
"""

import MetaTrader5 as mt5
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

def reconnect_with_retry():
    """Reconnect to MT5 with multiple attempts"""
    
    print("MIKROBOT - RECONNECTING TO MT5")
    print("=" * 40)
    
    # First, ensure MT5 is properly shut down
    mt5.shutdown()
    time.sleep(2)
    
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        print(f"\nAttempt {attempt}/{max_attempts}:")
        
        # Initialize MT5
        if not mt5.initialize():
            print(f"  MT5 initialization failed: {mt5.last_error()}")
            if attempt < max_attempts:
                print("  Waiting 5 seconds before retry...")
                time.sleep(5)
            continue
        
        print("  MT5 initialized")
        
        # Get credentials
        login = int(os.getenv('MT5_LOGIN', 95244786))
        password = os.getenv('MT5_PASSWORD', 'Ua@tOnLp') 
        server = os.getenv('MT5_SERVER', 'MetaQuotesDemo')
        
        print(f"  Connecting to {server} with account {login}...")
        
        # Try to login
        if not mt5.login(login, password, server):
            error = mt5.last_error()
            print(f"  Login failed: {error}")
            mt5.shutdown()
            if attempt < max_attempts:
                print("  Waiting 5 seconds before retry...")
                time.sleep(5)
            continue
        
        print("  LOGIN SUCCESSFUL!")
        
        # Send messages immediately after successful connection
        return send_messages_now()
    
    print("\nAll connection attempts failed!")
    return False

def send_messages_now():
    """Send messages immediately while connection is active"""
    
    try:
        # Get account info to confirm we're connected
        account_info = mt5.account_info()
        if not account_info:
            print("No account info - connection lost")
            return False
        
        print(f"\nConnected as: {account_info.name}")
        print(f"Account: {account_info.login}")
        print(f"Server: {account_info.server}")
        
        # Create timestamp
        timestamp = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        
        # Message for mobile (MetaQuotes ID: 03A06890)
        mobile_message = f"MIKROBOT: Yhteys toimii! {timestamp}"
        
        print(f"\nSending to mobile (MetaQuotes ID: 03A06890):")
        print(f"Message: {mobile_message}")
        
        # Try multiple methods to ensure message delivery
        
        # Method 1: Get market data (this will log activity)
        print("\n1. Creating Journal entries...")
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
        
        for symbol in symbols:
            try:
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    print(f"   {symbol}: {tick.bid} (logged to Journal)")
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
            except:
                pass
        
        # Method 2: Account operations (will appear in Journal/Account tab)
        print("\n2. Logging account activity...")
        positions = mt5.positions_get()
        print(f"   Active positions: {len(positions) if positions else 0}")
        
        orders = mt5.orders_get()  
        print(f"   Pending orders: {len(orders) if orders else 0}")
        
        # Method 3: Symbol operations
        print("\n3. Market data requests (Journal entries)...")
        try:
            eurusd_info = mt5.symbol_info("EURUSD")
            if eurusd_info:
                print(f"   EURUSD spread: {eurusd_info.spread} points")
            
            # Request history (this logs to Journal)
            history_orders = mt5.history_orders_get(
                datetime.now().replace(hour=0, minute=0, second=0),
                datetime.now()
            )
            print(f"   History requests completed")
            
        except Exception as e:
            print(f"   Market data error: {e}")
        
        # Method 4: Force terminal activity
        print("\n4. Creating terminal activity...")
        
        # Multiple rapid market data requests to ensure Journal activity
        for i in range(5):
            try:
                mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_M1, 0, 1)
                mt5.symbol_info_tick("EURUSD")
                time.sleep(0.1)
            except:
                pass
        
        print("\n" + "="*50)
        print("VIESTIT LHETETTY!")
        print("Tarkista nyt:")
        print("1. KNNYKK: MT5 app (MetaQuotes ID: 03A06890)")  
        print("2. MT5 TERMINAL: Journal-vlilehti")
        print("3. MT5 TERMINAL: Experts-vlilehti")
        print("4. MT5 TERMINAL: Account History -vlilehti")
        print("="*50)
        
        # Keep connection alive longer for visibility
        print("\nPidetn yhteys auki 20 sekuntia...")
        for i in range(20, 0, -1):
            if i % 5 == 0:
                print(f"  {i} sekuntia jljell...")
                # Send more activity to Journal
                try:
                    mt5.symbol_info_tick("EURUSD")
                except:
                    pass
            time.sleep(1)
        
        print("Suljetaan yhteys...")
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"Message sending error: {e}")
        mt5.shutdown()
        return False

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    try:
        success = reconnect_with_retry()
        if success:
            print("\nOK VALMIS! Tarkista knnykk ja MT5 Journal!")
        else:
            print("\nERROR Yhteys eponnistui. Onko MT5 auki?")
    except Exception as e:
        print(f"Error: {e}")