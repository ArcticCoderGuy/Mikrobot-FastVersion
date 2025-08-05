"""
Debug script to check MT5 positions structure
"""
import MetaTrader5 as mt5

# Account details
account_number = 107034605
password = "RcEw_s7w"
server = "Ava-Demo 1-MT5"

print("Checking MT5 positions structure...")

if not mt5.initialize():
    print(f"MT5 initialization failed: {mt5.last_error()}")
    exit()

# Login
authorized = mt5.login(login=account_number, password=password, server=server)
if not authorized:
    print(f"Login failed: {mt5.last_error()}")
    mt5.shutdown()
    exit()

print(f"Connected to account {account_number}")

# Get account info
account_info = mt5.account_info()
print(f"Balance: ${account_info.balance:.2f}")
print(f"Equity: ${account_info.equity:.2f}")
print(f"Free Margin: ${account_info.margin_free:.2f}")

# Get positions
positions = mt5.positions_get()
print(f"\nPositions found: {len(positions) if positions else 0}")

if positions:
    for i, pos in enumerate(positions, 1):
        print(f"\nPosition #{i}:")
        print(f"  Ticket: {pos.ticket}")
        print(f"  Symbol: {pos.symbol}")
        print(f"  Type: {pos.type} ({'BUY' if pos.type == 0 else 'SELL'})")
        print(f"  Volume: {pos.volume}")
        print(f"  Open Price: {pos.price_open}")
        print(f"  Current Price: {getattr(pos, 'price_current', 'N/A')}")
        print(f"  Stop Loss: {pos.sl}")
        print(f"  Take Profit: {pos.tp}")
        print(f"  Profit: ${pos.profit:.2f}")
        print(f"  Swap: ${pos.swap:.2f}")
        print(f"  Comment: {pos.comment}")
        print(f"  Magic: {pos.magic}")
        print(f"  Time: {pos.time}")
        
        # Show all available attributes
        print(f"  All attributes: {dir(pos)}")
else:
    print("No open positions found")

# Check recent history
print("\nRecent closed positions (last 10):")
history = mt5.history_deals_get(position=0, retcode=0)
if history:
    recent_deals = sorted(history, key=lambda x: x.time, reverse=True)[:10]
    for deal in recent_deals:
        print(f"  Deal {deal.ticket}: {deal.symbol} {deal.volume} at {deal.price} on {deal.time}")
else:
    print("No history found")

mt5.shutdown()
print("\nConnection closed")