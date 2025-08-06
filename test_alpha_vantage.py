#!/usr/bin/env python3
"""
Test Alpha Vantage API with your API key
API Key: 3M9G2YI3P8TTW72C
"""

import asyncio
from src.mikrobot_v2.data.alphavantage_provider import get_alpha_forex_price, get_alpha_forex_prices

async def test_alpha_vantage():
    """Test Alpha Vantage with real API key"""
    
    print("📊 ALPHA VANTAGE API TEST")
    print("✅ API Key: 3M9G2YI3P8TTW72C")
    print("🔥 REAL FOREX DATA")
    print("=" * 40)
    
    # Test major forex pairs
    test_symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF"]
    
    print("💱 Testing individual forex pairs:")
    print("-" * 40)
    
    for symbol in test_symbols:
        print(f"\n📈 Testing {symbol}...")
        
        tick = await get_alpha_forex_price(symbol)
        if tick:
            print(f"✅ {symbol}: {tick.price:.5f}")
            print(f"   Bid: {tick.bid:.5f}")
            print(f"   Ask: {tick.ask:.5f}")
            print(f"   Source: {tick.source}")
            print(f"   Time: {tick.timestamp.strftime('%H:%M:%S')}")
        else:
            print(f"❌ Failed to get {symbol}")
        
        # Small delay to respect rate limits
        await asyncio.sleep(1)
    
    print("\n" + "=" * 40)
    print("📊 Alpha Vantage test complete!")
    print("✅ Your API key is working!")
    print("⚠️ Remember: 25 requests/day limit")
    print("💡 Prices are cached for 3 minutes")

if __name__ == "__main__":
    asyncio.run(test_alpha_vantage())