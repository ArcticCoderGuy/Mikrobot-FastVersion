"""
TradingView Real Market Data Provider
====================================

Gets REAL market prices from TradingView API
Superior data quality for forex + crypto + stocks
"""

import asyncio
import aiohttp
import ssl
import json
import websockets
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TradingViewTick:
    """TradingView real market tick"""
    symbol: str
    price: float
    bid: float
    ask: float
    volume: float
    timestamp: datetime
    source: str = "TradingView"

class TradingViewDataProvider:
    """
    Real-time market data from TradingView
    FREE and professional grade data
    """
    
    def __init__(self):
        self.session_id = None
        self.chart_session = None
        self.websocket = None
        self.price_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 15  # 15 seconds cache
        
        # TradingView symbol mapping
        self.symbol_mapping = {
            # Forex pairs (TradingView format: FX:EURUSD)
            'EURUSD': 'FX:EURUSD',
            'GBPUSD': 'FX:GBPUSD', 
            'USDJPY': 'FX:USDJPY',
            'USDCHF': 'FX:USDCHF',
            'AUDUSD': 'FX:AUDUSD',
            'USDCAD': 'FX:USDCAD',
            'NZDUSD': 'FX:NZDUSD',
            'EURJPY': 'FX:EURJPY',
            'EURGBP': 'FX:EURGBP',
            'GBPJPY': 'FX:GBPJPY',
            'AUDJPY': 'FX:AUDJPY',
            
            # Crypto (TradingView format: BINANCE:BTCUSDT)
            'BTCUSD': 'BINANCE:BTCUSDT',
            'ETHUSD': 'BINANCE:ETHUSDT', 
            'BNBUSD': 'BINANCE:BNBUSDT',
            'XRPUSD': 'BINANCE:XRPUSDT',
            'SOLUSD': 'BINANCE:SOLUSDT',
            'ADAUSD': 'BINANCE:ADAUSDT',
            'AVAXUSD': 'BINANCE:AVAXUSDT',
            'DOTUSD': 'BINANCE:DOTUSDT',
            'LINKUSD': 'BINANCE:LINKUSDT',
            'LTCUSD': 'BINANCE:LTCUSDT'
        }
        
        logger.info("📈 TradingView Data Provider initialized")
        logger.info("🔥 Professional grade real-time data")
    
    def _generate_session_id(self) -> str:
        """Generate TradingView session ID"""
        import random
        import string
        return 'qs_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    
    def _is_cached_valid(self, symbol: str) -> bool:
        """Check if cached price is valid"""
        if symbol not in self.price_cache or symbol not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[symbol]
    
    def _cache_price(self, symbol: str, tick: TradingViewTick):
        """Cache price data"""
        self.price_cache[symbol] = tick
        self.cache_expiry[symbol] = datetime.now() + timedelta(seconds=self.cache_duration)
    
    async def get_quote_data(self, symbol: str) -> Optional[TradingViewTick]:
        """Get real-time quote from TradingView REST API"""
        
        # Check cache first
        if self._is_cached_valid(symbol):
            return self.price_cache[symbol]
        
        if symbol not in self.symbol_mapping:
            logger.warning(f"Symbol not supported: {symbol}")
            return None
        
        tv_symbol = self.symbol_mapping[symbol]
        
        try:
            # SSL context that ignores certificate errors
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                
                # Use simpler TradingView public API
                url = f"https://symbol-search.tradingview.com/symbol_search/"
                params = {
                    'text': tv_symbol,
                    'exchange': '',
                    'type': ''
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Referer': 'https://www.tradingview.com/',
                    'Origin': 'https://www.tradingview.com'
                }
                
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'd' in data and len(data['d']) > 0:
                            quote = data['d'][0]
                            
                            # Extract price data
                            bid = quote.get('bid', 0)
                            ask = quote.get('ask', 0) 
                            last_price = quote.get('last_price', 0)
                            volume = quote.get('volume', 0)
                            
                            # Use last_price as main price, calculate bid/ask if missing
                            price = last_price if last_price > 0 else (bid + ask) / 2 if bid > 0 and ask > 0 else 0
                            
                            if price > 0:
                                # Calculate spread if bid/ask not provided
                                if bid == 0 or ask == 0:
                                    if 'JPY' in symbol:
                                        spread = price * 0.0002  # 2 pips
                                    elif symbol.endswith('USD') and not symbol.startswith('USD'):  # Crypto
                                        spread = price * 0.001   # 0.1% 
                                    else:  # Forex
                                        spread = price * 0.00005 # 0.5 pips
                                    
                                    bid = price - spread/2
                                    ask = price + spread/2
                                
                                tick = TradingViewTick(
                                    symbol=symbol,
                                    price=round(price, 5),
                                    bid=round(bid, 5), 
                                    ask=round(ask, 5),
                                    volume=volume,
                                    timestamp=datetime.now(),
                                    source="TradingView"
                                )
                                
                                self._cache_price(symbol, tick)
                                logger.info(f"📈 TradingView: {symbol} = {price:.5f}")
                                return tick
                    else:
                        logger.warning(f"TradingView API error {response.status} for {symbol}")
            
        except Exception as e:
            logger.error(f"TradingView API error for {symbol}: {e}")
        
        return None
    
    async def get_screener_data(self, symbols: List[str]) -> Dict[str, TradingViewTick]:
        """Get multiple quotes using TradingView screener (faster for bulk)"""
        
        # Map symbols to TradingView format
        tv_symbols = []
        symbol_map = {}
        
        for symbol in symbols:
            if symbol in self.symbol_mapping:
                tv_symbol = self.symbol_mapping[symbol]
                tv_symbols.append(tv_symbol)
                symbol_map[tv_symbol] = symbol
        
        if not tv_symbols:
            return {}
        
        try:
            # SSL context that ignores certificate errors
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                
                # TradingView screener API
                url = "https://scanner.tradingview.com/crypto/scan"  # or "forex/scan"
                
                # Screener request payload
                payload = {
                    "filter": [
                        {"left": "name", "operation": "in_range", "right": tv_symbols}
                    ],
                    "columns": ["name", "bid", "ask", "last", "volume", "change", "change_percent"],
                    "sort": {"sortBy": "name", "sortOrder": "asc"},
                    "range": [0, len(tv_symbols)]
                }
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Content-Type': 'application/json',
                    'Referer': 'https://www.tradingview.com/',
                    'Origin': 'https://www.tradingview.com'
                }
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = {}
                        
                        if 'data' in data:
                            for row in data['data']:
                                if len(row['d']) >= 4:  # name, bid, ask, last
                                    tv_symbol = row['d'][0]
                                    bid = row['d'][1] or 0
                                    ask = row['d'][2] or 0
                                    last = row['d'][3] or 0
                                    volume = row['d'][4] if len(row['d']) > 4 else 0
                                    
                                    if tv_symbol in symbol_map:
                                        symbol = symbol_map[tv_symbol]
                                        price = last if last > 0 else (bid + ask) / 2 if bid > 0 and ask > 0 else 0
                                        
                                        if price > 0:
                                            tick = TradingViewTick(
                                                symbol=symbol,
                                                price=round(price, 5),
                                                bid=round(bid, 5) if bid > 0 else round(price * 0.9999, 5),
                                                ask=round(ask, 5) if ask > 0 else round(price * 1.0001, 5),
                                                volume=volume,
                                                timestamp=datetime.now(),
                                                source="TradingView Screener"
                                            )
                                            
                                            results[symbol] = tick
                                            self._cache_price(symbol, tick)
                        
                        logger.info(f"📈 TradingView screener: {len(results)} symbols retrieved")
                        return results
                    
                    else:
                        logger.warning(f"TradingView screener error: {response.status}")
            
        except Exception as e:
            logger.error(f"TradingView screener error: {e}")
        
        return {}
    
    async def get_real_price(self, symbol: str) -> Optional[TradingViewTick]:
        """Main method to get real price from TradingView"""
        return await self.get_quote_data(symbol)
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, TradingViewTick]:
        """Get multiple real prices efficiently"""
        return await self.get_screener_data(symbols)
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported symbols"""
        return list(self.symbol_mapping.keys())
    
    def is_symbol_supported(self, symbol: str) -> bool:
        """Check if symbol is supported"""
        return symbol in self.symbol_mapping

# Global TradingView provider instance
tradingview_provider = TradingViewDataProvider()

# Convenience functions
async def get_tradingview_price(symbol: str) -> Optional[TradingViewTick]:
    """Get real price from TradingView"""
    return await tradingview_provider.get_real_price(symbol)

async def get_tradingview_prices(symbols: List[str]) -> Dict[str, TradingViewTick]:
    """Get multiple real prices from TradingView"""
    return await tradingview_provider.get_multiple_prices(symbols)