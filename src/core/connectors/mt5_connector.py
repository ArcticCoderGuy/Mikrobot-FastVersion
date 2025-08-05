"""
MetaTrader 5 Connector
Handles all MT5 platform interactions
"""

import MetaTrader5 as mt5
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging
import asyncio
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OrderType(Enum):
    BUY = "ORDER_TYPE_BUY"
    SELL = "ORDER_TYPE_SELL"
    BUY_LIMIT = "ORDER_TYPE_BUY_LIMIT"
    SELL_LIMIT = "ORDER_TYPE_SELL_LIMIT"
    BUY_STOP = "ORDER_TYPE_BUY_STOP"
    SELL_STOP = "ORDER_TYPE_SELL_STOP"


@dataclass
class MT5Config:
    """MT5 connection configuration"""
    path: Optional[str] = None
    login: Optional[int] = None
    password: Optional[str] = None
    server: Optional[str] = None
    timeout: int = 60000
    retry_count: int = 3
    retry_delay: int = 5


class MT5Connector:
    """
    MetaTrader 5 connector following FoxBox principles
    - Deterministic connection management
    - Comprehensive error handling
    - Real-time data streaming
    """
    
    def __init__(self, config: MT5Config):
        self.config = config
        self.is_connected = False
        self.account_info = None
        self.symbols_info = {}
        
        # Connection metrics
        self.metrics = {
            'connection_attempts': 0,
            'successful_orders': 0,
            'failed_orders': 0,
            'total_latency': 0,
            'reconnections': 0
        }
    
    async def connect(self) -> bool:
        """Establish connection to MT5"""
        try:
            self.metrics['connection_attempts'] += 1
            
            # Initialize MT5
            if self.config.path:
                if not mt5.initialize(self.config.path):
                    logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                    return False
            else:
                if not mt5.initialize():
                    logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                    return False
            
            # Login if credentials provided
            if all([self.config.login, self.config.password, self.config.server]):
                authorized = mt5.login(
                    login=self.config.login,
                    password=self.config.password,
                    server=self.config.server,
                    timeout=self.config.timeout
                )
                
                if not authorized:
                    logger.error(f"MT5 login failed: {mt5.last_error()}")
                    mt5.shutdown()
                    return False
            
            # Get account info
            self.account_info = mt5.account_info()._asdict()
            
            # Cache symbol information
            await self._cache_symbols_info()
            
            self.is_connected = True
            logger.info(f"Connected to MT5: {self.account_info['name']} ({self.account_info['login']})")
            
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from MT5"""
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            logger.info("Disconnected from MT5")
    
    async def _cache_symbols_info(self):
        """Cache symbol information for faster access"""
        symbols = mt5.symbols_get()
        if symbols:
            for symbol in symbols:
                info = symbol._asdict()
                self.symbols_info[info['name']] = {
                    'digits': info['digits'],
                    'point': info['point'],
                    'trade_contract_size': info['trade_contract_size'],
                    'volume_min': info['volume_min'],
                    'volume_max': info['volume_max'],
                    'volume_step': info['volume_step'],
                    'trade_mode': info['trade_mode'],
                    'spread': info['spread']
                }
    
    async def ensure_connected(self) -> bool:
        """Ensure connection is active, reconnect if needed"""
        if not self.is_connected or not mt5.terminal_info():
            logger.warning("MT5 connection lost, attempting reconnect...")
            self.metrics['reconnections'] += 1
            return await self.connect()
        return True
    
    async def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol information"""
        if symbol in self.symbols_info:
            return self.symbols_info[symbol]
        
        # Try to get fresh info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info:
            info = symbol_info._asdict()
            self.symbols_info[symbol] = {
                'digits': info['digits'],
                'point': info['point'],
                'trade_contract_size': info['trade_contract_size'],
                'volume_min': info['volume_min'],
                'volume_max': info['volume_max'],
                'volume_step': info['volume_step'],
                'trade_mode': info['trade_mode'],
                'spread': info['spread']
            }
            return self.symbols_info[symbol]
        
        return None
    
    async def get_current_price(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get current bid/ask prices"""
        if not await self.ensure_connected():
            return None
        
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            return {
                'bid': tick.bid,
                'ask': tick.ask,
                'last': tick.last,
                'time': datetime.fromtimestamp(tick.time),
                'volume': tick.volume,
                'spread': tick.ask - tick.bid
            }
        
        return None
    
    async def place_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """Place order on MT5"""
        if not await self.ensure_connected():
            return {'success': False, 'error': 'Not connected to MT5'}
        
        try:
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": order_params['symbol'],
                "volume": order_params['volume'],
                "type": getattr(mt5, order_params['type']),
                "price": order_params.get('price', 0),
                "sl": order_params.get('sl', 0),
                "tp": order_params.get('tp', 0),
                "deviation": order_params.get('deviation', 20),
                "magic": order_params.get('magic', 0),
                "comment": order_params.get('comment', ''),
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.metrics['failed_orders'] += 1
                return {
                    'success': False,
                    'error': f"Order failed: {result.comment}",
                    'error_code': result.retcode,
                    'request': request
                }
            
            self.metrics['successful_orders'] += 1
            
            return {
                'success': True,
                'order_id': result.order,
                'ticket': result.order,
                'fill_price': result.price,
                'volume': result.volume,
                'sl': request['sl'],
                'tp': request['tp'],
                'commission': result.commission,
                'comment': result.comment
            }
            
        except Exception as e:
            logger.error(f"Order placement error: {str(e)}")
            self.metrics['failed_orders'] += 1
            return {'success': False, 'error': str(e)}
    
    async def close_position(self, ticket: int, volume: Optional[float] = None) -> Dict[str, Any]:
        """Close position by ticket"""
        if not await self.ensure_connected():
            return {'success': False, 'error': 'Not connected to MT5'}
        
        try:
            # Get position info
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return {'success': False, 'error': 'Position not found'}
            
            position = position[0]
            symbol = position.symbol
            
            # Determine close parameters
            close_type = mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY
            close_volume = volume or position.volume
            
            # Get current price
            price_info = await self.get_current_price(symbol)
            if not price_info:
                return {'success': False, 'error': 'Cannot get current price'}
            
            close_price = price_info['bid'] if close_type == mt5.ORDER_TYPE_SELL else price_info['ask']
            
            # Prepare close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": close_volume,
                "type": close_type,
                "position": ticket,
                "price": close_price,
                "deviation": 20,
                "magic": position.magic,
                "comment": f"Close #{ticket}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send close order
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'error': f"Close failed: {result.comment}",
                    'error_code': result.retcode
                }
            
            return {
                'success': True,
                'close_price': result.price,
                'close_time': datetime.now(),
                'profit': position.profit,
                'commission': result.commission
            }
            
        except Exception as e:
            logger.error(f"Position close error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_positions(self, symbol: Optional[str] = None, 
                          magic: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get open positions"""
        if not await self.ensure_connected():
            return []
        
        try:
            # Get positions with filters
            if symbol and magic:
                positions = mt5.positions_get(symbol=symbol, magic=magic)
            elif symbol:
                positions = mt5.positions_get(symbol=symbol)
            elif magic:
                positions = mt5.positions_get(magic=magic)
            else:
                positions = mt5.positions_get()
            
            if not positions:
                return []
            
            # Convert to dict format
            result = []
            for pos in positions:
                result.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'magic': pos.magic,
                    'comment': pos.comment,
                    'time': datetime.fromtimestamp(pos.time)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Get positions error: {str(e)}")
            return []
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information"""
        if not await self.ensure_connected():
            return None
        
        try:
            info = mt5.account_info()
            if info:
                return {
                    'login': info.login,
                    'balance': info.balance,
                    'equity': info.equity,
                    'margin': info.margin,
                    'margin_free': info.margin_free,
                    'margin_level': info.margin_level,
                    'profit': info.profit,
                    'credit': info.credit,
                    'leverage': info.leverage,
                    'currency': info.currency,
                    'trade_allowed': info.trade_allowed,
                    'limit_orders': info.limit_orders,
                    'margin_so_mode': info.margin_so_mode,
                    'margin_so_call': info.margin_so_call,
                    'margin_so_so': info.margin_so_so
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Get account info error: {str(e)}")
            return None
    
    async def get_historical_data(self, symbol: str, timeframe: int, 
                                 count: int = 1000) -> Optional[List[Dict[str, Any]]]:
        """Get historical price data"""
        if not await self.ensure_connected():
            return None
        
        try:
            # Get rates
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                return None
            
            # Convert to list of dicts
            result = []
            for rate in rates:
                result.append({
                    'time': datetime.fromtimestamp(rate['time']),
                    'open': rate['open'],
                    'high': rate['high'],
                    'low': rate['low'],
                    'close': rate['close'],
                    'tick_volume': rate['tick_volume'],
                    'spread': rate['spread'],
                    'real_volume': rate['real_volume']
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Get historical data error: {str(e)}")
            return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get connector metrics"""
        total_orders = self.metrics['successful_orders'] + self.metrics['failed_orders']
        success_rate = self.metrics['successful_orders'] / total_orders if total_orders > 0 else 0
        
        return {
            **self.metrics,
            'success_rate': round(success_rate, 3),
            'is_connected': self.is_connected
        }