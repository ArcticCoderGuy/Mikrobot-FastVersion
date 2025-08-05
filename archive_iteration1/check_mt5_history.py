"""
Check MT5 history and all positions
"""
import MetaTrader5 as mt5
from datetime import datetime, timedelta

mt5.initialize()

print("MT5 Account Status")
print("=" * 50)

account = mt5.account_info()
print(f"Account: {account.login}")
print(f"Server: {account.server}")
print(f"Balance: €{account.balance:.2f}")
print(f"Equity: €{account.equity:.2f}")
print(f"Margin: €{account.margin:.2f}")
print(f"Free margin: €{account.margin_free:.2f}")

# Check ALL positions (including pending orders)
print("\n" + "=" * 50)
print("CHECKING ALL POSITIONS AND ORDERS")
print("=" * 50)

# Get positions
positions = mt5.positions_get()
if positions:
    print(f"\nOpen positions: {len(positions)}")
    for p in positions:
        print(f"\nPosition:")
        print(f"  Ticket: {p.ticket}")
        print(f"  Symbol: {p.symbol}")
        print(f"  Type: {'BUY' if p.type == 0 else 'SELL'}")
        print(f"  Volume: {p.volume}")
        print(f"  Open price: {p.price_open}")
        print(f"  Current price: {p.price_current}")
        print(f"  Profit: €{p.profit:.2f}")
        print(f"  Comment: {p.comment}")
else:
    print("No open positions")

# Get pending orders
orders = mt5.orders_get()
if orders:
    print(f"\nPending orders: {len(orders)}")
    for o in orders:
        print(f"\nOrder:")
        print(f"  Ticket: {o.ticket}")
        print(f"  Symbol: {o.symbol}")
        print(f"  Type: {o.type}")
        print(f"  Volume: {o.volume}")
        print(f"  Price: {o.price_open}")
else:
    print("\nNo pending orders")

# Check recent history
print("\n" + "=" * 50)
print("RECENT TRADING HISTORY (Last 7 days)")
print("=" * 50)

# Get history from last 7 days
date_from = datetime.now() - timedelta(days=7)
date_to = datetime.now()

# Get deals history
deals = mt5.history_deals_get(date_from, date_to)
if deals:
    print(f"\nDeals in history: {len(deals)}")
    # Show last 10 deals
    for d in deals[-10:]:
        if d.ticket > 0:  # Skip balance operations
            print(f"\nDeal:")
            print(f"  Ticket: {d.ticket}")
            print(f"  Order: {d.order}")
            print(f"  Time: {datetime.fromtimestamp(d.time)}")
            print(f"  Symbol: {d.symbol}")
            print(f"  Type: {d.type}")
            print(f"  Volume: {d.volume}")
            print(f"  Price: {d.price}")
            print(f"  Profit: €{d.profit:.2f}")
            print(f"  Comment: {d.comment}")
else:
    print("No deals in history")

# Check if any position with ticket starting with 398
print("\n" + "=" * 50)
print("SEARCHING FOR TICKET 398xxx")
print("=" * 50)

# Check in a different way
all_positions = mt5.positions_total()
print(f"Total positions count: {all_positions}")

# Get symbol info for common pairs
symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
print("\nChecking common symbols:")
for symbol in symbols:
    pos = mt5.positions_get(symbol=symbol)
    if pos:
        print(f"- {symbol}: {len(pos)} positions")
        for p in pos:
            print(f"  Ticket: {p.ticket}")

mt5.shutdown()
print("\nDone!")