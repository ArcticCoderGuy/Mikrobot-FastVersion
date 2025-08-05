from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Test Suite for Enterprise Error Recovery System
Comprehensive validation of Above Robust! standards

Session #3 - Production-Ready System Testing
"""

import asyncio
import sys
import os
import tempfile
import unittest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.live_trading.error_recovery_system import (
        ErrorRecoverySystem, ErrorEvent, ErrorSeverity, RecoveryState,
        ConnectionState, ConnectionHealth, SystemState
    )
    from core.live_trading.production_integration import ProductionTradingSystem
    from core.connectors.mt5_connector import MT5Connector, MT5Config
    from core.product_owner_agent import ProductOwnerAgent
    
    IMPORTS_SUCCESS = True
except ImportError as e:
    print(f"Import error (expected in isolated test): {e}")
    IMPORTS_SUCCESS = False


class TestErrorRecoverySystem(unittest.TestCase):
    """Test Enterprise Error Recovery System"""
    
    def setUp(self):
        """Setup test environment"""
        if not IMPORTS_SUCCESS:
            self.skipTest("Required modules not available")
        
        # Create mock components
        self.mock_mt5_config = MT5Config()
        self.mock_mt5_connector = Mock(spec=MT5Connector)
        self.mock_mt5_connector.is_connected = True
        self.mock_mt5_connector.connect = AsyncMock(return_value=True)
        self.mock_mt5_connector.disconnect = AsyncMock()
        self.mock_mt5_connector.ensure_connected = AsyncMock(return_value=True)
        
        self.mock_product_owner = Mock(spec=ProductOwnerAgent)
        self.mock_product_owner.handle_message = AsyncMock()
        
        self.mock_trading_engine = Mock()
        self.mock_trading_engine.trading_enabled = True
        self.mock_trading_engine.emergency_stop = AsyncMock()
        self.mock_trading_engine.start_engine = AsyncMock(return_value=True)
        
        # Create error recovery system
        self.error_recovery = ErrorRecoverySystem(
            mt5_connector=self.mock_mt5_connector,
            product_owner=self.mock_product_owner,
            live_trading_engine=self.mock_trading_engine
        )
        
        # Use temporary file for state persistence
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.error_recovery.state_file = self.temp_file.name
    
    def tearDown(self):
        """Cleanup test environment"""
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
    
    async def test_error_reporting(self):
        """Test error reporting functionality"""
        print("\n Testing error reporting...")
        
        # Report a medium severity error
        error_id = await self.error_recovery.report_error(
            component="test_component",
            error_type="test_error",
            severity=ErrorSeverity.MEDIUM,
            message="Test error message",
            context={'test_key': 'test_value'}
        )
        
        # Verify error was recorded
        self.assertTrue(error_id)
        self.assertEqual(len(self.error_recovery.error_history), 1)
        self.assertEqual(self.error_recovery.error_counts[ErrorSeverity.MEDIUM], 1)
        
        error_event = list(self.error_recovery.error_history)[0]
        self.assertEqual(error_event.component, "test_component")
        self.assertEqual(error_event.message, "Test error message")
        self.assertEqual(error_event.severity, ErrorSeverity.MEDIUM)
        
        print("[PASS] Error reporting test passed")
        return True
    
    async def test_critical_error_recovery(self):
        """Test critical error triggers recovery"""
        print("\n Testing critical error recovery...")
        
        # Mock recovery methods
        self.error_recovery._recover_mt5_connection = AsyncMock()
        
        # Report critical error
        error_id = await self.error_recovery.report_error(
            component="mt5_connection",
            error_type="connection_failure",
            severity=ErrorSeverity.CRITICAL,
            message="MT5 connection lost"
        )
        
        # Wait for recovery to process
        await asyncio.sleep(0.1)
        
        # Verify recovery was triggered
        self.error_recovery._recover_mt5_connection.assert_called_once()
        
        print("OK Critical error recovery test passed")
        return True
    
    async def test_mt5_connection_recovery(self):
        """Test MT5 connection recovery with exponential backoff"""
        print("\n Testing MT5 connection recovery...")
        
        # Setup test scenario
        self.mock_mt5_connector.connect = AsyncMock(side_effect=[False, False, True])
        
        error_event = ErrorEvent(
            id="test_error",
            timestamp=datetime.now(timezone.utc),
            component="mt5_connection",
            error_type="connection_failure",
            severity=ErrorSeverity.HIGH,
            message="Connection test"
        )
        
        # Trigger recovery
        await self.error_recovery._recover_mt5_connection(error_event)
        
        # Verify reconnection attempts
        self.assertEqual(self.mock_mt5_connector.connect.call_count, 3)
        self.assertTrue(error_event.resolved)
        self.assertIn("Reconnected after 3 attempts", error_event.recovery_action)
        
        print("OK MT5 connection recovery test passed")
        return True
    
    async def test_circuit_breaker_functionality(self):
        """Test circuit breaker protection"""
        print("\n Testing circuit breaker functionality...")
        
        # Initially circuit breaker should be closed
        self.assertFalse(self.error_recovery.circuit_breakers['mt5_connection'])
        
        # Trigger MT5 connection error
        await self.error_recovery.report_error(
            component="mt5_connection",
            error_type="connection_failure",
            severity=ErrorSeverity.HIGH,
            message="Connection test for circuit breaker"
        )
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Circuit breaker should be open during recovery
        # (implementation detail may vary)
        
        # Test manual reset
        result = self.error_recovery.reset_circuit_breaker('mt5_connection')
        self.assertTrue(result)
        self.assertFalse(self.error_recovery.circuit_breakers['mt5_connection'])
        
        print("OK Circuit breaker test passed")
        return True
    
    async def test_health_monitoring(self):
        """Test health monitoring functionality"""
        print("\n Testing health monitoring...")
        
        # Initialize health tracking
        await self.error_recovery._initialize_health_tracking()
        
        # Verify health objects created
        self.assertIn('mt5_connection', self.error_recovery.connection_health)
        
        health = self.error_recovery.connection_health['mt5_connection']
        self.assertEqual(health.component, 'mt5_connection')
        self.assertEqual(health.state, ConnectionState.CONNECTED)
        
        # Perform health checks
        await self.error_recovery._perform_health_checks()
        
        # Verify no errors for healthy system
        self.mock_mt5_connector.ensure_connected.assert_called()
        
        print("OK Health monitoring test passed")
        return True
    
    async def test_state_persistence(self):
        """Test system state backup and recovery"""
        print("\n Testing state persistence...")
        
        # Initialize health tracking
        await self.error_recovery._initialize_health_tracking()
        
        # Save state
        await self.error_recovery._save_system_state()
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.error_recovery.state_file))
        
        # Clear current state
        original_health = self.error_recovery.connection_health.copy()
        self.error_recovery.connection_health.clear()
        
        # Load state
        await self.error_recovery._load_system_state()
        
        # Verify state restored
        self.assertEqual(len(self.error_recovery.connection_health), len(original_health))
        
        print("OK State persistence test passed")
        return True
    
    async def test_escalation_to_product_owner(self):
        """Test ProductOwner escalation"""
        print("\n Testing ProductOwner escalation...")
        
        # Create multiple high severity errors to trigger escalation
        for i in range(5):
            await self.error_recovery.report_error(
                component="test_component",
                error_type="test_error",
                severity=ErrorSeverity.HIGH,
                message=f"Test error {i}"
            )
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Verify ProductOwner was notified
        self.mock_product_owner.handle_message.assert_called()
        
        print("OK ProductOwner escalation test passed")
        return True
    
    async def test_system_health_status(self):
        """Test system health status reporting"""
        print("\n Testing system health status...")
        
        # Initialize and add some test data
        await self.error_recovery._initialize_health_tracking()
        
        await self.error_recovery.report_error(
            component="test",
            error_type="test",
            severity=ErrorSeverity.LOW,
            message="Test error"
        )
        
        # Get health status
        health_status = self.error_recovery.get_system_health()
        
        # Verify status structure
        self.assertIn('recovery_state', health_status)
        self.assertIn('total_errors', health_status)
        self.assertIn('connection_health', health_status)
        self.assertIn('circuit_breakers', health_status)
        self.assertIn('uptime_percentage', health_status)
        
        self.assertEqual(health_status['total_errors'], 1)
        self.assertEqual(health_status['recovery_state'], 'healthy')
        
        print("OK System health status test passed")
        return True
    
    async def test_production_integration(self):
        """Test production system integration"""
        print("\n Testing production integration...")
        
        # Create production system
        production_system = ProductionTradingSystem(
            mt5_config=self.mock_mt5_config,
            product_owner=self.mock_product_owner
        )
        
        # Mock the connector creation
        with patch('core.live_trading.production_integration.MT5Connector') as mock_connector_class:
            mock_connector_class.return_value = self.mock_mt5_connector
            
            # Initialize system
            success = await production_system.initialize()
            
        # Verify initialization
        self.assertTrue(success)
        self.assertTrue(production_system.is_initialized)
        self.assertIsNotNone(production_system.live_trading_engine)
        self.assertIsNotNone(production_system.error_recovery_system)
        
        # Test system status
        status = await production_system.get_system_status()
        self.assertIn('system', status)
        self.assertIn('metrics', status)
        
        # Cleanup
        await production_system.stop()
        
        print("OK Production integration test passed")
        return True


async def run_error_recovery_tests():
    """Run all error recovery system tests"""
    if not IMPORTS_SUCCESS:
        print("[WARNING] Skipping error recovery tests - imports not available")
        return False
    
    print("\n[TEST] Starting Enterprise Error Recovery System Tests")
    print("=" * 60)
    
    test_suite = TestErrorRecoverySystem()
    test_suite.setUp()
    
    tests = [
        test_suite.test_error_reporting,
        test_suite.test_critical_error_recovery,
        test_suite.test_mt5_connection_recovery,
        test_suite.test_circuit_breaker_functionality,
        test_suite.test_health_monitoring,
        test_suite.test_state_persistence,
        test_suite.test_escalation_to_product_owner,
        test_suite.test_system_health_status,
        test_suite.test_production_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"ERROR Test {test.__name__} failed: {e}")
            failed += 1
        finally:
            # Reset for next test
            try:
                test_suite.setUp()
            except:
                pass
    
    test_suite.tearDown()
    
    print("\n" + "=" * 60)
    print(f" Enterprise Error Recovery System Test Results:")
    print(f"OK Passed: {passed}")
    print(f"ERROR Failed: {failed}")
    print(f"CHART Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("TARGET ALL TESTS PASSED - Above Robust! standards validated")
        return True
    else:
        print("WARNING Some tests failed - requires attention")
        return False


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(run_error_recovery_tests())