"""
Financial Modeling Prep (FMP) Real Market Data
==============================================

Professional grade real-time forex + crypto prices
Free API with excellent coverage
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
class FMPTick:
    """FMP real market tick"""
    symbol: str
    price: float
    bid: float
    ask: float
    change: float
    timestamp: datetime
    source: str = "Financial Modeling Prep"

class FMPDataProvider:
    """
    Real-time market data from Financial Modeling Prep
    Free tier: 250 requests/day
    """
    
    def __init__(self, api_key: str = "demo"):
        self.api_key = api_key  # Use "demo" for testing, get real key for production
        self.base_url = "https://financialmodelingprep.com/api/v3"
        
        # Price cache
        self.price_cache = {}
        self.cache_expiry = {}
        self.cache_duration = 30  # 30 seconds cache
        
        # FMP symbol mapping
        self.forex_symbols = {
            'EURUSD': 'EURUSD',
            'GBPUSD': 'GBPUSD',
            'USDJPY': 'USDJPY', 
            'USDCHF': 'USDCHF',
            'AUDUSD': 'AUDUSD',
            'USDCAD': 'USDCAD',
            'NZDUSD': 'NZDUSD',
            'EURJPY': 'EURJPY',
            'EURGBP': 'EURGBP',
            'GBPJPY': 'GBPJPY',
            'AUDJPY': 'AUDJPY'
        }
        
        self.crypto_symbols = {
            'BTCUSD': 'BTCUSD',
            'ETHUSD': 'ETHUSD', 
            'BNBUSD': 'BNBUSD',
            'ADAUSD': 'ADAUSD',
            'SOLUSD': 'SOLUSD',
            'DOTUSD': 'DOTUSD',
            'LINKUSD': 'LINKUSD',
            'XRPUSD': 'XRPUSD'
        }
        
        logger.info("💼 Financial Modeling Prep initialized")
        logger.info("🔥 Professional market data provider")
    
    def _is_cached_valid(self, symbol: str) -> bool:
        """Check if cached price is valid"""
        if symbol not in self.price_cache or symbol not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[symbol]
    
    def _cache_price(self, symbol: str, tick: FMPTick):
        """Cache price data"""
        self.price_cache[symbol] = tick
        self.cache_expiry[symbol] = datetime.now() + timedelta(seconds=self.cache_duration)
    
    async def get_forex_price(self, symbol: str) -> Optional[FMPTick]:
        """Get real forex price from FMP"""
        
        # Check cache first
        if self._is_cached_valid(symbol):
            return self.price_cache[symbol]
        
        if symbol not in self.forex_symbols:
            return None
        
        fmp_symbol = self.forex_symbols[symbol]
        
        try:
            # SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                
                # FMP forex quote endpoint
                url = f"{self.base_url}/fx/{fmp_symbol}"
                params = {
                    'apikey': self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if isinstance(data, list) and len(data) > 0:
                            quote = data[0]
                            
                            bid = float(quote.get('bid', 0))
                            ask = float(quote.get('ask', 0))
                            price = (bid + ask) / 2 if bid > 0 and ask > 0 else float(quote.get('rate', 0))
                            change = float(quote.get('change', 0))
                            
                            if price > 0:
                                # If no bid/ask, calculate spread
                                if bid == 0 or ask == 0:
                                    if 'JPY' in symbol:
                                        spread = price * 0.0002  # 2 pips
                                    else:
                                        spread = price * 0.00005 # 0.5 pips
                                    bid = price - spread/2
                                    ask = price + spread/2
                                
                                tick = FMPTick(
                                    symbol=symbol,
                                    price=round(price, 5),
                                    bid=round(bid, 5),
                                    ask=round(ask, 5), 
                                    change=change,
                                    timestamp=datetime.now(),
                                    source="FMP Forex"
                                )
                                
                                self._cache_price(symbol, tick)
                                logger.info(f"💼 FMP Forex: {symbol} = {price:.5f}")
                                return tick
                    
                    else:
                        logger.warning(f"FMP Forex API error {response.status} for {symbol}")
            
        except Exception as e:
            logger.error(f"FMP Forex error for {symbol}: {e}")
        
        return None
    
    async def get_crypto_price(self, symbol: str) -> Optional[FMPTick]:
        """Get real crypto price from FMP"""
        
        # Check cache first
        if self._is_cached_valid(symbol):
            return self.price_cache[symbol]
        
        if symbol not in self.crypto_symbols:
            return None
        
        fmp_symbol = self.crypto_symbols[symbol]
        
        try:
            # SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                
                # FMP crypto quote endpoint  
                url = f"{self.base_url}/quote/{fmp_symbol}"
                params = {
                    'apikey': self.api_key
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if isinstance(data, list) and len(data) > 0:
                            quote = data[0]
                            
                            price = float(quote.get('price', 0))
                            change = float(quote.get('change', 0))
                            
                            if price > 0:
                                # Calculate crypto spread (wider than forex)
                                spread = price * 0.001  # 0.1%
                                bid = price - spread/2
                                ask = price + spread/2
                                
                                tick = FMPTick(
                                    symbol=symbol,
                                    price=round(price, 2),
                                    bid=round(bid, 2),
                                    ask=round(ask, 2),
                                    change=change,
                                    timestamp=datetime.now(),
                                    source="FMP Crypto"
                                )
                                
                                self._cache_price(symbol, tick)
                                logger.info(f"💼 FMP Crypto: {symbol} = ${price:,.2f}")
                                return tick
                    
                    else:
                        logger.warning(f"FMP Crypto API error {response.status} for {symbol}")
            
        except Exception as e:
            logger.error(f"FMP Crypto error for {symbol}: {e}")
        
        return None
    
    async def get_real_price(self, symbol: str) -> Optional[FMPTick]:
        """Get real price - main method"""
        
        if symbol in self.crypto_symbols:
            return await self.get_crypto_price(symbol)
        elif symbol in self.forex_symbols:
            return await self.get_forex_price(symbol)
        else:
            logger.warning(f"Symbol not supported by FMP: {symbol}")
            return None
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, FMPTick]:
        """Get multiple prices"""
        
        tasks = []
        for symbol in symbols:
            tasks.append(self.get_real_price(symbol))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, FMPTick):
                prices[symbol] = result
            elif isinstance(result, Exception):
                logger.error(f"Error getting FMP price for {symbol}: {result}")
        
        return prices
    
    def get_supported_symbols(self) -> List[str]:
        """Get supported symbols"""
        return list(self.forex_symbols.keys()) + list(self.crypto_symbols.keys())

# Global FMP provider
fmp_provider = FMPDataProvider()

# Convenience functions  
async def get_fmp_price(symbol: str) -> Optional[FMPTick]:
    """Get real price from FMP"""
    return await fmp_provider.get_real_price(symbol)

async def get_fmp_prices(symbols: List[str]) -> Dict[str, FMPTick]:
    """Get multiple real prices from FMP"""
    return await fmp_provider.get_multiple_prices(symbols)