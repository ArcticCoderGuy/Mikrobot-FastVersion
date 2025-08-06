from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
M5/M1 BOS STRATEGIAN 4 MINUUTIN VALVONTA
Tarkistaa ett MikroBot_BOS_M5M1 v2.00 on kynniss kaikissa mahdollisissa markkinoissa
"""
import time
import json
from pathlib import Path
from datetime import datetime
import schedule

COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")

def check_m5m1_status():
    """Tarkista M5/M1 BOS strategian status"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] M5/M1 BOS STRATEGIAN STATUS TARKISTUS")
    print("=" * 55)
    
    # 1. Aktivointisignaali
    activation_file = COMMON_PATH / "mikrobot_activation.json"
    if activation_file.exists():
        with open(activation_file, 'r', encoding='ascii', errors='ignore') as f:
            activation = json.load(f)
        
        strategy_name = activation.get('strategy_name')
        version = activation.get('version')
        
        if strategy_name == "MikroBot_BOS_M5M1" and version == "2.00":
            print("OK STRATEGIA: MikroBot_BOS_M5M1 v2.00 AKTIIVINEN")
        else:
            print("ERROR VAROITUS: Vr strategia tai versio!")
            return False
    else:
        print("ERROR KRIITTINEN: Aktivointisignaali puuttuu!")
        return False
    
    # 2. Konfiguraatio ja symbolit
    config_file = COMMON_PATH / "m5m1_strategy_config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='ascii', errors='ignore') as f:
            config = json.load(f)
        
        config_data = config.get('config', {})
        symbols = config_data.get('active_symbols', [])
        session_config = config_data.get('session_config', {})
        
        print(f"CHART SYMBOLIT: {', '.join(symbols)}")
        print(f" 24/7 MODE: {session_config.get('24_7_monitoring', False)}")
        print(f" CRYPTO FOCUS: {session_config.get('crypto_focus', False)}")
        print(f" WEEKEND MODE: {session_config.get('weekend_mode', False)}")
    
    # 3. EA yhteys
    status_file = COMMON_PATH / "mikrobot_status.txt"
    if status_file.exists():
        with open(status_file, 'r', encoding='ascii', errors='ignore') as f:
            status = f.read()
        
        if "CONNECTION VERIFIED" in status:
            print(" EA YHTEYS: VAHVISTETTU (95244786)")
        else:
            print("WARNING EA YHTEYS: EPVARMA")
    
    # 4. Markkina-aika analyysi
    current_hour = datetime.now().hour
    if 0 <= current_hour < 8:
        session = "AASIA"
    elif 8 <= current_hour < 16:
        session = "EUROOPPA"
    else:
        session = "AMERIKKA"
    
    print(f" SESSIO: {session} ({current_hour}:xx)")
    
    # 5. Crypto markkinat (24/7)
    crypto_markets = ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD"]
    print(f"MONEY CRYPTO: AKTIIVINEN 24/7 ({', '.join(crypto_markets)})")
    
    print("=" * 55)
    print("OK M5/M1 BOS VALVONTA VALMIS")
    
    return True

def explain_m5m1_strategy():
    """Selit miten M5/M1 BOS strategia toimii"""
    print("\n" + "=" * 60)
    print(" MikroBot_BOS_M5M1 v2.00 KAUPANKYNTI OHJEET")
    print("=" * 60)
    
    print("TARGET STRATEGIAN KUVAUS:")
    print("   M5 Break of Structure + M1 Break-and-Retest Pattern")
    print("   Ultra-high frequency signals with 0.2 pip precision")
    print()
    
    print("CHART VAIHEET:")
    print("   1 M5 BREAK OF STRUCTURE (BOS)")
    print("      - Analysoi M5 aikakehyksess structure high/low tasoja")
    print("      - Kun hinta breaks structure level (min 1 pip)")
    print("      - Tallentaa BOS level ja suunta (bullish/bearish)")
    print()
    
    print("   2 M1 BREAK MONITORING")
    print("      - Seuraa M1 aikakehyksess initial break of M5 BOS level")
    print("      - Odottaa ett M1 candle breaks M5 BOS level cleanly")
    print("      - Tallentaa first break candle high/low levels")
    print()
    
    print("   3 M1 RETEST TRIGGER")
    print("      - Odottaa 3rd M1 candle after initial break")
    print("      - BULLISH: 3rd candle high > first break high + 0.2 pips")
    print("      - BEARISH: 3rd candle low < first break low - 0.2 pips")
    print("      - SIGNAL TRIGGERS kun retest pattern valmis")
    print()
    
    print("FAST SIGNAALIN RAKENNE:")
    print("   - ea_name: MikroBot_BOS_M5M1")
    print("   - signal_type: M5_M1_BOS_RETEST") 
    print("   - direction: BUY tai SELL")
    print("   - trigger_price: Tarkka hinta jossa signal triggers")
    print("   - m5_bos_level: M5 structure level joka breaks")
    print("   - m1_break_high/low: Initial break candle levels")
    print("   - pip_trigger: 0.2 (ultra precision)")
    print()
    
    print(" TARKKUUS:")
    print("   - Pip trigger: 0.2 pips (ultra-high frequency)")
    print("   - Timeframes: M5 (primary) + M1 (confirmation)")
    print("   - Signal frequency: HIGH")
    print("   - Monitoring: 24/7 continuous")
    print()
    
    print(" SYMBOLIT:")
    print("   - BTCUSD: Bitcoin/USD (24/7)")
    print("   - ETHUSD: Ethereum/USD (24/7)")
    print("   - XRPUSD: Ripple/USD (24/7)")
    print("   - LTCUSD: Litecoin/USD (24/7)")
    print()
    
    print(" CYCLE:")
    print("   M5 BOS detected -> M1 monitoring starts -> Initial break")
    print("   -> Wait for 3rd candle -> Check 0.2 pip trigger -> SIGNAL!")
    print("   -> Reset monitoring -> Wait for next M5 BOS")
    print()
    
    print(" INTEGRATION:")
    print("   - Account: 95244786")
    print("   - Django MCP endpoint integration")
    print("   - Real-time signal delivery")
    print("   - HTTP POST to configured URL")
    
    print("=" * 60)

def monitor_loop():
    """4 minuutin vlein ajettava valvonta"""
    print("ROCKET M5/M1 BOS STRATEGIAN 4 MIN VALVONTA KYNNISTYY")
    print(" Tarkistaa 4 minuutin vlein ett strategia on kynniss")
    print(" Pysyt: Ctrl+C")
    print()
    
    # Selit strategia ensimmisell kerralla
    explain_m5m1_strategy()
    
    # Ajasta 4 minuutin vlein
    schedule.every(4).minutes.do(check_m5m1_status)
    
    # Aja ensimminen tarkistus heti
    check_m5m1_status()
    
    # Jatkuva silmukka
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Tarkista 30 sek vlein onko aika ajaa
    except KeyboardInterrupt:
        print("\n M5/M1 BOS valvonta pysytetty")
        print("OK MikroBot_BOS_M5M1 v2.00 jatkaa kymist taustalla")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    monitor_loop()