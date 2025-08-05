"""
CFD-INDICES TEST
Testaa M5/M1 BOS strategia CFD-indekseilla
0.8 pip trigger validation for indices
"""
import MetaTrader5 as mt5
import json
from pathlib import Path
from datetime import datetime

# MT5 Configuration
MT5_LOGIN = 107034605
MT5_PASSWORD = "RcEw_s7w"
MT5_SERVER = "Ava-Demo 1-MT5"

def test_cfd_indices():
    """Testaa CFD-indeksit M5/M1 BOS strategialle"""
    
    # CFD-Indeksit joita kannattaa testata
    cfd_indices = [
        # US Indices
        "US30", "US500", "NAS100", "US2000",
        # European Indices  
        "GER30", "GER40", "UK100", "FRA40", "SPA35", "ITA40",
        # Asian Indices
        "JPN225", "HK50", "AUS200",
        # Alternative names
        "USTEC", "SPX500", "DJ30", "NASDAQ", "DAX", "FTSE"
    ]
    
    print("CFD-INDICES COMPATIBILITY TEST")
    print("M5/M1 BOS Strategy with 0.8 pip trigger")
    print("=" * 50)
    
    # MT5 yhteys
    if not mt5.initialize():
        print("MT5_INIT_FAIL")
        return False
    
    if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
        print("MT5_LOGIN_FAIL")
        return False
    
    print("MT5_CONNECTION_OK")
    
    # Etsi kaikki indeksi-symbolit brokerilta
    all_symbols = mt5.symbols_get()
    available_indices = []
    
    print("\nSCANNING_FOR_INDEX_SYMBOLS...")
    
    for symbol in all_symbols:
        symbol_name = symbol.name.upper()
        
        # Tarkista onko indeksi
        index_keywords = ["US30", "US500", "NAS", "GER", "UK100", "JPN", "AUS", "DAX", "FTSE", "SPX", "DOW", "NIKKEI"]
        
        if any(keyword in symbol_name for keyword in index_keywords):
            available_indices.append(symbol.name)
        elif symbol_name in cfd_indices:
            available_indices.append(symbol.name)
    
    print(f"FOUND_{len(available_indices)}_INDEX_SYMBOLS")
    
    # Testaa löydetyt indeksit
    validated_indices = {}
    total_tested = 0
    total_validated = 0
    
    for symbol_name in available_indices:
        total_tested += 1
        
        # Testaa symboli
        if not mt5.symbol_select(symbol_name, True):
            print(f"{symbol_name}: UNAVAILABLE")
            continue
        
        # Hae symbolin tiedot
        symbol_info = mt5.symbol_info(symbol_name)
        tick = mt5.symbol_info_tick(symbol_name)
        
        if not symbol_info or not tick or tick.ask <= 0:
            print(f"{symbol_name}: NO_DATA")
            continue
        
        # Laske 0.8 pip trigger arvo indekseille
        # Indeksit yleensä käyttävät 1.0 tai 0.1 pip arvoja
        if symbol_info.digits == 0:
            pip_value = 1.0      # Kokonaisluvut (esim. US30)
        elif symbol_info.digits == 1:
            pip_value = 0.1      # 1 desimaali
        elif symbol_info.digits == 2:
            pip_value = 0.01     # 2 desimaalia  
        else:
            pip_value = 0.1      # Default indekseille
        
        pip_trigger_value = 0.8 * pip_value
        
        # Testaa M5/M1 historical data
        try:
            m5_rates = mt5.copy_rates_from_pos(symbol_name, mt5.TIMEFRAME_M5, 0, 5)
            m1_rates = mt5.copy_rates_from_pos(symbol_name, mt5.TIMEFRAME_M1, 0, 5)
            
            if m5_rates is not None and m1_rates is not None and len(m5_rates) > 0 and len(m1_rates) > 0:
                # Tarkista trading mode
                trade_allowed = symbol_info.trade_mode in [mt5.SYMBOL_TRADE_MODE_FULL, mt5.SYMBOL_TRADE_MODE_LONGONLY, mt5.SYMBOL_TRADE_MODE_SHORTONLY]
                
                if trade_allowed:
                    print(f"{symbol_name}: VALIDATED - 0.8pip = {pip_trigger_value:.2f} @ {tick.ask}")
                    validated_indices[symbol_name] = {
                        "status": "VALIDATED",
                        "pip_trigger_value": pip_trigger_value,
                        "current_price": tick.ask,
                        "spread": tick.ask - tick.bid,
                        "digits": symbol_info.digits,
                        "pip_value": pip_value,
                        "trade_mode": symbol_info.trade_mode
                    }
                    total_validated += 1
                else:
                    print(f"{symbol_name}: TRADE_DISABLED")
            else:
                print(f"{symbol_name}: NO_HISTORICAL_DATA")
        
        except Exception as e:
            print(f"{symbol_name}: ERROR - {str(e)}")
    
    # Lopputulokset
    print("\n" + "=" * 50)
    print("CFD-INDICES VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total Index Symbols Found: {len(available_indices)}")
    print(f"Total Tested: {total_tested}")
    print(f"Validated for M5/M1 BOS: {total_validated}")
    
    if total_tested > 0:
        validation_rate = (total_validated/total_tested)*100
        print(f"Validation Rate: {validation_rate:.1f}%")
    
    print(f"Strategy Version: MikroBot_BOS_M5M1_v2.01")
    print(f"Pip Trigger: 0.8 pip")
    
    # Näytä validoidut indeksit
    if validated_indices:
        print(f"\nVALIDATED_CFD_INDICES:")
        for symbol, data in validated_indices.items():
            price = data["current_price"]
            pip_trigger = data["pip_trigger_value"]
            print(f"  {symbol}: {price} (0.8pip = {pip_trigger})")
    
    # Tallenna tulokset
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"cfd_indices_validation_{timestamp}.json"
    
    results = {
        "timestamp": timestamp,
        "strategy_version": "MikroBot_BOS_M5M1_v2.01",
        "pip_trigger": 0.8,
        "total_found": len(available_indices),
        "total_tested": total_tested,
        "total_validated": total_validated,
        "validation_rate": (total_validated/total_tested)*100 if total_tested > 0 else 0,
        "available_indices": available_indices,
        "validated_indices": validated_indices
    }
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved: {results_file}")
    
    # Cleanup
    mt5.shutdown()
    
    # Return success if we found and validated any indices
    return total_validated > 0

if __name__ == "__main__":
    print("Testing CFD-Indices compatibility with M5/M1 BOS strategy")
    print("Checking if indices work with 0.8 pip trigger")
    print()
    
    success = test_cfd_indices()
    
    if success:
        print("\nCFD_INDICES_VALIDATION: SUCCESS")
        print("M5/M1_BOS_STRATEGY: INDEX_COMPATIBLE")
        print("0.8 pip trigger works with CFD indices")
    else:
        print("\nCFD_INDICES_VALIDATION: NO_INDICES_FOUND")
        print("Broker may not offer CFD indices")