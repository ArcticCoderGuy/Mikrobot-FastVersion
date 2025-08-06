#!/usr/bin/env python3
"""
MIKROBOT CHART SCANNER v2.0
============================

ML/MCP scans MT5 charts and sends iMessage alerts
USER makes manual trades after checking charts

NO AUTOMATIC TRADING - ONLY PATTERN DETECTION & ALERTS
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
        logging.FileHandler('mikrobot_scanner.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import Mikrobot components
from src.mikrobot_v2.core.mt5_direct_connector import MT5DirectConnector
from src.mikrobot_v2.strategies.lightning_bolt import LightningBoltStrategy
from src.mikrobot_v2.notifications.mail_notifier import mail_notifier
from src.mikrobot_v2.feedback.imessage_feedback_listener import (
    start_feedback_system, store_signal_for_feedback, get_signal_trust_score
)

class MikrobotScanner:
    """ML/MCP Chart Scanner - Alerts only, no trading"""
    
    def __init__(self):
        # Chart scanning components (read-only)
        self.mt5 = MT5DirectConnector()  # Direct MT5 for chart reading
        self.lightning_bolt = LightningBoltStrategy(self.mt5)
        
        # Scanner settings - SLOWER TO AVOID SPAM
        self.running = True
        self.scan_interval = 60  # 1 minute between scans (quality over quantity)
        self.detected_patterns = set()  # Avoid duplicate alerts
        
        # CRYPTO SYMBOLS - Real prices via CoinGecko API
        self.crypto_symbols = [
            "BTCUSD", "ETHUSD", "BNBUSD", "XRPUSD", "SOLUSD"
        ]
        
        # FOREX SYMBOLS - Real prices via Alpha Vantage API (limited to save API calls)
        # Using only major pairs due to 25 requests/day limit
        self.major_pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF"]
        
        # ALL SYMBOLS - Both forex and crypto with REAL prices!
        self.all_symbols = self.major_pairs + self.crypto_symbols  # 10 total symbols
        
        logger.info("🔍 MIKROBOT CHART SCANNER v2.0 initialized")
        logger.info(f"📱 iMessage alerts: +358440606044")
        logger.info(f"📊 Scanning {len(self.all_symbols)} instruments")
        logger.info("⚠️  NO AUTOMATIC TRADING - ALERTS ONLY")
        logger.info("🎧 iMessage feedback system enabled (Pass/Fail)")
    
    async def send_startup_notification(self):
        """Send scanner startup notification"""
        # Send startup email notification
        subject = "🔍 MIKROBOT CHART SCANNER STARTED"
        body = f"""MIKROBOT CHART SCANNER v2.0 ACTIVATED

📊 ML/MCP analyzing MT5 charts:
   • 7 Major forex pairs
   • 21 Minor/Cross pairs  
   • 10 Top crypto CFDs

⚡ Lightning Bolt pattern detection
🔄 M5 BOS + M1 Retest scanning
📱 Real-time alerts to +358440606044

⚠️  NO AUTO-TRADING
👀 You check charts & trade manually

🎧 FEEDBACK SYSTEM ACTIVE:
   Reply "Pass EURUSD" = Good signal
   Reply "Fail GBPJPY" = Bad signal
   ML learns from your validation!

🕐 Scanner started: {datetime.now().strftime('%H:%M:%S')}

🚀 ML/MCP CHART ANALYSIS ACTIVE!"""
        
        success = mail_notifier.send_mail_with_chart(subject, body)
        if success:
            logger.info("📧 Scanner startup email sent")
    
    async def send_pattern_alert(self, symbol: str, pattern_data: dict):
        """Send Lightning Bolt pattern alert"""
        
        phase = pattern_data.get('phase', 'UNKNOWN')
        price = pattern_data.get('price', 0)
        confidence = pattern_data.get('confidence', 0)
        timeframe = pattern_data.get('timeframe', 'M5')
        direction = pattern_data.get('direction', 'UNKNOWN')
        
        # Check if we should trust this signal based on ML learning
        should_trust = get_signal_trust_score(symbol, confidence)
        trust_emoji = "🔥" if should_trust else "⚠️"
        
        # Store signal for feedback matching
        signal_id = store_signal_for_feedback(symbol, pattern_data)
        
        # Create unique pattern ID to avoid duplicates
        pattern_id = f"{symbol}_{phase}_{int(price*10000)}"
        
        if pattern_id in self.detected_patterns:
            return  # Already alerted
        
        self.detected_patterns.add(pattern_id)
        
        if phase == 1 or 'BOS' in str(phase):
            # Phase 1: BOS Detection
            message = f"""⚡ LIGHTNING BOLT - PHASE 1

🔍 ML/MCP DETECTED:
📈 {symbol} - {direction} BOS
💰 Price: {price}
📊 Timeframe: {timeframe}
🎯 Confidence: {confidence:.1%}

👀 CHECK {symbol} CHART NOW!
⚡ M5 Break of Structure confirmed
🔄 Watch for M1 retest...

{trust_emoji} ML Trust: {"HIGH" if should_trust else "LOW"}
📱 Reply: "Pass {symbol}" or "Fail {symbol}"

🕐 {datetime.now().strftime('%H:%M:%S')}"""
            
        elif phase == 2 or 'RETEST' in str(phase):
            # Phase 2: Retest
            message = f"""🔄 LIGHTNING BOLT - PHASE 2

🔍 ML/MCP CONFIRMED:
📈 {symbol} - {direction} RETEST
💰 Current: {price}
📊 M1 retest valid
🎯 Confidence: {confidence:.1%}

👀 CHECK {symbol} CHART NOW!
🚀 Ready for +0.6 Ylipip entry
⚡ Pattern setup complete!

{trust_emoji} ML Trust: {"HIGH" if should_trust else "LOW"}
📱 Reply: "Pass {symbol}" or "Fail {symbol}"

🕐 {datetime.now().strftime('%H:%M:%S')}"""
            
        elif phase == 3 or 'ENTRY' in str(phase):
            # Phase 3: Entry zone
            entry_price = pattern_data.get('entry_price', price)
            sl = pattern_data.get('stop_loss', 0)
            tp = pattern_data.get('take_profit', 0)
            
            message = f"""🚀 LIGHTNING BOLT - PHASE 3

🔍 ML/MCP ENTRY SIGNAL:
📈 {symbol} - {direction}
💰 Entry Zone: {entry_price}
🛡️ Suggested SL: {sl}
🎯 Suggested TP: {tp}
⚡ +0.6 Ylipip level reached

👀 URGENT: CHECK {symbol} CHART!
✋ Manual trade decision needed
🔥 Lightning Bolt setup complete!

{trust_emoji} ML Trust: {"HIGH" if should_trust else "LOW"}
📱 Reply: "Pass {symbol}" or "Fail {symbol}"

🕐 {datetime.now().strftime('%H:%M:%S')}"""
        else:
            # Generic pattern
            message = f"""📊 PATTERN DETECTED

🔍 ML/MCP found: {phase}
📈 {symbol} @ {price}
🎯 Confidence: {confidence:.1%}

👀 Check chart for validation
🕐 {datetime.now().strftime('%H:%M:%S')}"""
        
        # Generate chart for the alert
        from src.mikrobot_v2.charts.chart_generator import generate_pattern_chart
        chart_path = None
        try:
            chart_path = generate_pattern_chart(symbol, str(phase), price)
        except Exception as e:
            logger.warning(f"Chart generation failed: {e}")
        
        # Send email with chart
        if phase == 1 or 'BOS' in str(phase):
            phase_num = 1
            phase_name = "BOS_DETECTION"
        elif phase == 2 or 'RETEST' in str(phase):
            phase_num = 2  
            phase_name = "RETEST_CONFIRMATION"
        elif phase == 3 or 'ENTRY' in str(phase):
            phase_num = 3
            phase_name = "YLIPIP_ENTRY"
        else:
            phase_num = 0
            phase_name = str(phase)
        
        success = mail_notifier.notify_lightning_bolt(
            symbol=symbol,
            phase=phase_num,
            phase_name=phase_name,
            price=price,
            confidence=confidence,
            chart_path=chart_path
        )
        
        if success:
            logger.info(f"📧 Pattern alert email sent: {symbol} {phase}")
        
        # Clean old patterns to avoid memory buildup
        if len(self.detected_patterns) > 100:
            self.detected_patterns.clear()
    
    async def scan_charts(self):
        """Scan charts for patterns and send alerts"""
        logger.info("🔍 Starting chart scan...")
        
        for symbol in self.all_symbols:
            try:
                # Get chart data
                m5_candles = await self.mt5.get_candles(symbol, "M5", 100)
                m1_candles = await self.mt5.get_candles(symbol, "M1", 200)
                
                if not m5_candles or not m1_candles:
                    continue
                
                # Check for BOS patterns (Phase 1)
                bos_pattern = await self.lightning_bolt._detect_m5_bos(symbol, m5_candles)
                if bos_pattern:
                    await self.send_pattern_alert(symbol, {
                        'phase': 1,
                        'price': bos_pattern.break_level,
                        'confidence': bos_pattern.confidence,
                        'timeframe': 'M5',
                        'direction': bos_pattern.direction.value
                    })
                
                # Check for retest confirmation (Phase 2)  
                if symbol in self.lightning_bolt.active_patterns:
                    active_pattern = self.lightning_bolt.active_patterns[symbol]
                    retest_confirmed = await self.lightning_bolt._confirm_m1_retest(
                        symbol, m1_candles, active_pattern
                    )
                    if retest_confirmed:
                        await self.send_pattern_alert(symbol, {
                            'phase': 2,
                            'price': m1_candles[-1].close,
                            'confidence': active_pattern.confidence,
                            'timeframe': 'M1',
                            'direction': active_pattern.direction.value
                        })
                
                # Brief pause between symbols
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
        
        logger.info(f"🔍 Chart scan complete - {len(self.all_symbols)} symbols")
    
    async def scanner_loop(self):
        """Main scanner loop"""
        logger.info("🔍 Starting ML/MCP chart scanner...")
        
        while self.running:
            try:
                await self.scan_charts()
                
                # Wait before next scan
                logger.info(f"⏳ Next scan in {self.scan_interval}s...")
                await asyncio.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Manual scanner stop")
                break
            except Exception as e:
                logger.error(f"Scanner loop error: {e}")
                await asyncio.sleep(5)
        
        logger.info("📊 Chart scanning session complete")
    
    async def start_scanner(self):
        """Start chart scanning"""
        logger.info("🔍 STARTING MIKROBOT CHART SCANNER")
        
        # Start feedback system
        start_feedback_system()
        
        # Test MT5 connection (read-only)
        connected = await self.mt5.connect()
        if not connected:
            logger.warning("⚠️ MT5 connection test failed, but continuing with simulation")
        
        # Send startup notification
        await self.send_startup_notification()
        
        # Start scanner loop
        await self.scanner_loop()
        
        return True
    
    def stop_scanner(self):
        """Stop scanner gracefully"""
        logger.info("🛑 Stopping chart scanner...")
        self.running = False

async def main():
    """Main entry point"""
    
    print("🔍 MIKROBOT CHART SCANNER v2.0")
    print("=" * 40)
    print("📊 ML/MCP Chart Analysis")
    print("📱 iMessage Pattern Alerts")
    print("👀 Manual Trade Validation")
    print("⚠️  NO AUTOMATIC TRADING")
    print("=" * 40)
    
    scanner = MikrobotScanner()
    
    # Setup signal handlers
    def signal_handler(sig, frame):
        logger.info(f"🛑 Received signal {sig}")
        scanner.stop_scanner()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        success = await scanner.start_scanner()
        if success:
            logger.info("✅ Scanner session completed successfully")
        else:
            logger.error("❌ Scanner session failed")
    
    except Exception as e:
        logger.error(f"❌ Fatal scanner error: {e}")
    
    logger.info("👋 Chart scanner shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Scanner interrupted by user")
    except Exception as e:
        print(f"\n❌ Scanner error: {e}")
        sys.exit(1)