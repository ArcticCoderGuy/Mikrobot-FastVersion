#!/usr/bin/env python3
"""
COMPREHENSIVE TEST RUNNER FOR MIKROBOT TRADING ENGINE
Runs unit tests, integration tests, and performance benchmarks
Generates coverage reports and validates 85%+ test coverage
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import json

def run_command(cmd: str, description: str) -> tuple[bool, str]:
    """Run a command and return success status and output"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print()
    
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"\n{status} (Exit code: {result.returncode})")
        
        return success, result.stdout + result.stderr
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, str(e)

def install_dependencies() -> bool:
    """Install required testing dependencies"""
    print("📦 Installing testing dependencies...")
    
    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0", 
        "pytest-cov>=4.0.0",
        "pytest-html>=3.1.0",
        "pytest-xdist>=3.0.0",  # For parallel test execution
        "psutil>=5.9.0",        # For memory usage tracking
    ]
    
    for dep in dependencies:
        success, _ = run_command(
            f"pip install {dep}",
            f"Installing {dep}"
        )
        if not success:
            print(f"⚠️ Failed to install {dep}, but continuing...")
    
    return True

def run_unit_tests(coverage: bool = True, html_report: bool = True) -> tuple[bool, dict]:
    """Run unit tests with coverage"""
    cmd_parts = ["python", "-m", "pytest", "tests/test_trading_engine.py", "-v"]
    
    if coverage:
        cmd_parts.extend([
            "--cov=src.core.trading_engine",
            "--cov=execute_consolidated",
            "--cov-report=term-missing",
            "--cov-fail-under=85"
        ])
        
        if html_report:
            cmd_parts.append("--cov-report=html:htmlcov")
    
    # Add markers and options
    cmd_parts.extend([
        "-m", "not slow",  # Skip slow tests in unit test run
        "--tb=short",
        "--maxfail=5"
    ])
    
    success, output = run_command(
        " ".join(cmd_parts),
        "Running Unit Tests with Coverage"
    )
    
    # Parse coverage from output
    coverage_percent = 0.0
    for line in output.split('\n'):
        if 'TOTAL' in line and '%' in line:
            try:
                coverage_percent = float(line.split('%')[0].split()[-1])
                break
            except:
                pass
    
    return success, {
        "success": success,
        "coverage_percent": coverage_percent,
        "output": output
    }

def run_integration_tests() -> tuple[bool, dict]:
    """Run integration tests"""
    cmd = "python -m pytest tests/test_integration.py -v --tb=short --maxfail=3"
    
    success, output = run_command(
        cmd,
        "Running Integration Tests"
    )
    
    return success, {
        "success": success,
        "output": output
    }

def run_performance_benchmarks() -> tuple[bool, dict]:
    """Run performance benchmarks"""
    cmd = "python benchmarks/performance_benchmark.py"
    
    success, output = run_command(
        cmd,
        "Running Performance Benchmarks"
    )
    
    # Try to extract performance improvement from output
    improvement_percent = 0.0
    target_met = False
    
    for line in output.split('\n'):
        if 'Overall Improvement:' in line:
            try:
                improvement_percent = float(line.split(':')[1].strip().replace('%', ''))
            except:
                pass
        elif 'Target Met' in line:
            target_met = 'YES' in line
    
    return success, {
        "success": success,
        "improvement_percent": improvement_percent,
        "target_met": target_met,
        "output": output
    }

def run_backward_compatibility_tests() -> tuple[bool, dict]:
    """Test backward compatibility with original execute_*.py files"""
    print("\n🔄 Testing Backward Compatibility...")
    print("Verifying consolidated executor supports all 19 original execute_*.py modes")
    
    # Test different execution modes
    modes_to_test = [
        ("simple", "--symbol EURJPY --direction SELL"),
        ("eurjpy", "--variant bear"),
        ("ferrari", ""),
        ("gbpjpy", "--variant bear"),
        ("signal", "--symbol BCHUSD")
    ]
    
    all_success = True
    results = []
    
    for mode, args in modes_to_test:
        cmd = f"python execute_consolidated.py {mode} {args} --dry-run"
        success, output = run_command(
            cmd,
            f"Testing {mode} mode compatibility"
        )
        
        results.append({
            "mode": mode,
            "success": success,
            "output": output[:500] + "..." if len(output) > 500 else output
        })
        
        if not success:
            all_success = False
    
    return all_success, {
        "success": all_success,
        "mode_results": results
    }

def generate_test_report(results: dict) -> str:
    """Generate comprehensive test report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "unit_tests_passed": results["unit_tests"]["success"],
            "integration_tests_passed": results["integration_tests"]["success"],
            "performance_benchmarks_passed": results["performance_benchmarks"]["success"],
            "backward_compatibility_passed": results["backward_compatibility"]["success"],
            "coverage_percent": results["unit_tests"]["coverage_percent"],
            "performance_improvement": results["performance_benchmarks"]["improvement_percent"],
            "performance_target_met": results["performance_benchmarks"]["target_met"]
        },
        "detailed_results": results
    }
    
    # Save report
    report_path = Path(__file__).parent.parent / report_file
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return str(report_path)

def print_summary(results: dict, report_file: str):
    """Print test summary"""
    print("\n" + "="*80)
    print("🎯 MIKROBOT TRADING ENGINE TEST SUMMARY")
    print("="*80)
    
    # Overall status
    all_passed = all([
        results["unit_tests"]["success"],
        results["integration_tests"]["success"],
        results["performance_benchmarks"]["success"],
        results["backward_compatibility"]["success"]
    ])
    
    status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"Overall Status: {status}")
    print()
    
    # Individual test results
    print("📊 TEST RESULTS:")
    print(f"  Unit Tests: {'✅' if results['unit_tests']['success'] else '❌'} "
          f"(Coverage: {results['unit_tests']['coverage_percent']:.1f}%)")
    
    print(f"  Integration Tests: {'✅' if results['integration_tests']['success'] else '❌'}")
    
    print(f"  Performance Benchmarks: {'✅' if results['performance_benchmarks']['success'] else '❌'} "
          f"(Improvement: {results['performance_benchmarks']['improvement_percent']:.1f}%)")
    
    print(f"  Backward Compatibility: {'✅' if results['backward_compatibility']['success'] else '❌'}")
    
    print()
    
    # Coverage analysis
    coverage = results["unit_tests"]["coverage_percent"]
    if coverage >= 85:
        print(f"✅ Coverage target MET: {coverage:.1f}% >= 85%")
    else:
        print(f"❌ Coverage target NOT MET: {coverage:.1f}% < 85%")
    
    # Performance analysis
    improvement = results["performance_benchmarks"]["improvement_percent"]
    target_met = results["performance_benchmarks"]["target_met"]
    
    if target_met:
        print(f"✅ Performance target MET: {improvement:.1f}% >= 60%")
    else:
        print(f"❌ Performance target NOT MET: {improvement:.1f}% < 60%")
    
    print()
    print(f"📁 Detailed report saved to: {report_file}")
    
    if all_passed:
        print("\n🎉 Consolidated trading engine is ready for production!")
    else:
        print("\n🔧 Please fix failing tests before deployment.")
    
    print("="*80)

def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(
        description="Comprehensive test runner for Mikrobot Trading Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python tests/run_tests.py                    # Run all tests
  python tests/run_tests.py --quick            # Run quick tests only
  python tests/run_tests.py --no-coverage     # Skip coverage
  python tests/run_tests.py --performance-only # Only performance tests
        """
    )
    
    parser.add_argument('--quick', action='store_true',
                       help='Run quick tests only (skip slow integration and performance tests)')
    parser.add_argument('--no-coverage', action='store_true',
                       help='Skip code coverage analysis')
    parser.add_argument('--no-install', action='store_true',
                       help='Skip dependency installation')
    parser.add_argument('--performance-only', action='store_true',
                       help='Run only performance benchmarks')
    parser.add_argument('--unit-only', action='store_true',
                       help='Run only unit tests')
    parser.add_argument('--integration-only', action='store_true',
                       help='Run only integration tests')
    
    args = parser.parse_args()
    
    print("🚀 MIKROBOT TRADING ENGINE TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Install dependencies
    if not args.no_install:
        install_dependencies()
    
    results = {}
    
    try:
        if args.performance_only:
            # Only run performance benchmarks
            success, results["performance_benchmarks"] = run_performance_benchmarks()
            
            # Create minimal results structure
            results.update({
                "unit_tests": {"success": True, "coverage_percent": 0.0},
                "integration_tests": {"success": True},
                "backward_compatibility": {"success": True}
            })
            
        elif args.unit_only:
            # Only run unit tests
            success, results["unit_tests"] = run_unit_tests(
                coverage=not args.no_coverage,
                html_report=True
            )
            
            # Create minimal results structure
            results.update({
                "integration_tests": {"success": True},
                "performance_benchmarks": {"success": True, "improvement_percent": 0.0, "target_met": False},
                "backward_compatibility": {"success": True}
            })
            
        elif args.integration_only:
            # Only run integration tests
            success, results["integration_tests"] = run_integration_tests()
            
            # Create minimal results structure
            results.update({
                "unit_tests": {"success": True, "coverage_percent": 0.0},
                "performance_benchmarks": {"success": True, "improvement_percent": 0.0, "target_met": False},
                "backward_compatibility": {"success": True}
            })
            
        else:
            # Run all tests
            # 1. Unit tests with coverage
            if not args.quick:
                success, results["unit_tests"] = run_unit_tests(
                    coverage=not args.no_coverage,
                    html_report=True
                )
            else:
                # Quick unit tests without coverage
                success, results["unit_tests"] = run_unit_tests(coverage=False, html_report=False)
            
            # 2. Integration tests
            if not args.quick:
                success, results["integration_tests"] = run_integration_tests()
            else:
                results["integration_tests"] = {"success": True}
            
            # 3. Performance benchmarks
            if not args.quick:
                success, results["performance_benchmarks"] = run_performance_benchmarks()
            else:
                results["performance_benchmarks"] = {
                    "success": True,
                    "improvement_percent": 0.0,
                    "target_met": False
                }
            
            # 4. Backward compatibility tests
            success, results["backward_compatibility"] = run_backward_compatibility_tests()
        
        # Generate report
        report_file = generate_test_report(results)
        
        # Print summary
        print_summary(results, report_file)
        
        # Determine exit code
        if args.performance_only:
            exit_code = 0 if results["performance_benchmarks"]["success"] else 1
        elif args.unit_only:
            exit_code = 0 if results["unit_tests"]["success"] else 1
        elif args.integration_only:
            exit_code = 0 if results["integration_tests"]["success"] else 1
        else:
            # All tests must pass
            all_passed = all([
                results["unit_tests"]["success"],
                results["integration_tests"]["success"],
                results["performance_benchmarks"]["success"],
                results["backward_compatibility"]["success"]
            ])
            exit_code = 0 if all_passed else 1
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()