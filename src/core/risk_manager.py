#!/usr/bin/env python3
"""
Risk Manager
Implements risk management rules and position sizing
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RiskManager:
    """Risk management system"""
    
    def __init__(self):
        self.max_risk_per_trade = 0.55  # 0.55% as per MIKROBOT spec
        self.max_daily_risk = 2.0  # 2% max daily risk
        self.max_positions_per_symbol = 3
        self.max_total_positions = 10
        
        # Risk tracking
        self.daily_risk_used = 0.0
        self.last_reset_date = datetime.now().date()
        
    async def initialize(self) -> bool:
        """Initialize risk manager"""
        return True
    
    async def validate_trade(self, trade_request) -> Dict[str, Any]:
        """Validate trade against risk rules"""
        # Reset daily risk if new day
        if datetime.now().date() > self.last_reset_date:
            self.daily_risk_used = 0.0
            self.last_reset_date = datetime.now().date()
        
        # Check daily risk limit
        trade_risk_percent = trade_request.risk_percent or self.max_risk_per_trade
        
        if self.daily_risk_used + trade_risk_percent > self.max_daily_risk:
            return {
                'allowed': False,
                'reason': f'Daily risk limit exceeded: {self.daily_risk_used + trade_risk_percent:.2f}% > {self.max_daily_risk}%'
            }
        
        # Check per-trade risk limit
        if trade_risk_percent > self.max_risk_per_trade:
            return {
                'allowed': False,
                'reason': f'Trade risk too high: {trade_risk_percent:.2f}% > {self.max_risk_per_trade}%'
            }
        
        # Update daily risk usage
        self.daily_risk_used += trade_risk_percent
        
        return {'allowed': True}
