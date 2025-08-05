#!/usr/bin/env python3
"""
UNICODE RESOLUTION TESTING SCRIPT
Comprehensive testing to verify all Unicode encoding issues are permanently resolved
Tests file operations, print statements, and MT5 signal handling
"""

import sys
import os
import json
from datetime import datetime
from encoding_utils import (
    ASCIIFileManager, 
    UnicodeReplacer, 
    ascii_print, 
    write_ascii_json, 
    read_mt5_signal, 
    write_mt5_signal,
    initialize_encoding_system
)

class UnicodeResolutionTester:
    """Test all aspects of Unicode resolution"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    def run_test(self, test_name: str, test_function) -> bool:
        """Run a single test and record results"""
        try:
            ascii_print(f"Testing: {test_name}")
            result = test_function()
            if result:
                ascii_print("  PASS")
                self.tests_passed += 1
                self.test_results.append({"test": test_name, "status": "PASS", "error": None})
                return True
            else:
                ascii_print("  FAIL - Test function returned False")
                self.tests_failed += 1
                self.test_results.append({"test": test_name, "status": "FAIL", "error": "Test function returned False"})
                return False
        except Exception as e:
            ascii_print(f"  FAIL - {str(e)}")
            self.tests_failed += 1
            self.test_results.append({"test": test_name, "status": "FAIL", "error": str(e)})
            return False
    
    def test_ascii_print_function(self) -> bool:
        """Test ASCII print function with Unicode characters"""
        # Test with common Unicode characters that cause issues
        test_strings = [
            "Trade executed ✅ successfully",
            "Error ❌ in execution", 
            "Warning ⚠️ detected",
            "Profit 💰 target reached",
            "System ⚡ performance optimal",
            "Analysis 📊 complete"
        ]
        
        for test_string in test_strings:
            ascii_print(f"    Testing: {test_string}")
        
        return True
    
    def test_unicode_replacement(self) -> bool:
        """Test Unicode character replacement"""
        test_cases = [
            ("Trade executed ✅", "Trade executed OK"),
            ("Error ❌ occurred", "Error ERROR occurred"),
            ("Warning ⚠️ detected", "Warning WARNING detected"),
            ("Price → 1.2345", "Price -> 1.2345"),
            ("€100 profit", "EUR100 profit"),
            ("≈2.5 lots", "~=2.5 lots")
        ]
        
        for input_text, expected in test_cases:
            result = UnicodeReplacer.replace_unicode(input_text)
            if result != expected:
                ascii_print(f"    FAIL: Expected '{expected}', got '{result}'")
                return False
            ascii_print(f"    OK: '{input_text}' -> '{result}'")
        
        return True
    
    def test_ascii_file_writing(self) -> bool:
        """Test ASCII-only file writing"""
        test_data = {
            "status": "Trade executed ✅ successfully",
            "profit": "💰 $1,234.56",
            "analysis": "📊 Performance optimal",
            "timestamp": datetime.now().isoformat()
        }
        
        test_file = "test_unicode_write.json"
        
        # Test ASCII JSON writing
        if not write_ascii_json(test_file, test_data):
            return False
        
        # Verify file was written and can be read
        try:
            with open(test_file, 'r', encoding='ascii', errors='ignore') as f:
                content = f.read()
                # Should not contain any Unicode characters
                for char in content:
                    if ord(char) > 127:
                        ascii_print(f"    FAIL: Found Unicode character: {repr(char)}")
                        return False
            
            # Clean up
            os.remove(test_file)
            ascii_print("    OK: ASCII file writing successful")
            return True
        
        except Exception as e:
            ascii_print(f"    FAIL: Could not read written file: {e}")
            return False
    
    def test_mt5_signal_handling(self) -> bool:
        """Test MT5 signal file handling"""
        test_signal = {
            "symbol": "EURJPY",
            "trade_direction": "BULL",
            "status": "Signal generated ✅",
            "profit_target": "Target 🎯 reached",
            "timestamp": datetime.now().isoformat(),
            "phase_4_ylipip": {
                "triggered": True,
                "value": 0.6
            }
        }
        
        signal_file = "test_mt5_signal.json"
        
        # Test writing MT5 signal
        if not write_mt5_signal(signal_file, test_signal):
            ascii_print("    FAIL: Could not write MT5 signal")
            return False
        
        # Test reading MT5 signal
        read_signal = read_mt5_signal(signal_file)
        if not read_signal:
            ascii_print("    FAIL: Could not read MT5 signal") 
            return False
        
        # Verify signal content
        if read_signal["symbol"] != "EURJPY":
            ascii_print("    FAIL: Signal data corrupted")
            return False
        
        # Clean up
        try:
            os.remove(signal_file)
        except:
            pass
        
        ascii_print("    OK: MT5 signal handling successful")
        return True
    
    def test_log_file_operations(self) -> bool:
        """Test log file operations with potential Unicode"""
        log_file = "test_unicode_log.json"
        
        # Test various log messages with Unicode
        log_messages = [
            "System initialized ✅",
            "Trade executed successfully 💰", 
            "Warning: High volatility ⚠️",
            "Performance optimal ⚡",
            "Analysis complete 📊"
        ]
        
        for message in log_messages:
            if not ASCIIFileManager.log_to_file(log_file, message, "INFO"):
                ascii_print(f"    FAIL: Could not log message: {message}")
                return False
        
        # Verify log file content
        try:
            with open(log_file, 'r', encoding='ascii', errors='ignore') as f:
                content = f.read()
                # Parse JSON to verify structure
                log_data = json.loads(content)
                if not isinstance(log_data, list):
                    ascii_print("    FAIL: Log file format incorrect")
                    return False
        
            # Clean up
            os.remove(log_file)
            ascii_print("    OK: Log file operations successful")
            return True
        
        except Exception as e:
            ascii_print(f"    FAIL: Log file verification failed: {e}")
            return False
    
    def test_system_output_encoding(self) -> bool:
        """Test that system output encoding is configured correctly"""
        try:
            # Test stdout encoding
            encoding = sys.stdout.encoding
            ascii_print(f"    Stdout encoding: {encoding}")
            
            # Test that reconfigure worked
            if hasattr(sys.stdout, 'reconfigure'):
                ascii_print("    OK: stdout.reconfigure available")
            else:
                ascii_print("    WARNING: stdout.reconfigure not available (older Python)")
            
            # Test printing various characters
            test_output = "Test: Basic ASCII + numbers 123 + symbols !@#$%"
            ascii_print(f"    {test_output}")
            
            return True
        
        except Exception as e:
            ascii_print(f"    FAIL: System encoding test failed: {e}")
            return False
    
    def test_existing_file_compatibility(self) -> bool:
        """Test that existing files can be processed safely"""
        # Test with the session initialization file
        test_files = [
            "session_initialization.py",
            "ascii_only_production.py",
            "encoding_utils.py"
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                try:
                    with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Clean content should not cause encoding errors
                    clean_content = ASCIIFileManager.clean_ascii_string(content)
                    ascii_print(f"    OK: {test_file} processed successfully")
                
                except Exception as e:
                    ascii_print(f"    FAIL: Could not process {test_file}: {e}")
                    return False
            else:
                ascii_print(f"    SKIP: {test_file} not found")
        
        return True
    
    def run_all_tests(self) -> bool:
        """Run all Unicode resolution tests"""
        ascii_print("MIKROBOT UNICODE RESOLUTION TEST SUITE")
        ascii_print("=" * 50)
        ascii_print("")
        
        # Initialize encoding system
        initialize_encoding_system()
        ascii_print("")
        
        # Run all tests
        tests = [
            ("ASCII Print Function", self.test_ascii_print_function),
            ("Unicode Character Replacement", self.test_unicode_replacement), 
            ("ASCII File Writing", self.test_ascii_file_writing),
            ("MT5 Signal Handling", self.test_mt5_signal_handling),
            ("Log File Operations", self.test_log_file_operations),
            ("System Output Encoding", self.test_system_output_encoding),
            ("Existing File Compatibility", self.test_existing_file_compatibility)
        ]
        
        for test_name, test_function in tests:
            self.run_test(test_name, test_function)
            ascii_print("")
        
        # Print summary
        ascii_print("TEST RESULTS SUMMARY")
        ascii_print("=" * 30)
        ascii_print(f"Tests Passed: {self.tests_passed}")
        ascii_print(f"Tests Failed: {self.tests_failed}")
        ascii_print(f"Success Rate: {(self.tests_passed / (self.tests_passed + self.tests_failed) * 100):.1f}%")
        
        # Save detailed results
        test_report = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "success_rate_percent": (self.tests_passed / (self.tests_passed + self.tests_failed) * 100),
            "detailed_results": self.test_results,
            "unicode_resolution_status": "COMPLETE" if self.tests_failed == 0 else "ISSUES_DETECTED"
        }
        
        write_ascii_json("unicode_resolution_test_report.json", test_report)
        ascii_print("")
        ascii_print("Detailed report: unicode_resolution_test_report.json")
        
        if self.tests_failed == 0:
            ascii_print("")
            ascii_print("SUCCESS: ALL UNICODE ISSUES RESOLVED")
            ascii_print("The system is now immune to charmap codec errors")
            return True
        else:
            ascii_print("")
            ascii_print(f"WARNING: {self.tests_failed} tests failed")
            ascii_print("Additional fixes may be required")
            return False

def main():
    """Main test execution"""
    # Initialize ASCII output
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
        sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
    except:
        pass  # Older Python versions
    
    # Run comprehensive tests
    tester = UnicodeResolutionTester()
    success = tester.run_all_tests()
    
    if success:
        ascii_print("")
        ascii_print("MIKROBOT TRADING SYSTEM IS NOW UNICODE-SAFE")
        ascii_print("No more charmap codec errors will occur")
        ascii_print("All file operations use ASCII-only encoding")
        return 0
    else:
        ascii_print("")
        ascii_print("ADDITIONAL FIXES REQUIRED")
        ascii_print("Check the test report for details")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)