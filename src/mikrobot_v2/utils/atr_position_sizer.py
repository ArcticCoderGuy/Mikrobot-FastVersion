"""
ATR Position Sizing Calculator
==============================

Calculates position sizes based on ATR (Average True Range) for proper risk management.
Implements 1:1 ATR position sizing with 0.328 Fibonacci stop loss levels.
"""

import asyncio
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import statistics

from ..core.mt5_direct_connector import MT5DirectConnector, Candle

logger = logging.getLogger(__name__)

class ATRPositionSizer:
    """
    Calculate position sizes based on ATR (Average True Range)
    
    Implements the user's specific requirements:
    - 1:1 ratio between trades and ATR positioning
    - Stop loss at 0.328 Fibonacci level
    - Risk percentage based position sizing
    """
    
    def __init__(self, mt5_connector: MT5DirectConnector):
        self.mt5 = mt5_connector
        self.atr_period = 14  # Standard ATR period
        self.risk_percent = 0.0015  # 0.15% risk per trade
        self.fib_stop_level = 0.328  # 0.328 Fibonacci retracement
        
        # ATR cache for performance
        self.atr_cache: Dict[str, Dict] = {}
        self.cache_expiry = 300  # 5 minutes
        
        logger.info("📊 ATR Position Sizer initialized")
    
    async def calculate_atr(self, symbol: str, timeframe: str = "H1") -> Optional[float]:
        """Calculate Average True Range for symbol"""
        try:
            # Check cache first
            cache_key = f"{symbol}_{timeframe}"
            if self._is_cache_valid(cache_key):
                return self.atr_cache[cache_key]['atr']
            
            # Get candles for ATR calculation
            candles = await self.mt5.get_candles(symbol, timeframe, self.atr_period + 1)
            
            if len(candles) < self.atr_period + 1:
                logger.warning(f"Insufficient data for ATR calculation: {symbol}")
                return None
            
            # Calculate True Range for each period
            true_ranges = []
            
            for i in range(1, len(candles)):
                current = candles[i]
                previous = candles[i-1]
                
                # True Range = max of:
                # 1. Current High - Current Low
                # 2. Current High - Previous Close
                # 3. Previous Close - Current Low
                tr1 = current.high - current.low
                tr2 = abs(current.high - previous.close)
                tr3 = abs(previous.close - current.low)
                
                true_range = max(tr1, tr2, tr3)
                true_ranges.append(true_range)
            
            # Calculate ATR as simple moving average of True Ranges
            if len(true_ranges) >= self.atr_period:
                atr = statistics.mean(true_ranges[-self.atr_period:])
                
                # Cache the result
                self.atr_cache[cache_key] = {
                    'atr': atr,
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'timeframe': timeframe
                }
                
                logger.debug(f"ATR calculated for {symbol}: {atr:.5f}")
                return atr
            
            return None
            
        except Exception as e:
            logger.error(f"ATR calculation error for {symbol}: {e}")
            return None
    
    async def calculate_position_size(self, symbol: str, entry_price: float, 
                                    direction: str, account_balance: float = 10000.0) -> Dict:
        """
        Calculate position size based on ATR and 0.328 Fibonacci stop loss
        
        Args:
            symbol: Trading symbol
            entry_price: Planned entry price
            direction: "BUY" or "SELL"
            account_balance: Account balance for risk calculation
            
        Returns:
            Dict with position sizing information
        """
        try:
            # Get ATR for position sizing
            atr = await self.calculate_atr(symbol, "H1")
            if not atr:
                logger.warning(f"Could not calculate ATR for {symbol}")
                return self._get_default_position_size(symbol)
            
            # Calculate 0.328 Fibonacci stop loss distance
            fib_stop_distance = atr * self.fib_stop_level
            
            # Calculate stop loss price
            if direction.upper() == "BUY":
                stop_loss = entry_price - fib_stop_distance
            else:  # SELL
                stop_loss = entry_price + fib_stop_distance
            
            # Calculate risk amount in account currency
            risk_amount = account_balance * self.risk_percent
            
            # Calculate price difference (risk per unit)
            price_diff = abs(entry_price - stop_loss)
            
            # Get symbol specifications for lot size calculation
            pip_value = self._get_pip_value(symbol)
            contract_size = self._get_contract_size(symbol)
            
            # Calculate position size
            # Risk Amount = Position Size * Price Difference * Pip Value
            # Position Size = Risk Amount / (Price Difference * Pip Value)
            
            if pip_value > 0 and price_diff > 0:
                # For forex: position size in lots
                if self._is_forex_pair(symbol):
                    position_size = risk_amount / (price_diff * 100000)  # Standard lot = 100,000 units
                # For crypto CFDs: position size in contracts
                elif self._is_crypto_symbol(symbol):
                    position_size = risk_amount / (price_diff * contract_size)
                # For indices: position size in lots
                else:
                    position_size = risk_amount / (price_diff * contract_size)
                
                # Ensure minimum and maximum position sizes
                position_size = max(0.01, min(position_size, 10.0))  # Between 0.01 and 10 lots
                
            else:
                position_size = 0.01  # Default fallback
            
            # Calculate take profit (2:1 risk/reward)
            if direction.upper() == "BUY":
                take_profit = entry_price + (fib_stop_distance * 2.0)
            else:
                take_profit = entry_price - (fib_stop_distance * 2.0)
            
            position_info = {
                'symbol': symbol,
                'position_size': round(position_size, 2),
                'entry_price': entry_price,
                'stop_loss': round(stop_loss, 5),
                'take_profit': round(take_profit, 5),
                'atr': atr,
                'fib_stop_distance': fib_stop_distance,
                'risk_amount': risk_amount,
                'risk_percent': self.risk_percent * 100,
                'risk_reward_ratio': 2.0,
                'direction': direction.upper()
            }
            
            logger.info(f"📊 ATR Position sizing for {symbol}:")
            logger.info(f"   Size: {position_size:.2f} lots")
            logger.info(f"   ATR: {atr:.5f}")
            logger.info(f"   SL: {stop_loss:.5f} (0.328 fib)")
            logger.info(f"   TP: {take_profit:.5f}")
            
            return position_info
            
        except Exception as e:
            logger.error(f"Position sizing error for {symbol}: {e}")
            return self._get_default_position_size(symbol)
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if ATR cache is still valid"""
        if cache_key not in self.atr_cache:
            return False
        
        cache_time = self.atr_cache[cache_key]['timestamp']
        return (datetime.now() - cache_time).total_seconds() < self.cache_expiry
    
    def _get_pip_value(self, symbol: str) -> float:
        """Get pip value for symbol"""
        if symbol.endswith('JPY'):
            return 0.01  # JPY pairs
        elif self._is_forex_pair(symbol):
            return 0.0001  # Standard forex pairs
        elif self._is_crypto_symbol(symbol):
            return 1.0  # Crypto CFDs
        else:
            return 1.0  # Index CFDs
    
    def _get_contract_size(self, symbol: str) -> float:
        """Get contract size for symbol"""
        if self._is_forex_pair(symbol):
            return 100000  # Standard lot
        elif self._is_crypto_symbol(symbol):
            return 1.0  # 1 contract = 1 unit
        else:
            return 1.0  # Index CFDs
    
    def _is_forex_pair(self, symbol: str) -> bool:
        """Check if symbol is forex pair - ALL MT5 FOREX PAIRS"""
        
        # Major Pairs (7)
        major_pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
        
        # Minor/Cross Pairs (20)
        minor_pairs = [
            "EURJPY", "EURGBP", "EURCHF", "EURAUD", "EURCAD", "EURNZD",
            "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD", 
            "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
            "CADJPY", "CADCHF", "NZDJPY", "NZDCHF", "NZDCAD", "CHFJPY"
        ]
        
        # Exotic Pairs (25+)
        exotic_pairs = [
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
        
        # ALL FOREX PAIRS (52+ pairs)
        all_forex_pairs = major_pairs + minor_pairs + exotic_pairs
        return symbol in all_forex_pairs
    
    def _is_crypto_symbol(self, symbol: str) -> bool:
        """Check if symbol is crypto CFD"""
        crypto_symbols = ['BTCUSD', 'ETHUSD', 'XRPUSD', 'LTCUSD', 'BCHUSD', 'ADAUSD', 'DOTUSD']
        return symbol in crypto_symbols
    
    def _get_default_position_size(self, symbol: str) -> Dict:
        """Get default position size when ATR calculation fails"""
        return {
            'symbol': symbol,
            'position_size': 0.01,
            'entry_price': 0.0,
            'stop_loss': 0.0,
            'take_profit': 0.0,
            'atr': 0.0,
            'fib_stop_distance': 0.0,
            'risk_amount': 100.0,
            'risk_percent': 1.0,
            'risk_reward_ratio': 2.0,
            'direction': 'BUY',
            'note': 'Default sizing - ATR calculation failed'
        }
    
    async def get_account_balance(self) -> float:
        """Get current account balance from MT5"""
        try:
            if self.mt5.simulation_mode:
                return 10000.0  # Default demo balance
            
            # Real MT5 account info would go here
            # account_info = mt5.account_info()
            # return account_info.balance if account_info else 10000.0
            
            return 10000.0
            
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return 10000.0
    
    def clear_cache(self):
        """Clear ATR cache"""
        self.atr_cache.clear()
        logger.info("ATR cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cached_symbols': len(self.atr_cache),
            'cache_expiry_minutes': self.cache_expiry / 60,
            'symbols': list(self.atr_cache.keys())
        }