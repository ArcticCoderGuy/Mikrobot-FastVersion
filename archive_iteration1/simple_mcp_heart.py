"""
SIMPLE MCP HEART - WORKING VERSION
Lightweight signal processor that bridges EA v8_Fixed with basic MCP processing
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMCPHeart:
    """
    Simplified heart system that processes EA v8_Fixed signals
    without complex orchestration dependencies
    """
    
    def __init__(self):
        self.signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
        self.response_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_trade_response.json")
        
        self.is_running = False
        self.processed_signals = 0
        
        logger.info("SIMPLE MCP HEART INITIALIZED")
        logger.info(f"Monitoring: {self.signal_file}")
        logger.info(f"Response: {self.response_file}")
    
    async def start_heart(self):
        """Start the simplified heart - main monitoring loop"""
        
        logger.info("STARTING SIMPLE MCP HEART")
        logger.info("=" * 60)
        logger.info("EA v8_Fixed -> 4-Phase Signal -> Simple Processing -> Trade Response")
        logger.info("=" * 60)
        
        self.is_running = True
        last_signal_content = None
        
        while self.is_running:
            try:
                # Check for new 4-phase signal from EA
                if self.signal_file.exists():
                    with open(self.signal_file, 'r') as f:
                        signal_content = f.read()
                    
                    # Only process if signal content changed
                    if signal_content != last_signal_content:
                        logger.info("NEW 4-PHASE SIGNAL DETECTED FROM EA v8_Fixed")
                        
                        try:
                            signal_data = json.loads(signal_content)
                            await self.process_simple_signal(signal_data)
                            last_signal_content = signal_content
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON in signal file: {e}")
                        except Exception as e:
                            logger.error(f"Error processing signal: {e}")
                
                # Heart beat every 100ms for real-time processing
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Heart stopped by user")
                break
            except Exception as e:
                logger.error(f"Heart error: {e}")
                await asyncio.sleep(1)  # Prevent rapid error loops
    
    async def process_simple_signal(self, signal_data: Dict[str, Any]):
        """Process 4-phase signal with simplified logic"""
        
        start_time = time.time()
        self.processed_signals += 1
        
        logger.info(f"PROCESSING SIGNAL #{self.processed_signals}")
        logger.info(f"   Symbol: {signal_data.get('symbol', 'N/A')}")
        logger.info(f"   Direction: {signal_data.get('direction', 'N/A')}")
        logger.info(f"   Strategy: {signal_data.get('strategy', 'N/A')}")
        
        try:
            # Simple validation - approve most signals
            if self.simple_validation(signal_data):
                logger.info("Signal APPROVED by simple validation")
                
                # Generate trade response
                trade_response = self.generate_simple_trade_response(signal_data)
                
                # Send response back to EA
                await self.send_trade_response(trade_response)
                
                processing_time = (time.time() - start_time) * 1000
                logger.info(f"SIGNAL PROCESSED SUCCESSFULLY in {processing_time:.1f}ms")
            else:
                logger.warning("Signal REJECTED by simple validation")
                await self.send_rejection_response(signal_data, "Simple validation failed")
                
        except Exception as e:
            logger.error(f"SIGNAL PROCESSING FAILED: {e}")
            await self.send_error_response(signal_data, str(e))
    
    def simple_validation(self, signal_data: Dict[str, Any]) -> bool:
        """Simple signal validation logic"""
        
        # Basic validation rules
        symbol = signal_data.get('symbol', '')
        direction = signal_data.get('direction', '')
        
        # Must have valid symbol and direction
        if not symbol or not direction:
            return False
        
        # Accept BCHUSD signals
        if symbol == 'BCHUSD':
            return True
        
        # Accept other major pairs
        major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD']
        if symbol in major_pairs:
            return True
        
        # Accept crypto
        crypto_symbols = ['BTCUSD', 'ETHUSD', 'XRPUSD', 'LTCUSD', 'ADAUSD']
        if symbol in crypto_symbols:
            return True
        
        # Reject others for now
        return False
    
    def generate_simple_trade_response(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate simplified trade response"""
        
        symbol = signal_data.get('symbol', 'BCHUSD')
        direction = signal_data.get('direction', 'BUY')
        
        # Simple trade parameters based on symbol
        if symbol == 'BCHUSD':
            entry_price = 541.0
            pip_value = 0.1  # CFD_CRYPTO
            stop_loss_pips = 8
            take_profit_pips = 16
            lot_size = 1.0
        elif symbol in ['BTCUSD', 'ETHUSD']:
            entry_price = 65000.0 if symbol == 'BTCUSD' else 3500.0
            pip_value = 1.0
            stop_loss_pips = 50
            take_profit_pips = 100
            lot_size = 0.1
        else:  # Forex pairs
            entry_price = 1.0800
            pip_value = 0.0001
            stop_loss_pips = 15
            take_profit_pips = 30
            lot_size = 0.1
        
        # Calculate SL/TP
        if direction == 'BUY':
            stop_loss = entry_price - (stop_loss_pips * pip_value)
            take_profit = entry_price + (take_profit_pips * pip_value)
        else:
            stop_loss = entry_price + (stop_loss_pips * pip_value)
            take_profit = entry_price - (take_profit_pips * pip_value)
        
        trade_response = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'signal_id': f"simple_{self.processed_signals}_{int(time.time())}",
            'action': 'EXECUTE_TRADE',
            'symbol': symbol,
            'direction': direction,
            'lot_size': lot_size,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'magic_number': 999888,
            'comment': f"SIMPLE_MCP_{direction}",
            'confidence': 0.85,
            'source': 'SIMPLE_MCP_HEART'
        }
        
        return trade_response
    
    async def send_trade_response(self, trade_response: Dict[str, Any]):
        """Send trade response back to EA"""
        
        try:
            with open(self.response_file, 'w') as f:
                json.dump(trade_response, f, indent=2)
            
            logger.info("TRADE RESPONSE SENT TO EA")
            logger.info(f"   Action: {trade_response['action']}")
            logger.info(f"   Symbol: {trade_response['symbol']} {trade_response['direction']}")
            logger.info(f"   Lot Size: {trade_response['lot_size']}")
            logger.info(f"   Entry: {trade_response['entry_price']}")
            logger.info(f"   SL: {trade_response['stop_loss']}")
            logger.info(f"   TP: {trade_response['take_profit']}")
            
        except Exception as e:
            logger.error(f"Failed to send trade response: {e}")
    
    async def send_rejection_response(self, signal_data: Dict[str, Any], reason: str):
        """Send rejection response to EA"""
        
        rejection_response = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': 'REJECT_TRADE',
            'symbol': signal_data.get('symbol', 'BCHUSD'),
            'reason': reason,
            'source': 'SIMPLE_MCP_HEART'
        }
        
        with open(self.response_file, 'w') as f:
            json.dump(rejection_response, f, indent=2)
        
        logger.warning(f"TRADE REJECTED: {reason}")
    
    async def send_error_response(self, signal_data: Dict[str, Any], error: str):
        """Send error response to EA"""
        
        error_response = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': 'ERROR',
            'symbol': signal_data.get('symbol', 'BCHUSD'),
            'error': error,
            'source': 'SIMPLE_MCP_HEART'
        }
        
        with open(self.response_file, 'w') as f:
            json.dump(error_response, f, indent=2)
        
        logger.error(f"ERROR RESPONSE SENT: {error}")
    
    def stop_heart(self):
        """Stop the heart"""
        self.is_running = False
        logger.info("SIMPLE MCP HEART STOPPED")

async def main():
    """Main entry point"""
    
    print("STARTING SIMPLE MCP HEART SYSTEM")
    print("=" * 60)
    print("Lightweight bridge between EA v8_Fixed and trading logic")
    print("This version works without complex orchestration dependencies")
    print("=" * 60)
    
    heart = SimpleMCPHeart()
    
    try:
        await heart.start_heart()
    except KeyboardInterrupt:
        print("\nHeart stopped by user")
    finally:
        heart.stop_heart()

if __name__ == "__main__":
    asyncio.run(main())