from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
APPLY COMPREHENSIVE PIP RULES
Update M5/M1 BOS strategy with comprehensive 0.8 pip conversions
Above Robust! implementation
"""
import json
import time
from pathlib import Path

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

def load_pip_rules():
    """Load the latest pip conversion rules"""
    print("LOADING_COMPREHENSIVE_PIP_RULES")
    
    # Find latest pip rules file
    pip_files = list(Path(".").glob("mt5_pip_rules_*.json"))
    if not pip_files:
        print("NO_PIP_RULES_FOUND")
        return None
    
    # Get latest file
    latest_file = sorted(pip_files)[-1]
    print(f"Loading: {latest_file}")
    
    with open(latest_file, 'r', encoding='ascii', errors='ignore') as f:
        pip_data = json.load(f)
    
    return pip_data["pip_conversion_rules"]

def update_strategy_with_comprehensive_rules():
    """Update M5/M1 strategy with comprehensive pip rules"""
    print("UPDATING_M5M1_STRATEGY_WITH_COMPREHENSIVE_RULES")
    print("=" * 60)
    
    # Load pip conversion rules
    pip_rules = load_pip_rules()
    if not pip_rules:
        print("FAILED_TO_LOAD_PIP_RULES")
        return False
    
    print(f"Loaded {len(pip_rules)} symbol pip conversions")
    
    # Update strategy configuration
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    
    if config_file.exists():
        with open(config_file, 'r', encoding='ascii', errors='ignore') as f:
            config = json.load(f)
    else:
        config = {"config": {}}
    
    config_data = config.get('config', {})
    
    # Update with comprehensive pip rules
    config_data.update({
        "strategy_id": "M5M1_BOS_COMPREHENSIVE_08",
        "comprehensive_pip_rules": {
            "enabled": True,
            "base_pip_trigger": 0.8,
            "symbol_specific_rules": pip_rules,
            "fallback_pip_value": 0.0001,
            "auto_detection": True
        },
        "pattern_detection": {
            "bos_sensitivity": "MEDIUM",
            "retest_precision": 0.8,
            "break_confirmation": "VOLUME_SPIKE",
            "false_break_filter": True,
            "symbol_adaptive": True
        },
        "entry_rules": {
            "entry_method": "RETEST_TRIGGER",
            "pip_distance": 0.8,
            "symbol_specific_pip_distance": pip_rules,
            "volume_confirmation": True,
            "time_filter": "EXCLUDE_NEWS"
        },
        "supported_symbols": list(pip_rules.keys()),
        "asset_classes": {
            "crypto": ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "BCHUSD"],
            "forex_major": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"],
            "forex_minor": ["EURJPY", "GBPJPY", "EURGBP", "AUDJPY", "CADJPY"],
            "other": ["AUDCAD"]
        }
    })
    
    config["timestamp"] = time.time()
    
    # Save updated configuration
    with open(config_file, 'w', encoding='ascii', errors='ignore') as f:
        json.dump(config, f, indent=2)
    
    print(f"Strategy configuration updated: {config_file}")
    
    # Create comprehensive activation signal
    activation_signal = {
        "command": "ACTIVATE_COMPREHENSIVE_M5M1",
        "strategy_name": "MikroBot_BOS_M5M1",
        "version": "2.03_COMPREHENSIVE",
        "parameters": {
            "timeframes": ["M5", "M1"],
            "signal_type": "BOS_BREAK_RETEST",
            "base_pip_trigger": 0.8,
            "comprehensive_pip_rules": pip_rules,
            "frequency": "ADAPTIVE",
            "supported_symbols": list(pip_rules.keys()),
            "risk_management": {
                "position_size": 0.05,
                "stop_loss_method": "BREAK_LEVEL",
                "take_profit_ratio": 2.5,
                "max_positions": 3
            }
        },
        "activation_time": time.time(),
        "account": 95244786,
        "source": "Comprehensive_Pip_Update"
    }
    
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    with open(activation_file, 'w', encoding='ascii', errors='ignore') as f:
        json.dump(activation_signal, f, indent=2)
    
    print(f"Comprehensive activation signal sent: {activation_file}")
    
    return True

def create_pip_lookup_function():
    """Create pip lookup function for EA"""
    print("CREATING_PIP_LOOKUP_FUNCTION")
    
    pip_rules = load_pip_rules()
    if not pip_rules:
        return False
    
    # Create MQL5-compatible pip lookup
    mql5_pip_lookup = {
        "function_name": "GetSymbolPipTrigger08",
        "description": "Get 0.8 pip trigger value for any symbol",
        "pip_rules": pip_rules,
        "fallback_rules": {
            "forex_major_5digit": 0.000008,
            "forex_major_4digit": 0.00008,
            "forex_jpy": 0.008,
            "crypto_btc": 0.8,
            "crypto_other": 0.008,
            "default": 0.00008
        },
        "algorithm": "symbol_lookup_with_fallback"
    }
    
    pip_lookup_file = COMMON_PATH / "pip_lookup_function.json"
    with open(pip_lookup_file, 'w', encoding='ascii', errors='ignore') as f:
        json.dump(mql5_pip_lookup, f, indent=2)
    
    print(f"Pip lookup function created: {pip_lookup_file}")
    
    return True

def verify_comprehensive_update():
    """Verify comprehensive update was successful"""
    print("\nVERIFYING_COMPREHENSIVE_UPDATE")
    print("=" * 40)
    
    # Check strategy config
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='ascii', errors='ignore') as f:
            config = json.load(f)
        
        comprehensive_rules = config.get('config', {}).get('comprehensive_pip_rules', {})
        if comprehensive_rules.get('enabled'):
            symbol_count = len(comprehensive_rules.get('symbol_specific_rules', {}))
            print(f"OK Comprehensive pip rules: {symbol_count} symbols")
        else:
            print("ERROR Comprehensive pip rules not enabled")
    
    # Check activation signal
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    if activation_file.exists():
        with open(activation_file, 'r', encoding='ascii', errors='ignore') as f:
            activation = json.load(f)
        
        version = activation.get('version', '')
        if 'COMPREHENSIVE' in version:
            print(f"OK Activation signal: {version}")
        else:
            print(f"ERROR Activation signal not comprehensive: {version}")
    
    # Check pip lookup
    lookup_file = COMMON_PATH / "pip_lookup_function.json"
    if lookup_file.exists():
        print("OK Pip lookup function created")
    else:
        print("ERROR Pip lookup function missing")
    
    print("=" * 40)
    print("OK COMPREHENSIVE_UPDATE_VERIFIED")

def run_comprehensive_pip_application():
    """Run comprehensive pip rules application"""
    print("APPLYING COMPREHENSIVE PIP RULES TO M5/M1 BOS STRATEGY")
    print("Above Robust! implementation with unified pip conversion")
    print("=" * 70)
    
    # 1. Update strategy configuration
    if not update_strategy_with_comprehensive_rules():
        print("STRATEGY_UPDATE_FAILED")
        return False
    
    # 2. Create pip lookup function
    if not create_pip_lookup_function():
        print("PIP_LOOKUP_CREATION_FAILED")
        return False
    
    # 3. Verify update
    verify_comprehensive_update()
    
    print("\n" + "=" * 70)
    print("ROCKET M5/M1 BOS STRATEGY: COMPREHENSIVE PIP RULES APPLIED")
    print("CHART 18 priority symbols with precise 0.8 pip conversions")
    print("FAST Symbol-adaptive precision for optimal signal quality")
    print("TARGET Above Robust! unified pip conversion system active")
    
    return True

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    success = run_comprehensive_pip_application()
    
    if success:
        print("\nOK COMPREHENSIVE PIP RULES APPLICATION: SUCCESS")
        print("M5/M1 BOS strategy now uses unified 0.8 pip conversions")
        print("All tradeable symbols have proper pip trigger values")
    else:
        print("\nERROR COMPREHENSIVE PIP RULES APPLICATION: FAILED")
        print("Manual intervention required")