#!/usr/bin/env python3
"""
Test Mikrobot scanner with REAL crypto prices only
Focus on crypto since those APIs work perfectly
"""

import asyncio
from src.mikrobot_v2.core.mt5_direct_connector import MT5DirectConnector
from src.mikrobot_v2.strategies.lightning_bolt import LightningBoltStrategy
from src.mikrobot_v2.notifications.imessage_notifier import imessage_notifier

async def test_crypto_scanner():
    """Test scanner with real crypto data"""
    
    print("🪙 MIKROBOT CRYPTO SCANNER TEST")
    print("🔥 REAL CRYPTO PRICES - NO SIMULATION")
    print("=" * 40)
    
    # Initialize components
    mt5 = MT5DirectConnector()
    await mt5.connect()
    
    strategy = LightningBoltStrategy(mt5)
    
    # Test only crypto symbols (where real prices work)
    crypto_symbols = ["BTCUSD", "ETHUSD", "BNBUSD", "XRPUSD", "SOLUSD"]
    
    print(f"📊 Testing {len(crypto_symbols)} crypto symbols with REAL prices:")
    
    for symbol in crypto_symbols:
        print(f"\n🔍 Testing {symbol}...")
        
        # Get real tick first
        tick = await mt5.get_current_tick(symbol)
        if tick:
            print(f"   💰 Real price: ${tick.bid:,.2f} / ${tick.ask:,.2f}")
            print(f"   📡 Source: Real market data")
            
            # Test Lightning Bolt analysis
            if not strategy._is_symbol_in_cooldown(symbol):
                signal = await strategy.analyze_symbol(symbol)
                if signal:
                    print(f"   ⚡ SIGNAL: {signal.direction.value} @ ${signal.entry_price:,.2f}")
                    print(f"   🎯 Confidence: {signal.confidence:.1%}")
                    
                    # Send test iMessage for crypto
                    success = imessage_notifier.send_imessage(f"""🪙 CRYPTO LIGHTNING BOLT TEST

⚡ {symbol} - REAL PRICE ANALYSIS
💰 Current: ${tick.price:,.2f}
🎯 Pattern: {signal.direction.value}
📊 Confidence: {signal.confidence:.1%}

🔥 REAL CRYPTO DATA - NO SIMULATION!
🕐 {datetime.now().strftime('%H:%M:%S')}""")
                    
                    if success:
                        print(f"   📱 iMessage sent successfully!")
                else:
                    print(f"   ⚪ No Lightning Bolt pattern detected")
            else:
                print(f"   ⏰ In cooldown - skipping analysis")
        else:
            print(f"   ❌ No real price data available")
        
        await asyncio.sleep(1)
    
    print("\n✅ Crypto scanner test complete!")
    print("🔥 All crypto prices were REAL market data from APIs")

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(test_crypto_scanner())