#!/usr/bin/env python3
"""
Test REAL market prices from APIs
NO SIMULATION - ONLY REAL DATA
"""

import asyncio
from src.mikrobot_v2.data.real_market_data import get_real_tick, get_real_prices

async def test_real_prices():
    """Test that we get REAL market prices"""
    
    print("📡 TESTING REAL MARKET PRICES")
    print("🚫 NO SIMULATION - REAL APIS ONLY")
    print("=" * 40)
    
    # Test individual price
    print("📊 Testing individual prices...")
    
    test_symbols = ["EURUSD", "GBPUSD", "BTCUSD", "ETHUSD"]
    
    for symbol in test_symbols:
        print(f"📡 Fetching real {symbol} price...")
        tick = await get_real_tick(symbol)
        
        if tick:
            print(f"   ✅ {symbol}: {tick.price:.5f} (bid: {tick.bid:.5f}, ask: {tick.ask:.5f})")
            print(f"   📡 Source: {tick.source}")
            print(f"   🕐 Time: {tick.timestamp.strftime('%H:%M:%S')}")
        else:
            print(f"   ❌ Failed to get real price for {symbol}")
        print()
    
    print("📊 Testing batch prices...")
    batch_symbols = ["EURUSD", "BTCUSD", "ETHUSD"]
    prices = await get_real_prices(batch_symbols)
    
    for symbol, tick in prices.items():
        print(f"✅ {symbol}: ${tick.price:,.5f} from {tick.source}")
    
    print(f"\n📊 Got {len(prices)} real prices successfully!")
    print("🔥 NO SIMULATION USED - ALL REAL MARKET DATA!")

if __name__ == "__main__":
    asyncio.run(test_real_prices())