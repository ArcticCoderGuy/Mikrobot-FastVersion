"""
Indices Data Connector for Market Index Data
Real-time indices data via multiple providers
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone
import logging
import aiohttp
import json

from .data_ingestion_engine import DataConnector
from .data_models import (
    TickData, OHLCVData, AssetType, DataSource, 
    DataQuality
)

logger = logging.getLogger(__name__)


class IndicesDataConnector(DataConnector):
    """
    Multi-provider indices data connector
    
    Supports:
    - Yahoo Finance API for major indices
    - Alpha Vantage for premium data
    - Real-time and historical data
    - Multiple index families (S&P, Dow, NASDAQ, etc.)
    """
    
    def __init__(self, 
                 provider: str = "yahoo",
                 api_key: Optional[str] = None):
        super().__init__(f"indices_{provider}", DataSource.YAHOO_FINANCE)
        
        self.provider = provider.lower()
        self.api_key = api_key
        
        # Provider configuration
        if self.provider == "yahoo":
            self.base_url = "https://query1.finance.yahoo.com"
            self.source = DataSource.YAHOO_FINANCE
        elif self.provider == "alphavantage":
            self.base_url = "https://www.alphavantage.co"
            self.source = DataSource.CUSTOM
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Subscriptions
        self.symbol_subscriptions: Dict[str, bool] = {}
        
        # Performance tracking
        self.request_latencies: List[float] = []
        self.max_latency_samples = 1000
        
        # Polling task for real-time updates
        self.polling_task: Optional[asyncio.Task] = None
        self.polling_interval = 5  # 5 seconds
        
        # Index symbol mapping
        self.index_symbols = {
            # Major US Indices
            'SPX': '^GSPC',    # S&P 500
            'DJI': '^DJI',     # Dow Jones
            'NDX': '^IXIC',    # NASDAQ
            'RUT': '^RUT',     # Russell 2000
            'VIX': '^VIX',     # Volatility Index
            
            # European Indices
            'DAX': '^GDAXI',   # German DAX
            'FTSE': '^FTSE',   # UK FTSE 100
            'CAC': '^FCHI',    # French CAC 40
            'STOXX': '^STOXX50E', # Euro Stoxx 50
            
            # Asian Indices
            'NIKKEI': '^N225', # Nikkei 225
            'HSI': '^HSI',     # Hang Seng
            'ASX': '^AXJO',    # Australian ASX 200
            
            # Commodities
            'GOLD': 'GC=F',    # Gold Futures
            'OIL': 'CL=F',     # Crude Oil
            'SILVER': 'SI=F'   # Silver Futures
        }
    
    async def connect(self) -> bool:
        """Connect to data provider"""
        try:
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            )
            
            # Test connection
            if self.provider == "yahoo":
                test_url = f"{self.base_url}/v8/finance/chart/%5EGSPC"
                async with self.session.get(test_url) as response:
                    if response.status != 200:
                        logger.error(f"Yahoo Finance API test failed: {response.status}")
                        return False
            
            elif self.provider == "alphavantage":
                if not self.api_key:
                    logger.error("Alpha Vantage API key required")
                    return False
                
                test_url = f"{self.base_url}/query"
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': 'SPY',
                    'apikey': self.api_key
                }
                async with self.session.get(test_url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Alpha Vantage API test failed: {response.status}")
                        return False
            
            # Start polling task for subscribed symbols
            self.polling_task = asyncio.create_task(self._polling_loop())
            
            self.is_connected = True
            self.connection_metrics['messages_received'] = 0
            logger.info(f"Connected to {self.provider.title()} indices data")
            
            return True
            
        except Exception as e:
            logger.error(f"Indices connector connection error: {e}")
            self.connection_metrics['last_error'] = str(e)
            self.connection_metrics['connection_failures'] += 1
            await self._cleanup_connection()
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from data provider"""
        try:
            await self._cleanup_connection()
            self.is_connected = False
            logger.info(f"Disconnected from {self.provider.title()}")
            return True
            
        except Exception as e:
            logger.error(f"Indices connector disconnect error: {e}")
            return False
    
    async def _cleanup_connection(self):
        """Clean up connections"""
        # Cancel polling task
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        
        # Close HTTP session
        if self.session:
            await self.session.close()
            self.session = None
    
    async def subscribe_symbol(self, symbol: str, asset_type: AssetType) -> bool:
        """Subscribe to index updates"""
        try:
            if not self.is_connected:
                logger.error(f"Not connected to {self.provider}")
                return False
            
            # Convert symbol to provider format
            provider_symbol = self._convert_symbol(symbol)
            if not provider_symbol:
                logger.error(f"Symbol {symbol} not supported")
                return False
            
            # Test symbol availability
            test_data = await self.get_tick_data(symbol)
            if test_data is None:
                logger.error(f"Symbol {symbol} not available")
                return False
            
            # Add to subscriptions
            self.symbol_subscriptions[symbol] = True
            
            logger.info(f"Subscribed to {symbol} ({provider_symbol})")
            return True
            
        except Exception as e:
            logger.error(f"Symbol subscription error for {symbol}: {e}")
            return False
    
    async def unsubscribe_symbol(self, symbol: str) -> bool:
        """Unsubscribe from symbol updates"""
        try:
            if symbol in self.symbol_subscriptions:
                del self.symbol_subscriptions[symbol]
                
            logger.info(f"Unsubscribed from {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Symbol unsubscription error for {symbol}: {e}")
            return False
    
    async def get_tick_data(self, symbol: str) -> Optional[TickData]:
        """Get latest index data"""
        try:
            if not self.session:
                logger.error("No HTTP session available")
                return None
            
            tick_start = time.perf_counter()
            
            if self.provider == "yahoo":
                tick_data = await self._get_yahoo_tick(symbol)
            elif self.provider == "alphavantage":
                tick_data = await self._get_alphavantage_tick(symbol)
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return None
            
            if tick_data:
                # Calculate latency
                latency_ms = (time.perf_counter() - tick_start) * 1000
                tick_data.latency_ms = latency_ms
                self._track_latency(latency_ms)
                
                # Update quality based on latency
                if latency_ms < 50:
                    tick_data.quality = DataQuality.EXCELLENT
                elif latency_ms < 100:
                    tick_data.quality = DataQuality.GOOD
                elif latency_ms < 200:
                    tick_data.quality = DataQuality.ACCEPTABLE
                else:
                    tick_data.quality = DataQuality.POOR
                
                self.connection_metrics['messages_received'] += 1
                self.update_heartbeat()
            
            return tick_data
            
        except Exception as e:
            logger.error(f"Get tick data error for {symbol}: {e}")
            return None
    
    async def get_ohlcv_data(self, symbol: str, timeframe: str) -> Optional[OHLCVData]:
        """Get OHLCV data for index"""
        try:
            if not self.session:
                logger.error("No HTTP session available")
                return None
            
            ohlcv_start = time.perf_counter()
            
            if self.provider == "yahoo":
                ohlcv_data = await self._get_yahoo_ohlcv(symbol, timeframe)
            elif self.provider == "alphavantage":
                ohlcv_data = await self._get_alphavantage_ohlcv(symbol, timeframe)
            else:
                logger.error(f"Unsupported provider: {self.provider}")
                return None
            
            if ohlcv_data:
                # Calculate latency
                latency_ms = (time.perf_counter() - ohlcv_start) * 1000
                
                # Update quality based on latency
                if latency_ms < 100:
                    ohlcv_data.quality = DataQuality.EXCELLENT
                elif latency_ms < 200:
                    ohlcv_data.quality = DataQuality.GOOD
                elif latency_ms < 500:
                    ohlcv_data.quality = DataQuality.ACCEPTABLE
                else:
                    ohlcv_data.quality = DataQuality.POOR
                
                self.connection_metrics['messages_received'] += 1
                self.update_heartbeat()
            
            return ohlcv_data
            
        except Exception as e:
            logger.error(f"Get OHLCV data error for {symbol} {timeframe}: {e}")
            return None
    
    async def _get_yahoo_tick(self, symbol: str) -> Optional[TickData]:
        """Get tick data from Yahoo Finance"""
        try:
            provider_symbol = self._convert_symbol(symbol)
            if not provider_symbol:
                return None
            
            url = f"{self.base_url}/v8/finance/chart/{provider_symbol}"
            params = {
                'interval': '1m',
                'range': '1d',
                'includePrePost': 'false'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Yahoo Finance API error: {response.status}")
                    return None
                
                data = await response.json()
            
            chart = data['chart']['result'][0]
            meta = chart['meta']
            
            # Get current price
            current_price = meta['regularMarketPrice']
            
            # For indices, we don't have bid/ask, so we estimate
            # Using a small spread based on the index value
            spread_estimate = current_price * 0.0001  # 0.01% spread
            bid = current_price - (spread_estimate / 2)
            ask = current_price + (spread_estimate / 2)
            
            tick_data = TickData(
                timestamp=datetime.fromtimestamp(meta['regularMarketTime'], tz=timezone.utc),
                symbol=symbol,
                bid=bid,
                ask=ask,
                spread=spread_estimate,
                volume=None,  # Not available for indices
                asset_type=AssetType.INDICES,
                source=self.source,
                quality=DataQuality.GOOD
            )
            
            return tick_data
            
        except Exception as e:
            logger.error(f"Yahoo tick data error for {symbol}: {e}")
            return None
    
    async def _get_yahoo_ohlcv(self, symbol: str, timeframe: str) -> Optional[OHLCVData]:
        """Get OHLCV data from Yahoo Finance"""
        try:
            provider_symbol = self._convert_symbol(symbol)
            if not provider_symbol:
                return None
            
            # Convert timeframe to Yahoo format
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1h': '1h',
                '1d': '1d',
                '1w': '1wk',
                '1M': '1mo'
            }
            
            yahoo_interval = interval_map.get(timeframe, '1d')
            
            url = f"{self.base_url}/v8/finance/chart/{provider_symbol}"
            params = {
                'interval': yahoo_interval,
                'range': '2d',  # Get last 2 days to ensure we have recent data
                'includePrePost': 'false'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Yahoo Finance OHLCV API error: {response.status}")
                    return None
                
                data = await response.json()
            
            chart = data['chart']['result'][0]
            indicators = chart['indicators']['quote'][0]
            timestamps = chart['timestamp']
            
            if not timestamps or not indicators['close']:
                logger.error(f"No OHLCV data available for {symbol}")
                return None
            
            # Get the latest complete candle
            latest_index = -1
            while (latest_index >= -len(timestamps) and 
                   (indicators['open'][latest_index] is None or
                    indicators['high'][latest_index] is None or
                    indicators['low'][latest_index] is None or
                    indicators['close'][latest_index] is None)):
                latest_index -= 1
            
            if abs(latest_index) > len(timestamps):
                logger.error(f"No valid OHLCV data for {symbol}")
                return None
            
            ohlcv_data = OHLCVData(
                timestamp=datetime.fromtimestamp(timestamps[latest_index], tz=timezone.utc),
                symbol=symbol,
                open=indicators['open'][latest_index],
                high=indicators['high'][latest_index],
                low=indicators['low'][latest_index],
                close=indicators['close'][latest_index],
                volume=indicators['volume'][latest_index] or 0,
                timeframe=timeframe,
                asset_type=AssetType.INDICES,
                source=self.source,
                quality=DataQuality.GOOD
            )
            
            return ohlcv_data
            
        except Exception as e:
            logger.error(f"Yahoo OHLCV data error for {symbol} {timeframe}: {e}")
            return None
    
    async def _get_alphavantage_tick(self, symbol: str) -> Optional[TickData]:
        """Get tick data from Alpha Vantage"""
        try:
            if not self.api_key:
                logger.error("Alpha Vantage API key required")
                return None
            
            provider_symbol = self._convert_symbol(symbol)
            if not provider_symbol:
                return None
            
            url = f"{self.base_url}/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': provider_symbol,
                'apikey': self.api_key
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Alpha Vantage API error: {response.status}")
                    return None
                
                data = await response.json()
            
            if 'Global Quote' not in data:
                logger.error(f"No quote data for {symbol}")
                return None
            
            quote = data['Global Quote']
            current_price = float(quote['05. price'])
            
            # Estimate spread
            spread_estimate = current_price * 0.0001
            bid = current_price - (spread_estimate / 2)
            ask = current_price + (spread_estimate / 2)
            
            tick_data = TickData(
                timestamp=datetime.now(timezone.utc),  # Alpha Vantage doesn't provide exact timestamp
                symbol=symbol,
                bid=bid,
                ask=ask,
                spread=spread_estimate,
                volume=int(float(quote['06. volume'])) if quote['06. volume'] != '0' else None,
                asset_type=AssetType.INDICES,
                source=self.source,
                quality=DataQuality.GOOD
            )
            
            return tick_data
            
        except Exception as e:
            logger.error(f"Alpha Vantage tick data error for {symbol}: {e}")
            return None
    
    async def _get_alphavantage_ohlcv(self, symbol: str, timeframe: str) -> Optional[OHLCVData]:
        """Get OHLCV data from Alpha Vantage"""
        # Alpha Vantage OHLCV implementation would go here
        # For brevity, returning None - can be implemented based on needs
        logger.warning("Alpha Vantage OHLCV not implemented yet")
        return None
    
    async def _polling_loop(self):
        """Polling loop for subscribed symbols"""
        logger.info("Started indices polling loop")
        
        try:
            while self.is_connected:
                if self.symbol_subscriptions:
                    # Update all subscribed symbols
                    tasks = []
                    for symbol in list(self.symbol_subscriptions.keys()):
                        task = asyncio.create_task(self.get_tick_data(symbol))
                        tasks.append(task)
                    
                    # Process updates in parallel
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Log successful updates
                    successful = sum(1 for r in results if isinstance(r, TickData))
                    if successful > 0:
                        logger.debug(f"Updated {successful}/{len(tasks)} indices")
                
                # Wait before next polling cycle
                await asyncio.sleep(self.polling_interval)
                
        except asyncio.CancelledError:
            logger.info("Polling loop cancelled")
        except Exception as e:
            logger.error(f"Polling loop error: {e}")
    
    def _convert_symbol(self, symbol: str) -> Optional[str]:
        """Convert symbol to provider format"""
        # Check direct mapping
        if symbol in self.index_symbols:
            return self.index_symbols[symbol]
        
        # Check if already in provider format
        if self.provider == "yahoo" and symbol.startswith('^'):
            return symbol
        
        # Try common patterns
        symbol_upper = symbol.upper()
        if symbol_upper in self.index_symbols:
            return self.index_symbols[symbol_upper]
        
        return None
    
    def _track_latency(self, latency_ms: float):
        """Track latency for performance monitoring"""
        self.request_latencies.append(latency_ms)
        
        # Maintain size limit
        if len(self.request_latencies) > self.max_latency_samples:
            self.request_latencies = self.request_latencies[-self.max_latency_samples:]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get connector performance statistics"""
        stats = {
            'is_connected': self.is_connected,
            'provider': self.provider,
            'subscribed_symbols': len(self.symbol_subscriptions),
            'messages_received': self.connection_metrics['messages_received'],
            'polling_interval': self.polling_interval
        }
        
        if self.request_latencies:
            sorted_latencies = sorted(self.request_latencies)
            stats['latency_stats'] = {
                'avg_ms': sum(self.request_latencies) / len(self.request_latencies),
                'min_ms': sorted_latencies[0],
                'max_ms': sorted_latencies[-1],
                'p50_ms': sorted_latencies[len(sorted_latencies) // 2],
                'p95_ms': sorted_latencies[int(len(sorted_latencies) * 0.95)],
                'p99_ms': sorted_latencies[int(len(sorted_latencies) * 0.99)]
            }
        
        return stats
    
    async def get_available_symbols(self) -> List[str]:
        """Get list of available index symbols"""
        return list(self.index_symbols.keys())