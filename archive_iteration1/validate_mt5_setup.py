"""
MT5 Setup Validation for Demo Account 107034605
Quick check if MT5 is properly configured for crypto trading
"""

import MetaTrader5 as mt5
import sys

def validate_mt5_setup():
    print("MT5 SETUP VALIDATION")
    print("=" * 30)
    
    # Test 1: MT5 Package Import
    try:
        print("1. MT5 Package: OK")
    except ImportError:
        print("1. MT5 Package: FAILED - pip install MetaTrader5")
        return False
    
    # Test 2: MT5 Terminal Initialization
    try:
        if mt5.initialize():
            print("2. MT5 Terminal: OK")
            
            # Get terminal info
            terminal_info = mt5.terminal_info()
            if terminal_info:
                print(f"   Terminal: {terminal_info.name}")
                print(f"   Version: {terminal_info.build}")
                print(f"   Path: {terminal_info.path}")
            
            mt5.shutdown()
        else:
            print("2. MT5 Terminal: FAILED - Install MT5 terminal")
            return False
    except Exception as e:
        print(f"2. MT5 Terminal: ERROR - {e}")
        return False
    
    # Test 3: Demo Account Check (without login)
    print("3. Demo Account: Ready for testing")
    print(f"   Account: 107034605")
    print(f"   Server: MetaQuotes-Demo")
    print("   Password: [Required for live connection]")
    
    # Test 4: Crypto Symbol Check
    print("4. Crypto Symbols: Ready for validation")
    print("   Target symbols: BTCUSD, ETHUSD")
    print("   (Will be validated after login)")
    
    print("\n" + "=" * 30)
    print("VALIDATION COMPLETE")
    print("Next step: Run live demo with actual password")
    print("Command: python run_crypto_demo.py")
    
    return True

if __name__ == "__main__":
    success = validate_mt5_setup()
    sys.exit(0 if success else 1)