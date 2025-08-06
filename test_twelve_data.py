#!/usr/bin/env python3
"""
Test Twelve Data API
Free tier: 800 requests/day
"""

import asyncio
from src.mikrobot_v2.data.twelvedata_provider import (
    get_twelve_price, get_twelve_prices, set_twelve_api_key
)

async def test_twelve_data():
    """Test Twelve Data API"""
    
    print("📊 TWELVE DATA API TEST")
    print("🔥 PROFESSIONAL FOREX + CRYPTO DATA")
    print("=" * 40)
    
    # YOU NEED TO SET YOUR API KEY HERE!
    # Get free key from: https://twelvedata.com/
    API_KEY = "demo"  # REPLACE WITH YOUR KEY
    
    if API_KEY == "demo":
        print("⚠️  DEMO MODE - Limited functionality")
        print("📝 Get free API key from: https://twelvedata.com/")
        print("")
    else:
        set_twelve_api_key(API_KEY)
        print("✅ API key configured")
        print("")
    
    # Test forex pairs
    print("💱 FOREX PAIRS:")
    forex_symbols = ["EURUSD", "GBPUSD", "USDJPY"]
    
    for symbol in forex_symbols:
        tick = await get_twelve_price(symbol)
        if tick:
            print(f"✅ {symbol}: {tick.price:.5f} (Bid: {tick.bid:.5f} / Ask: {tick.ask:.5f})")
            if tick.change_percent != 0:
                print(f"   📈 Change: {tick.change_percent:.2f}%")
        else:
            print(f"❌ {symbol}: No data (need API key)")
    
    # Test crypto
    print("\n🪙 CRYPTO:")
    crypto_symbols = ["BTCUSD", "ETHUSD"]
    
    for symbol in crypto_symbols:
        tick = await get_twelve_price(symbol)
        if tick:
            print(f"✅ {symbol}: ${tick.price:,.2f}")
        else:
            print(f"❌ {symbol}: No data")
    
    # Test batch request
    print("\n📦 BATCH REQUEST (saves API calls):")
    all_symbols = ["EURUSD", "GBPUSD", "BTCUSD"]
    prices = await get_twelve_prices(all_symbols)
    
    for symbol, tick in prices.items():
        if symbol.endswith('USD') and not symbol.startswith('USD'):
            # Crypto
            print(f"✅ {symbol}: ${tick.price:,.2f}")
        else:
            # Forex
            print(f"✅ {symbol}: {tick.price:.5f}")
    
    if not prices:
        print("❌ No batch data - API key required")
    
    print("\n" + "=" * 40)
    if API_KEY == "demo":
        print("📝 TO ENABLE FOREX DATA:")
        print("1. Go to: https://twelvedata.com/")
        print("2. Sign up (free)")
        print("3. Get your API key")
        print("4. Replace 'demo' with your key above")
    else:
        print("✅ Twelve Data API configured!")
        print("📊 You can now get real forex prices!")

if __name__ == "__main__":
    asyncio.run(test_twelve_data())