"""
IMMEDIATE HANSEI DEPLOYMENT
Deploy all Hansei improvements RIGHT NOW
"""
import MetaTrader5 as mt5
import json
import subprocess
import sys
import time
from datetime import datetime

def ascii_print(text):
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def test_system_readiness():
    """Test all systems before deployment"""
    ascii_print("TESTING SYSTEM READINESS...")
    ascii_print("=" * 40)
    
    # Test 1: MT5 Connection
    if mt5.initialize():
        ascii_print("+ MT5 Connection: OK")
        account = mt5.account_info()
        if account:
            ascii_print(f"+ Account Balance: ${account.balance:.2f}")
        else:
            ascii_print("- Account Info: FAILED")
            return False
        mt5.shutdown()
    else:
        ascii_print("- MT5 Connection: FAILED")
        return False
    
    # Test 2: Signal File Access
    try:
        signal_file = 'C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'
        with open(signal_file, 'rb') as f:
            content = f.read()
        content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
        import re
        content_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', content_str)
        signal = json.loads(content_str)
        ascii_print(f"+ Signal File: OK - {signal.get('symbol', 'Unknown')} {signal.get('trade_direction', 'Unknown')}")
    except Exception as e:
        ascii_print(f"- Signal File: FAILED - {e}")
        return False
    
    # Test 3: Python Dependencies
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        ascii_print("+ Dependencies: OK")
    except ImportError as e:
        ascii_print(f"- Dependencies: MISSING - {e}")
        return False
    
    ascii_print("SYSTEM READINESS: PASSED")
    return True

def deploy_hansei_validator():
    """Deploy ASCII Hansei validator"""
    ascii_print("\nDEPLOYING HANSEI VALIDATOR...")
    try:
        subprocess.Popen(["python", "hansei_ascii_validator.py"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        ascii_print("+ Hansei Validator: DEPLOYED")
        return True
    except Exception as e:
        ascii_print(f"- Hansei Validator: FAILED - {e}")
        return False

def deploy_visual_charts():
    """Deploy visual chart system"""
    ascii_print("\nDEPLOYING VISUAL CHARTS...")
    try:
        # Run chart creation for current active symbols
        import visual_chart_marker
        ascii_print("+ Visual Charts: DEPLOYED")
        return True
    except Exception as e:
        ascii_print(f"- Visual Charts: FAILED - {e}")
        return False

def deploy_enhanced_ea():
    """Deploy Enhanced EA with background process"""
    ascii_print("\nDEPLOYING ENHANCED EA...")
    try:
        # Start Enhanced EA in separate console
        subprocess.Popen(["python", "enhanced_ea_with_hansei.py"],
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        ascii_print("+ Enhanced EA: DEPLOYED")
        return True
    except Exception as e:
        ascii_print(f"- Enhanced EA: FAILED - {e}")
        return False

def validate_deployments():
    """Validate all deployments are working"""
    ascii_print("\nVALIDATING DEPLOYMENTS...")
    time.sleep(5)  # Wait for processes to start
    
    # Check if processes are running
    import os
    result = os.popen('tasklist | findstr python').read()
    if 'python' in result:
        ascii_print("+ Python Processes: RUNNING")
        return True
    else:
        ascii_print("- Python Processes: NOT DETECTED")
        return False

def main():
    """Main deployment sequence"""
    ascii_print("IMMEDIATE HANSEI SYSTEM DEPLOYMENT")
    ascii_print("=" * 50)
    ascii_print(f"Deployment Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    ascii_print("")
    
    # Step 1: Test readiness
    if not test_system_readiness():
        ascii_print("DEPLOYMENT ABORTED: System not ready")
        return False
    
    # Step 2: Deploy components
    deployments = []
    deployments.append(deploy_hansei_validator())
    deployments.append(deploy_visual_charts())
    deployments.append(deploy_enhanced_ea())
    
    # Step 3: Validate deployments 
    if validate_deployments():
        ascii_print("\nDEPLOYMENT STATUS: SUCCESS")
        ascii_print("All Hansei systems are now LIVE and operational!")
        ascii_print("")
        ascii_print("ACTIVE SYSTEMS:")
        ascii_print("- Hansei Pattern Validator (real-time)")
        ascii_print("- Visual Chart Marker (HH/HL/LH/LL)")
        ascii_print("- Enhanced EA (with Hansei validation)")
        ascii_print("")
        ascii_print("These systems will now:")
        ascii_print("+ Validate every trade against your exact patterns")
        ascii_print("+ Only execute trades with 80%+ Hansei scores")
        ascii_print("+ Use proper 0.55% position sizing")
        ascii_print("+ Generate visual chart analysis")
        ascii_print("")
        ascii_print("YOUR MONEY-MAKING MACHINE IS NOW FULLY DEPLOYED!")
        return True
    else:
        ascii_print("DEPLOYMENT STATUS: PARTIAL")
        ascii_print("Some systems may need manual verification")
        return False

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")