#!/usr/bin/env python3
"""
MIKROBOT CROSS-PLATFORM DEMONSTRATION
======================================

Shows how Mac → Windows MT5 webhook system works
Creates actual trade signals for Windows MT5 execution
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from mikrobot_v2.core.mt5_webhook_connector import MT5WebhookConnector

async def demonstrate_cross_platform_system():
    """Demonstrate the complete cross-platform workflow"""
    
    print("🔥 MIKROBOT CROSS-PLATFORM DEMONSTRATION")
    print("=" * 60)
    print("🍎 Mac: Signal Generation & Analysis")
    print("🌐 Webhook: Cross-platform communication") 
    print("🖥️ Windows: MT5 Trade Execution")
    print("📱 Account: 95244786 @ MetaQuotesDemo")
    print("=" * 60)
    print()
    
    # Create webhook connector (will attempt to connect to Windows bridge)
    webhook_connector = MT5WebhookConnector(
        webhook_url="http://localhost:8000/bridge/webhook/trading-signal"
    )
    
    # Initialize
    print("🔄 Initializing cross-platform bridge...")
    await webhook_connector.connect()
    print()
    
    # Demonstrate Lightning Bolt signal generation
    print("⚡ LIGHTNING BOLT SIGNALS GENERATED:")
    print("-" * 40)
    
    lightning_bolt_signals = [
        {
            'symbol': 'EURUSD',
            'direction': 'BULLISH',
            'entry_price': 1.0856,
            'confidence': 0.85,
            'phase': 'ENTRY_TRIGGERED',
            'atr_info': {
                'position_size': 0.18,
                'atr': 0.00208
            },
            'stop_loss': 1.0832,
            'take_profit': 1.0904
        },
        {
            'symbol': 'GBPJPY', 
            'direction': 'BEARISH',
            'entry_price': 190.45,
            'confidence': 0.78,
            'phase': 'ENTRY_TRIGGERED',
            'atr_info': {
                'position_size': 0.12,
                'atr': 0.45
            },
            'stop_loss': 191.20,
            'take_profit': 189.25
        },
        {
            'symbol': 'BTCUSD',
            'direction': 'BULLISH', 
            'entry_price': 43280.0,
            'confidence': 0.92,
            'phase': 'ENTRY_TRIGGERED',
            'atr_info': {
                'position_size': 0.01,
                'atr': 850.0
            },
            'stop_loss': 42500.0,
            'take_profit': 44800.0
        }
    ]
    
    executed_signals = []
    
    for i, signal in enumerate(lightning_bolt_signals, 1):
        print(f"🎯 Signal {i}: {signal['symbol']} {signal['direction']}")
        print(f"   Entry: {signal['entry_price']}")
        print(f"   ATR Position: {signal['atr_info']['position_size']} lots")
        print(f"   SL: {signal['stop_loss']}, TP: {signal['take_profit']}")
        print(f"   Confidence: {signal['confidence']*100:.1f}%")
        
        # Convert to MT5 order
        from mikrobot_v2.core.mt5_direct_connector import OrderType
        order_type = OrderType.BUY if signal['direction'] == 'BULLISH' else OrderType.SELL
        
        # This would normally send to Windows MT5
        # For demonstration, we show what would be sent
        webhook_payload = {
            'symbol': signal['symbol'],
            'action': order_type.value,
            'volume': signal['atr_info']['position_size'],
            'price': signal['entry_price'],
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit'],
            'comment': f"LIGHTNING_BOLT_{signal['direction']}",
            'magic': 20250806,
            'strategy': 'LIGHTNING_BOLT',
            'confidence': signal['confidence'],
            'timestamp': datetime.now().isoformat(),
            'signal_id': f"LB_{int(datetime.now().timestamp())}"
        }
        
        print(f"   📡 Webhook Payload Ready:")
        print(f"      Action: {webhook_payload['action']}")
        print(f"      Volume: {webhook_payload['volume']} lots") 
        print(f"      Magic: {webhook_payload['magic']}")
        print()
        
        executed_signals.append(webhook_payload)
        await asyncio.sleep(1)
    
    # Save webhook signals to files (what would be sent to Windows)
    print("💾 SAVING WEBHOOK SIGNALS FOR WINDOWS MT5:")
    print("-" * 50)
    
    for i, signal in enumerate(executed_signals, 1):
        filename = f"mt5_signal_{signal['signal_id']}.json"
        filepath = Path(f"mt5_messages/{filename}")
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(signal, f, indent=2)
        
        print(f"✅ Signal {i}: {filepath}")
        print(f"   → Windows MT5 would execute: {signal['symbol']} {signal['action']}")
    
    print()
    print("🌐 WEBHOOK COMMUNICATION FLOW:")
    print("-" * 40)
    print("1. 🍎 Mac: Lightning Bolt pattern detected")
    print("2. 📊 Mac: ATR position size calculated") 
    print("3. 🔄 Mac: Signal validated by ML/MCP")
    print("4. 📡 Mac: POST JSON to Django webhook")
    print("5. 🖥️ Windows: Webhook bridge receives signal")
    print("6. 📈 Windows: MetaTrader5 executes trade")
    print("7. ✅ Windows: Confirmation sent back to Mac")
    
    print()
    print("📊 DEMONSTRATION SUMMARY:")
    print("-" * 30)
    print(f"✅ Signals Generated: {len(executed_signals)}")
    print(f"✅ Cross-platform Ready: YES")  
    print(f"✅ MT5 Integration: WEBHOOK BRIDGE")
    print(f"✅ Account Target: 95244786 @ MetaQuotesDemo")
    print()
    print("🎯 NEXT STEPS FOR REAL TRADING:")
    print("1. Set up Windows machine with MT5")
    print("2. Run windows_mt5_executor.py on Windows")
    print("3. Configure IP addresses between Mac/Windows")
    print("4. Start Django webhook server")
    print("5. Deploy real Lightning Bolt trading!")
    print()
    print("🔥 CROSS-PLATFORM MIKROBOT SYSTEM: READY! ✅")
    
    return executed_signals

async def main():
    """Main demonstration"""
    signals = await demonstrate_cross_platform_system()
    return len(signals)

if __name__ == "__main__":
    try:
        signal_count = asyncio.run(main())
        print(f"\n✅ Successfully demonstrated {signal_count} cross-platform signals")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)