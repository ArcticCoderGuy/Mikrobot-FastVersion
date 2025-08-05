from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Signal-Based Trading System
Production-ready solution for MT5 connection conflicts
Enables concurrent Python bot + terminal/mobile monitoring
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from pathlib import Path

from src.core.connectors.signal_based_mt5_connector import (
    SignalBasedMT5Connector, TradingSignal, ExecutionResponse
)

logger = logging.getLogger(__name__)


class ConflictFreeTradingSystem:
    """
    Production trading system that resolves MT5 connection conflicts
    Allows simultaneous:
    - Python bot trading
    - Windows MT5 terminal monitoring  
    - iPhone MT5 mobile app monitoring
    """
    
    def __init__(self, 
                 account_number: int = 107034605,
                 server: str = "Ava-Demo 1-MT5",
                 magic_number: int = 999888):
        
        self.account_number = account_number
        self.server = server
        self.magic_number = magic_number
        
        # Initialize signal-based connector
        self.connector = SignalBasedMT5Connector(
            ea_name="MikrobotEA",
            timeout_seconds=30
        )
        
        # Trading state
        self.is_active = False
        self.active_positions = {}
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0.0,
            'avg_execution_time_ms': 0.0
        }
        
        logger.info(f"Conflict-free trading system initialized for account {account_number}")
    
    async def start(self) -> bool:
        """
        Start the conflict-free trading system
        This does NOT interfere with existing MT5 connections
        """
        try:
            logger.info("ROCKET Starting conflict-free trading system...")
            
            # Connect via signals (no connection conflict)
            if not await self.connector.connect():
                logger.error("ERROR Failed to establish signal-based connection")
                return False
            
            # Verify EA is responding
            account_info = await self.connector.get_account_info()
            if not account_info:
                logger.error("ERROR EA not responding to status requests")
                return False
            
            logger.info(f"OK Connected to account {account_info.get('login')}")
            logger.info(f"OK Balance: {account_info.get('balance', 0):.2f}")
            logger.info(f"OK Equity: {account_info.get('equity', 0):.2f}")
            
            # Load existing positions
            await self._sync_positions()
            
            self.is_active = True
            logger.info("TARGET Trading system is now active and conflict-free!")
            
            return True
            
        except Exception as e:
            logger.error(f"Startup error: {str(e)}")
            return False
    
    async def stop(self):
        """Stop trading system gracefully"""
        try:
            logger.info(" Stopping trading system...")
            
            self.is_active = False
            
            # Disconnect from EA
            await self.connector.disconnect()
            
            # Log final metrics
            metrics = self.get_performance_metrics()
            logger.info(f"CHART Final Performance:")
            logger.info(f"   Total Trades: {metrics['total_trades']}")
            logger.info(f"   Win Rate: {metrics['win_rate']:.1%}")
            logger.info(f"   Total Profit: {metrics['total_profit']:.2f}")
            
            logger.info("OK Trading system stopped")
            
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")
    
    async def place_buy_order(self, 
                             symbol: str, 
                             volume: float, 
                             sl: Optional[float] = None,
                             tp: Optional[float] = None,
                             comment: str = "Mikrobot Buy") -> Dict[str, Any]:
        """
        Place buy order via signal-based system
        User can monitor in real-time on terminal/mobile
        """
        if not self.is_active:
            return {'success': False, 'error': 'Trading system not active'}
        
        try:
            order_params = {
                'symbol': symbol,
                'action': 'BUY',
                'volume': volume,
                'sl': sl,
                'tp': tp,
                'comment': comment,
                'magic': self.magic_number
            }
            
            logger.info(f"GRAPH_UP Placing BUY order: {symbol} {volume} lots")
            
            result = await self.connector.place_order(order_params)
            
            if result['success']:
                # Track position
                self.active_positions[result['ticket']] = {
                    'symbol': symbol,
                    'type': 'BUY',
                    'volume': volume,
                    'open_price': result['execution_price'],
                    'open_time': datetime.now(),
                    'sl': sl,
                    'tp': tp
                }
                
                self.performance_metrics['total_trades'] += 1
                
                logger.info(f"OK BUY order executed: Ticket #{result['ticket']}")
                logger.info(f"   Price: {result['execution_price']:.5f}")
                logger.info(f"   Execution Time: {result.get('execution_time_ms', 0):.1f}ms")
            else:
                logger.error(f"ERROR BUY order failed: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Buy order error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def place_sell_order(self, 
                              symbol: str, 
                              volume: float, 
                              sl: Optional[float] = None,
                              tp: Optional[float] = None,
                              comment: str = "Mikrobot Sell") -> Dict[str, Any]:
        """
        Place sell order via signal-based system
        User can monitor in real-time on terminal/mobile
        """
        if not self.is_active:
            return {'success': False, 'error': 'Trading system not active'}
        
        try:
            order_params = {
                'symbol': symbol,
                'action': 'SELL',
                'volume': volume,
                'sl': sl,
                'tp': tp,
                'comment': comment,
                'magic': self.magic_number
            }
            
            logger.info(f" Placing SELL order: {symbol} {volume} lots")
            
            result = await self.connector.place_order(order_params)
            
            if result['success']:
                # Track position
                self.active_positions[result['ticket']] = {
                    'symbol': symbol,
                    'type': 'SELL',
                    'volume': volume,
                    'open_price': result['execution_price'],
                    'open_time': datetime.now(),
                    'sl': sl,
                    'tp': tp
                }
                
                self.performance_metrics['total_trades'] += 1
                
                logger.info(f"OK SELL order executed: Ticket #{result['ticket']}")
                logger.info(f"   Price: {result['execution_price']:.5f}")
                logger.info(f"   Execution Time: {result.get('execution_time_ms', 0):.1f}ms")
            else:
                logger.error(f"ERROR SELL order failed: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Sell order error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def close_position(self, ticket: int) -> Dict[str, Any]:
        """
        Close position via signal-based system
        User sees closure in real-time on terminal/mobile
        """
        if not self.is_active:
            return {'success': False, 'error': 'Trading system not active'}
        
        try:
            logger.info(f" Closing position: #{ticket}")
            
            result = await self.connector.close_position(ticket)
            
            if result['success']:
                # Update tracking
                if ticket in self.active_positions:
                    position = self.active_positions[ticket]
                    
                    # Calculate profit (simplified)
                    open_price = position['open_price']
                    close_price = result['close_price']
                    volume = position['volume']
                    
                    if position['type'] == 'BUY':
                        profit = (close_price - open_price) * volume * 100000  # Simplified
                    else:
                        profit = (open_price - close_price) * volume * 100000
                    
                    self.performance_metrics['total_profit'] += profit
                    
                    if profit > 0:
                        self.performance_metrics['winning_trades'] += 1
                    else:
                        self.performance_metrics['losing_trades'] += 1
                    
                    # Remove from active positions
                    del self.active_positions[ticket]
                
                logger.info(f"OK Position closed: #{ticket}")
                logger.info(f"   Close Price: {result['close_price']:.5f}")
            else:
                logger.error(f"ERROR Close failed: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Close position error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions (visible on terminal/mobile too)"""
        try:
            positions = await self.connector.get_positions()
            
            # Filter by magic number
            mikrobot_positions = [
                pos for pos in positions 
                if pos.get('magic') == self.magic_number
            ]
            
            return mikrobot_positions
            
        except Exception as e:
            logger.error(f"Get positions error: {str(e)}")
            return []
    
    async def get_account_status(self) -> Optional[Dict[str, Any]]:
        """Get current account status"""
        try:
            return await self.connector.get_account_info()
        except Exception as e:
            logger.error(f"Get account status error: {str(e)}")
            return None
    
    async def _sync_positions(self):
        """Sync positions with EA state"""
        try:
            positions = await self.get_positions()
            
            self.active_positions = {}
            for pos in positions:
                self.active_positions[pos['ticket']] = {
                    'symbol': pos['symbol'],
                    'type': pos['type'],
                    'volume': pos['volume'],
                    'open_price': pos['price_open'],
                    'open_time': pos.get('time', datetime.now()),
                    'sl': pos.get('sl', 0),
                    'tp': pos.get('tp', 0)
                }
            
            logger.info(f"CHART Synced {len(self.active_positions)} active positions")
            
        except Exception as e:
            logger.error(f"Position sync error: {str(e)}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get trading performance metrics"""
        total_trades = self.performance_metrics['total_trades']
        winning_trades = self.performance_metrics['winning_trades']
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Get connector metrics
        connector_metrics = self.connector.get_metrics()
        
        return {
            **self.performance_metrics,
            'win_rate': win_rate,
            'active_positions': len(self.active_positions),
            'connector_metrics': connector_metrics,
            'is_active': self.is_active
        }
    
    async def run_trading_loop(self, trading_strategy_func):
        """
        Run main trading loop with custom strategy
        Strategy function should accept (system) and return trading decisions
        """
        logger.info(" Starting trading loop...")
        
        try:
            while self.is_active:
                # Execute trading strategy
                if callable(trading_strategy_func):
                    try:
                        await trading_strategy_func(self)
                    except Exception as e:
                        logger.error(f"Strategy error: {str(e)}")
                
                # Health check
                if not await self.connector.ensure_connected():
                    logger.warning("WARNING Connection lost, attempting recovery...")
                    continue
                
                # Brief pause
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Trading loop error: {str(e)}")
        
        logger.info(" Trading loop stopped")


# Example usage and testing
async def demo_trading_strategy(trading_system: ConflictFreeTradingSystem):
    """
    Demo trading strategy for testing
    This runs while user monitors on terminal/mobile
    """
    
    # Get account status
    account = await trading_system.get_account_status()
    if not account:
        return
    
    # Simple demo strategy - place small test orders
    positions = await trading_system.get_positions()
    
    if len(positions) < 2:  # Limit to 2 demo positions
        # Demo buy order
        result = await trading_system.place_buy_order(
            symbol="EURUSD",
            volume=0.01,
            sl=None,
            tp=None,
            comment="Demo signal test"
        )
        
        if result['success']:
            logger.info(f"OK Demo order placed - user can see in terminal/mobile")
    
    # Demo close after 30 seconds (for testing)
    for ticket, position in trading_system.active_positions.items():
        open_time = position['open_time']
        if isinstance(open_time, str):
            continue
            
        if (datetime.now() - open_time).seconds > 30:
            await trading_system.close_position(ticket)
            logger.info(f"OK Demo position closed - user saw it in terminal/mobile")


async def main():
    """
    Main function demonstrating conflict-free trading
    """
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("ROCKET Starting Mikrobot Conflict-Free Trading System")
    logger.info(" User can monitor in real-time on:")
    logger.info("   - Windows MT5 Terminal")
    logger.info("   - iPhone MT5 Mobile App")
    logger.info("   - No connection conflicts!")
    
    # Initialize trading system
    trading_system = ConflictFreeTradingSystem(
        account_number=107034605,
        server="Ava-Demo 1-MT5"
    )
    
    try:
        # Start system (no connection conflicts)
        if await trading_system.start():
            logger.info("OK Trading system started successfully")
            
            # Run demo strategy
            await trading_system.run_trading_loop(demo_trading_strategy)
        else:
            logger.error("ERROR Failed to start trading system")
    
    except KeyboardInterrupt:
        logger.info(" Shutting down...")
    
    finally:
        await trading_system.stop()


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(main())