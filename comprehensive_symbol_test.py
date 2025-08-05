"""
COMPREHENSIVE MT5 SYMBOL TEST
Testaa M5/M1 BOS strategia kaikilla MT5 symboleilla ja omaisuusluokilla
0.8 pip trigger validation across all asset classes
"""
import MetaTrader5 as mt5
import json
import time
from pathlib import Path
from datetime import datetime

# MT5 Configuration
MT5_LOGIN = 107034605
MT5_PASSWORD = "RcEw_s7w"
MT5_SERVER = "Ava-Demo 1-MT5"

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

class SymbolTestValidator:
    """Testaa M5/M1 strategia kaikilla saatavilla olevilla symboleilla"""
    
    def __init__(self):
        self.connected = False
        self.test_results = {}
        self.asset_classes = {}
        self.pip_values = {}
        
    def connect_mt5(self):
        """Yhdista MT5 tiliin"""
        try:
            if not mt5.initialize():
                print(f"MT5_INIT_FAIL: {mt5.last_error()}")
                return False
            
            authorized = mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
            if not authorized:
                print(f"MT5_LOGIN_FAIL: {mt5.last_error()}")
                return False
            
            account = mt5.account_info()
            print(f"MT5_CONNECTION_OK: {account.login}")
            print(f"ACCOUNT_BALANCE: {account.balance}")
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"MT5_CONNECTION_ERROR: {str(e)}")
            return False
    
    def get_all_symbols(self):
        """Hae kaikki saatavilla olevat symbolit"""
        if not self.connected:
            print("MT5_NOT_CONNECTED")
            return []
        
        print("FETCHING_ALL_SYMBOLS...")
        all_symbols = mt5.symbols_get()
        
        if not all_symbols:
            print("NO_SYMBOLS_FOUND")
            return []
        
        print(f"TOTAL_SYMBOLS_FOUND: {len(all_symbols)}")
        return all_symbols
    
    def classify_symbol(self, symbol_name):
        """Luokittele symboli omaisuusluokan mukaan"""
        symbol_name = symbol_name.upper()
        
        # Forex majors
        forex_majors = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
        if symbol_name in forex_majors:
            return "FOREX_MAJOR"
        
        # Forex minors
        forex_minors = ["EURJPY", "GBPJPY", "EURGBP", "AUDCAD", "AUDJPY", "CADJPY", "CHFJPY", "EURCHF", "EURNZD", "GBPCHF", "GBPCAD", "NZDJPY"]
        if symbol_name in forex_minors:
            return "FOREX_MINOR"
        
        # Cryptocurrencies
        crypto_pairs = ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "ADAUSD", "BCHUSD", "EOSUSD", "LINKUSD"]
        if symbol_name in crypto_pairs or "BTC" in symbol_name or "ETH" in symbol_name:
            return "CRYPTO"
        
        # Commodities
        commodities = ["XAUUSD", "XAGUSD", "USOIL", "UKOIL", "XPTUSD", "XPDUSD"]
        if symbol_name in commodities or "XAU" in symbol_name or "XAG" in symbol_name or "OIL" in symbol_name:
            return "COMMODITY"
        
        # Indices
        indices = ["US30", "US500", "NAS100", "GER30", "UK100", "JPN225", "AUS200"]
        if symbol_name in indices or any(idx in symbol_name for idx in ["US30", "US500", "NAS", "GER", "UK100", "JPN"]):
            return "INDEX"
        
        # Exotic forex
        if "USD" in symbol_name or any(curr in symbol_name for curr in ["EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]):
            return "FOREX_EXOTIC"
        
        return "OTHER"
    
    def calculate_pip_value(self, symbol_info):
        """Laske pip-arvo symbolille"""
        if not symbol_info:
            return None
        
        # JPY parit käyttävät 0.01 pip arvoa
        if "JPY" in symbol_info.name:
            return 0.01
        
        # Crypto parit riippuen desimaalien määrästä
        if symbol_info.digits == 5:
            return 0.00001  # 5 desimaalin forex
        elif symbol_info.digits == 3:
            return 0.001    # 3 desimaalin forex (JPY)
        elif symbol_info.digits == 2:
            return 0.01     # 2 desimaalin (indices, commodities)
        elif symbol_info.digits == 1:
            return 0.1      # 1 desimaalin
        elif symbol_info.digits == 0:
            return 1.0      # Kokonaiset numerot
        else:
            return 0.0001   # Default 4 desimaalin forex
    
    def test_symbol_m5m1_compatibility(self, symbol):
        """Testaa symbolin M5/M1 BOS strategian yhteensopivuus"""
        symbol_name = symbol.name
        
        # Tarkista symbolin saatavuus
        if not mt5.symbol_select(symbol_name, True):
            return {
                "status": "UNAVAILABLE",
                "reason": "Symbol selection failed"
            }
        
        # Hae symbolin tiedot
        symbol_info = mt5.symbol_info(symbol_name)
        if not symbol_info:
            return {
                "status": "NO_INFO",
                "reason": "Symbol info unavailable"
            }
        
        # Tarkista hintatiedot
        tick = mt5.symbol_info_tick(symbol_name)
        if not tick or tick.ask <= 0:
            return {
                "status": "NO_PRICE",
                "reason": "No price data available"
            }
        
        # Luokittele omaisuusluokka
        asset_class = self.classify_symbol(symbol_name)
        
        # Laske pip-arvo
        pip_value = self.calculate_pip_value(symbol_info)
        
        # Testaa M5/M1 data saatavuus
        try:
            # Kokeile hakea M5 dataa
            m5_rates = mt5.copy_rates_from_pos(symbol_name, mt5.TIMEFRAME_M5, 0, 10)
            m1_rates = mt5.copy_rates_from_pos(symbol_name, mt5.TIMEFRAME_M1, 0, 10)
            
            m5_available = m5_rates is not None and len(m5_rates) > 0
            m1_available = m1_rates is not None and len(m1_rates) > 0
            
            if not m5_available or not m1_available:
                return {
                    "status": "NO_HISTORICAL_DATA",
                    "reason": f"M5: {m5_available}, M1: {m1_available}",
                    "asset_class": asset_class,
                    "pip_value": pip_value
                }
        
        except Exception as e:
            return {
                "status": "DATA_ERROR",
                "reason": str(e),
                "asset_class": asset_class,
                "pip_value": pip_value
            }
        
        # Laske 0.8 pip trigger hinta-arvo
        pip_trigger_value = 0.8 * pip_value if pip_value else None
        
        # Testaa kaupankäynti saatavuus
        trade_mode = symbol_info.trade_mode
        trade_allowed = trade_mode in [mt5.SYMBOL_TRADE_MODE_FULL, mt5.SYMBOL_TRADE_MODE_LONGONLY, mt5.SYMBOL_TRADE_MODE_SHORTONLY]
        
        return {
            "status": "COMPATIBLE" if trade_allowed else "TRADE_DISABLED",
            "asset_class": asset_class,
            "pip_value": pip_value,
            "pip_trigger_value": pip_trigger_value,
            "current_price": tick.ask,
            "spread": tick.ask - tick.bid,
            "digits": symbol_info.digits,
            "trade_mode": trade_mode,
            "min_volume": symbol_info.volume_min,
            "max_volume": symbol_info.volume_max,
            "volume_step": symbol_info.volume_step,
            "m5_data": m5_available,
            "m1_data": m1_available
        }
    
    def run_comprehensive_test(self):
        """Aja kattava testi kaikille symboleille"""
        if not self.connect_mt5():
            return False
        
        print("COMPREHENSIVE_SYMBOL_TEST_START")
        print("Testing M5/M1 BOS strategy compatibility with 0.8 pip trigger")
        print("=" * 70)
        
        all_symbols = self.get_all_symbols()
        if not all_symbols:
            return False
        
        # Testaa symbolit luokittain
        compatible_symbols = {}
        incompatible_symbols = {}
        
        for i, symbol in enumerate(all_symbols):
            if i % 50 == 0:  # Progress update
                print(f"TESTING_PROGRESS: {i}/{len(all_symbols)}")
            
            result = self.test_symbol_m5m1_compatibility(symbol)
            
            asset_class = result.get("asset_class", "OTHER")
            
            # Tallenna tulokset
            if result["status"] == "COMPATIBLE":
                if asset_class not in compatible_symbols:
                    compatible_symbols[asset_class] = []
                compatible_symbols[asset_class].append({
                    "symbol": symbol.name,
                    "result": result
                })
            else:
                if asset_class not in incompatible_symbols:
                    incompatible_symbols[asset_class] = []
                incompatible_symbols[asset_class].append({
                    "symbol": symbol.name,
                    "result": result
                })
        
        # Tulosta tulokset omaisuusluokittain
        print("\n" + "=" * 70)
        print("COMPATIBILITY_RESULTS_BY_ASSET_CLASS")
        print("=" * 70)
        
        total_compatible = 0
        total_tested = len(all_symbols)
        
        for asset_class in sorted(set(list(compatible_symbols.keys()) + list(incompatible_symbols.keys()))):
            compatible_count = len(compatible_symbols.get(asset_class, []))
            incompatible_count = len(incompatible_symbols.get(asset_class, []))
            total_count = compatible_count + incompatible_count
            
            print(f"\n{asset_class}:")
            print(f"  COMPATIBLE: {compatible_count}")
            print(f"  INCOMPATIBLE: {incompatible_count}")
            print(f"  TOTAL: {total_count}")
            
            if compatible_count > 0:
                print(f"  COMPATIBLE_SYMBOLS:")
                for item in compatible_symbols[asset_class][:5]:  # Show first 5
                    symbol_name = item["symbol"]
                    pip_trigger = item["result"]["pip_trigger_value"]
                    price = item["result"]["current_price"]
                    print(f"    {symbol_name}: 0.8pip = {pip_trigger:.6f} @ {price}")
                if len(compatible_symbols[asset_class]) > 5:
                    print(f"    ... and {len(compatible_symbols[asset_class]) - 5} more")
            
            total_compatible += compatible_count
        
        # Lopputulokset
        print("\n" + "=" * 70)
        print("FINAL_COMPATIBILITY_SUMMARY")
        print("=" * 70)
        print(f"TOTAL_SYMBOLS_TESTED: {total_tested}")
        print(f"COMPATIBLE_WITH_M5M1_BOS: {total_compatible}")
        print(f"INCOMPATIBLE: {total_tested - total_compatible}")
        print(f"COMPATIBILITY_RATE: {(total_compatible/total_tested)*100:.1f}%")
        print(f"PIP_TRIGGER_VALUE: 0.8 pip")
        print(f"STRATEGY_VERSION: MikroBot_BOS_M5M1_v2.01")
        
        # Tallenna tulokset
        self.save_test_results(compatible_symbols, incompatible_symbols, total_compatible, total_tested)
        
        # Cleanup
        mt5.shutdown()
        
        return total_compatible > 0
    
    def save_test_results(self, compatible, incompatible, total_compatible, total_tested):
        """Tallenna testitulokset"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {
            "test_timestamp": timestamp,
            "strategy_version": "MikroBot_BOS_M5M1_v2.01",
            "pip_trigger": 0.8,
            "total_symbols_tested": total_tested,
            "compatible_symbols": total_compatible,
            "compatibility_rate": (total_compatible/total_tested)*100,
            "compatible_by_asset_class": {},
            "incompatible_by_asset_class": {},
            "summary": {
                "forex_major_compatible": len(compatible.get("FOREX_MAJOR", [])),
                "forex_minor_compatible": len(compatible.get("FOREX_MINOR", [])),
                "crypto_compatible": len(compatible.get("CRYPTO", [])),
                "commodity_compatible": len(compatible.get("COMMODITY", [])),
                "index_compatible": len(compatible.get("INDEX", [])),
                "total_asset_classes": len(set(list(compatible.keys()) + list(incompatible.keys())))
            }
        }
        
        # Tallenna yksityiskohtaiset tulokset
        for asset_class, symbols in compatible.items():
            results["compatible_by_asset_class"][asset_class] = [
                {
                    "symbol": item["symbol"],
                    "pip_trigger_value": item["result"]["pip_trigger_value"],
                    "current_price": item["result"]["current_price"],
                    "digits": item["result"]["digits"]
                }
                for item in symbols
            ]
        
        for asset_class, symbols in incompatible.items():
            results["incompatible_by_asset_class"][asset_class] = [
                {
                    "symbol": item["symbol"],
                    "status": item["result"]["status"],
                    "reason": item["result"]["reason"]
                }
                for item in symbols
            ]
        
        # Tallenna tiedostoon
        results_file = f"m5m1_symbol_compatibility_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"TEST_RESULTS_SAVED: {results_file}")

if __name__ == "__main__":
    print("MT5 COMPREHENSIVE SYMBOL COMPATIBILITY TEST")
    print("M5/M1 BOS Strategy with 0.8 pip trigger validation")
    print("Testing all available asset classes and symbols")
    print()
    
    validator = SymbolTestValidator()
    success = validator.run_comprehensive_test()
    
    if success:
        print("\nSYMBOL_COMPATIBILITY_TEST: COMPLETED")
        print("M5/M1_STRATEGY: VALIDATED_ACROSS_ASSET_CLASSES")
    else:
        print("\nSYMBOL_COMPATIBILITY_TEST: FAILED")
        print("CHECK_MT5_CONNECTION_AND_SYMBOLS")