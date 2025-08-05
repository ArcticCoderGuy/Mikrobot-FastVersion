"""
MIKROBOT FASTVERSION DEPLOYMENT SCRIPT - CLEAN VERSION
Complete system deployment to account 107034605
"""
import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

# Test individual components first
def test_atr_system():
    """Test ATR Dynamic Positioning"""
    print("Testing ATR Dynamic Positioning System...")
    try:
        result = subprocess.run([sys.executable, "atr_dynamic_positioning.py"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("SUCCESS: ATR system working")
            return True
        else:
            print(f"ERROR: ATR system failed - {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: ATR system test failed - {e}")
        return False

def test_ylipip_system():
    """Test Universal Ylipip Trigger"""
    print("Testing Universal Ylipip Trigger...")
    try:
        result = subprocess.run([sys.executable, "universal_ylipip_trigger.py"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("SUCCESS: Ylipip system working")
            return True
        else:
            print(f"ERROR: Ylipip system failed - {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: Ylipip system test failed - {e}")
        return False

def test_xpws_system():
    """Test XPWS Weekly Tracker"""
    print("Testing XPWS Weekly Tracker...")
    try:
        result = subprocess.run([sys.executable, "xpws_weekly_tracker.py"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("SUCCESS: XPWS system working")
            return True
        else:
            print(f"ERROR: XPWS system failed - {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: XPWS system test failed - {e}")
        return False

def test_dual_phase_system():
    """Test Dual Phase TP System"""
    print("Testing Dual Phase TP System...")
    try:
        result = subprocess.run([sys.executable, "dual_phase_tp_system.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("SUCCESS: Dual Phase TP system working")
            return True
        else:
            print(f"ERROR: Dual Phase TP system failed - {result.stderr}")
            return False
    except Exception as e:
        print(f"ERROR: Dual Phase TP system test failed - {e}")
        return False

def create_master_signal():
    """Create master activation signal"""
    print("Creating master activation signal...")
    
    common_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
    
    activation_signal = {
        "timestamp": datetime.now().isoformat(),
        "account": 107034605,
        "strategy": "MIKROBOT_FASTVERSION",
        "status": "FULLY_ACTIVE",
        "components": {
            "atr_dynamic_positioning": True,
            "universal_ylipip_trigger": True,
            "xpws_weekly_tracker": True,
            "dual_phase_tp_system": True
        },
        "parameters": {
            "risk_percent": 0.55,
            "atr_min_pips": 4,
            "atr_max_pips": 15,
            "ylipip_standard": 0.6,
            "xpws_threshold": 10.0
        },
        "trading_active": True,
        "message": "MIKROBOT_FASTVERSION READY FOR 24/7/365 TRADING"
    }
    
    try:
        signal_file = common_path / "mikrobot_fastversion_signal.json"
        with open(signal_file, 'w') as f:
            json.dump(activation_signal, f, indent=2)
        print(f"SUCCESS: Master signal created at {signal_file}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create master signal - {e}")
        return False

if __name__ == "__main__":
    print("MIKROBOT FASTVERSION SYSTEM DEPLOYMENT")
    print("Account: 107034605")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # Test all components
    if test_atr_system():
        success_count += 1
    
    if test_ylipip_system():
        success_count += 1
    
    if test_xpws_system():
        success_count += 1
    
    if test_dual_phase_system():
        success_count += 1
    
    print("=" * 50)
    print(f"DEPLOYMENT RESULTS: {success_count}/{total_tests} components working")
    
    if success_count == total_tests:
        if create_master_signal():
            print("SUCCESS: MIKROBOT FASTVERSION FULLY DEPLOYED!")
            print("READY FOR LIVE TRADING ON ACCOUNT 107034605")
            print("Strategy: MIKROBOT_FASTVERSION.md")
            print("Status: 24/7/365 OPERATIONAL")
        else:
            print("WARNING: Components working but signal creation failed")
    else:
        print(f"ERROR: {total_tests - success_count} components failed")
        print("Fix errors above before proceeding to live trading")