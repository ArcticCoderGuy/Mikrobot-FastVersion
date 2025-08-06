#!/usr/bin/env python3
"""
iMessage Notification Tester
=============================

Test iMessage notifications for Lightning Bolt phases
"""

import asyncio
from datetime import datetime
from src.mikrobot_v2.notifications.imessage_notifier import (
    imessage_notifier, notify_bos_detected, notify_retest_confirmed,
    notify_entry_executed, LightningBoltPhase
)

async def test_imessage_system():
    """Test complete iMessage notification system"""
    
    print("📱 TESTING IMESSAGE LIGHTNING BOLT NOTIFICATIONS")
    print("=" * 55)
    
    # Update phone number if needed (replace with your number)
    # imessage_notifier.set_phone_number("+358123456789")  # Your number here
    
    # Test 1: Basic connectivity
    print("\n🔧 Testing basic iMessage connectivity...")
    success = imessage_notifier.test_notification()
    if success:
        print("✅ Basic iMessage test sent!")
    else:
        print("❌ Basic iMessage test failed!")
        return False
    
    await asyncio.sleep(2)
    
    # Test 2: Phase 1 - BOS Detection
    print("\n⚡ Testing Phase 1: BOS Detection...")
    success = notify_bos_detected(
        symbol="EURUSD",
        price=1.0856,
        confidence=0.85,
        timeframe="M5"
    )
    if success:
        print("✅ Phase 1 BOS notification sent!")
    else:
        print("❌ Phase 1 BOS notification failed!")
    
    await asyncio.sleep(3)
    
    # Test 3: Phase 2 - Retest Confirmation  
    print("\n🔄 Testing Phase 2: Retest Confirmation...")
    success = notify_retest_confirmed(
        symbol="EURUSD",
        price=1.0850,
        retest_level=1.0856,
        confidence=0.78
    )
    if success:
        print("✅ Phase 2 Retest notification sent!")
    else:
        print("❌ Phase 2 Retest notification failed!")
    
    await asyncio.sleep(3)
    
    # Test 4: Phase 3 - Entry Execution
    print("\n🚀 Testing Phase 3: Entry Execution...")
    success = notify_entry_executed(
        symbol="EURUSD",
        entry_price=1.0862,
        sl=1.0832,
        tp=1.0904,
        volume=0.18
    )
    if success:
        print("✅ Phase 3 Entry notification sent!")
    else:
        print("❌ Phase 3 Entry notification failed!")
    
    await asyncio.sleep(3)
    
    # Test 5: Market Structure Change
    print("\n📊 Testing Market Structure notification...")
    success = imessage_notifier.notify_market_structure_change(
        symbol="GBPJPY",
        change_type="HH",  # Higher High
        price=190.45,
        details={'trend': 'BULLISH'}
    )
    if success:
        print("✅ Market Structure notification sent!")
    else:
        print("❌ Market Structure notification failed!")
    
    await asyncio.sleep(3)
    
    # Test 6: ML Pattern Detection
    print("\n🧠 Testing ML Pattern Detection...")
    success = imessage_notifier.notify_ml_pattern_detection(
        symbol="BTCUSD",
        pattern="LIGHTNING_BOLT_SETUP",
        confidence=0.92,
        price=43280.0
    )
    if success:
        print("✅ ML Pattern notification sent!")
    else:
        print("❌ ML Pattern notification failed!")
    
    await asyncio.sleep(3)
    
    # Test 7: ATR Position Sizing
    print("\n📏 Testing ATR Position Sizing...")
    success = imessage_notifier.notify_atr_position_sizing(
        symbol="EURUSD",
        atr_value=0.00125,
        position_size=0.18,
        risk_percent=0.0015  # 0.15%
    )
    if success:
        print("✅ ATR Position sizing notification sent!")
    else:
        print("❌ ATR Position sizing notification failed!")
    
    print("\n🔥 iMessage notification testing complete!")
    print("📱 Check your phone for all test messages!")
    
    return True

async def test_custom_phase_notification():
    """Test custom Lightning Bolt phase notification"""
    
    print("\n🧪 Testing custom Lightning Bolt phase notification...")
    
    # Create custom phase data
    phase_data = LightningBoltPhase(
        symbol="GBPUSD",
        phase=2,
        phase_name="RETEST_CONFIRMATION", 
        timeframe="M1",
        price=1.2734,
        confidence=0.88,
        timestamp=datetime.now(),
        details={
            'trend_direction': 'BULLISH',
            'retest_level': 1.2725,
            'strength': 'HIGH'
        }
    )
    
    success = imessage_notifier.notify_lightning_bolt_phase(phase_data)
    
    if success:
        print("✅ Custom phase notification sent!")
    else:
        print("❌ Custom phase notification failed!")
    
    return success

def configure_phone_number():
    """Configure your phone number for notifications"""
    
    print("\n📞 PHONE NUMBER CONFIGURATION")
    print("=" * 35)
    
    current_number = imessage_notifier.phone_number
    print(f"Current number: {current_number}")
    
    # Set your actual phone number
    new_number = "+358440606044"  # Markuksen numero
    imessage_notifier.set_phone_number(new_number)
    print(f"Updated to: {new_number}")
    
    print("⚠️  To set your phone number:")
    print("1. Edit this file: test_imessage_notifications.py")
    print("2. Uncomment lines and add your real phone number")
    print("3. Run test again")

async def main():
    """Main test function"""
    
    print("🔥 MIKROBOT IMESSAGE TESTING")
    print("=" * 30)
    
    # Configure phone number
    configure_phone_number()
    
    # Run basic tests
    await test_imessage_system()
    
    # Run custom test
    await test_custom_phase_notification()
    
    print("\n✅ ALL TESTS COMPLETE!")
    print("📱 Your iPhone should have received multiple test messages")
    print("🚀 iMessage Lightning Bolt notifications are READY!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted")
    except Exception as e:
        print(f"\n❌ Testing error: {e}")