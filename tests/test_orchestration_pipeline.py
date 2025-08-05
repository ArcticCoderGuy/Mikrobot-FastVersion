"""
Comprehensive Test Suite for Orchestration Pipeline
Tests the complete ProductOwner → MCPController → U-Cells flow
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Optional
import json

# Import system components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.enhanced_orchestrator import EnhancedOrchestrator, PipelineResult, ProcessingStage
from core.product_owner_agent import ProductOwnerAgent, StrategyType, PerformanceMetrics
from core.mcp_controller import MCPController, MCPMessage, MessageType, AgentRole
from core.error_recovery import ErrorRecoverySystem, ErrorSeverity, RecoveryAction
from core.monitoring import MonitoringSystem, MetricType, AlertSeverity


class TestProductOwnerAgent:
    """Test ProductOwner Agent functionality"""
    
    @pytest.fixture
    def product_owner(self):
        """Create ProductOwner agent for testing"""
        return ProductOwnerAgent("test_product_owner")
    
    @pytest.mark.asyncio
    async def test_strategic_evaluation_approval(self, product_owner):
        """Test strategic evaluation with approved signal"""
        signal_data = {
            'symbol': 'EURUSD',
            'timeframe': 'M5',
            'pattern_type': 'M5_BOS',
            'direction': 'BUY',
            'risk_percent': 0.01,
            'entry': 1.0850,
            'stop_loss': 1.0830,
            'take_profit': 1.0890
        }
        
        evaluation_message = MCPMessage(
            id="test_eval_001",
            method="evaluate_signal",
            params={'signal_data': signal_data, 'trace_id': 'test_trace_001'},
            sender="test_client"
        )
        
        response = await product_owner.handle_message(evaluation_message)
        
        assert response is not None
        assert response.method == "signal_evaluation_result"
        evaluation = response.params.get('evaluation', {})
        
        assert 'approved' in evaluation
        assert 'confidence' in evaluation
        assert 'reasons' in evaluation
        assert isinstance(evaluation['approved'], bool)
        assert 0.0 <= evaluation['confidence'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_strategic_evaluation_rejection(self, product_owner):
        """Test strategic evaluation with rejected signal"""
        # Signal with excessive risk
        signal_data = {
            'symbol': 'EURUSD',
            'timeframe': 'M5',
            'pattern_type': 'M5_BOS',
            'direction': 'BUY',
            'risk_percent': 0.10,  # 10% risk - too high
            'entry': 1.0850,
            'stop_loss': 1.0830,
            'take_profit': 1.0890
        }
        
        evaluation_message = MCPMessage(
            id="test_eval_002",
            method="evaluate_signal",
            params={'signal_data': signal_data, 'trace_id': 'test_trace_002'},
            sender="test_client"
        )
        
        response = await product_owner.handle_message(evaluation_message)
        evaluation = response.params.get('evaluation', {})
        
        # Should be rejected due to high risk
        assert evaluation['approved'] == False
        assert 'risk parameters exceed limits' in ' '.join(evaluation['reasons']).lower()
    
    @pytest.mark.asyncio
    async def test_performance_update(self, product_owner):
        """Test performance metrics update"""
        # Simulate winning trade
        trade_result = {
            'pnl': 50.0,
            'rr_ratio': 2.5,
            'execution_latency_ms': 150.0
        }
        
        performance_message = MCPMessage(
            id="test_perf_001",
            method="update_performance",
            params={'trade_result': trade_result, 'trace_id': 'test_trace_003'},
            sender="test_orchestrator"
        )
        
        initial_trades = product_owner.performance.total_trades
        initial_pnl = product_owner.performance.total_pnl
        
        response = await product_owner.handle_message(performance_message)
        
        assert response is not None
        assert response.method == "performance_updated"
        
        # Check metrics were updated
        assert product_owner.performance.total_trades == initial_trades + 1
        assert product_owner.performance.total_pnl == initial_pnl + 50.0
        assert product_owner.performance.winning_trades > 0
    
    def test_strategy_configuration(self, product_owner):
        """Test strategy configuration and management"""
        # Check default strategies loaded
        assert 'm5_bos' in product_owner.strategies
        assert 'm1_retest' in product_owner.strategies
        assert product_owner.active_strategy is not None
        
        # Test strategy properties
        m5_strategy = product_owner.strategies['m5_bos']
        assert m5_strategy.strategy_type == StrategyType.M5_BOS
        assert m5_strategy.max_risk_per_trade <= 0.02  # Max 2% risk
        assert m5_strategy.min_win_rate >= 0.5  # At least 50% win rate target


class TestMCPController:
    """Test MCP Controller functionality"""
    
    @pytest.fixture
    def mcp_controller(self):
        """Create MCP Controller for testing"""
        return MCPController({'test_mode': True})
    
    @pytest.fixture
    def mock_agent(self):
        """Create mock agent for testing"""
        agent = Mock()
        agent.agent_id = "test_agent"
        agent.role = AgentRole.SIGNAL_VALIDATOR
        agent.is_active = True
        agent.metrics = {'messages_received': 0}
        agent.handle_message = AsyncMock()
        return agent
    
    def test_agent_registration(self, mcp_controller, mock_agent):
        """Test agent registration"""
        mcp_controller.register_agent(mock_agent)
        
        assert "test_agent" in mcp_controller.agents
        assert mcp_controller.agents["test_agent"] == mock_agent
        assert mock_agent.controller == mcp_controller
        assert "test_agent" in mcp_controller.circuit_breakers
        assert "test_agent" in mcp_controller.agent_health
    
    @pytest.mark.asyncio
    async def test_message_routing(self, mcp_controller, mock_agent):
        """Test message routing to agent"""
        mcp_controller.register_agent(mock_agent)
        
        # Configure mock response
        mock_response = MCPMessage(
            id="response_001",
            method="test_response",
            params={'status': 'success'},
            type=MessageType.RESPONSE
        )
        mock_agent.handle_message.return_value = mock_response
        
        # Send message
        test_message = MCPMessage(
            id="test_001",
            method="test_method",
            params={'test': True},
            recipient="test_agent",
            sender="test_client"
        )
        
        # Use internal routing to avoid priority queue
        response = await mcp_controller._route_message_internal(test_message, datetime.utcnow())
        
        assert response is not None
        assert response.method == "test_response"
        assert mock_agent.handle_message.called
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, mcp_controller, mock_agent):
        """Test circuit breaker protection"""
        mcp_controller.register_agent(mock_agent)
        
        # Configure agent to fail
        mock_agent.handle_message.side_effect = Exception("Agent failure")
        
        # Send multiple messages to trigger circuit breaker
        test_message = MCPMessage(
            id="test_cb_001",
            method="test_method",
            params={},
            recipient="test_agent"
        )
        
        # Send 6 messages (threshold is 5)
        for i in range(6):
            await mcp_controller._route_message_internal(test_message, datetime.utcnow())
        
        # Circuit breaker should be open
        assert mcp_controller.circuit_breakers["test_agent"]['state'] == 'OPEN'
        assert mcp_controller.metrics['circuit_breaker_trips'] > 0
    
    @pytest.mark.asyncio
    async def test_health_check(self, mcp_controller, mock_agent):
        """Test health check functionality"""
        mcp_controller.register_agent(mock_agent)
        
        # Configure successful ping response
        ping_response = MCPMessage(
            id="pong_001",
            method="pong",
            params={'timestamp': datetime.utcnow().isoformat()},
            type=MessageType.RESPONSE
        )
        mock_agent.handle_message.return_value = ping_response
        
        # Execute health check
        health_message = MCPMessage(
            id="health_001",
            method="health_check",
            params={},
            sender="test_client"
        )
        
        response = await mcp_controller._handle_health_check(health_message)
        
        assert response is not None
        assert response.method == "health_status"
        health_data = response.params.get('agents', {})
        assert "test_agent" in health_data
        assert health_data["test_agent"]['status'] == 'healthy'


class TestEnhancedOrchestrator:
    """Test Enhanced Orchestrator functionality"""
    
    @pytest.fixture
    def orchestrator_config(self):
        """Create orchestrator configuration for testing"""
        return {
            'mcp_config': {'test_mode': True},
            'ucell_config': {
                'mt5_connection': Mock(),
                'account_config': {
                    'balance': 10000.0,
                    'max_daily_loss_percent': 0.05,
                    'max_total_loss_percent': 0.10,
                    'max_position_risk_percent': 0.02
                }
            }
        }
    
    @pytest.fixture
    def enhanced_orchestrator(self, orchestrator_config):
        """Create Enhanced Orchestrator for testing"""
        with patch('core.enhanced_orchestrator.UCellOrchestrator') as mock_ucell:
            # Configure UCellOrchestrator mock
            mock_ucell_instance = Mock()
            mock_ucell_instance.process_signal = AsyncMock()
            mock_ucell.return_value = mock_ucell_instance
            
            orchestrator = EnhancedOrchestrator(orchestrator_config)
            orchestrator.ucell_orchestrator = mock_ucell_instance
            return orchestrator
    
    @pytest.mark.asyncio
    async def test_complete_pipeline_success(self, enhanced_orchestrator):
        """Test complete pipeline with successful execution"""
        # Mock successful strategic evaluation
        mock_strategic_response = MCPMessage(
            id="strategic_001",
            method="signal_evaluation_result",
            params={
                'evaluation': {
                    'approved': True,
                    'confidence': 0.85,
                    'strategy_match': True,
                    'risk_acceptable': True,
                    'market_conditions_favorable': True,
                    'reasons': ['Signal approved'],
                    'adjustments': {'risk_reduction': 0.9}
                }
            },
            type=MessageType.RESPONSE
        )
        
        # Mock successful U-Cell execution
        mock_ucell_result = {
            'trace_id': 'test_trace_001',
            'final_status': 'success',
            'total_latency_ms': 245.5,
            'cell_outputs': {
                'U4': {
                    'data': {
                        'pnl': 75.0,
                        'rr_achieved': 2.1,
                        'order_id': 'ORDER_12345'
                    }
                }
            }
        }
        
        # Mock MCP controller routing
        enhanced_orchestrator.mcp_controller.route_message = AsyncMock(return_value=mock_strategic_response)
        enhanced_orchestrator.ucell_orchestrator.process_signal.return_value = mock_ucell_result
        
        # Test signal
        signal_data = {
            'symbol': 'EURUSD',
            'timeframe': 'M5',
            'pattern_type': 'M5_BOS',
            'direction': 'BUY',
            'risk_percent': 0.01,
            'entry': 1.0850,
            'stop_loss': 1.0830,
            'take_profit': 1.0890
        }
        
        # Execute pipeline
        result = await enhanced_orchestrator.process_trading_signal(signal_data)
        
        # Validate results
        assert isinstance(result, PipelineResult)
        assert result.final_status == 'success'
        assert result.strategic_decision['approved'] == True
        assert result.u_cell_results['final_status'] == 'success'
        assert result.total_latency_ms > 0
        assert ProcessingStage.STRATEGIC_EVALUATION.value in result.stage_results
        assert result.errors == []
    
    @pytest.mark.asyncio
    async def test_strategic_rejection_pipeline(self, enhanced_orchestrator):
        """Test pipeline with strategic rejection"""
        # Mock strategic rejection
        mock_strategic_response = MCPMessage(
            id="strategic_002",
            method="signal_evaluation_result",
            params={
                'evaluation': {
                    'approved': False,
                    'confidence': 0.25,
                    'strategy_match': False,
                    'risk_acceptable': False,
                    'market_conditions_favorable': True,
                    'reasons': ['Risk parameters exceed limits', 'Strategy mismatch']
                }
            },
            type=MessageType.RESPONSE
        )
        
        enhanced_orchestrator.mcp_controller.route_message = AsyncMock(return_value=mock_strategic_response)
        
        # Test signal with high risk
        signal_data = {
            'symbol': 'GBPUSD',
            'timeframe': 'M1',
            'pattern_type': 'M1_RETEST',
            'direction': 'SELL',
            'risk_percent': 0.05,  # High risk
            'entry': 1.2650,
            'stop_loss': 1.2680,
            'take_profit': 1.2590
        }
        
        # Execute pipeline
        result = await enhanced_orchestrator.process_trading_signal(signal_data)
        
        # Validate rejection
        assert result.final_status == 'strategically_rejected'
        assert result.strategic_decision['approved'] == False
        assert 'rejection_reason' in result.stage_results
        assert result.u_cell_results == {}  # Should not reach U-Cells
    
    @pytest.mark.asyncio
    async def test_pipeline_error_handling(self, enhanced_orchestrator):
        """Test pipeline error handling"""
        # Mock MCP controller failure
        enhanced_orchestrator.mcp_controller.route_message = AsyncMock(side_effect=Exception("MCP communication failed"))
        
        signal_data = {
            'symbol': 'USDJPY',
            'timeframe': 'M5',
            'pattern_type': 'M5_BOS',
            'direction': 'BUY',
            'risk_percent': 0.015
        }
        
        # Execute pipeline
        result = await enhanced_orchestrator.process_trading_signal(signal_data)
        
        # Validate error handling
        assert result.final_status == 'pipeline_error'
        assert len(result.errors) > 0
        assert 'MCP communication failed' in result.errors[0]
    
    def test_strategic_adjustments(self, enhanced_orchestrator):
        """Test strategic adjustments application"""
        signal_data = {
            'symbol': 'EURUSD',
            'risk_percent': 0.02,
            'target_rr_ratio': 2.0
        }
        
        strategic_decision = {
            'adjustments': {
                'risk_reduction': 0.5,
                'target_rr': 2.5
            }
        }
        
        adjusted_signal = enhanced_orchestrator._apply_strategic_adjustments(signal_data, strategic_decision)
        
        # Validate adjustments
        assert adjusted_signal['risk_percent'] == 0.01  # 0.02 * 0.5
        assert adjusted_signal['target_rr_ratio'] == 2.5
        assert 'strategic_metadata' in adjusted_signal
        assert adjusted_signal['strategic_metadata']['adjustments_applied'] == strategic_decision['adjustments']
    
    def test_metrics_collection(self, enhanced_orchestrator):
        """Test orchestration metrics collection"""
        # Simulate some completed pipelines
        enhanced_orchestrator.orchestration_metrics['total_signals_processed'] = 10
        enhanced_orchestrator.orchestration_metrics['strategic_approvals'] = 7
        enhanced_orchestrator.orchestration_metrics['strategic_rejections'] = 3
        enhanced_orchestrator.orchestration_metrics['pipeline_completions'] = 6
        enhanced_orchestrator.orchestration_metrics['pipeline_failures'] = 1
        
        metrics = enhanced_orchestrator.get_comprehensive_metrics()
        
        # Validate metrics structure
        assert 'orchestration' in metrics
        assert 'mcp_controller' in metrics
        assert 'product_owner' in metrics
        assert 'ucell_orchestrator' in metrics
        assert 'system_status' in metrics
        
        orchestration_metrics = metrics['orchestration']
        assert orchestration_metrics['total_signals_processed'] == 10
        assert orchestration_metrics['strategic_approvals'] == 7
        assert orchestration_metrics['strategic_rejections'] == 3


class TestIntegrationScenarios:
    """Integration tests for complete system scenarios"""
    
    @pytest.fixture
    def full_system_config(self):
        """Create full system configuration"""
        return {
            'mcp_config': {'test_mode': True},
            'ucell_config': {
                'mt5_connection': Mock(),
                'account_config': {
                    'balance': 10000.0,
                    'max_daily_loss_percent': 0.05,
                    'max_total_loss_percent': 0.10,
                    'max_position_risk_percent': 0.02
                }
            },
            'monitoring_config': {'test_mode': True},
            'error_recovery_config': {'test_mode': True}
        }
    
    @pytest.mark.asyncio
    async def test_high_volume_processing(self, full_system_config):
        """Test system under high volume processing"""
        with patch('core.enhanced_orchestrator.UCellOrchestrator') as mock_ucell:
            mock_ucell_instance = Mock()
            mock_ucell_instance.process_signal = AsyncMock()
            mock_ucell.return_value = mock_ucell_instance
            
            orchestrator = EnhancedOrchestrator(full_system_config)
            orchestrator.ucell_orchestrator = mock_ucell_instance
            
            # Mock successful responses
            strategic_response = MCPMessage(
                id="vol_test",
                method="signal_evaluation_result",
                params={'evaluation': {'approved': True, 'confidence': 0.8, 'reasons': ['Approved']}},
                type=MessageType.RESPONSE
            )
            
            ucell_result = {
                'final_status': 'success',
                'total_latency_ms': 100.0,
                'cell_outputs': {'U4': {'data': {'pnl': 25.0, 'rr_achieved': 2.0}}}
            }
            
            orchestrator.mcp_controller.route_message = AsyncMock(return_value=strategic_response)
            mock_ucell_instance.process_signal.return_value = ucell_result
            
            # Process multiple signals concurrently
            signals = []
            for i in range(20):
                signal = {
                    'symbol': f'PAIR{i:02d}',
                    'timeframe': 'M5',
                    'pattern_type': 'M5_BOS',
                    'direction': 'BUY' if i % 2 == 0 else 'SELL',
                    'risk_percent': 0.01
                }
                signals.append(signal)
            
            # Execute all signals concurrently
            tasks = [orchestrator.process_trading_signal(signal) for signal in signals]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Validate results
            successful_results = [r for r in results if isinstance(r, PipelineResult) and r.final_status == 'success']
            assert len(successful_results) == 20
            
            # Check metrics
            metrics = orchestrator.get_comprehensive_metrics()
            assert metrics['orchestration']['total_signals_processed'] == 20
    
    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, full_system_config):
        """Test error recovery system integration"""
        with patch('core.enhanced_orchestrator.UCellOrchestrator') as mock_ucell:
            mock_ucell_instance = Mock()
            mock_ucell_instance.process_signal = AsyncMock()
            mock_ucell.return_value = mock_ucell_instance
            
            orchestrator = EnhancedOrchestrator(full_system_config)
            orchestrator.ucell_orchestrator = mock_ucell_instance
            
            # Create error recovery system
            error_recovery = ErrorRecoverySystem()
            
            # Test various error scenarios
            error_scenarios = [
                (ConnectionError("MT5 connection lost"), 'mt5_connection', 'connect'),
                (TimeoutError("Signal processing timeout"), 'signal_processing', 'validate'),
                (ValueError("Invalid order parameters"), 'trade_execution', 'place_order')
            ]
            
            recovery_results = []
            for error, component, operation in error_scenarios:
                recovery_success = await error_recovery.handle_error(error, component, operation)
                recovery_results.append(recovery_success)
            
            # Validate error recovery
            assert len(recovery_results) == 3
            assert any(recovery_results)  # At least some recoveries should succeed
            
            # Check error analytics
            analytics = error_recovery.get_error_analytics()
            assert analytics['metrics']['total_errors'] == 3
            assert len(analytics['recent_errors']) == 3
    
    @pytest.mark.asyncio
    async def test_monitoring_integration(self, full_system_config):
        """Test monitoring system integration"""
        monitoring = MonitoringSystem(full_system_config.get('monitoring_config', {}))
        
        # Start monitoring
        await monitoring.start()
        
        # Record various metrics
        monitoring.increment_counter('signals.received', 5)
        monitoring.set_gauge('system.cpu_usage', 65.5)
        monitoring.record_histogram('latency.pipeline', 150.0)
        
        # Create alerts
        monitoring.alerts.create_alert(
            name="high_latency",
            condition="latency > 1000ms",
            severity=AlertSeverity.WARNING,
            message="Pipeline latency is high",
            component="orchestrator"
        )
        
        # Validate monitoring data
        status = monitoring.get_comprehensive_status()
        
        assert status['system_health']['status'] in ['healthy', 'degraded', 'unhealthy']
        assert status['metrics_summary']['counters_count'] > 0
        assert status['alert_summary']['total_alerts'] > 0
        
        # Stop monitoring
        await monitoring.stop()


class TestPerformanceAndLoadTesting:
    """Performance and load testing scenarios"""
    
    @pytest.mark.asyncio
    async def test_latency_requirements(self):
        """Test system meets latency requirements"""
        config = {
            'mcp_config': {'test_mode': True},
            'ucell_config': {'mt5_connection': Mock()}
        }
        
        with patch('core.enhanced_orchestrator.UCellOrchestrator') as mock_ucell:
            mock_ucell_instance = Mock()
            mock_ucell_instance.process_signal = AsyncMock()
            mock_ucell.return_value = mock_ucell_instance
            
            orchestrator = EnhancedOrchestrator(config)
            orchestrator.ucell_orchestrator = mock_ucell_instance
            
            # Mock fast responses
            strategic_response = MCPMessage(
                id="latency_test",
                method="signal_evaluation_result",
                params={'evaluation': {'approved': True, 'confidence': 0.8}},
                type=MessageType.RESPONSE
            )
            
            ucell_result = {
                'final_status': 'success',
                'total_latency_ms': 50.0
            }
            
            orchestrator.mcp_controller.route_message = AsyncMock(return_value=strategic_response)
            mock_ucell_instance.process_signal.return_value = ucell_result
            
            # Test signal processing time
            signal_data = {
                'symbol': 'EURUSD',
                'timeframe': 'M5',
                'pattern_type': 'M5_BOS',
                'direction': 'BUY'
            }
            
            start_time = datetime.utcnow()
            result = await orchestrator.process_trading_signal(signal_data)
            end_time = datetime.utcnow()
            
            processing_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Validate latency requirements (should be < 1000ms for complete pipeline)
            assert processing_time_ms < 1000.0
            assert result.total_latency_ms < 1000.0
    
    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test system memory usage under load"""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        config = {
            'mcp_config': {'test_mode': True},
            'ucell_config': {'mt5_connection': Mock()}
        }
        
        with patch('core.enhanced_orchestrator.UCellOrchestrator') as mock_ucell:
            mock_ucell_instance = Mock()
            mock_ucell_instance.process_signal = AsyncMock(return_value={'final_status': 'success'})
            mock_ucell.return_value = mock_ucell_instance
            
            orchestrator = EnhancedOrchestrator(config)
            orchestrator.ucell_orchestrator = mock_ucell_instance
            
            # Mock responses
            strategic_response = MCPMessage(
                id="memory_test",
                method="signal_evaluation_result", 
                params={'evaluation': {'approved': True, 'confidence': 0.8}},
                type=MessageType.RESPONSE
            )
            orchestrator.mcp_controller.route_message = AsyncMock(return_value=strategic_response)
            
            # Process many signals to test memory usage
            for i in range(100):
                signal_data = {
                    'symbol': f'PAIR{i:02d}',
                    'timeframe': 'M5',
                    'pattern_type': 'M5_BOS',
                    'direction': 'BUY'
                }
                await orchestrator.process_trading_signal(signal_data)
                
                # Force garbage collection periodically
                if i % 50 == 0:
                    gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (< 100MB for 100 signals)
            assert memory_increase < 100.0


@pytest.mark.asyncio
async def test_end_to_end_pipeline():
    """Complete end-to-end pipeline test"""
    # This test simulates a complete trading signal flow
    config = {
        'mcp_config': {'test_mode': True},
        'ucell_config': {
            'mt5_connection': Mock(),
            'account_config': {
                'balance': 10000.0,
                'max_daily_loss_percent': 0.05
            }
        }
    }
    
    with patch('core.enhanced_orchestrator.UCellOrchestrator') as mock_ucell:
        mock_ucell_instance = Mock()
        mock_ucell_instance.process_signal = AsyncMock()
        mock_ucell.return_value = mock_ucell_instance
        
        # Create orchestrator
        orchestrator = EnhancedOrchestrator(config)
        orchestrator.ucell_orchestrator = mock_ucell_instance
        
        # Start orchestrator
        await orchestrator.start()
        
        # Mock successful execution chain
        strategic_response = MCPMessage(
            id="e2e_strategic",
            method="signal_evaluation_result",
            params={
                'evaluation': {
                    'approved': True,
                    'confidence': 0.9,
                    'strategy_match': True,
                    'risk_acceptable': True,
                    'market_conditions_favorable': True,
                    'reasons': ['All criteria met'],
                    'adjustments': {'target_rr': 2.5}
                }
            },
            type=MessageType.RESPONSE
        )
        
        ucell_result = {
            'trace_id': 'e2e_test_001',
            'final_status': 'success',
            'total_latency_ms': 200.0,
            'cell_outputs': {
                'U1': {'status': 'success', 'data': {'pattern_confirmed': True}},
                'U2': {'status': 'success', 'data': {'ml_confidence': 0.85}},
                'U3': {'status': 'success', 'data': {'risk_approved': True}},
                'U4': {'status': 'success', 'data': {'order_id': 'ORD_12345', 'pnl': 125.0, 'rr_achieved': 2.3}},
                'U5': {'status': 'success', 'data': {'quality_score': 0.92}}
            }
        }
        
        orchestrator.mcp_controller.route_message = AsyncMock(return_value=strategic_response)
        mock_ucell_instance.process_signal.return_value = ucell_result
        
        # Test signal representing real trading scenario
        signal_data = {
            'symbol': 'EURUSD',
            'timeframe': 'M5', 
            'pattern_type': 'M5_BOS',
            'direction': 'BUY',
            'price_levels': {
                'entry': 1.0850,
                'stop_loss': 1.0830,
                'take_profit': 1.0900,
                'current_price': 1.0851,
                'break_level': 1.0845
            },
            'volume': 0.01,
            'risk_percent': 0.015,
            'metadata': {
                'signal_source': 'mt5_ea',
                'signal_strength': 'strong',
                'market_session': 'london'
            }
        }
        
        # Execute complete pipeline
        result = await orchestrator.process_trading_signal(signal_data)
        
        # Comprehensive validation
        assert isinstance(result, PipelineResult)
        assert result.final_status == 'success'
        assert result.strategic_decision['approved'] == True
        assert result.strategic_decision['confidence'] == 0.9
        assert result.u_cell_results['final_status'] == 'success'
        assert result.total_latency_ms > 0
        
        # Validate all processing stages completed
        expected_stages = [
            ProcessingStage.STRATEGIC_EVALUATION.value,
            ProcessingStage.PERFORMANCE_UPDATE.value
        ]
        
        for stage in expected_stages:
            assert stage in result.stage_results
            assert result.stage_results[stage]['latency_ms'] > 0
        
        # Validate strategic adjustments were applied
        assert 'strategic_metadata' in result.u_cell_results.get('adjusted_signal_data', {})
        
        # Check metrics updated
        metrics = orchestrator.get_comprehensive_metrics()
        assert metrics['orchestration']['total_signals_processed'] > 0
        assert metrics['orchestration']['strategic_approvals'] > 0
        assert metrics['orchestration']['pipeline_completions'] > 0
        
        # Check ProductOwner performance updated
        po_metrics = metrics['product_owner']['performance']
        assert po_metrics['total_trades'] > 0
        assert po_metrics['winning_trades'] > 0
        assert po_metrics['total_pnl'] > 0
        
        # Stop orchestrator
        await orchestrator.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])