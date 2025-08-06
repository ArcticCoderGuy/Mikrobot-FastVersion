#!/usr/bin/env python3
"""
Test exchangerate.host API - NO API KEY NEEDED!
Free forex data
"""

import asyncio
import aiohttp
import ssl

async def test_exchangerate_host():
    """Test free forex API"""
    
    print("💱 EXCHANGERATE.HOST TEST")
    print("🔥 FREE FOREX DATA - NO API KEY!")
    print("=" * 40)
    
    # Test pairs
    pairs = [
        ("EUR", "USD"),  # EURUSD
        ("GBP", "USD"),  # GBPUSD
        ("USD", "JPY"),  # USDJPY
        ("AUD", "USD"),  # AUDUSD
        ("USD", "CHF"),  # USDCHF
    ]
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        
        for base, quote in pairs:
            url = f"https://api.exchangerate.host/latest?base={base}&symbols={quote}"
            
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'rates' in data and quote in data['rates']:
                            rate = data['rates'][quote]
                            symbol = f"{base}{quote}"
                            print(f"✅ {symbol}: {rate:.5f}")
                        else:
                            print(f"❌ {base}{quote}: No data")
                    else:
                        print(f"❌ HTTP {response.status} for {base}{quote}")
            
            except Exception as e:
                print(f"❌ Error for {base}{quote}: {e}")
    
    print("\n" + "=" * 40)
    print("📊 exchangerate.host provides free forex data!")
    print("✅ No API key required")
    print("📈 Updates every 60 seconds")

if __name__ == "__main__":
    asyncio.run(test_exchangerate_host())