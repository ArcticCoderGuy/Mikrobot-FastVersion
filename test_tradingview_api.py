#!/usr/bin/env python3
"""
Test TradingView API for real market prices
Professional grade forex + crypto data
"""

import asyncio
from src.mikrobot_v2.data.tradingview_data import get_tradingview_price, get_tradingview_prices, tradingview_provider

async def test_tradingview():
    """Test TradingView real market data"""
    
    print("📈 TRADINGVIEW API TEST")
    print("🔥 PROFESSIONAL GRADE REAL DATA")
    print("=" * 40)
    
    # Test individual symbols
    test_symbols = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD"]
    
    print("📊 Individual price tests:")
    for symbol in test_symbols:
        print(f"\n📈 Testing {symbol}...")
        
        tick = await get_tradingview_price(symbol)
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
    prices = await get_tradingview_prices(bulk_symbols)
    
    for symbol, tick in prices.items():
        if symbol.endswith('USD') and not symbol.startswith('USD'):
            print(f"✅ {symbol}: ${tick.price:,.2f} from {tick.source}")
        else:
            print(f"✅ {symbol}: {tick.price:.5f} from {tick.source}")
    
    # Show supported symbols
    print(f"\n📋 Supported symbols ({len(tradingview_provider.get_supported_symbols())}):")
    supported = tradingview_provider.get_supported_symbols()
    
    forex_symbols = [s for s in supported if not (s.endswith('USD') and not s.startswith('USD'))]
    crypto_symbols = [s for s in supported if s.endswith('USD') and not s.startswith('USD')]
    
    print(f"💱 Forex ({len(forex_symbols)}): {', '.join(forex_symbols[:10])}...")
    print(f"🪙 Crypto ({len(crypto_symbols)}): {', '.join(crypto_symbols)}")
    
    print(f"\n📊 TradingView test complete!")
    if prices:
        print("🔥 TradingView API WORKING - Professional grade data!")
    else:
        print("❌ TradingView API needs configuration")

if __name__ == "__main__":
    asyncio.run(test_tradingview())