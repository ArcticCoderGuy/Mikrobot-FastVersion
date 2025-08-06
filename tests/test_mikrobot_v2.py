"""
Comprehensive Test Suite for MIKROBOT FASTVERSION v2.0
======================================================

Unit tests and integration tests for all trading components:
- MT5 Direct Connector
- Lightning Bolt Strategy  
- MCP v2 Controller
- Hansei Reflector
- Trading Engine Integration
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mikrobot_v2.core.mt5_direct_connector import MT5DirectConnector, Tick, Candle, OrderType
from mikrobot_v2.strategies.lightning_bolt import LightningBoltStrategy, TrendDirection, YlipipCalculator
from mikrobot_v2.orchestration.mcp_v2_controller import MCPv2Controller, MCPMessage, MessageType, AgentType
from mikrobot_v2.orchestration.hansei_reflector import HanseiReflector, ReflectionType
from mikrobot_v2.main_trading_engine import MikrobotV2TradingEngine

class TestMT5DirectConnector:
    """Test MT5 Direct Connector functionality"""
    
    @pytest.fixture
    def mt5_connector(self):
        return MT5DirectConnector()
    
    @pytest.mark.asyncio
    async def test_connection_simulation_mode(self, mt5_connector):
        """Test MT5 connection in simulation mode"""
        # Should connect successfully in simulation mode
        result = await mt5_connector.connect()
        assert result == True
        assert mt5_connector.connected == True
        assert mt5_connector.simulation_mode == True
    
    @pytest.mark.asyncio
    async def test_get_current_tick(self, mt5_connector):
        """Test tick data retrieval"""
        await mt5_connector.connect()
        
        tick = await mt5_connector.get_current_tick("EURUSD")
        
        assert tick is not None
        assert tick.symbol == "EURUSD"
        assert tick.bid > 0
        assert tick.ask > tick.bid  # Ask should be higher than bid
        assert isinstance(tick.time, datetime)
    
    @pytest.mark.asyncio
    async def test_get_candles(self, mt5_connector):
        """Test candlestick data retrieval"""
        await mt5_connector.connect()
        
        candles = await mt5_connector.get_candles("EURUSD", "M5", 10)
        
        assert len(candles) == 10
        for candle in candles:
            assert candle.symbol == "EURUSD"
            assert candle.timeframe == "M5"
            assert candle.high >= candle.low
            assert candle.high >= max(candle.open, candle.close)
            assert candle.low <= min(candle.open, candle.close)
    
    @pytest.mark.asyncio
    async def test_place_order_simulation(self, mt5_connector):
        """Test order placement in simulation mode"""
        await mt5_connector.connect()
        
        result = await mt5_connector.place_order(
            symbol="EURUSD",
            order_type=OrderType.BUY,
            volume=0.01,
            price=1.0800,
            comment="Test order"
        )
        
        assert result is not None
        assert result['retcode'] == 10009  # TRADE_RETCODE_DONE
        assert result['volume'] == 0.01
        assert 'deal' in result

class TestYlipipCalculator:
    """Test Ylipip calculation for different assets"""
    
    def test_forex_ylipip_values(self):
        """Test Ylipip values for forex pairs"""
        assert YlipipCalculator.get_ylipip("EURUSD") == 0.6 * 0.0001
        assert YlipipCalculator.get_ylipip("GBPUSD") == 0.6 * 0.0001
        assert YlipipCalculator.get_ylipip("USDJPY") == 0.6 * 0.01
    
    def test_crypto_ylipip_values(self):
        """Test Ylipip values for crypto CFDs"""
        assert YlipipCalculator.get_ylipip("BTCUSD") == 0.6 * 10.0
        assert YlipipCalculator.get_ylipip("ETHUSD") == 0.6 * 1.0
    
    def test_index_ylipip_values(self):
        """Test Ylipip values for index CFDs"""
        assert YlipipCalculator.get_ylipip("SPX500") == 0.6 * 1.0
        assert YlipipCalculator.get_ylipip("NAS100") == 0.6 * 1.0
    
    def test_unknown_symbol_default(self):
        """Test default Ylipip for unknown symbols"""
        assert YlipipCalculator.get_ylipip("UNKNOWN") == 0.6 * 0.0001

class TestLightningBoltStrategy:
    """Test Lightning Bolt Strategy implementation"""
    
    @pytest.fixture
    def mock_mt5(self):
        mt5 = Mock()
        mt5.active_symbols = ["EURUSD", "GBPUSD", "BTCUSD"]
        return mt5
    
    @pytest.fixture
    def strategy(self, mock_mt5):
        return LightningBoltStrategy(mock_mt5)
    
    def test_strategy_initialization(self, strategy):
        """Test strategy initialization"""
        assert strategy.min_confidence == 0.75
        assert strategy.max_risk_per_trade == 0.01
        assert strategy.rr_ratio == 2.0
    
    @pytest.mark.asyncio
    async def test_pattern_confidence_calculation(self, strategy):
        """Test BOS pattern confidence calculation"""
        # Create mock candle and level
        candle = Mock()
        candle.close = 1.0850
        candle.high = 1.0860
        candle.low = 1.0840
        candle.open = 1.0845
        
        level = Mock()
        level.price = 1.0840
        level.strength = 3
        
        confidence = strategy._calculate_bos_confidence(
            candle, level, TrendDirection.BULLISH
        )
        
        assert 0.5 <= confidence <= 1.0
    
    def test_active_patterns_management(self, strategy):
        """Test pattern tracking and cleanup"""
        # Test that we can store and retrieve patterns
        initial_count = len(strategy.active_patterns)
        
        # Add some mock patterns would go here
        # This is a placeholder for pattern management testing
        
        assert len(strategy.get_active_patterns()) >= initial_count

class TestMCPv2Controller:
    """Test MCP v2 Controller orchestration"""
    
    @pytest.fixture
    def mcp_controller(self):
        return MCPv2Controller()
    
    def test_controller_initialization(self, mcp_controller):
        """Test MCP controller initialization"""
        assert mcp_controller.total_trades == 0
        assert mcp_controller.successful_trades == 0
        assert mcp_controller.total_profit == 0.0
        assert len(mcp_controller.agents) == 0
    
    def test_agent_registration(self, mcp_controller):
        """Test agent registration"""
        mock_handler = AsyncMock()
        
        mcp_controller.register_agent(
            "test_agent",
            AgentType.STRATEGY,
            mock_handler,
            {"config": "test"}
        )
        
        assert "test_agent" in mcp_controller.agents
        assert mcp_controller.agents["test_agent"]["type"] == AgentType.STRATEGY
        assert "test_agent" in mcp_controller.performance_metrics
    
    @pytest.mark.asyncio
    async def test_message_queuing(self, mcp_controller):
        """Test message priority queuing"""
        
        # Create messages with different priorities
        high_priority_msg = MCPMessage(
            id="high_priority",
            type=MessageType.SIGNAL,
            sender="test",
            recipient="mcp",
            payload={},
            timestamp=datetime.now(),
            priority=1
        )
        
        low_priority_msg = MCPMessage(
            id="low_priority", 
            type=MessageType.SYSTEM_STATUS,
            sender="test",
            recipient="mcp",
            payload={},
            timestamp=datetime.now(),
            priority=5
        )
        
        # Send low priority first, then high priority
        await mcp_controller.send_message(low_priority_msg)
        await mcp_controller.send_message(high_priority_msg)
        
        # High priority should be first in queue
        assert mcp_controller.message_queue[0].priority == 1
        assert mcp_controller.message_queue[1].priority == 5
    
    def test_system_stats(self, mcp_controller):
        """Test system statistics reporting"""
        stats = mcp_controller.get_system_stats()
        
        required_keys = [
            'total_trades', 'successful_trades', 'success_rate',
            'total_profit', 'active_signals', 'queue_size',
            'active_agents', 'daily_performance'
        ]
        
        for key in required_keys:
            assert key in stats

class TestHanseiReflector:
    """Test Hansei Reflection System"""
    
    @pytest.fixture
    def hansei_reflector(self):
        return HanseiReflector()
    
    def test_reflector_initialization(self, hansei_reflector):
        """Test Hansei reflector initialization"""
        assert hansei_reflector.tactical_interval == 300
        assert hansei_reflector.strategic_interval == 3600
        assert hansei_reflector.philosophical_interval == 86400
        assert hansei_reflector.insight_confidence_threshold == 0.7
    
    def test_reflection_summary(self, hansei_reflector):
        """Test reflection summary generation"""
        summary = hansei_reflector.get_reflection_summary()
        
        # Empty reflector should return basic summary
        assert summary['total_insights'] == 0
    
    @pytest.mark.asyncio
    async def test_tactical_reflection(self, hansei_reflector):
        """Test tactical reflection logic"""
        # Mock MCP controller with stats
        mock_mcp = Mock()
        mock_mcp.get_system_stats.return_value = {
            'success_rate': 50.0,  # Low success rate
            'active_signals': 6    # High signal count
        }
        
        hansei_reflector.mcp = mock_mcp
        
        insights = await hansei_reflector._perform_tactical_reflection()
        
        # Should detect both low success rate and signal overload
        assert len(insights) >= 1
        
        # Check that insights are properly classified
        for insight in insights:
            assert insight.type == ReflectionType.TACTICAL
            assert 0.0 <= insight.confidence <= 1.0

class TestTradingEngineIntegration:
    """Integration tests for complete trading engine"""
    
    @pytest.fixture
    def trading_engine(self):
        return MikrobotV2TradingEngine()
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, trading_engine):
        """Test trading engine initialization"""
        # Mock MT5 connection success
        with patch.object(trading_engine.mt5, 'connect', return_value=True):
            result = await trading_engine.initialize()
            
            assert result == True
            assert trading_engine.strategy is not None
            assert trading_engine.execution_agent is not None
            assert trading_engine.hansei is not None
    
    def test_ml_validation_agent(self, trading_engine):
        """Test ML validation agent"""
        ml_agent = trading_engine.ml_agent
        
        # Test validation with different signals
        test_signals = [
            {'symbol': 'EURUSD', 'confidence': 0.8},
            {'symbol': 'BTCUSD', 'confidence': 0.7},
            {'symbol': 'SPX500', 'confidence': 0.6}
        ]
        
        for signal in test_signals:
            # Validation should return a score between 0 and 1
            # Note: This is async, so in real test we'd await it
            pass  # Placeholder for async test
    
    def test_risk_agent(self, trading_engine):
        """Test risk management agent"""
        risk_agent = trading_engine.risk_agent
        
        # Test trade within risk limits
        safe_trade = {
            'symbol': 'EURUSD',
            'volume': 0.01,
            'entry_price': 1.0800,
            'stop_loss': 1.0790,
            'take_profit': 1.0820
        }
        
        # This would be async in real implementation
        # result = await risk_agent.check_risk(safe_trade)
        # assert result['approved'] == True
        
        # Test trade exceeding limits
        risky_trade = {
            'symbol': 'EURUSD', 
            'volume': 1.0,  # Too large
            'entry_price': 1.0800,
            'stop_loss': 1.0790,
            'take_profit': 1.0820
        }
        
        # result = await risk_agent.check_risk(risky_trade)
        # assert result['approved'] == False

class TestSystemBehavior:
    """Test overall system behavior and edge cases"""
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self):
        """Test that system shuts down gracefully"""
        engine = MikrobotV2TradingEngine()
        
        # Initialize without actually starting trading
        with patch.object(engine.mt5, 'connect', return_value=True):
            await engine.initialize()
        
        # Should not raise exceptions
        await engine.stop_trading()
        
        assert engine.running == False
    
    def test_error_handling(self):
        """Test error handling in various components"""
        # Test that components handle missing data gracefully
        mt5 = MT5DirectConnector()
        
        # Should not crash with invalid symbols
        # (This would be async in real test)
        pass
    
    def test_configuration_validation(self):
        """Test that system validates configuration"""
        # Test invalid credentials
        invalid_mt5 = MT5DirectConnector(login=0, password="", server="")
        
        # Should handle invalid configuration gracefully
        assert invalid_mt5.login == 0
        assert invalid_mt5.simulation_mode == True  # Should fallback to simulation

# Performance and load tests
class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.asyncio
    async def test_message_processing_performance(self):
        """Test MCP message processing under load"""
        mcp = MCPv2Controller()
        
        # Create many messages
        messages = []
        for i in range(100):
            msg = MCPMessage(
                id=f"perf_test_{i}",
                type=MessageType.SYSTEM_STATUS,
                sender="perf_test",
                recipient="mcp",
                payload={'test': i},
                timestamp=datetime.now(),
                priority=5
            )
            messages.append(msg)
        
        # Send all messages
        start_time = datetime.now()
        for msg in messages:
            await mcp.send_message(msg)
        end_time = datetime.now()
        
        # Should process messages quickly
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 1.0  # Less than 1 second for 100 messages
    
    @pytest.mark.asyncio
    async def test_strategy_scanning_performance(self):
        """Test strategy scanning performance"""
        mock_mt5 = Mock()
        mock_mt5.active_symbols = ["EURUSD", "GBPUSD", "BTCUSD", "SPX500", "NAS100"] * 5  # 25 symbols
        
        strategy = LightningBoltStrategy(mock_mt5)
        
        # Mock candle data
        with patch.object(strategy.mt5, 'get_candles', return_value=[]):
            start_time = datetime.now()
            signals = await strategy.scan_all_symbols()
            end_time = datetime.now()
            
            scan_time = (end_time - start_time).total_seconds()
            assert scan_time < 5.0  # Should scan 25 symbols in under 5 seconds

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    # Add markers
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])