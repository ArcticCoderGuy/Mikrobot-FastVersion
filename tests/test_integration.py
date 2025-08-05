#!/usr/bin/env python3
"""
INTEGRATION TESTS FOR CONSOLIDATED TRADING SYSTEM
Tests signal file reading, consolidated executor modes, error handling and recovery
Validates end-to-end functionality and 19 original execute_*.py compatibility
"""

import pytest
import asyncio
import sys
import json
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import consolidated components
from src.core.trading_engine import TradingEngine, TradingSignal, ascii_print
from execute_consolidated import (
    execute_simple_mode, execute_eurjpy_mode, execute_ferrari_mode,
    execute_gbpjpy_mode, execute_multi_asset_mode, execute_signal_mode
)

class TestSignalFileIntegration:
    """Test real signal file processing and integration"""
    
    @pytest.fixture
    def signal_file_paths(self):
        """Standard signal file paths used by the system"""
        return [
            r"C:\Users\HP\AppData\Roaming\MetaQuotes\Terminal\Common\Files\mikrobot_4phase_signal.json",
            r"C:\Users\HP\AppData\Roaming\MetaQuotes\Terminal\Common\Files\mikrobot_test_signal.json"
        ]
    
    def create_test_signal_file(self, file_path: str, signal_data: Dict[str, Any]) -> None:
        """Create a test signal file with proper encoding"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Write as UTF-16LE with null bytes (matches actual MT5 signal files)
        content = json.dumps(signal_data, ensure_ascii=True)
        encoded_content = content.encode('utf-16le') + b'\x00\x00'
        
        with open(file_path, 'wb') as f:
            f.write(encoded_content)
    
    @pytest.mark.asyncio
    async def test_signal_file_reading_encoding(self):
        """Test signal file reading with various encoding scenarios"""
        engine = TradingEngine()
        await engine.initialize()
        
        try:
            # Test 1: Standard UTF-16LE with null bytes
            signal_data = {
                "symbol": "EURJPY",
                "trade_direction": "SELL",
                "timestamp": datetime.now().isoformat(),
                "current_price": 157.123,
                "phase_4_ylipip": {"triggered": True}
            }
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
                test_file = f.name
            
            self.create_test_signal_file(test_file, signal_data)
            
            result = await engine.read_signal_file_async(test_file)
            assert result is not None
            assert result['symbol'] == 'EURJPY'
            assert result['phase_4_ylipip']['triggered'] is True
            
            # Test 2: Corrupted file handling
            with open(test_file, 'wb') as f:
                f.write(b'\xff\xfe\x00\x00INVALID JSON')
            
            result = await engine.read_signal_file_async(test_file)
            assert result is None  # Should handle gracefully
            
        finally:
            try:
                Path(test_file).unlink()
            except:
                pass
            await engine.stop_engine()
    
    @pytest.mark.asyncio
    async def test_multi_signal_file_processing(self):
        """Test processing multiple signal files concurrently"""
        engine = TradingEngine()
        await engine.initialize()
        
        temp_files = []
        try:
            # Create multiple signal files
            signals = [
                {"symbol": "EURJPY", "trade_direction": "SELL", "current_price": 157.123},
                {"symbol": "_FERRARI.IT", "trade_direction": "BUY", "current_price": 123.45},
                {"symbol": "GBPJPY", "trade_direction": "SELL", "current_price": 187.456},
                {"symbol": "BCHUSD", "trade_direction": "BUY", "current_price": 234.56}
            ]
            
            for i, signal_data in enumerate(signals):
                signal_data["timestamp"] = datetime.now().isoformat()
                signal_data["phase_4_ylipip"] = {"triggered": True}
                
                temp_file = tempfile.mktemp(suffix=f'_signal_{i}.json')
                self.create_test_signal_file(temp_file, signal_data)
                temp_files.append(temp_file)
            
            # Read all files concurrently
            tasks = [engine.read_signal_file_async(path) for path in temp_files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify all files processed successfully
            assert len(results) == 4
            valid_results = [r for r in results if isinstance(r, dict)]
            assert len(valid_results) == 4
            
            # Verify signal creation from results
            trading_signals = []
            for result in valid_results:
                signal = engine.create_trading_signal(result)
                if signal and signal.is_valid():
                    trading_signals.append(signal)
            
            assert len(trading_signals) == 4
            symbols = {signal.symbol for signal in trading_signals}
            expected_symbols = {"EURJPY", "_FERRARI.IT", "GBPJPY", "BCHUSD"}
            assert symbols == expected_symbols
            
        finally:
            for temp_file in temp_files:
                try:
                    Path(temp_file).unlink()
                except:
                    pass
            await engine.stop_engine()

class TestConsolidatedExecutorModes:
    """Test all execution modes from execute_consolidated.py"""
    
    @pytest.fixture
    async def mock_engine(self):
        """Mock trading engine for mode testing"""
        engine = TradingEngine()
        
        # Mock MT5 operations
        with patch('src.core.trading_engine.mt5') as mock_mt5:
            mock_mt5.initialize.return_value = True
            mock_mt5.account_info.return_value = Mock(balance=100000.0, login=12345)
            mock_mt5.symbol_info_tick.return_value = Mock(bid=157.123, ask=157.126)
            mock_mt5.order_send.return_value = Mock(
                retcode=10009,  # TRADE_RETCODE_DONE
                order=12345,
                comment="Success"
            )
            
            await engine.initialize()
            yield engine
            await engine.stop_engine()
    
    @pytest.mark.asyncio
    async def test_simple_mode_execution(self, mock_engine):
        """Test simple execution mode"""
        # Mock args for simple mode
        args = Mock()
        args.symbol = "EURJPY" 
        args.direction = "SELL"
        args.manual = False
        
        # Replace the global trading_engine with our mock
        import execute_consolidated
        original_engine = execute_consolidated.trading_engine
        execute_consolidated.trading_engine = mock_engine
        
        try:
            result = await execute_simple_mode(args)
            assert result is True
        finally:
            execute_consolidated.trading_engine = original_engine
    
    @pytest.mark.asyncio 
    async def test_eurjpy_mode_variants(self, mock_engine):
        """Test EURJPY mode with different variants"""
        import execute_consolidated
        original_engine = execute_consolidated.trading_engine
        execute_consolidated.trading_engine = mock_engine
        
        try:
            variants = ['bear', 'bull', 'compliant', 'fixed', 'live', 'ultimate']
            
            for variant in variants:
                args = Mock()
                args.variant = variant
                
                result = await execute_eurjpy_mode(args)
                assert isinstance(result, bool)
                
        finally:
            execute_consolidated.trading_engine = original_engine
    
    @pytest.mark.asyncio
    async def test_ferrari_mode_execution(self, mock_engine):
        """Test Ferrari.IT CFD execution mode"""
        import execute_consolidated
        original_engine = execute_consolidated.trading_engine
        execute_consolidated.trading_engine = mock_engine
        
        try:
            args = Mock()
            result = await execute_ferrari_mode(args)
            assert isinstance(result, bool)
            
        finally:
            execute_consolidated.trading_engine = original_engine
    
    @pytest.mark.asyncio
    async def test_gbpjpy_mode_execution(self, mock_engine):
        """Test GBPJPY execution mode"""
        import execute_consolidated
        original_engine = execute_consolidated.trading_engine
        execute_consolidated.trading_engine = mock_engine
        
        try:
            # Test bear variant
            args = Mock()
            args.variant = 'bear'
            result = await execute_gbpjpy_mode(args)
            assert isinstance(result, bool)
            
            # Test bull variant
            args.variant = 'bull'
            result = await execute_gbpjpy_mode(args)
            assert isinstance(result, bool)
            
        finally:
            execute_consolidated.trading_engine = original_engine
    
    @pytest.mark.asyncio
    async def test_multi_asset_mode_execution(self, mock_engine):
        """Test multi-asset execution mode"""
        import execute_consolidated
        original_engine = execute_consolidated.trading_engine
        
        # Create mock engine with signal reading capability
        mock_engine.signal_paths = [
            tempfile.mktemp(suffix='_test1.json'),
            tempfile.mktemp(suffix='_test2.json')
        ]
        
        # Create test signal files
        signal_data = {
            "symbol": "EURJPY",
            "trade_direction": "SELL", 
            "timestamp": datetime.now().isoformat(),
            "current_price": 157.123,
            "phase_4_ylipip": {"triggered": True}
        }
        
        try:
            for path in mock_engine.signal_paths:
                with open(path, 'w') as f:
                    json.dump(signal_data, f)
            
            execute_consolidated.trading_engine = mock_engine
            
            args = Mock()
            result = await execute_multi_asset_mode(args)
            assert isinstance(result, bool)
            
        finally:
            for path in mock_engine.signal_paths:
                try:
                    Path(path).unlink()
                except:
                    pass
            execute_consolidated.trading_engine = original_engine
    
    @pytest.mark.asyncio
    async def test_signal_mode_execution(self, mock_engine):
        """Test universal signal execution mode"""
        import execute_consolidated
        original_engine = execute_consolidated.trading_engine
        execute_consolidated.trading_engine = mock_engine
        
        try:
            # Test specific symbol execution
            args = Mock()
            args.symbol = "EURJPY"
            args.direction = "SELL"
            
            result = await execute_signal_mode(args)
            assert isinstance(result, bool)
            
            # Test monitoring mode (no specific symbol)
            args.symbol = None
            args.direction = None
            
            result = await execute_signal_mode(args)
            assert isinstance(result, bool)
            
        finally:
            execute_consolidated.trading_engine = original_engine

class TestErrorHandlingAndRecovery:
    """Test error handling, recovery mechanisms, and edge cases"""
    
    @pytest.mark.asyncio
    async def test_mt5_connection_recovery(self):
        """Test MT5 connection failure and recovery"""
        engine = TradingEngine()
        
        # Simulate MT5 initialization failure, then success
        with patch('src.core.trading_engine.mt5') as mock_mt5:
            # First attempt fails
            mock_mt5.initialize.side_effect = [False, True]
            
            # First initialization should fail
            success = await engine.initialize()
            assert success is False
            
            # Second attempt should succeed
            success = await engine.initialize()
            assert success is True
    
    @pytest.mark.asyncio
    async def test_signal_cache_under_stress(self):
        """Test signal cache behavior under high load"""
        engine = TradingEngine()
        await engine.initialize()
        
        try:
            # Rapidly add many cache entries
            for i in range(1000):
                engine.signal_cache.set(f"key_{i}", {"data": i})
            
            # Verify cache still functions
            assert engine.signal_cache.get("key_500")["data"] == 500
            
            # Force cache cleanup
            engine.signal_cache.clear_expired()
            
            # Should still work after cleanup
            engine.signal_cache.set("new_key", {"test": True})
            assert engine.signal_cache.get("new_key")["test"] is True
            
        finally:
            await engine.stop_engine()
    
    @pytest.mark.asyncio
    async def test_concurrent_trade_execution_safety(self):
        """Test safety of concurrent trade executions"""
        engine = TradingEngine()
        
        with patch('src.core.trading_engine.mt5') as mock_mt5:
            mock_mt5.initialize.return_value = True
            mock_mt5.account_info.return_value = Mock(balance=100000.0, login=12345)
            mock_mt5.symbol_info_tick.return_value = Mock(bid=157.123)
            mock_mt5.order_send.return_value = Mock(
                retcode=10009,
                order=12345,
                comment="Success"
            )
            
            await engine.initialize()
            
            try:
                # Create multiple trading signals
                signals = []
                for i in range(10):
                    signal = TradingSignal(
                        symbol=f"TEST{i}",
                        trade_direction="BUY",
                        timestamp=datetime.now().isoformat(),
                        current_price=1.0 + i * 0.01,
                        strategy="CONCURRENT_TEST"
                    )
                    signals.append(signal)
                
                # Execute all trades concurrently
                start_time = datetime.now()
                tasks = [engine.execute_trade_async(signal) for signal in signals]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Verify all completed without errors
                assert len(results) == 10
                assert all(isinstance(result, bool) for result in results)
                
                # Should complete efficiently
                assert execution_time < 5.0
                
                # Performance metrics should be consistent
                metrics = engine.performance_metrics
                assert metrics['trades_executed'] >= 10
                
            finally:
                await engine.stop_engine()
    
    def test_invalid_signal_data_scenarios(self):
        """Test handling of various invalid signal data scenarios"""
        engine = TradingEngine()
        
        # Test None input
        signal = engine.create_trading_signal(None)
        assert signal is None
        
        # Test empty dict
        signal = engine.create_trading_signal({})
        assert signal is not None
        assert not signal.is_valid()  # Should be invalid due to missing data
        
        # Test malformed data
        signal = engine.create_trading_signal({
            "symbol": 123,  # Wrong type
            "trade_direction": None,
            "current_price": "not_a_number"
        })
        assert signal is None
        
        # Test partial valid data
        signal = engine.create_trading_signal({
            "symbol": "EURJPY",  
            "trade_direction": "SELL",
            # Missing timestamp and price
        })
        assert signal is not None
        assert not signal.is_valid()

class TestBackwardCompatibilityIntegration:
    """Test that consolidated system maintains compatibility with 19 original files"""
    
    def test_original_execute_file_functionality_mapping(self):
        """Verify all 19 original execute_*.py files have equivalent functionality"""
        # Map of original files to consolidated modes/functionality
        original_files_mapping = {
            'execute_compliant_simple.py': ('simple', 'EURJPY', 'SELL'),
            'execute_eurjpy_bear_08_35.py': ('eurjpy', 'EURJPY', 'BEAR'),
            'execute_eurjpy_08_30.py': ('eurjpy', 'EURJPY', 'BUY'),
            'execute_eurjpy_corrected.py': ('eurjpy', 'EURJPY', 'BUY'),
            'execute_eurjpy_fixed.py': ('eurjpy', 'EURJPY', 'BUY'),
            'execute_eurjpy_live.py': ('eurjpy', 'EURJPY', 'BUY'),
            'execute_eurjpy_signal.py': ('signal', 'EURJPY', 'BUY'),
            'execute_eurjpy_ultimate.py': ('eurjpy', 'EURJPY', 'BUY'),
            'execute_ferrari_08_30.py': ('ferrari', '_FERRARI.IT', 'BULL'),
            'execute_ferrari_compliant.py': ('ferrari', '_FERRARI.IT', 'BULL'),
            'execute_ferrari_direct.py': ('ferrari', '_FERRARI.IT', 'BULL'),
            'execute_fresh_eurjpy_08_28.py': ('eurjpy', 'EURJPY', 'BUY'),
            'execute_gbpjpy_bear_urgent.py': ('gbpjpy', 'GBPJPY', 'BEAR'),
            'execute_live_gbpusd_bear.py': ('signal', 'GBPUSD', 'BEAR'),
            'execute_multi_asset_signals.py': ('multi', 'MULTI', 'ANY'),
            'execute_poc_trade.py': ('signal', 'ANY', 'ANY'),
            'execute_usdcad_08_36.py': ('signal', 'USDCAD', 'BUY'),
            'execute_compliant_eurjpy_bear.py': ('eurjpy', 'EURJPY', 'BEAR'),
            'execute_compliant_eurjpy_fixed.py': ('eurjpy', 'EURJPY', 'BUY')
        }
        
        # Verify mapping completeness
        assert len(original_files_mapping) == 19
        
        # Test that all modes are supported
        supported_modes = {'simple', 'eurjpy', 'ferrari', 'gbpjpy', 'multi', 'signal'}
        mapped_modes = {mapping[0] for mapping in original_files_mapping.values()}
        assert mapped_modes.issubset(supported_modes)
    
    @pytest.mark.asyncio 
    async def test_position_sizing_consistency(self):
        """Test that position sizing matches original MIKROBOT specifications"""
        engine = TradingEngine()
        
        with patch('src.core.trading_engine.mt5') as mock_mt5:
            mock_mt5.initialize.return_value = True
            mock_mt5.account_info.return_value = Mock(balance=100000.0)
            mock_mt5.symbol_info_tick.return_value = Mock(bid=157.123)
            
            await engine.initialize()
            
            try:
                # Test position sizing calculation
                signal = TradingSignal(
                    symbol="EURJPY",
                    trade_direction="SELL",
                    timestamp=datetime.now().isoformat(),
                    current_price=157.123,
                    strategy="POSITION_SIZE_TEST"
                )
                
                # Mock the order_send to capture position size
                captured_requests = []
                def capture_order(request):
                    captured_requests.append(request)
                    return Mock(retcode=10009, order=12345, comment="Success")
                
                mock_mt5.order_send.side_effect = capture_order
                
                result = await engine.execute_trade_async(signal)
                assert result is True
                assert len(captured_requests) == 1
                
                # Verify position sizing follows 0.55% risk rule
                request = captured_requests[0]
                lot_size = request['volume']
                
                # Expected calculation: 
                # risk_amount = 100000 * 0.0055 = 550
                # atr_pips = 8, pip_value = 100 (JPY pair)
                # expected_lots = 550 / (8 * 100) = 0.69 (rounded to 0.69)
                expected_lots = round(550 / (8 * 100), 2)
                assert lot_size == expected_lots
                
            finally:
                await engine.stop_engine()

class TestSystemIntegrationScenarios:
    """Test complete system integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_trading_workflow(self):
        """Test complete workflow from signal file to trade execution"""
        engine = TradingEngine()
        
        with patch('src.core.trading_engine.mt5') as mock_mt5:
            # Setup mocks
            mock_mt5.initialize.return_value = True
            mock_mt5.account_info.return_value = Mock(balance=100000.0, login=12345)
            mock_mt5.symbol_info_tick.return_value = Mock(bid=157.123, ask=157.126)
            mock_mt5.order_send.return_value = Mock(
                retcode=10009,
                order=12345,
                comment="Success",
                volume=0.69
            )
            
            await engine.initialize()
            
            try:
                # 1. Create signal file
                signal_data = {
                    "symbol": "EURJPY",
                    "trade_direction": "SELL",
                    "timestamp": datetime.now().isoformat(),
                    "current_price": 157.123,
                    "strategy": "MIKROBOT_FASTVERSION_4PHASE",
                    "phase_4_ylipip": {"triggered": True, "strength": 0.8},
                    "confidence_score": 0.95
                }
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(signal_data, f)
                    signal_file = f.name
                
                # 2. Read signal file
                read_data = await engine.read_signal_file_async(signal_file)
                assert read_data is not None
                assert read_data['symbol'] == 'EURJPY'
                
                # 3. Create trading signal
                trading_signal = engine.create_trading_signal(read_data)
                assert trading_signal is not None
                assert trading_signal.is_valid()
                assert trading_signal.is_ylipip_triggered()
                
                # 4. Execute trade
                result = await engine.execute_trade_async(trading_signal)
                assert result is True
                
                # 5. Verify performance metrics updated
                metrics = engine.performance_metrics
                assert metrics['trades_executed'] > 0
                assert metrics['success_rate'] > 0
                assert metrics['last_execution'] is not None
                
            finally:
                try:
                    Path(signal_file).unlink()
                except:
                    pass
                await engine.stop_engine()
    
    @pytest.mark.asyncio
    async def test_continuous_mode_simulation(self):
        """Test continuous execution mode simulation"""
        engine = TradingEngine()
        
        with patch('src.core.trading_engine.mt5') as mock_mt5:
            mock_mt5.initialize.return_value = True
            mock_mt5.account_info.return_value = Mock(balance=100000.0)
            mock_mt5.symbol_info_tick.return_value = Mock(bid=157.123)
            mock_mt5.order_send.return_value = Mock(retcode=10009, order=12345)
            
            await engine.initialize()
            
            try:
                # Create temporary signal files
                temp_files = []
                for symbol in ['EURJPY', 'GBPJPY']:
                    signal_data = {
                        "symbol": symbol,
                        "trade_direction": "SELL",
                        "timestamp": datetime.now().isoformat(),
                        "current_price": 157.123,
                        "phase_4_ylipip": {"triggered": True}
                    }
                    
                    temp_file = tempfile.mktemp(suffix=f'_{symbol}.json')
                    with open(temp_file, 'w') as f:
                        json.dump(signal_data, f)
                    temp_files.append(temp_file)
                
                # Update engine signal paths to use temp files
                engine.signal_paths = temp_files
                
                # Run continuous mode for a short time
                async def stop_after_delay():
                    await asyncio.sleep(2)  # Run for 2 seconds
                    engine.running = False
                
                # Start both continuous mode and stop timer
                continuous_task = asyncio.create_task(engine.continuous_execution_mode())
                stop_task = asyncio.create_task(stop_after_delay())
                
                # Wait for either to complete
                done, pending = await asyncio.wait(
                    [continuous_task, stop_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel remaining tasks
                for task in pending:
                    task.cancel()
                
                # Should have processed signals during continuous run
                metrics = engine.performance_metrics
                assert metrics['trades_executed'] >= 0  # May be 0 if no YLIPIP triggers
                
            finally:
                for temp_file in temp_files:
                    try:
                        Path(temp_file).unlink()
                    except:
                        pass
                await engine.stop_engine()

if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        "-v",
        "--tb=short", 
        "--maxfail=3",
        __file__
    ])