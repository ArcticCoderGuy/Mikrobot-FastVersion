"""
Alpha Vantage Real Market Data Provider
========================================

Professional forex data with your API key
Free tier: 25 requests/day, 5 requests/minute
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
class AlphaVantageTick:
    """Alpha Vantage market tick"""
    symbol: str
    price: float
    bid: float
    ask: float
    timestamp: datetime
    source: str = "Alpha Vantage"

class AlphaVantageProvider:
    """
    Real-time forex data from Alpha Vantage
    Your API key: 3M9G2YI3P8TTW72C
    """
    
    def __init__(self):
        self.api_key = "3M9G2YI3P8TTW72C"  # Your personal API key
        self.base_url = "https://www.alphavantage.co/query"
        
        # Cache to minimize API calls (25/day limit)
        self.price_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 180  # 3 minute cache (aggressive due to low limit)
        
        # Rate limiting
        self.last_request_time = None
        self.min_request_interval = 12  # 5 requests per minute = 12 seconds between
        
        logger.info("📊 Alpha Vantage Provider initialized")
        logger.info("✅ API key configured: 3M9G2YI3P8TTW72C")
    
    def _is_cached_valid(self, symbol: str) -> bool:
        """Check if cached price is valid"""
        if symbol not in self.price_cache or symbol not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[symbol]
    
    def _cache_price(self, symbol: str, tick: AlphaVantageTick):
        """Cache price data"""
        self.price_cache[symbol] = tick
        self.cache_expiry[symbol] = datetime.now() + timedelta(seconds=self.cache_duration)
    
    async def _rate_limit(self):
        """Enforce rate limiting"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.min_request_interval:
                wait_time = self.min_request_interval - elapsed
                logger.info(f"⏳ Rate limiting: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self.last_request_time = datetime.now()
    
    async def get_forex_price(self, symbol: str) -> Optional[AlphaVantageTick]:
        """Get real forex price from Alpha Vantage"""
        
        # Check cache first
        if self._is_cached_valid(symbol):
            logger.info(f"📦 Using cached price for {symbol}")
            return self.price_cache[symbol]
        
        # Map symbols to Alpha Vantage format
        from_currency = symbol[:3]
        to_currency = symbol[3:6]
        
        # Rate limiting
        await self._rate_limit()
        
        try:
            # SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                
                # Alpha Vantage FX endpoint
                params = {
                    'function': 'CURRENCY_EXCHANGE_RATE',
                    'from_currency': from_currency,
                    'to_currency': to_currency,
                    'apikey': self.api_key
                }
                
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'Realtime Currency Exchange Rate' in data:
                            rate_data = data['Realtime Currency Exchange Rate']
                            
                            # Get bid and ask
                            bid = float(rate_data.get('8. Bid Price', 0))
                            ask = float(rate_data.get('9. Ask Price', 0))
                            
                            # If no bid/ask, use exchange rate
                            if bid == 0 or ask == 0:
                                exchange_rate = float(rate_data.get('5. Exchange Rate', 0))
                                if exchange_rate > 0:
                                    # Calculate spread
                                    if 'JPY' in symbol:
                                        spread = exchange_rate * 0.0002  # 2 pips
                                    else:
                                        spread = exchange_rate * 0.00005  # 0.5 pips
                                    
                                    bid = exchange_rate - spread/2
                                    ask = exchange_rate + spread/2
                            
                            if bid > 0 and ask > 0:
                                price = (bid + ask) / 2
                                
                                tick = AlphaVantageTick(
                                    symbol=symbol,
                                    price=round(price, 5),
                                    bid=round(bid, 5),
                                    ask=round(ask, 5),
                                    timestamp=datetime.now(),
                                    source="Alpha Vantage"
                                )
                                
                                self._cache_price(symbol, tick)
                                logger.info(f"✅ Alpha Vantage {symbol}: {price:.5f}")
                                return tick
                        
                        elif 'Note' in data:
                            logger.warning(f"⚠️ API limit reached: {data['Note']}")
                        elif 'Error Message' in data:
                            logger.error(f"❌ API error: {data['Error Message']}")
                        else:
                            logger.warning(f"Unexpected response: {data}")
                    
                    else:
                        logger.error(f"HTTP {response.status} for {symbol}")
        
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
        
        return None
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, AlphaVantageTick]:
        """Get multiple forex prices (with rate limiting)"""
        
        results = {}
        
        # Process symbols one by one due to rate limits
        for symbol in symbols:
            # Skip if recently cached
            if self._is_cached_valid(symbol):
                results[symbol] = self.price_cache[symbol]
                continue
            
            # Only fetch forex symbols
            if len(symbol) == 6 and symbol[:3].isalpha() and symbol[3:].isalpha():
                tick = await self.get_forex_price(symbol)
                if tick:
                    results[symbol] = tick
        
        return results
    
    def get_supported_forex(self) -> List[str]:
        """Get supported forex symbols"""
        return [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
            "EURJPY", "EURGBP", "EURCHF", "EURAUD", "EURCAD", "EURNZD",
            "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD",
            "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
            "CADJPY", "CADCHF", "NZDJPY", "NZDCHF", "NZDCAD", "CHFJPY"
        ]

# Global instance with your API key
alpha_provider = AlphaVantageProvider()

# Convenience functions
async def get_alpha_forex_price(symbol: str) -> Optional[AlphaVantageTick]:
    """Get real forex price from Alpha Vantage"""
    return await alpha_provider.get_forex_price(symbol)

async def get_alpha_forex_prices(symbols: List[str]) -> Dict[str, AlphaVantageTick]:
    """Get multiple forex prices from Alpha Vantage"""
    return await alpha_provider.get_multiple_prices(symbols)