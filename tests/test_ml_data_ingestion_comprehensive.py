from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Comprehensive ML Data Ingestion Test Suite
Tests all essential components with Fail/Pass methodology

Session #2 ML-Enhanced Core - Complete System Validation
"""

import pytest
import asyncio
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock

# Import components to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from data_ingestion.data_ingestion_engine import DataIngestionEngine, DataConnector
from data_ingestion.data_models import (
    TickData, OHLCVData, MarketData, AssetType, 
    DataSource, DataQuality, ValidationResult
)
from data_ingestion.data_validator import DataValidator, DataQualityMonitor
from data_ingestion.forex_connector import ForexDataConnector
from data_ingestion.crypto_connector import CryptoDataConnector
from data_ingestion.indices_connector import IndicesDataConnector
from data_ingestion.performance_monitor import IngestionPerformanceMonitor, PerformanceThresholds
from data_ingestion.ml_integration_example import MLEnhancedDataIngestion

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestResult:
    """Test result tracking"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name: str, passed: bool, details: str = ""):
        """Add test result"""
        status = "PASS" if passed else "FAIL"
        self.results.append(f"[{status}] {test_name}: {details}")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        
        # Log result
        log_func = logger.info if passed else logger.error
        log_func(f"{status}: {test_name} - {details}")
    
    def get_summary(self) -> str:
        """Get test summary"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        summary = f"""
=== ML DATA INGESTION TEST RESULTS ===
Total Tests: {total}
Passed: {self.passed}
Failed: {self.failed}
Success Rate: {success_rate:.1f}%

{'OK ALL TESTS PASSED' if self.failed == 0 else 'ERROR SOME TESTS FAILED'}

Detailed Results:
"""
        for result in self.results:
            summary += f"  {result}\n"
        
        return summary


class MockDataConnector(DataConnector):
    """Mock connector for testing"""
    
    def __init__(self, connector_id: str = "mock"):
        super().__init__(connector_id, DataSource.CUSTOM)
        self.connect_should_fail = False
        self.data_should_fail = False
        self.simulate_latency = 0.001  # 1ms
    
    async def connect(self) -> bool:
        await asyncio.sleep(self.simulate_latency)
        if self.connect_should_fail:
            return False
        self.is_connected = True
        return True
    
    async def disconnect(self) -> bool:
        self.is_connected = False
        return True
    
    async def subscribe_symbol(self, symbol: str, asset_type: AssetType) -> bool:
        return self.is_connected and not self.data_should_fail
    
    async def unsubscribe_symbol(self, symbol: str) -> bool:
        return True
    
    async def get_tick_data(self, symbol: str) -> Optional[TickData]:
        if not self.is_connected or self.data_should_fail:
            return None
        
        await asyncio.sleep(self.simulate_latency)
        return TickData(
            timestamp=datetime.now(timezone.utc),
            symbol=symbol,
            bid=1.1000,
            ask=1.1001,
            spread=0.0001,
            asset_type=AssetType.FOREX,
            source=DataSource.CUSTOM,
            quality=DataQuality.EXCELLENT,
            latency_ms=self.simulate_latency * 1000
        )
    
    async def get_ohlcv_data(self, symbol: str, timeframe: str) -> Optional[OHLCVData]:
        if not self.is_connected or self.data_should_fail:
            return None
        
        await asyncio.sleep(self.simulate_latency)
        return OHLCVData(
            timestamp=datetime.now(timezone.utc),
            symbol=symbol,
            open=1.1000,
            high=1.1010,
            low=1.0990,
            close=1.1005,
            volume=1000.0,
            timeframe=timeframe,
            asset_type=AssetType.FOREX,
            source=DataSource.CUSTOM,
            quality=DataQuality.EXCELLENT
        )


class MLDataIngestionTestSuite:
    """Comprehensive test suite for ML Data Ingestion system"""
    
    def __init__(self):
        self.results = TestResult()
    
    async def run_all_tests(self) -> TestResult:
        """Run all tests"""
        logger.info("ROCKET Starting ML Data Ingestion Test Suite")
        
        # Core component tests
        await self.test_data_models()
        await self.test_data_validator()
        await self.test_performance_monitor()
        await self.test_data_ingestion_engine()
        
        # Connector tests (with mocks to avoid external dependencies)
        await self.test_connectors()
        
        # Integration tests
        await self.test_ml_integration()
        
        # Performance tests
        await self.test_performance_requirements()
        
        logger.info("OK Test Suite Complete")
        return self.results
    
    async def test_data_models(self):
        """Test data model functionality"""
        logger.info("CHART Testing Data Models...")
        
        try:
            # Test TickData
            tick = TickData(
                timestamp=datetime.now(timezone.utc),
                symbol="EURUSD",
                bid=1.1000,
                ask=1.1001,
                spread=0.0001,
                asset_type=AssetType.FOREX
            )
            
            # Test calculations
            mid_price = tick.mid_price
            self.results.add_result(
                "TickData mid_price calculation",
                abs(mid_price - 1.10005) < 0.00001,
                f"Expected: 1.10005, Got: {mid_price}"
            )
            
            # Test serialization
            tick_dict = tick.to_dict()
            self.results.add_result(
                "TickData serialization",
                'symbol' in tick_dict and 'mid_price' in tick_dict,
                f"Keys: {list(tick_dict.keys())}"
            )
            
            # Test OHLCVData
            ohlcv = OHLCVData(
                timestamp=datetime.now(timezone.utc),
                symbol="EURUSD",
                open=1.1000,
                high=1.1010,
                low=1.0990,
                close=1.1005,
                volume=1000.0,
                timeframe="5m",
                asset_type=AssetType.FOREX
            )
            
            # Test pip calculations
            range_pips = ohlcv.range_pips
            self.results.add_result(
                "OHLCV range_pips calculation",
                range_pips > 0,
                f"Range pips: {range_pips:.1f}"
            )
            
            # Test MarketData container
            market_data = MarketData(
                symbol="EURUSD",
                asset_type=AssetType.FOREX,
                tick_data=tick
            )
            
            current_price = market_data.current_price
            self.results.add_result(
                "MarketData current_price",
                current_price == mid_price,
                f"Expected: {mid_price}, Got: {current_price}"
            )
            
        except Exception as e:
            self.results.add_result("Data Models", False, f"Exception: {str(e)}")
    
    async def test_data_validator(self):
        """Test data validation functionality"""
        logger.info(" Testing Data Validator...")
        
        try:
            validator = DataValidator()
            
            # Test valid tick data
            valid_tick = TickData(
                timestamp=datetime.now(timezone.utc),
                symbol="EURUSD",
                bid=1.1000,
                ask=1.1001,
                spread=0.0001,
                asset_type=AssetType.FOREX,
                quality=DataQuality.EXCELLENT
            )
            
            valid_data = MarketData(
                symbol="EURUSD",
                asset_type=AssetType.FOREX,
                tick_data=valid_tick
            )
            
            result = await validator.validate(valid_data)
            self.results.add_result(
                "Data Validator - Valid Data",
                result.is_valid,
                f"Validation passed: {result.is_valid}, Errors: {result.errors}"
            )
            
            # Test invalid tick data (bid >= ask)
            invalid_tick = TickData(
                timestamp=datetime.now(timezone.utc),
                symbol="EURUSD",
                bid=1.1001,  # Invalid: bid >= ask
                ask=1.1000,
                spread=0.0001,
                asset_type=AssetType.FOREX
            )
            
            invalid_data = MarketData(
                symbol="EURUSD",
                asset_type=AssetType.FOREX,
                tick_data=invalid_tick
            )
            
            result = await validator.validate(invalid_data)
            self.results.add_result(
                "Data Validator - Invalid Data Detection",
                not result.is_valid,
                f"Correctly rejected invalid data: {result.errors}"
            )
            
            # Test validation latency
            start_time = time.perf_counter()
            await validator.validate(valid_data)
            validation_time = (time.perf_counter() - start_time) * 1000
            
            self.results.add_result(
                "Data Validator - Performance",
                validation_time < 5.0,  # Should be under 5ms
                f"Validation time: {validation_time:.2f}ms"
            )
            
            # Test quality monitor
            monitor = DataQualityMonitor()
            monitor.record_quality("EURUSD", DataQuality.EXCELLENT)
            monitor.record_latency(2.5)
            
            report = monitor.get_quality_report("EURUSD")
            self.results.add_result(
                "Quality Monitor - Reporting",
                "symbols" in report and "EURUSD" in report["symbols"],
                f"Report generated successfully"
            )
            
        except Exception as e:
            self.results.add_result("Data Validator", False, f"Exception: {str(e)}")
    
    async def test_performance_monitor(self):
        """Test performance monitoring"""
        logger.info("FAST Testing Performance Monitor...")
        
        try:
            # Custom thresholds for testing
            thresholds = PerformanceThresholds(
                latency_warning=5.0,
                latency_error=10.0,
                throughput_warning=10.0
            )
            
            alerts_received = []
            
            def alert_callback(alert):
                alerts_received.append(alert)
            
            monitor = IngestionPerformanceMonitor(
                thresholds=thresholds,
                alert_callback=alert_callback
            )
            
            await monitor.start_monitoring()
            
            # Record normal metrics
            monitor.record_latency(3.0, "EURUSD")
            monitor.record_message("EURUSD", success=True)
            
            stats = monitor.get_performance_stats()
            self.results.add_result(
                "Performance Monitor - Basic Stats",
                "latency_stats" in stats and "message_stats" in stats,
                f"Stats generated: {list(stats.keys())}"
            )
            
            # Test alert generation
            monitor.record_latency(15.0, "EURUSD")  # Should trigger error alert
            await asyncio.sleep(0.1)  # Allow alert processing
            
            self.results.add_result(
                "Performance Monitor - Alert Generation",
                len(alerts_received) > 0,
                f"Alerts received: {len(alerts_received)}"
            )
            
            # Test latency calculation
            latency_stats = stats.get("latency_stats", {})
            self.results.add_result(
                "Performance Monitor - Latency Stats",
                "avg_ms" in latency_stats,
                f"Latency stats: {latency_stats}"
            )
            
            await monitor.stop_monitoring()
            
        except Exception as e:
            self.results.add_result("Performance Monitor", False, f"Exception: {str(e)}")
    
    async def test_data_ingestion_engine(self):
        """Test data ingestion engine"""
        logger.info("ROCKET Testing Data Ingestion Engine...")
        
        try:
            engine = DataIngestionEngine(max_workers=5)
            
            # Test connector registration
            mock_connector = MockDataConnector("test_connector")
            
            registration_success = engine.register_connector(mock_connector)
            self.results.add_result(
                "Engine - Connector Registration",
                registration_success,
                f"Connector registered: {registration_success}"
            )
            
            # Test engine startup
            startup_success = await engine.start()
            self.results.add_result(
                "Engine - Startup",
                startup_success,
                f"Engine started: {startup_success}"
            )
            
            if startup_success:
                # Test symbol subscription
                subscription_success = await engine.subscribe_symbol(
                    "EURUSD", 
                    AssetType.FOREX
                )
                self.results.add_result(
                    "Engine - Symbol Subscription",
                    subscription_success,
                    f"Subscription success: {subscription_success}"
                )
                
                # Test data callback registration
                callback_data = []
                
                def test_callback(data):
                    callback_data.append(data)
                
                engine.register_callback(test_callback)
                
                # Simulate data ingestion
                test_tick = TickData(
                    timestamp=datetime.now(timezone.utc),
                    symbol="EURUSD",
                    bid=1.1000,
                    ask=1.1001,
                    spread=0.0001,
                    asset_type=AssetType.FOREX
                )
                
                engine.ingest_tick_data(test_tick, priority=1)
                
                # Wait for processing
                await asyncio.sleep(0.5)
                
                self.results.add_result(
                    "Engine - Data Processing",
                    len(callback_data) > 0,
                    f"Callbacks triggered: {len(callback_data)}"
                )
                
                # Test metrics
                metrics = engine.get_metrics()
                self.results.add_result(
                    "Engine - Metrics Collection",
                    "total_messages" in metrics,
                    f"Metrics: {list(metrics.keys())}"
                )
                
                # Test performance
                start_time = time.perf_counter()
                for i in range(10):
                    engine.ingest_tick_data(test_tick, priority=5)
                
                await asyncio.sleep(0.1)
                processing_time = (time.perf_counter() - start_time) * 1000
                
                self.results.add_result(
                    "Engine - Batch Processing Performance",
                    processing_time < 100,  # Should process 10 items in <100ms
                    f"Batch processing time: {processing_time:.2f}ms"
                )
            
            # Clean shutdown
            await engine.stop()
            
        except Exception as e:
            self.results.add_result("Data Ingestion Engine", False, f"Exception: {str(e)}")
    
    async def test_connectors(self):
        """Test data connectors (with mocks)"""
        logger.info(" Testing Data Connectors...")
        
        # Test Mock Connector (validates connector interface)
        try:
            mock_connector = MockDataConnector("test")
            
            # Test connection
            connect_success = await mock_connector.connect()
            self.results.add_result(
                "Connector Interface - Connection",
                connect_success and mock_connector.is_connected,
                f"Connected: {connect_success}"
            )
            
            # Test subscription
            if connect_success:
                sub_success = await mock_connector.subscribe_symbol("EURUSD", AssetType.FOREX)
                self.results.add_result(
                    "Connector Interface - Subscription",
                    sub_success,
                    f"Subscription: {sub_success}"
                )
                
                # Test data retrieval
                tick_data = await mock_connector.get_tick_data("EURUSD")
                self.results.add_result(
                    "Connector Interface - Tick Data",
                    tick_data is not None and tick_data.symbol == "EURUSD",
                    f"Data retrieved: {tick_data is not None}"
                )
                
                # Test OHLCV data
                ohlcv_data = await mock_connector.get_ohlcv_data("EURUSD", "5m")
                self.results.add_result(
                    "Connector Interface - OHLCV Data",
                    ohlcv_data is not None and ohlcv_data.timeframe == "5m",
                    f"OHLCV retrieved: {ohlcv_data is not None}"
                )
                
                # Test latency
                start_time = time.perf_counter()
                await mock_connector.get_tick_data("EURUSD")
                latency = (time.perf_counter() - start_time) * 1000
                
                self.results.add_result(
                    "Connector Interface - Latency",
                    latency < 10,  # Should be under 10ms
                    f"Latency: {latency:.2f}ms"
                )
            
            # Test disconnection
            disconnect_success = await mock_connector.disconnect()
            self.results.add_result(
                "Connector Interface - Disconnection",
                disconnect_success and not mock_connector.is_connected,
                f"Disconnected: {disconnect_success}"
            )
            
        except Exception as e:
            self.results.add_result("Connector Interface", False, f"Exception: {str(e)}")
        
        # Test error handling
        try:
            error_connector = MockDataConnector("error_test")
            error_connector.connect_should_fail = True
            
            connect_fail = await error_connector.connect()
            self.results.add_result(
                "Connector Error Handling - Connection Failure",
                not connect_fail,
                f"Correctly failed connection: {not connect_fail}"
            )
            
            error_connector.data_should_fail = True
            error_connector.is_connected = True  # Force connected state
            
            tick_data = await error_connector.get_tick_data("EURUSD")
            self.results.add_result(
                "Connector Error Handling - Data Failure",
                tick_data is None,
                f"Correctly returned None on data failure"
            )
            
        except Exception as e:
            self.results.add_result("Connector Error Handling", False, f"Exception: {str(e)}")
    
    async def test_ml_integration(self):
        """Test ML integration components"""
        logger.info(" Testing ML Integration...")
        
        try:
            # Test ML callback system
            ml_data_received = []
            
            async def test_ml_callback(features: Dict[str, Any]):
                ml_data_received.append(features)
            
            # Create test system (with mocked ProductOwner to avoid dependencies)
            with patch('data_ingestion.ml_integration_example.ProductOwnerAgent') as mock_po:
                mock_po_instance = Mock()
                mock_po_instance.handle_message = AsyncMock()
                mock_po.return_value = mock_po_instance
                
                ml_system = MLEnhancedDataIngestion()
                ml_system.register_ml_callback(test_ml_callback)
                
                self.results.add_result(
                    "ML Integration - Callback Registration",
                    len(ml_system.ml_callbacks) == 1,
                    f"Callbacks registered: {len(ml_system.ml_callbacks)}"
                )
                
                # Test ML preprocessing
                test_data = MarketData(
                    symbol="EURUSD",
                    asset_type=AssetType.FOREX,
                    tick_data=TickData(
                        timestamp=datetime.now(timezone.utc),
                        symbol="EURUSD",
                        bid=1.1000,
                        ask=1.1001,
                        spread=0.0001,
                        asset_type=AssetType.FOREX,
                        quality=DataQuality.EXCELLENT,
                        latency_ms=2.5
                    )
                )
                test_data.processing_latency_ms = 2.5
                test_data.validation_passed = True
                
                await ml_system._ml_preprocessing_callback(test_data)
                
                self.results.add_result(
                    "ML Integration - Preprocessing Pipeline",
                    len(ml_data_received) > 0,
                    f"ML callbacks executed: {len(ml_data_received)}"
                )
                
                # Verify ML features
                if ml_data_received:
                    features = ml_data_received[0]
                    expected_keys = ['timestamp', 'symbol', 'price', 'quality_score', 'bid', 'ask']
                    has_keys = all(key in features for key in expected_keys)
                    
                    self.results.add_result(
                        "ML Integration - Feature Extraction",
                        has_keys,
                        f"Features: {list(features.keys())}"
                    )
                    
                    # Test quality score conversion
                    quality_score = features.get('quality_score', 0)
                    self.results.add_result(
                        "ML Integration - Quality Score Conversion",
                        quality_score == 1.0,  # Excellent = 1.0
                        f"Quality score: {quality_score}"
                    )
            
        except Exception as e:
            self.results.add_result("ML Integration", False, f"Exception: {str(e)}")
    
    async def test_performance_requirements(self):
        """Test that system meets performance requirements"""
        logger.info("FAST Testing Performance Requirements...")
        
        try:
            # Test latency requirement (<10ms)
            validator = DataValidator()
            
            test_data = MarketData(
                symbol="EURUSD",
                asset_type=AssetType.FOREX,
                tick_data=TickData(
                    timestamp=datetime.now(timezone.utc),
                    symbol="EURUSD",
                    bid=1.1000,
                    ask=1.1001,
                    spread=0.0001,
                    asset_type=AssetType.FOREX
                )
            )
            
            # Measure validation latency
            latencies = []
            for _ in range(100):  # Test 100 validations
                start_time = time.perf_counter()
                await validator.validate(test_data)
                latency = (time.perf_counter() - start_time) * 1000
                latencies.append(latency)
            
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
            
            self.results.add_result(
                "Performance - Validation Latency Average",
                avg_latency < 5.0,  # Target: <5ms average
                f"Average: {avg_latency:.2f}ms"
            )
            
            self.results.add_result(
                "Performance - Validation Latency P95",
                p95_latency < 10.0,  # Target: <10ms P95
                f"P95: {p95_latency:.2f}ms"
            )
            
            self.results.add_result(
                "Performance - Validation Latency Max",
                max_latency < 20.0,  # Target: <20ms max
                f"Max: {max_latency:.2f}ms"
            )
            
            # Test throughput capability
            engine = DataIngestionEngine(max_workers=5)
            mock_connector = MockDataConnector("throughput_test")
            mock_connector.simulate_latency = 0.001  # 1ms simulation
            
            engine.register_connector(mock_connector)
            await engine.start()
            
            processed_count = 0
            def count_callback(data):
                nonlocal processed_count
                processed_count += 1
            
            engine.register_callback(count_callback)
            
            # Send batch of messages
            start_time = time.perf_counter()
            for i in range(100):
                test_tick = TickData(
                    timestamp=datetime.now(timezone.utc),
                    symbol=f"TEST{i%10}",  # 10 different symbols
                    bid=1.1000,
                    ask=1.1001,
                    spread=0.0001,
                    asset_type=AssetType.FOREX
                )
                engine.ingest_tick_data(test_tick, priority=5)
            
            # Wait for processing
            await asyncio.sleep(1.0)
            processing_time = time.perf_counter() - start_time
            throughput = processed_count / processing_time
            
            self.results.add_result(
                "Performance - Throughput Capability",
                throughput > 50,  # Target: >50 messages/second
                f"Throughput: {throughput:.1f} msg/s"
            )
            
            await engine.stop()
            
            # Test memory efficiency (simplified check)
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            self.results.add_result(
                "Performance - Memory Usage",
                memory_mb < 200,  # Target: <200MB for test
                f"Memory: {memory_mb:.1f}MB"
            )
            
        except Exception as e:
            self.results.add_result("Performance Requirements", False, f"Exception: {str(e)}")


async def main():
    """Run comprehensive test suite"""
    print(" Starting ML Data Ingestion Comprehensive Test Suite")
    print("=" * 60)
    
    test_suite = MLDataIngestionTestSuite()
    results = await test_suite.run_all_tests()
    
    # Print results
    print(results.get_summary())
    
    # Return exit code
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    exit_code = asyncio.run(main())
    exit(exit_code)