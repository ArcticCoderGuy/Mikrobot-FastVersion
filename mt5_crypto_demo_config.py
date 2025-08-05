from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MT5 Crypto Demo Trading Configuration
48-Hour Live Trading Test Setup for Account 107034605

Above Robust! operational standards implementation for immediate weekend crypto trading.
This is business-critical configuration targeting 10kEUR weekly revenue validation.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import MetaTrader5 as mt5

# Import existing system components
from src.core.connectors.mt5_connector import MT5Connector, MT5Config
from src.core.live_trading.live_trading_engine import LiveTradingEngine, TradingOrder, OrderSide, OrderType
from src.core.live_trading.error_recovery_system import ErrorRecoverySystem
from src.core.live_trading.position_manager import PositionManager
from src.core.data_ingestion.crypto_connector import CryptoDataConnector
from src.core.product_owner_agent import ProductOwnerAgent

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'mt5_crypto_demo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class CryptoTradingConfig:
    """Comprehensive crypto trading configuration"""
    # Demo account credentials
    account_number: int = 107034605
    password: str = ""  # Set during initialization
    server: str = "MetaQuotes-Demo"  # Standard demo server
    
    # Risk management parameters (Conservative for demo test)
    max_risk_per_trade: float = 0.01  # 1% per trade
    max_daily_risk: float = 0.05      # 5% daily limit
    max_position_size: float = 0.1    # 0.1 lots maximum
    stop_loss_pips: int = 50          # 50 pips SL
    take_profit_pips: int = 100       # 100 pips TP
    
    # Trading symbols (Focus on BTC/ETH as requested)
    primary_symbols: List[str] = field(default_factory=lambda: [
        "BTCUSD",   # Bitcoin USD
        "ETHUSD",   # Ethereum USD
        "XRPUSD",   # Ripple USD (backup)
        "ADAUSD",   # Cardano USD (backup)
    ])
    
    # Weekend crypto trading (24/7 markets)
    weekend_trading_enabled: bool = True
    trading_hours_24_7: bool = True
    
    # Performance targets (Above Robust! standards)
    target_execution_latency_ms: float = 50.0  # <50ms execution
    target_success_rate: float = 0.99          # 99% success rate
    max_slippage_pips: float = 2.0             # 2 pips max slippage
    
    # Emergency protocols
    emergency_stop_loss_percent: float = 0.10  # 10% account loss = emergency stop
    circuit_breaker_failure_threshold: int = 3  # 3 failures = circuit breaker
    
    # Monitoring intervals
    health_check_interval_seconds: int = 30
    position_monitor_interval_seconds: int = 10
    error_recovery_timeout_seconds: int = 60


class MT5CryptoDemoEnvironment:
    """
    Production-grade MT5 crypto demo trading environment
    
    Implements Above Robust! standards:
    - 99.9% uptime target
    - <50ms execution latency
    - Real-time monitoring and alerting
    - Automatic error recovery
    - Emergency stop protocols
    """
    
    def __init__(self, config: CryptoTradingConfig):
        self.config = config
        self.is_initialized = False
        self.trading_active = False
        
        # Core components
        self.mt5_connector: Optional[MT5Connector] = None
        self.trading_engine: Optional[LiveTradingEngine] = None
        self.error_recovery: Optional[ErrorRecoverySystem] = None
        self.position_manager: Optional[PositionManager] = None
        self.product_owner: Optional[ProductOwnerAgent] = None
        self.crypto_connector: Optional[CryptoDataConnector] = None
        
        # Performance tracking
        self.performance_metrics = {
            'session_start': datetime.now(timezone.utc),
            'orders_executed': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'avg_execution_time_ms': 0.0,
            'uptime_percentage': 100.0
        }
        
        # Health monitoring
        self.health_status = {
            'mt5_connected': False,
            'trading_engine_active': False,
            'error_recovery_ready': False,
            'position_manager_active': False,
            'crypto_feed_connected': False,
            'last_health_check': datetime.now(timezone.utc)
        }
        
        logger.info("MT5 Crypto Demo Environment initialized - Above Robust! standards")
    
    async def initialize(self, password: str) -> bool:
        """
        Initialize complete trading environment for immediate deployment
        """
        try:
            logger.info("ROCKET Initializing MT5 Crypto Demo Environment...")
            
            # Set password
            self.config.password = password
            
            # Step 1: Initialize MT5 Connector
            if not await self._initialize_mt5_connector():
                logger.error("ERROR MT5 connector initialization failed")
                return False
            
            # Step 2: Initialize Crypto Data Feed
            if not await self._initialize_crypto_connector():
                logger.error("ERROR Crypto connector initialization failed")
                return False
            
            # Step 3: Initialize ProductOwner Agent
            if not await self._initialize_product_owner():
                logger.error("ERROR ProductOwner initialization failed")
                return False
            
            # Step 4: Initialize Trading Engine
            if not await self._initialize_trading_engine():
                logger.error("ERROR Trading engine initialization failed")
                return False
            
            # Step 5: Initialize Error Recovery System
            if not await self._initialize_error_recovery():
                logger.error("ERROR Error recovery system initialization failed")
                return False
            
            # Step 6: Initialize Position Manager
            if not await self._initialize_position_manager():
                logger.error("ERROR Position manager initialization failed")
                return False
            
            # Step 7: Validate crypto symbol availability
            if not await self._validate_crypto_symbols():
                logger.error("ERROR Crypto symbol validation failed")
                return False
            
            # Step 8: Start monitoring systems
            await self._start_monitoring()
            
            self.is_initialized = True
            logger.info("OK MT5 Crypto Demo Environment READY for live trading")
            
            # Log configuration summary
            await self._log_configuration_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"ERROR Environment initialization failed: {e}")
            return False
    
    async def _initialize_mt5_connector(self) -> bool:
        """Initialize MT5 connector with demo account credentials"""
        try:
            logger.info("Initializing MT5 connector...")
            
            mt5_config = MT5Config(
                login=self.config.account_number,
                password=self.config.password,
                server=self.config.server,
                timeout=60000,
                retry_count=3,
                retry_delay=5
            )
            
            self.mt5_connector = MT5Connector(mt5_config)
            
            if await self.mt5_connector.connect():
                # Verify account info
                account_info = await self.mt5_connector.get_account_info()
                if account_info:
                    logger.info(f"OK Connected to MT5 Demo Account: {account_info['login']}")
                    logger.info(f"   Balance: {account_info['balance']} {account_info['currency']}")
                    logger.info(f"   Leverage: 1:{account_info['leverage']}")
                    logger.info(f"   Trade Allowed: {account_info['trade_allowed']}")
                    
                    self.health_status['mt5_connected'] = True
                    return True
                else:
                    logger.error("Failed to retrieve account information")
                    return False
            else:
                logger.error("MT5 connection failed")
                return False
                
        except Exception as e:
            logger.error(f"MT5 connector initialization error: {e}")
            return False
    
    async def _initialize_crypto_connector(self) -> bool:
        """Initialize crypto data connector for real-time feeds"""
        try:
            logger.info("Initializing crypto data connector...")
            
            self.crypto_connector = CryptoDataConnector(use_testnet=False)
            
            if await self.crypto_connector.connect():
                logger.info("OK Connected to Binance crypto data feed")
                
                # Subscribe to primary symbols
                for symbol in ["BTC/USDT", "ETH/USDT"]:
                    await self.crypto_connector.subscribe_symbol(symbol, "crypto")
                    logger.info(f"   Subscribed to {symbol}")
                
                self.health_status['crypto_feed_connected'] = True
                return True
            else:
                logger.error("Crypto connector connection failed")
                return False
                
        except Exception as e:
            logger.error(f"Crypto connector initialization error: {e}")
            return False
    
    async def _initialize_product_owner(self) -> bool:
        """Initialize ProductOwner agent for trade oversight"""
        try:
            logger.info("Initializing ProductOwner agent...")
            
            self.product_owner = ProductOwnerAgent(
                agent_id="crypto_demo_owner",
                risk_tolerance=0.05,  # 5% max risk
                performance_threshold=0.01  # 1% minimum performance
            )
            
            if await self.product_owner.initialize():
                logger.info("OK ProductOwner agent initialized")
                return True
            else:
                logger.error("ProductOwner initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"ProductOwner initialization error: {e}")
            return False
    
    async def _initialize_trading_engine(self) -> bool:
        """Initialize live trading engine with crypto-optimized settings"""
        try:
            logger.info("Initializing live trading engine...")
            
            # Create forex connector wrapper for trading engine compatibility
            from src.core.data_ingestion.forex_connector import ForexDataConnector
            forex_connector = ForexDataConnector()
            
            # Initialize with MT5 connector
            if hasattr(forex_connector, 'mt5_connector'):
                forex_connector.mt5_connector = self.mt5_connector
            
            self.trading_engine = LiveTradingEngine(
                mt5_connector=forex_connector,
                product_owner=self.product_owner,
                max_concurrent_orders=5  # Conservative for demo
            )
            
            # Configure for crypto trading
            self.trading_engine.max_position_size = self.config.max_position_size
            self.trading_engine.max_daily_loss = -self.config.max_daily_risk * 1000  # Assume 1000 base
            
            if await self.trading_engine.start_engine():
                logger.info("OK Live trading engine started")
                self.health_status['trading_engine_active'] = True
                return True
            else:
                logger.error("Trading engine start failed")
                return False
                
        except Exception as e:
            logger.error(f"Trading engine initialization error: {e}")
            return False
    
    async def _initialize_error_recovery(self) -> bool:
        """Initialize error recovery system"""
        try:
            logger.info("Initializing error recovery system...")
            
            self.error_recovery = ErrorRecoverySystem(
                max_retries=3,
                retry_delay=5.0,
                circuit_breaker_threshold=self.config.circuit_breaker_failure_threshold
            )
            
            # Configure recovery strategies for crypto trading
            self.error_recovery.recovery_strategies = {
                'connection_lost': 'reconnect_with_backoff',
                'order_rejection': 'adjust_and_retry',
                'position_error': 'emergency_close',
                'data_feed_error': 'switch_to_backup'
            }
            
            logger.info("OK Error recovery system initialized")
            self.health_status['error_recovery_ready'] = True
            return True
            
        except Exception as e:
            logger.error(f"Error recovery initialization error: {e}")
            return False
    
    async def _initialize_position_manager(self) -> bool:
        """Initialize position manager for crypto trading"""
        try:
            logger.info("Initializing position manager...")
            
            self.position_manager = PositionManager(
                mt5_connector=self.mt5_connector,
                max_positions=10,
                risk_per_trade=self.config.max_risk_per_trade,
                stop_loss_pips=self.config.stop_loss_pips,
                take_profit_pips=self.config.take_profit_pips
            )
            
            if await self.position_manager.initialize():
                logger.info("OK Position manager initialized")
                self.health_status['position_manager_active'] = True
                return True
            else:
                logger.error("Position manager initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Position manager initialization error: {e}")
            return False
    
    async def _validate_crypto_symbols(self) -> bool:
        """Validate crypto symbol availability on MT5"""
        try:
            logger.info("Validating crypto symbol availability...")
            
            available_symbols = []
            for symbol in self.config.primary_symbols:
                symbol_info = await self.mt5_connector.get_symbol_info(symbol)
                if symbol_info:
                    available_symbols.append(symbol)
                    logger.info(f"OK {symbol} available - Spread: {symbol_info.get('spread', 'N/A')}")
                else:
                    logger.warning(f"WARNING {symbol} not available")
            
            if len(available_symbols) >= 2:  # Need at least 2 symbols for diversification
                logger.info(f"OK {len(available_symbols)} crypto symbols validated")
                return True
            else:
                logger.error("Insufficient crypto symbols available")
                return False
                
        except Exception as e:
            logger.error(f"Symbol validation error: {e}")
            return False
    
    async def _start_monitoring(self):
        """Start comprehensive monitoring systems"""
        try:
            logger.info("Starting monitoring systems...")
            
            # Start health check monitor
            asyncio.create_task(self._health_check_monitor())
            
            # Start performance monitor
            asyncio.create_task(self._performance_monitor())
            
            # Start position monitor
            asyncio.create_task(self._position_monitor())
            
            logger.info("OK All monitoring systems started")
            
        except Exception as e:
            logger.error(f"Monitoring system start error: {e}")
    
    async def start_trading(self) -> bool:
        """Start live crypto trading for 48-hour test"""
        if not self.is_initialized:
            logger.error("Environment not initialized")
            return False
        
        try:
            logger.info("ROCKET STARTING 48-HOUR CRYPTO TRADING TEST")
            
            # Final pre-trading checks
            if not await self._pre_trading_checks():
                logger.error("Pre-trading checks failed")
                return False
            
            # Enable trading
            self.trading_active = True
            self.trading_engine.trading_enabled = True
            
            # Log trading start
            start_time = datetime.now(timezone.utc)
            logger.info(f"OK LIVE CRYPTO TRADING STARTED at {start_time}")
            logger.info(f"   Demo Account: {self.config.account_number}")
            logger.info(f"   Target Duration: 48 hours")
            logger.info(f"   End Time: {start_time + timedelta(hours=48)}")
            logger.info(f"   Risk per Trade: {self.config.max_risk_per_trade * 100}%")
            logger.info(f"   Daily Risk Limit: {self.config.max_daily_risk * 100}%")
            
            # Start trading session monitoring
            asyncio.create_task(self._trading_session_monitor())
            
            return True
            
        except Exception as e:
            logger.error(f"Trading start error: {e}")
            return False
    
    async def stop_trading(self, reason: str = "Manual stop"):
        """Stop live trading and generate report"""
        try:
            logger.info(f" STOPPING CRYPTO TRADING: {reason}")
            
            self.trading_active = False
            if self.trading_engine:
                await self.trading_engine.emergency_stop(reason)
            
            # Generate final report
            await self._generate_trading_report()
            
            logger.info("OK Trading stopped successfully")
            
        except Exception as e:
            logger.error(f"Trading stop error: {e}")
    
    async def _pre_trading_checks(self) -> bool:
        """Comprehensive pre-trading validation"""
        try:
            logger.info("Performing pre-trading checks...")
            
            checks = {
                'MT5 Connection': self.health_status['mt5_connected'],
                'Trading Engine': self.health_status['trading_engine_active'],
                'Error Recovery': self.health_status['error_recovery_ready'],
                'Position Manager': self.health_status['position_manager_active'],
                'Crypto Feed': self.health_status['crypto_feed_connected']
            }
            
            all_passed = True
            for check_name, status in checks.items():
                if status:
                    logger.info(f"OK {check_name}: PASS")
                else:
                    logger.error(f"ERROR {check_name}: FAIL")
                    all_passed = False
            
            # Check account balance
            account_info = await self.mt5_connector.get_account_info()
            if account_info and account_info['balance'] > 1000:  # Minimum 1000 for demo
                logger.info(f"OK Account Balance: {account_info['balance']} {account_info['currency']}")
            else:
                logger.error("ERROR Insufficient account balance")
                all_passed = False
            
            # Check weekend crypto market availability
            if self.config.weekend_trading_enabled:
                logger.info("OK Weekend crypto trading enabled")
            
            return all_passed
            
        except Exception as e:
            logger.error(f"Pre-trading checks error: {e}")
            return False
    
    async def _health_check_monitor(self):
        """Continuous health monitoring"""
        logger.info("Health check monitor started")
        
        while self.is_initialized:
            try:
                # Update health status
                self.health_status['last_health_check'] = datetime.now(timezone.utc)
                
                # Check MT5 connection
                if self.mt5_connector and not self.mt5_connector.is_connected:
                    logger.warning("WARNING MT5 connection lost - attempting recovery")
                    if await self.mt5_connector.connect():
                        logger.info("OK MT5 connection recovered")
                    else:
                        logger.error("ERROR MT5 recovery failed")
                
                # Check trading engine health
                if self.trading_engine:
                    stats = self.trading_engine.get_execution_stats()
                    if stats['success_rate'] < 0.95:  # Below 95%
                        logger.warning(f"WARNING Trading success rate: {stats['success_rate']:.1%}")
                
                # Check position manager
                if self.position_manager:
                    position_count = len(await self.position_manager.get_all_positions())
                    if position_count > 5:  # Too many positions
                        logger.warning(f"WARNING High position count: {position_count}")
                
                await asyncio.sleep(self.config.health_check_interval_seconds)
                
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await asyncio.sleep(60)  # Extended interval on error
    
    async def _performance_monitor(self):
        """Performance metrics monitoring"""
        logger.info("Performance monitor started")
        
        while self.is_initialized:
            try:
                # Update performance metrics
                if self.trading_engine:
                    stats = self.trading_engine.get_execution_stats()
                    self.performance_metrics.update({
                        'orders_executed': stats['total_orders'],
                        'successful_trades': stats['successful_executions'],
                        'failed_trades': stats['failed_executions'],
                        'avg_execution_time_ms': stats['avg_execution_time_ms']
                    })
                
                # Calculate uptime
                session_duration = datetime.now(timezone.utc) - self.performance_metrics['session_start']
                uptime_hours = session_duration.total_seconds() / 3600
                self.performance_metrics['uptime_percentage'] = min(100.0, (uptime_hours / 48.0) * 100)
                
                # Log performance every 30 minutes
                if int(time.time()) % 1800 == 0:  # Every 30 minutes
                    logger.info("CHART PERFORMANCE METRICS:")
                    logger.info(f"   Orders Executed: {self.performance_metrics['orders_executed']}")
                    logger.info(f"   Success Rate: {stats.get('success_rate', 0):.1%}")
                    logger.info(f"   Avg Execution: {self.performance_metrics['avg_execution_time_ms']:.1f}ms")
                    logger.info(f"   Uptime: {self.performance_metrics['uptime_percentage']:.1f}%")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Performance monitor error: {e}")
                await asyncio.sleep(60)
    
    async def _position_monitor(self):
        """Position monitoring and risk management"""
        logger.info("Position monitor started")
        
        while self.is_initialized and self.trading_active:
            try:
                if self.position_manager:
                    positions = await self.position_manager.get_all_positions()
                    
                    total_exposure = 0.0
                    losing_positions = 0
                    
                    for position in positions:
                        total_exposure += abs(position['volume'])
                        if position['profit'] < 0:
                            losing_positions += 1
                    
                    # Risk management checks
                    if total_exposure > self.config.max_position_size * 5:
                        logger.warning(f"WARNING High total exposure: {total_exposure}")
                    
                    if losing_positions > 3:
                        logger.warning(f"WARNING Multiple losing positions: {losing_positions}")
                
                await asyncio.sleep(self.config.position_monitor_interval_seconds)
                
            except Exception as e:
                logger.error(f"Position monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _trading_session_monitor(self):
        """Monitor 48-hour trading session"""
        logger.info("Trading session monitor started")
        
        session_start = datetime.now(timezone.utc)
        session_end = session_start + timedelta(hours=48)
        
        while self.trading_active and datetime.now(timezone.utc) < session_end:
            try:
                # Check if session should continue
                remaining_time = session_end - datetime.now(timezone.utc)
                
                # Log session progress every hour
                if int(time.time()) % 3600 == 0:  # Every hour
                    hours_remaining = remaining_time.total_seconds() / 3600
                    logger.info(f" Trading session: {hours_remaining:.1f} hours remaining")
                
                # Emergency stop conditions
                account_info = await self.mt5_connector.get_account_info()
                if account_info:
                    equity = account_info['equity']
                    balance = account_info['balance']
                    drawdown = (balance - equity) / balance if balance > 0 else 0
                    
                    if drawdown > self.config.emergency_stop_loss_percent:
                        await self.stop_trading(f"Emergency stop: {drawdown:.1%} drawdown")
                        break
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Session monitor error: {e}")
                await asyncio.sleep(60)
        
        # Session completed
        if datetime.now(timezone.utc) >= session_end:
            await self.stop_trading("48-hour session completed")
    
    async def _log_configuration_summary(self):
        """Log comprehensive configuration summary"""
        logger.info(" CONFIGURATION SUMMARY:")
        logger.info(f"   Demo Account: {self.config.account_number}")
        logger.info(f"   Server: {self.config.server}")
        logger.info(f"   Risk per Trade: {self.config.max_risk_per_trade * 100}%")
        logger.info(f"   Daily Risk Limit: {self.config.max_daily_risk * 100}%")
        logger.info(f"   Max Position Size: {self.config.max_position_size} lots")
        logger.info(f"   Stop Loss: {self.config.stop_loss_pips} pips")
        logger.info(f"   Take Profit: {self.config.take_profit_pips} pips")
        logger.info(f"   Primary Symbols: {', '.join(self.config.primary_symbols)}")
        logger.info(f"   Weekend Trading: {self.config.weekend_trading_enabled}")
        logger.info(f"   Target Latency: <{self.config.target_execution_latency_ms}ms")
        logger.info(f"   Target Success Rate: {self.config.target_success_rate * 100}%")
    
    async def _generate_trading_report(self):
        """Generate comprehensive trading session report"""
        try:
            logger.info("CHART GENERATING FINAL TRADING REPORT...")
            
            # Get final account info
            account_info = await self.mt5_connector.get_account_info()
            
            # Get trading engine stats
            engine_stats = self.trading_engine.get_execution_stats() if self.trading_engine else {}
            
            # Calculate session duration
            session_duration = datetime.now(timezone.utc) - self.performance_metrics['session_start']
            
            report = f"""
ROCKET MT5 CRYPTO DEMO TRADING REPORT ROCKET
{'='*50}

SESSION INFO:
  Demo Account: {self.config.account_number}
  Duration: {session_duration}
  Start Time: {self.performance_metrics['session_start']}
  End Time: {datetime.now(timezone.utc)}

ACCOUNT PERFORMANCE:
  Final Balance: {account_info.get('balance', 'N/A')} {account_info.get('currency', '')}
  Final Equity: {account_info.get('equity', 'N/A')} {account_info.get('currency', '')}
  Total P&L: {account_info.get('profit', 'N/A')} {account_info.get('currency', '')}

EXECUTION METRICS:
  Total Orders: {engine_stats.get('total_orders', 0)}
  Successful: {engine_stats.get('successful_executions', 0)}
  Failed: {engine_stats.get('failed_executions', 0)}
  Success Rate: {engine_stats.get('success_rate', 0):.1%}
  Avg Execution Time: {engine_stats.get('avg_execution_time_ms', 0):.1f}ms
  Max Execution Time: {engine_stats.get('max_execution_time_ms', 0):.1f}ms

SYSTEM PERFORMANCE:
  Uptime: {self.performance_metrics['uptime_percentage']:.1f}%
  Circuit Breaker Triggered: {engine_stats.get('circuit_breaker_open', False)}

RISK MANAGEMENT:
  Max Risk per Trade: {self.config.max_risk_per_trade * 100}%
  Daily Risk Limit: {self.config.max_daily_risk * 100}%
  Emergency Stop Triggered: {'Yes' if not self.trading_active else 'No'}

{'='*50}
DEMO TEST STATUS: {'COMPLETED' if session_duration.total_seconds() >= 48*3600 else 'TERMINATED'}
"""
            
            logger.info(report)
            
            # Save report to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"crypto_demo_report_{timestamp}.txt", "w") as f:
                f.write(report)
            
            logger.info("OK Trading report generated successfully")
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")


async def main():
    """Main execution function for immediate deployment"""
    print("ROCKET MT5 Crypto Demo Trading Environment")
    print("=" * 50)
    print("48-Hour Live Trading Test Setup")
    print("Account: 107034605 (Demo)")
    print("Target: Weekend crypto trading validation")
    print("=" * 50)
    
    # Get demo account password
    password = input("Enter demo account password: ").strip()
    if not password:
        print("ERROR Password required for demo account")
        return
    
    # Initialize configuration
    config = CryptoTradingConfig()
    
    # Create trading environment
    trading_env = MT5CryptoDemoEnvironment(config)
    
    # Initialize environment
    print("\nTOOL Initializing trading environment...")
    if not await trading_env.initialize(password):
        print("ERROR Environment initialization failed")
        return
    
    print("\nOK Environment ready for live trading")
    
    # Confirm trading start
    confirm = input("\nROCKET Start 48-hour live crypto trading? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Trading cancelled by user")
        return
    
    # Start trading
    if await trading_env.start_trading():
        print("\nOK 48-hour crypto trading test STARTED")
        print("Monitor logs for real-time updates...")
        
        try:
            # Keep running until trading stops
            while trading_env.trading_active:
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            print("\n Manual stop requested")
            await trading_env.stop_trading("User interrupt")
    else:
        print("ERROR Failed to start trading")


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    # Execute for immediate weekend deployment
    asyncio.run(main())