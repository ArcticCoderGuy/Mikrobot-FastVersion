#!/usr/bin/env python3
"""
Test FreeForexAPI.com - NO REGISTRATION NEEDED!
100% free forex data
"""

import asyncio
import aiohttp
import ssl
import json

async def test_free_forex_api():
    """Test completely free forex API"""
    
    print("💱 FREEFOREXAPI.COM TEST")
    print("🔥 100% FREE - NO API KEY NEEDED!")
    print("=" * 40)
    
    # Test pairs
    pairs = [
        "EURUSD",
        "GBPUSD", 
        "USDJPY",
        "AUDUSD",
        "USDCHF",
        "USDCAD",
        "NZDUSD",
        "EURJPY",
        "EURGBP",
        "GBPJPY"
    ]
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        
        # Get all pairs at once
        pairs_string = ','.join(pairs)
        url = f"https://www.freeforexapi.com/api/live?pairs={pairs_string}"
        
        print(f"📡 Fetching: {url}\n")
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'rates' in data:
                        print("✅ REAL-TIME FOREX RATES:")
                        print("-" * 40)
                        
                        for pair, rate_data in data['rates'].items():
                            rate = rate_data.get('rate', 0)
                            timestamp = rate_data.get('timestamp', 0)
                            
                            if rate > 0:
                                # Calculate spread
                                if 'JPY' in pair:
                                    spread = rate * 0.0002  # 2 pips
                                else:
                                    spread = rate * 0.00005  # 0.5 pips
                                
                                bid = rate - spread/2
                                ask = rate + spread/2
                                
                                print(f"✅ {pair}: {rate:.5f}")
                                print(f"   Bid: {bid:.5f} | Ask: {ask:.5f}")
                        
                        print("\n📊 Success! Free forex data working!")
                        print("✅ No API key needed")
                        print("📈 Real-time rates")
                    else:
                        print("❌ No rates in response")
                        print(f"Response: {data}")
                
                else:
                    print(f"❌ HTTP {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            print("\n💡 Trying alternative endpoint...")
            
            # Try single pair
            for pair in pairs[:3]:  # Test first 3
                try:
                    url = f"https://www.freeforexapi.com/api/live?pairs={pair}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if 'rates' in data and pair in data['rates']:
                                rate = data['rates'][pair]['rate']
                                print(f"✅ {pair}: {rate:.5f}")
                        else:
                            print(f"❌ {pair}: HTTP {response.status}")
                
                except Exception as e2:
                    print(f"❌ {pair}: {e2}")

if __name__ == "__main__":
    asyncio.run(test_free_forex_api())