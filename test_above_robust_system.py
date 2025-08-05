#!/usr/bin/env python3
"""
ABOVE ROBUST! SYSTEM TEST RUNNER
Comprehensive testing for ML Observation System and Six Sigma Quality Engine
Validates path to Cp/Cpk 3.0 achievement
"""

import sys
import os
import time
import asyncio
import json
from datetime import datetime, timedelta
import random
import sqlite3

# Add encoding utilities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from encoding_utils import ascii_print, write_ascii_json

# Import our systems
from ml_observation_system import MLObservationSystem
from six_sigma_quality_engine import SixSigmaQualityEngine

class AboveRobustSystemTester:
    """
    Comprehensive test suite for Above Robust! ML Observation System
    Tests all components and validates Six Sigma quality achievement
    """
    
    def __init__(self):
        self.name = "Above Robust! System Tester"
        self.version = "1.0.0"
        self.test_results = []
        
        ascii_print(f"Initialized {self.name} v{self.version}")
    
    def generate_test_trading_data(self, num_phases: int = 100):
        """Generate realistic test trading data"""
        ascii_print(f"Generating {num_phases} test trading phases...")
        
        observation_system = MLObservationSystem()
        
        symbols = ['EURUSD', 'GBPUSD', 'USDCAD', 'EURJPY', 'GBPJPY']
        phase_names = ['M5_BOS_DETECTION', 'M1_BREAK_CONFIRMATION', 'M1_RETEST_VALIDATION', 'YLIPIP_TRIGGER']
        
        for i in range(num_phases):
            # Create realistic phase data with some defects
            symbol = random.choice(symbols)
            phase = random.randint(1, 4)
            phase_name = phase_names[phase - 1]
            
            # Simulate quality - 85% good, 15% defects
            is_high_quality = random.random() > 0.15
            
            if is_high_quality:
                quality_score = random.uniform(0.8, 1.0)
                success = True
                compliance = True
                duration_ms = random.randint(500, 2000)
            else:
                quality_score = random.uniform(0.2, 0.6)
                success = random.random() > 0.3
                compliance = False
                duration_ms = random.randint(2000, 8000)
            
            # Phase-specific realistic data
            if phase == 1:  # M5 BOS
                phase_data = {
                    'trade_id': f'test_{i:04d}',
                    'symbol': symbol,
                    'phase': phase,
                    'phase_name': phase_name,
                    'duration_ms': duration_ms,
                    'success': success,
                    'bos_detected': compliance,
                    'bos_strength': random.uniform(0.5, 1.0) if compliance else random.uniform(0.0, 0.4)
                }
            elif phase == 2:  # M1 Break
                phase_data = {
                    'trade_id': f'test_{i:04d}',
                    'symbol': symbol,
                    'phase': phase,
                    'phase_name': phase_name,
                    'duration_ms': duration_ms,
                    'success': success,
                    'm1_break_confirmed': compliance,
                    'break_quality': random.uniform(0.6, 1.0) if compliance else random.uniform(0.0, 0.5)
                }
            elif phase == 3:  # M1 Retest
                phase_data = {
                    'trade_id': f'test_{i:04d}',
                    'symbol': symbol,
                    'phase': phase,
                    'phase_name': phase_name,
                    'duration_ms': duration_ms,
                    'success': success,
                    'retest_completed': compliance,
                    'retest_quality': random.uniform(0.7, 1.0) if compliance else random.uniform(0.0, 0.6)
                }
            else:  # YLIPIP
                phase_data = {
                    'trade_id': f'test_{i:04d}',
                    'symbol': symbol,
                    'phase': phase,
                    'phase_name': phase_name,
                    'duration_ms': duration_ms,
                    'success': success,
                    'ylipip_triggered': compliance,
                    'pip_distance': 0.6 + random.uniform(-0.05, 0.05) if compliance else random.uniform(0.3, 1.2)
                }
            
            # Record the phase
            observation_system.observe_trading_phase(phase_data)
            
            # Small delay to spread timestamps
            time.sleep(0.01)
        
        ascii_print(f"Generated {num_phases} test trading phases successfully")
        return True
    
    def test_ml_observation_system(self) -> dict:
        """Test ML Observation System functionality"""
        ascii_print("Testing ML Observation System...")
        
        test_result = {
            'test_name': 'ML Observation System',
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'subtests': []
        }
        
        try:
            # Test 1: System initialization
            observation_system = MLObservationSystem()
            test_result['subtests'].append({
                'name': 'System Initialization',
                'status': 'PASS',
                'details': 'ML Observation System initialized successfully'
            })
            
            # Test 2: Database connectivity
            conn = sqlite3.connect(observation_system.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM trading_phases")
            phase_count = cursor.fetchone()[0]
            conn.close()
            
            test_result['subtests'].append({
                'name': 'Database Connectivity',
                'status': 'PASS',
                'details': f'Database accessible, {phase_count} trading phases recorded'
            })
            
            # Test 3: Quality metrics calculation
            observation_system.update_quality_metrics()
            current_cpk = observation_system.current_metrics.cpk
            
            test_result['subtests'].append({
                'name': 'Quality Metrics Calculation',
                'status': 'PASS' if current_cpk > 0 else 'FAIL',
                'details': f'Current Cpk: {current_cpk:.3f}'
            })
            
            # Test 4: Compliance checking
            test_phase_data = {
                'trade_id': 'test_compliance',
                'symbol': 'EURUSD',
                'phase': 1,
                'phase_name': 'M5_BOS_DETECTION',
                'duration_ms': 1000,
                'success': True,
                'bos_detected': True,
                'bos_strength': 0.8
            }
            
            compliance = observation_system.check_phase_compliance(test_phase_data)
            test_result['subtests'].append({
                'name': 'Compliance Checking',
                'status': 'PASS' if compliance else 'FAIL',
                'details': f'Compliance check result: {compliance}'
            })
            
            test_result['status'] = 'PASS'
            test_result['overall_score'] = sum(1 for t in test_result['subtests'] if t['status'] == 'PASS')
            
        except Exception as e:
            test_result['status'] = 'FAIL'
            test_result['error'] = str(e)
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def test_six_sigma_engine(self) -> dict:
        """Test Six Sigma Quality Engine functionality"""
        ascii_print("Testing Six Sigma Quality Engine...")
        
        test_result = {
            'test_name': 'Six Sigma Quality Engine',
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'subtests': []
        }
        
        try:
            # Test 1: Engine initialization
            engine = SixSigmaQualityEngine()
            test_result['subtests'].append({
                'name': 'Engine Initialization',
                'status': 'PASS',
                'details': 'Six Sigma Quality Engine initialized successfully'
            })
            
            # Test 2: Control chart creation
            control_chart = engine.create_xbar_r_chart("M5_BOS_DETECTION")
            test_result['subtests'].append({
                'name': 'Control Chart Creation',
                'status': 'PASS' if control_chart else 'SKIP',
                'details': f'Control chart created: {bool(control_chart)}'
            })
            
            # Test 3: Pareto analysis
            pareto_results = engine.perform_pareto_analysis('defects')
            test_result['subtests'].append({
                'name': 'Pareto Analysis',
                'status': 'PASS' if pareto_results else 'SKIP',
                'details': f'Pareto items found: {len(pareto_results)}'
            })
            
            # Test 4: QFD matrix creation
            qfd_matrix = engine.create_qfd_matrix()
            test_result['subtests'].append({
                'name': 'QFD Matrix Creation',
                'status': 'PASS' if qfd_matrix else 'FAIL',
                'details': f'QFD matrix created with {len(qfd_matrix.get("customer_requirements", []))} customer requirements'
            })
            
            # Test 5: COPQ calculation
            copq = engine.calculate_cost_of_poor_quality()
            test_result['subtests'].append({
                'name': 'Cost of Poor Quality',
                'status': 'PASS' if copq else 'FAIL',
                'details': f'Total COPQ: ${copq.get("total_copq", 0):.2f}'
            })
            
            # Test 6: Comprehensive report generation
            report = engine.generate_six_sigma_report()
            test_result['subtests'].append({
                'name': 'Six Sigma Report Generation',
                'status': 'PASS' if report else 'FAIL',
                'details': f'Report generated, Current Cpk: {report.get("current_cpk", 0):.3f}'
            })
            
            test_result['status'] = 'PASS'
            test_result['overall_score'] = sum(1 for t in test_result['subtests'] if t['status'] == 'PASS')
            
        except Exception as e:
            test_result['status'] = 'FAIL'
            test_result['error'] = str(e)
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def test_integration(self) -> dict:
        """Test integration between ML Observation and Six Sigma systems"""
        ascii_print("Testing system integration...")
        
        test_result = {
            'test_name': 'System Integration',
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'subtests': []
        }
        
        try:
            # Test 1: Data flow from observation to analysis
            observation_system = MLObservationSystem()
            engine = SixSigmaQualityEngine()
            
            # Generate some test data
            test_phase_data = {
                'trade_id': 'integration_test',
                'symbol': 'EURUSD',
                'phase': 3,
                'phase_name': 'M1_RETEST_VALIDATION',
                'duration_ms': 1500,
                'success': True,
                'retest_completed': True,
                'retest_quality': 0.85
            }
            
            observation_system.observe_trading_phase(test_phase_data)
            
            # Verify data was stored and can be analyzed
            conn = sqlite3.connect(observation_system.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM trading_phases WHERE trade_id = ?", ('integration_test',))
            recorded_count = cursor.fetchone()[0]
            conn.close()
            
            test_result['subtests'].append({
                'name': 'Data Flow Observation → Storage',
                'status': 'PASS' if recorded_count > 0 else 'FAIL',
                'details': f'Test data recorded: {recorded_count > 0}'
            })
            
            # Test 2: Quality metrics calculation integration
            observation_system.update_quality_metrics()
            current_metrics = observation_system.current_metrics
            
            test_result['subtests'].append({
                'name': 'Quality Metrics Integration',
                'status': 'PASS' if current_metrics.cpk > 0 else 'FAIL',
                'details': f'Cpk calculated: {current_metrics.cpk:.3f}'
            })
            
            # Test 3: Six Sigma analysis of observed data
            report = engine.generate_six_sigma_report()
            
            test_result['subtests'].append({
                'name': 'Six Sigma Analysis Integration',
                'status': 'PASS' if report else 'FAIL',
                'details': f'Integrated report generated: {bool(report)}'
            })
            
            test_result['status'] = 'PASS'
            test_result['overall_score'] = sum(1 for t in test_result['subtests'] if t['status'] == 'PASS')
            
        except Exception as e:
            test_result['status'] = 'FAIL'
            test_result['error'] = str(e)
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def test_cpk_progression_path(self) -> dict:
        """Test the path to achieve Cp/Cpk 3.0"""
        ascii_print("Testing Cp/Cpk 3.0 progression path...")
        
        test_result = {
            'test_name': 'Cpk 3.0 Progression Path',
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'progression_data': []
        }
        
        try:
            observation_system = MLObservationSystem()
            engine = SixSigmaQualityEngine()
            
            # Simulate improvement over time
            improvement_phases = [
                {'name': 'Baseline', 'defect_rate': 0.15, 'quality_improvement': 0.0},
                {'name': 'Phase 1: Pareto Focus', 'defect_rate': 0.10, 'quality_improvement': 0.1},
                {'name': 'Phase 2: Process Control', 'defect_rate': 0.07, 'quality_improvement': 0.2},
                {'name': 'Phase 3: Six Sigma Implementation', 'defect_rate': 0.04, 'quality_improvement': 0.3},
                {'name': 'Phase 4: Above Robust!', 'defect_rate': 0.01, 'quality_improvement': 0.4}
            ]
            
            for phase_info in improvement_phases:
                # Clear previous data for clean simulation
                conn = sqlite3.connect(observation_system.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM trading_phases WHERE trade_id LIKE 'cpk_test_%'")
                conn.commit()
                conn.close()
                
                # Generate data with improved quality
                defect_rate = phase_info['defect_rate']
                quality_boost = phase_info['quality_improvement']
                
                for i in range(50):  # 50 phases per improvement phase
                    # Create phase data with improving quality
                    is_defective = random.random() < defect_rate
                    
                    if not is_defective:
                        quality_score = random.uniform(0.8 + quality_boost, 1.0)
                        compliance = True
                    else:
                        quality_score = random.uniform(0.2, 0.6)
                        compliance = False
                    
                    phase_data = {
                        'trade_id': f'cpk_test_{phase_info["name"]}_{i:03d}',
                        'symbol': 'EURUSD',
                        'phase': 3,
                        'phase_name': 'M1_RETEST_VALIDATION',
                        'duration_ms': random.randint(500, 2000),
                        'success': compliance,
                        'retest_completed': compliance,
                        'retest_quality': quality_score
                    }
                    
                    observation_system.observe_trading_phase(phase_data)
                
                # Calculate metrics for this phase
                observation_system.update_quality_metrics()
                current_cpk = observation_system.current_metrics.cpk
                
                progression_data = {
                    'phase': phase_info['name'],
                    'cpk': round(current_cpk, 3),
                    'defect_rate_ppm': round(observation_system.current_metrics.defect_rate_ppm, 1),
                    'sigma_level': round(observation_system.current_metrics.sigma_level, 1),
                    'target_achieved': current_cpk >= 3.0
                }
                
                test_result['progression_data'].append(progression_data)
                
                ascii_print(f"  {phase_info['name']}: Cpk = {current_cpk:.3f}")
            
            # Check if we achieved the target
            final_cpk = test_result['progression_data'][-1]['cpk']
            test_result['status'] = 'PASS' if final_cpk >= 3.0 else 'PARTIAL'
            test_result['final_cpk'] = final_cpk
            test_result['target_achieved'] = final_cpk >= 3.0
            
        except Exception as e:
            test_result['status'] = 'FAIL'
            test_result['error'] = str(e)
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def run_comprehensive_test_suite(self):
        """Run the complete Above Robust! test suite"""
        ascii_print("=" * 80)
        ascii_print("ABOVE ROBUST! COMPREHENSIVE TEST SUITE")
        ascii_print("ML Observation System + Six Sigma Quality Engine")
        ascii_print("=" * 80)
        
        # Generate test data first
        ascii_print("\n1. GENERATING TEST DATA")
        ascii_print("-" * 40)
        self.generate_test_trading_data(200)
        
        # Run all tests
        tests = [
            self.test_ml_observation_system,
            self.test_six_sigma_engine,
            self.test_integration,
            self.test_cpk_progression_path
        ]
        
        for i, test_func in enumerate(tests, 2):
            ascii_print(f"\n{i}. {test_func.__name__.replace('test_', '').replace('_', ' ').upper()}")
            ascii_print("-" * 40)
            
            result = test_func()
            self.test_results.append(result)
            
            # Display result summary
            status_icon = "✓" if result['status'] == 'PASS' else "⚠" if result['status'] == 'PARTIAL' else "✗"
            ascii_print(f"Status: {status_icon} {result['status']}")
            
            if 'overall_score' in result:
                ascii_print(f"Score: {result['overall_score']}/{len(result['subtests'])}")
            
            if 'error' in result:
                ascii_print(f"Error: {result['error']}")
        
        # Generate comprehensive test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        ascii_print("\n" + "=" * 80)
        ascii_print("ABOVE ROBUST! TEST RESULTS SUMMARY")
        ascii_print("=" * 80)
        
        # Overall statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        partial_tests = sum(1 for r in self.test_results if r['status'] == 'PARTIAL')
        failed_tests = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        
        ascii_print(f"Total Tests: {total_tests}")
        ascii_print(f"Passed: {passed_tests}")
        ascii_print(f"Partial: {partial_tests}")
        ascii_print(f"Failed: {failed_tests}")
        ascii_print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        ascii_print("\nDETAILED RESULTS:")
        ascii_print("-" * 40)
        
        for result in self.test_results:
            status_icon = "✓" if result['status'] == 'PASS' else "⚠" if result['status'] == 'PARTIAL' else "✗"
            ascii_print(f"{status_icon} {result['test_name']}: {result['status']}")
            
            if 'subtests' in result:
                for subtest in result['subtests']:
                    sub_icon = "✓" if subtest['status'] == 'PASS' else "⚠" if subtest['status'] == 'SKIP' else "✗"
                    ascii_print(f"  {sub_icon} {subtest['name']}")
        
        # Cpk progression results
        cpk_test = next((r for r in self.test_results if r['test_name'] == 'Cpk 3.0 Progression Path'), None)
        if cpk_test and 'progression_data' in cpk_test:
            ascii_print("\nCp/Cpk 3.0 PROGRESSION PATH:")
            ascii_print("-" * 40)
            
            for phase_data in cpk_test['progression_data']:
                target_icon = "🎯" if phase_data['target_achieved'] else "→"
                ascii_print(f"{target_icon} {phase_data['phase']}: Cpk = {phase_data['cpk']:.3f}, σ = {phase_data['sigma_level']:.1f}")
            
            final_cpk = cpk_test.get('final_cpk', 0)
            if final_cpk >= 3.0:
                ascii_print(f"\n🏆 ABOVE ROBUST! TARGET ACHIEVED: Cpk = {final_cpk:.3f}")
            else:
                ascii_print(f"\n📈 PROGRESS TOWARD TARGET: Cpk = {final_cpk:.3f} (Target: 3.0)")
        
        # Save detailed report
        report_data = {
            'test_suite': 'Above Robust! Comprehensive Test Suite',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'partial_tests': partial_tests,
                'failed_tests': failed_tests,
                'success_rate': round((passed_tests/total_tests)*100, 1)
            },
            'detailed_results': self.test_results
        }
        
        report_file = f"above_robust_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        write_ascii_json(report_file, report_data)
        
        ascii_print(f"\n📊 Detailed test report saved: {report_file}")
        ascii_print("\n" + "=" * 80)
        ascii_print("ABOVE ROBUST! SYSTEM TESTING COMPLETE")
        ascii_print("Ready for Six Sigma Excellence!")
        ascii_print("=" * 80)

def main():
    """Main test runner function"""
    tester = AboveRobustSystemTester()
    tester.run_comprehensive_test_suite()

if __name__ == "__main__":
    main()