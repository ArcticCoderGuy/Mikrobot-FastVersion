#!/usr/bin/env python3
"""
Test Yahoo Finance direct connection
"""

import requests
import json

def test_yahoo_direct():
    """Test Yahoo Finance API directly"""
    
    symbols = ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]
    
    for symbol in symbols:
        print(f"Testing {symbol}...")
        
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            
            response = requests.get(url, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    
                    if 'meta' in result and 'regularMarketPrice' in result['meta']:
                        price = float(result['meta']['regularMarketPrice'])
                        print(f"✅ {symbol}: {price}")
                    else:
                        print(f"❌ {symbol}: No price in meta")
                        print(f"Available keys: {list(result.get('meta', {}).keys())}")
                else:
                    print(f"❌ {symbol}: No chart result")
            else:
                print(f"❌ {symbol}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {symbol}: Error {e}")

if __name__ == "__main__":
    test_yahoo_direct()