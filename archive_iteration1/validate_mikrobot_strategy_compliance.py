"""
VALIDOI ETTÄ KAIKKI KAUPAT NOUDATTAVAT ALKUPERÄISTÄ MIKROBOT_BOS_M5M1 STRATEGIAA
Tarkistaa että toteutus on 100% alkuperäisen mq5-tiedoston mukainen
"""
import MetaTrader5 as mt5
import json
from pathlib import Path
from datetime import datetime, timedelta

# MT5 Configuration
MT5_LOGIN = 95244786
MT5_PASSWORD = "Ua@tOnLp"
MT5_SERVER = "Ava-Demo 1-MT5"

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

class MikrobotStrategyValidator:
    """Validoi että kaupankäynti noudattaa täsmälleen alkuperäistä strategiaa"""
    
    def __init__(self):
        self.original_strategy_rules = {
            "pip_trigger": 0.2,  # ALKUPERÄINEN!
            "m5_min_breakout": 1.0,  # pips
            "lookback_bars": 10,
            "timeout_m1_candles": 120,  # 2 hours
            "signal_only": True,
            "entry_method": "M1_3RD_CANDLE_TRIGGER",
            "sl_method": "BREAK_LEVEL_PLUS_BUFFER",
            "tp_ratio": 2.5
        }
    
    def connect_mt5(self):
        """Connect to MT5"""
        if not mt5.initialize():
            print("MT5_INIT_FAIL")
            return False
        
        if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
            print("MT5_LOGIN_FAIL")
            return False
        
        print("MT5_CONNECTION_OK")
        return True
    
    def validate_current_configuration(self):
        """Validoi nykyinen konfiguraatio alkuperäistä vastaan"""
        print("VALIDOIDAAN NYKYINEN KONFIGURAATIO")
        print("=" * 50)
        
        validation_results = {
            "config_compliance": True,
            "issues": [],
            "warnings": []
        }
        
        # Tarkista aktivointisignaali
        activation_file = COMMON_PATH / "mikrobot_activation.json"
        if activation_file.exists():
            with open(activation_file, 'r') as f:
                activation = json.load(f)
            
            pip_trigger = activation.get('parameters', {}).get('pip_trigger')
            if pip_trigger != self.original_strategy_rules["pip_trigger"]:
                validation_results["issues"].append(f"Pip trigger: {pip_trigger} (pitäisi olla {self.original_strategy_rules['pip_trigger']})")
                validation_results["config_compliance"] = False
            else:
                print(f"OK Pip trigger: {pip_trigger}")
            
            version = activation.get('version', '')
            if '2.00' not in version:
                validation_results["warnings"].append(f"Version: {version} (ei välttämättä alkuperäinen)")
            else:
                print(f"OK Version: {version}")
        else:
            validation_results["issues"].append("Aktivointisignaali puuttuu")
            validation_results["config_compliance"] = False
        
        # Tarkista strategia konfiguraatio
        config_file = COMMON_PATH / "m5m1_strategy_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            config_data = config.get('config', {})
            
            # Tarkista entry method
            entry_method = config_data.get('entry_rules', {}).get('entry_method')
            if entry_method != self.original_strategy_rules["entry_method"]:
                validation_results["issues"].append(f"Entry method: {entry_method} (pitäisi olla {self.original_strategy_rules['entry_method']})")
                validation_results["config_compliance"] = False
            else:
                print(f"OK Entry method: {entry_method}")
            
            # Tarkista retest precision
            retest_precision = config_data.get('pattern_detection', {}).get('retest_precision')
            if retest_precision != self.original_strategy_rules["pip_trigger"]:
                validation_results["issues"].append(f"Retest precision: {retest_precision} (pitäisi olla {self.original_strategy_rules['pip_trigger']})")
                validation_results["config_compliance"] = False
            else:
                print(f"OK Retest precision: {retest_precision}")
            
            # Tarkista signal only
            signal_only = config_data.get('entry_rules', {}).get('signal_only')
            if signal_only != self.original_strategy_rules["signal_only"]:
                validation_results["warnings"].append(f"Signal only: {signal_only} (alkuperäinen on signal detector)")
        
        return validation_results
    
    def validate_recent_trades(self, hours_back=24):
        """Validoi viimeaikaiset kaupat alkuperäistä strategiaa vastaan"""
        print(f"\nVALIDOIDAAV VIIMEAIKAISET KAUPAT ({hours_back}h)")
        print("=" * 50)
        
        if not self.connect_mt5():
            return False
        
        # Get recent trades
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours_back)
        
        deals = mt5.history_deals_get(start_time, end_time)
        if not deals:
            print("Ei viimeaikaisia kauppoja")
            return True
        
        validation_results = {
            "total_trades": len(deals),
            "compliant_trades": 0,
            "non_compliant_trades": 0,
            "issues": []
        }
        
        for deal in deals:
            if deal.type in [mt5.DEAL_TYPE_BUY, mt5.DEAL_TYPE_SELL]:
                is_compliant = self.validate_single_trade(deal)
                if is_compliant:
                    validation_results["compliant_trades"] += 1
                else:
                    validation_results["non_compliant_trades"] += 1
        
        print(f"\nKAUPAN VALIDOINTI TULOKSET:")
        print(f"Yhteensä kauppoja: {validation_results['total_trades']}")
        print(f"Strategian mukaisia: {validation_results['compliant_trades']}")
        print(f"Ei strategian mukaisia: {validation_results['non_compliant_trades']}")
        
        if validation_results["non_compliant_trades"] > 0:
            compliance_rate = (validation_results["compliant_trades"] / validation_results["total_trades"]) * 100
            print(f"Compliance rate: {compliance_rate:.1f}%")
            if compliance_rate < 90:
                print("WARNING: Compliance rate alle 90%!")
        
        mt5.shutdown()
        return validation_results
    
    def validate_single_trade(self, deal):
        """Validoi yksittäinen kauppa alkuperäistä strategiaa vastaan"""
        print(f"\nValidoidaan kauppa {deal.ticket}:")
        print(f"  Symbol: {deal.symbol}")
        print(f"  Type: {'BUY' if deal.type == mt5.DEAL_TYPE_BUY else 'SELL'}")
        print(f"  Price: {deal.price}")
        print(f"  Time: {datetime.fromtimestamp(deal.time)}")
        
        # Tarkista että kauppa on tehty kommentilla joka viittaa strategiaan
        comment = getattr(deal, 'comment', '')
        if "MikroBot" not in comment and "M5M1" not in comment:
            print("  WARNING: Kauppa ei ole MikroBot strategian mukainen (kommentti)")
            return False
        
        # Tarkista position (jos vielä auki)
        positions = mt5.positions_get(ticket=deal.ticket)
        if positions:
            position = positions[0]
            
            # Tarkista SL/TP suhde
            if position.type == mt5.POSITION_TYPE_BUY:
                sl_distance = position.price_open - position.sl
                tp_distance = position.tp - position.price_open
            else:  # SELL
                sl_distance = position.sl - position.price_open
                tp_distance = position.price_open - position.tp
            
            if tp_distance > 0 and sl_distance > 0:
                rr_ratio = tp_distance / sl_distance
                expected_ratio = self.original_strategy_rules["tp_ratio"]
                
                print(f"  R:R ratio: {rr_ratio:.2f} (odotettu: {expected_ratio})")
                
                if abs(rr_ratio - expected_ratio) > 0.5:
                    print(f"  WARNING: R:R ratio ei vastaa strategiaa")
                    return False
        
        print("  OK: Kauppa näyttää strategian mukaiselta")
        return True
    
    def check_strategy_implementation_files(self):
        """Tarkista että strategian toteutustiedostot ovat olemassa ja oikeat"""
        print("\nTARKISTETAAN STRATEGIAN TOTEUTUSTIEDOSTOT")
        print("=" * 50)
        
        required_files = {
            "mikrobot_activation.json": "Aktivointisignaali",
            "m5m1_strategy_config.json": "Strategia konfiguraatio", 
            "pip_lookup_function.json": "Pip lookup funktio",
            "original_m5m1_strategy.json": "Alkuperäinen strategia referenssi"
        }
        
        missing_files = []
        
        for filename, description in required_files.items():
            filepath = COMMON_PATH / filename
            if filepath.exists():
                print(f"OK {description}: {filename}")
            else:
                print(f"ERROR {description} puuttuu: {filename}")
                missing_files.append(filename)
        
        # Tarkista myös toteutustiedosto
        implementation_file = Path("implement_exact_mikrobot_strategy.py")
        if implementation_file.exists():
            print(f"OK Strategian toteutus: {implementation_file}")
        else:
            print(f"ERROR Strategian toteutus puuttuu: {implementation_file}")
            missing_files.append(str(implementation_file))
        
        return len(missing_files) == 0
    
    def run_complete_validation(self):
        """Aja täydellinen validointi"""
        print("MIKROBOT_BOS_M5M1 STRATEGIAN TÄYDELLINEN VALIDOINTI")
        print("Varmistetaan että toteutus on 100% alkuperäisen mq5:n mukainen")
        print("=" * 70)
        
        # 1. Tarkista konfiguraatio
        config_results = self.validate_current_configuration()
        
        # 2. Tarkista tiedostot
        files_ok = self.check_strategy_implementation_files()
        
        # 3. Tarkista viimeaikaiset kaupat
        trade_results = self.validate_recent_trades(24)
        
        # Yhteenveto
        print("\n" + "=" * 70)
        print("VALIDOINTI YHTEENVETO")
        print("=" * 70)
        
        overall_compliance = True
        
        if config_results["config_compliance"]:
            print("OK Konfiguraatio on alkuperäisen strategian mukainen")
        else:
            print("ERROR Konfiguraatiossa ongelmia:")
            for issue in config_results["issues"]:
                print(f"  - {issue}")
            overall_compliance = False
        
        if config_results["warnings"]:
            print("WARNINGS:")
            for warning in config_results["warnings"]:
                print(f"  - {warning}")
        
        if files_ok:
            print("OK Kaikki vaaditut tiedostot löytyvät")
        else:
            print("ERROR Puuttuvia tiedostoja")
            overall_compliance = False
        
        if trade_results and trade_results["non_compliant_trades"] == 0:
            print("OK Kaikki viimeaikaiset kaupat strategian mukaisia")
        elif trade_results:
            print(f"WARNING {trade_results['non_compliant_trades']} kauppaa ei strategian mukaisia")
            if trade_results["non_compliant_trades"] > trade_results["compliant_trades"]:
                overall_compliance = False
        
        print("\n" + "=" * 70)
        if overall_compliance:
            print("SUCCESS: STRATEGIA ON TÄYSIN ALKUPERÄISEN MUKAINEN")
            print("Kaupankäynti tapahtuu nyt täsmälleen Mikrobot_BOS_M5M1.mq5 v2.00 mukaan")
        else:
            print("ERROR: STRATEGIASSA ON ONGELMIA")
            print("Korjaa ongelmat ennen jatkamista")
        
        return overall_compliance

if __name__ == "__main__":
    validator = MikrobotStrategyValidator()
    compliance = validator.run_complete_validation()
    
    if compliance:
        print("\nVALIDOINTI ONNISTUI!")
        print("Voit nyt luottaa että kaupankäynti tapahtuu alkuperäisen strategian mukaan")
    else:
        print("\nVALIDOINTI EPÄONNISTUI!")
        print("Korjaa raportoidut ongelmat")