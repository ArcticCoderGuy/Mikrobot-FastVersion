#!/usr/bin/env python3
"""
TEST CONFIGURATION AND FIXTURES
Provides shared test fixtures, mock data generators, and test utilities
for the consolidated trading engine test suite
"""

import pytest
import asyncio
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.trading_engine import TradingEngine, TradingSignal, MT5ConnectionPool, SignalCache

class MockMT5:
    """Comprehensive MT5 mock for testing"""
    
    # MT5 Constants
    TRADE_RETCODE_DONE = 10009
    TRADE_RETCODE_INVALID = 10013
    TRADE_RETCODE_INVALID_VOLUME = 10014
    TRADE_RETCODE_INSUFFICIENT_FUNDS = 10019
    TRADE_RETCODE_MARKET_CLOSED = 10018
    
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    ORDER_FILLING_FOK = 0
    ORDER_FILLING_IOC = 1
    ORDER_FILLING_RETURN = 2
    TRADE_ACTION_DEAL = 1
    TRADE_ACTION_SLTP = 2
    
    def __init__(self):
        self.initialized = False
        self.account_balance = 100000.0
        self.account_login = 12345
        self.connection_failures = 0
        self.order_failures = 0
        self.simulate_failures = False
        
        # Track calls for verification
        self.initialize_calls = 0
        self.account_info_calls = 0
        self.order_send_calls = 0
        self.symbol_info_calls = 0
        
        # Position tracking
        self.open_positions = {}
        self.order_counter = 10000
    
    def reset_stats(self):
        """Reset call counters and failure simulation"""
        self.initialize_calls = 0
        self.account_info_calls = 0
        self.order_send_calls = 0
        self.symbol_info_calls = 0
        self.connection_failures = 0
        self.order_failures = 0
        self.simulate_failures = False
        self.open_positions = {}
    
    def enable_failure_simulation(self, connection_failures: int = 1, order_failures: int = 1):
        """Enable failure simulation for testing error handling"""
        self.simulate_failures = True
        self.connection_failures = connection_failures
        self.order_failures = order_failures
    
    def initialize(self):
        """Mock MT5 initialization"""
        self.initialize_calls += 1
        
        if self.simulate_failures and self.connection_failures > 0:
            self.connection_failures -= 1
            return False
        
        self.initialized = True
        return True
    
    def shutdown(self):
        """Mock MT5 shutdown"""
        self.initialized = False
    
    def account_info(self):
        """Mock account information"""
        self.account_info_calls += 1
        
        if not self.initialized:
            return None
        
        return Mock(
            balance=self.account_balance,
            login=self.account_login,
            equity=self.account_balance * 1.05,  # 5% unrealized profit
            margin=self.account_balance * 0.1,   # 10% margin used
            free_margin=self.account_balance * 0.9
        )
    
    def symbol_info_tick(self, symbol: str):
        """Mock symbol tick information"""
        self.symbol_info_calls += 1
        
        if not self.initialized:
            return None
        
        # Symbol-specific tick data
        tick_data = {
            'EURJPY': {'bid': 157.123, 'ask': 157.126, 'spread': 0.003},
            'EURUSD': {'bid': 1.0995, 'ask': 1.1005, 'spread': 0.001},
            'GBPJPY': {'bid': 187.456, 'ask': 187.459, 'spread': 0.003},
            '_FERRARI.IT': {'bid': 123.45, 'ask': 123.47, 'spread': 0.02},
            'BCHUSD': {'bid': 234.56, 'ask': 234.58, 'spread': 0.02},
            'USDCAD': {'bid': 1.3456, 'ask': 1.3458, 'spread': 0.0002},
            'GBPUSD': {'bid': 1.2543, 'ask': 1.2545, 'spread': 0.0002}
        }
        
        data = tick_data.get(symbol, {'bid': 1.0, 'ask': 1.001, 'spread': 0.001})
        
        return Mock(
            bid=data['bid'],
            ask=data['ask'],
            time=int(datetime.now().timestamp()),
            flags=0
        )
    
    def symbol_info(self, symbol: str):
        """Mock symbol information"""
        if not self.initialized:
            return None
        
        # Symbol-specific info
        symbol_info = {
            'EURJPY': {'digits': 3, 'point': 0.001, 'volume_min': 0.01, 'volume_max': 100.0},
            'EURUSD': {'digits': 5, 'point': 0.00001, 'volume_min': 0.01, 'volume_max': 100.0},
            'GBPJPY': {'digits': 3, 'point': 0.001, 'volume_min': 0.01, 'volume_max': 100.0},
            '_FERRARI.IT': {'digits': 2, 'point': 0.01, 'volume_min': 1.0, 'volume_max': 1000.0},
            'BCHUSD': {'digits': 2, 'point': 0.01, 'volume_min': 0.01, 'volume_max': 100.0}
        }
        
        info = symbol_info.get(symbol, {'digits': 5, 'point': 0.00001, 'volume_min': 0.01, 'volume_max': 100.0})
        
        return Mock(
            digits=info['digits'],
            point=info['point'],
            volume_min=info['volume_min'],
            volume_max=info['volume_max'],
            volume_step=0.01,
            trade_tick_value=10.0,
            trade_tick_size=info['point']
        )
    
    def order_send(self, request: Dict[str, Any]):
        """Mock order sending"""
        self.order_send_calls += 1
        self.order_counter += 1
        
        if not self.initialized:
            return Mock(
                retcode=self.TRADE_RETCODE_INVALID,
                comment="Not initialized"
            )
        
        # Simulate order failures
        if self.simulate_failures and self.order_failures > 0:
            self.order_failures -= 1
            return Mock(
                retcode=self.TRADE_RETCODE_INVALID_VOLUME,
                comment="Invalid volume",
                order=0
            )
        
        # Validate request
        if not request.get('symbol') or not request.get('volume'):
            return Mock(
                retcode=self.TRADE_RETCODE_INVALID,
                comment="Invalid request"
            )
        
        volume = request.get('volume', 0.01)
        symbol = request.get('symbol', 'UNKNOWN')
        
        # Check volume limits
        symbol_info = self.symbol_info(symbol)
        if volume < symbol_info.volume_min or volume > symbol_info.volume_max:
            return Mock(
                retcode=self.TRADE_RETCODE_INVALID_VOLUME,
                comment=f"Invalid volume: {volume}"
            )
        
        # Check sufficient funds (simplified)
        required_margin = volume * 1000  # Simplified calculation
        if required_margin > self.account_balance * 0.9:
            return Mock(
                retcode=self.TRADE_RETCODE_INSUFFICIENT_FUNDS,
                comment="Insufficient funds"
            )
        
        # Success case
        tick = self.symbol_info_tick(symbol)
        fill_price = tick.ask if request.get('type') == self.ORDER_TYPE_BUY else tick.bid
        
        # Track position
        self.open_positions[self.order_counter] = {
            'symbol': symbol,
            'volume': volume,
            'type': request.get('type'),
            'open_price': fill_price,
            'timestamp': datetime.now()
        }
        
        return Mock(
            retcode=self.TRADE_RETCODE_DONE,
            order=self.order_counter,
            deal=self.order_counter + 50000,
            volume=volume,
            price=fill_price,
            comment="Success",
            request_id=0
        )
    
    def positions_get(self, symbol: Optional[str] = None):
        """Mock positions retrieval"""
        if not self.initialized:
            return []
        
        positions = []
        for ticket, pos_data in self.open_positions.items():
            if symbol and pos_data['symbol'] != symbol:
                continue
            
            # Calculate current P&L (simplified)
            tick = self.symbol_info_tick(pos_data['symbol'])
            current_price = tick.bid if pos_data['type'] == self.ORDER_TYPE_BUY else tick.ask
            profit = (current_price - pos_data['open_price']) * pos_data['volume'] * 100
            
            positions.append(Mock(
                ticket=ticket,
                symbol=pos_data['symbol'],
                volume=pos_data['volume'],
                type=pos_data['type'],
                price_open=pos_data['open_price'],
                price_current=current_price,
                profit=profit,
                time=int(pos_data['timestamp'].timestamp())
            ))
        
        return positions

# Global mock instance
mock_mt5 = MockMT5()

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment with mocked MT5"""
    # Mock MetaTrader5 module
    sys.modules['MetaTrader5'] = mock_mt5
    yield
    # Cleanup after tests
    if 'MetaTrader5' in sys.modules:
        del sys.modules['MetaTrader5']

@pytest.fixture
def clean_mock_mt5():
    """Provide clean MT5 mock for each test"""
    mock_mt5.reset_stats()
    yield mock_mt5

@pytest.fixture
async def trading_engine():
    """Provide initialized trading engine for tests"""
    engine = TradingEngine()
    success = await engine.initialize()
    assert success, "Failed to initialize trading engine"
    
    yield engine
    
    # Cleanup
    await engine.stop_engine()

@pytest.fixture
async def connection_pool():
    """Provide MT5 connection pool for tests"""
    pool = MT5ConnectionPool(max_connections=3)
    success = await pool.initialize()
    assert success, "Failed to initialize connection pool"
    
    yield pool

@pytest.fixture
def signal_cache():
    """Provide signal cache for tests"""
    return SignalCache(ttl_seconds=30)

@pytest.fixture
def sample_trading_signals():
    """Generate sample trading signals for testing"""
    signals = []
    
    # EURJPY SELL signal
    signals.append(TradingSignal(
        symbol="EURJPY",
        trade_direction="SELL",
        timestamp=datetime.now().isoformat(),
        current_price=157.123,
        strategy="MIKROBOT_4PHASE",
        phase_4_ylipip={"triggered": True, "strength": 0.8},
        confidence_score=0.9
    ))
    
    # Ferrari CFD BUY signal
    signals.append(TradingSignal(
        symbol="_FERRARI.IT",
        trade_direction="BUY",
        timestamp=datetime.now().isoformat(),
        current_price=123.45,
        strategy="CFD_MOMENTUM",
        confidence_score=0.75
    ))
    
    # GBPJPY BEAR signal
    signals.append(TradingSignal(
        symbol="GBPJPY",
        trade_direction="BEAR",
        timestamp=datetime.now().isoformat(),
        current_price=187.456,
        strategy="HANSEI_4PHASE",
        phase_4_ylipip={"triggered": True, "strength": 0.9},
        confidence_score=0.95
    ))
    
    # Crypto signal
    signals.append(TradingSignal(
        symbol="BCHUSD",
        trade_direction="BUY",
        timestamp=datetime.now().isoformat(),
        current_price=234.56,
        strategy="CRYPTO_BREAKOUT",
        confidence_score=0.8
    ))
    
    return signals

@pytest.fixture
def sample_signal_files(tmp_path):
    """Create temporary signal files for testing"""
    signal_files = []
    
    # EURJPY signal file
    eurjpy_data = {
        "symbol": "EURJPY",
        "trade_direction": "SELL",
        "timestamp": datetime.now().isoformat(),
        "current_price": 157.123,
        "strategy": "MIKROBOT_4PHASE",
        "phase_4_ylipip": {"triggered": True, "strength": 0.8},
        "confidence_score": 0.9
    }
    
    eurjpy_file = tmp_path / "eurjpy_signal.json"
    with open(eurjpy_file, 'w') as f:
        json.dump(eurjpy_data, f)
    signal_files.append(str(eurjpy_file))
    
    # Ferrari signal file
    ferrari_data = {
        "symbol": "_FERRARI.IT",
        "trade_direction": "BUY",
        "timestamp": datetime.now().isoformat(),
        "current_price": 123.45,
        "strategy": "CFD_MOMENTUM",
        "confidence_score": 0.75
    }
    
    ferrari_file = tmp_path / "ferrari_signal.json"
    with open(ferrari_file, 'w') as f:
        json.dump(ferrari_data, f)
    signal_files.append(str(ferrari_file))
    
    # Multi-asset signal file
    multi_data = {
        "symbol": "GBPJPY",
        "trade_direction": "BEAR",
        "timestamp": datetime.now().isoformat(),
        "current_price": 187.456,
        "phase_4_ylipip": {"triggered": True, "strength": 0.9}
    }
    
    multi_file = tmp_path / "multi_signal.json"
    with open(multi_file, 'w') as f:
        json.dump(multi_data, f)
    signal_files.append(str(multi_file))
    
    return signal_files

@pytest.fixture
def hansei_signal_data():
    """Complete Hansei 4-phase signal data"""
    return {
        "symbol": "EURJPY",
        "trade_direction": "SELL",
        "timestamp": datetime.now().isoformat(),
        "current_price": 157.123,
        "strategy": "HANSEI_4PHASE",
        "phase_1_bos": {
            "completed": True,
            "timestamp": "2025-01-01T10:00:00",
            "price": 157.200,
            "strength": 0.85
        },
        "phase_2_break": {
            "completed": True,
            "timestamp": "2025-01-01T10:05:00",
            "price": 157.100,
            "candles": 4,
            "strength": 0.9
        },
        "phase_3_retest": {
            "completed": True,
            "timestamp": "2025-01-01T10:10:00",
            "price": 157.150,
            "confirmed": True,
            "strength": 0.8
        },
        "phase_4_ylipip": {
            "triggered": True,
            "timestamp": "2025-01-01T10:15:00",
            "trigger_price": 157.123,
            "movement_pips": 0.6,
            "strength": 0.95
        },
        "atr_pips": 8.5,
        "confidence_score": 0.95,
        "risk_reward_ratio": 2.5,
        "stop_loss": 157.200,
        "take_profit": 156.950
    }

@pytest.fixture
def invalid_signal_data():
    """Various invalid signal data scenarios for testing"""
    return [
        # Missing symbol
        {
            "trade_direction": "BUY",
            "timestamp": datetime.now().isoformat(),
            "current_price": 1.1000
        },
        # Missing trade direction
        {
            "symbol": "EURUSD",
            "timestamp": datetime.now().isoformat(),
            "current_price": 1.1000
        },
        # Invalid price
        {
            "symbol": "EURUSD",
            "trade_direction": "BUY",
            "timestamp": datetime.now().isoformat(),
            "current_price": 0.0
        },
        # Empty strings
        {
            "symbol": "",
            "trade_direction": "",
            "timestamp": "",
            "current_price": 0.0
        },
        # Wrong data types
        {
            "symbol": 123,
            "trade_direction": None,
            "timestamp": 456,
            "current_price": "not_a_number"
        }
    ]

# Test utility functions
def create_test_signal_file(file_path: str, signal_data: Dict[str, Any], encoding: str = 'utf-8') -> None:
    """Create a test signal file with specified encoding"""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    content = json.dumps(signal_data, ensure_ascii=True)
    
    if encoding == 'utf-16le':
        # Simulate actual MT5 signal file format
        encoded_content = content.encode('utf-16le') + b'\x00\x00'
        with open(file_path, 'wb') as f:
            f.write(encoded_content)
    else:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)

def assert_signal_valid(signal: TradingSignal) -> None:
    """Assert that a trading signal is valid"""
    assert signal is not None, "Signal should not be None"
    assert signal.is_valid(), f"Signal should be valid: {signal}"
    assert signal.symbol, "Signal should have a symbol"
    assert signal.trade_direction, "Signal should have a trade direction"
    assert signal.current_price > 0, "Signal should have a positive price"

def assert_performance_improvement(old_time: float, new_time: float, min_improvement: float = 30.0) -> None:
    """Assert that performance improvement meets minimum threshold"""
    improvement = ((old_time - new_time) / old_time) * 100
    assert improvement >= min_improvement, f"Performance improvement {improvement:.1f}% < {min_improvement}%"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Async test utilities
async def wait_for_condition(condition_func, timeout: float = 1.0, interval: float = 0.1):
    """Wait for a condition to become true"""
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < timeout:
        if condition_func():
            return True
        await asyncio.sleep(interval)
    
    return False

# Performance testing utilities
class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.elapsed_ms = 0
    
    def __enter__(self):
        self.start_time = asyncio.get_event_loop().time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = asyncio.get_event_loop().time()
        self.elapsed_ms = (self.end_time - self.start_time) * 1000

@pytest.fixture
def performance_timer():
    """Provide performance timer for tests"""
    return PerformanceTimer

# Memory usage utilities
def get_memory_usage():
    """Get current memory usage in MB"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0

# Test markers
pytestmark = [
    pytest.mark.asyncio,  # All tests are async by default
]

# Configure asyncio for tests
@pytest.fixture(scope="session", autouse=True)
def configure_asyncio():
    """Configure asyncio for testing"""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Test categories
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow tests")

# Pytest collection modifiers
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add unit marker to unit tests
        if "test_unit" in item.nodeid or "/unit/" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to integration tests
        if "test_integration" in item.nodeid or "/integration/" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add performance marker to performance tests
        if "performance" in item.nodeid or "benchmark" in item.nodeid:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)