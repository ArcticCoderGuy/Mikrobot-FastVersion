"""
Quick MT5 position check
"""
import MetaTrader5 as mt5

print("Checking MT5 positions...")

if mt5.initialize():
    print("MT5 initialized")
    
    # Get current positions without login
    positions = mt5.positions_get()
    if positions:
        print(f"\nFound {len(positions)} positions:")
        for p in positions:
            print(f"- Ticket: {p.ticket}")
            print(f"  Symbol: {p.symbol}")
            print(f"  Volume: {p.volume}")
            print(f"  Profit: {p.profit}")
            print(f"  Comment: {p.comment}")
            print()
    else:
        print("No positions found")
    
    # Check account
    account = mt5.account_info()
    if account:
        print(f"Account: {account.login}")
        print(f"Server: {account.server}")
        print(f"Balance: {account.balance}")
        print(f"Equity: {account.equity}")
    
    mt5.shutdown()
else:
    print("MT5 initialization failed")
    print("Make sure MT5 terminal is running and logged in")