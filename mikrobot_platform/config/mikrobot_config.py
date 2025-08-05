"""
MIKROBOT TRADING CONFIGURATION REPOSITORY
Above Robust central configuration system with MIKROBOT_FASTVERSION.md integration
Submarine-grade parameter control for enterprise trading platform
"""

import os
import json
from datetime import datetime
from pathlib import Path
from django.conf import settings


class MikrobotConfig:
    """Above Robust central configuration management"""
    
    def __init__(self):
        self.config_root = Path(__file__).parent.parent.parent
        self.mikrobot_fastversion_path = self.config_root / "MIKROBOT_FASTVERSION.md"
        self.config_cache = {}
        self.load_configuration()
    
    def load_configuration(self):
        """Load configuration from MIKROBOT_FASTVERSION.md and other sources"""
        self.config_cache = {
            # Above Robust Core Standards
            'POSITION_SIZING': {
                'DEFAULT_RISK_PERCENT': 0.55,  # 0.55% risk per trade (immutable)
                'MIN_RISK_PERCENT': 0.25,
                'MAX_RISK_PERCENT': 2.0,
                'ATR_MIN_PIPS': 4,
                'ATR_MAX_PIPS': 15,
            },
            
            # Signal Validation Standards
            'SIGNAL_VALIDATION': {
                'REQUIRED_PHASES': 4,  # M5 BOS + M1 Break + M1 Retest + Ylipip
                'YLIPIP_TRIGGER': 0.6,  # Standard trigger value
                'VALIDATION_TIMEOUT': 30,  # seconds
                'CACHE_DURATION': 300,  # 5 minutes
            },
            
            # Platform Configuration
            'PLATFORM': {
                'ASCII_ONLY_ENFORCED': True,
                'SUBMARINE_GRADE_PRECISION': True,
                'ABOVE_ROBUST_COMPLIANCE': True,
                'MAX_CONCURRENT_TRADES': 5,
                'SIGNAL_PROCESSING_RATE': 200,  # ms between signals
            },
            
            # Subscription Tiers (Customer Revenue)
            'SUBSCRIPTION_TIERS': {
                'BASIC': {
                    'price_monthly': 99,
                    'max_trades_daily': 10,
                    'max_concurrent_trades': 2,
                    'features': ['M5_BOS_M1_RETEST', 'BASIC_SIGNALS']
                },
                'PROFESSIONAL': {
                    'price_monthly': 199,
                    'max_trades_daily': 50,
                    'max_concurrent_trades': 5,
                    'features': ['M5_BOS_M1_RETEST', 'SUBMARINE_GOLD_STANDARD', 'ADVANCED_ANALYTICS']
                },
                'ENTERPRISE': {
                    'price_monthly': 499,
                    'max_trades_daily': -1,  # Unlimited
                    'max_concurrent_trades': 10,
                    'features': ['ALL_STRATEGIES', 'CUSTOM_RISK_MANAGEMENT', 'PRIORITY_SUPPORT']
                }
            },
            
            # Asset Class Configuration (from Submarine Command Center)
            'ASSET_CLASSES': {
                'FOREX': {'pip_value': 0.0001, 'atr_multiplier': 1.0, 'risk_factor': 1.0},
                'CFD_INDICES': {'pip_value': 1.0, 'atr_multiplier': 1.5, 'risk_factor': 1.2},
                'CFD_CRYPTO': {'pip_value': 0.1, 'atr_multiplier': 2.0, 'risk_factor': 1.5},
                'CFD_METALS': {'pip_value': 0.01, 'atr_multiplier': 1.2, 'risk_factor': 1.1},
                'CFD_ENERGIES': {'pip_value': 0.01, 'atr_multiplier': 1.8, 'risk_factor': 1.4},
                'CFD_STOCKS': {'pip_value': 0.01, 'atr_multiplier': 1.3, 'risk_factor': 1.2},
            },
            
            # Quality Control (Six Sigma Integration)
            'QUALITY_CONTROL': {
                'TARGET_CP_CPK': 3.0,  # Gold Standard
                'MIN_WIN_RATE': 0.70,
                'MAX_DRAWDOWN': 0.05,  # 5%
                'DAILY_LOSS_LIMIT': 0.02,  # 2%
            }
        }
        
        # Load MIKROBOT_FASTVERSION.md if exists
        if self.mikrobot_fastversion_path.exists():
            self.parse_mikrobot_fastversion()
    
    def parse_mikrobot_fastversion(self):
        """Parse MIKROBOT_FASTVERSION.md for configuration overrides"""
        try:
            with open(self.mikrobot_fastversion_path, 'r', encoding='ascii', errors='ignore') as f:
                content = f.read()
            
            # Parse position sizing settings
            if '0.55%' in content:
                self.config_cache['POSITION_SIZING']['DEFAULT_RISK_PERCENT'] = 0.55
            
            # Parse submarine mode settings
            if 'SUBMARINE' in content:
                self.config_cache['PLATFORM']['SUBMARINE_MODE_ACTIVE'] = True
            
            # Parse ATR settings
            if 'ATR' in content:
                # Extract ATR configuration from markdown
                lines = content.split('\n')
                for line in lines:
                    if 'ATR' in line and 'pips' in line:
                        # Parse ATR pip ranges from markdown
                        pass
            
        except Exception as e:
            print(f"WARNING: Could not parse MIKROBOT_FASTVERSION.md - {str(e)}")
    
    def get(self, key_path, default=None):
        """Get configuration value using dot notation"""
        keys = key_path.split('.')
        value = self.config_cache
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config_cache
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get_position_sizing_config(self):
        """Get complete position sizing configuration"""
        return self.config_cache['POSITION_SIZING']
    
    def get_subscription_config(self, tier):
        """Get subscription tier configuration"""
        return self.config_cache['SUBSCRIPTION_TIERS'].get(tier, {})
    
    def get_asset_class_config(self, symbol):
        """Get asset class configuration for symbol"""
        # Determine asset class from symbol
        if any(pair in symbol for pair in ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD']):
            return self.config_cache['ASSET_CLASSES']['FOREX']
        elif 'XAU' in symbol or 'XAG' in symbol:
            return self.config_cache['ASSET_CLASSES']['CFD_METALS']
        elif any(crypto in symbol for crypto in ['BTC', 'ETH', 'BCH']):
            return self.config_cache['ASSET_CLASSES']['CFD_CRYPTO']
        elif any(index in symbol for index in ['GER40', 'US30', 'SPX500']):
            return self.config_cache['ASSET_CLASSES']['CFD_INDICES']
        elif 'FERRARI' in symbol or '.IT' in symbol:
            return self.config_cache['ASSET_CLASSES']['CFD_STOCKS']
        else:
            return self.config_cache['ASSET_CLASSES']['FOREX']  # Default
    
    def calculate_position_size(self, account_balance, atr_pips, symbol, risk_percent=None):
        """Calculate Above Robust position size"""
        if risk_percent is None:
            risk_percent = self.get('POSITION_SIZING.DEFAULT_RISK_PERCENT')
        
        # Get asset class configuration
        asset_config = self.get_asset_class_config(symbol)
        
        # Calculate risk amount
        risk_amount = account_balance * (risk_percent / 100)
        
        # Apply asset-specific risk factor
        risk_amount *= asset_config['risk_factor']
        
        # Calculate position size
        pip_value = asset_config['pip_value']
        if 'JPY' in symbol:
            pip_value = 0.01  # Special handling for JPY pairs
        
        usd_per_pip_per_lot = pip_value * 100000  # Standard lot size
        if 'XAU' in symbol:  # Gold
            usd_per_pip_per_lot = 1.0
        elif any(index in symbol for index in ['GER40', 'US30']):
            usd_per_pip_per_lot = 1.0
        
        lot_size = risk_amount / (atr_pips * usd_per_pip_per_lot)
        
        # Apply minimum/maximum lot size constraints
        min_lot = 0.01
        max_lot = 10.0
        
        return max(min_lot, min(max_lot, round(lot_size, 2)))
    
    def is_above_robust_compliant(self):
        """Check if current configuration meets Above Robust standards"""
        checks = [
            self.get('PLATFORM.ASCII_ONLY_ENFORCED'),
            self.get('PLATFORM.SUBMARINE_GRADE_PRECISION'),
            self.get('POSITION_SIZING.DEFAULT_RISK_PERCENT') == 0.55,
            self.get('SIGNAL_VALIDATION.REQUIRED_PHASES') == 4,
        ]
        
        return all(checks)
    
    def export_config_json(self):
        """Export current configuration as JSON"""
        return json.dumps(self.config_cache, indent=2, ensure_ascii=True)
    
    def save_to_mikrobot_fastversion(self):
        """Save current configuration back to MIKROBOT_FASTVERSION.md"""
        config_section = f"""
## MIKROBOT CONFIGURATION (Auto-Generated)

### Position Sizing Standards
- **Default Risk**: {self.get('POSITION_SIZING.DEFAULT_RISK_PERCENT')}% per trade
- **ATR Range**: {self.get('POSITION_SIZING.ATR_MIN_PIPS')}-{self.get('POSITION_SIZING.ATR_MAX_PIPS')} pips
- **Above Robust Compliant**: {self.is_above_robust_compliant()}

### Platform Status
- **Submarine Grade**: {self.get('PLATFORM.SUBMARINE_GRADE_PRECISION')}
- **ASCII Only**: {self.get('PLATFORM.ASCII_ONLY_ENFORCED')}
- **Max Concurrent Trades**: {self.get('PLATFORM.MAX_CONCURRENT_TRADES')}

### Quality Control
- **Target Cp/Cpk**: {self.get('QUALITY_CONTROL.TARGET_CP_CPK')}
- **Min Win Rate**: {self.get('QUALITY_CONTROL.MIN_WIN_RATE')}
- **Max Drawdown**: {self.get('QUALITY_CONTROL.MAX_DRAWDOWN')}

### Revenue Model
- **Basic**: ${self.get('SUBSCRIPTION_TIERS.BASIC.price_monthly')}/month
- **Professional**: ${self.get('SUBSCRIPTION_TIERS.PROFESSIONAL.price_monthly')}/month  
- **Enterprise**: ${self.get('SUBSCRIPTION_TIERS.ENTERPRISE.price_monthly')}/month

*Configuration last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        try:
            # Read existing MIKROBOT_FASTVERSION.md
            existing_content = ""
            if self.mikrobot_fastversion_path.exists():
                with open(self.mikrobot_fastversion_path, 'r', encoding='ascii', errors='ignore') as f:
                    existing_content = f.read()
            
            # Replace or append configuration section
            if "## MIKROBOT CONFIGURATION" in existing_content:
                # Replace existing section
                lines = existing_content.split('\n')
                new_lines = []
                skip_section = False
                
                for line in lines:
                    if line.startswith("## MIKROBOT CONFIGURATION"):
                        skip_section = True
                        new_lines.append(config_section.strip())
                    elif line.startswith("##") and skip_section:
                        skip_section = False
                        new_lines.append(line)
                    elif not skip_section:
                        new_lines.append(line)
                
                updated_content = '\n'.join(new_lines)
            else:
                # Append configuration section
                updated_content = existing_content + "\n\n" + config_section
            
            # Write back to file
            with open(self.mikrobot_fastversion_path, 'w', encoding='ascii', errors='ignore') as f:
                f.write(updated_content)
            
            return True
            
        except Exception as e:
            print(f"ERROR: Could not save to MIKROBOT_FASTVERSION.md - {str(e)}")
            return False


# Global configuration instance
mikrobot_config = MikrobotConfig()


# Django settings integration
def get_mikrobot_setting(key, default=None):
    """Get Mikrobot configuration value for Django settings"""
    return mikrobot_config.get(key, default)


# Convenience functions for common operations
def calculate_lot_size(account_balance, atr_pips, symbol, risk_percent=None):
    """Calculate Above Robust lot size"""
    return mikrobot_config.calculate_position_size(account_balance, atr_pips, symbol, risk_percent)


def get_subscription_limits(tier):
    """Get subscription tier limits"""
    config = mikrobot_config.get_subscription_config(tier)
    return {
        'max_trades_daily': config.get('max_trades_daily', 3),
        'max_concurrent_trades': config.get('max_concurrent_trades', 2),
        'monthly_revenue': config.get('price_monthly', 99)
    }


def is_above_robust_compliant():
    """Check Above Robust compliance"""
    return mikrobot_config.is_above_robust_compliant()