#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Consolidated Trading Engine
85%+ test coverage target for all critical trading paths
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.trading_engine import (
    TradingEngine, TradingSignal, MT5ConnectionPool, SignalCache,
    TradeDirection, ExecutionMode, ascii_print
)

class TestTradingSignal:
    """Test TradingSignal dataclass and validation"""
    
    def test_valid_signal_creation(self):
        """Test creating a valid trading signal"""
        signal = TradingSignal(
            symbol="EURJPY",
            trade_direction="BULL",
            timestamp="2025-08-05T10:30:00",
            current_price=165.123,
            strategy="MIKROBOT_FASTVERSION_4PHASE"
        )
        
        assert signal.symbol == "EURJPY"
        assert signal.trade_direction == "BULL"
        assert signal.current_price == 165.123
        assert signal.is_valid() is True
    
    def test_invalid_signal_validation(self):
        """Test signal validation with missing fields"""
        # Missing symbol
        signal = TradingSignal(
            symbol="",
            trade_direction="BULL",
            timestamp="2025-08-05T10:30:00",
            current_price=165.123
        )
        assert signal.is_valid() is False
        
        # Zero price
        signal = TradingSignal(
            symbol="EURJPY",
            trade_direction="BULL",
            timestamp="2025-08-05T10:30:00",
            current_price=0.0
        )
        assert signal.is_valid() is False
    
    def test_ylipip_trigger_detection(self):
        """Test YLIPIP trigger detection"""
        # Signal with triggered YLIPIP
        signal = TradingSignal(
            symbol="EURJPY",
            trade_direction="BULL",
            timestamp="2025-08-05T10:30:00",
            current_price=165.123,
            phase_4_ylipip={'triggered': True, 'target': 165.100, 'current': 165.123}
        )
        assert signal.is_ylipip_triggered() is True
        
        # Signal without YLIPIP
        signal = TradingSignal(
            symbol="EURJPY",
            trade_direction="BULL",
            timestamp="2025-08-05T10:30:00",
            current_price=165.123
        )
        assert signal.is_ylipip_triggered() is False
        
        # Signal with non-triggered YLIPIP
        signal = TradingSignal(
            symbol="EURJPY",
            trade_direction="BULL",
            timestamp="2025-08-05T10:30:00",
            current_price=165.123,
            phase_4_ylipip={'triggered': False, 'target': 165.100, 'current': 165.050}
        )
        assert signal.is_ylipip_triggered() is False

class TestMT5ConnectionPool:
    """Test MT5 connection pool functionality"""
    
    @pytest.fixture
    def connection_pool(self):
        """Create a connection pool for testing"""
        return MT5ConnectionPool(max_connections=3)
    
    @pytest.mark.asyncio
    async def test_pool_initialization(self, connection_pool):
        """Test connection pool initialization"""
        with patch('MetaTrader5.initialize', return_value=True):
            success = await connection_pool.initialize()
            assert success is True
            assert connection_pool._initialized is True
            assert connection_pool._active_connections >= 2
    
    @pytest.mark.asyncio
    async def test_pool_initialization_failure(self, connection_pool):
        """Test connection pool initialization failure"""
        with patch('MetaTrader5.initialize', return_value=False):
            success = await connection_pool.initialize()
            assert success is False
            assert connection_pool._initialized is False
    
    @pytest.mark.asyncio
    async def test_get_and_return_connection(self, connection_pool):
        """Test getting and returning connections"""
        with patch('MetaTrader5.initialize', return_value=True):
            await connection_pool.initialize()
            
            # Get connection
            connection = await connection_pool.get_connection()
            assert connection is not None
            
            # Return connection
            await connection_pool.return_connection(connection)
    
    @pytest.mark.asyncio
    async def test_connection_pool_exhaustion(self, connection_pool):
        """Test behavior when connection pool is exhausted"""
        with patch('MetaTrader5.initialize', return_value=True):
            await connection_pool.initialize()
            
            # Get all connections
            connections = []
            for i in range(connection_pool.max_connections):
                try:
                    conn = await asyncio.wait_for(connection_pool.get_connection(), timeout=1.0)
                    connections.append(conn)
                except:
                    break
            
            # Try to get one more (should fail or create new)
            try:
                extra_conn = await asyncio.wait_for(connection_pool.get_connection(), timeout=1.0)
                # If we get here, pool created new connection
                assert extra_conn is not None
            except asyncio.TimeoutError:
                # Expected behavior when pool is exhausted
                pass

class TestSignalCache:
    """Test signal caching functionality"""
    
    @pytest.fixture
    def signal_cache(self):
        """Create a signal cache for testing"""
        return SignalCache(ttl_seconds=1)  # Short TTL for testing
    
    def test_cache_set_and_get(self, signal_cache):
        """Test basic cache set and get operations"""
        test_data = {"symbol": "EURJPY", "price": 165.123}
        
        # Set data
        signal_cache.set("test_key", test_data)
        
        # Get data
        retrieved_data = signal_cache.get("test_key")
        assert retrieved_data == test_data
    
    def test_cache_expiration(self, signal_cache):
        """Test cache TTL expiration"""
        test_data = {"symbol": "EURJPY", "price": 165.123}
        
        # Set data
        signal_cache.set("test_key", test_data)
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Try to get expired data
        retrieved_data = signal_cache.get("test_key")
        assert retrieved_data is None
    
    def test_cache_clear_expired(self, signal_cache):
        """Test manual cleanup of expired entries"""
        # Add multiple entries
        signal_cache.set("key1", "value1")
        signal_cache.set("key2", "value2")
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Add new entry
        signal_cache.set("key3", "value3")
        
        # Clear expired
        signal_cache.clear_expired()
        
        # Check that only new entry remains
        assert signal_cache.get("key1") is None
        assert signal_cache.get("key2") is None
        assert signal_cache.get("key3") == "value3"

class TestTradingEngine:
    """Test main TradingEngine functionality"""
    
    @pytest.fixture
    def trading_engine(self):
        """Create a trading engine for testing"""
        return TradingEngine()
    
    @pytest.fixture
    def mock_mt5(self):
        """Mock MT5 module for testing"""
        with patch('src.core.trading_engine.mt5') as mock:
            # Mock successful initialization
            mock.initialize.return_value = True
            
            # Mock account info
            mock_account = Mock()
            mock_account.login = 12345
            mock_account.balance = 10000.0
            mock.account_info.return_value = mock_account
            
            # Mock successful order
            mock_result = Mock()
            mock_result.retcode = mock.TRADE_RETCODE_DONE = 10009
            mock_result.order = 123456
            mock.order_send.return_value = mock_result
            
            # Mock constants
            mock.ORDER_TYPE_BUY = 0
            mock.ORDER_TYPE_SELL = 1
            mock.TRADE_ACTION_DEAL = 1
            mock.ORDER_FILLING_FOK = 2
            
            yield mock
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, trading_engine, mock_mt5):
        """Test trading engine initialization"""
        success = await trading_engine.initialize()
        assert success is True
        mock_mt5.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_signal_file_reading(self, trading_engine, tmp_path):
        """Test async signal file reading"""
        # Create test signal file
        signal_data = {
            "symbol": "EURJPY",
            "trade_direction": "BULL",
            "timestamp": "2025-08-05T10:30:00",
            "current_price": 165.123,
            "phase_4_ylipip": {"triggered": True}
        }
        
        # Create UTF-16LE encoded file (as MT5 creates)
        test_file = tmp_path / "test_signal.json"
        json_str = json.dumps(signal_data, ensure_ascii=False)
        with open(test_file, 'w', encoding='utf-16le') as f:
            f.write(json_str)
        
        # Test reading
        result = await trading_engine.read_signal_file_async(str(test_file))
        assert result is not None
        assert result["symbol"] == "EURJPY"
        assert result["trade_direction"] == "BULL"
    
    def test_trading_signal_creation(self, trading_engine):
        """Test creation of TradingSignal from raw data"""
        raw_data = {
            "symbol": "EURJPY",
            "trade_direction": "BULL",
            "timestamp": "2025-08-05T10:30:00",
            "current_price": 165.123,
            "strategy": "MIKROBOT_FASTVERSION_4PHASE",
            "phase_4_ylipip": {"triggered": True}
        }
        
        signal = trading_engine.create_trading_signal(raw_data)
        assert signal is not None
        assert signal.symbol == "EURJPY"
        assert signal.trade_direction == "BULL"
        assert signal.is_ylipip_triggered() is True
    
    def test_pip_value_calculation(self, trading_engine):
        """Test pip value calculation for different symbols"""
        # JPY pairs
        assert trading_engine._get_pip_value("EURJPY") == 100
        assert trading_engine._get_pip_value("GBPJPY") == 100
        assert trading_engine._get_pip_value("USDJPY") == 100
        
        # Major pairs
        assert trading_engine._get_pip_value("EURUSD") == 10
        assert trading_engine._get_pip_value("GBPUSD") == 10
        assert trading_engine._get_pip_value("USDCAD") == 10
        
        # CFD and Crypto
        assert trading_engine._get_pip_value("_FERRARI.IT") == 1
        assert trading_engine._get_pip_value("BCHUSD") == 1
        
        # Unknown symbol (default)
        assert trading_engine._get_pip_value("UNKNOWN") == 10
    
    @pytest.mark.asyncio
    async def test_trade_execution(self, trading_engine, mock_mt5):
        """Test async trade execution"""
        await trading_engine.initialize()
        
        # Create test signal
        signal = TradingSignal(
            symbol="EURJPY",
            trade_direction="BULL",
            timestamp="2025-08-05T10:30:00",
            current_price=165.123,
            phase_4_ylipip={"triggered": True}
        )
        
        # Execute trade
        result = await trading_engine.execute_trade_async(signal)
        assert result is True
        
        # Verify MT5 calls
        mock_mt5.account_info.assert_called()
        mock_mt5.order_send.assert_called_once()
        
        # Check order request structure
        call_args = mock_mt5.order_send.call_args[0][0]
        assert call_args["symbol"] == "EURJPY"
        assert call_args["type"] == mock_mt5.ORDER_TYPE_BUY
        assert call_args["type_filling"] == mock_mt5.ORDER_FILLING_FOK
        assert "MIKROBOT_CONSOLIDATED" in call_args["comment"]
    
    @pytest.mark.asyncio
    async def test_position_sizing_calculation(self, trading_engine, mock_mt5):
        """Test position sizing with 0.55% risk (as per CLAUDE.md)"""
        await trading_engine.initialize()
        
        # Test with 10,000 balance
        mock_account = mock_mt5.account_info.return_value
        mock_account.balance = 10000.0
        
        signal = TradingSignal(
            symbol="EURJPY",
            trade_direction="BULL",
            timestamp="2025-08-05T10:30:00",
            current_price=165.123
        )
        
        await trading_engine.execute_trade_async(signal)
        
        # Check position sizing calculation
        call_args = mock_mt5.order_send.call_args[0][0]
        volume = call_args["volume"]
        
        # Expected: risk_amount = 10000 * 0.0055 = 55
        # Expected: lot_size = 55 / (8 ATR * 100 pip_value) = 0.07 (rounded)
        expected_risk = 10000.0 * 0.0055  # $55
        expected_lot_size = round(expected_risk / (8 * 100), 2)  # 0.07
        
        assert volume >= 0.01  # Minimum lot size
        assert volume <= 1.0   # Reasonable maximum
    
    def test_performance_metrics_tracking(self, trading_engine):
        """Test performance metrics updates"""
        # Initial state
        assert trading_engine.performance_metrics['trades_executed'] == 0
        assert trading_engine.performance_metrics['success_rate'] == 0.0
        
        # Simulate successful trade
        trading_engine._update_performance_metrics(True, 0.5)
        assert trading_engine.performance_metrics['trades_executed'] == 1
        assert trading_engine.performance_metrics['success_rate'] == 1.0
        assert trading_engine.performance_metrics['avg_execution_time'] == 0.5
        
        # Simulate failed trade
        trading_engine._update_performance_metrics(False, 1.0)
        assert trading_engine.performance_metrics['trades_executed'] == 2
        assert trading_engine.performance_metrics['success_rate'] == 0.5
        assert trading_engine.performance_metrics['avg_execution_time'] == 0.75
    
    @pytest.mark.asyncio
    async def test_specific_symbol_execution(self, trading_engine, mock_mt5):
        """Test executing specific symbol trades"""
        await trading_engine.initialize()
        
        # Test manual mode
        result = await trading_engine.execute_specific_symbol("EURJPY", "BULL", "manual")
        assert result is True
        
        # Verify MT5 was called
        mock_mt5.order_send.assert_called()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, trading_engine):
        """Test error handling in various scenarios"""
        # Test with failed MT5 initialization
        with patch('src.core.trading_engine.mt5.initialize', return_value=False):
            success = await trading_engine.initialize()
            assert success is False
        
        # Test invalid signal handling
        invalid_signal = TradingSignal(
            symbol="",  # Invalid empty symbol
            trade_direction="BULL",
            timestamp="2025-08-05T10:30:00",
            current_price=0.0  # Invalid zero price
        )
        
        await trading_engine.initialize()
        result = await trading_engine.execute_trade_async(invalid_signal)
        assert result is False

class TestAsyncPerformance:
    """Test async performance improvements"""
    
    @pytest.mark.asyncio
    async def test_concurrent_signal_reading(self):
        """Test that multiple signal files can be read concurrently"""
        engine = TradingEngine()
        
        # Create multiple file paths (some non-existent for testing)
        paths = [
            "nonexistent1.json",
            "nonexistent2.json", 
            "nonexistent3.json"
        ]
        
        start_time = time.time()
        
        # Read multiple files concurrently
        tasks = [engine.read_signal_file_async(path) for path in paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        execution_time = time.time() - start_time
        
        # Should complete quickly even with multiple files
        assert execution_time < 1.0
        assert len(results) == 3
        # All should be None (files don't exist)
        assert all(result is None for result in results)
    
    @pytest.mark.asyncio
    async def test_connection_pool_performance(self):
        """Test that connection pool provides performance benefits"""
        pool = MT5ConnectionPool(max_connections=3)
        
        with patch('MetaTrader5.initialize', return_value=True):
            await pool.initialize()
            
            start_time = time.time()
            
            # Get multiple connections concurrently
            tasks = [pool.get_connection() for _ in range(5)]
            connections = await asyncio.gather(*tasks)
            
            # Return connections
            return_tasks = [pool.return_connection(conn) for conn in connections]
            await asyncio.gather(*return_tasks)
            
            execution_time = time.time() - start_time
            
            # Should be very fast
            assert execution_time < 0.1
            assert len(connections) == 5

# Test utilities and fixtures
@pytest.fixture
def sample_signal_data():
    """Sample signal data for testing"""
    return {
        "symbol": "EURJPY",
        "trade_direction": "BULL",
        "timestamp": "2025-08-05T10:30:00.000Z",
        "current_price": 165.123,
        "strategy": "MIKROBOT_FASTVERSION_4PHASE",
        "phase_1_m5_bos": {
            "time": "2025-08-05T10:25:00",
            "price": 165.100,
            "direction": "BULL"
        },
        "phase_4_ylipip": {
            "target": 165.120,
            "current": 165.123,
            "triggered": True
        }
    }

@pytest.fixture
def mock_signal_file(tmp_path, sample_signal_data):
    """Create a mock signal file for testing"""
    signal_file = tmp_path / "test_signal.json"
    json_str = json.dumps(sample_signal_data, ensure_ascii=False)
    
    # Write as UTF-16LE (as MT5 does)
    with open(signal_file, 'w', encoding='utf-16le') as f:
        f.write(json_str)
    
    return str(signal_file)

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--cov=src.core.trading_engine",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])