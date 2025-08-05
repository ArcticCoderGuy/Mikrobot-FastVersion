from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MT5 Crypto Demo Setup Validation
Pre-deployment validation script for immediate weekend launch

Validates all components for business-critical 48-hour crypto trading test.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime, timezone
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoDemoValidator:
    """Comprehensive validation for crypto demo setup"""
    
    def __init__(self):
        self.validation_results = {}
        self.critical_failures = []
        self.warnings = []
        
    async def run_complete_validation(self) -> bool:
        """Run all validation checks"""
        print(" MT5 CRYPTO DEMO SETUP VALIDATION")
        print("=" * 50)
        print(f"Validation Time: {datetime.now(timezone.utc)}")
        print("Target: 48-hour weekend crypto trading")
        print("=" * 50)
        
        try:
            # Core system validation
            await self._validate_python_environment()
            await self._validate_required_packages()
            await self._validate_mt5_installation()
            await self._validate_project_files()
            await self._validate_network_connectivity()
            await self._validate_system_resources()
            
            # Component validation
            await self._validate_trading_components()
            await self._validate_crypto_components()
            await self._validate_emergency_systems()
            
            # Final assessment
            return self._generate_validation_report()
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            traceback.print_exc()
            return False
    
    async def _validate_python_environment(self):
        """Validate Python environment"""
        print("\n Python Environment Validation")
        
        try:
            # Check Python version
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                print(f"OK Python version: {version.major}.{version.minor}.{version.micro}")
                self.validation_results['python_version'] = True
            else:
                print(f"ERROR Python version too old: {version.major}.{version.minor}")
                self.critical_failures.append("Python version < 3.8")
                self.validation_results['python_version'] = False
            
            # Check asyncio support
            try:
                import asyncio
                print("OK Asyncio support: Available")
                self.validation_results['asyncio'] = True
            except ImportError:
                print("ERROR Asyncio support: Not available")
                self.critical_failures.append("No asyncio support")
                self.validation_results['asyncio'] = False
            
            # Check path configuration
            current_path = os.getcwd()
            print(f"OK Working directory: {current_path}")
            self.validation_results['working_directory'] = True
            
        except Exception as e:
            print(f"ERROR Python environment error: {e}")
            self.critical_failures.append(f"Python environment: {e}")
            self.validation_results['python_environment'] = False
    
    async def _validate_required_packages(self):
        """Validate required Python packages"""
        print("\n Package Dependencies Validation")
        
        required_packages = {
            'MetaTrader5': 'MT5 API integration',
            'aiohttp': 'Async HTTP client',
            'websockets': 'WebSocket connectivity',
            'pandas': 'Data manipulation',
            'json': 'JSON processing',
            'logging': 'Logging system',
            'datetime': 'Date/time handling',
            'asyncio': 'Async operations'
        }
        
        missing_packages = []
        for package, description in required_packages.items():
            try:
                __import__(package)
                print(f"OK {package}: Available ({description})")
            except ImportError:
                print(f"ERROR {package}: Missing ({description})")
                missing_packages.append(package)
        
        if missing_packages:
            self.critical_failures.append(f"Missing packages: {missing_packages}")
            self.validation_results['packages'] = False
            print(f"\nTOOL Install missing packages:")
            print(f"pip install {' '.join(missing_packages)}")
        else:
            print("OK All required packages available")
            self.validation_results['packages'] = True
    
    async def _validate_mt5_installation(self):
        """Validate MetaTrader 5 installation"""
        print("\n MetaTrader 5 Installation Validation")
        
        try:
            import MetaTrader5 as mt5
            
            # Test MT5 initialization
            if mt5.initialize():
                terminal_info = mt5.terminal_info()
                if terminal_info:
                    print(f"OK MT5 Terminal: {terminal_info.name}")
                    print(f"OK MT5 Version: {terminal_info.build}")
                    print(f"OK MT5 Path: {terminal_info.path}")
                    
                    # Check if demo trading is available
                    print(f"OK Demo Trading: {'Available' if terminal_info.trade_allowed else 'Check permissions'}")
                    
                    self.validation_results['mt5_installation'] = True
                else:
                    print("ERROR MT5 terminal info not available")
                    self.critical_failures.append("MT5 terminal info unavailable")
                    self.validation_results['mt5_installation'] = False
                
                mt5.shutdown()
            else:
                print("ERROR MT5 initialization failed")
                print("   - Check MT5 terminal is installed")
                print("   - Verify MT5 is not running (close if open)")
                print("   - Run as administrator if needed")
                self.critical_failures.append("MT5 initialization failed")
                self.validation_results['mt5_installation'] = False
                
        except ImportError:
            print("ERROR MetaTrader5 package not installed")
            print("   Install with: pip install MetaTrader5")
            self.critical_failures.append("MetaTrader5 package missing")
            self.validation_results['mt5_installation'] = False
        except Exception as e:
            print(f"ERROR MT5 validation error: {e}")
            self.critical_failures.append(f"MT5 error: {e}")
            self.validation_results['mt5_installation'] = False
    
    async def _validate_project_files(self):
        """Validate project files are present"""
        print("\n Project Files Validation")
        
        required_files = {
            'mt5_crypto_demo_config.py': 'Main trading configuration',
            'emergency_protocols.py': 'Emergency response system',
            'quick_deploy_crypto_demo.py': 'Quick deployment script',
            'src/core/connectors/mt5_connector.py': 'MT5 connector',
            'src/core/live_trading/live_trading_engine.py': 'Live trading engine',
            'src/core/data_ingestion/crypto_connector.py': 'Crypto data connector'
        }
        
        missing_files = []
        for filepath, description in required_files.items():
            if os.path.exists(filepath):
                print(f"OK {filepath}: Found ({description})")
            else:
                print(f"ERROR {filepath}: Missing ({description})")
                missing_files.append(filepath)
        
        if missing_files:
            self.critical_failures.append(f"Missing files: {missing_files}")
            self.validation_results['project_files'] = False
        else:
            print("OK All required project files present")
            self.validation_results['project_files'] = True
        
        # Check file permissions
        test_file = "validation_test.tmp"
        try:
            with open(test_file, 'w', encoding='ascii', errors='ignore') as f:
                f.write("test")
            os.remove(test_file)
            print("OK File write permissions: OK")
            self.validation_results['file_permissions'] = True
        except Exception as e:
            print(f"ERROR File write permissions: Failed ({e})")
            self.warnings.append("File write permissions issue")
            self.validation_results['file_permissions'] = False
    
    async def _validate_network_connectivity(self):
        """Validate network connectivity"""
        print("\n Network Connectivity Validation")
        
        try:
            import aiohttp
            
            # Test Binance API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://api.binance.com/api/v3/ping", timeout=10) as response:
                        if response.status == 200:
                            print("OK Binance API: Connected")
                            self.validation_results['binance_api'] = True
                        else:
                            print(f"ERROR Binance API: Error {response.status}")
                            self.warnings.append("Binance API connectivity issue")
                            self.validation_results['binance_api'] = False
            except Exception as e:
                print(f"ERROR Binance API: Connection failed ({e})")
                self.warnings.append("Binance API unreachable")
                self.validation_results['binance_api'] = False
            
            # Test general internet connectivity
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://www.google.com", timeout=5) as response:
                        if response.status == 200:
                            print("OK Internet connectivity: OK")
                            self.validation_results['internet'] = True
                        else:
                            print("ERROR Internet connectivity: Limited")
                            self.warnings.append("Internet connectivity issue")
                            self.validation_results['internet'] = False
            except:
                print("ERROR Internet connectivity: Failed")
                self.warnings.append("No internet connectivity")
                self.validation_results['internet'] = False
                
        except ImportError:
            print("ERROR aiohttp not available for network testing")
            self.warnings.append("Cannot test network connectivity")
            self.validation_results['network_testing'] = False
    
    async def _validate_system_resources(self):
        """Validate system resources"""
        print("\n System Resources Validation")
        
        try:
            import psutil
            
            # Memory check
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            if available_gb > 1.0:
                print(f"OK Available memory: {available_gb:.1f} GB")
                self.validation_results['memory'] = True
            else:
                print(f"WARNING Low memory: {available_gb:.1f} GB")
                self.warnings.append("Low available memory")
                self.validation_results['memory'] = False
            
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 80:
                print(f"OK CPU usage: {cpu_percent}%")
                self.validation_results['cpu'] = True
            else:
                print(f"WARNING High CPU usage: {cpu_percent}%")
                self.warnings.append("High CPU usage")
                self.validation_results['cpu'] = False
            
            # Disk space check
            disk_usage = psutil.disk_usage('.')
            free_gb = disk_usage.free / (1024**3)
            if free_gb > 1.0:
                print(f"OK Free disk space: {free_gb:.1f} GB")
                self.validation_results['disk'] = True
            else:
                print(f"WARNING Low disk space: {free_gb:.1f} GB")
                self.warnings.append("Low disk space")
                self.validation_results['disk'] = False
                
        except ImportError:
            print("WARNING psutil not available - skipping resource checks")
            self.warnings.append("Cannot check system resources")
            self.validation_results['system_resources'] = False
        except Exception as e:
            print(f"ERROR System resource check error: {e}")
            self.warnings.append(f"Resource check error: {e}")
            self.validation_results['system_resources'] = False
    
    async def _validate_trading_components(self):
        """Validate trading system components"""
        print("\nFAST Trading Components Validation")
        
        try:
            # Test import of core components
            sys.path.append(os.path.dirname(__file__))
            
            # Validate MT5 connector
            try:
                from src.core.connectors.mt5_connector import MT5Connector, MT5Config
                print("OK MT5Connector: Importable")
                self.validation_results['mt5_connector'] = True
            except Exception as e:
                print(f"ERROR MT5Connector: Import failed ({e})")
                self.critical_failures.append("MT5Connector import failed")
                self.validation_results['mt5_connector'] = False
            
            # Validate live trading engine
            try:
                from src.core.live_trading.live_trading_engine import LiveTradingEngine
                print("OK LiveTradingEngine: Importable")
                self.validation_results['trading_engine'] = True
            except Exception as e:
                print(f"ERROR LiveTradingEngine: Import failed ({e})")
                self.critical_failures.append("LiveTradingEngine import failed")
                self.validation_results['trading_engine'] = False
            
            # Validate error recovery
            try:
                from src.core.live_trading.error_recovery_system import ErrorRecoverySystem
                print("OK ErrorRecoverySystem: Importable")
                self.validation_results['error_recovery'] = True
            except Exception as e:
                print(f"ERROR ErrorRecoverySystem: Import failed ({e})")
                self.critical_failures.append("ErrorRecoverySystem import failed")
                self.validation_results['error_recovery'] = False
            
            # Validate position manager
            try:
                from src.core.live_trading.position_manager import PositionManager
                print("OK PositionManager: Importable")
                self.validation_results['position_manager'] = True
            except Exception as e:
                print(f"ERROR PositionManager: Import failed ({e})")
                self.critical_failures.append("PositionManager import failed")
                self.validation_results['position_manager'] = False
                
        except Exception as e:
            print(f"ERROR Trading components validation error: {e}")
            self.critical_failures.append(f"Trading components error: {e}")
    
    async def _validate_crypto_components(self):
        """Validate crypto-specific components"""
        print("\n Crypto Components Validation")
        
        try:
            # Validate crypto connector
            try:
                from src.core.data_ingestion.crypto_connector import CryptoDataConnector
                print("OK CryptoDataConnector: Importable")
                self.validation_results['crypto_connector'] = True
            except Exception as e:
                print(f"ERROR CryptoDataConnector: Import failed ({e})")
                self.critical_failures.append("CryptoDataConnector import failed")
                self.validation_results['crypto_connector'] = False
            
            # Validate demo configuration
            try:
                from mt5_crypto_demo_config import MT5CryptoDemoEnvironment, CryptoTradingConfig
                print("OK CryptoDemoConfig: Importable")
                self.validation_results['demo_config'] = True
            except Exception as e:
                print(f"ERROR CryptoDemoConfig: Import failed ({e})")
                self.critical_failures.append("CryptoDemoConfig import failed")
                self.validation_results['demo_config'] = False
                
        except Exception as e:
            print(f"ERROR Crypto components validation error: {e}")
            self.critical_failures.append(f"Crypto components error: {e}")
    
    async def _validate_emergency_systems(self):
        """Validate emergency and safety systems"""
        print("\n Emergency Systems Validation")
        
        try:
            # Validate emergency protocols
            try:
                from emergency_protocols import EmergencyProtocol, EmergencyLevel, EmergencyType
                print("OK EmergencyProtocol: Importable")
                self.validation_results['emergency_protocol'] = True
            except Exception as e:
                print(f"ERROR EmergencyProtocol: Import failed ({e})")
                self.critical_failures.append("EmergencyProtocol import failed")
                self.validation_results['emergency_protocol'] = False
            
            # Validate quick deploy
            try:
                from quick_deploy_crypto_demo import QuickDeployManager
                print("OK QuickDeployManager: Importable")
                self.validation_results['quick_deploy'] = True
            except Exception as e:
                print(f"ERROR QuickDeployManager: Import failed ({e})")
                self.critical_failures.append("QuickDeployManager import failed")
                self.validation_results['quick_deploy'] = False
                
        except Exception as e:
            print(f"ERROR Emergency systems validation error: {e}")
            self.critical_failures.append(f"Emergency systems error: {e}")
    
    def _generate_validation_report(self) -> bool:
        """Generate final validation report"""
        print("\nCHART VALIDATION SUMMARY")
        print("=" * 50)
        
        # Count results
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for result in self.validation_results.values() if result)
        failed_checks = total_checks - passed_checks
        
        # Display summary
        print(f"Total Checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {failed_checks}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Critical Failures: {len(self.critical_failures)}")
        
        # Detailed results
        print("\n DETAILED RESULTS:")
        for check, result in self.validation_results.items():
            status = "OK PASS" if result else "ERROR FAIL"
            print(f"   {check}: {status}")
        
        # Critical failures
        if self.critical_failures:
            print("\n CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"   ERROR {failure}")
        
        # Warnings
        if self.warnings:
            print("\nWARNING WARNINGS:")
            for warning in self.warnings:
                print(f"   WARNING {warning}")
        
        # Overall assessment
        print("\n" + "=" * 50)
        if len(self.critical_failures) == 0:
            if len(self.warnings) == 0:
                print("OK VALIDATION SUCCESSFUL - READY FOR DEPLOYMENT")
                print("All systems validated - proceed with confidence!")
                return True
            else:
                print("WARNING VALIDATION PASSED WITH WARNINGS")
                print("System is functional but review warnings before deployment")
                return True
        else:
            print("ERROR VALIDATION FAILED - NOT READY FOR DEPLOYMENT")
            print("Critical issues must be resolved before proceeding")
            return False


async def main():
    """Main validation execution"""
    validator = CryptoDemoValidator()
    
    try:
        result = await validator.run_complete_validation()
        
        if result:
            print("\n READY FOR 48-HOUR CRYPTO TRADING TEST")
            print("Execute: python quick_deploy_crypto_demo.py")
        else:
            print("\nTOOL RESOLVE ISSUES BEFORE DEPLOYMENT")
            print("Check error messages above and retry validation")
        
        return result
        
    except Exception as e:
        print(f"\nERROR VALIDATION ERROR: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    print(" MT5 CRYPTO DEMO SETUP VALIDATION")
    print("Comprehensive pre-deployment validation for weekend crypto trading")
    print("=" * 70)
    
    result = asyncio.run(main())
    
    if result:
        print("\nOK VALIDATION COMPLETE - SYSTEM READY")
    else:
        print("\nERROR VALIDATION FAILED - SYSTEM NOT READY")
    
    sys.exit(0 if result else 1)