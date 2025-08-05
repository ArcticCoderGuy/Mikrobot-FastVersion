"""
U-Cell 3: Risk Engine
FTMO-compliant risk management with prop firm rules
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from . import UCell, CellInput, CellOutput
import logging

logger = logging.getLogger(__name__)


class RiskEngineCell(UCell):
    """
    Risk management following FTMO and prop firm rules
    - Daily loss limits
    - Maximum loss limits
    - Position sizing
    - Weekly targets
    """
    
    def __init__(self, account_config: Optional[Dict[str, Any]] = None):
        super().__init__(cell_id="U3", name="Risk Engine")
        
        # Default FTMO-style rules
        self.account_config = account_config or {
            'balance': 100000,
            'max_daily_loss_percent': 5.0,  # 5% daily loss limit
            'max_total_loss_percent': 10.0,  # 10% total loss limit
            'profit_target_percent': 10.0,   # 10% profit target
            'min_trading_days': 10,
            'max_position_risk_percent': 1.0,  # 1% risk per trade
            'max_open_positions': 3,
            'leverage': 100
        }
        
        # Track account metrics
        self.account_metrics = {
            'current_balance': self.account_config['balance'],
            'starting_balance': self.account_config['balance'],
            'daily_starting_balance': self.account_config['balance'],
            'highest_balance': self.account_config['balance'],
            'daily_pnl': 0.0,
            'total_pnl': 0.0,
            'open_positions': 0,
            'trading_days': 0
        }
        
        # Risk limits
        self.risk_limits = self._calculate_risk_limits()
    
    def _calculate_risk_limits(self) -> Dict[str, float]:
        """Calculate absolute risk limits"""
        balance = self.account_config['balance']
        return {
            'max_daily_loss': balance * self.account_config['max_daily_loss_percent'] / 100,
            'max_total_loss': balance * self.account_config['max_total_loss_percent'] / 100,
            'profit_target': balance * self.account_config['profit_target_percent'] / 100,
            'max_position_risk': balance * self.account_config['max_position_risk_percent'] / 100
        }
    
    def validate_input(self, cell_input: CellInput) -> bool:
        """Validate input from ML Analysis cell"""
        required_keys = ['symbol', 'direction', 'probability', 'optimized_levels', 'pip_data']
        return all(key in cell_input.data for key in required_keys)
    
    def process(self, cell_input: CellInput) -> CellOutput:
        """Process trade through risk management rules"""
        data = cell_input.data
        
        try:
            # Check all risk rules
            risk_checks = self._perform_risk_checks(data)
            
            if all(check['passed'] for check in risk_checks.values()):
                # Calculate position size
                position_size = self._calculate_position_size(data)
                
                # Calculate monetary risk
                monetary_risk = self._calculate_monetary_risk(position_size, data)
                
                # Prepare risk-approved trade
                risk_approved_trade = {
                    **data,
                    'position_size': position_size,
                    'monetary_risk': monetary_risk,
                    'risk_checks': risk_checks,
                    'account_metrics': self.account_metrics.copy(),
                    'risk_limits': self.risk_limits.copy(),
                    'risk_reward_ratio': data['pip_data']['risk_reward'],
                    'max_loss': monetary_risk,
                    'potential_profit': monetary_risk * data['pip_data']['risk_reward']
                }
                
                return CellOutput(
                    timestamp=datetime.utcnow(),
                    status='success',
                    data=risk_approved_trade,
                    next_cell='U4',  # Trade Execution
                    trace_id=cell_input.trace_id
                )
            else:
                # Risk check failed
                failed_checks = [name for name, check in risk_checks.items() if not check['passed']]
                
                return CellOutput(
                    timestamp=datetime.utcnow(),
                    status='rejected',
                    data={
                        'reason': 'Risk checks failed',
                        'failed_checks': failed_checks,
                        'risk_checks': risk_checks
                    },
                    trace_id=cell_input.trace_id,
                    errors=[f"Failed risk checks: {', '.join(failed_checks)}"]
                )
                
        except Exception as e:
            logger.error(f"Risk engine error: {str(e)}")
            return CellOutput(
                timestamp=datetime.utcnow(),
                status='failed',
                data={},
                trace_id=cell_input.trace_id,
                errors=[str(e)]
            )
    
    def _perform_risk_checks(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Perform all risk checks"""
        checks = {}
        
        # 1. Daily loss limit check
        daily_loss_remaining = self.risk_limits['max_daily_loss'] - abs(self.account_metrics['daily_pnl'])
        checks['daily_loss_limit'] = {
            'passed': daily_loss_remaining > 0,
            'remaining': daily_loss_remaining,
            'limit': self.risk_limits['max_daily_loss']
        }
        
        # 2. Total loss limit check
        total_loss_from_highest = self.account_metrics['highest_balance'] - self.account_metrics['current_balance']
        total_loss_remaining = self.risk_limits['max_total_loss'] - total_loss_from_highest
        checks['total_loss_limit'] = {
            'passed': total_loss_remaining > 0,
            'remaining': total_loss_remaining,
            'limit': self.risk_limits['max_total_loss']
        }
        
        # 3. Open positions check
        checks['position_limit'] = {
            'passed': self.account_metrics['open_positions'] < self.account_config['max_open_positions'],
            'current': self.account_metrics['open_positions'],
            'limit': self.account_config['max_open_positions']
        }
        
        # 4. Minimum probability check
        checks['probability_threshold'] = {
            'passed': data['probability'] >= 0.65,
            'probability': data['probability'],
            'threshold': 0.65
        }
        
        # 5. Risk-reward check
        checks['risk_reward_ratio'] = {
            'passed': data['pip_data']['risk_reward'] >= 1.5,
            'ratio': data['pip_data']['risk_reward'],
            'minimum': 1.5
        }
        
        # 6. Session-based risk check
        current_session = self._get_trading_session()
        session_risk_multiplier = {
            'asian': 0.5,
            'european': 1.0,
            'american': 0.8
        }.get(current_session, 1.0)
        
        checks['session_risk'] = {
            'passed': True,  # Always pass but adjust position size
            'session': current_session,
            'risk_multiplier': session_risk_multiplier
        }
        
        return checks
    
    def _calculate_position_size(self, data: Dict[str, Any]) -> float:
        """Calculate position size based on risk parameters"""
        # Get account balance and risk amount
        balance = self.account_metrics['current_balance']
        max_risk = self.risk_limits['max_position_risk']
        
        # Get pip value and stop loss pips
        sl_pips = data['pip_data']['sl_pips']
        
        # Calculate pip value based on symbol
        symbol = data['symbol']
        if 'JPY' in symbol:
            pip_value = 0.01
        else:
            pip_value = 0.0001
        
        # Standard lot size (100,000 units)
        standard_lot = 100000
        
        # Calculate position size
        # Risk = Position Size × Pip Value × Stop Loss Pips
        # Position Size = Risk / (Pip Value × Stop Loss Pips)
        
        if sl_pips > 0:
            # Calculate lots
            position_size_units = max_risk / (pip_value * sl_pips)
            lots = position_size_units / standard_lot
            
            # Apply session risk multiplier
            session_multiplier = 1.0  # Could adjust based on session
            lots *= session_multiplier
            
            # Apply probability-based sizing
            if data['probability'] < 0.70:
                lots *= 0.8
            elif data['probability'] > 0.80:
                lots *= 1.2
            
            # Round to 2 decimal places (0.01 lot precision)
            lots = round(lots, 2)
            
            # Ensure minimum and maximum lot sizes
            lots = max(0.01, min(lots, 10.0))
            
            return lots
        else:
            return 0.01  # Minimum lot size
    
    def _calculate_monetary_risk(self, position_size: float, data: Dict[str, Any]) -> float:
        """Calculate monetary risk for the position"""
        sl_pips = data['pip_data']['sl_pips']
        
        # Calculate pip value for the position
        symbol = data['symbol']
        if 'JPY' in symbol:
            pip_value = 0.01
        else:
            pip_value = 0.0001
        
        # Monetary risk = Position Size × Pip Value × Stop Loss Pips × Lot Size
        monetary_risk = position_size * 100000 * pip_value * sl_pips
        
        return round(monetary_risk, 2)
    
    def _get_trading_session(self) -> str:
        """Determine current trading session"""
        from datetime import datetime
        hour = datetime.utcnow().hour
        
        if 0 <= hour < 8:
            return 'asian'
        elif 8 <= hour < 16:
            return 'european'
        else:
            return 'american'
    
    def update_metrics(self, trade_result: Dict[str, Any]):
        """Update account metrics after trade completion"""
        pnl = trade_result.get('pnl', 0)
        
        # Update balances
        self.account_metrics['current_balance'] += pnl
        self.account_metrics['daily_pnl'] += pnl
        self.account_metrics['total_pnl'] += pnl
        
        # Update highest balance
        if self.account_metrics['current_balance'] > self.account_metrics['highest_balance']:
            self.account_metrics['highest_balance'] = self.account_metrics['current_balance']
        
        # Update open positions
        if trade_result.get('action') == 'open':
            self.account_metrics['open_positions'] += 1
        elif trade_result.get('action') == 'close':
            self.account_metrics['open_positions'] = max(0, self.account_metrics['open_positions'] - 1)
    
    def reset_daily_metrics(self):
        """Reset daily metrics (call at start of new trading day)"""
        self.account_metrics['daily_starting_balance'] = self.account_metrics['current_balance']
        self.account_metrics['daily_pnl'] = 0.0
        self.account_metrics['trading_days'] += 1