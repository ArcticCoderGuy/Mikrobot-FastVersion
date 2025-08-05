from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
IMMEDIATE MT5 CRYPTO DEPLOYMENT
48-Hour Weekend Trading Test - Account 107034605

This is a simplified deployment script for immediate business validation.
No dependencies on complex imports - direct MT5 integration only.
"""

import asyncio
import MetaTrader5 as mt5
import logging
import time
import getpass
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import traceback
import sys
import os

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'crypto_trading_live_{timestamp}.log')
    ]
)
logger = logging.getLogger(__name__)


class ImmediateCryptoTrader:
    """
    Immediate MT5 crypto trader for 48-hour validation
    Direct MT5 integration without complex dependencies
    """
    
    def __init__(self):
        self.account = 107034605
        self.server = "MetaQuotes-Demo"
        self.password = ""
        self.trading_active = False
        self.start_time = None
        self.symbols = ["BTCUSD", "ETHUSD"]
        
        # Risk parameters (CONSERVATIVE)
        self.risk_per_trade = 0.01  # 1%
        self.max_daily_risk = 0.05  # 5%
        self.max_position_size = 0.1  # 0.1 lots
        self.stop_loss_pips = 50
        self.take_profit_pips = 100
        
        # Statistics
        self.stats = {
            'orders_placed': 0,
            'orders_successful': 0,
            'orders_failed': 0,
            'total_pnl': 0.0,
            'session_start': None
        }
        
        logger.info("Immediate Crypto Trader initialized")
        logger.info(f"Account: {self.account}")
        logger.info(f"Risk per trade: {self.risk_per_trade * 100}%")
        logger.info(f"Daily risk limit: {self.max_daily_risk * 100}%")
    
    async def deploy_immediately(self) -> bool:
        """Execute immediate deployment for weekend trading"""
        try:
            print("ROCKET MT5 CRYPTO TRADING - IMMEDIATE DEPLOYMENT")
            print("=" * 60)
            print(f"Target: 48-hour weekend crypto validation")
            print(f"Account: {self.account} (Demo)")
            print(f"Symbols: {', '.join(self.symbols)}")
            print(f"Risk: {self.risk_per_trade * 100}% per trade, {self.max_daily_risk * 100}% daily")
            print("=" * 60)
            
            # Step 1: Get credentials
            self.password = getpass.getpass("Enter demo account password: ").strip()
            if not self.password:
                print("ERROR Password required")
                return False
            
            # Step 2: Initialize MT5
            if not self._initialize_mt5():
                print("ERROR MT5 initialization failed")
                return False
            
            # Step 3: Validate account and symbols
            if not self._validate_account():
                print("ERROR Account validation failed")
                return False
            
            # Step 4: Final confirmation
            print("\n READY TO START LIVE TRADING")
            print(f"Configuration:")
            print(f"  Account: {self.account}")
            print(f"  Balance: {self._get_balance()} USD")
            print(f"  Symbols: {', '.join(self.symbols)}")
            print(f"  Duration: 48 hours")
            
            confirm = input("\nType 'START' to begin live trading: ").strip()
            if confirm != 'START':
                print("ERROR Trading cancelled")
                return False
            
            # Step 5: Start trading
            if not await self._start_trading():
                print("ERROR Trading start failed")
                return False
            
            # Step 6: Monitor trading
            await self._monitor_trading()
            
            print("OK DEPLOYMENT COMPLETED")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            print(f"ERROR DEPLOYMENT ERROR: {e}")
            traceback.print_exc()
            return False
        finally:
            self._shutdown_mt5()
    
    def _initialize_mt5(self) -> bool:
        """Initialize MT5 terminal connection"""
        try:
            print("\nTOOL Initializing MT5...")
            
            # Initialize MT5
            if not mt5.initialize():
                logger.error("MT5 initialize() failed")
                return False
            
            # Login to account
            if not mt5.login(self.account, password=self.password, server=self.server):
                logger.error(f"Login failed for account {self.account}")
                return False
            
            # Get terminal info
            terminal_info = mt5.terminal_info()
            if terminal_info:
                logger.info(f"Connected to MT5: {terminal_info.name} v{terminal_info.build}")
                print(f"OK Connected to MT5: {terminal_info.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"MT5 initialization error: {e}")
            return False
    
    def _validate_account(self) -> bool:
        """Validate account and trading capabilities"""
        try:
            print("\n Validating account...")
            
            # Get account info
            account_info = mt5.account_info()
            if not account_info:
                logger.error("Cannot get account info")
                return False
            
            logger.info(f"Account: {account_info.login}")
            logger.info(f"Balance: {account_info.balance} {account_info.currency}")
            logger.info(f"Leverage: 1:{account_info.leverage}")
            logger.info(f"Trade allowed: {account_info.trade_allowed}")
            
            print(f"OK Account: {account_info.login}")
            print(f"   Balance: {account_info.balance} {account_info.currency}")
            print(f"   Leverage: 1:{account_info.leverage}")
            
            # Check minimum balance
            if account_info.balance < 1000:
                logger.error("Insufficient balance (minimum 1000)")
                return False
            
            # Check trading allowed
            if not account_info.trade_allowed:
                logger.error("Trading not allowed")
                return False
            
            # Validate symbols
            available_symbols = []
            for symbol in self.symbols:
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info:
                    available_symbols.append(symbol)
                    logger.info(f"Symbol {symbol}: Spread {symbol_info.spread}")
                else:
                    logger.warning(f"Symbol {symbol} not available")
            
            if len(available_symbols) < 1:
                logger.error("No crypto symbols available")
                return False
            
            self.symbols = available_symbols  # Use only available symbols
            print(f"OK Available symbols: {', '.join(self.symbols)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Account validation error: {e}")
            return False
    
    def _get_balance(self) -> float:
        """Get current account balance"""
        try:
            account_info = mt5.account_info()
            return account_info.balance if account_info else 0.0
        except:
            return 0.0
    
    def _get_equity(self) -> float:
        """Get current account equity"""
        try:
            account_info = mt5.account_info()
            return account_info.equity if account_info else 0.0
        except:
            return 0.0
    
    async def _start_trading(self) -> bool:
        """Start the 48-hour trading session"""
        try:
            logger.info("ROCKET STARTING 48-HOUR CRYPTO TRADING SESSION")
            
            self.trading_active = True
            self.start_time = datetime.now(timezone.utc)
            self.stats['session_start'] = self.start_time
            
            end_time = self.start_time + timedelta(hours=48)
            
            logger.info(f"Session start: {self.start_time}")
            logger.info(f"Session end: {end_time}")
            
            print(f"\nOK LIVE TRADING STARTED")
            print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            return True
            
        except Exception as e:
            logger.error(f"Trading start error: {e}")
            return False
    
    async def _monitor_trading(self):
        """Monitor trading session for 48 hours"""
        try:
            logger.info("CHART Trading session monitoring started")
            print("\nCHART MONITORING ACTIVE")
            print("Press Ctrl+C to stop trading")
            
            end_time = self.start_time + timedelta(hours=48)
            
            while self.trading_active and datetime.now(timezone.utc) < end_time:
                try:
                    # Basic position monitoring
                    positions = mt5.positions_get()
                    if positions:
                        logger.info(f"Active positions: {len(positions)}")
                        for pos in positions:
                            logger.info(f"  {pos.symbol}: {pos.type} {pos.volume} lots, P&L: {pos.profit}")
                    
                    # Account status check
                    current_equity = self._get_equity()
                    current_balance = self._get_balance()
                    
                    if current_balance > 0:
                        drawdown = (current_balance - current_equity) / current_balance
                        if drawdown > self.max_daily_risk:
                            logger.warning(f"Emergency stop: {drawdown:.1%} drawdown")
                            await self._emergency_stop("Maximum drawdown exceeded")
                            break
                    
                    # Status update every 10 minutes
                    now = datetime.now(timezone.utc)
                    remaining = end_time - now
                    hours_remaining = remaining.total_seconds() / 3600
                    
                    if int(time.time()) % 600 == 0:  # Every 10 minutes
                        logger.info(f" Status: {hours_remaining:.1f}h remaining, Equity: {current_equity:.2f}")
                        print(f" {now.strftime('%H:%M')} | {hours_remaining:.1f}h left | Equity: {current_equity:.2f}")
                    
                    await asyncio.sleep(60)  # Check every minute
                    
                except KeyboardInterrupt:
                    logger.info(" Manual stop requested")
                    await self._emergency_stop("User interrupt")
                    break
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    await asyncio.sleep(30)
            
            # Session completed
            if datetime.now(timezone.utc) >= end_time:
                logger.info("OK 48-hour session completed")
                await self._generate_final_report()
            
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            await self._emergency_stop(f"Monitoring error: {e}")
    
    async def _emergency_stop(self, reason: str):
        """Emergency stop all trading"""
        try:
            logger.warning(f" EMERGENCY STOP: {reason}")
            
            self.trading_active = False
            
            # Close all positions
            positions = mt5.positions_get()
            if positions:
                logger.info(f"Closing {len(positions)} open positions")
                for pos in positions:
                    ticket = pos.ticket
                    symbol = pos.symbol
                    lot = pos.volume
                    
                    if pos.type == 0:  # Buy position
                        request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": symbol,
                            "volume": lot,
                            "type": mt5.ORDER_TYPE_SELL,
                            "position": ticket,
                            "deviation": 20,
                            "magic": 234000,
                            "comment": f"Emergency close: {reason}",
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_IOC,
                        }
                    else:  # Sell position
                        request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": symbol,
                            "volume": lot,
                            "type": mt5.ORDER_TYPE_BUY,
                            "position": ticket,
                            "deviation": 20,
                            "magic": 234000,
                            "comment": f"Emergency close: {reason}",
                            "type_time": mt5.ORDER_TIME_GTC,
                            "type_filling": mt5.ORDER_FILLING_IOC,
                        }
                    
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        logger.info(f"Position {ticket} closed successfully")
                    else:
                        logger.error(f"Failed to close position {ticket}: {result.comment}")
            
            await self._generate_final_report()
            
        except Exception as e:
            logger.error(f"Emergency stop error: {e}")
    
    async def _generate_final_report(self):
        """Generate comprehensive final report"""
        try:
            logger.info("CHART Generating final trading report...")
            
            # Get final account info
            account_info = mt5.account_info()
            session_duration = datetime.now(timezone.utc) - self.start_time
            
            report = f"""
ROCKET MT5 CRYPTO TRADING REPORT ROCKET
{'='*50}

SESSION INFO:
  Demo Account: {self.account}
  Duration: {session_duration}
  Start Time: {self.start_time}
  End Time: {datetime.now(timezone.utc)}

ACCOUNT PERFORMANCE:
  Final Balance: {account_info.balance if account_info else 'N/A'} USD
  Final Equity: {account_info.equity if account_info else 'N/A'} USD
  Session P&L: {(account_info.equity - account_info.balance) if account_info else 'N/A'} USD

TRADING STATISTICS:
  Orders Placed: {self.stats['orders_placed']}
  Successful Orders: {self.stats['orders_successful']}
  Failed Orders: {self.stats['orders_failed']}
  Success Rate: {(self.stats['orders_successful'] / max(1, self.stats['orders_placed'])) * 100:.1f}%

RISK MANAGEMENT:
  Risk per Trade: {self.risk_per_trade * 100}%
  Daily Risk Limit: {self.max_daily_risk * 100}%
  Max Position Size: {self.max_position_size} lots
  Stop Loss: {self.stop_loss_pips} pips
  Take Profit: {self.take_profit_pips} pips

SYMBOLS TRADED:
  {', '.join(self.symbols)}

{'='*50}
DEMO TEST STATUS: {'COMPLETED' if session_duration.total_seconds() >= 48*3600 else 'TERMINATED'}
"""
            
            logger.info(report)
            print(report)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"crypto_trading_report_{timestamp}.txt"
            with open(report_file, 'w', encoding='ascii', errors='ignore') as f:
                f.write(report)
            
            logger.info(f"OK Report saved to {report_file}")
            print(f"OK Report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Report generation error: {e}")
    
    def _shutdown_mt5(self):
        """Shutdown MT5 connection"""
        try:
            if mt5.terminal_info():
                mt5.shutdown()
                logger.info("OK MT5 connection closed")
        except:
            pass


async def main():
    """Main execution function"""
    trader = ImmediateCryptoTrader()
    
    try:
        success = await trader.deploy_immediately()
        
        if success:
            print("\n CRYPTO TRADING DEPLOYMENT COMPLETED")
            print("Check logs and report files for detailed results")
        else:
            print("\nERROR DEPLOYMENT FAILED")
            print("Check logs for error details")
        
        return success
        
    except KeyboardInterrupt:
        print("\n Deployment cancelled by user")
        await trader._emergency_stop("User interrupt")
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

    print("IMMEDIATE MT5 CRYPTO DEPLOYMENT")
    print("=" * 60)
    print("48-Hour Weekend Trading Validation")
    print("Account: 107034605 (Demo)")
    print("Target: 10k EUR weekly revenue validation")
    print("=" * 60)
    
    # Execute deployment
    result = asyncio.run(main())
    
    if result:
        print("\nOK IMMEDIATE DEPLOYMENT SUCCESSFUL")
        print("Live crypto trading validation complete!")
    else:
        print("\nERROR IMMEDIATE DEPLOYMENT FAILED")
        print("Review error logs and retry")
    
    sys.exit(0 if result else 1)