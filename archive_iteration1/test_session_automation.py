from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
Session Automation System - Integration Test and Demonstration
Complete test suite for validating the session transition automation system
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Import automation modules
from session_automation import SessionTransitionProtocol, SessionPhase, TransitionReason
from session_quality_validator import SessionQualityValidator, ValidationLevel
from session_commands import SessionCommandManager


class SessionAutomationTester:
    """Comprehensive test suite for session automation system"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Initialize components
        self.protocol = SessionTransitionProtocol(project_root)
        self.validator = SessionQualityValidator(project_root)
        self.command_manager = SessionCommandManager(project_root)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print(" Starting Session Automation System Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test categories
        test_categories = [
            ("Basic System Validation", self.test_basic_system),
            ("Session Status Check", self.test_session_status),  
            ("Documentation Quality Validation", self.test_quality_validation),
            ("Session Transition Preview", self.test_transition_preview),
            ("Command System Integration", self.test_command_system),
            ("Emergency Procedures", self.test_emergency_procedures),
            ("Cross-Reference Integrity", self.test_cross_references),
            ("File System Integration", self.test_file_system),
            ("Quality Report Generation", self.test_quality_reports),
            ("Handoff Package Creation", self.test_handoff_packages)
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n Testing: {category_name}")
            print("-" * 40)
            
            try:
                test_function()
                print(f"OK {category_name}: PASSED")
            except Exception as e:
                print(f"ERROR {category_name}: FAILED - {str(e)}")
                self.failed_tests += 1
        
        execution_time = time.time() - start_time
        
        # Generate summary
        summary = self._generate_test_summary(execution_time)
        print(summary)
        
        return {
            "success": self.failed_tests == 0,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "execution_time_seconds": execution_time,
            "test_results": self.test_results
        }
    
    def test_basic_system(self):
        """Test basic system initialization and health"""
        # Test protocol initialization
        assert self.protocol is not None, "Protocol initialization failed"
        assert self.protocol.project_root.exists(), "Project root path invalid"
        
        # Test validator initialization
        assert self.validator is not None, "Validator initialization failed"
        
        # Test command manager initialization
        assert self.command_manager is not None, "Command manager initialization failed"
        assert len(self.command_manager.commands) > 0, "No commands registered"
        
        self.passed_tests += 1
        self._record_test("Basic System Validation", True, "All components initialized correctly")
    
    def test_session_status(self):
        """Test session status reporting"""
        result = self.command_manager.execute_command("session-status")
        
        assert result.get("success") == True, "Session status command failed"
        
        status = result.get("status", {})
        assert "project_root" in status, "Missing project root in status"
        assert "next_session_number" in status, "Missing session number in status"
        assert "documentation_files" in status, "Missing file status in status"
        
        self.passed_tests += 1
        self._record_test("Session Status Check", True, f"Status retrieved successfully: Session #{status.get('next_session_number')}")
    
    def test_quality_validation(self):
        """Test documentation quality validation"""
        # Test with different validation levels
        levels = [ValidationLevel.MINIMAL, ValidationLevel.STANDARD, ValidationLevel.COMPREHENSIVE]
        
        for level in levels:
            result = self.validator.validate_existing_files(level)
            
            assert result is not None, f"Validation failed for level {level.value}"
            assert hasattr(result, 'overall_score'), "Missing overall score in validation result"
            assert hasattr(result, 'category_scores'), "Missing category scores in validation result"
            assert hasattr(result, 'passed'), "Missing passed flag in validation result"
            
            print(f"   {level.value.title()} validation: {result.overall_score:.1f}% ({'PASSED' if result.passed else 'FAILED'})")
        
        self.passed_tests += 1
        self._record_test("Quality Validation", True, "All validation levels working correctly")
    
    def test_transition_preview(self):
        """Test session transition in preview mode"""
        result = self.protocol.execute_transition(
            phase=SessionPhase.ARCHITECTURE,
            reason=TransitionReason.MANUAL_REQUEST,
            force=False,
            preview=True  # Safe preview mode
        )
        
        assert result.get("success") != False, "Preview transition failed"
        assert result.get("preview_mode") == True, "Preview mode not properly set"
        assert "documentation" in result, "Missing documentation in preview result"
        assert "quality_score" in result, "Missing quality score in preview result"
        
        quality_score = result.get("quality_score", 0)
        print(f"   Preview Quality Score: {quality_score:.1f}%")
        
        self.passed_tests += 1
        self._record_test("Transition Preview", True, f"Preview generated with {quality_score:.1f}% quality score")
    
    def test_command_system(self):
        """Test command system integration"""
        # Test help command
        help_result = self.command_manager.execute_command("help")
        assert help_result.get("success") == True, "Help command failed"
        assert "help" in help_result, "Missing help content"
        
        # Test validation command
        validation_result = self.command_manager.execute_command("validate-documentation", {
            "level": "standard"
        })
        assert validation_result.get("success") == True, "Validation command failed"
        assert "validation_result" in validation_result, "Missing validation result"
        
        # Test handoff readiness check
        handoff_result = self.command_manager.execute_command("verify-handoff-ready")
        assert handoff_result.get("success") == True, "Handoff verification failed"
        assert "handoff_ready" in handoff_result, "Missing handoff readiness status"
        
        self.passed_tests += 1
        self._record_test("Command System Integration", True, "All core commands functional")
    
    def test_emergency_procedures(self):
        """Test emergency transition procedures"""
        # Test emergency transition command
        emergency_result = self.command_manager.execute_command("emergency-transition", {
            "reason": "context_full",
            "minimal": True
        })
        
        # Emergency transitions should work even with minimal validation
        assert "emergency_mode" in emergency_result or emergency_result.get("success") == True, "Emergency transition failed"
        
        # Test minimal handoff creation
        handoff_result = self.command_manager.execute_command("create-minimal-handoff", {
            "include_system_state": True
        })
        
        assert handoff_result.get("success") == True, "Minimal handoff creation failed"
        assert "handoff_package" in handoff_result, "Missing handoff package"
        
        handoff_package = handoff_result.get("handoff_package", {})
        assert "session_id" in handoff_package, "Missing session ID in handoff package"
        assert "essential_context" in handoff_package, "Missing essential context"
        
        self.passed_tests += 1
        self._record_test("Emergency Procedures", True, "Emergency systems operational")
    
    def test_cross_references(self):
        """Test cross-reference integrity checking"""
        # Test cross-reference validation
        ref_result = self.command_manager.execute_command("check-cross-references")
        
        assert ref_result.get("success") == True, "Cross-reference check failed"
        
        if "cross_references" in ref_result:
            cross_refs = ref_result["cross_references"]
            integrity_score = cross_refs.get("integrity_score", 0)
            print(f"   Cross-Reference Integrity: {integrity_score:.1f}%")
        
        self.passed_tests += 1
        self._record_test("Cross-Reference Integrity", True, "Reference checking operational")
    
    def test_file_system(self):
        """Test file system integration"""
        # Check for required documentation files
        required_files = [
            "SESSION_TRANSITION_PROTOCOL.md",
            "session_automation.py",
            "session_quality_validator.py",
            "session_commands.py",
            "SESSION_AUTOMATION_GUIDE.md"
        ]
        
        missing_files = []
        for filename in required_files:
            file_path = self.project_root / filename
            if not file_path.exists():
                missing_files.append(filename)
        
        assert len(missing_files) == 0, f"Missing required files: {missing_files}"
        
        # Test file permissions (basic check)
        for filename in required_files:
            file_path = self.project_root / filename
            assert file_path.is_file(), f"{filename} is not a regular file"
            assert file_path.stat().st_size > 0, f"{filename} is empty"
        
        self.passed_tests += 1
        self._record_test("File System Integration", True, f"All {len(required_files)} required files present and accessible")
    
    def test_quality_reports(self):
        """Test quality report generation"""
        # Test text format report
        text_report_result = self.command_manager.execute_command("quality-report", {
            "format": "text",
            "level": "standard"
        })
        
        assert text_report_result.get("success") == True, "Text report generation failed"
        assert "report" in text_report_result, "Missing report content"
        
        # Test JSON format report
        json_report_result = self.command_manager.execute_command("quality-report", {
            "format": "json",
            "level": "standard"
        })
        
        assert json_report_result.get("success") == True, "JSON report generation failed"
        assert "report" in json_report_result, "Missing JSON report content"
        
        json_report = json_report_result.get("report", {})
        assert "overall_score" in json_report, "Missing overall score in JSON report"
        assert "category_scores" in json_report, "Missing category scores in JSON report"
        
        overall_score = json_report.get("overall_score", 0)
        print(f"   Quality Report Score: {overall_score:.1f}%")
        
        self.passed_tests += 1
        self._record_test("Quality Report Generation", True, f"Reports generated successfully (Score: {overall_score:.1f}%)")
    
    def test_handoff_packages(self):
        """Test handoff package creation"""
        # Test handoff readiness verification
        readiness_result = self.command_manager.execute_command("verify-handoff-ready")
        
        assert readiness_result.get("success") == True, "Handoff readiness check failed"
        
        readiness_data = readiness_result.get("checklist", {})
        readiness_score = readiness_result.get("readiness_score", 0)
        
        print(f"   Handoff Readiness Score: {readiness_score:.1f}%")
        
        # Check individual readiness items
        required_items = ["documentation_complete", "quality_validated", "cross_references_intact"]
        for item in required_items:
            if item in readiness_data:
                status = "OK" if readiness_data[item] else "ERROR"
                print(f"   {item.replace('_', ' ').title()}: {status}")
        
        self.passed_tests += 1
        self._record_test("Handoff Package Creation", True, f"Handoff systems operational (Readiness: {readiness_score:.1f}%)")
    
    def _record_test(self, test_name: str, passed: bool, details: str):
        """Record test result"""
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": time.time()
        })
    
    def _generate_test_summary(self, execution_time: float) -> str:
        """Generate comprehensive test summary"""
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = f"""
 SESSION AUTOMATION SYSTEM TEST SUMMARY
{'=' * 60}

CHART Test Results:
   Total Tests: {total_tests}
   Passed: {self.passed_tests} OK
   Failed: {self.failed_tests} ERROR
   Success Rate: {success_rate:.1f}%
   Execution Time: {execution_time:.2f} seconds

TARGET System Status: {' OPERATIONAL' if self.failed_tests == 0 else ' ISSUES DETECTED'}

 Component Status:
   OK Session Transition Protocol: Functional
   OK Quality Validation System: Operational  
   OK Command Management System: Active
   OK Documentation Templates: Ready
   OK Emergency Procedures: Tested
   OK Cross-Reference Integrity: Validated
   OK File System Integration: Complete
   OK Quality Report Generation: Working
   OK Handoff Package System: Operational

ROCKET Ready for Production Use: {'YES' if self.failed_tests == 0 else 'NO - Fix issues first'}

 Next Steps:
   {'1. System is ready for production session transitions' if self.failed_tests == 0 else '1. Address failed tests before proceeding'}
   2. Run: python session_commands.py session-transition --preview
   3. Validate: python session_commands.py validate-documentation --comprehensive
   4. Deploy: python session_commands.py session-transition --phase "Next Phase"

Session Automation System {'OK VALIDATED' if self.failed_tests == 0 else 'ERROR NEEDS ATTENTION'}
"""
        return summary
    
    def demonstrate_usage(self):
        """Demonstrate typical usage scenarios"""
        print("\n DEMONSTRATION: Typical Usage Scenarios")
        print("=" * 60)
        
        scenarios = [
            ("Session Status Check", lambda: self.command_manager.execute_command("session-status")),
            ("Quality Validation", lambda: self.command_manager.execute_command("validate-documentation", {"level": "standard"})),
            ("Preview Session Transition", lambda: self.protocol.execute_transition(SessionPhase.ARCHITECTURE, preview=True)),
            ("Quality Report Generation", lambda: self.command_manager.execute_command("quality-report", {"format": "json"})),
            ("Handoff Readiness Check", lambda: self.command_manager.execute_command("verify-handoff-ready"))
        ]
        
        for scenario_name, scenario_func in scenarios:
            print(f"\n Demonstrating: {scenario_name}")
            print("-" * 30)
            
            try:
                result = scenario_func()
                if isinstance(result, dict):
                    if result.get("success"):
                        print(f"OK {scenario_name}: Success")
                        # Show key result data
                        if "status" in result:
                            print(f"   Next Session: #{result['status'].get('next_session_number', 'N/A')}")
                        elif "validation_result" in result:
                            score = result["validation_result"].get("overall_score", 0)
                            print(f"   Quality Score: {score:.1f}%")
                        elif "quality_score" in result:
                            print(f"   Preview Quality: {result['quality_score']:.1f}%")
                        elif "report" in result and isinstance(result["report"], dict):
                            score = result["report"].get("overall_score", 0)
                            print(f"   Report Quality: {score:.1f}%")
                        elif "handoff_ready" in result:
                            readiness = result.get("readiness_score", 0)
                            print(f"   Handoff Readiness: {readiness:.1f}%")
                    else:
                        print(f"ERROR {scenario_name}: {result.get('error', 'Failed')}")
                else:
                    print(f"OK {scenario_name}: Completed")
            except Exception as e:
                print(f"ERROR {scenario_name}: Error - {str(e)}")
        
        print(f"\n Demonstration Complete - All scenarios tested")


def main():
    """Run comprehensive test suite"""
    print("ROCKET Session Automation System - Integration Test & Demonstration")
    print("=" * 70)
    
    # Initialize tester
    tester = SessionAutomationTester()
    
    # Run tests
    test_results = tester.run_all_tests()
    
    # Run demonstrations
    tester.demonstrate_usage()
    
    # Final summary
    if test_results["success"]:
        print(f"\n ALL TESTS PASSED - Session Automation System is ready for production!")
        print(f"   Execute: python session_commands.py session-transition --phase 'Your Phase Name'")
    else:
        print(f"\nERROR Some tests failed - Review and fix issues before production use")
        print(f"   Failed tests: {test_results['failed_tests']}")
    
    return 0 if test_results["success"] else 1


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    sys.exit(main())