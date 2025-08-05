"""
VALIDATE CFD PIP CONVERSION
Testaa että CFD-muunnokset toimivat M5/M1 BOS strategiassa
"""
import json
from pathlib import Path
from datetime import datetime

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

def validate_cfd_conversion():
    """Validoi CFD pip-muunnos"""
    print("CFD PIP CONVERSION VALIDATION")
    print("Checking M5/M1 BOS strategy CFD compatibility")
    print("=" * 50)
    
    # Tarkista että konfiguraatio on päivitetty
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if not config_file.exists():
        print("CONFIG_FILE_MISSING")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    config_data = config.get('config', {})
    
    # Tarkista strategy ID
    strategy_id = config_data.get('strategy_id')
    if strategy_id != "M5M1_BOS_WEEKEND_08_CFD":
        print(f"STRATEGY_ID_WRONG: {strategy_id}")
        return False
    
    print(f"STRATEGY_ID: {strategy_id} - OK")
    
    # Tarkista CFD-osio
    cfd_section = config_data.get('cfd_indices', {})
    if not cfd_section.get('enabled'):
        print("CFD_SECTION_DISABLED")
        return False
    
    print("CFD_SECTION: ENABLED - OK")
    
    # Tarkista pip conversion rules
    pip_rules = cfd_section.get('pip_conversion_rules', {})
    if not pip_rules:
        print("NO_PIP_RULES")
        return False
    
    print(f"CFD_PIP_RULES: {len(pip_rules)} symbols - OK")
    
    # Validoi jokainen CFD-indeksi
    print("\nVALIDATING_CFD_SYMBOLS:")
    validation_passed = True
    
    for symbol, rules in pip_rules.items():
        pip_value = rules.get('pip_value')
        pip_trigger_value = rules.get('pip_trigger_value')
        description = rules.get('description')
        
        # Tarkista että pip_trigger_value = 0.8 * pip_value
        expected_trigger = 0.8 * pip_value
        
        if abs(pip_trigger_value - expected_trigger) < 0.000001:  # Float precision
            status = "OK"
        else:
            status = "FAIL"
            validation_passed = False
        
        print(f"  {symbol}:")
        print(f"    Pip Value: {pip_value}")
        print(f"    Trigger Value: {pip_trigger_value}")
        print(f"    Expected: {expected_trigger}")
        print(f"    Status: {status}")
        print(f"    Description: {description}")
    
    # Tarkista päivityssignaali
    cfd_update_file = COMMON_PATH / "cfd_pip_update.json"
    if cfd_update_file.exists():
        print("\nCFD_UPDATE_SIGNAL: FOUND - OK")
    else:
        print("\nCFD_UPDATE_SIGNAL: MISSING")
    
    # Lopputulos
    print("\n" + "=" * 50)
    if validation_passed:
        print("CFD_PIP_CONVERSION_VALIDATION: PASS")
        print("M5M1_BOS_STRATEGY: CFD_READY")
        print("All CFD indices have correct 0.8 pip triggers")
        
        # Näytä yhteenveto
        print("\nCFD_TRIGGER_SUMMARY:")
        for symbol, rules in pip_rules.items():
            print(f"  {symbol}: 0.8pip = {rules['pip_trigger_value']}")
        
        return True
    else:
        print("CFD_PIP_CONVERSION_VALIDATION: FAIL")
        print("CFD pip conversion has errors")
        return False

if __name__ == "__main__":
    success = validate_cfd_conversion()
    
    if success:
        print("\nCFD pip conversion successfully validated")
        print("M5/M1 BOS strategy ready for CFD indices")
    else:
        print("\nCFD pip conversion validation failed")
        print("Manual correction required")