from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Aktivoi MikroBot M5/M1 BOS Strategy
Sinun oikea price-action strategia
"""

import json
import time
from pathlib import Path
import logging

# Signal files
COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
ACTIVATION_SIGNAL = COMMON_PATH / "mikrobot_activation.json"
STATUS_FILE = COMMON_PATH / "mikrobot_status.txt"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def activate_m5m1_strategy():
    """Aktivoi MikroBot M5/M1 BOS strategia"""
    
    activation_command = {
        "command": "ACTIVATE_STRATEGY",
        "strategy_name": "MikroBot_BOS_M5M1",
        "version": "2.00",
        "parameters": {
            "timeframes": ["M5", "M1"],
            "signal_type": "BOS_BREAK_RETEST",
            "pip_trigger": 0.2,
            "frequency": "HIGH",
            "symbols": ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD"],
            "risk_management": {
                "position_size": 0.05,
                "stop_loss_method": "BREAK_LEVEL",
                "take_profit_ratio": 2.5,
                "max_positions": 3
            }
        },
        "activation_time": time.time(),
        "account": 107034605,
        "source": "Python_Activation"
    }
    
    logger.info("AKTIVOIDAAN M5/M1 BOS STRATEGIA")
    logger.info("=" * 50)
    logger.info("Strategia: MikroBot_BOS_M5M1 v2.00")
    logger.info("Aikakehykset: M5 (primary) + M1 (confirmation)")
    logger.info("Signaali tyyppi: Break of Structure + Retest")
    logger.info("Pip trigger: 0.2 (erittin tarkka)")
    logger.info("Symbolit: BTC, ETH, XRP, LTC")
    logger.info("=" * 50)
    
    # Kirjoita aktivointisignaali
    with open(ACTIVATION_SIGNAL, 'w', encoding='ascii', errors='ignore') as f:
        json.dump(activation_command, f, indent=2)
    
    logger.info(f"Aktivointisignaali lhetetty: {ACTIVATION_SIGNAL}")
    
    # Odota hetki ja tarkista status
    time.sleep(3)
    
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r', encoding='ascii', errors='ignore') as f:
            status = f.read()
        
        logger.info("\nEA STATUS:")
        logger.info(status)
        
        if "CONNECTION VERIFIED" in status:
            logger.info("\nOK EA YHTEYS OK - M5/M1 strategia aktivoitavissa")
            return True
        else:
            logger.warning("\nWARNING EA status epvarma")
            return False
    else:
        logger.warning("\nERROR EA ei vastaa")
        return False

def send_strategy_config():
    """Lhet yksityiskohtainen strategia konfiguraatio"""
    
    config_signal = {
        "command": "CONFIG_M5M1_STRATEGY", 
        "config": {
            "strategy_id": "M5M1_BOS_WEEKEND",
            "primary_timeframe": "M5",
            "confirmation_timeframe": "M1", 
            "pattern_detection": {
                "bos_sensitivity": "HIGH",
                "retest_precision": 0.2,
                "break_confirmation": "VOLUME_SPIKE",
                "false_break_filter": True
            },
            "entry_rules": {
                "entry_method": "RETEST_TRIGGER",
                "pip_distance": 0.2,
                "volume_confirmation": True,
                "time_filter": "EXCLUDE_NEWS"
            },
            "exit_rules": {
                "stop_loss": "BREAK_LOW_HIGH",
                "take_profit_1": "2.5R",
                "take_profit_2": "4R", 
                "trailing_stop": True
            },
            "risk_parameters": {
                "max_risk_per_trade": 1.0,  # 1% per trade
                "position_size": 0.05,
                "max_daily_loss": 5.0,      # 5% daily limit
                "correlation_filter": True
            },
            "active_symbols": ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD"],
            "session_config": {
                "weekend_mode": True,
                "crypto_focus": True,
                "24_7_monitoring": True
            }
        },
        "timestamp": time.time()
    }
    
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    
    with open(config_file, 'w', encoding='ascii', errors='ignore') as f:
        json.dump(config_signal, f, indent=2)
    
    logger.info(f"Strategia konfiguraatio lhetetty: {config_file}")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    print("MIKROBOT M5/M1 BOS STRATEGY ACTIVATION")
    print("Aktivoidaan sinun oikea price-action strategia")
    print()
    
    # Aktivoi strategia
    success = activate_m5m1_strategy()
    
    if success:
        print("\nOK Strategia aktivointi onnistui!")
        print("Lhetetn yksityiskohtainen konfiguraatio...")
        
        # Lhet config
        send_strategy_config()
        
        print("\nROCKET M5/M1 BOS STRATEGIA KYNNISTYY!")
        print("- Break of Structure detection")
        print("- M1 retest confirmation")  
        print("- 0.2 pip precision triggers")
        print("- Weekend crypto focus")
        print("\nTarkista MT5 Asiantuntijat-vlilehti!")
        
    else:
        print("\nERROR Strategia aktivointi eponnistui")
        print("Tarkista ett EA on kynniss MT5:ss")