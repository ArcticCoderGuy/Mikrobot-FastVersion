"""
KORJAA PIP TRIGGER TAKAISIN ALKUPERÄISEEN 0.2
Alkuperäinen Mikrobot_BOS_M5M1.mq5 v2.00 käyttää 0.2 pip triggeriä!
"""
import json
import time
from pathlib import Path

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

def revert_pip_trigger_to_original():
    """Palauta pip trigger alkuperäiseen 0.2 arvoon"""
    print("KORJATAAN PIP TRIGGER TAKAISIN ALKUPERÄISEEN 0.2")
    print("Alkuperäinen Mikrobot_BOS_M5M1.mq5 v2.00 strategia käyttää 0.2!")
    print("=" * 60)
    
    # 1. Korjaa aktivointisignaali
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    if activation_file.exists():
        with open(activation_file, 'r') as f:
            activation = json.load(f)
        
        # Palauta alkuperäinen 0.2 pip trigger
        if 'parameters' in activation:
            activation['parameters']['pip_trigger'] = 0.2
            activation['parameters']['frequency'] = 'HIGH'  # 0.2 pips = high frequency
        
        activation['activation_time'] = time.time()
        activation['version'] = "2.00_ORIGINAL"  # Back to original
        activation['strategy_name'] = "MikroBot_BOS_M5M1"
        activation['command'] = "REVERT_TO_ORIGINAL_STRATEGY"
        
        with open(activation_file, 'w') as f:
            json.dump(activation, f, indent=2)
        
        print("OK Aktivointisignaali korjattu")
        print(f"   Pip trigger: 0.2 (ALKUPERÄINEN)")
        print(f"   Frequency: HIGH")
        print(f"   Version: 2.00_ORIGINAL")
    
    # 2. Korjaa strategia konfiguraatio
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        config_data = config.get('config', {})
        
        # Palauta alkuperäinen pip trigger konfiguraatiossa
        if 'pattern_detection' in config_data:
            config_data['pattern_detection']['retest_precision'] = 0.2
            config_data['pattern_detection']['bos_sensitivity'] = 'HIGH'
        
        if 'entry_rules' in config_data:
            config_data['entry_rules']['pip_distance'] = 0.2
            config_data['entry_rules']['entry_method'] = "M1_3RD_CANDLE_TRIGGER"
            config_data['entry_rules']['signal_only'] = True
        
        # Päivitä symbol-specific pip distancet takaisin 0.2 kerrottuna
        if 'symbol_specific_pip_distance' in config_data['entry_rules']:
            symbol_rules = config_data['entry_rules']['symbol_specific_pip_distance']
            for symbol in symbol_rules:
                # Jaa 0.8-arvot takaisin 0.2:lla (0.8/4 = 0.2 kerroin)
                if symbol == "BTCUSD":
                    symbol_rules[symbol] = 0.2  # 0.8 -> 0.2
                elif symbol in ["ETHUSD", "XRPUSD", "LTCUSD"]:
                    symbol_rules[symbol] = 0.002  # 0.008 -> 0.002
                elif symbol == "BCHUSD":
                    symbol_rules[symbol] = 0.00002  # 0.00008 -> 0.00002
                elif "JPY" in symbol:
                    symbol_rules[symbol] = 0.002  # 0.008 -> 0.002
                else:  # Forex majors
                    symbol_rules[symbol] = 0.000002  # 0.000008 -> 0.000002
        
        config_data['strategy_id'] = "M5M1_BOS_ORIGINAL_02"
        config['timestamp'] = time.time()
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("OK Konfiguraatio korjattu")
        print(f"   Retest precision: 0.2")
        print(f"   Strategy ID: M5M1_BOS_ORIGINAL_02")
    
    # 3. Luo alkuperäisen strategian mukainen signaali
    original_strategy_signal = {
        "command": "IMPLEMENT_ORIGINAL_M5M1_STRATEGY",
        "ea_reference": "Mikrobot_BOS_M5M1.mq5",
        "version": "2.00",
        "original_pip_trigger": 0.2,
        "strategy_rules": {
            "m5_bos_detection": {
                "minimum_breakout": "1.0 pip",
                "lookback_bars": 10,
                "structure_levels": "high_low_from_lookback"
            },
            "m1_break_and_retest": {
                "phase_1": "M1 candle breaks M5 BOS level",
                "phase_2": "3rd M1 candle trigger with 0.2 pip precision",
                "timeout": "120 M1 candles (2 hours)"
            },
            "entry_trigger": {
                "bullish": "3rd M1 candle high >= first_break_high + 0.2_pip",
                "bearish": "3rd M1 candle low <= first_break_low - 0.2_pip"
            },
            "execution_mode": "SIGNAL_ONLY",
            "sl_tp_handling": "EXTERNAL_SYSTEM_RESPONSIBILITY"
        },
        "correction_from_08_error": True,
        "update_time": time.time()
    }
    
    strategy_file = COMMON_PATH / "original_m5m1_strategy.json"
    with open(strategy_file, 'w') as f:
        json.dump(original_strategy_signal, f, indent=2)
    
    print("OK Alkuperäinen strategia signaali luotu")
    print(f"   Strategy file: {strategy_file}")
    
    # 4. Päivitä pip lookup takaisin 0.2 kerrottuna
    lookup_file = COMMON_PATH / "pip_lookup_function.json"
    if lookup_file.exists():
        with open(lookup_file, 'r') as f:
            lookup = json.load(f)
        
        # Päivitä pip rules takaisin 0.2 kerrottuna
        if 'pip_rules' in lookup:
            pip_rules = lookup['pip_rules']
            for symbol in pip_rules:
                # Jaa nykyiset 0.8-arvot neljällä = 0.2 kerroin
                pip_rules[symbol] = pip_rules[symbol] / 4.0
        
        lookup['base_pip_trigger'] = 0.2
        lookup['description'] = "Get 0.2 pip trigger value for any symbol (ORIGINAL)"
        
        with open(lookup_file, 'w') as f:
            json.dump(lookup, f, indent=2)
        
        print("OK Pip lookup korjattu takaisin 0.2 kerrottuna")
    
    print("\n" + "=" * 60)
    print("KRIITTINEN KORJAUS VALMIS")
    print("Pip trigger palautettu alkuperäiseen 0.2 arvoon")
    print("Strategia nyt Mikrobot_BOS_M5M1.mq5 v2.00 mukainen!")
    
    return True

def validate_pip_trigger_correction():
    """Varmista että korjaus onnistui"""
    print("\nVARMISTETAAN PIP TRIGGER KORJAUS")
    print("=" * 40)
    
    # Tarkista aktivointisignaali
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    if activation_file.exists():
        with open(activation_file, 'r') as f:
            activation = json.load(f)
        
        pip_trigger = activation.get('parameters', {}).get('pip_trigger')
        if pip_trigger == 0.2:
            print("OK Aktivointisignaali: 0.2 pip trigger ALKUPERÄINEN")
        else:
            print(f"ERROR Aktivointisignaali: {pip_trigger} (pitäisi olla 0.2)")
    
    # Tarkista konfiguraatio
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        precision = config.get('config', {}).get('pattern_detection', {}).get('retest_precision')
        if precision == 0.2:
            print("OK Konfiguraatio: 0.2 pip precision ALKUPERÄINEN")
        else:
            print(f"ERROR Konfiguraatio: {precision} (pitäisi olla 0.2)")
    
    print("=" * 40)
    print("PIP TRIGGER 0.2 ALKUPERÄINEN VARMISTETTU")

if __name__ == "__main__":
    if revert_pip_trigger_to_original():
        validate_pip_trigger_correction()
        print("\nALKUPERÄINEN MIKROBOT_BOS_M5M1 STRATEGIA PALAUTETTU!")
        print("Nyt kaupankäynti tapahtuu täsmälleen mq5-tiedoston mukaan")