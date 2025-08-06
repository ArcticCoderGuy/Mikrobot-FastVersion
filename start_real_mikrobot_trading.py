#!/usr/bin/env python3
"""
REAL MIKROBOT TRADING WITH WEBHOOK BRIDGE
==========================================

This version sends REAL trades to Windows MT5 via webhook
NO MORE SIMULATION - ACTUAL DEMO TRADES ON ACCOUNT 95244786
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from mikrobot_v2.core.mt5_webhook_connector import MT5WebhookConnector
from mikrobot_v2.strategies.lightning_bolt import LightningBoltStrategy
from mikrobot_v2.utils.atr_position_sizer import ATRPositionSizer
from mikrobot_v2.orchestration.mcp_v2_controller import MCPv2Controller
from mikrobot_v2.orchestration.hansei_reflector import HanseiReflector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mikrobot_v2_REAL_TRADING.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RealMikrobotTradingEngine:
    """
    REAL trading engine with webhook bridge to Windows MT5
    """
    
    def __init__(self, webhook_url: str = "http://localhost:8000/bridge/webhook/trading-signal"):
        # Use webhook connector instead of simulation
        self.mt5 = MT5WebhookConnector(webhook_url)
        self.strategy = None
        self.atr_sizer = None
        self.executed_real_trades = []
        
        logger.info("🔥 REAL MIKROBOT v2.0 - WEBHOOK BRIDGE MODE")
        logger.info("🚨 THIS WILL SEND REAL TRADES TO MT5!")
        
    async def initialize(self) -> bool:
        """Initialize for REAL trading"""
        try:
            logger.info("🔄 Initializing REAL trading engine...")
            
            # Connect webhook bridge
            if not await self.mt5.connect():
                logger.error("❌ Webhook bridge connection failed")
                return False
            
            # Initialize strategy
            self.strategy = LightningBoltStrategy(self.mt5)
            
            # Initialize ATR position sizer
            self.atr_sizer = ATRPositionSizer(self.mt5)
            
            logger.info("✅ REAL trading components initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Real trading initialization failed: {e}")
            return False
    
    async def execute_real_demo_trades(self):
        """Execute 5 real demo trades immediately"""
        
        logger.info("🚨 EXECUTING 5 REAL DEMO TRADES NOW!")
        logger.info("📱 Account: 95244786 @ MetaQuotesDemo")
        print("=" * 60)
        
        trades_to_execute = [
            {
                'symbol': 'EURUSD',
                'action': 'BUY',
                'volume': 0.01,
                'sl_offset': 50,  # 5 pips
                'tp_offset': 100  # 10 pips
            },
            {
                'symbol': 'GBPUSD', 
                'action': 'SELL',
                'volume': 0.01,
                'sl_offset': 50,
                'tp_offset': 100
            },
            {
                'symbol': 'USDJPY',
                'action': 'BUY', 
                'volume': 0.01,
                'sl_offset': 0.50,  # 50 points
                'tp_offset': 1.00   # 100 points
            },
            {
                'symbol': 'EURJPY',
                'action': 'SELL',
                'volume': 0.01,
                'sl_offset': 0.80,
                'tp_offset': 1.60
            },
            {
                'symbol': 'BTCUSD',
                'action': 'BUY',
                'volume': 0.01,
                'sl_offset': 500,   # $500
                'tp_offset': 1000   # $1000
            }
        ]
        
        for i, trade_spec in enumerate(trades_to_execute, 1):
            try:
                # Get current price
                tick = await self.mt5.get_current_tick(trade_spec['symbol'])
                if not tick:
                    logger.error(f"❌ Could not get price for {trade_spec['symbol']}")
                    continue
                
                # Calculate prices
                if trade_spec['action'] == 'BUY':
                    entry_price = tick.ask
                    stop_loss = entry_price - (trade_spec['sl_offset'] * 0.0001)
                    take_profit = entry_price + (trade_spec['tp_offset'] * 0.0001)
                else:  # SELL
                    entry_price = tick.bid
                    stop_loss = entry_price + (trade_spec['sl_offset'] * 0.0001)
                    take_profit = entry_price - (trade_spec['tp_offset'] * 0.0001)
                
                # Round properly
                if 'JPY' in trade_spec['symbol']:
                    stop_loss = round(stop_loss, 3)
                    take_profit = round(take_profit, 3)
                elif 'USD' in trade_spec['symbol'] and len(trade_spec['symbol']) == 6:
                    stop_loss = round(stop_loss, 5)
                    take_profit = round(take_profit, 5)
                else:
                    stop_loss = round(stop_loss, 2)  # For crypto
                    take_profit = round(take_profit, 2)
                
                logger.info(f"🎯 REAL TRADE {i}/5: {trade_spec['symbol']} {trade_spec['action']}")
                logger.info(f"   Entry: {entry_price}")
                logger.info(f"   SL: {stop_loss}")
                logger.info(f"   TP: {take_profit}")
                
                # Execute REAL trade via webhook
                from mikrobot_v2.core.mt5_direct_connector import OrderType
                order_type = OrderType.BUY if trade_spec['action'] == 'BUY' else OrderType.SELL
                
                result = await self.mt5.place_order(
                    symbol=trade_spec['symbol'],
                    order_type=order_type,
                    volume=trade_spec['volume'],
                    price=entry_price,
                    sl=stop_loss,
                    tp=take_profit,
                    comment=f"REAL_DEMO_TRADE_{i}"
                )
                
                if result:
                    self.executed_real_trades.append({
                        'trade_number': i,
                        'symbol': trade_spec['symbol'],
                        'action': trade_spec['action'],
                        'volume': trade_spec['volume'],
                        'entry_price': entry_price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'webhook_result': result,
                        'status': 'SENT_TO_MT5'
                    })
                    logger.info(f"✅ REAL TRADE {i} SENT TO MT5!")
                else:
                    logger.error(f"❌ REAL TRADE {i} FAILED!")
                
                # Wait between trades
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"❌ Error executing real trade {i}: {e}")
                continue
        
        # Summary
        successful_trades = len(self.executed_real_trades)
        logger.info("=" * 60)
        logger.info(f"🔥 REAL DEMO TRADING COMPLETE!")
        logger.info(f"✅ Successfully sent {successful_trades}/5 trades to MT5")
        logger.info(f"📱 Account: 95244786 @ MetaQuotesDemo")
        logger.info("🌐 Trades sent via webhook bridge to Windows MT5")
        logger.info("=" * 60)
        
        return self.executed_real_trades

async def main():
    """Execute real demo trades immediately"""
    
    print("🚨 MIKROBOT v2.0 - REAL DEMO TRADING")
    print("=" * 50)
    print("⚠️  WARNING: This will send REAL trades to MT5!")
    print("📱 Account: 95244786 @ MetaQuotesDemo")  
    print("🌐 Via webhook bridge to Windows")
    print("=" * 50)
    
    # Confirm execution
    response = input("🔥 Execute 5 REAL demo trades now? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Real trading cancelled")
        return 0
    
    # Create engine
    engine = RealMikrobotTradingEngine()
    
    try:
        # Initialize
        if not await engine.initialize():
            logger.error("❌ Failed to initialize real trading engine")
            return 1
        
        # Execute real trades
        trades = await engine.execute_real_demo_trades()
        
        print(f"\n🎯 REAL TRADING SUMMARY:")
        for trade in trades:
            print(f"   {trade['trade_number']}. {trade['symbol']} {trade['action']} - {trade['status']}")
        
        print(f"\n✅ {len(trades)} REAL TRADES SENT TO MT5!")
        print("📊 Check MT5 terminal for actual executions")
        
    except Exception as e:
        logger.error(f"❌ Real trading error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Real trading interrupted")
        sys.exit(0)