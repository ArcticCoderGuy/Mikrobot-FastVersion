"""
Quick Test Runner - ML Data Ingestion Components
Standalone test without external dependencies

Session #2 ML-Enhanced Core - Quick Validation
"""

import asyncio
import sys
import os
import time
from datetime import datetime, timezone

# Add source path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print formatted test result"""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {test_name}: {details}")
    return passed

async def test_data_models():
    """Test basic data model functionality"""
    print("\n[Testing Data Models...]")
    
    try:
        from data_ingestion.data_models import TickData, OHLCVData, MarketData, AssetType, DataQuality
        
        # Test TickData creation and calculations
        tick = TickData(
            timestamp=datetime.now(timezone.utc),
            symbol="EURUSD",
            bid=1.1000,
            ask=1.1001,
            spread=0.0001,
            asset_type=AssetType.FOREX,
            quality=DataQuality.EXCELLENT
        )
        
        mid_price_correct = print_test_result(
            "TickData mid_price calculation",
            abs(tick.mid_price - 1.10005) < 0.00001,
            f"Mid price: {tick.mid_price}"
        )
        
        serialization_works = print_test_result(
            "TickData serialization",
            'symbol' in tick.to_dict() and 'mid_price' in tick.to_dict(),
            "Contains required keys"
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
        
        pip_calculation = print_test_result(
            "OHLCV pip calculations",
            ohlcv.range_pips > 0 and ohlcv.body_pips >= 0,
            f"Range: {ohlcv.range_pips:.1f} pips, Body: {ohlcv.body_pips:.1f} pips"
        )
        
        # Test MarketData container
        market_data = MarketData(
            symbol="EURUSD",
            asset_type=AssetType.FOREX,
            tick_data=tick,
            ohlcv_data=ohlcv
        )
        
        container_works = print_test_result(
            "MarketData container",
            market_data.current_price == tick.mid_price,
            f"Current price: {market_data.current_price}"
        )
        
        return all([mid_price_correct, serialization_works, pip_calculation, container_works])
        
    except Exception as e:
        print_test_result("Data Models Import", False, f"Exception: {str(e)}")
        return False

async def test_data_validator():
    """Test data validation functionality"""
    print("\n[Testing Data Validator...]")
    
    try:
        from data_ingestion.data_validator import DataValidator
        from data_ingestion.data_models import TickData, MarketData, AssetType, DataQuality
        
        validator = DataValidator()
        
        # Test valid data
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
        
        valid_result = await validator.validate(valid_data)
        validation_passes = print_test_result(
            "Valid data validation",
            valid_result.is_valid,
            f"Errors: {valid_result.errors}"
        )
        
        # Test invalid data (bid >= ask)
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
        
        invalid_result = await validator.validate(invalid_data)
        error_detection = print_test_result(
            "Invalid data detection",
            not invalid_result.is_valid,
            f"Correctly rejected: {len(invalid_result.errors)} errors"
        )
        
        # Test validation performance
        start_time = time.perf_counter()
        for _ in range(10):
            await validator.validate(valid_data)
        avg_time = ((time.perf_counter() - start_time) * 1000) / 10
        
        performance_ok = print_test_result(
            "Validation performance",
            avg_time < 5.0,
            f"Average: {avg_time:.2f}ms per validation"
        )
        
        return all([validation_passes, error_detection, performance_ok])
        
    except Exception as e:
        print_test_result("Data Validator", False, f"Exception: {str(e)}")
        return False

async def test_performance_monitor():
    """Test performance monitoring"""
    print("\n[Testing Performance Monitor...]")
    
    try:
        from data_ingestion.performance_monitor import IngestionPerformanceMonitor, PerformanceThresholds
        
        # Create monitor with test thresholds
        thresholds = PerformanceThresholds(
            latency_warning=5.0,
            latency_error=10.0
        )
        
        alerts_received = []
        def test_alert_callback(alert):
            alerts_received.append(alert)
        
        monitor = IngestionPerformanceMonitor(
            thresholds=thresholds,
            alert_callback=test_alert_callback
        )
        
        await monitor.start_monitoring()
        
        # Record some metrics
        monitor.record_latency(3.0, "EURUSD")
        monitor.record_latency(2.5, "GBPUSD")
        monitor.record_message("EURUSD", success=True)
        monitor.record_message("GBPUSD", success=True)
        
        stats = monitor.get_performance_stats()
        stats_generation = print_test_result(
            "Stats generation",
            "latency_stats" in stats and "message_stats" in stats,
            f"Keys: {list(stats.keys())}"
        )
        
        # Test alert triggering
        monitor.record_latency(15.0, "EURUSD")  # Should trigger alert
        await asyncio.sleep(0.1)
        
        alert_system = print_test_result(
            "Alert system",
            len(alerts_received) > 0,
            f"Alerts triggered: {len(alerts_received)}"
        )
        
        # Test latency calculations
        latency_stats = stats.get("latency_stats", {})
        calculations = print_test_result(
            "Latency calculations",
            "avg_ms" in latency_stats and latency_stats["avg_ms"] > 0,
            f"Avg latency: {latency_stats.get('avg_ms', 0):.2f}ms"
        )
        
        await monitor.stop_monitoring()
        
        return all([stats_generation, alert_system, calculations])
        
    except Exception as e:
        print_test_result("Performance Monitor", False, f"Exception: {str(e)}")
        return False

async def test_ingestion_engine():
    """Test ingestion engine basic functionality"""
    print("\n[Testing Ingestion Engine...]")
    
    try:
        from data_ingestion.data_ingestion_engine import DataIngestionEngine, DataConnector
        from data_ingestion.data_models import TickData, AssetType, DataSource, DataQuality
        
        # Create simple mock connector
        class SimpleConnector(DataConnector):
            def __init__(self):
                super().__init__("test", DataSource.CUSTOM)
            
            async def connect(self):
                self.is_connected = True
                return True
            
            async def disconnect(self):
                self.is_connected = False
                return True
            
            async def subscribe_symbol(self, symbol, asset_type):
                return self.is_connected
            
            async def unsubscribe_symbol(self, symbol):
                return True
            
            async def get_tick_data(self, symbol):
                return TickData(
                    timestamp=datetime.now(timezone.utc),
                    symbol=symbol,
                    bid=1.1000,
                    ask=1.1001,
                    spread=0.0001,
                    asset_type=AssetType.FOREX,
                    quality=DataQuality.EXCELLENT
                )
            
            async def get_ohlcv_data(self, symbol, timeframe):
                return None
        
        # Test engine
        engine = DataIngestionEngine(max_workers=3)
        connector = SimpleConnector()
        
        registration = print_test_result(
            "Connector registration",
            engine.register_connector(connector),
            "Connector registered successfully"
        )
        
        startup = await engine.start()
        startup_success = print_test_result(
            "Engine startup",
            startup,
            f"Started with {len(engine.connectors)} connectors"
        )
        
        if startup:
            # Test callback system
            received_data = []
            def test_callback(data):
                received_data.append(data)
            
            engine.register_callback(test_callback)
            
            # Test data ingestion
            test_tick = TickData(
                timestamp=datetime.now(timezone.utc),
                symbol="EURUSD",
                bid=1.1000,
                ask=1.1001,
                spread=0.0001,
                asset_type=AssetType.FOREX,
                quality=DataQuality.EXCELLENT
            )
            
            engine.ingest_tick_data(test_tick)
            await asyncio.sleep(0.2)  # Wait for processing
            
            callback_system = print_test_result(
                "Callback system",
                len(received_data) > 0,
                f"Processed {len(received_data)} messages"
            )
            
            # Test metrics
            metrics = engine.get_metrics()
            metrics_collection = print_test_result(
                "Metrics collection",
                "total_messages" in metrics,
                f"Metrics: {list(metrics.keys())}"
            )
            
            await engine.stop()
            
            return all([registration, startup_success, callback_system, metrics_collection])
        else:
            return False
        
    except Exception as e:
        print_test_result("Ingestion Engine", False, f"Exception: {str(e)}")
        return False

async def test_integration_example():
    """Test ML integration example (basic functionality)"""
    print("\n[Testing ML Integration...]")
    
    try:
        # Test basic imports and initialization
        from data_ingestion.ml_integration_example import MLEnhancedDataIngestion
        
        # Mock ProductOwner to avoid dependencies
        import unittest.mock
        
        with unittest.mock.patch('data_ingestion.ml_integration_example.ProductOwnerAgent'):
            ml_system = MLEnhancedDataIngestion()
            
            initialization = print_test_result(
                "ML system initialization",
                ml_system.engine is not None and ml_system.performance_monitor is not None,
                "Core components initialized"
            )
            
            # Test ML callback registration
            test_data = []
            
            def test_ml_callback(features):
                test_data.append(features)
            
            ml_system.register_ml_callback(test_ml_callback)
            
            callback_registration = print_test_result(
                "ML callback registration",
                len(ml_system.ml_callbacks) == 1,
                f"Callbacks: {len(ml_system.ml_callbacks)}"
            )
            
            # Test feature preprocessing
            from data_ingestion.data_models import MarketData, TickData, AssetType, DataQuality
            
            test_market_data = MarketData(
                symbol="EURUSD",
                asset_type=AssetType.FOREX,
                tick_data=TickData(
                    timestamp=datetime.now(timezone.utc),
                    symbol="EURUSD",
                    bid=1.1000,
                    ask=1.1001,
                    spread=0.0001,
                    asset_type=AssetType.FOREX,
                    quality=DataQuality.EXCELLENT
                )
            )
            test_market_data.processing_latency_ms = 2.5
            test_market_data.validation_passed = True
            
            await ml_system._ml_preprocessing_callback(test_market_data)
            
            feature_extraction = print_test_result(
                "Feature extraction",
                len(test_data) > 0 and 'symbol' in test_data[0],
                f"Features extracted: {list(test_data[0].keys()) if test_data else 'None'}"
            )
            
            # Test quality score conversion
            if test_data:
                quality_score = test_data[0].get('quality_score', 0)
                quality_conversion = print_test_result(
                    "Quality score conversion",
                    quality_score == 1.0,  # Excellent should be 1.0
                    f"Quality score: {quality_score}"
                )
            else:
                quality_conversion = False
            
            return all([initialization, callback_registration, feature_extraction, quality_conversion])
        
    except Exception as e:
        print_test_result("ML Integration", False, f"Exception: {str(e)}")
        return False

async def run_all_tests():
    """Run all quick tests"""
    print("ML Data Ingestion - Quick Test Suite")
    print("=" * 50)
    
    tests = [
        ("Data Models", test_data_models),
        ("Data Validator", test_data_validator),
        ("Performance Monitor", test_performance_monitor),
        ("Ingestion Engine", test_ingestion_engine),
        ("ML Integration", test_integration_example)
    ]
    
    results = []
    start_time = time.perf_counter()
    
    for test_name, test_func in tests:
        print(f"\n[Running {test_name} tests...]")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[FAIL] {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    total_time = time.perf_counter() - start_time
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    print(f"Total Time: {total_time:.2f} seconds")
    
    if failed == 0:
        print("\nALL TESTS PASSED!")
        print("ML Data Ingestion System - Ready for Production")
        print("Session #2 ML-Enhanced Core - VALIDATED")
    else:
        print(f"\n{failed} TESTS FAILED")
        print("Please review failed components")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)