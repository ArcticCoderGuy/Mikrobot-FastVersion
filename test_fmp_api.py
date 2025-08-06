#!/usr/bin/env python3
"""
Test Financial Modeling Prep (FMP) API for real market prices
Professional grade forex + crypto data
"""

import asyncio
from src.mikrobot_v2.data.fmp_data import get_fmp_price, get_fmp_prices, fmp_provider

async def test_fmp_api():
    """Test FMP API for real market data"""
    
    print("💼 FINANCIAL MODELING PREP API TEST")
    print("🔥 PROFESSIONAL GRADE MARKET DATA")
    print("=" * 40)
    
    # Test individual symbols
    test_symbols = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD"]
    
    print("📊 Individual price tests:")
    for symbol in test_symbols:
        print(f"\n💼 Testing {symbol}...")
        
        tick = await get_fmp_price(symbol)
        if tick:
            if symbol.endswith('USD') and not symbol.startswith('USD'):
                # Crypto - show in dollars
                print(f"   ✅ {symbol}: ${tick.price:,.2f}")
                print(f"   💰 Bid: ${tick.bid:,.2f} | Ask: ${tick.ask:,.2f}")
            else:
                # Forex - show with more decimals
                print(f"   ✅ {symbol}: {tick.price:.5f}")
                print(f"   💰 Bid: {tick.bid:.5f} | Ask: {tick.ask:.5f}")
            
            print(f"   📡 Source: {tick.source}")
            print(f"   🕐 Time: {tick.timestamp.strftime('%H:%M:%S')}")
        else:
            print(f"   ❌ Failed to get {symbol}")
    
    # Test bulk retrieval
    print(f"\n📊 Bulk price test:")
    bulk_symbols = ["EURUSD", "BTCUSD", "ETHUSD", "GBPUSD"]
    prices = await get_fmp_prices(bulk_symbols)
    
    for symbol, tick in prices.items():
        if symbol.endswith('USD') and not symbol.startswith('USD'):
            print(f"✅ {symbol}: ${tick.price:,.2f} from {tick.source}")
        else:
            print(f"✅ {symbol}: {tick.price:.5f} from {tick.source}")
    
    # Show supported symbols
    print(f"\n📋 Supported symbols ({len(fmp_provider.get_supported_symbols())}):") 
    supported = fmp_provider.get_supported_symbols()
    
    forex_symbols = [s for s in supported if s in fmp_provider.forex_symbols]
    crypto_symbols = [s for s in supported if s in fmp_provider.crypto_symbols]
    
    print(f"💱 Forex ({len(forex_symbols)}): {', '.join(forex_symbols)}")
    print(f"🪙 Crypto ({len(crypto_symbols)}): {', '.join(crypto_symbols)}")
    
    print(f"\n📊 FMP test complete!")
    if prices:
        print("🔥 FMP API WORKING - Professional grade data!")
        print("💡 For production use, get proper API key from financialmodelingprep.com")
    else:
        print("❌ FMP API needs proper API key for production")

if __name__ == "__main__":
    asyncio.run(test_fmp_api())