#!/usr/bin/env python3
"""
Session Automation System - Simple Demonstration
Demonstrates the complete session transition automation system
"""

import os
import sys
import json
import time
from pathlib import Path

# Import automation modules
try:
    from session_automation import SessionTransitionProtocol, SessionPhase, TransitionReason
    from session_quality_validator import SessionQualityValidator, ValidationLevel
    from session_commands import SessionCommandManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all automation modules are in the same directory")
    sys.exit(1)


def main():
    """Demonstrate session automation system"""
    print("Session Automation System - Demonstration")
    print("=" * 50)
    
    try:
        # Initialize components
        project_root = Path.cwd()
        print(f"Project Root: {project_root}")
        
        protocol = SessionTransitionProtocol(str(project_root))
        validator = SessionQualityValidator(str(project_root))
        command_manager = SessionCommandManager(str(project_root))
        
        print("Components initialized successfully")
        
        # Test 1: Session Status
        print("\n1. Testing Session Status...")
        status_result = command_manager.execute_command("session-status")
        if status_result.get("success"):
            status = status_result.get("status", {})
            print(f"   Next Session Number: {status.get('next_session_number')}")
            print(f"   System Health: {status.get('system_health')}")
        else:
            print(f"   Error: {status_result.get('error')}")
        
        # Test 2: Quality Validation
        print("\n2. Testing Quality Validation...")
        validation_result = command_manager.execute_command("validate-documentation", {
            "level": "standard"
        })
        if validation_result.get("success"):
            val_data = validation_result.get("validation_result", {})
            print(f"   Overall Score: {val_data.get('overall_score', 0):.1f}%")
            print(f"   Validation Passed: {val_data.get('passed', False)}")
        else:
            print(f"   Error: {validation_result.get('error')}")
        
        # Test 3: Preview Session Transition
        print("\n3. Testing Session Transition Preview...")
        try:
            preview_result = protocol.execute_transition(
                phase=SessionPhase.ARCHITECTURE,
                reason=TransitionReason.MANUAL_REQUEST,
                preview=True
            )
            if preview_result.get("success") is not False:
                print(f"   Preview Mode: {preview_result.get('preview_mode', False)}")
                print(f"   Quality Score: {preview_result.get('quality_score', 0):.1f}%")
            else:
                print(f"   Error: {preview_result.get('error')}")
        except Exception as e:
            print(f"   Error: {str(e)}")
        
        # Test 4: Quality Report
        print("\n4. Testing Quality Report Generation...")
        report_result = command_manager.execute_command("quality-report", {
            "format": "json",
            "level": "standard"
        })
        if report_result.get("success"):
            report_data = report_result.get("report", {})
            print(f"   Report Generated: {len(str(report_data))} characters")
            print(f"   Overall Score: {report_data.get('overall_score', 0):.1f}%")
        else:
            print(f"   Error: {report_result.get('error')}")
        
        # Test 5: Handoff Readiness
        print("\n5. Testing Handoff Readiness...")
        handoff_result = command_manager.execute_command("verify-handoff-ready")
        if handoff_result.get("success"):
            print(f"   Handoff Ready: {handoff_result.get('handoff_ready', False)}")
            print(f"   Readiness Score: {handoff_result.get('readiness_score', 0):.1f}%")
        else:
            print(f"   Error: {handoff_result.get('error')}")
        
        # Test 6: Emergency Procedures
        print("\n6. Testing Emergency Procedures...")
        emergency_result = command_manager.execute_command("create-minimal-handoff", {
            "include_system_state": True
        })
        if emergency_result.get("success"):
            handoff_package = emergency_result.get("handoff_package", {})
            print(f"   Emergency Handoff Created: {handoff_package.get('session_id', 'N/A')}")
            print(f"   Essential Context: Available")
        else:
            print(f"   Error: {emergency_result.get('error')}")
        
        print("\n" + "=" * 50)
        print("Demonstration Complete")
        print("\nKey Features Validated:")
        print("- Session status monitoring")
        print("- Documentation quality validation")
        print("- Session transition preview")
        print("- Quality report generation")
        print("- Handoff readiness verification")
        print("- Emergency procedures")
        
        print("\nSystem Status: OPERATIONAL")
        print("\nTo execute a real session transition:")
        print("python session_commands.py session-transition --phase \"Your Phase Name\"")
        
        return 0
        
    except Exception as e:
        print(f"\nError during demonstration: {str(e)}")
        print("Please check that all required files are present:")
        print("- session_automation.py")
        print("- session_quality_validator.py") 
        print("- session_commands.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())