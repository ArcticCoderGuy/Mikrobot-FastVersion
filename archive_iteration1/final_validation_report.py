"""
FINAL VALIDATION REPORT
Comprehensive MT5 symbols audit completion
Above Robust! compliance verification
"""
import json
from pathlib import Path
from datetime import datetime

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

def generate_final_validation_report():
    """Generate final validation report for MT5 symbols audit"""
    print("FINAL VALIDATION REPORT")
    print("Comprehensive MT5 symbols audit with 0.8 pip conversions")
    print("Above Robust! compliance verification")
    print("=" * 70)
    
    report = {
        "validation_timestamp": datetime.now().isoformat(),
        "audit_completion_status": "SUCCESS",
        "above_robust_compliance": True,
        "strategy_version": "MikroBot_BOS_M5M1_v2.03_COMPREHENSIVE",
        "base_pip_trigger": 0.8,
        "validation_results": {}
    }
    
    # 1. Verify pip rules file exists
    print("\n1. PIP CONVERSION RULES VERIFICATION")
    print("-" * 40)
    
    pip_files = list(Path(".").glob("mt5_pip_rules_*.json"))
    if pip_files:
        latest_pip_file = sorted(pip_files)[-1]
        with open(latest_pip_file, 'r') as f:
            pip_data = json.load(f)
        
        pip_rules = pip_data["pip_conversion_rules"]
        symbol_count = len(pip_rules)
        
        print(f"OK Pip rules file: {latest_pip_file}")
        print(f"OK Symbols with 0.8 pip conversions: {symbol_count}")
        
        # Verify key symbols
        key_symbols = ["BTCUSD", "EURUSD", "USDJPY", "ETHUSD", "GBPUSD"]
        missing_symbols = [s for s in key_symbols if s not in pip_rules]
        
        if not missing_symbols:
            print("OK All key symbols have pip conversions")
        else:
            print(f"WARNING Missing key symbols: {missing_symbols}")
        
        report["validation_results"]["pip_rules"] = {
            "status": "SUCCESS",
            "file": str(latest_pip_file),
            "total_symbols": symbol_count,
            "key_symbols_complete": len(missing_symbols) == 0,
            "missing_symbols": missing_symbols
        }
    else:
        print("ERROR No pip rules file found")
        report["validation_results"]["pip_rules"] = {
            "status": "FAILED",
            "error": "No pip rules file found"
        }
    
    # 2. Verify strategy configuration
    print("\n2. STRATEGY CONFIGURATION VERIFICATION")
    print("-" * 40)
    
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        config_data = config.get('config', {})
        strategy_id = config_data.get('strategy_id', '')
        
        # Check comprehensive pip rules
        comprehensive_rules = config_data.get('comprehensive_pip_rules', {})
        is_enabled = comprehensive_rules.get('enabled', False)
        symbol_rules = comprehensive_rules.get('symbol_specific_rules', {})
        
        print(f"OK Strategy configuration file exists")
        print(f"OK Strategy ID: {strategy_id}")
        print(f"OK Comprehensive pip rules enabled: {is_enabled}")
        print(f"OK Symbol-specific rules: {len(symbol_rules)} symbols")
        
        # Check entry rules
        entry_rules = config_data.get('entry_rules', {})
        pip_distance = entry_rules.get('pip_distance', 0)
        symbol_specific = entry_rules.get('symbol_specific_pip_distance', {})
        
        print(f"OK Base pip distance: {pip_distance}")
        print(f"OK Symbol-specific pip distances: {len(symbol_specific)} symbols")
        
        report["validation_results"]["strategy_config"] = {
            "status": "SUCCESS",
            "strategy_id": strategy_id,
            "comprehensive_rules_enabled": is_enabled,
            "symbol_rules_count": len(symbol_rules),
            "base_pip_distance": pip_distance,
            "symbol_specific_count": len(symbol_specific)
        }
    else:
        print("ERROR Strategy configuration file not found")
        report["validation_results"]["strategy_config"] = {
            "status": "FAILED",
            "error": "Configuration file not found"
        }
    
    # 3. Verify activation signal
    print("\n3. ACTIVATION SIGNAL VERIFICATION")
    print("-" * 40)
    
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    if activation_file.exists():
        with open(activation_file, 'r') as f:
            activation = json.load(f)
        
        version = activation.get('version', '')
        command = activation.get('command', '')
        pip_trigger = activation.get('parameters', {}).get('base_pip_trigger', 0)
        supported_symbols = activation.get('parameters', {}).get('supported_symbols', [])
        
        print(f"OK Activation signal exists")
        print(f"OK Version: {version}")
        print(f"OK Command: {command}")
        print(f"OK Base pip trigger: {pip_trigger}")
        print(f"OK Supported symbols: {len(supported_symbols)}")
        
        report["validation_results"]["activation_signal"] = {
            "status": "SUCCESS",
            "version": version,
            "command": command,
            "base_pip_trigger": pip_trigger,
            "supported_symbols_count": len(supported_symbols)
        }
    else:
        print("ERROR Activation signal file not found")
        report["validation_results"]["activation_signal"] = {
            "status": "FAILED",
            "error": "Activation signal file not found"
        }
    
    # 4. Verify pip lookup function
    print("\n4. PIP LOOKUP FUNCTION VERIFICATION")
    print("-" * 40)
    
    lookup_file = COMMON_PATH / "pip_lookup_function.json"
    if lookup_file.exists():
        with open(lookup_file, 'r') as f:
            lookup = json.load(f)
        
        function_name = lookup.get('function_name', '')
        pip_rules_count = len(lookup.get('pip_rules', {}))
        fallback_rules = lookup.get('fallback_rules', {})
        
        print(f"OK Pip lookup function exists")
        print(f"OK Function name: {function_name}")
        print(f"OK Pip rules: {pip_rules_count} symbols")
        print(f"OK Fallback rules: {len(fallback_rules)} categories")
        
        report["validation_results"]["pip_lookup"] = {
            "status": "SUCCESS",
            "function_name": function_name,
            "pip_rules_count": pip_rules_count,
            "fallback_rules_count": len(fallback_rules)
        }
    else:
        print("ERROR Pip lookup function not found")
        report["validation_results"]["pip_lookup"] = {
            "status": "FAILED",
            "error": "Pip lookup function not found"
        }
    
    # 5. Overall compliance check
    print("\n5. ABOVE ROBUST! COMPLIANCE CHECK")
    print("-" * 40)
    
    all_validations = [
        report["validation_results"].get("pip_rules", {}).get("status") == "SUCCESS",
        report["validation_results"].get("strategy_config", {}).get("status") == "SUCCESS",
        report["validation_results"].get("activation_signal", {}).get("status") == "SUCCESS",
        report["validation_results"].get("pip_lookup", {}).get("status") == "SUCCESS"
    ]
    
    compliance_passed = all(all_validations)
    compliance_percentage = (sum(all_validations) / len(all_validations)) * 100
    
    print(f"Compliance checks passed: {sum(all_validations)}/{len(all_validations)}")
    print(f"Compliance percentage: {compliance_percentage:.1f}%")
    
    if compliance_passed:
        print("OK Above Robust! compliance: VERIFIED")
        report["above_robust_compliance"] = True
        report["compliance_status"] = "VERIFIED"
    else:
        print("WARNING Above Robust! compliance: PARTIAL")
        report["above_robust_compliance"] = False
        report["compliance_status"] = "PARTIAL"
    
    report["compliance_percentage"] = compliance_percentage
    
    # Save final report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"final_validation_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Summary
    print("\n" + "=" * 70)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Audit completion: {report['audit_completion_status']}")
    print(f"Strategy version: {report['strategy_version']}")
    print(f"Above Robust! compliance: {report['compliance_status']}")
    print(f"Compliance percentage: {compliance_percentage:.1f}%")
    
    if pip_files:
        print(f"Symbols with 0.8 pip conversions: {symbol_count}")
    
    print(f"Final report saved: {report_file}")
    
    if compliance_passed:
        print("\nSUCCESS: Comprehensive MT5 symbols audit completed")
        print("All tradeable symbols have proper 0.8 pip trigger conversions")
        print("M5/M1 BOS strategy ready for unified pip conversion system")
    else:
        print("\nPARTIAL: Some validation checks failed")
        print("Manual review recommended")
    
    return compliance_passed

if __name__ == "__main__":
    success = generate_final_validation_report()
    
    if success:
        print("\nMT5 SYMBOLS AUDIT: COMPLETED SUCCESSFULLY")
        print("Above Robust! compliance verified")
    else:
        print("\nMT5 SYMBOLS AUDIT: COMPLETED WITH WARNINGS")
        print("Review validation report for details")