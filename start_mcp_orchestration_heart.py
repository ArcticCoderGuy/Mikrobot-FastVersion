from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MCP ORCHESTRATION HEART - THE MISSING PIECE
Signal monitoring and processing system that bridges EA v8_Fixed with MCP orchestration

This is the heart that processes 4-phase signals from EA through the MCP pipeline
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import os

# Import the orchestration components from Session #1
try:
    from src.core.enhanced_orchestrator import EnhancedOrchestrator
    from src.core.product_owner_agent import ProductOwnerAgent, StrategyType
    from src.core.mcp_controller import MCPController
except ImportError as e:
    print(f"ERROR: Cannot import orchestration components: {e}")
    print("Make sure Session #1 components are available")
    exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPOrchestrationHeart:
    """
    The heart of the MCP orchestration system
    Monitors 4-phase signals from EA v8_Fixed and processes them through MCP pipeline
    """
    
    def __init__(self):
        self.signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
        self.response_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_trade_response.json")
        
        # Initialize orchestration components
        self.product_owner = ProductOwnerAgent()
        self.mcp_controller = MCPController()
        self.orchestrator = EnhancedOrchestrator(
            product_owner=self.product_owner,
            mcp_controller=self.mcp_controller
        )
        
        self.is_running = False
        self.processed_signals = 0
        
        logger.info("MCP ORCHESTRATION HEART INITIALIZED")
        logger.info(f"Monitoring: {self.signal_file}")
        logger.info(f"Response: {self.response_file}")
    
    async def start_heart(self):
        """Start the heart - main monitoring loop"""
        
        logger.info("ROCKET STARTING MCP ORCHESTRATION HEART")
        logger.info("=" * 60)
        logger.info("EA v8_Fixed -> 4-Phase Signal -> MCP Processing -> Trade Response")
        logger.info("=" * 60)
        
        self.is_running = True
        last_signal_content = None
        
        while self.is_running:
            try:
                # Check for new 4-phase signal from EA
                if self.signal_file.exists():
                    with open(self.signal_file, 'r', encoding='ascii', errors='ignore') as f:
                        signal_content = f.read()
                    
                    # Only process if signal content changed
                    if signal_content != last_signal_content:
                        logger.info(" NEW 4-PHASE SIGNAL DETECTED FROM EA v8_Fixed")
                        
                        try:
                            signal_data = json.loads(signal_content)
                            await self.process_4phase_signal(signal_data)
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
    
    async def process_4phase_signal(self, signal_data: Dict[str, Any]):
        """Process 4-phase signal through MCP orchestration pipeline"""
        
        start_time = time.time()
        self.processed_signals += 1
        
        logger.info(f" PROCESSING SIGNAL #{self.processed_signals}")
        logger.info(f"   Symbol: {signal_data.get('symbol', 'N/A')}")
        logger.info(f"   Direction: {signal_data.get('direction', 'N/A')}")
        logger.info(f"   Strategy: {signal_data.get('strategy', 'N/A')}")
        
        try:
            # Step 1: Strategic evaluation by ProductOwner
            logger.info("TARGET STEP 1: ProductOwner strategic evaluation...")
            strategic_result = await self.product_owner.evaluate_signal(signal_data)
            
            if not strategic_result.get('approved', False):
                logger.warning("ERROR ProductOwner REJECTED signal")
                await self.send_rejection_response(signal_data, strategic_result.get('reason', 'Unknown'))
                return
            
            logger.info("OK ProductOwner APPROVED signal")
            
            # Step 2: Enhanced orchestration through MCP pipeline
            logger.info(" STEP 2: MCP orchestration pipeline...")
            
            # Convert to orchestrator format
            orchestrator_input = {
                'signal_id': f"signal_{self.processed_signals}_{int(time.time())}",
                'symbol': signal_data.get('symbol', 'BCHUSD'),
                'direction': signal_data.get('direction', 'BUY'),
                'signal_type': signal_data.get('signal_type', 'M5_BOS'),
                'confidence': signal_data.get('confidence', 0.85),
                'source': 'EA_v8_Fixed_4Phase',
                'timestamp': datetime.now().isoformat()
            }
            
            # Process through orchestrator
            orchestration_result = await self.orchestrator.process_signal(orchestrator_input)
            
            # Step 3: Generate trade response for EA
            logger.info(" STEP 3: Generating trade response for EA...")
            trade_response = self.generate_trade_response(signal_data, strategic_result, orchestration_result)
            
            # Step 4: Send response back to EA
            await self.send_trade_response(trade_response)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"OK SIGNAL PROCESSED SUCCESSFULLY in {processing_time:.1f}ms")
            
        except Exception as e:
            logger.error(f"ERROR SIGNAL PROCESSING FAILED: {e}")
            await self.send_error_response(signal_data, str(e))
    
    def generate_trade_response(self, signal_data: Dict[str, Any], strategic_result: Dict[str, Any], orchestration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trade response for EA based on MCP processing"""
        
        # Extract recommended values from orchestration
        risk_data = orchestration_result.get('u_cell_results', {}).get('risk_assessment', {})
        ml_data = orchestration_result.get('u_cell_results', {}).get('ml_analysis', {})
        
        # Calculate trade parameters
        symbol = signal_data.get('symbol', 'BCHUSD')
        direction = signal_data.get('direction', 'BUY')
        
        # Default values with MCP enhancement
        lot_size = risk_data.get('recommended_lot_size', 1.0)
        stop_loss_pips = risk_data.get('stop_loss_pips', 8)
        take_profit_pips = risk_data.get('take_profit_pips', 16)
        
        # For BCHUSD CFD_CRYPTO
        if symbol == 'BCHUSD':
            pip_value = 0.1  # CFD_CRYPTO pip value
            entry_price = 541.0  # Current approximate price
            
            if direction == 'BUY':
                stop_loss = entry_price - (stop_loss_pips * pip_value)
                take_profit = entry_price + (take_profit_pips * pip_value)
            else:
                stop_loss = entry_price + (stop_loss_pips * pip_value)
                take_profit = entry_price - (take_profit_pips * pip_value)
        else:
            entry_price = 1.0800  # Default for other pairs
            stop_loss = entry_price - 0.0008 if direction == 'BUY' else entry_price + 0.0008
            take_profit = entry_price + 0.0016 if direction == 'BUY' else entry_price - 0.0016
        
        trade_response = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'signal_id': orchestration_result.get('pipeline_id', 'unknown'),
            'action': 'EXECUTE_TRADE',
            'symbol': symbol,
            'direction': direction,
            'lot_size': lot_size,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'magic_number': 999888,
            'comment': f"MCP_ORCHESTRATED_{direction}",
            'confidence': ml_data.get('confidence', 0.85),
            'source': 'MCP_ORCHESTRATION_HEART',
            'processing_time_ms': orchestration_result.get('total_latency_ms', 0),
            'strategic_approval': strategic_result,
            'mcp_results': orchestration_result
        }
        
        return trade_response
    
    async def send_trade_response(self, trade_response: Dict[str, Any]):
        """Send trade response back to EA"""
        
        try:
            # Remove large objects for cleaner EA response
            clean_response = trade_response.copy()
            if 'mcp_results' in clean_response:
                del clean_response['mcp_results']
            
            with open(self.response_file, 'w', encoding='ascii', errors='ignore') as f:
                json.dump(clean_response, f, indent=2)
            
            logger.info(" TRADE RESPONSE SENT TO EA")
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
            'source': 'MCP_ORCHESTRATION_HEART'
        }
        
        with open(self.response_file, 'w', encoding='ascii', errors='ignore') as f:
            json.dump(rejection_response, f, indent=2)
        
        logger.warning(f" TRADE REJECTED: {reason}")
    
    async def send_error_response(self, signal_data: Dict[str, Any], error: str):
        """Send error response to EA"""
        
        error_response = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'action': 'ERROR',
            'symbol': signal_data.get('symbol', 'BCHUSD'),
            'error': error,
            'source': 'MCP_ORCHESTRATION_HEART'
        }
        
        with open(self.response_file, 'w', encoding='ascii', errors='ignore') as f:
            json.dump(error_response, f, indent=2)
        
        logger.error(f" ERROR RESPONSE SENT: {error}")
    
    def stop_heart(self):
        """Stop the heart"""
        self.is_running = False
        logger.info(" MCP ORCHESTRATION HEART STOPPED")

async def main():
    """Main entry point"""
    
    print("ROCKET STARTING MCP ORCHESTRATION HEART SYSTEM")
    print("=" * 60)
    print("This is the missing piece that processes EA v8_Fixed signals")
    print("through the Session #1 MCP orchestration pipeline!")
    print("=" * 60)
    
    heart = MCPOrchestrationHeart()
    
    try:
        await heart.start_heart()
    except KeyboardInterrupt:
        print("\n  Heart stopped by user")
    finally:
        heart.stop_heart()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(main())