from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Quick Deployment Script for MT5 Crypto Demo
48-Hour Weekend Trading Test - Immediate Launch

This script provides one-click deployment for business-critical crypto trading validation.
Target: 10kEUR weekly revenue validation through weekend crypto markets.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timezone
import traceback

# Add project root to path
sys.path.append(os.path.dirname(__file__))

# Import configuration and emergency protocols
from mt5_crypto_demo_config import MT5CryptoDemoEnvironment, CryptoTradingConfig
from emergency_protocols import EmergencyProtocol

# Configure logging for immediate visibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'crypto_demo_deploy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


class QuickDeployManager:
    """
    Quick deployment manager for immediate weekend crypto trading
    
    Features:
    - One-click initialization
    - Pre-flight safety checks
    - Automatic error recovery
    - Real-time monitoring
    - Emergency stop protocols
    """
    
    def __init__(self):
        self.deployment_start = datetime.now(timezone.utc)
        self.trading_env = None
        self.emergency_protocol = None
        self.deployment_success = False
        
        logger.info("Quick Deploy Manager initialized")
    
    async def deploy(self) -> bool:
        """Execute complete deployment for immediate trading"""
        try:
            print("ROCKET MT5 CRYPTO DEMO - QUICK DEPLOYMENT")
            print("=" * 60)
            print(f"Deployment Time: {self.deployment_start}")
            print("Target: 48-hour weekend crypto trading validation")
            print("Account: 107034605 (Demo)")
            print("Risk: Conservative (1% per trade, 5% daily)")
            print("=" * 60)
            
            # Step 1: Pre-deployment validation
            if not await self._pre_deployment_checks():
                print("ERROR Pre-deployment checks failed")
                return False
            
            # Step 2: Get credentials
            credentials = await self._get_credentials()
            if not credentials:
                print("ERROR Credential validation failed")
                return False
            
            # Step 3: Initialize trading environment
            if not await self._initialize_environment(credentials):
                print("ERROR Environment initialization failed")
                return False
            
            # Step 4: Setup emergency protocols
            if not await self._setup_emergency_protocols():
                print("ERROR Emergency protocol setup failed")
                return False
            
            # Step 5: Final pre-trading validation
            if not await self._final_validation():
                print("ERROR Final validation failed")
                return False
            
            # Step 6: Start trading
            if not await self._start_trading():
                print("ERROR Trading start failed")
                return False
            
            self.deployment_success = True
            print("\nOK DEPLOYMENT SUCCESSFUL - LIVE TRADING ACTIVE")
            print("Monitor logs for real-time trading updates...")
            
            # Keep deployment manager running
            await self._monitor_deployment()
            
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            print(f"ERROR DEPLOYMENT FAILED: {e}")
            traceback.print_exc()
            return False
    
    async def _pre_deployment_checks(self) -> bool:
        """Comprehensive pre-deployment validation"""
        print("\n Running pre-deployment checks...")
        
        checks = {
            'Python Environment': self._check_python_environment(),
            'Required Packages': await self._check_packages(),
            'MT5 Terminal': await self._check_mt5_terminal(),
            'Network Connectivity': await self._check_network(),
            'File Permissions': self._check_file_permissions(),
            'System Resources': self._check_system_resources()
        }
        
        all_passed = True
        for check_name, result in checks.items():
            if result:
                print(f"OK {check_name}: PASS")
            else:
                print(f"ERROR {check_name}: FAIL")
                all_passed = False
        
        if all_passed:
            print("OK All pre-deployment checks passed")
        else:
            print("ERROR Some pre-deployment checks failed")
        
        return all_passed
    
    def _check_python_environment(self) -> bool:
        """Check Python version and environment"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
                return True
            else:
                logger.error(f"Python version too old: {version}")
                return False
        except Exception as e:
            logger.error(f"Python check error: {e}")
            return False
    
    async def _check_packages(self) -> bool:
        """Check required packages are installed"""
        required_packages = [
            'MetaTrader5',
            'asyncio',
            'aiohttp',
            'websockets',
            'pandas'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"Missing packages: {missing_packages}")
            print(f"Install missing packages: pip install {' '.join(missing_packages)}")
            return False
        
        return True
    
    async def _check_mt5_terminal(self) -> bool:
        """Check MT5 terminal availability"""
        try:
            import MetaTrader5 as mt5
            
            # Try to initialize MT5 (will fail if not installed)
            if mt5.initialize():
                terminal_info = mt5.terminal_info()
                if terminal_info:
                    logger.info(f"MT5 Terminal: {terminal_info.name}")
                    logger.info(f"MT5 Version: {terminal_info.build}")
                    mt5.shutdown()
                    return True
                else:
                    logger.error("MT5 terminal info not available")
                    mt5.shutdown()
                    return False
            else:
                logger.error("MT5 initialization failed - check installation")
                return False
                
        except Exception as e:
            logger.error(f"MT5 check error: {e}")
            return False
    
    async def _check_network(self) -> bool:
        """Check network connectivity"""
        try:
            import aiohttp
            
            # Test Binance API connectivity
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.binance.com/api/v3/ping", timeout=10) as response:
                    if response.status == 200:
                        logger.info("Binance API connectivity: OK")
                        return True
                    else:
                        logger.error(f"Binance API error: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Network check error: {e}")
            return False
    
    def _check_file_permissions(self) -> bool:
        """Check file system permissions"""
        try:
            # Test write access to current directory
            test_file = "test_write_access.tmp"
            with open(test_file, 'w', encoding='ascii', errors='ignore') as f:
                f.write("test")
            os.remove(test_file)
            
            # Test write access to MT5 files directory
            mt5_files_dir = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "MetaQuotes", "Terminal", "Common", "Files")
            if os.path.exists(mt5_files_dir):
                test_file_mt5 = os.path.join(mt5_files_dir, "test_write.tmp")
                try:
                    with open(test_file_mt5, 'w', encoding='ascii', errors='ignore') as f:
                        f.write("test")
                    os.remove(test_file_mt5)
                    logger.info("MT5 files directory: Write access OK")
                except:
                    logger.warning("MT5 files directory: Limited write access")
            
            return True
            
        except Exception as e:
            logger.error(f"File permissions check error: {e}")
            return False
    
    def _check_system_resources(self) -> bool:
        """Check available system resources"""
        try:
            import psutil
            
            # Check memory
            memory = psutil.virtual_memory()
            if memory.available > 1024 * 1024 * 1024:  # 1GB available
                logger.info(f"Available memory: {memory.available / (1024**3):.1f} GB")
            else:
                logger.warning("Low available memory")
                return False
            
            # Check CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 80:
                logger.info(f"CPU usage: {cpu_percent}%")
            else:
                logger.warning(f"High CPU usage: {cpu_percent}%")
            
            return True
            
        except ImportError:
            logger.warning("psutil not available - skipping resource check")
            return True
        except Exception as e:
            logger.error(f"Resource check error: {e}")
            return True  # Non-critical
    
    async def _get_credentials(self) -> dict:
        """Get and validate credentials"""
        print("\n Credential Configuration")
        
        # Demo account details
        account = 107034605
        
        # Get password from user
        import getpass
        password = getpass.getpass("Enter demo account password: ").strip()
        
        if not password:
            print("ERROR Password is required")
            return None
        
        # Validate credentials format
        if len(password) < 4:
            print("ERROR Password too short")
            return None
        
        credentials = {
            'account': account,
            'password': password,
            'server': 'MetaQuotes-Demo'
        }
        
        print(f"OK Credentials configured for account {account}")
        return credentials
    
    async def _initialize_environment(self, credentials: dict) -> bool:
        """Initialize complete trading environment"""
        print("\nTOOL Initializing trading environment...")
        
        try:
            # Create configuration
            config = CryptoTradingConfig()
            config.account_number = credentials['account']
            config.server = credentials['server']
            
            # Initialize environment
            self.trading_env = MT5CryptoDemoEnvironment(config)
            
            # Initialize with credentials
            if await self.trading_env.initialize(credentials['password']):
                print("OK Trading environment initialized successfully")
                return True
            else:
                print("ERROR Trading environment initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Environment initialization error: {e}")
            print(f"ERROR Environment initialization error: {e}")
            return False
    
    async def _setup_emergency_protocols(self) -> bool:
        """Setup emergency protocols and monitoring"""
        print("\n Setting up emergency protocols...")
        
        try:
            # Initialize emergency protocol
            self.emergency_protocol = EmergencyProtocol(self.trading_env)
            
            # Start emergency monitoring
            await self.emergency_protocol.start_monitoring()
            
            print("OK Emergency protocols activated")
            print("   - Connection monitoring")
            print("   - Performance monitoring")
            print("   - Position risk monitoring")
            print("   - Account status monitoring")
            
            return True
            
        except Exception as e:
            logger.error(f"Emergency protocol setup error: {e}")
            print(f"ERROR Emergency protocol setup error: {e}")
            return False
    
    async def _final_validation(self) -> bool:
        """Final validation before trading starts"""
        print("\nOK Final pre-trading validation...")
        
        try:
            # Check account info
            account_info = await self.trading_env.mt5_connector.get_account_info()
            if not account_info:
                print("ERROR Cannot retrieve account information")
                return False
            
            print(f"   Account: {account_info['login']}")
            print(f"   Balance: {account_info['balance']} {account_info['currency']}")
            print(f"   Leverage: 1:{account_info['leverage']}")
            print(f"   Trade Allowed: {account_info['trade_allowed']}")
            
            # Minimum balance check
            if account_info['balance'] < 1000:
                print("ERROR Insufficient demo account balance (minimum 1000)")
                return False
            
            # Trading permission check
            if not account_info['trade_allowed']:
                print("ERROR Trading not allowed on this account")
                return False
            
            # Check crypto symbols
            symbols_available = []
            for symbol in self.trading_env.config.primary_symbols:
                symbol_info = await self.trading_env.mt5_connector.get_symbol_info(symbol)
                if symbol_info:
                    symbols_available.append(symbol)
            
            if len(symbols_available) < 2:
                print(f"ERROR Insufficient crypto symbols available: {symbols_available}")
                return False
            
            print(f"   Available symbols: {', '.join(symbols_available)}")
            
            # Check weekend trading capability
            weekend_trading = datetime.now(timezone.utc).weekday() >= 5  # Saturday or Sunday
            if weekend_trading:
                print("   Weekend crypto trading: ENABLED")
            else:
                print("   Weekday trading: ENABLED")
            
            print("OK All final validations passed")
            return True
            
        except Exception as e:
            logger.error(f"Final validation error: {e}")
            print(f"ERROR Final validation error: {e}")
            return False
    
    async def _start_trading(self) -> bool:
        """Start live trading"""
        print("\nROCKET Starting live crypto trading...")
        
        try:
            # Final confirmation
            print("\nTRADING CONFIGURATION:")
            print(f"   Demo Account: {self.trading_env.config.account_number}")
            print(f"   Risk per Trade: {self.trading_env.config.max_risk_per_trade * 100}%")
            print(f"   Daily Risk Limit: {self.trading_env.config.max_daily_risk * 100}%")
            print(f"   Max Position Size: {self.trading_env.config.max_position_size} lots")
            print(f"   Stop Loss: {self.trading_env.config.stop_loss_pips} pips")
            print(f"   Take Profit: {self.trading_env.config.take_profit_pips} pips")
            print(f"   Duration: 48 hours")
            
            confirm = input("\n START LIVE TRADING? (type 'START' to confirm): ").strip()
            if confirm != 'START':
                print("Trading cancelled by user")
                return False
            
            # Start trading
            if await self.trading_env.start_trading():
                print("\nOK LIVE CRYPTO TRADING STARTED")
                print(f"   Start Time: {datetime.now(timezone.utc)}")
                print(f"   End Time: {datetime.now(timezone.utc)} + 48 hours")
                print("\nCHART Monitor real-time performance in logs...")
                return True
            else:
                print("ERROR Failed to start trading")
                return False
                
        except Exception as e:
            logger.error(f"Trading start error: {e}")
            print(f"ERROR Trading start error: {e}")
            return False
    
    async def _monitor_deployment(self):
        """Monitor deployment and trading session"""
        print("\nCHART Deployment monitoring active...")
        print("Press Ctrl+C to stop trading and generate final report")
        
        try:
            while self.trading_env.trading_active:
                # Display periodic status updates
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Get current statistics
                if self.trading_env.trading_engine:
                    stats = self.trading_env.trading_engine.get_execution_stats()
                    print(f"\n {datetime.now().strftime('%H:%M:%S')} STATUS UPDATE:")
                    print(f"   Orders: {stats['total_orders']} | Success: {stats.get('success_rate', 0):.1%} | Avg: {stats['avg_execution_time_ms']:.1f}ms")
                    
                    if stats['total_orders'] > 0:
                        account_info = await self.trading_env.mt5_connector.get_account_info()
                        if account_info:
                            print(f"   Balance: {account_info['balance']} | Equity: {account_info['equity']} | P&L: {account_info['profit']}")
                
        except KeyboardInterrupt:
            print("\n Manual stop requested...")
            await self.trading_env.stop_trading("User requested stop")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            await self.trading_env.stop_trading(f"Monitoring error: {e}")
        
        print("\nOK Deployment monitoring completed")
        return True


async def main():
    """Main deployment execution"""
    deploy_manager = QuickDeployManager()
    
    try:
        success = await deploy_manager.deploy()
        
        if success:
            print("\n DEPLOYMENT COMPLETED SUCCESSFULLY")
            print("Trading session active - check logs for updates")
        else:
            print("\nERROR DEPLOYMENT FAILED")
            print("Check logs for error details")
        
        return success
        
    except KeyboardInterrupt:
        print("\n Deployment cancelled by user")
        return False
    except Exception as e:
        print(f"\nERROR DEPLOYMENT ERROR: {e}")
        logger.error(f"Main deployment error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    print("ROCKET MT5 CRYPTO DEMO - QUICK DEPLOYMENT SCRIPT")
    print("=" * 60)
    print("Business-critical 48-hour weekend crypto trading validation")
    print("Above Robust! operational standards")
    print("Target: 10kEUR weekly revenue validation")
    print("=" * 60)
    
    # Run deployment
    result = asyncio.run(main())
    
    if result:
        print("\nOK QUICK DEPLOYMENT SUCCESSFUL")
        print("Live crypto trading is now active!")
        print("Monitor logs for real-time trading updates...")
    else:
        print("\nERROR QUICK DEPLOYMENT FAILED")
        print("Review error messages and try again")
        
    sys.exit(0 if result else 1)