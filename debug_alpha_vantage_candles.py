#!/usr/bin/env python3
"""
Debug Alpha Vantage candlestick data
"""

import asyncio
import aiohttp
import ssl
import json

async def debug_alpha_vantage():
    """Debug Alpha Vantage API response"""
    
    print("🔍 DEBUGGING ALPHA VANTAGE CANDLE DATA")
    print("=" * 40)
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            
            # Try forex intraday
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'FX_INTRADAY',
                'from_symbol': 'EUR',
                'to_symbol': 'USD', 
                'interval': '5min',
                'outputsize': 'compact',
                'apikey': '3M9G2YI3P8TTW72C'
            }
            
            print(f"📡 Testing: {url}")
            print(f"Parameters: {params}")
            
            async with session.get(url, params=params) as response:
                print(f"Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("📊 Response keys:", list(data.keys()))
                    
                    # Check for different possible keys
                    possible_keys = [
                        'Time Series FX (5min)',
                        'Time Series (5min)',
                        'Meta Data',
                        'Error Message',
                        'Note'
                    ]
                    
                    for key in possible_keys:
                        if key in data:
                            print(f"✅ Found key: {key}")
                            if key == 'Time Series FX (5min)':
                                time_series = data[key]
                                print(f"📈 Time series entries: {len(time_series)}")
                                # Show first few entries
                                for i, (timestamp, ohlcv) in enumerate(list(time_series.items())[:3]):
                                    print(f"   {timestamp}: O={ohlcv['1. open']}, H={ohlcv['2. high']}, L={ohlcv['3. low']}, C={ohlcv['4. close']}")
                            elif key in ['Error Message', 'Note']:
                                print(f"❌ {key}: {data[key]}")
                    
                    # If we can't find expected keys, dump everything
                    if 'Time Series FX (5min)' not in data:
                        print("📄 Full response:")
                        print(json.dumps(data, indent=2)[:1000] + "...")
                
                else:
                    text = await response.text()
                    print(f"❌ HTTP Error: {text[:500]}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_alpha_vantage())