#!/usr/bin/env python3
"""
Test realistic market prices
"""

import asyncio
from src.mikrobot_v2.core.mt5_direct_connector import MT5DirectConnector

async def test_prices():
    """Test that prices are now realistic"""
    
    mt5 = MT5DirectConnector()
    await mt5.connect()
    
    symbols_to_test = ["EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD", "EURJPY"]
    
    print("💰 REALISTIC PRICE TEST")
    print("=" * 30)
    
    for symbol in symbols_to_test:
        tick = await mt5.get_current_tick(symbol)
        if tick:
            print(f"{symbol}: {tick.bid:.5f} / {tick.ask:.5f}")
        else:
            print(f"{symbol}: Not available")
    
    print("\n✅ Prices should now look realistic!")
    print(f"EURUSD should be around 1.78375 (your provided price)")

if __name__ == "__main__":
    asyncio.run(test_prices())