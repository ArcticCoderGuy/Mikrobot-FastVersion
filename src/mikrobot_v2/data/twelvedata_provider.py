"""
Twelve Data Real Market Provider
=================================

Professional forex + crypto data
FREE tier: 800 requests/day
"""

import asyncio
import aiohttp
import ssl
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TwelveTick:
    """Twelve Data market tick"""
    symbol: str
    price: float
    bid: float
    ask: float
    change: float
    change_percent: float
    timestamp: datetime
    source: str = "Twelve Data"

class TwelveDataProvider:
    """
    Real-time market data from Twelve Data
    Free tier: 800 requests/day
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "demo"  # Need real key
        self.base_url = "https://api.twelvedata.com"
        
        # Cache to minimize API calls
        self.price_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 60  # 1 minute cache
        
        # Symbol mapping
        self.forex_symbols = {
            'EURUSD': 'EUR/USD',
            'GBPUSD': 'GBP/USD',
            'USDJPY': 'USD/JPY',
            'USDCHF': 'USD/CHF',
            'AUDUSD': 'AUD/USD',
            'USDCAD': 'USD/CAD',
            'NZDUSD': 'NZD/USD',
            'EURJPY': 'EUR/JPY',
            'EURGBP': 'EUR/GBP',
            'GBPJPY': 'GBP/JPY',
            'AUDJPY': 'AUD/JPY'
        }
        
        self.crypto_symbols = {
            'BTCUSD': 'BTC/USD',
            'ETHUSD': 'ETH/USD',
            'BNBUSD': 'BNB/USD',
            'XRPUSD': 'XRP/USD',
            'SOLUSD': 'SOL/USD'
        }
        
        logger.info("📊 Twelve Data Provider initialized")
        if api_key:
            logger.info("✅ API key configured")
        else:
            logger.warning("⚠️ No API key - using demo mode")
    
    def _is_cached_valid(self, symbol: str) -> bool:
        """Check if cached price is valid"""
        if symbol not in self.price_cache or symbol not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[symbol]
    
    def _cache_price(self, symbol: str, tick: TwelveTick):
        """Cache price data"""
        self.price_cache[symbol] = tick
        self.cache_expiry[symbol] = datetime.now() + timedelta(seconds=self.cache_duration)
    
    async def get_quote(self, symbol: str) -> Optional[TwelveTick]:
        """Get real-time quote from Twelve Data"""
        
        # Check cache first
        if self._is_cached_valid(symbol):
            return self.price_cache[symbol]
        
        # Map symbol
        twelve_symbol = None
        if symbol in self.forex_symbols:
            twelve_symbol = self.forex_symbols[symbol]
        elif symbol in self.crypto_symbols:
            twelve_symbol = self.crypto_symbols[symbol]
        else:
            logger.warning(f"Symbol not supported: {symbol}")
            return None
        
        try:
            # SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                
                # Twelve Data quote endpoint
                url = f"{self.base_url}/quote"
                params = {
                    'symbol': twelve_symbol,
                    'apikey': self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'price' in data:
                            price = float(data['price'])
                            change = float(data.get('change', 0))
                            change_percent = float(data.get('percent_change', 0))
                            
                            # Calculate spread
                            if 'JPY' in symbol:
                                spread = price * 0.0002  # 2 pips
                            elif symbol in self.crypto_symbols:
                                spread = price * 0.001   # 0.1%
                            else:
                                spread = price * 0.00005 # 0.5 pips
                            
                            bid = price - spread/2
                            ask = price + spread/2
                            
                            tick = TwelveTick(
                                symbol=symbol,
                                price=round(price, 5),
                                bid=round(bid, 5),
                                ask=round(ask, 5),
                                change=change,
                                change_percent=change_percent,
                                timestamp=datetime.now(),
                                source="Twelve Data"
                            )
                            
                            self._cache_price(symbol, tick)
                            logger.info(f"📊 Twelve Data: {symbol} = {price:.5f}")
                            return tick
                        
                        elif 'code' in data:
                            # API error
                            logger.error(f"Twelve Data API error: {data.get('message', 'Unknown error')}")
                    
                    else:
                        logger.warning(f"Twelve Data HTTP error {response.status}")
        
        except Exception as e:
            logger.error(f"Twelve Data error for {symbol}: {e}")
        
        return None
    
    async def get_batch_quotes(self, symbols: List[str]) -> Dict[str, TwelveTick]:
        """Get multiple quotes in one request (saves API calls)"""
        
        # Map symbols
        twelve_symbols = []
        symbol_map = {}
        
        for symbol in symbols:
            if symbol in self.forex_symbols:
                twelve_symbol = self.forex_symbols[symbol]
                twelve_symbols.append(twelve_symbol)
                symbol_map[twelve_symbol] = symbol
            elif symbol in self.crypto_symbols:
                twelve_symbol = self.crypto_symbols[symbol]
                twelve_symbols.append(twelve_symbol)
                symbol_map[twelve_symbol] = symbol
        
        if not twelve_symbols:
            return {}
        
        try:
            # SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                
                # Batch quote endpoint
                url = f"{self.base_url}/quote"
                params = {
                    'symbol': ','.join(twelve_symbols),
                    'apikey': self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = {}
                        
                        # Handle batch response
                        for twelve_symbol, quote_data in data.items():
                            if twelve_symbol in symbol_map and 'price' in quote_data:
                                symbol = symbol_map[twelve_symbol]
                                price = float(quote_data['price'])
                                
                                # Calculate spread
                                if 'JPY' in symbol:
                                    spread = price * 0.0002
                                elif symbol in self.crypto_symbols:
                                    spread = price * 0.001
                                else:
                                    spread = price * 0.00005
                                
                                tick = TwelveTick(
                                    symbol=symbol,
                                    price=round(price, 5),
                                    bid=round(price - spread/2, 5),
                                    ask=round(price + spread/2, 5),
                                    change=float(quote_data.get('change', 0)),
                                    change_percent=float(quote_data.get('percent_change', 0)),
                                    timestamp=datetime.now(),
                                    source="Twelve Data Batch"
                                )
                                
                                results[symbol] = tick
                                self._cache_price(symbol, tick)
                        
                        logger.info(f"📊 Twelve Data batch: {len(results)} quotes retrieved")
                        return results
                    
                    else:
                        logger.warning(f"Twelve Data batch error: {response.status}")
        
        except Exception as e:
            logger.error(f"Twelve Data batch error: {e}")
        
        return {}
    
    async def get_real_price(self, symbol: str) -> Optional[TwelveTick]:
        """Main method to get real price"""
        return await self.get_quote(symbol)
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, TwelveTick]:
        """Get multiple prices efficiently"""
        return await self.get_batch_quotes(symbols)
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported symbols"""
        return list(self.forex_symbols.keys()) + list(self.crypto_symbols.keys())
    
    def set_api_key(self, api_key: str):
        """Set API key after initialization"""
        self.api_key = api_key
        logger.info(f"✅ Twelve Data API key updated")

# Global instance
twelve_provider = TwelveDataProvider()

# Convenience functions
async def get_twelve_price(symbol: str) -> Optional[TwelveTick]:
    """Get real price from Twelve Data"""
    return await twelve_provider.get_real_price(symbol)

async def get_twelve_prices(symbols: List[str]) -> Dict[str, TwelveTick]:
    """Get multiple real prices from Twelve Data"""
    return await twelve_provider.get_multiple_prices(symbols)

def set_twelve_api_key(api_key: str):
    """Set Twelve Data API key"""
    twelve_provider.set_api_key(api_key)