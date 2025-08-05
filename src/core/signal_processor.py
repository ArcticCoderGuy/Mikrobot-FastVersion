#!/usr/bin/env python3
"""
High-Performance Signal Processing Engine
Handles MT5 signal files, validation, and caching with async I/O
Replaces signal-specific processing across multiple execute files
"""

import asyncio
import json
import re
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Local imports
from ..utils.encoding_utils import ASCIIFileManager, ascii_print
from ..utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class SignalType(Enum):
    HANSEI_4PHASE = "HANSEI_4PHASE"
    BOS_M5M1 = "BOS_M5M1"
    YLIPIP_TRIGGER = "YLIPIP_TRIGGER"
    MANUAL = "MANUAL"
    API = "API"


class SignalStatus(Enum):
    PENDING = "PENDING"
    VALID = "VALID"
    INVALID = "INVALID"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"


@dataclass
class ProcessedSignal:
    """Standardized processed signal structure"""
    valid: bool
    symbol: str
    direction: str
    signal_type: SignalType
    confidence: float
    timestamp: datetime
    atr_pips: Optional[float] = None
    risk_percent: float = 0.55
    magic: int = 234000
    strategy: str = "AUTO"
    metadata: Dict[str, Any] = None
    reason: Optional[str] = None  # For invalid signals


class SignalProcessor:
    """
    High-performance signal processor with caching and validation
    Handles all signal types and formats used across the trading system
    """
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        
        # Signal file paths
        self.signal_paths = {
            'primary': Path('C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'),
            'backup': Path('signals/current_signal.json'),
            'archive': Path('signals/archive/')
        }
        
        # Caching system
        self._signal_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = timedelta(seconds=10)  # Short TTL for signals
        
        # Validation rules
        self.validation_rules = {
            'required_fields': ['symbol', 'trade_direction', 'timestamp'],
            'valid_directions': ['BUY', 'SELL', 'BULL', 'BEAR'],
            'symbol_patterns': {
                'forex': r'^[A-Z]{6}$',
                'crypto': r'^[A-Z]+USD$',
                'stocks': r'^_[A-Z]+\.[A-Z]{2}$'
            },
            'max_age_minutes': 30
        }
        
        # Performance metrics
        self.metrics = {
            'signals_processed': 0,
            'valid_signals': 0,
            'invalid_signals': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'file_read_errors': 0,
            'average_processing_time_ms': 0.0
        }
        
        # Initialize ASCII output
        ASCIIFileManager.initialize_ascii_output()
    
    async def initialize(self) -> bool:
        """Initialize signal processor"""
        try:
            ascii_print("SIGNAL PROCESSOR INITIALIZATION")
            ascii_print("=" * 35)
            
            # Ensure signal directories exist
            for path_key, path in self.signal_paths.items():
                if path_key != 'primary':  # Don't create MT5 directory
                    path.parent.mkdir(parents=True, exist_ok=True)
            
            # Test signal file access
            if self.signal_paths['primary'].exists():
                test_signal = await self._read_signal_file(self.signal_paths['primary'])
                if test_signal:
                    ascii_print("Primary signal file accessible")
                else:
                    ascii_print("WARNING: Cannot read primary signal file")
            else:
                ascii_print("WARNING: Primary signal file does not exist")
            
            ascii_print("Signal processor initialized successfully")
            ascii_print("")
            
            return True
            
        except Exception as e:
            logger.error(f"Signal processor initialization failed: {str(e)}")
            ascii_print(f"ERROR: Initialization failed - {str(e)}")
            return False
    
    async def process_signal(self, signal_data: Union[Dict[str, Any], str, Path]) -> ProcessedSignal:
        """Process signal from various sources with full validation"""
        start_time = datetime.now()
        
        try:
            self.metrics['signals_processed'] += 1
            
            # Handle different input types
            if isinstance(signal_data, (str, Path)):
                # File path provided
                raw_signal = await self._read_signal_file(Path(signal_data))
                if not raw_signal:
                    return self._create_invalid_signal("Failed to read signal file")
            elif isinstance(signal_data, dict):
                # Direct signal data
                raw_signal = signal_data
            else:
                return self._create_invalid_signal(f"Invalid signal data type: {type(signal_data)}")
            
            # Validate signal structure
            validation_result = await self._validate_signal_structure(raw_signal)
            if not validation_result['valid']:
                return self._create_invalid_signal(validation_result['reason'])
            
            # Determine signal type
            signal_type = self._determine_signal_type(raw_signal)
            
            # Process based on signal type
            if signal_type == SignalType.HANSEI_4PHASE:
                processed = await self._process_hansei_signal(raw_signal)
            elif signal_type == SignalType.BOS_M5M1:
                processed = await self._process_bos_signal(raw_signal)
            elif signal_type == SignalType.YLIPIP_TRIGGER:
                processed = await self._process_ylipip_signal(raw_signal)
            else:
                processed = await self._process_generic_signal(raw_signal)
            
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_processing_time_metric(processing_time)
            
            if processed.valid:
                self.metrics['valid_signals'] += 1
                ascii_print(f"SIGNAL PROCESSED: {processed.symbol} {processed.direction} ({signal_type.value})")
            else:
                self.metrics['invalid_signals'] += 1
                ascii_print(f"INVALID SIGNAL: {processed.reason}")
            
            # Cache the processed signal
            await self._cache_processed_signal(processed)
            
            return processed
            
        except Exception as e:
            logger.error(f"Signal processing error: {str(e)}")
            self.metrics['invalid_signals'] += 1
            return self._create_invalid_signal(f"Processing error: {str(e)}")
    
    async def read_current_signal(self) -> Optional[ProcessedSignal]:
        """Read and process current signal from primary location"""
        try:
            # Try primary signal file first
            signal_data = await self._read_signal_file_cached(self.signal_paths['primary'])
            
            if signal_data:
                return await self.process_signal(signal_data)
            
            # Try backup location
            signal_data = await self._read_signal_file_cached(self.signal_paths['backup'])
            
            if signal_data:
                return await self.process_signal(signal_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading current signal: {str(e)}")
            return None
    
    async def _read_signal_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Read signal file with proper encoding handling"""
        try:
            if not file_path.exists():
                return None
            
            # Use ASCIIFileManager for proper MT5 file handling
            signal_data = ASCIIFileManager.read_mt5_signal_file(str(file_path))
            
            if signal_data:
                return signal_data
            
            # Fallback: try regular JSON read
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Clean any problematic characters
                content = re.sub(r'[^\x20-\x7E\n\r\t]', '', content)
                return json.loads(content)
                
        except Exception as e:
            logger.error(f"Error reading signal file {file_path}: {str(e)}")
            self.metrics['file_read_errors'] += 1
            return None
    
    async def _read_signal_file_cached(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Read signal file with caching"""
        cache_key = str(file_path)
        now = datetime.now()
        
        # Check cache
        if cache_key in self._signal_cache:
            cached_data = self._signal_cache[cache_key]
            if now - cached_data['timestamp'] < self._cache_ttl:
                self.metrics['cache_hits'] += 1
                return cached_data['data']
        
        # Cache miss - read file
        self.metrics['cache_misses'] += 1
        signal_data = await self._read_signal_file(file_path)
        
        if signal_data:
            self._signal_cache[cache_key] = {
                'data': signal_data,
                'timestamp': now
            }
        
        return signal_data
    
    async def _validate_signal_structure(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate basic signal structure"""
        # Check required fields
        for field in self.validation_rules['required_fields']:
            if field not in signal_data:
                return {'valid': False, 'reason': f'Missing required field: {field}'}
        
        # Validate symbol format
        symbol = signal_data['symbol']
        if not self._validate_symbol_format(symbol):
            return {'valid': False, 'reason': f'Invalid symbol format: {symbol}'}
        
        # Validate direction
        direction = signal_data.get('trade_direction', '').upper()
        if direction not in self.validation_rules['valid_directions']:
            return {'valid': False, 'reason': f'Invalid trade direction: {direction}'}
        
        # Validate timestamp age
        if 'timestamp' in signal_data:
            try:
                signal_time = datetime.fromisoformat(signal_data['timestamp'].replace('Z', '+00:00'))
                age_minutes = (datetime.now() - signal_time).total_seconds() / 60
                
                if age_minutes > self.validation_rules['max_age_minutes']:
                    return {'valid': False, 'reason': f'Signal too old: {age_minutes:.1f} minutes'}
            except Exception:
                return {'valid': False, 'reason': 'Invalid timestamp format'}
        
        return {'valid': True}
    
    def _validate_symbol_format(self, symbol: str) -> bool:
        """Validate symbol format against known patterns"""
        for pattern_name, pattern in self.validation_rules['symbol_patterns'].items():
            if re.match(pattern, symbol):
                return True
        return False
    
    def _determine_signal_type(self, signal_data: Dict[str, Any]) -> SignalType:
        """Determine signal type from signal data"""
        # Check for Hansei 4-phase signals
        if all(key in signal_data for key in ['phase_1_bos', 'phase_2_break', 'phase_3_retest', 'phase_4_ylipip']):
            return SignalType.HANSEI_4PHASE
        
        # Check for BOS signals
        if 'bos_detected' in signal_data or 'market_structure' in signal_data:
            return SignalType.BOS_M5M1
        
        # Check for YLIPIP triggers
        if 'ylipip_trigger' in signal_data or 'ylipip_value' in signal_data:
            return SignalType.YLIPIP_TRIGGER
        
        # Default to manual/generic
        return SignalType.MANUAL
    
    async def _process_hansei_signal(self, signal_data: Dict[str, Any]) -> ProcessedSignal:
        """Process Hansei 4-phase trading signal"""
        try:
            # Validate 4-phase completion
            phases = ['phase_1_bos', 'phase_2_break', 'phase_3_retest', 'phase_4_ylipip']
            phase_status = {}
            
            for phase in phases:
                if phase in signal_data:
                    phase_data = signal_data[phase]
                    if isinstance(phase_data, dict):
                        phase_status[phase] = phase_data.get('completed', False)
                    else:
                        phase_status[phase] = bool(phase_data)
                else:
                    phase_status[phase] = False
            
            # Check if all phases completed
            all_phases_complete = all(phase_status.values())
            
            if not all_phases_complete:
                return ProcessedSignal(
                    valid=False,
                    symbol=signal_data['symbol'],
                    direction=signal_data['trade_direction'],
                    signal_type=SignalType.HANSEI_4PHASE,
                    confidence=0.0,
                    timestamp=datetime.now(),
                    reason="Not all 4 phases completed"
                )
            
            # Calculate confidence based on signal quality
            confidence = self._calculate_hansei_confidence(signal_data)
            
            # Extract ATR if available
            atr_pips = signal_data.get('atr_pips') or signal_data.get('calculated_atr')
            
            return ProcessedSignal(
                valid=True,
                symbol=signal_data['symbol'],
                direction=signal_data['trade_direction'].upper(),
                signal_type=SignalType.HANSEI_4PHASE,
                confidence=confidence,
                timestamp=datetime.fromisoformat(signal_data['timestamp'].replace('Z', '+00:00')),
                atr_pips=atr_pips,
                strategy="HANSEI_4PHASE",
                metadata={
                    'phases': phase_status,
                    'ylipip_value': signal_data.get('ylipip_trigger'),
                    'market_structure': signal_data.get('market_structure')
                }
            )
            
        except Exception as e:
            logger.error(f"Hansei signal processing error: {str(e)}")
            return self._create_invalid_signal(f"Hansei processing error: {str(e)}")
    
    async def _process_bos_signal(self, signal_data: Dict[str, Any]) -> ProcessedSignal:
        """Process Break of Structure signal"""
        try:
            confidence = 0.7  # Base confidence for BOS signals
            
            # Increase confidence based on signal quality indicators
            if signal_data.get('volume_confirmation'):
                confidence += 0.1
            if signal_data.get('multiple_timeframe_confirmation'):
                confidence += 0.1
            if signal_data.get('trend_alignment'):
                confidence += 0.1
            
            confidence = min(confidence, 1.0)
            
            return ProcessedSignal(
                valid=True,
                symbol=signal_data['symbol'],
                direction=signal_data['trade_direction'].upper(),
                signal_type=SignalType.BOS_M5M1,
                confidence=confidence,
                timestamp=datetime.fromisoformat(signal_data['timestamp'].replace('Z', '+00:00')),
                atr_pips=signal_data.get('atr_pips'),
                strategy="BOS_M5M1",
                metadata={
                    'bos_level': signal_data.get('bos_level'),
                    'market_structure': signal_data.get('market_structure'),
                    'volume_confirmation': signal_data.get('volume_confirmation')
                }
            )
            
        except Exception as e:
            logger.error(f"BOS signal processing error: {str(e)}")
            return self._create_invalid_signal(f"BOS processing error: {str(e)}")
    
    async def _process_ylipip_signal(self, signal_data: Dict[str, Any]) -> ProcessedSignal:
        """Process YLIPIP trigger signal"""
        try:
            # YLIPIP signals are high confidence when triggered
            ylipip_value = signal_data.get('ylipip_trigger') or signal_data.get('ylipip_value')
            
            if not ylipip_value:
                return self._create_invalid_signal("YLIPIP value not found")
            
            # High confidence for YLIPIP triggers
            confidence = 0.9
            
            return ProcessedSignal(
                valid=True,
                symbol=signal_data['symbol'],
                direction=signal_data['trade_direction'].upper(),
                signal_type=SignalType.YLIPIP_TRIGGER,
                confidence=confidence,
                timestamp=datetime.fromisoformat(signal_data['timestamp'].replace('Z', '+00:00')),
                atr_pips=signal_data.get('atr_pips'),
                strategy="YLIPIP",
                metadata={
                    'ylipip_value': ylipip_value,
                    'trigger_price': signal_data.get('trigger_price')
                }
            )
            
        except Exception as e:
            logger.error(f"YLIPIP signal processing error: {str(e)}")
            return self._create_invalid_signal(f"YLIPIP processing error: {str(e)}")
    
    async def _process_generic_signal(self, signal_data: Dict[str, Any]) -> ProcessedSignal:
        """Process generic/manual signal"""
        try:
            # Base confidence for manual signals
            confidence = signal_data.get('confidence', 0.5)
            
            return ProcessedSignal(
                valid=True,
                symbol=signal_data['symbol'],
                direction=signal_data['trade_direction'].upper(),
                signal_type=SignalType.MANUAL,
                confidence=confidence,
                timestamp=datetime.fromisoformat(signal_data['timestamp'].replace('Z', '+00:00')),
                atr_pips=signal_data.get('atr_pips'),
                strategy=signal_data.get('strategy', 'MANUAL'),
                metadata=signal_data.get('metadata', {})
            )
            
        except Exception as e:
            logger.error(f"Generic signal processing error: {str(e)}")
            return self._create_invalid_signal(f"Generic processing error: {str(e)}")
    
    def _calculate_hansei_confidence(self, signal_data: Dict[str, Any]) -> float:
        """Calculate confidence score for Hansei signals"""
        base_confidence = 0.8  # High base confidence for 4-phase completion
        
        # Bonus factors
        if signal_data.get('volume_confirmation'):
            base_confidence += 0.05
        
        if signal_data.get('trend_alignment'):
            base_confidence += 0.05
        
        if signal_data.get('multiple_timeframe_confirmation'):
            base_confidence += 0.05
        
        # YLIPIP quality bonus
        ylipip_data = signal_data.get('phase_4_ylipip', {})
        if isinstance(ylipip_data, dict):
            ylipip_strength = ylipip_data.get('strength', 0.5)
            base_confidence += (ylipip_strength - 0.5) * 0.1
        
        return min(base_confidence, 1.0)
    
    def _create_invalid_signal(self, reason: str) -> ProcessedSignal:
        """Create invalid signal result"""
        return ProcessedSignal(
            valid=False,
            symbol="UNKNOWN",
            direction="UNKNOWN",
            signal_type=SignalType.MANUAL,
            confidence=0.0,
            timestamp=datetime.now(),
            reason=reason
        )
    
    async def _cache_processed_signal(self, processed_signal: ProcessedSignal):
        """Cache processed signal for quick access"""
        if processed_signal.valid:
            cache_key = f"processed_{processed_signal.symbol}_{processed_signal.timestamp.isoformat()}"
            self._signal_cache[cache_key] = {
                'data': processed_signal,
                'timestamp': datetime.now()
            }
    
    def _update_processing_time_metric(self, processing_time_ms: float):
        """Update average processing time metric"""
        total_processed = self.metrics['signals_processed']
        current_avg = self.metrics['average_processing_time_ms']
        
        # Running average calculation
        self.metrics['average_processing_time_ms'] = (
            (current_avg * (total_processed - 1) + processing_time_ms) / total_processed
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get signal processor performance metrics"""
        total_processed = self.metrics['signals_processed']
        valid_rate = self.metrics['valid_signals'] / total_processed if total_processed > 0 else 0
        
        cache_total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = self.metrics['cache_hits'] / cache_total if cache_total > 0 else 0
        
        return {
            **self.metrics,
            'valid_signal_rate': round(valid_rate, 3),
            'cache_hit_rate': round(cache_hit_rate, 3)
        }
    
    async def archive_signal(self, processed_signal: ProcessedSignal) -> bool:
        """Archive processed signal for historical analysis"""
        try:
            archive_file = self.signal_paths['archive'] / f"signal_{processed_signal.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            
            signal_record = {
                'timestamp': processed_signal.timestamp.isoformat(),
                'symbol': processed_signal.symbol,
                'direction': processed_signal.direction,
                'signal_type': processed_signal.signal_type.value,
                'confidence': processed_signal.confidence,
                'valid': processed_signal.valid,
                'strategy': processed_signal.strategy,
                'atr_pips': processed_signal.atr_pips,
                'metadata': processed_signal.metadata,
                'reason': processed_signal.reason
            }
            
            return ASCIIFileManager.write_ascii_json(str(archive_file), signal_record)
            
        except Exception as e:
            logger.error(f"Signal archiving error: {str(e)}")
            return False


# Standalone functions for testing and compatibility
async def test_signal_processor():
    """Test signal processor functionality"""
    processor = SignalProcessor()
    await processor.initialize()
    
    # Test with current signal
    current_signal = await processor.read_current_signal()
    if current_signal:
        ascii_print(f"Current signal: {current_signal.symbol} {current_signal.direction} (confidence: {current_signal.confidence:.2f})")
    else:
        ascii_print("No current signal found")
    
    # Display metrics
    metrics = processor.get_metrics()
    ascii_print(f"Processor metrics: {metrics}")
    
    return current_signal is not None


if __name__ == "__main__":
    asyncio.run(test_signal_processor())
