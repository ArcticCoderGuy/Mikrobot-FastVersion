"""
Simple MT5 test - check what account is logged in
"""
import MetaTrader5 as mt5
import time

print("MT5 Simple Connection Test")
print("-" * 30)

# Give MT5 more time to initialize
print("Initializing MT5...")
mt5.initialize(timeout=10000)
time.sleep(2)  # Wait for initialization

# Try to get terminal info
terminal = mt5.terminal_info()
if terminal:
    print(f"Terminal path: {terminal.path}")
    print(f"Data path: {terminal.data_path}")
    print(f"Connected: {terminal.connected}")
    print(f"Trade allowed: {terminal.trade_allowed}")

# Try to get account info
print("\nChecking account...")
account = mt5.account_info()
if account:
    print(f"Account: {account.login}")
    print(f"Server: {account.server}")
    print(f"Balance: {account.balance}")
    print(f"Equity: {account.equity}")
    print(f"Currency: {account.currency}")
    
    # Check positions
    positions = mt5.positions_get()
    if positions:
        print(f"\nOpen positions: {len(positions)}")
        for p in positions:
            print(f"- {p.symbol}: Ticket {p.ticket}, Volume {p.volume}, P&L {p.profit}")
    else:
        print("\nNo open positions")
else:
    print("No account info available")
    print("MT5 might need manual login first")

# Check last error
error = mt5.last_error()
if error[0] != 1:  # 1 = RES_S_OK
    print(f"\nLast error: {error}")

mt5.shutdown()
print("\nDone!")