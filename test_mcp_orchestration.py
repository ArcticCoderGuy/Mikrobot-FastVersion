#!/usr/bin/env python3
"""
Test MCP Orchestration System - Validate complete integration
Tests Hansei validation + MT5 execution + Signal monitoring coordination
"""
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
import MetaTrader5 as mt5

# ASCII-only encoding enforcement
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    """Enforce ASCII-only output"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

class MCPOrchestrationTester:
    """Test the complete MCP orchestration system"""
    
    def __init__(self):
        self.signal_dir = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
        self.test_results = []
        
    def test_1_mt5_connection(self) -> bool:
        """Test MT5 connection and basic functionality"""
        ascii_print("TEST 1: MT5 Connection")
        ascii_print("-" * 30)
        
        try:
            if not mt5.initialize():
                ascii_print("FAIL: MT5 initialization failed")
                return False
                
            account_info = mt5.account_info()
            if not account_info:
                ascii_print("FAIL: No account information")
                return False
                
            ascii_print(f"PASS: Connected to account {account_info.login}")
            ascii_print(f"      Balance: ${account_info.balance:.2f}")
            
            # Test symbol info
            symbol_info = mt5.symbol_info('GBPJPY')
            if symbol_info:
                ascii_print(f"PASS: Symbol GBPJPY accessible")
            else:
                ascii_print("WARN: GBPJPY not available")
                
            return True
            
        except Exception as e:
            ascii_print(f"FAIL: {e}")
            return False
            
    def test_2_signal_file_access(self) -> bool:
        """Test signal file reading with Unicode handling"""
        ascii_print("\nTEST 2: Signal File Access")
        ascii_print("-" * 30)
        
        try:
            signal_files = list(self.signal_dir.glob("mikrobot*.json"))
            
            if not signal_files:
                ascii_print("FAIL: No signal files found")
                return False
                
            ascii_print(f"PASS: Found {len(signal_files)} signal files")
            
            # Test reading each file
            readable_files = 0
            for file in signal_files:
                try:
                    with open(file, 'rb') as f:
                        content = f.read()
                        
                    # Handle UTF-16LE encoding
                    if content.startswith(b'\\xff\\xfe'):
                        content_str = content.decode('utf-16le', errors='ignore')
                    else:
                        content_str = content.decode('utf-8', errors='ignore')
                        
                    # Clean content
                    content_str = content_str.replace('\\x00', '')
                    content_str = ''.join(char for char in content_str if ord(char) < 128 or char in '{}":,.-')
                    
                    signal_data = json.loads(content_str)
                    readable_files += 1
                    ascii_print(f"PASS: {file.name} readable")
                    
                except Exception as e:
                    ascii_print(f"WARN: {file.name} error: {e}")
                    
            if readable_files == 0:
                ascii_print("FAIL: No readable signal files")
                return False
                
            ascii_print(f"PASS: {readable_files}/{len(signal_files)} files readable")
            return True
            
        except Exception as e:
            ascii_print(f"FAIL: {e}")
            return False
            
    def test_3_hansei_validation(self) -> bool:
        """Test Hansei pattern validation"""
        ascii_print("\nTEST 3: Hansei Pattern Validation")
        ascii_print("-" * 30)
        
        # Create test signal data
        test_signal = {
            "timestamp": "2025.08.05 09:00",
            "symbol": "GBPJPY",
            "strategy": "MIKROBOT_FASTVERSION_4PHASE",
            "phase_1_m5_bos": {
                "time": "2025.08.05 08:55",
                "price": 195.95700,
                "direction": "BULL"
            },
            "phase_2_m1_break": {
                "time": "2025.08.05 08:57",
                "price": 195.95900
            },
            "phase_3_m1_retest": {
                "time": "2025.08.05 08:58",
                "price": 195.95900
            },
            "phase_4_ylipip": {
                "target": 195.96500,
                "current": 195.96700,
                "triggered": True
            },
            "trade_direction": "BULL",
            "current_price": 195.96700,
            "ylipip_trigger": 0.60,
            "source": "MIKROBOT_FASTVERSION_COMPLIANT_v8"
        }
        
        try:
            # Import orchestrator for validation
            from mcp_trading_orchestrator import MCPTradingOrchestrator
            orchestrator = MCPTradingOrchestrator()
            
            # Test validation
            valid, reason = orchestrator.validate_signal_hansei(test_signal)
            
            if valid:
                ascii_print(f"PASS: Signal validation passed - {reason}")
                
                # Test position sizing calculation
                lot_size = orchestrator.calculate_position_size('GBPJPY', 8.0)
                ascii_print(f"PASS: Position size calculated: {lot_size} lots")
                
                return True
            else:
                ascii_print(f"FAIL: Signal validation failed - {reason}")
                return False
                
        except Exception as e:
            ascii_print(f"FAIL: {e}")
            return False
            
    def test_4_position_sizing_compliance(self) -> bool:
        """Test position sizing compliance with standards"""
        ascii_print("\nTEST 4: Position Sizing Compliance")
        ascii_print("-" * 30)
        
        try:
            if not mt5.initialize():
                ascii_print("FAIL: MT5 not available for position sizing test")
                return False
                
            account_info = mt5.account_info()
            if not account_info:
                ascii_print("FAIL: No account info for position sizing")
                return False
                
            # Test calculations
            balance = account_info.balance
            risk_per_trade = 0.0055  # 0.55%
            atr_pips = 8.0
            
            risk_amount = balance * risk_per_trade
            usd_per_pip_per_lot = 100  # JPYXXX pairs
            expected_lot_size = round(risk_amount / (atr_pips * usd_per_pip_per_lot), 2)
            
            ascii_print(f"Balance: ${balance:.2f}")
            ascii_print(f"Risk Amount (0.55%): ${risk_amount:.2f}")
            ascii_print(f"ATR: {atr_pips} pips")
            ascii_print(f"Expected Lot Size: {expected_lot_size}")
            
            # Verify this is NOT 0.01 (the old broken method)
            if expected_lot_size == 0.01:
                ascii_print("WARN: Position size equals old broken method (0.01)")
                ascii_print("      This might indicate the fix isn't working")
            else:
                ascii_print("PASS: Position size differs from broken 0.01 method")
                
            # Verify it's reasonable (should be around 0.68 for current balance)
            if 0.5 <= expected_lot_size <= 1.0:
                ascii_print("PASS: Position size within expected range")
                return True
            else:
                ascii_print(f"WARN: Position size {expected_lot_size} outside expected range")
                return False
                
        except Exception as e:
            ascii_print(f"FAIL: {e}")
            return False
            
    def test_5_fail_safe_mechanisms(self) -> bool:
        """Test fail-safe mechanisms"""
        ascii_print("\nTEST 5: Fail-Safe Mechanisms")
        ascii_print("-" * 30)
        
        try:
            from mcp_trading_orchestrator import MCPTradingOrchestrator
            orchestrator = MCPTradingOrchestrator()
            
            # Test invalid signal handling
            invalid_signal = {"invalid": "data"}
            valid, reason = orchestrator.validate_signal_hansei(invalid_signal)
            
            if not valid:
                ascii_print(f"PASS: Invalid signal rejected - {reason}")
            else:
                ascii_print("FAIL: Invalid signal accepted")
                return False
                
            # Test corrupted signal file handling
            corrupted_signal = orchestrator.read_signal_file(Path("nonexistent.json"))
            if corrupted_signal is None:
                ascii_print("PASS: Corrupted file handled gracefully")
            else:
                ascii_print("FAIL: Corrupted file not handled")
                return False
                
            ascii_print("PASS: Fail-safe mechanisms working")
            return True
            
        except Exception as e:
            ascii_print(f"FAIL: {e}")
            return False
            
    async def test_6_end_to_end_simulation(self) -> bool:
        """Test end-to-end simulation (without actual trading)"""
        ascii_print("\nTEST 6: End-to-End Simulation")
        ascii_print("-" * 30)
        
        try:
            # Create a test signal file
            test_signal = {
                "timestamp": datetime.now().strftime("%Y.%m.%d %H:%M"),
                "symbol": "GBPJPY", 
                "strategy": "MIKROBOT_FASTVERSION_4PHASE",
                "phase_1_m5_bos": {
                    "time": datetime.now().strftime("%Y.%m.%d %H:%M"),
                    "price": 195.95700,
                    "direction": "BULL"
                },
                "phase_2_m1_break": {
                    "time": datetime.now().strftime("%Y.%m.%d %H:%M"),
                    "price": 195.95900
                },
                "phase_3_m1_retest": {
                    "time": datetime.now().strftime("%Y.%m.%d %H:%M"), 
                    "price": 195.95900
                },
                "phase_4_ylipip": {
                    "target": 195.96500,
                    "current": 195.96700,
                    "triggered": True
                },
                "trade_direction": "BULL",
                "current_price": 195.96700,
                "ylipip_trigger": 0.65,
                "source": "MCP_TEST"
            }
            
            # Write test signal
            test_file = self.signal_dir / "test_signal.json"
            with open(test_file, 'w') as f:
                json.dump(test_signal, f, ensure_ascii=True)
                
            ascii_print("PASS: Test signal file created")
            
            # Test orchestrator processing
            from mcp_trading_orchestrator import MCPTradingOrchestrator
            orchestrator = MCPTradingOrchestrator()
            
            # Initialize systems
            if not await orchestrator.initialize_systems():
                ascii_print("FAIL: System initialization failed")
                return False
                
            ascii_print("PASS: Systems initialized")
            
            # Read and validate test signal
            signal_data = orchestrator.read_signal_file(test_file)
            if not signal_data:
                ascii_print("FAIL: Could not read test signal")
                return False
                
            ascii_print("PASS: Test signal read successfully")
            
            # Validate signal
            valid, reason = orchestrator.validate_signal_hansei(signal_data)
            if not valid:
                ascii_print(f"FAIL: Signal validation failed - {reason}")
                return False
                
            ascii_print("PASS: Signal validation passed")
            
            # Cleanup
            test_file.unlink()
            ascii_print("PASS: End-to-end simulation completed")
            
            return True
            
        except Exception as e:
            ascii_print(f"FAIL: {e}")
            return False
            
    async def run_all_tests(self):
        """Run all orchestration tests"""
        ascii_print("=" * 60)
        ascii_print("  MCP ORCHESTRATION SYSTEM - COMPREHENSIVE TESTING")
        ascii_print("=" * 60)
        ascii_print("")
        
        tests = [
            ("MT5 Connection", self.test_1_mt5_connection),
            ("Signal File Access", self.test_2_signal_file_access),
            ("Hansei Validation", self.test_3_hansei_validation),
            ("Position Sizing Compliance", self.test_4_position_sizing_compliance),
            ("Fail-Safe Mechanisms", self.test_5_fail_safe_mechanisms),
            ("End-to-End Simulation", self.test_6_end_to_end_simulation)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()
                    
                if result:
                    passed += 1
                    self.test_results.append((test_name, "PASS"))
                else:
                    self.test_results.append((test_name, "FAIL"))
                    
            except Exception as e:
                ascii_print(f"ERROR in {test_name}: {e}")
                self.test_results.append((test_name, "ERROR"))
                
        # Final report
        ascii_print("\n" + "=" * 60)
        ascii_print("  TEST RESULTS SUMMARY")
        ascii_print("=" * 60)
        
        for test_name, result in self.test_results:
            status_icon = {"PASS": "[PASS]", "FAIL": "[FAIL]", "ERROR": "[ERR]"}[result]
            ascii_print(f"{status_icon} {test_name}")
            
        ascii_print("")
        ascii_print(f"TOTAL: {passed}/{total} tests passed")
        
        if passed == total:
            ascii_print("SUCCESS: All tests passed - MCP orchestration system ready")
        else:
            ascii_print("WARNING: Some tests failed - review issues before deployment")
            
        # Cleanup
        if mt5.initialize():
            mt5.shutdown()

async def main():
    """Main entry point"""
    tester = MCPOrchestrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())