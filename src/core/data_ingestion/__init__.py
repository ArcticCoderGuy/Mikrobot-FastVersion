"""
Real-Time Data Ingestion System for Mikrobot ML-Enhanced Core
Session #2 Implementation - Foundation for ML Trading Intelligence

Provides multi-asset real-time data ingestion with:
- 99.9% uptime target
- <10ms latency performance
- Multi-asset support (Forex, Crypto, Indices)
- Real-time data validation
- Integration with ProductOwner → MCP → U-Cells architecture
"""

from .data_ingestion_engine import DataIngestionEngine, DataConnector
from .data_models import (
    TickData, OHLCVData, MarketData, AssetType, 
    DataQuality, ValidationResult, DataSource
)
from .forex_connector import ForexDataConnector
from .crypto_connector import CryptoDataConnector
from .indices_connector import IndicesDataConnector
from .data_validator import DataValidator, DataQualityMonitor
from .performance_monitor import IngestionPerformanceMonitor

__all__ = [
    'DataIngestionEngine',
    'DataConnector', 
    'TickData',
    'OHLCVData',
    'MarketData',
    'AssetType',
    'DataQuality',
    'ValidationResult',
    'DataSource',
    'ForexDataConnector',
    'CryptoDataConnector', 
    'IndicesDataConnector',
    'DataValidator',
    'DataQualityMonitor',
    'IngestionPerformanceMonitor'
]