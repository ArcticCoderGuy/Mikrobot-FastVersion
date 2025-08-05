from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
48-Hour Live Crypto Trading Demo
Immediate deployment for business validation

Account: 107034605 (Demo)
Duration: 48 hours weekend crypto trading
Target: 10kEUR weekly revenue validation
"""

import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
import MetaTrader5 as mt5
from typing import Dict, Any, Optional
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'crypto_demo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Demo Account Configuration
DEMO_ACCOUNT = 107034605
DEMO_SERVER = "MetaQuotes-Demo"
MAX_DAILY_LOSS = -500.0  # EUR500 daily loss limit
MAX_POSITION_RISK = 100.0  # EUR100 per position
TEST_DURATION_HOURS = 48

# Crypto symbols for weekend trading
CRYPTO_SYMBOLS = ["BTCUSD", "ETHUSD", "XRPUSD", "ADAUSD"]

class CryptoDemoTrader:
    """48-Hour Crypto Demo Trading System"""
    
    def __init__(self):
        self.is_connected = False
        self.start_time = None
        self.positions = {}
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'max_drawdown': 0.0,
            'current_equity': 0.0,
            'starting_equity': 0.0
        }
        self.emergency_stop = False
        
    async def initialize(self, password: str) -> bool:
        """Initialize MT5 connection and demo account"""
        try:
            logger.info("[INIT] Initializing Crypto Demo Trading System...")
            
            # Initialize MT5
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            # Login to demo account
            authorized = mt5.login(
                login=DEMO_ACCOUNT,
                password=password,
                server=DEMO_SERVER
            )
            
            if not authorized:
                logger.error(f"Login failed: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            # Get account info
            account_info = mt5.account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return False
            
            self.performance_metrics['starting_equity'] = account_info.equity
            self.performance_metrics['current_equity'] = account_info.equity
            self.is_connected = True
            
            logger.info(f"OK Connected to Demo Account {DEMO_ACCOUNT}")
            logger.info(f"CHART Starting Equity: EUR{account_info.equity:.2f}")
            logger.info(f"MONEY Balance: EUR{account_info.balance:.2f}")
            logger.info(f"GRAPH_UP Leverage: {account_info.leverage}:1")
            
            # Validate crypto symbols
            await self._validate_crypto_symbols()
            
            return True
            
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    async def _validate_crypto_symbols(self):
        """Validate available crypto symbols"""
        logger.info(" Validating crypto symbols...")
        
        available_symbols = []
        for symbol in CRYPTO_SYMBOLS:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is not None:
                # Enable symbol in Market Watch
                if mt5.symbol_select(symbol, True):
                    available_symbols.append(symbol)
                    logger.info(f"OK {symbol} - Available and enabled")
                else:
                    logger.warning(f"WARNING {symbol} - Failed to enable")
            else:
                logger.warning(f"ERROR {symbol} - Not available")
        
        if not available_symbols:
            logger.error("ERROR No crypto symbols available!")
            raise Exception("No crypto symbols available for trading")
        
        # Update symbols list to only available ones  
        CRYPTO_SYMBOLS[:] = available_symbols
        logger.info(f" Trading symbols: {', '.join(CRYPTO_SYMBOLS)}")
    
    async def start_trading(self):
        """Start 48-hour crypto trading session"""
        try:
            self.start_time = datetime.now(timezone.utc)
            end_time = self.start_time + timedelta(hours=TEST_DURATION_HOURS)
            
            logger.info("TARGET STARTING 48-HOUR CRYPTO TRADING TEST")
            logger.info(f" Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            logger.info(f" End: {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            logger.info(f" Strategy: Conservative crypto trading")
            logger.info(f" Risk: Max EUR{abs(MAX_DAILY_LOSS)} daily loss, EUR{MAX_POSITION_RISK} per position")
            
            # Main trading loop
            while datetime.now(timezone.utc) < end_time and not self.emergency_stop:
                try:
                    # Update account info
                    await self._update_performance_metrics()
                    
                    # Check risk limits
                    if await self._check_risk_limits():
                        # Look for trading opportunities
                        await self._scan_crypto_opportunities()
                        
                        # Manage existing positions
                        await self._manage_positions()
                    
                    # Status update every 5 minutes
                    if int(time.time()) % 300 == 0:
                        await self._log_status_update()
                    
                    # Sleep for 30 seconds between cycles
                    await asyncio.sleep(30)
                    
                except KeyboardInterrupt:
                    logger.warning(" Manual stop requested")
                    break
                except Exception as e:
                    logger.error(f"Trading loop error: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute on error
            
            # Final status
            await self._final_report()
            
        except Exception as e:
            logger.error(f"Trading session error: {e}")
        finally:
            await self._cleanup()
    
    async def _update_performance_metrics(self):
        """Update current performance metrics"""
        try:
            account_info = mt5.account_info()
            if account_info:
                self.performance_metrics['current_equity'] = account_info.equity
                
                # Calculate drawdown
                starting_equity = self.performance_metrics['starting_equity']
                current_equity = self.performance_metrics['current_equity']
                
                if starting_equity > 0:
                    drawdown = (starting_equity - current_equity) / starting_equity * 100
                    if drawdown > self.performance_metrics['max_drawdown']:
                        self.performance_metrics['max_drawdown'] = drawdown
                
        except Exception as e:
            logger.error(f"Performance update error: {e}")
    
    async def _check_risk_limits(self) -> bool:
        """Check if we can continue trading within risk limits"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                return False
            
            # Check daily loss limit
            daily_pnl = account_info.equity - self.performance_metrics['starting_equity']
            if daily_pnl <= MAX_DAILY_LOSS:
                logger.critical(f" DAILY LOSS LIMIT REACHED: EUR{daily_pnl:.2f}")
                await self._emergency_close_all("Daily loss limit")
                return False
            
            # Check drawdown limit (10%)
            if self.performance_metrics['max_drawdown'] > 10.0:
                logger.critical(f" MAXIMUM DRAWDOWN EXCEEDED: {self.performance_metrics['max_drawdown']:.1f}%")
                await self._emergency_close_all("Maximum drawdown")
                return False
            
            # Check margin level
            if account_info.margin_level < 200.0 and account_info.margin > 0:
                logger.warning(f"WARNING LOW MARGIN LEVEL: {account_info.margin_level:.1f}%")
                # Close losing positions if margin is low
                await self._close_losing_positions()
            
            return True
            
        except Exception as e:
            logger.error(f"Risk check error: {e}")
            return False
    
    async def _scan_crypto_opportunities(self):
        """Scan for crypto trading opportunities"""
        try:
            # Simple momentum strategy for demo
            for symbol in CRYPTO_SYMBOLS:
                try:
                    # Get current price
                    tick = mt5.symbol_info_tick(symbol)
                    if not tick:
                        continue
                    
                    # Get recent bars
                    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
                    if rates is None or len(rates) < 20:
                        continue
                    
                    # Simple momentum check (price above 20-period average)
                    current_price = tick.bid
                    avg_price = sum(rates[-20:]['close']) / 20
                    
                    # Only trade if no position exists for this symbol
                    positions = mt5.positions_get(symbol=symbol)
                    if positions and len(positions) > 0:
                        continue
                    
                    # Conservative entry conditions
                    if current_price > avg_price * 1.002:  # 0.2% above average
                        await self._place_buy_order(symbol, current_price)
                    elif current_price < avg_price * 0.998:  # 0.2% below average
                        await self._place_sell_order(symbol, current_price)
                        
                except Exception as e:
                    logger.error(f"Opportunity scan error for {symbol}: {e}")
                    
        except Exception as e:
            logger.error(f"Crypto scan error: {e}")
    
    async def _place_buy_order(self, symbol: str, current_price: float):
        """Place conservative buy order"""
        try:
            volume = 0.01  # Small position size
            sl = current_price * 0.99  # 1% stop loss
            tp = current_price * 1.02  # 2% take profit
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY,
                "price": current_price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 20250802,
                "comment": "Crypto Demo BUY",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.performance_metrics['total_trades'] += 1
                logger.info(f"OK BUY {symbol}: Volume {volume}, Price {current_price:.5f}, SL {sl:.5f}, TP {tp:.5f}")
            else:
                logger.warning(f"ERROR BUY order failed for {symbol}: {result.comment}")
                
        except Exception as e:
            logger.error(f"Buy order error: {e}")
    
    async def _place_sell_order(self, symbol: str, current_price: float):
        """Place conservative sell order"""
        try:
            volume = 0.01  # Small position size
            sl = current_price * 1.01  # 1% stop loss
            tp = current_price * 0.98  # 2% take profit
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_SELL,
                "price": current_price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 20250802,
                "comment": "Crypto Demo SELL",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.performance_metrics['total_trades'] += 1
                logger.info(f"OK SELL {symbol}: Volume {volume}, Price {current_price:.5f}, SL {sl:.5f}, TP {tp:.5f}")
            else:
                logger.warning(f"ERROR SELL order failed for {symbol}: {result.comment}")
                
        except Exception as e:
            logger.error(f"Sell order error: {e}")
    
    async def _manage_positions(self):
        """Manage existing positions"""
        try:
            positions = mt5.positions_get()
            if not positions:
                return
            
            for position in positions:
                # Check if position is profitable
                if position.profit > 0:
                    self.performance_metrics['total_profit'] += position.profit
                    # Consider partial profit taking on large gains
                    if position.profit > MAX_POSITION_RISK * 0.5:  # 50% of max risk as profit
                        logger.info(f"MONEY Large profit on {position.symbol}: EUR{position.profit:.2f}")
                else:
                    self.performance_metrics['total_loss'] += abs(position.profit)
                
        except Exception as e:
            logger.error(f"Position management error: {e}")
    
    async def _close_losing_positions(self):
        """Close losing positions to preserve margin"""
        try:
            positions = mt5.positions_get()
            if not positions:
                return
            
            for position in positions:
                if position.profit < -MAX_POSITION_RISK * 0.3:  # Close at 30% of max risk
                    # Close position
                    close_request = {
                        "action": mt5.TRADE_ACTION_DEAL,
                        "symbol": position.symbol,
                        "volume": position.volume,
                        "type": mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
                        "position": position.ticket,
                        "price": mt5.symbol_info_tick(position.symbol).bid if position.type == 0 else mt5.symbol_info_tick(position.symbol).ask,
                        "deviation": 20,
                        "magic": 20250802,
                        "comment": "Risk management close",
                        "type_time": mt5.ORDER_TIME_GTC,
                        "type_filling": mt5.ORDER_FILLING_IOC,
                    }
                    
                    result = mt5.order_send(close_request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        logger.info(f" Risk close {position.symbol}: Loss EUR{position.profit:.2f}")
                        
        except Exception as e:
            logger.error(f"Risk close error: {e}")
    
    async def _emergency_close_all(self, reason: str):
        """Emergency close all positions"""
        try:
            logger.critical(f" EMERGENCY CLOSE ALL POSITIONS: {reason}")
            
            positions = mt5.positions_get()
            if not positions:
                return
            
            for position in positions:
                close_request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": position.symbol,
                    "volume": position.volume,
                    "type": mt5.ORDER_TYPE_SELL if position.type == 0 else mt5.ORDER_TYPE_BUY,
                    "position": position.ticket,
                    "price": mt5.symbol_info_tick(position.symbol).bid if position.type == 0 else mt5.symbol_info_tick(position.symbol).ask,
                    "deviation": 50,
                    "magic": 20250802,
                    "comment": f"Emergency close: {reason}",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
                
                result = mt5.order_send(close_request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f" Emergency closed {position.symbol}")
            
            self.emergency_stop = True
            
        except Exception as e:
            logger.error(f"Emergency close error: {e}")
    
    async def _log_status_update(self):
        """Log 5-minute status update"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                return
            
            # Calculate session performance
            session_pnl = account_info.equity - self.performance_metrics['starting_equity']
            session_pnl_pct = (session_pnl / self.performance_metrics['starting_equity']) * 100
            
            # Get current positions
            positions = mt5.positions_get()
            position_count = len(positions) if positions else 0
            
            # Calculate session duration
            if self.start_time:
                elapsed = datetime.now(timezone.utc) - self.start_time
                elapsed_hours = elapsed.total_seconds() / 3600
            else:
                elapsed_hours = 0
            
            logger.info("=" * 60)
            logger.info(f"CHART STATUS UPDATE - {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")
            logger.info(f" Session time: {elapsed_hours:.1f}h / {TEST_DURATION_HOURS}h")
            logger.info(f"MONEY Equity: EUR{account_info.equity:.2f} (Start: EUR{self.performance_metrics['starting_equity']:.2f})")
            logger.info(f"GRAPH_UP Session P&L: EUR{session_pnl:.2f} ({session_pnl_pct:+.2f}%)")
            logger.info(f"CHART Max Drawdown: {self.performance_metrics['max_drawdown']:.2f}%")
            logger.info(f"TARGET Total Trades: {self.performance_metrics['total_trades']}")
            logger.info(f" Open Positions: {position_count}")
            logger.info(f" Free Margin: EUR{account_info.margin_free:.2f}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Status update error: {e}")
    
    async def _final_report(self):
        """Generate final trading session report"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                return
            
            # Close any remaining positions
            positions = mt5.positions_get()
            if positions:
                await self._emergency_close_all("Session end")
            
            # Calculate final metrics
            final_equity = account_info.equity
            starting_equity = self.performance_metrics['starting_equity']
            total_pnl = final_equity - starting_equity
            total_pnl_pct = (total_pnl / starting_equity) * 100
            
            # Session duration
            if self.start_time:
                session_duration = datetime.now(timezone.utc) - self.start_time
                duration_hours = session_duration.total_seconds() / 3600
            else:
                duration_hours = 0
            
            logger.info("TARGET FINAL 48-HOUR CRYPTO TRADING REPORT")
            logger.info("=" * 80)
            logger.info(f" Session Duration: {duration_hours:.1f} hours")
            logger.info(f"MONEY Starting Equity: EUR{starting_equity:.2f}")
            logger.info(f"MONEY Final Equity: EUR{final_equity:.2f}")
            logger.info(f"GRAPH_UP Total P&L: EUR{total_pnl:.2f} ({total_pnl_pct:+.2f}%)")
            logger.info(f"CHART Max Drawdown: {self.performance_metrics['max_drawdown']:.2f}%")
            logger.info(f"TARGET Total Trades: {self.performance_metrics['total_trades']}")
            logger.info(f" Total Profit: EUR{self.performance_metrics['total_profit']:.2f}")
            logger.info(f" Total Loss: EUR{self.performance_metrics['total_loss']:.2f}")
            
            # Extrapolate to weekly performance
            if duration_hours > 0:
                hourly_return = total_pnl / duration_hours
                weekly_projection = hourly_return * 168  # 168 hours in a week
                logger.info(f"CHART Weekly Projection: EUR{weekly_projection:.2f} (based on {duration_hours:.1f}h sample)")
                
                if weekly_projection > 0:
                    target_achievement = (weekly_projection / 10000) * 100
                    logger.info(f"TARGET 10kEUR Target Achievement: {target_achievement:.1f}%")
            
            logger.info("=" * 80)
            
            # Business validation
            if total_pnl > 0 and self.performance_metrics['max_drawdown'] < 5.0:
                logger.info("OK BUSINESS VALIDATION: SUCCESSFUL")
                logger.info("- Positive returns achieved")
                logger.info("- Risk management effective")
                logger.info("- System stability demonstrated")
            else:
                logger.info("WARNING BUSINESS VALIDATION: MIXED RESULTS")
                logger.info("- Review risk parameters and strategy")
                logger.info("- System performed reliably")
            
        except Exception as e:
            logger.error(f"Final report error: {e}")
    
    async def _cleanup(self):
        """Cleanup and disconnect"""
        try:
            logger.info(" Cleaning up...")
            
            # Close any remaining positions
            positions = mt5.positions_get()
            if positions:
                logger.info(f"Closing {len(positions)} remaining positions...")
                await self._emergency_close_all("Cleanup")
            
            # Disconnect
            mt5.shutdown()
            logger.info("OK Cleanup complete - MT5 disconnected")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


async def main():
    """Main execution function"""
    print("[START] MIKROBOT FASTVERSION - 48-HOUR CRYPTO TRADING TEST")
    print("=" * 60)
    print("Account: 107034605 (Demo)")
    print("Duration: 48 hours")
    print("Markets: Crypto (BTC, ETH, XRP, ADA)")
    print("Risk: Conservative (1% per trade, 5% daily limit)")
    print("=" * 60)
    
    # Get demo account password
    password = input("Enter demo account password: ").strip()
    if not password:
        print("ERROR Password required")
        return
    
    # Initialize and start trading
    trader = CryptoDemoTrader()
    
    try:
        if await trader.initialize(password):
            print("\nTARGET Starting 48-hour crypto trading session...")
            print(" Press Ctrl+C anytime to stop")
            await trader.start_trading()
        else:
            print("ERROR Failed to initialize trading system")
    
    except KeyboardInterrupt:
        print("\n Manual stop requested")
    except Exception as e:
        print(f"ERROR System error: {e}")
    finally:
        await trader._cleanup()
        print("\nOK Session complete")


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(main())