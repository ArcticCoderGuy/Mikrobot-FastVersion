"""
MT5 Direct Connector - No EA Required
=====================================

Direct MT5 connection for autonomous trading without Expert Advisor dependency.
Uses native MT5 Python API for real-time trading operations.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd

# Try to import MetaTrader5 - should work on macOS too
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    print("✅ MetaTrader5 Python library found!")
except ImportError:
    MT5_AVAILABLE = False
    print("❌ MetaTrader5 library not found - using simulation")

logger = logging.getLogger(__name__)

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"

@dataclass
class Tick:
    """Real-time tick data"""
    symbol: str
    bid: float
    ask: float
    time: datetime
    volume: int = 0
    
@dataclass
class Candle:
    """OHLC candle data"""
    symbol: str
    timeframe: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    
@dataclass
class Position:
    """Active position data"""
    ticket: int
    symbol: str
    type: OrderType
    volume: float
    price_open: float
    price_current: float
    profit: float
    swap: float
    comment: str

class MT5DirectConnector:
    """
    Direct MT5 connection manager for autonomous trading
    No EA required - pure Python integration
    """
    
    def __init__(self, login: int = 95244786, password: str = "Ua@tOnLp", server: str = "MetaQuotesDemo"):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
        self.simulation_mode = not MT5_AVAILABLE
        
        # Force real MT5 connection attempt if library is available
        if MT5_AVAILABLE:
            logger.info("🚀 MT5 library available - attempting REAL connection!")
        else:
            logger.info("⚠️ MT5 library not available - simulation mode")
        
        # ALL FOREX PAIRS AVAILABLE IN MT5 + Crypto
        
        # Major Forex Pairs (7)
        self.major_pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
        
        # Minor/Cross Pairs (20)
        self.minor_pairs = [
            "EURJPY", "EURGBP", "EURCHF", "EURAUD", "EURCAD", "EURNZD",
            "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD", 
            "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
            "CADJPY", "CADCHF", "NZDJPY", "NZDCHF", "NZDCAD", "CHFJPY"
        ]
        
        # Exotic Pairs (25+)
        self.exotic_pairs = [
            # USD Exotics
            "USDSEK", "USDNOK", "USDDKK", "USDPLN", "USDHUF", "USDCZK", 
            "USDTRY", "USDZAR", "USDMXN", "USDSGD", "USDHKD", "USDTHB",
            # EUR Exotics  
            "EURSEK", "EURNOK", "EURDKK", "EURPLN", "EURHUF", "EURCZK",
            "EURTRY", "EURZAR", "EURSGD", "EURHKD",
            # GBP Exotics
            "GBPSEK", "GBPNOK", "GBPDKK", "GBPSGD", "GBPHKD",
            # Others
            "SEKJPY", "NOKJPY", "SGDJPY", "HKDJPY"
        ]
        
        # Crypto pairs
        self.crypto_symbols = ["BTCUSD", "ETHUSD"]
        
        # ALL FOREX PAIRS (52+ pairs total!)
        self.forex_symbols = self.major_pairs + self.minor_pairs + self.exotic_pairs
        self.all_symbols = self.forex_symbols + self.crypto_symbols  # 54+ symbols total!
        self.active_symbols = []
        
        # Real-time data storage
        self.current_ticks: Dict[str, Tick] = {}
        self.m5_candles: Dict[str, List[Candle]] = {}
        self.m1_candles: Dict[str, List[Candle]] = {}
        
        logger.info(f"MT5DirectConnector initialized - Simulation: {self.simulation_mode}")
    
    async def connect(self) -> bool:
        """Establish direct connection to MT5"""
        try:
            if self.simulation_mode:
                logger.info("🔄 SIMULATION MODE - MT5 connection simulated")
                await asyncio.sleep(1)  # Simulate connection time
                self.connected = True
                return True
            
            # Real MT5 connection
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"MT5 initialization failed: {error}")
                return False
            
            # Login with credentials
            if not mt5.login(self.login, self.password, self.server):
                error = mt5.last_error()
                logger.error(f"MT5 login failed: {error}")
                mt5.shutdown()
                return False
            
            # Verify account
            account_info = mt5.account_info()
            if not account_info:
                logger.error("Failed to get account info")
                mt5.shutdown()
                return False
            
            self.connected = True
            logger.info(f"✅ Connected to MT5: Account {account_info.login}, Balance: {account_info.balance}")
            
            # Initialize symbols
            await self._initialize_symbols()
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def _initialize_symbols(self):
        """Initialize and validate tradeable symbols"""
        if self.simulation_mode:
            # In simulation, assume all symbols are available
            self.active_symbols = self.all_symbols  # Use ALL forex pairs + crypto (54+ symbols!)
            logger.info(f"✅ Simulation: {len(self.active_symbols)} symbols initialized (ALL FOREX PAIRS)")
            return
        
        # Real MT5 symbol validation
        for symbol in self.all_symbols:
            if mt5.symbol_select(symbol, True):
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info and symbol_info.visible:
                    self.active_symbols.append(symbol)
                    logger.info(f"✅ Symbol activated: {symbol}")
            else:
                logger.warning(f"⚠️ Symbol not available: {symbol}")
        
        logger.info(f"📊 Active symbols: {len(self.active_symbols)}")
    
    async def get_current_tick(self, symbol: str) -> Optional[Tick]:
        """Get current tick for symbol - REAL DATA ONLY"""
        if self.simulation_mode:
            # Use REAL market data instead of simulation
            from ..data.real_market_data import get_real_tick
            
            real_tick = await get_real_tick(symbol)
            if real_tick:
                # Convert to MT5 Tick format
                tick = Tick(
                    symbol=symbol,
                    bid=real_tick.bid,
                    ask=real_tick.ask,
                    time=real_tick.timestamp,
                    volume=100  # Volume not available from free APIs
                )
                self.current_ticks[symbol] = tick
                logger.info(f"📡 REAL {symbol}: {real_tick.bid:.5f}/{real_tick.ask:.5f} from {real_tick.source}")
                return tick
            
            logger.warning(f"🚫 No real data available for {symbol} - skipping")
            return None
        
        else:
            # Real MT5 tick
            tick_data = mt5.symbol_info_tick(symbol)
            if tick_data:
                tick = Tick(
                    symbol=symbol,
                    bid=tick_data.bid,
                    ask=tick_data.ask,
                    time=datetime.fromtimestamp(tick_data.time),
                    volume=tick_data.volume
                )
                self.current_ticks[symbol] = tick
                return tick
        
        return None
    
    async def get_candles(self, symbol: str, timeframe: str, count: int = 100) -> List[Candle]:
        """Get historical candles for pattern analysis"""
        if self.simulation_mode:
            # Generate realistic OHLC simulation data
            candles = []
            base_price = 1.0800 if symbol == "EURUSD" else 45000.0 if symbol == "BTCUSD" else 4500.0
            
            current_time = datetime.now()
            if timeframe == "M5":
                time_delta = timedelta(minutes=5)
            elif timeframe == "M1":
                time_delta = timedelta(minutes=1)
            else:
                time_delta = timedelta(hours=1)
            
            price = base_price
            for i in range(count):
                candle_time = current_time - (time_delta * (count - i))
                
                # Simulate price movement
                import random
                change = random.uniform(-0.002, 0.002)
                price = price * (1 + change)
                
                # Create OHLC
                open_price = price
                high_price = price * (1 + abs(change) * 0.5)
                low_price = price * (1 - abs(change) * 0.5)
                close_price = price * (1 + change * 0.8)
                
                candle = Candle(
                    symbol=symbol,
                    timeframe=timeframe,
                    time=candle_time,
                    open=round(open_price, 5),
                    high=round(high_price, 5),
                    low=round(low_price, 5),
                    close=round(close_price, 5),
                    volume=random.randint(100, 1000)
                )
                candles.append(candle)
            
            return candles
        
        else:
            # Real MT5 candle data
            if timeframe == "M1":
                mt5_timeframe = mt5.TIMEFRAME_M1
            elif timeframe == "M5":
                mt5_timeframe = mt5.TIMEFRAME_M5
            elif timeframe == "H1":
                mt5_timeframe = mt5.TIMEFRAME_H1
            else:
                mt5_timeframe = mt5.TIMEFRAME_M5
            
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            if rates is None:
                return []
            
            candles = []
            for rate in rates:
                candle = Candle(
                    symbol=symbol,
                    timeframe=timeframe,
                    time=datetime.fromtimestamp(rate['time']),
                    open=rate['open'],
                    high=rate['high'],
                    low=rate['low'],
                    close=rate['close'],
                    volume=rate['tick_volume']
                )
                candles.append(candle)
            
            return candles
    
    async def place_order(self, symbol: str, order_type: OrderType, volume: float, 
                         price: float = 0.0, sl: float = 0.0, tp: float = 0.0,
                         comment: str = "MikrobotV2") -> Optional[Dict]:
        """Place trading order"""
        try:
            if self.simulation_mode:
                # Simulate order placement
                logger.info(f"🔄 SIMULATION ORDER: {order_type.value} {volume} {symbol} @ {price}")
                await asyncio.sleep(0.1)  # Simulate execution time
                
                order_result = {
                    "retcode": 10009,  # TRADE_RETCODE_DONE
                    "deal": f"sim_{int(time.time())}",
                    "order": f"ord_{int(time.time())}",
                    "volume": volume,
                    "price": price or (await self.get_current_tick(symbol)).ask,
                    "comment": comment
                }
                
                logger.info(f"✅ SIMULATION ORDER EXECUTED: {order_result['deal']}")
                return order_result
            
            else:
                # Real MT5 order
                if order_type == OrderType.BUY:
                    mt5_type = mt5.ORDER_TYPE_BUY
                elif order_type == OrderType.SELL:
                    mt5_type = mt5.ORDER_TYPE_SELL
                else:
                    mt5_type = mt5.ORDER_TYPE_BUY
                
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": volume,
                    "type": mt5_type,
                    "price": price,
                    "sl": sl,
                    "tp": tp,
                    "comment": comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOK,
                }
                
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"✅ ORDER EXECUTED: {result.deal}")
                    return {
                        "retcode": result.retcode,
                        "deal": result.deal,
                        "order": result.order,
                        "volume": result.volume,
                        "price": result.price,
                        "comment": result.comment
                    }
                else:
                    logger.error(f"❌ ORDER FAILED: {result.retcode if result else 'No response'}")
                    return None
        
        except Exception as e:
            logger.error(f"Order placement error: {e}")
            return None
    
    async def get_positions(self) -> List[Position]:
        """Get current open positions"""
        if self.simulation_mode:
            # Return empty for simulation - could add position tracking
            return []
        
        positions = mt5.positions_get()
        if not positions:
            return []
        
        result = []
        for pos in positions:
            position = Position(
                ticket=pos.ticket,
                symbol=pos.symbol,
                type=OrderType.BUY if pos.type == 0 else OrderType.SELL,
                volume=pos.volume,
                price_open=pos.price_open,
                price_current=pos.price_current,
                profit=pos.profit,
                swap=pos.swap,
                comment=pos.comment
            )
            result.append(position)
        
        return result
    
    async def close_position(self, ticket: int) -> bool:
        """Close position by ticket"""
        if self.simulation_mode:
            logger.info(f"🔄 SIMULATION: Closing position {ticket}")
            return True
        
        # Implementation for real MT5 position closing
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            return False
        
        position = positions[0]
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": close_type,
            "position": ticket,
            "comment": "MikrobotV2_Close"
        }
        
        result = mt5.order_send(request)
        return result and result.retcode == mt5.TRADE_RETCODE_DONE
    
    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            if not self.simulation_mode:
                mt5.shutdown()
            self.connected = False
            logger.info("🔌 MT5 connection closed")