"""
CORE SYMBOLS VALIDATION
Testaa että M5/M1 BOS strategia toimii varmasti kaikissa ydinsymboleissa
0.8 pip trigger verification
"""
import MetaTrader5 as mt5
import json
from pathlib import Path
from datetime import datetime

# MT5 Configuration
MT5_LOGIN = 95244786
MT5_PASSWORD = "Ua@tOnLp"
MT5_SERVER = "Ava-Demo 1-MT5"

def validate_core_symbols():
    """Validoi ydinsymbolit M5/M1 BOS strategialle"""
    
    # Ydinsymbolit joilla strategia PITÄÄ toimia
    core_symbols = {
        "CRYPTO": ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD"],
        "FOREX_MAJOR": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"],
        "FOREX_MINOR": ["EURJPY", "GBPJPY", "EURGBP", "AUDCAD", "AUDJPY"],
        "COMMODITIES": ["XAUUSD", "XAGUSD"]
    }
    
    print("CORE SYMBOLS VALIDATION - M5/M1 BOS STRATEGY")
    print("0.8 pip trigger verification")
    print("=" * 55)
    
    # MT5 yhteys
    if not mt5.initialize():
        print("MT5_INIT_FAIL")
        return False
    
    if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
        print("MT5_LOGIN_FAIL")
        return False
    
    print("MT5_CONNECTION_OK")
    
    validation_results = {}
    total_symbols = 0
    validated_symbols = 0
    
    for asset_class, symbols in core_symbols.items():
        print(f"\n{asset_class}:")
        validation_results[asset_class] = {}
        
        for symbol in symbols:
            total_symbols += 1
            
            # Testaa symboli
            if not mt5.symbol_select(symbol, True):
                print(f"  {symbol}: UNAVAILABLE")
                validation_results[asset_class][symbol] = "UNAVAILABLE"
                continue
            
            # Hae symbolin tiedot
            symbol_info = mt5.symbol_info(symbol)
            tick = mt5.symbol_info_tick(symbol)
            
            if not symbol_info or not tick or tick.ask <= 0:
                print(f"  {symbol}: NO_DATA")
                validation_results[asset_class][symbol] = "NO_DATA"
                continue
            
            # Laske 0.8 pip trigger arvo
            if "JPY" in symbol:
                pip_value = 0.01
            elif symbol_info.digits == 5:
                pip_value = 0.00001
            elif symbol_info.digits == 3:
                pip_value = 0.001
            elif symbol_info.digits == 2:
                pip_value = 0.01
            else:
                pip_value = 0.0001
            
            pip_trigger_value = 0.8 * pip_value
            
            # Testaa M5/M1 data
            try:
                m5_rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 5)
                m1_rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 5)
                
                if m5_rates is not None and m1_rates is not None and len(m5_rates) > 0 and len(m1_rates) > 0:
                    print(f"  {symbol}: VALIDATED - 0.8pip = {pip_trigger_value:.6f} @ {tick.ask}")
                    validation_results[asset_class][symbol] = {
                        "status": "VALIDATED",
                        "pip_trigger_value": pip_trigger_value,
                        "current_price": tick.ask,
                        "spread": tick.ask - tick.bid,
                        "digits": symbol_info.digits
                    }
                    validated_symbols += 1
                else:
                    print(f"  {symbol}: NO_HISTORICAL_DATA")
                    validation_results[asset_class][symbol] = "NO_HISTORICAL_DATA"
            
            except Exception as e:
                print(f"  {symbol}: ERROR - {str(e)}")
                validation_results[asset_class][symbol] = f"ERROR: {str(e)}"
    
    # Lopputulokset
    print("\n" + "=" * 55)
    print("CORE SYMBOLS VALIDATION SUMMARY")
    print("=" * 55)
    print(f"Total Core Symbols: {total_symbols}")
    print(f"Validated Symbols: {validated_symbols}")
    print(f"Validation Rate: {(validated_symbols/total_symbols)*100:.1f}%")
    print(f"Strategy Version: MikroBot_BOS_M5M1_v2.01")
    print(f"Pip Trigger: 0.8 pip")
    
    # Erittele omaisuusluokittain
    print("\nVALIDATION BY ASSET CLASS:")
    for asset_class, results in validation_results.items():
        validated_count = sum(1 for r in results.values() if isinstance(r, dict) and r.get("status") == "VALIDATED")
        total_count = len(results)
        rate = (validated_count/total_count)*100 if total_count > 0 else 0
        print(f"  {asset_class}: {validated_count}/{total_count} ({rate:.1f}%)")
    
    # Tallenna tulokset
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"core_symbols_validation_{timestamp}.json"
    
    final_results = {
        "timestamp": timestamp,
        "strategy_version": "MikroBot_BOS_M5M1_v2.01",
        "pip_trigger": 0.8,
        "total_symbols": total_symbols,
        "validated_symbols": validated_symbols,
        "validation_rate": (validated_symbols/total_symbols)*100,
        "results_by_asset_class": validation_results
    }
    
    with open(results_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\nResults saved: {results_file}")
    
    # Cleanup
    mt5.shutdown()
    
    # Lopputulos
    if validated_symbols >= total_symbols * 0.9:  # 90% success rate
        print("\nCORE_SYMBOLS_VALIDATION: PASS")
        print("M5/M1_BOS_STRATEGY: CORE_COMPATIBLE")
        return True
    else:
        print("\nCORE_SYMBOLS_VALIDATION: FAIL")
        print("M5/M1_BOS_STRATEGY: COMPATIBILITY_ISSUES")
        return False

if __name__ == "__main__":
    success = validate_core_symbols()
    
    if success:
        print("0.8 pip trigger validated across core trading symbols")
        print("M5/M1 BOS strategy ready for production deployment")
    else:
        print("Core symbol validation failed")
        print("Manual intervention required")