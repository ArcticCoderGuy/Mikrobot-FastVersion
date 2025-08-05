#!/usr/bin/env python3
"""
Position Manager
Handles position tracking, management, and portfolio optimization
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from .connectors.mt5_connector import MT5Connector

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Position data structure"""
    ticket: int
    symbol: str
    type: str  # BUY or SELL
    volume: float
    price_open: float
    sl: float
    tp: float
    price_current: float
    profit: float
    swap: float
    magic: int
    comment: str
    time: datetime


class PositionManager:
    """Manages trading positions and portfolio state"""
    
    def __init__(self):
        self.mt5_connector: Optional[MT5Connector] = None
        self.positions: Dict[int, Position] = {}
        
    async def initialize(self, mt5_connector: MT5Connector) -> bool:
        """Initialize position manager"""
        self.mt5_connector = mt5_connector
        await self._sync_positions()
        return True
    
    async def _sync_positions(self):
        """Synchronize positions with MT5"""
        if not self.mt5_connector:
            return
        
        mt5_positions = await self.mt5_connector.get_positions()
        
        self.positions.clear()
        for pos_data in mt5_positions:
            position = Position(
                ticket=pos_data['ticket'],
                symbol=pos_data['symbol'],
                type=pos_data['type'],
                volume=pos_data['volume'],
                price_open=pos_data['price_open'],
                sl=pos_data['sl'],
                tp=pos_data['tp'],
                price_current=pos_data['price_current'],
                profit=pos_data['profit'],
                swap=pos_data['swap'],
                magic=pos_data['magic'],
                comment=pos_data['comment'],
                time=pos_data['time']
            )
            self.positions[position.ticket] = position
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Get positions, optionally filtered by symbol"""
        await self._sync_positions()
        
        if symbol:
            return [pos for pos in self.positions.values() if pos.symbol == symbol]
        return list(self.positions.values())
    
    async def close_position(self, ticket: int, volume: Optional[float] = None) -> bool:
        """Close position"""
        if not self.mt5_connector:
            return False
        
        result = await self.mt5_connector.close_position(ticket, volume)
        
        if result['success']:
            await self._sync_positions()
            return True
        
        return False
