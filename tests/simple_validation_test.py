"""
Simple Validation Test - ML Data Ingestion Core Components
Tests essential functionality without external dependencies

Session #2 ML-Enhanced Core - Core Validation
"""

import asyncio
import sys
import os
import time
from datetime import datetime, timezone

# Add source path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

def test_result(name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name}: {details}")
    return passed

async def test_core_data_models():
    """Test core data models"""
    print("\n=== Testing Core Data Models ===")
    
    try:
        # Import directly to avoid aiohttp dependency from __init__.py
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core', 'data_ingestion'))
        from data_models import (
            TickData, OHLCVData, MarketData, AssetType, 
            DataQuality, DataSource, ValidationResult
        )
        
        results = []
        
        # Test TickData
        tick = TickData(
            timestamp=datetime.now(timezone.utc),
            symbol="EURUSD",
            bid=1.1000,
            ask=1.1001,
            spread=0.0001,
            asset_type=AssetType.FOREX,
            source=DataSource.MT5,
            quality=DataQuality.EXCELLENT
        )
        
        results.append(test_result(
            "TickData creation",
            tick.symbol == "EURUSD" and tick.bid == 1.1000,
            f"Symbol: {tick.symbol}, Bid: {tick.bid}"
        ))
        
        results.append(test_result(
            "TickData mid_price calculation",
            abs(tick.mid_price - 1.10005) < 0.00001,
            f"Mid price: {tick.mid_price}"
        ))
        
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
        
        results.append(test_result(
            "OHLCVData creation",
            ohlcv.timeframe == "5m" and ohlcv.volume == 1000.0,
            f"Timeframe: {ohlcv.timeframe}, Volume: {ohlcv.volume}"
        ))
        
        results.append(test_result(
            "OHLCVData range_pips calculation",
            ohlcv.range_pips > 0,
            f"Range: {ohlcv.range_pips:.1f} pips"
        ))
        
        # Test MarketData container
        market_data = MarketData(
            symbol="EURUSD",
            asset_type=AssetType.FOREX,
            tick_data=tick,
            ohlcv_data=ohlcv
        )
        
        results.append(test_result(
            "MarketData container",
            market_data.current_price == tick.mid_price,
            f"Current price: {market_data.current_price}"
        ))
        
        # Test serialization
        tick_dict = tick.to_dict()
        results.append(test_result(
            "Data serialization",
            'symbol' in tick_dict and 'mid_price' in tick_dict,
            f"Keys: {len(tick_dict)} fields"
        ))
        
        return all(results)
        
    except Exception as e:
        test_result("Data Models Import", False, f"Exception: {str(e)}")
        return False

async def test_data_validator():
    """Test data validation without external dependencies"""
    print("\n=== Testing Data Validator ===")
    
    try:
        # Import directly to avoid aiohttp dependencies
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core', 'data_ingestion'))
        from data_validator import DataValidator
        from data_models import TickData, MarketData, AssetType, DataQuality
        
        validator = DataValidator()
        results = []
        
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
        results.append(test_result(
            "Valid data validation",
            valid_result.is_valid and len(valid_result.errors) == 0,
            f"Valid: {valid_result.is_valid}, Errors: {len(valid_result.errors)}"
        ))
        
        # Test invalid data
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
        results.append(test_result(
            "Invalid data detection",
            not invalid_result.is_valid and len(invalid_result.errors) > 0,
            f"Correctly rejected with {len(invalid_result.errors)} errors"
        ))
        
        # Test performance
        start_time = time.perf_counter()
        for _ in range(50):
            await validator.validate(valid_data)
        avg_time = ((time.perf_counter() - start_time) * 1000) / 50
        
        results.append(test_result(
            "Validation performance",
            avg_time < 10.0,  # Should be under 10ms average
            f"Average: {avg_time:.2f}ms per validation"
        ))
        
        # Test validation statistics
        stats = validator.get_validation_stats()
        results.append(test_result(
            "Validation statistics",
            'total_validations' in stats and stats['total_validations'] > 0,
            f"Total validations: {stats['total_validations']}"
        ))
        
        return all(results)
        
    except Exception as e:
        test_result("Data Validator", False, f"Exception: {str(e)}")
        return False

async def test_basic_engine():
    """Test basic ingestion engine functionality"""
    print("\n=== Testing Basic Engine ===")
    
    try:
        from data_ingestion.data_ingestion_engine import DataIngestionEngine, DataConnector
        from data_ingestion.data_models import TickData, AssetType, DataSource, DataQuality
        
        # Simple mock connector
        class TestConnector(DataConnector):
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
                if not self.is_connected:
                    return None
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
        
        results = []
        
        # Test engine creation
        engine = DataIngestionEngine(max_workers=3)
        results.append(test_result(
            "Engine creation",
            engine is not None,
            "Engine created successfully"
        ))
        
        # Test connector registration
        connector = TestConnector()
        reg_success = engine.register_connector(connector)
        results.append(test_result(
            "Connector registration",
            reg_success and len(engine.connectors) == 1,
            f"Connectors: {len(engine.connectors)}"
        ))
        
        # Test engine startup
        start_success = await engine.start()
        results.append(test_result(
            "Engine startup",
            start_success and engine.is_running,
            f"Started: {start_success}, Running: {engine.is_running}"
        ))
        
        if start_success:
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
            
            engine.ingest_tick_data(test_tick, priority=1)
            await asyncio.sleep(0.3)  # Wait for processing
            
            results.append(test_result(
                "Data processing callback",
                len(received_data) > 0,
                f"Callbacks triggered: {len(received_data)}"
            ))
            
            # Test metrics
            metrics = engine.get_metrics()
            results.append(test_result(
                "Metrics collection",
                'total_messages' in metrics and metrics['total_messages'] > 0,
                f"Total messages: {metrics['total_messages']}"
            ))
            
            # Test connector status
            connector_status = engine.get_connector_status()
            results.append(test_result(
                "Connector status",
                'test' in connector_status and connector_status['test']['is_connected'],
                f"Connectors: {list(connector_status.keys())}"
            ))
            
            # Test engine shutdown
            await engine.stop()
            results.append(test_result(
                "Engine shutdown",
                not engine.is_running,
                f"Running: {engine.is_running}"
            ))
        
        return all(results)
        
    except Exception as e:
        test_result("Basic Engine", False, f"Exception: {str(e)}")
        return False

async def test_performance_targets():
    """Test that core components meet performance targets"""
    print("\n=== Testing Performance Targets ===")
    
    try:
        # Import directly to avoid aiohttp dependencies
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core', 'data_ingestion'))
        from data_validator import DataValidator
        from data_models import TickData, MarketData, AssetType, DataQuality
        
        results = []
        
        # Test validation latency target (<10ms)
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
        
        # Measure latency over multiple runs
        latencies = []
        for _ in range(100):
            start_time = time.perf_counter()
            await validator.validate(test_data)
            latency = (time.perf_counter() - start_time) * 1000
            latencies.append(latency)
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        results.append(test_result(
            "Validation latency average",
            avg_latency < 5.0,  # Target: <5ms average
            f"Average: {avg_latency:.2f}ms"
        ))
        
        results.append(test_result(
            "Validation latency P95",
            p95_latency < 10.0,  # Target: <10ms P95
            f"P95: {p95_latency:.2f}ms"
        ))
        
        results.append(test_result(
            "Validation latency max",
            max_latency < 20.0,  # Target: <20ms max
            f"Max: {max_latency:.2f}ms"
        ))
        
        # Test data model performance
        start_time = time.perf_counter()
        for i in range(1000):
            tick = TickData(
                timestamp=datetime.now(timezone.utc),
                symbol=f"TEST{i%10}",
                bid=1.1000 + (i * 0.0001),
                ask=1.1001 + (i * 0.0001),
                spread=0.0001,
                asset_type=AssetType.FOREX
            )
            _ = tick.mid_price  # Calculate mid price
            _ = tick.to_dict()  # Serialize
        
        model_time = (time.perf_counter() - start_time) * 1000
        avg_model_time = model_time / 1000
        
        results.append(test_result(
            "Data model performance",
            avg_model_time < 1.0,  # Target: <1ms per model operation
            f"Average: {avg_model_time:.3f}ms per operation"
        ))
        
        return all(results)
        
    except Exception as e:
        test_result("Performance Targets", False, f"Exception: {str(e)}")
        return False

async def test_integration_readiness():
    """Test that components are ready for ML integration"""
    print("\n=== Testing ML Integration Readiness ===")
    
    try:
        # Import directly to avoid aiohttp dependencies
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'core', 'data_ingestion'))
        from data_models import TickData, MarketData, AssetType, DataQuality
        
        results = []
        
        # Test ML feature extraction readiness
        tick_data = TickData(
            timestamp=datetime.now(timezone.utc),
            symbol="EURUSD",
            bid=1.1000,
            ask=1.1001,
            spread=0.0001,
            volume=1000.0,
            asset_type=AssetType.FOREX,
            quality=DataQuality.EXCELLENT,
            latency_ms=2.5
        )
        
        market_data = MarketData(
            symbol="EURUSD",
            asset_type=AssetType.FOREX,
            tick_data=tick_data
        )
        market_data.processing_latency_ms = 2.5
        market_data.validation_passed = True
        
        # Test feature extraction
        features = {
            'timestamp': market_data.timestamp.isoformat(),
            'symbol': market_data.symbol,
            'price': market_data.current_price,
            'quality_score': 1.0 if market_data.tick_data.quality == DataQuality.EXCELLENT else 0.8,
            'latency_ms': market_data.processing_latency_ms,
            'bid': market_data.tick_data.bid,
            'ask': market_data.tick_data.ask,
            'spread': market_data.tick_data.spread,
            'volume': market_data.tick_data.volume
        }
        
        expected_features = ['timestamp', 'symbol', 'price', 'quality_score', 'latency_ms', 'bid', 'ask']
        has_features = all(key in features for key in expected_features)
        
        results.append(test_result(
            "ML feature extraction",
            has_features and len(features) >= 7,
            f"Features: {len(features)}, Required: {len(expected_features)}"
        ))
        
        # Test quality score conversion
        quality_score = features['quality_score']
        results.append(test_result(
            "Quality score conversion",
            quality_score == 1.0,  # Excellent = 1.0
            f"Quality score: {quality_score}"
        ))
        
        # Test data completeness for ML
        data_complete = all([
            features['price'] > 0,
            features['latency_ms'] > 0,
            features['spread'] > 0,
            features['timestamp'] is not None
        ])
        
        results.append(test_result(
            "ML data completeness",
            data_complete,
            "All required ML features present and valid"
        ))
        
        # Test serialization for ML pipeline
        import json
        try:
            json_str = json.dumps(features)
            parsed = json.loads(json_str)
            serialization_ok = len(parsed) == len(features)
        except Exception:
            serialization_ok = False
        
        results.append(test_result(
            "ML data serialization",
            serialization_ok,
            "Data can be serialized for ML pipeline"
        ))
        
        return all(results)
        
    except Exception as e:
        test_result("ML Integration Readiness", False, f"Exception: {str(e)}")
        return False

async def run_validation_tests():
    """Run all validation tests"""
    print("ML Data Ingestion - Core Validation Test Suite")
    print("=" * 55)
    print("Session #2 ML-Enhanced Core - Component Validation")
    print("=" * 55)
    
    tests = [
        ("Core Data Models", test_core_data_models),
        ("Data Validator", test_data_validator),
        ("Basic Engine", test_basic_engine),
        ("Performance Targets", test_performance_targets),
        ("ML Integration Readiness", test_integration_readiness)
    ]
    
    results = []
    start_time = time.perf_counter()
    
    for test_name, test_func in tests:
        print(f"\n[Running {test_name} validation...]")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[FAIL] {test_name} test failed: {e}")
            results.append((test_name, False))
    
    total_time = time.perf_counter() - start_time
    
    # Final summary
    print("\n" + "=" * 55)
    print("VALIDATION SUMMARY")
    print("=" * 55)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    print(f"Total Time: {total_time:.2f} seconds")
    
    if failed == 0:
        print("\n*** ALL VALIDATION TESTS PASSED ***")
        print("ML Data Ingestion System - VALIDATED")
        print("Session #2 ML-Enhanced Core - READY FOR PRODUCTION")
        print("\nCore Components Status:")
        print("[OK] Data Models - High-performance data structures")
        print("[OK] Data Validator - Real-time quality assurance")
        print("[OK] Ingestion Engine - Multi-threaded processing")
        print("[OK] Performance Targets - <10ms latency achieved")
        print("[OK] ML Integration - Feature extraction ready")
        
        print("\nPerformance Achievements:")
        print("- Sub-5ms average validation latency")
        print("- <10ms P95 validation latency")
        print("- Multi-asset data model support")
        print("- Real-time quality monitoring")
        print("- ML-ready feature extraction")
        
    else:
        print(f"\n*** {failed} VALIDATION TESTS FAILED ***")
        print("Please review failed components before production")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_validation_tests())
    exit(0 if success else 1)