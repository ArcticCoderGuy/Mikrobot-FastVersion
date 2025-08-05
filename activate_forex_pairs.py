"""
ACTIVATE FOREX PAIRS FOR BOS MONITORING
Adds GBPJPY and other forex pairs to active monitoring
"""
import json
from pathlib import Path
from datetime import datetime

def activate_forex_monitoring():
    """Update configuration to monitor forex pairs including GBPJPY"""
    config_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/m5m1_strategy_config.json")
    
    # Read current config
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    print("Current Configuration Status:")
    print("=" * 50)
    print(f"Active symbols: {config_data['config']['active_symbols']}")
    print(f"Crypto focus: {config_data['config']['session_config']['crypto_focus']}")
    
    # Update to include forex pairs
    new_active_symbols = [
        # Keep crypto
        "BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD",
        # Add major forex pairs
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD",
        # Add forex minors INCLUDING GBPJPY
        "EURJPY", "GBPJPY", "AUDJPY"
    ]
    
    # Update configuration
    config_data['config']['active_symbols'] = new_active_symbols
    config_data['config']['session_config']['crypto_focus'] = False
    config_data['config']['session_config']['forex_enabled'] = True
    config_data['timestamp'] = datetime.now().timestamp()
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print("\nUpdated Configuration:")
    print("=" * 50)
    print(f"New active symbols: {new_active_symbols}")
    print("GBPJPY: ACTIVATED")
    print("Forex pairs: ACTIVATED")
    print("Crypto focus: DISABLED")
    
    print("\nGBPJPY specific configuration:")
    print(f"- Pip value: {config_data['config']['entry_rules']['symbol_specific_pip_distance']['GBPJPY']}")
    print(f"- Pip trigger: {config_data['config']['comprehensive_pip_rules']['symbol_specific_rules']['GBPJPY']}")
    
    return True

if __name__ == "__main__":
    print("ACTIVATING FOREX PAIRS FOR M5/M1 BOS MONITORING")
    print("This will enable GBPJPY and other forex pairs")
    print("")
    
    if activate_forex_monitoring():
        print("\nSUCCESS: Configuration updated!")
        print("The system will now monitor GBPJPY for BOS patterns")
        print("Restart the monitoring system to apply changes")