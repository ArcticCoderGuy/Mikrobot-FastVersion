from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MT5 Activity Monitor
Tarkistaa Asiantuntijat ja Lehti vlilehdet 5 minuutin vlein
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import time

# MT5 Files
COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
SIGNAL_FILE = COMMON_PATH / "mikrobot_signal.json"
STATUS_FILE = COMMON_PATH / "mikrobot_status.txt"
MONITOR_LOG = COMMON_PATH / "mt5_monitor_log.txt"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MT5ActivityMonitor:
    """Seuraa MT5:n toimintaa ja signaalien kulkua"""
    
    def __init__(self):
        self.last_signal_id = 0
        self.signals_processed = 0
        self.monitoring_start = datetime.now()
        
    def log_to_file(self, message):
        """Kirjoita monitorointi lokiin"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            with open(MONITOR_LOG, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            logger.error(f"Log write error: {e}")
    
    def check_signal_activity(self):
        """Tarkista signaalien liikenne"""
        try:
            if SIGNAL_FILE.exists():
                with open(SIGNAL_FILE, 'r', encoding='ascii', errors='ignore') as f:
                    signal = json.load(f)
                
                current_id = signal.get('id', 0)
                symbol = signal.get('symbol', 'UNKNOWN')
                order_type = signal.get('order_type', 'UNKNOWN')
                comment = signal.get('comment', '')
                
                if current_id > self.last_signal_id:
                    self.signals_processed += 1
                    self.last_signal_id = current_id
                    
                    message = f"UUSI SIGNAALI #{current_id}: {order_type} {symbol} ({comment})"
                    logger.info(f"[SIGNAL] {message}")
                    self.log_to_file(f"SIGNAL: {message}")
                    
                    return True, message
                else:
                    return False, f"Signaali #{current_id} jo ksitelty"
            else:
                return False, "Signaalitiedostoa ei lydy"
                
        except Exception as e:
            error_msg = f"Signaalin lukuvirhe: {e}"
            logger.error(f"[ERROR] {error_msg}")
            self.log_to_file(f"ERROR: {error_msg}")
            return False, error_msg
    
    def check_ea_status(self):
        """Tarkista EA:n tila"""
        try:
            if STATUS_FILE.exists():
                with open(STATUS_FILE, 'r', encoding='ascii', errors='ignore') as f:
                    status = f.read()
                
                if "CONNECTION VERIFIED" in status:
                    return True, "EA yhteys OK"
                else:
                    return False, "EA yhteys epvarma"
            else:
                return False, "EA status-tiedostoa ei lydy"
                
        except Exception as e:
            return False, f"EA status virhe: {e}"
    
    async def monitor_cycle(self):
        """Yksi monitorointikierros"""
        logger.info("\n" + "="*60)
        logger.info("MT5 TOIMINNAN TARKISTUS")
        logger.info("="*60)
        
        # Tarkista signaalit
        signal_active, signal_msg = self.check_signal_activity()
        logger.info(f"[SIGNAALIT] {signal_msg}")
        
        # Tarkista EA status
        ea_ok, ea_msg = self.check_ea_status()
        logger.info(f"[EA STATUS] {ea_msg}")
        
        # Tilastot
        runtime = (datetime.now() - self.monitoring_start).total_seconds() / 60
        logger.info(f"[TILASTOT] Monitorointi: {runtime:.1f} min | Signaaleja ksitelty: {self.signals_processed}")
        
        # Ohjeet kyttjlle
        logger.info("\n[TARKISTA MT5]")
        logger.info("1. ASIANTUNTIJAT vlilehti:")
        logger.info("   - Pitisi nky Expert Advisor kynniss")
        logger.info("   - Hyminaama chartissa = EA toimii")
        logger.info("   - Ei virheilmoituksia")
        
        logger.info("\n2. LEHTI vlilehti:")
        logger.info("   - Uudet kaupat nkyvt")
        logger.info("   - 'order opened' tai 'deal' merkinnt")
        logger.info("   - Magic number: 20250802")
        
        logger.info("\n3. KAUPPA vlilehti:")
        logger.info("   - Avoimet positiot nkyvt")
        logger.info("   - Kommentit: 'Weekend Crypto X'")
        
        if signal_active:
            logger.info(f"\nOK TOIMINTA OK - Uusi signaali ksitelty: {signal_msg}")
        else:
            logger.info(f"\nWARNING  Ei uutta toimintaa - {signal_msg}")
        
        if ea_ok:
            logger.info("OK EA YHTEYS OK")
        else:
            logger.info(f"ERROR EA ONGELMA: {ea_msg}")
        
        # Kirjoita yhteenveto lokiin
        summary = f"Runtime: {runtime:.1f}min | Signaalit: {self.signals_processed} | EA: {'OK' if ea_ok else 'VIRHE'}"
        self.log_to_file(f"MONITOR: {summary}")
        
        logger.info("="*60)
    
    async def start_monitoring(self):
        """Aloita 5 minuutin vlein tapahtuva monitorointi"""
        logger.info(" MT5 ACTIVITY MONITOR KYNNISTYY")
        logger.info("Tarkistaa MT5:n toimintaa 5 minuutin vlein")
        logger.info("Paina Ctrl+C lopettaaksesi\n")
        
        try:
            cycle = 0
            while True:
                cycle += 1
                logger.info(f"\n>>> MONITOROINTIKIERROS {cycle} <<<")
                
                await self.monitor_cycle()
                
                logger.info(f"\nSeuraava tarkistus 5 minuutin pst...")
                logger.info("Voit tarkistaa MT5:st Asiantuntijat ja Lehti vlilehdet nyt!")
                
                # Odota 5 minuuttia
                await asyncio.sleep(300)  # 300 sekuntia = 5 minuuttia
                
        except KeyboardInterrupt:
            logger.info("\n MONITOROINTI LOPETETTU")
            logger.info(f"Yhteens ksitelty {self.signals_processed} signaalia")
            runtime = (datetime.now() - self.monitoring_start).total_seconds() / 60
            logger.info(f"Monitorointi kesti {runtime:.1f} minuuttia")

async def main():
    print("MT5 ACTIVITY MONITOR")
    print("=" * 40)
    print("Seuraa MT5:n Asiantuntijat ja Lehti vlilehti")
    print("Tarkistaa toimintaa 5 minuutin vlein")
    print("=" * 40)
    print()
    
    monitor = MT5ActivityMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(main())