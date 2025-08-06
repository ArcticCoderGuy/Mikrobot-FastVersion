"""
MIKROBOT FASTVERSION v2.0 - Direct MT5 Trading System
===================================================

New generation autonomous trading system with:
- Direct MT5 integration (no EA dependency)
- Lightning Bolt strategy (M5 BOS + M1 Retest + 0.6 Ylipip)
- Multi-asset support (Forex, Crypto, Indices)
- ML/MCP orchestration
- Hansei reflection system
- Real-time autonomous trading

Account: 95244786 @ MetaQuotesDemo
Strategy: Lightning Bolt 3-Phase Pattern
Risk: 0.01 lot size per trade
"""

__version__ = "2.0.0"
__author__ = "Mikrobot FastVersion Team"
__description__ = "Direct MT5 Trading System with Lightning Bolt Strategy"

# Core modules
from .core import MT5DirectConnector
from .strategies import LightningBoltStrategy
from .orchestration import MCPv2Controller, HanseiReflector

__all__ = [
    'MT5DirectConnector',
    'LightningBoltStrategy',
    'MCPv2Controller',
    'HanseiReflector'
]