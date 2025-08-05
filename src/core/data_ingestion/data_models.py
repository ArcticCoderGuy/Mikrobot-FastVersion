"""
Data Models for Real-Time Market Data Ingestion
Standardized data structures for multi-asset trading data
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid


class AssetType(Enum):
    """Asset type classification"""
    FOREX = "forex"
    CRYPTO = "crypto"
    INDICES = "indices"
    COMMODITIES = "commodities"
    STOCKS = "stocks"


class DataSource(Enum):
    """Data source providers"""
    MT5 = "metatrader5"
    BINANCE = "binance"
    COINBASE = "coinbase"
    ALPACA = "alpaca"
    YAHOO_FINANCE = "yahoo_finance"
    CUSTOM = "custom"


class DataQuality(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"    # <1ms latency, 100% accuracy
    GOOD = "good"             # <5ms latency, >99.9% accuracy  
    ACCEPTABLE = "acceptable"  # <10ms latency, >99% accuracy
    POOR = "poor"             # >10ms latency, <99% accuracy
    INVALID = "invalid"       # Corrupted or missing data


@dataclass
class TickData:
    """Real-time tick data structure"""
    timestamp: datetime
    symbol: str
    bid: float
    ask: float
    spread: float
    volume: Optional[float] = None
    asset_type: AssetType = AssetType.FOREX
    source: DataSource = DataSource.MT5
    quality: DataQuality = DataQuality.GOOD
    latency_ms: Optional[float] = None
    sequence_number: Optional[int] = None
    
    def __post_init__(self):
        """Calculate derived fields"""
        if self.spread is None and self.bid and self.ask:
            self.spread = self.ask - self.bid
        
        # Ensure UTC timezone
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
    
    @property
    def mid_price(self) -> float:
        """Calculate mid price"""
        return (self.bid + self.ask) / 2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'bid': self.bid,
            'ask': self.ask,
            'spread': self.spread,
            'mid_price': self.mid_price,
            'volume': self.volume,
            'asset_type': self.asset_type.value,
            'source': self.source.value,
            'quality': self.quality.value,
            'latency_ms': self.latency_ms,
            'sequence_number': self.sequence_number
        }


@dataclass  
class OHLCVData:
    """OHLCV candle data structure"""
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str  # 1m, 5m, 15m, 1h, 4h, 1d
    asset_type: AssetType = AssetType.FOREX
    source: DataSource = DataSource.MT5
    quality: DataQuality = DataQuality.GOOD
    tick_count: Optional[int] = None
    vwap: Optional[float] = None
    
    def __post_init__(self):
        """Calculate derived fields"""
        # Ensure UTC timezone
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
        
        # Calculate VWAP if not provided and volume > 0
        if self.vwap is None and self.volume > 0:
            self.vwap = (self.high + self.low + self.close) / 3
    
    @property
    def range_pips(self) -> float:
        """Calculate range in pips"""
        pip_value = self._get_pip_value()
        return (self.high - self.low) / pip_value
    
    @property
    def body_pips(self) -> float:
        """Calculate candle body in pips"""
        pip_value = self._get_pip_value()
        return abs(self.close - self.open) / pip_value
    
    def _get_pip_value(self) -> float:
        """Get pip value for symbol"""
        if 'JPY' in self.symbol.upper():
            return 0.01
        elif self.asset_type == AssetType.CRYPTO:
            if 'BTC' in self.symbol.upper():
                return 1.0
            else:
                return 0.01
        else:
            return 0.0001  # Standard forex
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'timeframe': self.timeframe,
            'asset_type': self.asset_type.value,
            'source': self.source.value,
            'quality': self.quality.value,
            'tick_count': self.tick_count,
            'vwap': self.vwap,
            'range_pips': self.range_pips,
            'body_pips': self.body_pips
        }


@dataclass
class MarketData:
    """Unified market data container"""
    data_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    symbol: str = ""
    asset_type: AssetType = AssetType.FOREX
    source: DataSource = DataSource.MT5
    
    # Data containers
    tick_data: Optional[TickData] = None
    ohlcv_data: Optional[OHLCVData] = None
    
    # Metadata
    quality: DataQuality = DataQuality.GOOD
    processing_latency_ms: Optional[float] = None
    validation_passed: bool = True
    
    def __post_init__(self):
        """Ensure timestamp consistency"""
        if self.timestamp.tzinfo is None:
            self.timestamp = self.timestamp.replace(tzinfo=timezone.utc)
    
    @property
    def current_price(self) -> Optional[float]:
        """Get current price from available data"""
        if self.tick_data:
            return self.tick_data.mid_price
        elif self.ohlcv_data:
            return self.ohlcv_data.close
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'data_id': self.data_id,
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'asset_type': self.asset_type.value,
            'source': self.source.value,
            'current_price': self.current_price,
            'tick_data': self.tick_data.to_dict() if self.tick_data else None,
            'ohlcv_data': self.ohlcv_data.to_dict() if self.ohlcv_data else None,
            'quality': self.quality.value,
            'processing_latency_ms': self.processing_latency_ms,
            'validation_passed': self.validation_passed
        }


@dataclass
class ValidationResult:
    """Data validation result"""
    is_valid: bool
    quality: DataQuality
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validation_latency_ms: Optional[float] = None
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.is_valid = False
        if self.quality != DataQuality.INVALID:
            self.quality = DataQuality.POOR
    
    def add_warning(self, warning: str):
        """Add validation warning"""
        self.warnings.append(warning)
        if self.quality == DataQuality.EXCELLENT:
            self.quality = DataQuality.GOOD


@dataclass
class DataIngestionMetrics:
    """Performance metrics for data ingestion"""
    total_messages: int = 0
    successful_ingestions: int = 0
    failed_ingestions: int = 0
    validation_failures: int = 0
    
    # Latency metrics (in milliseconds)
    avg_processing_latency: float = 0.0
    max_processing_latency: float = 0.0
    min_processing_latency: float = float('inf')
    
    # Quality metrics  
    excellent_quality_count: int = 0
    good_quality_count: int = 0
    acceptable_quality_count: int = 0
    poor_quality_count: int = 0
    invalid_quality_count: int = 0
    
    # Throughput metrics
    messages_per_second: float = 0.0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_messages == 0:
            return 0.0
        return self.successful_ingestions / self.total_messages
    
    @property
    def uptime_percentage(self) -> float:
        """Calculate uptime percentage (target: 99.9%)"""
        if self.total_messages == 0:
            return 100.0
        return (self.successful_ingestions / self.total_messages) * 100
    
    @property
    def quality_distribution(self) -> Dict[str, float]:
        """Get quality distribution percentages"""
        total = (self.excellent_quality_count + self.good_quality_count + 
                self.acceptable_quality_count + self.poor_quality_count + 
                self.invalid_quality_count)
        
        if total == 0:
            return {quality.value: 0.0 for quality in DataQuality}
        
        return {
            DataQuality.EXCELLENT.value: (self.excellent_quality_count / total) * 100,
            DataQuality.GOOD.value: (self.good_quality_count / total) * 100,
            DataQuality.ACCEPTABLE.value: (self.acceptable_quality_count / total) * 100,
            DataQuality.POOR.value: (self.poor_quality_count / total) * 100,
            DataQuality.INVALID.value: (self.invalid_quality_count / total) * 100
        }
    
    def update_latency(self, latency_ms: float):
        """Update latency metrics"""
        self.avg_processing_latency = (
            (self.avg_processing_latency * self.successful_ingestions + latency_ms) / 
            (self.successful_ingestions + 1)
        )
        self.max_processing_latency = max(self.max_processing_latency, latency_ms)
        self.min_processing_latency = min(self.min_processing_latency, latency_ms)
    
    def update_quality(self, quality: DataQuality):
        """Update quality metrics"""
        if quality == DataQuality.EXCELLENT:
            self.excellent_quality_count += 1
        elif quality == DataQuality.GOOD:
            self.good_quality_count += 1
        elif quality == DataQuality.ACCEPTABLE:
            self.acceptable_quality_count += 1
        elif quality == DataQuality.POOR:
            self.poor_quality_count += 1
        elif quality == DataQuality.INVALID:
            self.invalid_quality_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for monitoring"""
        return {
            'total_messages': self.total_messages,
            'successful_ingestions': self.successful_ingestions,
            'failed_ingestions': self.failed_ingestions,
            'validation_failures': self.validation_failures,
            'success_rate': self.success_rate,
            'uptime_percentage': self.uptime_percentage,
            'avg_processing_latency': self.avg_processing_latency,
            'max_processing_latency': self.max_processing_latency,
            'min_processing_latency': self.min_processing_latency,
            'messages_per_second': self.messages_per_second,
            'quality_distribution': self.quality_distribution,
            'last_updated': self.last_updated.isoformat()
        }