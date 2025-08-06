#!/usr/bin/env python3
"""
MIKROBOT FASTVERSION v2.0 - PRODUCTION STARTER
===============================================

Lightning Bolt Strategy with iMessage notifications
- 7 Major forex pairs
- 21 Minor/Cross forex pairs  
- 10 Top crypto CFDs
- Real-time iMessage alerts for all 3 phases
"""

import asyncio
import logging
import sys
import signal
from datetime import datetime, time
import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mikrobot_production.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import Mikrobot components
from src.mikrobot_v2.core.mt5_webhook_connector import MT5WebhookConnector
from src.mikrobot_v2.strategies.lightning_bolt import LightningBoltStrategy
from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier

class MikrobotProduction:
    """Production Mikrobot with iMessage notifications"""
    
    def __init__(self):
        # Trading components
        self.mt5 = MT5WebhookConnector()
        self.lightning_bolt = LightningBoltStrategy(self.mt5)
        
        # Trading schedule (Finnish timezone)
        self.finland_tz = pytz.timezone('Europe/Helsinki')
        self.stop_time = time(10, 0)  # 10:00 Finnish time
        
        # Production settings
        self.running = True
        self.scan_interval = 30  # 30 seconds between scans
        self.total_trades = 0
        
        logger.info("🚀 MIKROBOT PRODUCTION v2.0 initialized")
        logger.info(f"📱 iMessage notifications: +358440606044")
        logger.info(f"📈 Trading {len(self.mt5.all_symbols)} instruments")
        self.log_symbol_list()
    
    def log_symbol_list(self):
        """Log trading instruments"""
        logger.info("📊 TRADING INSTRUMENTS:")
        logger.info(f"   💰 Major Forex: {', '.join(self.mt5.major_pairs)}")
        logger.info(f"   💱 Minor/Cross: {', '.join(self.mt5.minor_pairs)}")  
        logger.info(f"   🪙 Top 10 Crypto: {', '.join(self.mt5.crypto_symbols)}")
        logger.info(f"   📈 Total: {len(self.mt5.all_symbols)} instruments")
    
    async def should_stop_trading(self) -> bool:
        """Check if trading should stop (10:00 Finnish time)"""
        finland_now = datetime.now(self.finland_tz)
        current_time = finland_now.time()
        
        if current_time >= self.stop_time:
            logger.info("🛑 10:00 Finnish time reached - stopping trading")
            return True
        return False
    
    async def send_startup_notification(self):
        """Send startup notification"""
        success = imessage_notifier.send_imessage(f"""🚀 MIKROBOT v2.0 STARTED!

⚡ Lightning Bolt Strategy ACTIVE
📈 Trading {len(self.mt5.all_symbols)} instruments:
   • 7 Major forex pairs
   • 21 Minor/Cross pairs  
   • 10 Top crypto CFDs

🎯 Risk: 0.15% per trade
🛡️ ATR + 0.328 Fib stops
⏰ Auto-stop: 10:00 Finnish time
📱 Real-time Phase notifications ON

🔥 LIVE TRADING BEGINS NOW!
{datetime.now().strftime('%H:%M:%S')}""")
        
        if success:
            logger.info("📱 Startup notification sent")
        else:
            logger.warning("📱 Startup notification failed")
    
    async def send_shutdown_notification(self):
        """Send shutdown notification"""
        success = imessage_notifier.send_imessage(f"""🛑 MIKROBOT v2.0 STOPPED

⏰ Daily trading session complete
📊 Total trades executed: {self.total_trades}
🕐 Stopped at: {datetime.now().strftime('%H:%M:%S')}

💤 Mikrobot sleeping until next session...
📱 iMessage notifications paused""")
        
        if success:
            logger.info("📱 Shutdown notification sent")
    
    async def trading_loop(self):
        """Main trading loop with iMessage notifications"""
        logger.info("⚡ Starting Lightning Bolt trading loop...")
        
        while self.running:
            try:
                # Check stop time
                if await self.should_stop_trading():
                    break
                
                # Scan all symbols for Lightning Bolt patterns
                logger.info("🔍 Scanning for Lightning Bolt patterns...")
                signals = await self.lightning_bolt.scan_all_symbols()
                
                if signals:
                    for signal in signals:
                        logger.info(f"⚡ LIGHTNING BOLT: {signal.symbol} {signal.direction.value}")
                        
                        # Execute trade via webhook
                        order_type = "BUY" if signal.direction.value == "BULLISH" else "SELL"
                        
                        trade_result = await self.mt5.place_order(
                            symbol=signal.symbol,
                            order_type=order_type,
                            volume=signal.atr_info['position_size'],
                            price=signal.entry_price,
                            sl=signal.stop_loss,
                            tp=signal.take_profit,
                            comment="LIGHTNING_BOLT_v2"
                        )
                        
                        if trade_result:
                            self.total_trades += 1
                            logger.info(f"✅ Trade #{self.total_trades} executed: {signal.symbol}")
                        else:
                            logger.error(f"❌ Trade execution failed: {signal.symbol}")
                
                # Wait before next scan
                await asyncio.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Manual stop requested")
                break
            except Exception as e:
                logger.error(f"Trading loop error: {e}")
                await asyncio.sleep(5)  # Brief pause on error
        
        logger.info(f"📊 Trading session complete - {self.total_trades} trades executed")
    
    async def start_trading(self):
        """Start production trading"""
        logger.info("🔥 STARTING MIKROBOT PRODUCTION TRADING")
        
        # Connect to MT5 (webhook test)
        connected = await self.mt5.connect()
        if not connected:
            logger.error("❌ MT5 connection failed")
            return False
        
        # Send startup notification
        await self.send_startup_notification()
        
        # Start trading loop
        await self.trading_loop()
        
        # Send shutdown notification  
        await self.send_shutdown_notification()
        
        return True
    
    def stop_trading(self):
        """Stop trading gracefully"""
        logger.info("🛑 Stopping Mikrobot...")
        self.running = False

async def main():
    """Main entry point"""
    
    print("🔥 MIKROBOT FASTVERSION v2.0 - PRODUCTION")
    print("=" * 50)
    print("⚡ Lightning Bolt Strategy")
    print("📱 iMessage Notifications: +358440606044")
    print("🎯 28 Forex + 10 Crypto = 38 instruments")
    print("🛡️ ATR Position Sizing + 0.328 Fib SL")
    print("⏰ Auto-stop: 10:00 Finnish time")
    print("=" * 50)
    
    mikrobot = MikrobotProduction()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"🛑 Received signal {sig}")
        mikrobot.stop_trading()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = await mikrobot.start_trading()
        if success:
            logger.info("✅ Mikrobot session completed successfully")
        else:
            logger.error("❌ Mikrobot session failed")
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        await mikrobot.send_shutdown_notification()
    
    logger.info("👋 Mikrobot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)