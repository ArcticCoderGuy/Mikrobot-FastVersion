"""
UNIVERSAL 0.6 YLIPIP TRIGGER SYSTEM
MIKROBOT_FASTVERSION.md Implementation
ALL 9 MT5 Asset Classes Support
"""
import MetaTrader5 as mt5
import json
from pathlib import Path
from datetime import datetime

class UniversalYlipipTrigger:
    """
    Universal 0.6 ylipip trigger for ALL MT5 asset classes:
    Forex, CFD-Indices, CFD-Crypto, CFD-Metals, CFD-Energies, 
    CFD-Agricultural, CFD-Bonds, CFD-Shares, CFD-ETFs
    """
    
    def __init__(self):
        self.ylipip_standard = 0.6  # Universal standard
        self.common_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
        
        # Asset class detection patterns
        self.asset_patterns = {
            "Forex": ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"],
            "CFD-Crypto": ["BTC", "ETH", "ADA", "XRP", "LTC", "BCH", "DOT", "LINK"],
            "CFD-Metals": ["XAU", "XAG", "XPT", "XPD", "GOLD", "SILVER"],
            "CFD-Indices": ["SPX", "NAS", "DAX", "FTSE", "CAC", "NIK", "ASX", "HSI"],
            "CFD-Energies": ["CRUDE", "BRENT", "NGAS", "HEATING", "GASOLINE"],
            "CFD-Agricultural": ["WHEAT", "CORN", "SOYBEAN", "SUGAR", "COFFEE", "COCOA"],
            "CFD-Bonds": ["BOND", "BUND", "NOTE", "GILT", "OAT"],
            "CFD-Shares": [],  # Individual stocks - detected by symbol info
            "CFD-ETFs": ["SPY", "QQQ", "IWM", "EFA", "EEM", "GLD", "SLV"]
        }
    
    def detect_asset_class(self, symbol):
        """Detect asset class for given symbol"""
        symbol_upper = symbol.upper()
        
        # Check each asset class pattern
        for asset_class, patterns in self.asset_patterns.items():
            if asset_class == "CFD-Shares":
                continue  # Handle stocks separately
                
            for pattern in patterns:
                if pattern in symbol_upper:
                    return asset_class
        
        # Check if it's a stock (has company-like symbol)
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info and hasattr(symbol_info, 'path'):
            if "Stocks" in symbol_info.path or "Shares" in symbol_info.path:
                return "CFD-Shares"
            elif "ETF" in symbol_info.path:
                return "CFD-ETFs"
        
        # Default to Forex if no pattern matches
        return "Forex"
    
    def get_asset_pip_value(self, symbol, asset_class):
        """Get pip value specific to asset class"""
        pip_values = {
            "Forex": {
                "JPY_pairs": 0.01,      # USDJPY, EURJPY etc.
                "standard": 0.0001      # EURUSD, GBPUSD etc.
            },
            "CFD-Crypto": {
                "BTC": 1.0,             # Bitcoin: 1 dollar = 1 pip
                "ETH": 0.1,             # Ethereum: 10 cents = 1 pip
                "standard": 0.01        # Other crypto: 1 cent = 1 pip
            },
            "CFD-Metals": {
                "XAU": 0.1,             # Gold: 10 cents = 1 pip
                "XAG": 0.01,            # Silver: 1 cent = 1 pip
                "standard": 0.01
            },
            "CFD-Indices": {
                "SPX": 1.0,             # S&P500: 1 point = 1 pip
                "NAS": 1.0,             # Nasdaq: 1 point = 1 pip
                "DAX": 1.0,             # DAX: 1 point = 1 pip
                "standard": 1.0
            },
            "CFD-Energies": {
                "CRUDE": 0.01,          # Crude oil: 1 cent = 1 pip
                "BRENT": 0.01,          # Brent oil: 1 cent = 1 pip
                "NGAS": 0.001,          # Natural gas: 0.1 cent = 1 pip
                "standard": 0.01
            },
            "CFD-Agricultural": {
                "standard": 0.01        # 1 cent = 1 pip for most agricultural
            },
            "CFD-Bonds": {
                "standard": 0.01        # 1 cent = 1 pip for bonds
            },
            "CFD-Shares": {
                "standard": 0.01        # 1 cent = 1 pip for stocks
            },
            "CFD-ETFs": {
                "standard": 0.01        # 1 cent = 1 pip for ETFs
            }
        }
        
        asset_config = pip_values.get(asset_class, {"standard": 0.0001})
        
        # Check for specific symbol patterns
        symbol_upper = symbol.upper()
        
        if asset_class == "Forex" and "JPY" in symbol_upper:
            return asset_config["JPY_pairs"]
        elif asset_class == "CFD-Crypto":
            if "BTC" in symbol_upper:
                return asset_config["BTC"]
            elif "ETH" in symbol_upper:
                return asset_config["ETH"]
        elif asset_class == "CFD-Metals":
            if "XAU" in symbol_upper:
                return asset_config["XAU"]
            elif "XAG" in symbol_upper:
                return asset_config["XAG"]
        
        return asset_config["standard"]
    
    def calculate_ylipip_trigger(self, symbol):
        """Calculate 0.6 ylipip trigger for any MT5 symbol"""
        # Detect asset class
        asset_class = self.detect_asset_class(symbol)
        
        # Get asset-specific pip value
        pip_value = self.get_asset_pip_value(symbol, asset_class)
        
        # Calculate 0.6 ylipip trigger
        ylipip_trigger = self.ylipip_standard * pip_value
        
        return {
            "symbol": symbol,
            "asset_class": asset_class,
            "pip_value": pip_value,
            "ylipip_standard": self.ylipip_standard,
            "ylipip_trigger": ylipip_trigger,
            "trigger_formatted": f"{ylipip_trigger:.5f}"
        }
    
    def validate_ylipip_trigger(self, symbol, current_price, entry_price, trade_type):
        """Validate if 0.6 ylipip trigger has been reached"""
        trigger_info = self.calculate_ylipip_trigger(symbol)
        ylipip_trigger = trigger_info["ylipip_trigger"]
        
        # Calculate price movement
        if trade_type.upper() == "BUY":
            price_movement = current_price - entry_price
        else:  # SELL
            price_movement = entry_price - current_price
            
        # Check if ylipip trigger reached
        trigger_reached = price_movement >= ylipip_trigger
        
        return {
            "trigger_reached": trigger_reached,
            "price_movement": round(price_movement, 5),
            "ylipip_trigger": ylipip_trigger,
            "distance_to_trigger": round(ylipip_trigger - price_movement, 5),
            "trigger_info": trigger_info
        }
    
    def create_universal_trigger_config(self):
        """Create configuration for all supported symbols"""
        if not mt5.initialize():
            return None
            
        # Get all available symbols
        symbols = mt5.symbols_get()
        if not symbols:
            return None
            
        config = {
            "timestamp": datetime.now().isoformat(),
            "ylipip_standard": self.ylipip_standard,
            "supported_symbols": {},
            "asset_class_summary": {}
        }
        
        asset_class_counts = {}
        
        for symbol in symbols[:100]:  # Limit to first 100 for performance
            symbol_name = symbol.name
            trigger_info = self.calculate_ylipip_trigger(symbol_name)
            
            config["supported_symbols"][symbol_name] = trigger_info
            
            # Count asset classes
            asset_class = trigger_info["asset_class"]
            asset_class_counts[asset_class] = asset_class_counts.get(asset_class, 0) + 1
        
        config["asset_class_summary"] = asset_class_counts
        
        return config
    
    def save_universal_config(self):
        """Save universal ylipip configuration to file"""
        config = self.create_universal_trigger_config()
        if not config:
            return False
            
        config_file = self.common_path / "universal_ylipip_config.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving universal config: {e}")
            return False
    
    def get_trigger_for_symbol(self, symbol):
        """Get ylipip trigger value for specific symbol"""
        trigger_info = self.calculate_ylipip_trigger(symbol)
        return trigger_info["ylipip_trigger"]

if __name__ == "__main__":
    # Test Universal Ylipip Trigger
    trigger_system = UniversalYlipipTrigger()
    
    if mt5.initialize():
        print("Testing Universal 0.6 Ylipip Trigger System")
        
        # Test different asset classes
        test_symbols = [
            "EURUSD",    # Forex
            "USDJPY",    # Forex JPY
            "BTCUSD",    # Crypto
            "XAUUSD",    # Metals
            "SPX500",    # Indices
            "CRUDE",     # Energies
            "WHEAT",     # Agricultural
        ]
        
        print(f"\nTesting 0.6 ylipip across asset classes:")
        
        for symbol in test_symbols:
            trigger_info = trigger_system.calculate_ylipip_trigger(symbol)
            print(f"  {symbol:10} | {trigger_info['asset_class']:15} | {trigger_info['ylipip_trigger']:8.5f} | pip: {trigger_info['pip_value']}")
        
        # Save universal configuration
        if trigger_system.save_universal_config():
            print(f"\nSUCCESS Universal configuration saved to: {trigger_system.common_path / 'universal_ylipip_config.json'}")
        
        mt5.shutdown()
    else:
        print("ERROR Failed to initialize MT5")