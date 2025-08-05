"""
CFD-INDICES PIP CONVERTER
Muuntaa 0.8 pip trigger oikeaan arvoon CFD-indekseille
Testaa että M5/M1 BOS strategia toimii oikeilla arvoilla
"""
import MetaTrader5 as mt5
import json
from pathlib import Path
from datetime import datetime

# MT5 Configuration
MT5_LOGIN = 107034605
MT5_PASSWORD = "RcEw_s7w"
MT5_SERVER = "Ava-Demo 1-MT5"

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

class CFDPipConverter:
    """CFD-indeksien pip-muunnin M5/M1 BOS strategialle"""
    
    def __init__(self):
        self.cfd_pip_rules = {}
        self.converted_configs = {}
        
    def connect_mt5(self):
        """Yhdista MT5"""
        if not mt5.initialize():
            print("MT5_INIT_FAIL")
            return False
        
        if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
            print("MT5_LOGIN_FAIL")
            return False
        
        print("MT5_CONNECTION_OK")
        return True
    
    def analyze_cfd_pip_requirements(self):
        """Analysoi CFD-indeksien pip-vaatimukset"""
        print("ANALYZING_CFD_PIP_REQUIREMENTS")
        print("=" * 50)
        
        # Hae CFD-indeksit
        all_symbols = mt5.symbols_get()
        cfd_indices = []
        
        for symbol in all_symbols:
            symbol_name = symbol.name.upper()
            
            # Etsi indeksit
            index_keywords = ["GERMANY", "AUS_", "NAS100", "US30", "UK100", "JPN225", "DAX", "FTSE", "SPX"]
            
            if any(keyword in symbol_name for keyword in index_keywords):
                if mt5.symbol_select(symbol.name, True):
                    symbol_info = mt5.symbol_info(symbol.name)
                    tick = mt5.symbol_info_tick(symbol.name)
                    
                    if symbol_info and tick and tick.ask > 0:
                        cfd_indices.append({
                            "symbol": symbol.name,
                            "price": tick.ask,
                            "digits": symbol_info.digits,
                            "point": symbol_info.point,
                            "tick_size": symbol_info.trade_tick_size,
                            "tick_value": symbol_info.trade_tick_value
                        })
        
        print(f"FOUND_{len(cfd_indices)}_CFD_INDICES")
        
        # Analysoi jokainen indeksi
        for cfd in cfd_indices:
            symbol = cfd["symbol"]
            price = cfd["price"]
            digits = cfd["digits"]
            point = cfd["point"]
            tick_size = cfd["tick_size"]
            
            print(f"\n{symbol}:")
            print(f"  Current Price: {price}")
            print(f"  Digits: {digits}")
            print(f"  Point: {point}")
            print(f"  Tick Size: {tick_size}")
            
            # Laske pip-arvo indeksille
            if "GERMANY" in symbol or "DAX" in symbol:
                # DAX: 1 point = 1 pip
                pip_value = 1.0
                pip_description = "1 point = 1 pip (DAX style)"
            elif "AUS_" in symbol:
                # AUS200: 1 point = 1 pip
                pip_value = 1.0
                pip_description = "1 point = 1 pip (ASX style)"
            elif price > 10000:
                # High value indices (US30, NAS100)
                pip_value = 1.0
                pip_description = "1 point = 1 pip (high value)"
            elif price > 1000:
                # Medium value indices
                pip_value = 0.1
                pip_description = "0.1 point = 1 pip (medium value)"
            elif digits == 0:
                # Integer pricing
                pip_value = 1.0
                pip_description = "1 point = 1 pip (integer)"
            elif digits == 1:
                # 1 decimal
                pip_value = 0.1
                pip_description = "0.1 point = 1 pip (1 decimal)"
            elif digits == 2:
                # 2 decimals
                pip_value = 0.01
                pip_description = "0.01 point = 1 pip (2 decimals)"
            else:
                # Default
                pip_value = point
                pip_description = f"point value = {point}"
            
            # Laske 0.8 pip trigger
            pip_trigger_value = 0.8 * pip_value
            
            print(f"  Pip Value: {pip_value} ({pip_description})")
            print(f"  0.8 Pip Trigger: {pip_trigger_value}")
            
            # Tallenna säännöt
            self.cfd_pip_rules[symbol] = {
                "pip_value": pip_value,
                "pip_trigger_value": pip_trigger_value,
                "description": pip_description,
                "price": price,
                "digits": digits
            }
        
        return len(cfd_indices) > 0
    
    def create_cfd_config_update(self):
        """Luo CFD-spesifinen konfiguraatio päivitys"""
        print("\nCREATING_CFD_CONFIG_UPDATE")
        print("=" * 50)
        
        # Lue nykyinen konfiguraatio
        config_file = COMMON_PATH / "m5m1_strategy_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            print("CONFIG_FILE_NOT_FOUND")
            return False
        
        # Lisää CFD-spesifiset pip-arvot
        config_data = config.get('config', {})
        
        # Luo CFD-osio
        if "cfd_indices" not in config_data:
            config_data["cfd_indices"] = {}
        
        config_data["cfd_indices"]["pip_conversion_rules"] = self.cfd_pip_rules
        config_data["cfd_indices"]["enabled"] = True
        config_data["cfd_indices"]["base_pip_trigger"] = 0.8
        
        # Päivitä strategy ID
        config_data["strategy_id"] = "M5M1_BOS_WEEKEND_08_CFD"
        config["timestamp"] = datetime.now().timestamp()
        
        # Tallenna päivitetty konfiguraatio
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("CFD_CONFIG_UPDATED")
        
        # Luo erillinen CFD-päivityssignaali
        cfd_update = {
            "command": "UPDATE_CFD_PIP_RULES",
            "cfd_pip_rules": self.cfd_pip_rules,
            "base_pip_trigger": 0.8,
            "timestamp": datetime.now().timestamp(),
            "strategy_version": "2.02_CFD"
        }
        
        cfd_update_file = COMMON_PATH / "cfd_pip_update.json"
        with open(cfd_update_file, 'w') as f:
            json.dump(cfd_update, f, indent=2)
        
        print(f"CFD_UPDATE_SIGNAL_SENT: {cfd_update_file}")
        
        return True
    
    def test_cfd_pip_conversion(self):
        """Testaa CFD pip-muunnos käytännössä"""
        print("\nTESTING_CFD_PIP_CONVERSION")
        print("=" * 50)
        
        test_results = {}
        
        for symbol, rules in self.cfd_pip_rules.items():
            print(f"\nTesting {symbol}:")
            
            # Hae nykyinen hinta
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                print(f"  NO_TICK_DATA")
                continue
            
            current_price = tick.ask
            pip_trigger_value = rules["pip_trigger_value"]
            
            # Simuloi M5 BOS break scenario
            # Oletetaan että M5 BOS level on 1% alempi/ylempi
            price_movement = current_price * 0.01  # 1% liike
            
            # BULLISH scenario: hinta nousee
            simulated_bos_level = current_price - price_movement
            simulated_break_high = current_price + (price_movement * 0.5)
            simulated_trigger_price = simulated_break_high + pip_trigger_value
            
            print(f"  Current Price: {current_price}")
            print(f"  Simulated BOS Level: {simulated_bos_level}")
            print(f"  Simulated Break High: {simulated_break_high}")
            print(f"  0.8 Pip Trigger: {pip_trigger_value}")
            print(f"  Trigger Price: {simulated_trigger_price}")
            
            # Tarkista että trigger on järkevä
            trigger_percentage = (pip_trigger_value / current_price) * 100
            
            if 0.001 <= trigger_percentage <= 0.1:  # 0.001% - 0.1% liike
                status = "OPTIMAL"
            elif trigger_percentage < 0.001:
                status = "TOO_SMALL"
            elif trigger_percentage > 0.1:
                status = "TOO_LARGE"
            else:
                status = "UNKNOWN"
            
            print(f"  Trigger Percentage: {trigger_percentage:.4f}%")
            print(f"  Status: {status}")
            
            test_results[symbol] = {
                "pip_trigger_value": pip_trigger_value,
                "trigger_percentage": trigger_percentage,
                "status": status,
                "current_price": current_price
            }
        
        # Yhteenveto
        print("\n" + "=" * 50)
        print("CFD_PIP_CONVERSION_TEST_SUMMARY")
        print("=" * 50)
        
        optimal_count = sum(1 for r in test_results.values() if r["status"] == "OPTIMAL")
        total_count = len(test_results)
        
        print(f"Total CFD Indices Tested: {total_count}")
        print(f"Optimal Pip Triggers: {optimal_count}")
        print(f"Success Rate: {(optimal_count/total_count)*100:.1f}%")
        
        # Tallenna testitulokset
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"cfd_pip_test_{timestamp}.json"
        
        final_results = {
            "timestamp": timestamp,
            "strategy_version": "MikroBot_BOS_M5M1_v2.02_CFD",
            "base_pip_trigger": 0.8,
            "test_results": test_results,
            "cfd_pip_rules": self.cfd_pip_rules,
            "summary": {
                "total_tested": total_count,
                "optimal_triggers": optimal_count,
                "success_rate": (optimal_count/total_count)*100 if total_count > 0 else 0
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(final_results, f, indent=2)
        
        print(f"Test results saved: {results_file}")
        
        return optimal_count == total_count
    
    def run_cfd_pip_conversion(self):
        """Aja koko CFD pip-muunnos prosessi"""
        print("CFD-INDICES PIP CONVERSION FOR M5/M1 BOS STRATEGY")
        print("Converting 0.8 pip trigger to CFD-specific values")
        print("=" * 60)
        
        if not self.connect_mt5():
            return False
        
        # 1. Analysoi CFD pip-vaatimukset
        if not self.analyze_cfd_pip_requirements():
            print("NO_CFD_INDICES_FOUND")
            return False
        
        # 2. Luo konfiguraatio päivitys
        if not self.create_cfd_config_update():
            print("CONFIG_UPDATE_FAILED")
            return False
        
        # 3. Testaa muunnos
        success = self.test_cfd_pip_conversion()
        
        # Cleanup
        mt5.shutdown()
        
        if success:
            print("\nCFD_PIP_CONVERSION: SUCCESS")
            print("M5/M1_BOS_STRATEGY: CFD_OPTIMIZED")
            print("0.8 pip trigger converted for all CFD indices")
        else:
            print("\nCFD_PIP_CONVERSION: ISSUES_DETECTED")
            print("Manual adjustment may be required")
        
        return success

if __name__ == "__main__":
    converter = CFDPipConverter()
    success = converter.run_cfd_pip_conversion()
    
    if success:
        print("\nCFD pip conversion completed successfully")
        print("M5/M1 BOS strategy optimized for CFD indices")
    else:
        print("\nCFD pip conversion needs manual review")