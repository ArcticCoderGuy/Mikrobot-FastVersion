"""
Data Validation and Quality Monitoring
Ensures data integrity and quality for ML models
"""

import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
import statistics
import logging

from .data_models import (
    TickData, OHLCVData, MarketData, DataQuality, 
    ValidationResult, AssetType
)

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates market data for quality and integrity
    
    Validation checks:
    - Price sanity (no negative prices, reasonable ranges)
    - Timestamp consistency
    - Spread validation
    - Volume validation
    - Data completeness
    """
    
    def __init__(self):
        # Price range limits by asset type (% from last known price)
        self.price_change_limits = {
            AssetType.FOREX: 0.05,      # 5% max change
            AssetType.CRYPTO: 0.20,     # 20% max change
            AssetType.INDICES: 0.10,    # 10% max change
            AssetType.COMMODITIES: 0.15, # 15% max change
            AssetType.STOCKS: 0.15      # 15% max change
        }
        
        # Maximum acceptable spread by asset type (in percentage)
        self.max_spread_percentage = {
            AssetType.FOREX: 0.01,      # 1% max spread
            AssetType.CRYPTO: 0.05,     # 5% max spread
            AssetType.INDICES: 0.02,    # 2% max spread
            AssetType.COMMODITIES: 0.03, # 3% max spread
            AssetType.STOCKS: 0.02      # 2% max spread
        }
        
        # Historical price cache for validation
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.max_history_size = 1000
        
        # Validation statistics
        self.validation_stats = {
            'total_validations': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
    
    async def validate(self, data: MarketData) -> ValidationResult:
        """Validate market data"""
        validation_start = time.perf_counter()
        
        result = ValidationResult(
            is_valid=True,
            quality=DataQuality.EXCELLENT
        )
        
        try:
            # Validate based on data type
            if data.tick_data:
                await self._validate_tick_data(data.tick_data, result)
            
            if data.ohlcv_data:
                await self._validate_ohlcv_data(data.ohlcv_data, result)
            
            # Common validations
            self._validate_timestamp(data.timestamp, result)
            
            # Update validation latency
            result.validation_latency_ms = (time.perf_counter() - validation_start) * 1000
            
            # Update statistics
            self.validation_stats['total_validations'] += 1
            if result.is_valid:
                self.validation_stats['passed'] += 1
            else:
                self.validation_stats['failed'] += 1
            
            if result.warnings:
                self.validation_stats['warnings'] += 1
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            result.add_error(f"Validation exception: {str(e)}")
            result.quality = DataQuality.INVALID
        
        return result
    
    async def _validate_tick_data(self, tick: TickData, result: ValidationResult):
        """Validate tick data"""
        # Price validation
        if tick.bid <= 0 or tick.ask <= 0:
            result.add_error("Invalid price: bid or ask <= 0")
            return
        
        if tick.bid >= tick.ask:
            result.add_error(f"Invalid spread: bid ({tick.bid}) >= ask ({tick.ask})")
            return
        
        # Spread validation
        spread_percentage = (tick.ask - tick.bid) / tick.bid
        max_spread = self.max_spread_percentage.get(tick.asset_type, 0.05)
        
        if spread_percentage > max_spread:
            result.add_warning(f"Large spread: {spread_percentage:.4%} > {max_spread:.4%}")
            if result.quality == DataQuality.EXCELLENT:
                result.quality = DataQuality.GOOD
        
        # Historical price validation
        if not self._validate_price_change(tick.symbol, tick.mid_price, tick.asset_type):
            result.add_warning("Unusual price change detected")
            if result.quality in [DataQuality.EXCELLENT, DataQuality.GOOD]:
                result.quality = DataQuality.ACCEPTABLE
        
        # Latency check
        if tick.latency_ms:
            if tick.latency_ms < 1:
                result.quality = DataQuality.EXCELLENT
            elif tick.latency_ms < 5:
                if result.quality == DataQuality.EXCELLENT:
                    result.quality = DataQuality.GOOD
            elif tick.latency_ms < 10:
                if result.quality in [DataQuality.EXCELLENT, DataQuality.GOOD]:
                    result.quality = DataQuality.ACCEPTABLE
            else:
                result.quality = DataQuality.POOR
                result.add_warning(f"High latency: {tick.latency_ms:.1f}ms")
        
        # Update price history
        self._update_price_history(tick.symbol, tick.mid_price)
    
    async def _validate_ohlcv_data(self, ohlcv: OHLCVData, result: ValidationResult):
        """Validate OHLCV data"""
        # Basic OHLCV validation
        if any(price <= 0 for price in [ohlcv.open, ohlcv.high, ohlcv.low, ohlcv.close]):
            result.add_error("Invalid OHLCV: negative or zero prices")
            return
        
        # OHLCV consistency
        if ohlcv.high < max(ohlcv.open, ohlcv.close):
            result.add_error("Invalid OHLCV: high < max(open, close)")
            return
        
        if ohlcv.low > min(ohlcv.open, ohlcv.close):
            result.add_error("Invalid OHLCV: low > min(open, close)")
            return
        
        if ohlcv.high < ohlcv.low:
            result.add_error("Invalid OHLCV: high < low")
            return
        
        # Volume validation
        if ohlcv.volume < 0:
            result.add_error("Invalid volume: negative value")
            return
        elif ohlcv.volume == 0:
            result.add_warning("Zero volume detected")
        
        # Historical validation
        typical_price = (ohlcv.high + ohlcv.low + ohlcv.close) / 3
        if not self._validate_price_change(ohlcv.symbol, typical_price, ohlcv.asset_type):
            result.add_warning("Unusual OHLCV price change")
            if result.quality in [DataQuality.EXCELLENT, DataQuality.GOOD]:
                result.quality = DataQuality.ACCEPTABLE
        
        # Update price history
        self._update_price_history(ohlcv.symbol, typical_price)
    
    def _validate_timestamp(self, timestamp: datetime, result: ValidationResult):
        """Validate timestamp"""
        now = datetime.now(timezone.utc)
        
        # Check if timestamp is in the future
        if timestamp > now:
            time_diff = (timestamp - now).total_seconds()
            if time_diff > 1:  # Allow 1 second tolerance
                result.add_error(f"Future timestamp: {time_diff:.1f} seconds ahead")
                return
        
        # Check if timestamp is too old
        age_seconds = (now - timestamp).total_seconds()
        if age_seconds > 60:  # More than 1 minute old
            result.add_warning(f"Stale data: {age_seconds:.1f} seconds old")
            if age_seconds > 300:  # More than 5 minutes
                result.quality = DataQuality.POOR
    
    def _validate_price_change(self, symbol: str, price: float, asset_type: AssetType) -> bool:
        """Validate price change against historical data"""
        if symbol not in self.price_history or not self.price_history[symbol]:
            return True  # No history to compare
        
        # Get recent prices
        recent_prices = [p for _, p in self.price_history[symbol][-10:]]
        if not recent_prices:
            return True
        
        # Calculate average recent price
        avg_price = statistics.mean(recent_prices)
        
        # Check price change
        price_change = abs(price - avg_price) / avg_price
        max_change = self.price_change_limits.get(asset_type, 0.10)
        
        return price_change <= max_change
    
    def _update_price_history(self, symbol: str, price: float):
        """Update price history for symbol"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        # Add new price
        self.price_history[symbol].append((datetime.now(timezone.utc), price))
        
        # Maintain size limit
        if len(self.price_history[symbol]) > self.max_history_size:
            self.price_history[symbol] = self.price_history[symbol][-self.max_history_size:]
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        total = self.validation_stats['total_validations']
        if total == 0:
            return self.validation_stats
        
        return {
            **self.validation_stats,
            'pass_rate': self.validation_stats['passed'] / total,
            'fail_rate': self.validation_stats['failed'] / total,
            'warning_rate': self.validation_stats['warnings'] / total
        }


class DataQualityMonitor:
    """
    Monitors data quality over time and generates alerts
    """
    
    def __init__(self, alert_callback: Optional[callable] = None):
        self.alert_callback = alert_callback
        
        # Quality tracking
        self.quality_history: Dict[str, List[Tuple[datetime, DataQuality]]] = {}
        self.quality_thresholds = {
            'excellent_ratio': 0.8,  # Alert if < 80% excellent
            'acceptable_ratio': 0.95,  # Alert if < 95% acceptable or better
            'poor_ratio': 0.05  # Alert if > 5% poor quality
        }
        
        # Anomaly detection
        self.anomaly_counts: Dict[str, int] = {}
        self.anomaly_threshold = 10  # Alert after 10 anomalies
        
        # Performance tracking
        self.latency_history: List[Tuple[datetime, float]] = []
        self.latency_threshold = 10.0  # 10ms threshold
    
    def record_quality(self, symbol: str, quality: DataQuality, timestamp: Optional[datetime] = None):
        """Record quality measurement"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        if symbol not in self.quality_history:
            self.quality_history[symbol] = []
        
        self.quality_history[symbol].append((timestamp, quality))
        
        # Maintain history size
        if len(self.quality_history[symbol]) > 1000:
            self.quality_history[symbol] = self.quality_history[symbol][-1000:]
        
        # Check quality thresholds
        self._check_quality_thresholds(symbol)
    
    def record_latency(self, latency_ms: float, timestamp: Optional[datetime] = None):
        """Record latency measurement"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        self.latency_history.append((timestamp, latency_ms))
        
        # Maintain history size
        if len(self.latency_history) > 10000:
            self.latency_history = self.latency_history[-10000:]
        
        # Check latency threshold
        if latency_ms > self.latency_threshold:
            self._trigger_alert(
                'high_latency',
                f"High latency detected: {latency_ms:.1f}ms",
                {'latency_ms': latency_ms}
            )
    
    def record_anomaly(self, symbol: str, anomaly_type: str, details: Dict[str, Any]):
        """Record data anomaly"""
        key = f"{symbol}:{anomaly_type}"
        
        if key not in self.anomaly_counts:
            self.anomaly_counts[key] = 0
        
        self.anomaly_counts[key] += 1
        
        # Check anomaly threshold
        if self.anomaly_counts[key] >= self.anomaly_threshold:
            self._trigger_alert(
                'anomaly_threshold',
                f"Anomaly threshold exceeded for {symbol} ({anomaly_type})",
                {
                    'symbol': symbol,
                    'anomaly_type': anomaly_type,
                    'count': self.anomaly_counts[key],
                    'details': details
                }
            )
            # Reset count after alert
            self.anomaly_counts[key] = 0
    
    def _check_quality_thresholds(self, symbol: str):
        """Check if quality thresholds are breached"""
        if symbol not in self.quality_history or len(self.quality_history[symbol]) < 100:
            return  # Not enough data
        
        # Get recent quality measurements
        recent_quality = [q for _, q in self.quality_history[symbol][-100:]]
        
        # Calculate ratios
        total = len(recent_quality)
        excellent_count = sum(1 for q in recent_quality if q == DataQuality.EXCELLENT)
        good_count = sum(1 for q in recent_quality if q == DataQuality.GOOD)
        acceptable_count = sum(1 for q in recent_quality if q == DataQuality.ACCEPTABLE)
        poor_count = sum(1 for q in recent_quality if q == DataQuality.POOR)
        
        excellent_ratio = excellent_count / total
        acceptable_or_better_ratio = (excellent_count + good_count + acceptable_count) / total
        poor_ratio = poor_count / total
        
        # Check thresholds
        if excellent_ratio < self.quality_thresholds['excellent_ratio']:
            self._trigger_alert(
                'low_quality',
                f"Low excellent quality ratio for {symbol}: {excellent_ratio:.1%}",
                {
                    'symbol': symbol,
                    'excellent_ratio': excellent_ratio,
                    'threshold': self.quality_thresholds['excellent_ratio']
                }
            )
        
        if acceptable_or_better_ratio < self.quality_thresholds['acceptable_ratio']:
            self._trigger_alert(
                'poor_quality',
                f"Poor overall quality for {symbol}: {acceptable_or_better_ratio:.1%} acceptable or better",
                {
                    'symbol': symbol,
                    'acceptable_ratio': acceptable_or_better_ratio,
                    'threshold': self.quality_thresholds['acceptable_ratio']
                }
            )
        
        if poor_ratio > self.quality_thresholds['poor_ratio']:
            self._trigger_alert(
                'high_poor_quality',
                f"High poor quality ratio for {symbol}: {poor_ratio:.1%}",
                {
                    'symbol': symbol,
                    'poor_ratio': poor_ratio,
                    'threshold': self.quality_thresholds['poor_ratio']
                }
            )
    
    def _trigger_alert(self, alert_type: str, message: str, data: Dict[str, Any]):
        """Trigger quality alert"""
        alert = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': alert_type,
            'message': message,
            'data': data
        }
        
        logger.warning(f"Quality Alert: {message}")
        
        if self.alert_callback:
            try:
                self.alert_callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def get_quality_report(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Generate quality report"""
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'symbols': {}
        }
        
        symbols_to_report = [symbol] if symbol else list(self.quality_history.keys())
        
        for sym in symbols_to_report:
            if sym not in self.quality_history:
                continue
            
            recent_quality = [q for _, q in self.quality_history[sym][-1000:]]
            if not recent_quality:
                continue
            
            total = len(recent_quality)
            quality_counts = {
                'excellent': sum(1 for q in recent_quality if q == DataQuality.EXCELLENT),
                'good': sum(1 for q in recent_quality if q == DataQuality.GOOD),
                'acceptable': sum(1 for q in recent_quality if q == DataQuality.ACCEPTABLE),
                'poor': sum(1 for q in recent_quality if q == DataQuality.POOR),
                'invalid': sum(1 for q in recent_quality if q == DataQuality.INVALID)
            }
            
            report['symbols'][sym] = {
                'total_measurements': total,
                'quality_distribution': {
                    k: f"{(v/total)*100:.1f}%" for k, v in quality_counts.items()
                },
                'quality_counts': quality_counts
            }
        
        # Add latency statistics
        if self.latency_history:
            recent_latencies = [lat for _, lat in self.latency_history[-1000:]]
            report['latency_stats'] = {
                'avg': statistics.mean(recent_latencies),
                'min': min(recent_latencies),
                'max': max(recent_latencies),
                'p50': statistics.median(recent_latencies),
                'p95': statistics.quantiles(recent_latencies, n=20)[18],  # 95th percentile
                'p99': statistics.quantiles(recent_latencies, n=100)[98]  # 99th percentile
            }
        
        return report