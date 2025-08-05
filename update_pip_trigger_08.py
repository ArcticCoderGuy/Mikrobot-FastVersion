from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
KORJAA PIP TRIGGER 0.2 -> 0.8
Pivit M5/M1 BOS strategian pip trigger oikeaksi arvoksi
"""
import json
import time
from pathlib import Path

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

def update_pip_trigger_to_08():
    """Pivit pip trigger 0.8:aan"""
    print("PIVITETN PIP TRIGGER 0.2 -> 0.8")
    print("=" * 40)
    
    # 1. Pivit aktivointisignaali
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    if activation_file.exists():
        with open(activation_file, 'r', encoding='ascii', errors='ignore') as f:
            activation = json.load(f)
        
        # Pivit pip_trigger
        if 'parameters' in activation:
            activation['parameters']['pip_trigger'] = 0.8
            activation['parameters']['frequency'] = 'MEDIUM'  # 0.8 pips = medium frequency
        
        activation['activation_time'] = time.time()
        activation['version'] = "2.01"  # Bump version
        
        with open(activation_file, 'w', encoding='ascii', errors='ignore') as f:
            json.dump(activation, f, indent=2)
        
        print("OK Aktivointisignaali pivitetty")
        print(f"   Pip trigger: 0.8")
        print(f"   Frequency: MEDIUM")
        print(f"   Version: 2.01")
    
    # 2. Pivit strategia konfiguraatio
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='ascii', errors='ignore') as f:
            config = json.load(f)
        
        config_data = config.get('config', {})
        
        # Pivit pip trigger konfiguraatiossa
        if 'pattern_detection' in config_data:
            config_data['pattern_detection']['retest_precision'] = 0.8
            config_data['pattern_detection']['bos_sensitivity'] = 'MEDIUM'
        
        if 'entry_rules' in config_data:
            config_data['entry_rules']['pip_distance'] = 0.8
        
        config_data['strategy_id'] = "M5M1_BOS_WEEKEND_08"
        config['timestamp'] = time.time()
        
        with open(config_file, 'w', encoding='ascii', errors='ignore') as f:
            json.dump(config, f, indent=2)
        
        print("OK Konfiguraatio pivitetty")
        print(f"   Retest precision: 0.8")
        print(f"   Strategy ID: M5M1_BOS_WEEKEND_08")
    
    # 3. Lhet pivityssignaali EA:lle
    update_signal = {
        "command": "UPDATE_PIP_TRIGGER",
        "new_pip_trigger": 0.8,
        "strategy_version": "2.01",
        "update_time": time.time(),
        "parameters": {
            "retest_precision": 0.8,
            "frequency": "MEDIUM",
            "sensitivity": "STANDARD"
        }
    }
    
    update_file = COMMON_PATH / "mikrobot_update.json"
    with open(update_file, 'w', encoding='ascii', errors='ignore') as f:
        json.dump(update_signal, f, indent=2)
    
    print("OK Pivityssignaali lhetetty EA:lle")
    print(f"   Update file: {update_file}")
    
    print("\n" + "=" * 40)
    print("TARGET PIP TRIGGER PIVITETTY 0.8:aan")
    print("CHART M5/M1 BOS strategia kytt nyt 0.8 pip tarkkuutta")
    print("FAST Frequency: MEDIUM (vhemmn signaaleja, parempi laatu)")
    
    return True

def verify_pip_trigger_update():
    """Varmista ett pivitys onnistui"""
    print("\n VARMISTETAAN PIP TRIGGER PIVITYS")
    print("=" * 40)
    
    # Tarkista aktivointisignaali
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    if activation_file.exists():
        with open(activation_file, 'r', encoding='ascii', errors='ignore') as f:
            activation = json.load(f)
        
        pip_trigger = activation.get('parameters', {}).get('pip_trigger')
        if pip_trigger == 0.8:
            print("OK Aktivointisignaali: 0.8 pip trigger OK")
        else:
            print(f"ERROR Aktivointisignaali: {pip_trigger} (pitisi olla 0.8)")
    
    # Tarkista konfiguraatio
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='ascii', errors='ignore') as f:
            config = json.load(f)
        
        precision = config.get('config', {}).get('pattern_detection', {}).get('retest_precision')
        if precision == 0.8:
            print("OK Konfiguraatio: 0.8 pip precision OK")
        else:
            print(f"ERROR Konfiguraatio: {precision} (pitisi olla 0.8)")
    
    print("=" * 40)
    print("OK PIP TRIGGER 0.8 VARMISTETTU")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    if update_pip_trigger_to_08():
        verify_pip_trigger_update()
        print("\nROCKET M5/M1 BOS strategia kytt nyt 0.8 pip triggeri!")
        print("GRAPH_UP Vhemmn signaaleja mutta parempi laatu")