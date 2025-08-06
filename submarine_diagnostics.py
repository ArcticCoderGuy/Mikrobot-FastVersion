from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
SUBMARINE DIAGNOSTICS PROTOCOL
Emergency MT5 Connection Analysis for Admiral's Mission
"""

import MetaTrader5 as mt5
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - DIAGNOSTIC - %(message)s')
logger = logging.getLogger(__name__)

def submarine_diagnostic_scan():
    """Comprehensive MT5 diagnostic scan"""
    
    print("=" * 60)
    print("SUBMARINE DIAGNOSTIC PROTOCOL")
    print("=" * 60)
    
    # Test 1: MT5 Module
    try:
        logger.info("TEST 1: MT5 Module Import")
        import MetaTrader5 as mt5
        logger.info("OK MT5 module imported successfully")
        print(f"MT5 Version: {mt5.__version__ if hasattr(mt5, '__version__') else 'Unknown'}")
    except Exception as e:
        logger.error(f"ERROR MT5 Import failed: {e}")
        return
    
    # Test 2: MT5 Initialize
    try:
        logger.info("TEST 2: MT5 Initialize")
        if mt5.initialize():
            logger.info("OK MT5 initialized successfully")
            
            # Get terminal info
            terminal_info = mt5.terminal_info()
            if terminal_info:
                print(f"Terminal Path: {terminal_info.path}")
                print(f"Terminal Version: {terminal_info.build}")
                print(f"Terminal Connected: {terminal_info.connected}")
                print(f"Terminal Trade Allowed: {terminal_info.trade_allowed}")
            
        else:
            error = mt5.last_error()
            logger.error(f"ERROR MT5 Initialize failed: {error}")
            return
    except Exception as e:
        logger.error(f"ERROR MT5 Initialize exception: {e}")
        return
    
    # Test 3: Account Info (without login)
    try:
        logger.info("TEST 3: Current Account Info")
        account_info = mt5.account_info()
        if account_info:
            print(f"Current Account: {account_info.login}")
            print(f"Current Server: {account_info.server}")
            print(f"Current Balance: ${account_info.balance}")
            print(f"Current Company: {account_info.company}")
        else:
            logger.info("No current account logged in")
    except Exception as e:
        logger.warning(f"Account info error: {e}")
    
    # Test 4: Available Demo Accounts Test
    try:
        logger.info("TEST 4: Testing Common Demo Account Patterns")
        
        # Common demo account numbers to test
        test_accounts = [
            95244786,  # Original target
            107034604,  # One digit off
            107034606,  # One digit off
            5000000000, # Common demo pattern
            1000000000, # Common demo pattern
        ]
        
        for test_account in test_accounts:
            try:
                # Try without server (auto-detect)
                result = mt5.login(test_account)
                if result:
                    account_info = mt5.account_info()
                    logger.info(f"OK SUCCESS: Account {test_account} connected!")
                    print(f"   Server: {account_info.server}")
                    print(f"   Balance: ${account_info.balance}")
                    print(f"   Company: {account_info.company}")
                    
                    # Test symbol access
                    symbols = mt5.symbols_get()
                    if symbols:
                        forex_count = len([s for s in symbols if len(s.name) == 6])
                        print(f"   Available Forex Pairs: {forex_count}")
                    
                    break
                else:
                    error = mt5.last_error()
                    logger.info(f"ERROR Account {test_account} failed: {error}")
                    
            except Exception as e:
                logger.warning(f"Error testing account {test_account}: {e}")
                
    except Exception as e:
        logger.error(f"Account testing failed: {e}")
    
    # Test 5: Symbol Scan (if connected)
    try:
        logger.info("TEST 5: Symbol Availability Scan")
        symbols = mt5.symbols_get()
        if symbols:
            total_symbols = len(symbols)
            forex_symbols = [s for s in symbols if len(s.name) == 6 and any(curr in s.name for curr in ['USD', 'EUR', 'GBP', 'JPY'])]
            
            print(f"Total Symbols Available: {total_symbols}")
            print(f"Forex Symbols Detected: {len(forex_symbols)}")
            
            if forex_symbols:
                print("Sample Forex Pairs:")
                for symbol in forex_symbols[:15]:  # Show first 15
                    print(f"   {symbol.name} - {symbol.description if hasattr(symbol, 'description') else 'N/A'}")
        else:
            logger.warning("No symbols available")
            
    except Exception as e:
        logger.error(f"Symbol scan failed: {e}")
    
    # Cleanup
    try:
        mt5.shutdown()
        logger.info("MT5 shutdown completed")
    except:
        pass
    
    print("=" * 60)
    print("DIAGNOSTIC SCAN COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    submarine_diagnostic_scan()