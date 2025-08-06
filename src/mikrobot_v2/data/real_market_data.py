"""
Real Market Data Provider
=========================

Gets REAL market prices from multiple sources
NO SIMULATION - ONLY REAL MARKET DATA
"""

import asyncio
import aiohttp
import ssl
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RealTick:
    """Real market tick data"""
    symbol: str
    bid: float
    ask: float
    price: float
    timestamp: datetime
    source: str

class RealMarketDataProvider:
    """
    Provides REAL market data from multiple APIs
    """
    
    def __init__(self):
        # FREE API Keys - you can get your own for better rate limits
        self.alpha_vantage_key = "demo"  # Free demo key
        self.fixer_key = "demo"  # Free demo key
        
        # Data caching to avoid API rate limits
        self.price_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 30  # 30 seconds cache
        
        # API endpoints
        self.endpoints = {
            'forex': 'https://www.alphavantage.co/query',
            'crypto': 'https://api.coingecko.com/api/v3/simple/price',
            'forex_backup': 'https://api.exchangerate-api.com/v4/latest/USD'
        }
        
        logger.info("📡 Real Market Data Provider initialized")
        logger.info("🚫 NO SIMULATION - REAL PRICES ONLY")
    
    def _is_cached_valid(self, symbol: str) -> bool:
        """Check if cached price is still valid"""
        if symbol not in self.price_cache or symbol not in self.cache_expiry:
            return False
        
        return datetime.now() < self.cache_expiry[symbol]
    
    def _cache_price(self, symbol: str, tick: RealTick):
        """Cache price data"""
        self.price_cache[symbol] = tick
        self.cache_expiry[symbol] = datetime.now() + timedelta(seconds=self.cache_duration)
    
    async def get_forex_price(self, symbol: str) -> Optional[RealTick]:
        """Get real forex price from Yahoo Finance (free, no API key needed)"""
        
        # Check cache first
        if self._is_cached_valid(symbol):
            return self.price_cache[symbol]
        
        # Use Yahoo Finance directly - free and reliable
        return await self.get_yahoo_forex(symbol)
    
    async def get_yahoo_forex(self, symbol: str) -> Optional[RealTick]:
        """Get forex price from Fixer.io API (simpler and more reliable)"""
        
        try:
            # Use free fixer.io API for forex rates
            base_currency = symbol[:3]  # EUR from EURUSD
            target_currency = symbol[3:]  # USD from EURUSD
            
            # SSL context that ignores certificate errors
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Use simple exchange rate API
                url = f"https://api.fixer.io/latest?base={base_currency}&symbols={target_currency}&access_key=demo"
                
                # Fallback to more reliable API
                if True:  # Always use backup for now
                    # Use exchangerate.host (free, no key needed)
                    url = f"https://api.exchangerate.host/latest?base={base_currency}&symbols={target_currency}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'rates' in data and target_currency in data['rates']:
                            price = float(data['rates'][target_currency])
                            
                            # Calculate realistic bid/ask spread
                            if 'JPY' in symbol:
                                spread = price * 0.0001  # 1 pip for JPY pairs
                            else:
                                spread = price * 0.00005  # 0.5 pips for major pairs
                            
                            bid = price - spread/2
                            ask = price + spread/2
                            
                            tick = RealTick(
                                symbol=symbol,
                                bid=round(bid, 5),
                                ask=round(ask, 5),
                                price=round(price, 5),
                                timestamp=datetime.now(),
                                source="ExchangeRate.host"
                            )
                            
                            self._cache_price(symbol, tick)
                            logger.info(f"📡 Real forex price: {symbol} = {price:.5f}")
                            return tick
            
        except Exception as e:
            logger.error(f"Forex API error for {symbol}: {e}")
        
        return None
    
    async def get_forex_backup(self, symbol: str) -> Optional[RealTick]:
        """Backup forex price from exchangerate-api.com"""
        
        try:
            from_currency = symbol[:3]
            to_currency = symbol[3:]
            
            # SSL context that ignores certificate errors
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'rates' in data and to_currency in data['rates']:
                            price = float(data['rates'][to_currency])
                            bid = price * 0.9998
                            ask = price * 1.0002
                            
                            tick = RealTick(
                                symbol=symbol,
                                bid=bid,
                                ask=ask,
                                price=price,
                                timestamp=datetime.now(),
                                source="ExchangeRate-API"
                            )
                            
                            self._cache_price(symbol, tick)
                            logger.info(f"📡 Backup price: {symbol} = {price:.5f}")
                            return tick
            
        except Exception as e:
            logger.error(f"Backup forex API error for {symbol}: {e}")
        
        return None
    
    async def get_crypto_price(self, symbol: str) -> Optional[RealTick]:
        """Get real crypto price from CoinGecko"""
        
        # Check cache first
        if self._is_cached_valid(symbol):
            return self.price_cache[symbol]
        
        try:
            # Convert symbol: BTCUSD -> bitcoin
            crypto_map = {
                'BTCUSD': 'bitcoin',
                'ETHUSD': 'ethereum',
                'BNBUSD': 'binancecoin',
                'XRPUSD': 'ripple',
                'SOLUSD': 'solana',
                'ADAUSD': 'cardano',
                'AVAXUSD': 'avalanche-2',
                'DOTUSD': 'polkadot',
                'LINKUSD': 'chainlink',
                'LTCUSD': 'litecoin'
            }
            
            if symbol not in crypto_map:
                return None
            
            coin_id = crypto_map[symbol]
            
            # SSL context that ignores certificate errors
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                url = f"{self.endpoints['crypto']}"
                params = {
                    'ids': coin_id,
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if coin_id in data and 'usd' in data[coin_id]:
                            price = float(data[coin_id]['usd'])
                            
                            # Crypto spreads are wider
                            spread_percent = 0.001  # 0.1% spread
                            spread = price * spread_percent
                            bid = price - spread/2
                            ask = price + spread/2
                            
                            tick = RealTick(
                                symbol=symbol,
                                bid=bid,
                                ask=ask,
                                price=price,
                                timestamp=datetime.now(),
                                source="CoinGecko"
                            )
                            
                            self._cache_price(symbol, tick)
                            logger.info(f"📡 Real crypto: {symbol} = ${price:,.2f}")
                            return tick
            
        except Exception as e:
            logger.error(f"CoinGecko error for {symbol}: {e}")
        
        return None
    
    async def get_real_price(self, symbol: str) -> Optional[RealTick]:
        """Get real market price - MAIN METHOD"""
        
        logger.info(f"📡 Fetching REAL price for {symbol}")
        
        # Determine if forex or crypto
        crypto_symbols = ['BTCUSD', 'ETHUSD', 'BNBUSD', 'XRPUSD', 'SOLUSD', 
                         'ADAUSD', 'AVAXUSD', 'DOTUSD', 'LINKUSD', 'LTCUSD']
        
        if symbol in crypto_symbols:
            # Crypto prices work perfectly via CoinGecko
            return await self.get_crypto_price(symbol)
        else:
            # Use Alpha Vantage for forex (we have API key now!)
            from .alphavantage_provider import get_alpha_forex_price
            
            alpha_tick = await get_alpha_forex_price(symbol)
            if alpha_tick:
                # Convert to RealTick format
                return RealTick(
                    symbol=symbol,
                    bid=alpha_tick.bid,
                    ask=alpha_tick.ask,
                    price=alpha_tick.price,
                    timestamp=alpha_tick.timestamp,
                    source=alpha_tick.source
                )
            
            logger.warning(f"❌ No forex data for {symbol}")
            return None
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, RealTick]:
        """Get real prices for multiple symbols"""
        
        logger.info(f"📡 Fetching {len(symbols)} real prices...")
        
        tasks = []
        for symbol in symbols:
            tasks.append(self.get_real_price(symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, RealTick):
                prices[symbol] = result
            elif isinstance(result, Exception):
                logger.error(f"Error getting price for {symbol}: {result}")
        
        logger.info(f"📡 Got {len(prices)} real prices successfully")
        return prices
    
    def get_cache_status(self) -> Dict[str, str]:
        """Get cache status for debugging"""
        status = {}
        for symbol, expiry in self.cache_expiry.items():
            if datetime.now() < expiry:
                age = (datetime.now() - (expiry - timedelta(seconds=self.cache_duration))).seconds
                status[symbol] = f"Cached ({age}s old)"
            else:
                status[symbol] = "Expired"
        return status

# Global instance
real_data_provider = RealMarketDataProvider()

# Convenience functions
async def get_real_tick(symbol: str) -> Optional[RealTick]:
    """Get real market tick"""
    return await real_data_provider.get_real_price(symbol)

async def get_real_prices(symbols: List[str]) -> Dict[str, RealTick]:
    """Get real prices for multiple symbols"""
    return await real_data_provider.get_multiple_prices(symbols)