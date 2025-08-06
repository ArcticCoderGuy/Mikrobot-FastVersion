#!/usr/bin/env python3
"""
Test current crypto prices - verify real data is working
"""

import asyncio
from src.mikrobot_v2.core.mt5_direct_connector import MT5DirectConnector

async def test_crypto_prices():
    """Test current crypto prices"""
    
    print("🪙 TESTING CURRENT CRYPTO PRICES")
    print("🔥 REAL-TIME MARKET DATA CHECK")
    print("=" * 40)
    
    mt5 = MT5DirectConnector()
    await mt5.connect()
    
    crypto_symbols = [
        "BTCUSD", "ETHUSD", "BNBUSD", "XRPUSD", "SOLUSD", 
        "ADAUSD", "AVAXUSD", "DOTUSD", "LINKUSD", "LTCUSD"
    ]
    
    for symbol in crypto_symbols:
        print(f"\n📊 {symbol}:")
        
        tick = await mt5.get_current_tick(symbol)
        if tick:
            price = (tick.bid + tick.ask) / 2
            print(f"   💰 Price: ${price:,.2f}")
            print(f"   📈 Bid: ${tick.bid:,.2f}")  
            print(f"   📉 Ask: ${tick.ask:,.2f}")
            print(f"   ⏰ Time: {tick.time.strftime('%H:%M:%S')}")
            print(f"   ✅ REAL DATA RECEIVED")
        else:
            print(f"   ❌ NO DATA - PROBLEM!")
    
    print(f"\n🔍 Test complete!")

if __name__ == "__main__":
    asyncio.run(test_crypto_prices())