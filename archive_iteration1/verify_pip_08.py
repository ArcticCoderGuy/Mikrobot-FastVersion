"""
Varmista pip trigger 0.8 paivitys
"""
import json
from pathlib import Path

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

def check_pip_trigger():
    print("TARKISTETAAN PIP TRIGGER ARVO")
    print("=" * 35)
    
    # Aktivointisignaali
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    if activation_file.exists():
        with open(activation_file, 'r') as f:
            activation = json.load(f)
        
        pip_trigger = activation.get('parameters', {}).get('pip_trigger')
        frequency = activation.get('parameters', {}).get('frequency')
        version = activation.get('version')
        
        print(f"AKTIVOINTI:")
        print(f"  Pip trigger: {pip_trigger}")
        print(f"  Frequency: {frequency}")
        print(f"  Version: {version}")
    
    # Konfiguraatio
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        config_data = config.get('config', {})
        precision = config_data.get('pattern_detection', {}).get('retest_precision')
        strategy_id = config_data.get('strategy_id')
        
        print(f"\nKONFIGURAATIO:")
        print(f"  Retest precision: {precision}")
        print(f"  Strategy ID: {strategy_id}")
    
    # Paivityssignaali
    update_file = COMMON_PATH / "mikrobot_update.json"
    if update_file.exists():
        print(f"\nPAIVITYSSIGNAALI: Lahetetty EA:lle")
    
    print("\n" + "=" * 35)
    
    if pip_trigger == 0.8 and precision == 0.8:
        print("OK: PIP TRIGGER 0.8 ASETETTU OIKEIN")
        print("M5/M1 BOS strategia kayttaa 0.8 pip tarkkuutta")
        print("Frequency: MEDIUM (vahemman signaaleja, parempi laatu)")
        return True
    else:
        print("VAROITUS: Pip trigger ei ole 0.8")
        return False

if __name__ == "__main__":
    check_pip_trigger()