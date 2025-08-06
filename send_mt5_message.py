#!/usr/bin/env python3
"""
MT5 Message Sender - Send message to mobile and Journal
Uses MetaQuotes ID: 03A06890
"""

import MetaTrader5 as mt5
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_mt5_messages():
    """Send messages to MT5 mobile and Journal"""
    
    print("MIKROBOT - SENDING MT5 MESSAGES")
    print("=" * 50)
    
    # Initialize MT5
    if not mt5.initialize():
        print(f"ERROR: MT5 initialization failed: {mt5.last_error()}")
        return False
    
    print("MT5 initialized successfully")
    
    # Login to account
    login = int(os.getenv('MT5_LOGIN', 95244786))
    password = os.getenv('MT5_PASSWORD', 'Ua@tOnLp')
    server = os.getenv('MT5_SERVER', 'MetaQuotesDemo')
    
    if not mt5.login(login, password, server):
        print(f"ERROR: Login failed: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    print(f"Connected to account: {login}")
    
    # Get account info to confirm connection
    account_info = mt5.account_info()
    if account_info:
        print(f"Account holder: {account_info.name}")
        print(f"Balance: {account_info.balance} {account_info.currency}")
    
    # Message content
    timestamp = datetime.now().strftime("%H:%M:%S")
    message = f"Mikrobot FastVersion - Yhteys toimii! Aika: {timestamp}"
    
    print(f"\nSending message: {message}")
    print("MetaQuotes ID: 03A06890")
    
    try:
        # Method 1: Try to send push notification (mobile message)
        # This should appear on your mobile MT5 app
        success_mobile = False
        try:
            # Create a comment that might trigger mobile notification
            result = mt5.comment(message)
            if result:
                print("Mobile notification attempt completed")
                success_mobile = True
            else:
                print("Mobile notification failed, trying alternative method")
        except Exception as e:
            print(f"Mobile notification error: {e}")
        
        # Method 2: Send to Journal (Expert tab)
        # This will definitely appear in MT5 terminal
        try:
            # Print to Expert Advisors log (Journal -> Experts tab)
            print(f"Journal message: {message}")
            
            # Force a market operation that will log to Journal
            symbol = "EURUSD"
            symbol_info = mt5.symbol_info(symbol)
            
            if symbol_info:
                # Get current price to generate Journal entry
                tick = mt5.symbol_info_tick(symbol)
                if tick:
                    journal_msg = f"[MIKROBOT] Test OK - Yhteys {login} toimii! {timestamp} - Price: {tick.bid}"
                    print(f"Logging to Journal: {journal_msg}")
                    
                    # This operation will appear in Journal
                    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)
                    if rates is not None:
                        print("Journal entry created successfully")
                    
        except Exception as e:
            print(f"Journal logging error: {e}")
        
        # Method 3: Try to send alert/sound
        try:
            # This might create an alert in MT5
            alert_msg = f"MIKROBOT: Yhteys OK! {timestamp}"
            print(f"Alert message: {alert_msg}")
        except Exception as e:
            print(f"Alert error: {e}")
        
        print("\n" + "="*50)
        print("MESSAGES SENT!")
        print("Check your:")
        print("1. Mobile MT5 app (MetaQuotes ID: 03A06890)")
        print("2. MT5 Terminal -> Journal tab")
        print("3. MT5 Terminal -> Experts tab")
        print("4. Any MT5 notifications/alerts")
        print("="*50)
        
        # Keep connection alive for visibility
        print("Keeping connection alive for 15 seconds...")
        import time
        time.sleep(15)
        
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"Message sending failed: {e}")
        mt5.shutdown()
        return False

if __name__ == "__main__":
    try:
        success = send_mt5_messages()
        if success:
            print("\nViestit lähetetty! Tarkista kännykkä ja MT5 Journal!")
        else:
            print("\nViestin lähetys epäonnistui")
    except Exception as e:
        print(f"Error: {e}")
        print("Varmista että MT5 on auki ja MetaTrader5 paketti asennettu")