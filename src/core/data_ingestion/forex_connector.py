"""
Forex Data Connector for MT5 Integration
Real-time forex data ingestion with <10ms latency
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone
import logging
import MetaTrader5 as mt5
from threading import Thread, Event
import queue

from data_ingestion_engine import DataConnector
from data_models import (
    TickData, OHLCVData, AssetType, DataSource, 
    DataQuality
)

logger = logging.getLogger(__name__)


class ForexDataConnector(DataConnector):
    """
    MT5-based Forex data connector with real-time streaming
    
    Features:
    - Real-time tick data streaming
    - OHLCV candle data on multiple timeframes
    - Automatic reconnection
    - Sub-10ms latency performance
    """
    
    def __init__(self, 
                 account: Optional[int] = None,
                 password: Optional[str] = None,
                 server: Optional[str] = None):
        super().__init__("forex_mt5", DataSource.MT5)
        
        # MT5 credentials
        self.account = account
        self.password = password
        self.server = server
        
        # Subscriptions and callbacks
        self.symbol_subscriptions: Dict[str, bool] = {}
        self.tick_callbacks: Dict[str, List[Callable]] = {}
        
        # Threading for real-time data
        self.tick_thread: Optional[Thread] = None
        self.tick_queue = queue.Queue(maxsize=10000)
        self.stop_event = Event()
        
        # Performance tracking
        self.tick_latencies: List[float] = []
        self.max_latency_samples = 1000
        
        # MT5 timeframe mapping
        self.timeframe_map = {
            '1m': mt5.TIMEFRAME_M1,
            '5m': mt5.TIMEFRAME_M5,
            '15m': mt5.TIMEFRAME_M15,
            '30m': mt5.TIMEFRAME_M30,
            '1h': mt5.TIMEFRAME_H1,
            '4h': mt5.TIMEFRAME_H4,
            '1d': mt5.TIMEFRAME_D1,
            '1w': mt5.TIMEFRAME_W1,
            '1M': mt5.TIMEFRAME_MN1
        }
    
    async def connect(self) -> bool:
        """Connect to MT5 terminal"""
        try:
            # Initialize MT5
            if not mt5.initialize():
                logger.error("MT5 initialization failed")
                return False
            
            # Login if credentials provided
            if self.account and self.password and self.server:
                authorized = mt5.login(
                    login=self.account,
                    password=self.password,
                    server=self.server
                )
                if not authorized:
                    logger.error(f"MT5 login failed: {mt5.last_error()}")
                    mt5.shutdown()
                    return False
            
            # Verify connection
            terminal_info = mt5.terminal_info()
            if terminal_info is None:
                logger.error("Failed to get terminal info")
                mt5.shutdown()
                return False
            
            # Start tick processing thread
            self.stop_event.clear()
            self.tick_thread = Thread(target=self._tick_processor, daemon=True)
            self.tick_thread.start()
            
            self.is_connected = True
            self.connection_metrics['messages_received'] = 0
            logger.info(f"Connected to MT5: {terminal_info.name} v{terminal_info.build}")
            
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            self.connection_metrics['last_error'] = str(e)
            self.connection_metrics['connection_failures'] += 1
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MT5"""
        try:
            # Stop tick thread
            self.stop_event.set()
            if self.tick_thread and self.tick_thread.is_alive():
                self.tick_thread.join(timeout=5)
            
            # Shutdown MT5
            mt5.shutdown()
            
            self.is_connected = False
            logger.info("Disconnected from MT5")
            return True
            
        except Exception as e:
            logger.error(f"MT5 disconnect error: {e}")
            return False
    
    async def subscribe_symbol(self, symbol: str, asset_type: AssetType) -> bool:
        """Subscribe to symbol updates"""
        try:
            if not self.is_connected:
                logger.error("Not connected to MT5")
                return False
            
            # Check if symbol exists
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found in MT5")
                return False
            
            # Enable symbol in Market Watch
            if not symbol_info.visible:
                if not mt5.symbol_select(symbol, True):
                    logger.error(f"Failed to select symbol {symbol}")
                    return False
            
            # Add to subscriptions
            self.symbol_subscriptions[symbol] = True
            
            logger.info(f"Subscribed to {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Symbol subscription error for {symbol}: {e}")
            return False
    
    async def unsubscribe_symbol(self, symbol: str) -> bool:
        """Unsubscribe from symbol updates"""
        try:
            if symbol in self.symbol_subscriptions:
                del self.symbol_subscriptions[symbol]
                
            # Remove from Market Watch if no other subscriptions
            if not any(s.startswith(symbol) for s in self.symbol_subscriptions):
                mt5.symbol_select(symbol, False)
                
            logger.info(f"Unsubscribed from {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Symbol unsubscription error for {symbol}: {e}")
            return False
    
    async def get_tick_data(self, symbol: str) -> Optional[TickData]:
        """Get latest tick data for symbol"""
        try:
            tick_start = time.perf_counter()
            
            # Get latest tick from MT5
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"No tick data for {symbol}")
                return None
            
            # Calculate latency
            latency_ms = (time.perf_counter() - tick_start) * 1000
            self._track_latency(latency_ms)
            
            # Determine data quality based on latency
            if latency_ms < 1:
                quality = DataQuality.EXCELLENT
            elif latency_ms < 5:
                quality = DataQuality.GOOD
            elif latency_ms < 10:
                quality = DataQuality.ACCEPTABLE
            else:
                quality = DataQuality.POOR
            
            # Create tick data
            tick_data = TickData(
                timestamp=datetime.fromtimestamp(tick.time, tz=timezone.utc),
                symbol=symbol,
                bid=tick.bid,
                ask=tick.ask,
                spread=tick.ask - tick.bid,
                volume=float(tick.volume) if hasattr(tick, 'volume') else None,
                asset_type=AssetType.FOREX,
                source=DataSource.MT5,
                quality=quality,
                latency_ms=latency_ms
            )
            
            self.connection_metrics['messages_received'] += 1
            self.update_heartbeat()
            
            return tick_data
            
        except Exception as e:
            logger.error(f"Get tick data error for {symbol}: {e}")
            return None
    
    async def get_ohlcv_data(self, symbol: str, timeframe: str) -> Optional[OHLCVData]:
        """Get OHLCV data for symbol and timeframe"""
        try:
            ohlcv_start = time.perf_counter()
            
            # Convert timeframe
            mt5_timeframe = self.timeframe_map.get(timeframe)
            if mt5_timeframe is None:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None
            
            # Get latest candle
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, 1)
            if rates is None or len(rates) == 0:
                logger.error(f"No OHLCV data for {symbol} {timeframe}")
                return None
            
            rate = rates[0]
            
            # Calculate latency
            latency_ms = (time.perf_counter() - ohlcv_start) * 1000
            
            # Determine quality
            if latency_ms < 5:
                quality = DataQuality.EXCELLENT
            elif latency_ms < 10:
                quality = DataQuality.GOOD
            elif latency_ms < 20:
                quality = DataQuality.ACCEPTABLE
            else:
                quality = DataQuality.POOR
            
            # Create OHLCV data
            ohlcv_data = OHLCVData(
                timestamp=datetime.fromtimestamp(rate['time'], tz=timezone.utc),
                symbol=symbol,
                open=rate['open'],
                high=rate['high'],
                low=rate['low'],
                close=rate['close'],
                volume=float(rate['tick_volume']),
                timeframe=timeframe,
                asset_type=AssetType.FOREX,
                source=DataSource.MT5,
                quality=quality,
                tick_count=int(rate['real_volume']) if 'real_volume' in rate else None
            )
            
            self.connection_metrics['messages_received'] += 1
            self.update_heartbeat()
            
            return ohlcv_data
            
        except Exception as e:
            logger.error(f"Get OHLCV data error for {symbol} {timeframe}: {e}")
            return None
    
    def _tick_processor(self):
        """Background thread for processing real-time ticks"""
        logger.info("Started tick processor thread")
        
        while not self.stop_event.is_set():
            try:
                # Process subscribed symbols
                for symbol in list(self.symbol_subscriptions.keys()):
                    if self.stop_event.is_set():
                        break
                    
                    # Get tick data synchronously in thread
                    tick_start = time.perf_counter()
                    tick = mt5.symbol_info_tick(symbol)
                    
                    if tick:
                        latency_ms = (time.perf_counter() - tick_start) * 1000
                        
                        # Create tick data
                        tick_data = {
                            'symbol': symbol,
                            'time': tick.time,
                            'bid': tick.bid,
                            'ask': tick.ask,
                            'volume': tick.volume if hasattr(tick, 'volume') else None,
                            'latency_ms': latency_ms
                        }
                        
                        # Add to queue for async processing
                        try:
                            self.tick_queue.put_nowait(tick_data)
                        except queue.Full:
                            logger.warning(f"Tick queue full, dropping tick for {symbol}")
                
                # Brief pause to prevent CPU spinning
                time.sleep(0.001)  # 1ms pause
                
            except Exception as e:
                logger.error(f"Tick processor error: {e}")
                time.sleep(0.1)
        
        logger.info("Tick processor thread stopped")
    
    def get_pending_ticks(self) -> List[Dict[str, Any]]:
        """Get pending ticks from queue"""
        ticks = []
        
        try:
            while not self.tick_queue.empty() and len(ticks) < 100:
                tick = self.tick_queue.get_nowait()
                ticks.append(tick)
        except queue.Empty:
            pass
        
        return ticks
    
    def _track_latency(self, latency_ms: float):
        """Track latency for performance monitoring"""
        self.tick_latencies.append(latency_ms)
        
        # Maintain size limit
        if len(self.tick_latencies) > self.max_latency_samples:
            self.tick_latencies = self.tick_latencies[-self.max_latency_samples:]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get connector performance statistics"""
        stats = {
            'is_connected': self.is_connected,
            'subscribed_symbols': len(self.symbol_subscriptions),
            'messages_received': self.connection_metrics['messages_received'],
            'pending_ticks': self.tick_queue.qsize()
        }
        
        if self.tick_latencies:
            sorted_latencies = sorted(self.tick_latencies)
            stats['latency_stats'] = {
                'avg_ms': sum(self.tick_latencies) / len(self.tick_latencies),
                'min_ms': sorted_latencies[0],
                'max_ms': sorted_latencies[-1],
                'p50_ms': sorted_latencies[len(sorted_latencies) // 2],
                'p95_ms': sorted_latencies[int(len(sorted_latencies) * 0.95)],
                'p99_ms': sorted_latencies[int(len(sorted_latencies) * 0.99)]
            }
        
        return stats
    
    async def get_available_symbols(self) -> List[str]:
        """Get list of available forex symbols"""
        try:
            symbols = mt5.symbols_get()
            if symbols is None:
                return []
            
            # Filter forex symbols
            forex_symbols = [
                s.name for s in symbols 
                if s.path.lower().startswith('forex') or 
                   any(curr in s.name.upper() for curr in ['EUR', 'USD', 'GBP', 'JPY', 'CHF', 'AUD', 'NZD', 'CAD'])
            ]
            
            return forex_symbols
            
        except Exception as e:
            logger.error(f"Error getting available symbols: {e}")
            return []