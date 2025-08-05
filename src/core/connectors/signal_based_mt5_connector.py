from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Signal-Based MT5 Connector
Resolves connection conflicts by using MQL5 EA communication
Maintains user's terminal/mobile connection while enabling bot trading
"""

import json
import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio
import uuid

logger = logging.getLogger(__name__)


@dataclass
class TradingSignal:
    """Trading signal structure for MQL5 EA communication"""
    signal_id: str
    signal_type: str  # OPEN, CLOSE, MODIFY, STATUS_REQUEST
    symbol: str
    action: str  # BUY, SELL
    volume: float
    price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    comment: str = "Mikrobot"
    magic_number: int = 999888
    timestamp: str = None
    expiry_seconds: int = 300  # Signal expires in 5 minutes
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ExecutionResponse:
    """Response from MQL5 EA after signal execution"""
    signal_id: str
    success: bool
    ticket: Optional[int] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    execution_price: Optional[float] = None
    execution_time: Optional[str] = None
    account_info: Optional[Dict] = None


class SignalBasedMT5Connector:
    """
    Signal-based MT5 connector that preserves existing connections
    Uses file-based communication with MQL5 Expert Advisor
    """
    
    def __init__(self, 
                 signal_directory: str = None,
                 response_directory: str = None,
                 ea_name: str = "MikrobotEA",
                 timeout_seconds: int = 30):
        
        # Default MT5 file paths
        self.mt5_files_path = Path.home() / "AppData/Roaming/MetaQuotes/Terminal"
        
        # Find the correct terminal folder
        if signal_directory:
            self.signal_dir = Path(signal_directory)
        else:
            self.signal_dir = self._find_mt5_files_directory() / "Files"
            
        if response_directory:
            self.response_dir = Path(response_directory)
        else:
            self.response_dir = self.signal_dir
            
        self.ea_name = ea_name
        self.timeout_seconds = timeout_seconds
        
        # Ensure directories exist
        self.signal_dir.mkdir(parents=True, exist_ok=True)
        self.response_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths - CORRECTED to match EA expectations
        self.signal_file = self.signal_dir / "mikrobot_fastversion_signal.json"
        self.response_file = self.response_dir / f"{ea_name}_response.json"
        self.status_file = self.signal_dir / f"{ea_name}_status.json"
        
        # Connection state
        self.is_connected = False
        self.last_heartbeat = None
        
        # Metrics
        self.metrics = {
            'signals_sent': 0,
            'signals_executed': 0,
            'signals_failed': 0,
            'execution_latency_ms': [],
            'connection_checks': 0
        }
        
        logger.info(f"Signal-based connector initialized")
        logger.info(f"Signal directory: {self.signal_dir}")
        logger.info(f"Response directory: {self.response_dir}")
    
    def _find_mt5_files_directory(self) -> Path:
        """Find MT5 terminal directory automatically"""
        terminal_base = self.mt5_files_path
        
        if not terminal_base.exists():
            raise Exception(f"MT5 terminal directory not found: {terminal_base}")
        
        # Look for terminal folders
        terminal_folders = [d for d in terminal_base.iterdir() 
                          if d.is_dir() and len(d.name) == 32]  # Terminal hash folders
        
        if not terminal_folders:
            # Try Common folder
            common_path = terminal_base / "Common"
            if common_path.exists():
                return common_path
            raise Exception("No MT5 terminal folders found")
        
        # Use the most recently modified terminal folder
        latest_terminal = max(terminal_folders, key=lambda x: x.stat().st_mtime)
        logger.info(f"Using MT5 terminal: {latest_terminal}")
        
        return latest_terminal
    
    async def connect(self) -> bool:
        """
        Establish signal-based connection
        Does NOT interfere with existing MT5 connections
        """
        try:
            # Send connection test signal
            test_signal = TradingSignal(
                signal_id=str(uuid.uuid4()),
                signal_type="CONNECTION_TEST",
                symbol="EURUSD",
                action="NONE",
                volume=0.0,
                comment="Connection test"
            )
            
            success = await self._send_signal(test_signal)
            if success:
                # Wait for EA response
                response = await self._wait_for_response(test_signal.signal_id, timeout=10)
                if response and response.success:
                    self.is_connected = True
                    self.last_heartbeat = datetime.now()
                    logger.info("OK Signal-based connection established")
                    return True
            
            logger.error("ERROR EA not responding to connection test")
            return False
            
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False
    
    async def disconnect(self):
        """Clean disconnect - removes signal files"""
        try:
            # Send disconnect signal
            if self.is_connected:
                disconnect_signal = TradingSignal(
                    signal_id=str(uuid.uuid4()),
                    signal_type="DISCONNECT",
                    symbol="EURUSD",
                    action="NONE",
                    volume=0.0
                )
                await self._send_signal(disconnect_signal)
            
            # Clean up files
            for file_path in [self.signal_file, self.response_file]:
                if file_path.exists():
                    file_path.unlink()
            
            self.is_connected = False
            logger.info("Disconnected from signal-based MT5")
            
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")
    
    async def ensure_connected(self) -> bool:
        """Check connection health via heartbeat"""
        if not self.is_connected:
            return await self.connect()
        
        # Check last heartbeat
        if (self.last_heartbeat and 
            datetime.now() - self.last_heartbeat > timedelta(minutes=2)):
            logger.warning("Heartbeat timeout, reconnecting...")
            return await self.connect()
        
        return True
    
    async def place_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place order via signal to MQL5 EA
        Preserves user's connection while executing trades
        """
        if not await self.ensure_connected():
            return {'success': False, 'error': 'Signal connection not available'}
        
        try:
            start_time = time.time()
            
            # Create trading signal
            signal = TradingSignal(
                signal_id=str(uuid.uuid4()),
                signal_type="OPEN",
                symbol=order_params['symbol'],
                action=order_params['action'],  # BUY or SELL
                volume=order_params['volume'],
                price=order_params.get('price'),
                sl=order_params.get('sl'),
                tp=order_params.get('tp'),
                comment=order_params.get('comment', 'Mikrobot'),
                magic_number=order_params.get('magic', 999888)
            )
            
            # Send signal to EA
            if not await self._send_signal(signal):
                self.metrics['signals_failed'] += 1
                return {'success': False, 'error': 'Failed to send signal to EA'}
            
            self.metrics['signals_sent'] += 1
            
            # Wait for execution response
            response = await self._wait_for_response(signal.signal_id)
            
            if response:
                execution_time = (time.time() - start_time) * 1000
                self.metrics['execution_latency_ms'].append(execution_time)
                
                if response.success:
                    self.metrics['signals_executed'] += 1
                    return {
                        'success': True,
                        'ticket': response.ticket,
                        'execution_price': response.execution_price,
                        'execution_time_ms': execution_time,
                        'signal_id': signal.signal_id
                    }
                else:
                    self.metrics['signals_failed'] += 1
                    return {
                        'success': False,
                        'error': response.error_message,
                        'error_code': response.error_code,
                        'signal_id': signal.signal_id
                    }
            else:
                self.metrics['signals_failed'] += 1
                return {
                    'success': False, 
                    'error': 'Timeout waiting for EA response',
                    'signal_id': signal.signal_id
                }
                
        except Exception as e:
            logger.error(f"Order placement error: {str(e)}")
            self.metrics['signals_failed'] += 1
            return {'success': False, 'error': str(e)}
    
    async def close_position(self, ticket: int) -> Dict[str, Any]:
        """Close position via signal to MQL5 EA"""
        if not await self.ensure_connected():
            return {'success': False, 'error': 'Signal connection not available'}
        
        try:
            signal = TradingSignal(
                signal_id=str(uuid.uuid4()),
                signal_type="CLOSE",
                symbol="ANY",  # EA will determine from ticket
                action="CLOSE",
                volume=0.0,  # EA will use position volume
                comment=f"Close #{ticket}"
            )
            
            # Add ticket info to signal
            signal_data = asdict(signal)
            signal_data['ticket'] = ticket
            
            # Send modified signal
            if not await self._send_signal_data(signal_data):
                return {'success': False, 'error': 'Failed to send close signal'}
            
            # Wait for response
            response = await self._wait_for_response(signal.signal_id)
            
            if response and response.success:
                return {
                    'success': True,
                    'ticket': ticket,
                    'close_price': response.execution_price,
                    'close_time': response.execution_time
                }
            else:
                error_msg = response.error_message if response else "Timeout"
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            logger.error(f"Position close error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions via status request to EA"""
        if not await self.ensure_connected():
            return []
        
        try:
            signal = TradingSignal(
                signal_id=str(uuid.uuid4()),
                signal_type="STATUS_REQUEST",
                symbol="ANY",
                action="GET_POSITIONS",
                volume=0.0
            )
            
            if not await self._send_signal(signal):
                return []
            
            response = await self._wait_for_response(signal.signal_id)
            
            if response and response.success and response.account_info:
                return response.account_info.get('positions', [])
            
            return []
            
        except Exception as e:
            logger.error(f"Get positions error: {str(e)}")
            return []
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account info via status request to EA"""
        if not await self.ensure_connected():
            return None
        
        try:
            signal = TradingSignal(
                signal_id=str(uuid.uuid4()),
                signal_type="STATUS_REQUEST",
                symbol="ANY",
                action="GET_ACCOUNT",
                volume=0.0
            )
            
            if not await self._send_signal(signal):
                return None
            
            response = await self._wait_for_response(signal.signal_id)
            
            if response and response.success and response.account_info:
                return response.account_info.get('account', {})
            
            return None
            
        except Exception as e:
            logger.error(f"Get account info error: {str(e)}")
            return None
    
    async def _send_signal(self, signal: TradingSignal) -> bool:
        """Send signal to MQL5 EA via JSON file"""
        try:
            return await self._send_signal_data(asdict(signal))
        except Exception as e:
            logger.error(f"Send signal error: {str(e)}")
            return False
    
    async def _send_signal_data(self, signal_data: Dict) -> bool:
        """Send signal data to MQL5 EA via JSON file"""
        try:
            # Write signal file atomically
            temp_file = self.signal_file.with_suffix('.tmp')
            
            with temp_file.open('w') as f:
                json.dump(signal_data, f, indent=2)
            
            # Atomic move
            temp_file.replace(self.signal_file)
            
            logger.debug(f"Signal sent: {signal_data['signal_type']} - {signal_data['signal_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Send signal data error: {str(e)}")
            return False
    
    async def _wait_for_response(self, signal_id: str, timeout: int = None) -> Optional[ExecutionResponse]:
        """Wait for EA response to signal"""
        timeout = timeout or self.timeout_seconds
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if self.response_file.exists():
                    with self.response_file.open('r') as f:
                        response_data = json.load(f)
                    
                    if response_data.get('signal_id') == signal_id:
                        # Remove response file after reading
                        self.response_file.unlink()
                        
                        return ExecutionResponse(
                            signal_id=response_data['signal_id'],
                            success=response_data.get('success', False),
                            ticket=response_data.get('ticket'),
                            error_code=response_data.get('error_code'),
                            error_message=response_data.get('error_message'),
                            execution_price=response_data.get('execution_price'),
                            execution_time=response_data.get('execution_time'),
                            account_info=response_data.get('account_info')
                        )
                
                await asyncio.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                logger.error(f"Response wait error: {str(e)}")
                await asyncio.sleep(0.1)
        
        logger.warning(f"Timeout waiting for response to signal {signal_id}")
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get connector performance metrics"""
        avg_latency = 0
        if self.metrics['execution_latency_ms']:
            avg_latency = sum(self.metrics['execution_latency_ms']) / len(self.metrics['execution_latency_ms'])
        
        success_rate = 0
        total_signals = self.metrics['signals_executed'] + self.metrics['signals_failed']
        if total_signals > 0:
            success_rate = self.metrics['signals_executed'] / total_signals
        
        return {
            **self.metrics,
            'avg_execution_latency_ms': round(avg_latency, 2),
            'success_rate': round(success_rate, 3),
            'is_connected': self.is_connected,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None
        }