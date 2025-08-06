#!/usr/bin/env python3
"""
Test improved BOS detection with stricter filtering
"""

import asyncio
from src.mikrobot_v2.core.mt5_direct_connector import MT5DirectConnector
from src.mikrobot_v2.strategies.lightning_bolt import LightningBoltStrategy

async def test_improved_bos():
    """Test that BOS detection is now much stricter"""
    
    mt5 = MT5DirectConnector()
    await mt5.connect()
    
    strategy = LightningBoltStrategy(mt5)
    
    print("🔍 TESTING IMPROVED BOS DETECTION")
    print("=" * 40)
    print(f"🎯 Min confidence: {strategy.min_confidence:.1%}")
    print(f"⏰ Cooldown: {strategy.cooldown_minutes} minutes")
    print(f"📊 Min structure strength: {strategy.structure_analyzer.min_structure_strength}")
    print(f"💪 Min break strength: {strategy.structure_analyzer.min_break_strength}")
    print()
    
    # Test a few symbols
    test_symbols = ["EURUSD", "GBPUSD", "USDJPY"]
    
    for symbol in test_symbols:
        print(f"🔍 Analyzing {symbol}...")
        
        # Check if in cooldown
        if strategy._is_symbol_in_cooldown(symbol):
            print(f"   ⏰ In cooldown - skipping")
            continue
        
        try:
            signal = await strategy.analyze_symbol(symbol)
            if signal:
                print(f"   ⚡ BOS DETECTED: {signal.direction.value} @ {signal.entry_price}")
                print(f"   🎯 Confidence: {signal.confidence:.1%}")
            else:
                print(f"   ⚪ No valid BOS pattern found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        await asyncio.sleep(0.5)
    
    print("\n✅ Test complete!")
    print("📊 Should see much fewer (but higher quality) signals now")

if __name__ == "__main__":
    asyncio.run(test_improved_bos())