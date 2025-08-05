#!/usr/bin/env python3
"""
SIX SIGMA QUALITY ENGINE - ABOVE ROBUST! IMPLEMENTATION
Statistical Process Control, Pareto Analysis, and QFD for Mikrobot
Target: Cp/Cpk = 3.0 and Six Sigma Quality Excellence
"""

import sys
import os
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import statistics
import math
from dataclasses import dataclass

# Add encoding utilities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from encoding_utils import ascii_print, write_ascii_json

@dataclass
class ControlLimits:
    """Control chart limits"""
    ucl: float  # Upper Control Limit
    lcl: float  # Lower Control Limit
    center_line: float
    usl: float  # Upper Spec Limit
    lsl: float  # Lower Spec Limit

@dataclass
class ParetoItem:
    """Pareto analysis item"""
    category: str
    frequency: int
    percentage: float
    cumulative_percentage: float
    cost_impact: float

class SixSigmaQualityEngine:
    """
    Six Sigma Quality Engine for Mikrobot Trading System
    Implements SPC, Pareto Analysis, QFD, and DMAIC methodology
    """
    
    def __init__(self, db_path: str = "mikrobot_quality_metrics.db"):
        self.db_path = db_path
        self.name = "Six Sigma Quality Engine"
        self.version = "1.0.0"
        
        # Quality standards
        self.target_sigma_level = 6.0
        self.target_cpk = 3.0
        self.target_defect_rate_ppm = 3.4
        
        # Western Electric Rules for control chart violations
        self.western_electric_rules = {
            'rule1': 'One point beyond 3σ',
            'rule2': 'Nine consecutive points on same side of center',
            'rule3': 'Six consecutive increasing or decreasing points',
            'rule4': 'Fourteen alternating up/down points',
            'rule5': 'Two of three consecutive points beyond 2σ',
            'rule6': 'Four of five consecutive points beyond 1σ',
            'rule7': 'Fifteen consecutive points within 1σ',
            'rule8': 'Eight consecutive points beyond 1σ on both sides'
        }
        
        ascii_print(f"Initialized {self.name} v{self.version}")
        ascii_print(f"Target: Cp/Cpk >= {self.target_cpk}, σ-level >= {self.target_sigma_level}")
    
    def create_xbar_r_chart(self, process_name: str, sample_size: int = 5) -> Dict[str, Any]:
        """Create X-bar and R control charts for process monitoring"""
        conn = sqlite3.connect(self.db_path)
        
        # Get recent trading phase data
        query = '''
        SELECT quality_score, timestamp FROM trading_phases 
        WHERE phase_name = ? 
        ORDER BY timestamp DESC LIMIT 100
        '''
        
        df = pd.read_sql_query(query, conn, params=(process_name,))
        conn.close()
        
        if len(df) < sample_size * 5:  # Need at least 5 subgroups
            ascii_print(f"Insufficient data for {process_name} control chart")
            return {}
        
        # Create subgroups
        subgroups = []
        values = df['quality_score'].values
        
        for i in range(0, len(values) - sample_size + 1, sample_size):
            subgroup = values[i:i + sample_size]
            subgroups.append({
                'mean': np.mean(subgroup),
                'range': np.max(subgroup) - np.min(subgroup),
                'values': subgroup.tolist()
            })
        
        if len(subgroups) < 5:
            return {}
        
        # Calculate control limits for X-bar chart
        subgroup_means = [sg['mean'] for sg in subgroups]
        grand_mean = np.mean(subgroup_means)
        
        subgroup_ranges = [sg['range'] for sg in subgroups]
        mean_range = np.mean(subgroup_ranges)
        
        # Control chart constants for sample size
        constants = self.get_control_chart_constants(sample_size)
        
        xbar_ucl = grand_mean + constants['A2'] * mean_range
        xbar_lcl = grand_mean - constants['A2'] * mean_range
        
        # Control limits for R chart
        r_ucl = constants['D4'] * mean_range
        r_lcl = constants['D3'] * mean_range
        
        # Check for violations
        xbar_violations = self.check_western_electric_rules(subgroup_means, grand_mean, xbar_ucl, xbar_lcl)
        r_violations = self.check_western_electric_rules(subgroup_ranges, mean_range, r_ucl, r_lcl)
        
        control_chart = {
            'process_name': process_name,
            'chart_type': 'X-bar_R',
            'sample_size': sample_size,
            'subgroups_count': len(subgroups),
            'xbar_chart': {
                'center_line': grand_mean,
                'ucl': xbar_ucl,
                'lcl': xbar_lcl,
                'values': subgroup_means,
                'violations': xbar_violations
            },
            'r_chart': {
                'center_line': mean_range,
                'ucl': r_ucl,
                'lcl': r_lcl,
                'values': subgroup_ranges,
                'violations': r_violations
            },
            'process_capability': self.calculate_process_capability_from_chart(subgroups, 0.9, 0.4),
            'control_status': 'in_control' if not xbar_violations and not r_violations else 'out_of_control'
        }
        
        # Store in database
        self.store_control_chart_data(control_chart)
        
        return control_chart
    
    def get_control_chart_constants(self, sample_size: int) -> Dict[str, float]:
        """Get control chart constants for given sample size"""
        constants_table = {
            2: {'A2': 1.880, 'D3': 0, 'D4': 3.267},
            3: {'A2': 1.023, 'D3': 0, 'D4': 2.574},
            4: {'A2': 0.729, 'D3': 0, 'D4': 2.282},
            5: {'A2': 0.577, 'D3': 0, 'D4': 2.114},
            6: {'A2': 0.483, 'D3': 0, 'D4': 2.004},
            7: {'A2': 0.419, 'D3': 0.076, 'D4': 1.924},
            8: {'A2': 0.373, 'D3': 0.136, 'D4': 1.864},
            9: {'A2': 0.337, 'D3': 0.184, 'D4': 1.816},
            10: {'A2': 0.308, 'D3': 0.223, 'D4': 1.777}
        }
        
        return constants_table.get(sample_size, constants_table[5])  # Default to n=5
    
    def check_western_electric_rules(self, values: List[float], center_line: float, 
                                   ucl: float, lcl: float) -> List[Dict[str, Any]]:
        """Check Western Electric Rules for control chart violations"""
        violations = []
        n = len(values)
        
        if n < 9:  # Need minimum data points
            return violations
        
        # Calculate sigma zones
        sigma = (ucl - center_line) / 3
        zone_a_upper = center_line + 2 * sigma
        zone_a_lower = center_line - 2 * sigma
        zone_b_upper = center_line + sigma
        zone_b_lower = center_line - sigma
        
        for i in range(n):
            point = values[i]
            
            # Rule 1: One point beyond 3σ
            if point > ucl or point < lcl:
                violations.append({
                    'rule': 'rule1',
                    'description': self.western_electric_rules['rule1'],
                    'point_index': i,
                    'point_value': point,
                    'severity': 'high'
                })
            
            # Rule 2: Nine consecutive points on same side of center
            if i >= 8:
                last_nine = values[i-8:i+1]
                if all(v > center_line for v in last_nine) or all(v < center_line for v in last_nine):
                    violations.append({
                        'rule': 'rule2',
                        'description': self.western_electric_rules['rule2'],
                        'point_index': i,
                        'sequence_start': i-8,
                        'severity': 'medium'
                    })
            
            # Rule 3: Six consecutive increasing or decreasing points
            if i >= 5:
                last_six = values[i-5:i+1]
                increasing = all(last_six[j] < last_six[j+1] for j in range(5))
                decreasing = all(last_six[j] > last_six[j+1] for j in range(5))
                
                if increasing or decreasing:
                    violations.append({
                        'rule': 'rule3',
                        'description': self.western_electric_rules['rule3'],
                        'point_index': i,
                        'trend': 'increasing' if increasing else 'decreasing',
                        'severity': 'medium'
                    })
            
            # Rule 5: Two of three consecutive points beyond 2σ
            if i >= 2:
                last_three = values[i-2:i+1]
                beyond_2sigma = sum(1 for v in last_three 
                                  if v > zone_a_upper or v < zone_a_lower)
                
                if beyond_2sigma >= 2:
                    violations.append({
                        'rule': 'rule5',
                        'description': self.western_electric_rules['rule5'],
                        'point_index': i,
                        'severity': 'medium'
                    })
        
        return violations
    
    def calculate_process_capability_from_chart(self, subgroups: List[Dict], 
                                             target: float, tolerance: float) -> Dict[str, float]:
        """Calculate process capability from control chart data"""
        all_values = []
        for sg in subgroups:
            all_values.extend(sg['values'])
        
        if len(all_values) < 10:
            return {'cp': 0.0, 'cpk': 0.0, 'pp': 0.0, 'ppk': 0.0}
        
        mean = np.mean(all_values)
        std_dev = np.std(all_values, ddof=1)  # Sample standard deviation
        
        # Specification limits
        usl = target + tolerance
        lsl = target - tolerance
        
        # Process capability indices
        cp = (usl - lsl) / (6 * std_dev) if std_dev > 0 else float('inf')
        
        cpu = (usl - mean) / (3 * std_dev) if std_dev > 0 else float('inf')
        cpl = (mean - lsl) / (3 * std_dev) if std_dev > 0 else float('inf')
        cpk = min(cpu, cpl)
        
        # Process performance indices (using total variation)
        pp = cp  # For this implementation, assume process is in control
        ppk = cpk
        
        return {
            'cp': round(cp, 3),
            'cpk': round(cpk, 3),
            'pp': round(pp, 3),
            'ppk': round(ppk, 3),
            'mean': round(mean, 3),
            'std_dev': round(std_dev, 4)
        }
    
    def perform_pareto_analysis(self, analysis_type: str = 'defects') -> List[ParetoItem]:
        """Perform Pareto analysis on defects or issues"""
        conn = sqlite3.connect(self.db_path)
        
        if analysis_type == 'defects':
            query = '''
            SELECT defect_type, COUNT(*) as frequency, AVG(COALESCE(cost_impact, 100)) as avg_cost
            FROM trading_phases 
            WHERE defect_type IS NOT NULL 
            GROUP BY defect_type
            ORDER BY frequency DESC
            '''
        else:  # journal errors
            query = '''
            SELECT error_category, COUNT(*) as frequency, AVG(impact_level * 50) as avg_cost
            FROM journal_observations 
            WHERE error_category IS NOT NULL 
            GROUP BY error_category
            ORDER BY frequency DESC
            '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return []
        
        # Calculate Pareto items
        total_frequency = df['frequency'].sum()
        cumulative_percentage = 0
        pareto_items = []
        
        for _, row in df.iterrows():
            percentage = (row['frequency'] / total_frequency) * 100
            cumulative_percentage += percentage
            
            pareto_items.append(ParetoItem(
                category=row.iloc[0],  # First column (defect_type or error_category)
                frequency=int(row['frequency']),
                percentage=round(percentage, 1),
                cumulative_percentage=round(cumulative_percentage, 1),
                cost_impact=round(row['avg_cost'], 2)
            ))
        
        # Store Pareto analysis results
        self.store_pareto_analysis(pareto_items, analysis_type)
        
        return pareto_items
    
    def identify_vital_few(self, pareto_items: List[ParetoItem], threshold: float = 80.0) -> Dict[str, Any]:
        """Identify the vital few (80/20 rule) from Pareto analysis"""
        vital_few = []
        useful_many = []
        
        for item in pareto_items:
            if item.cumulative_percentage <= threshold:
                vital_few.append(item)
            else:
                useful_many.append(item)
        
        # Calculate impact
        vital_few_frequency = sum(item.frequency for item in vital_few)
        total_frequency = sum(item.frequency for item in pareto_items)
        vital_few_impact = (vital_few_frequency / total_frequency) * 100 if total_frequency > 0 else 0
        
        vital_few_cost = sum(item.cost_impact * item.frequency for item in vital_few)
        total_cost = sum(item.cost_impact * item.frequency for item in pareto_items)
        vital_few_cost_impact = (vital_few_cost / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            'vital_few': vital_few,
            'useful_many': useful_many,
            'vital_few_count': len(vital_few),
            'vital_few_impact_percent': round(vital_few_impact, 1),
            'vital_few_cost_impact_percent': round(vital_few_cost_impact, 1),
            'recommendation': self.generate_improvement_recommendations(vital_few)
        }
    
    def generate_improvement_recommendations(self, vital_few: List[ParetoItem]) -> List[Dict[str, str]]:
        """Generate improvement recommendations based on vital few"""
        recommendations = []
        
        for item in vital_few:
            category = item.category
            
            if category == "NO_M1_CONFIRMATION":
                recommendations.append({
                    'category': category,
                    'recommendation': 'Improve M1 timeframe validation logic',
                    'priority': 'high',
                    'estimated_impact': 'Reduce 35% of trading failures'
                })
            elif category == "POOR_RETEST_QUALITY":
                recommendations.append({
                    'category': category,
                    'recommendation': 'Enhance retest quality scoring algorithm',
                    'priority': 'high',
                    'estimated_impact': 'Improve trade entry accuracy by 25%'
                })
            elif category == "AUTO_TRADING_DISABLED":
                recommendations.append({
                    'category': category,
                    'recommendation': 'Implement auto-trading status monitoring and alerts',
                    'priority': 'critical',
                    'estimated_impact': 'Prevent 100% of auto-trading failures'
                })
            elif category == "CONNECTION_FAILURE":
                recommendations.append({
                    'category': category,
                    'recommendation': 'Add connection redundancy and auto-reconnect',
                    'priority': 'high',
                    'estimated_impact': 'Reduce connection-related losses by 80%'
                })
            else:
                recommendations.append({
                    'category': category,
                    'recommendation': f'Investigate and address {category} root causes',
                    'priority': 'medium',
                    'estimated_impact': f'Reduce {category} frequency by 50%'
                })
        
        return recommendations
    
    def create_qfd_matrix(self) -> Dict[str, Any]:
        """Create Quality Function Deployment (House of Quality) matrix"""
        
        # Customer requirements (Voice of Customer)
        customer_requirements = [
            {'requirement': 'High Win Rate', 'importance': 9, 'current_satisfaction': 7},
            {'requirement': 'Low Risk per Trade', 'importance': 8, 'current_satisfaction': 8},
            {'requirement': 'Consistent Performance', 'importance': 9, 'current_satisfaction': 6},
            {'requirement': 'Fast Execution', 'importance': 7, 'current_satisfaction': 8},
            {'requirement': 'System Reliability', 'importance': 8, 'current_satisfaction': 7},
            {'requirement': 'Easy Monitoring', 'importance': 6, 'current_satisfaction': 5}
        ]
        
        # Technical characteristics (How to deliver)
        technical_characteristics = [
            'M5 BOS Accuracy',
            'M1 Confirmation Quality', 
            'Retest Validation Precision',
            'YLIPIP Trigger Accuracy',
            'Position Sizing Precision',
            'Execution Latency',
            'System Uptime',
            'Error Rate'
        ]
        
        # Relationship matrix (9=strong, 3=medium, 1=weak, 0=none)
        relationship_matrix = [
            [9, 9, 9, 9, 3, 1, 3, 9],  # High Win Rate
            [3, 3, 3, 3, 9, 1, 3, 3],  # Low Risk per Trade
            [9, 9, 9, 9, 9, 3, 9, 9],  # Consistent Performance
            [3, 3, 3, 3, 1, 9, 3, 3],  # Fast Execution
            [1, 1, 1, 1, 1, 3, 9, 9],  # System Reliability
            [1, 1, 1, 1, 1, 1, 3, 3]   # Easy Monitoring
        ]
        
        # Calculate weighted importance for technical characteristics
        weighted_importance = []
        for j in range(len(technical_characteristics)):
            total_weight = 0
            for i in range(len(customer_requirements)):
                importance = customer_requirements[i]['importance']
                relationship = relationship_matrix[i][j]
                total_weight += importance * relationship
            weighted_importance.append(total_weight)
        
        # Current technical performance (estimated)
        current_performance = [8.2, 7.5, 6.8, 8.9, 9.1, 8.5, 8.0, 7.2]  # Out of 10
        target_performance = [9.5, 9.0, 9.0, 9.5, 9.8, 9.0, 9.5, 9.0]   # Target values
        
        # Prioritize improvements
        improvement_priorities = []
        for i, char in enumerate(technical_characteristics):
            improvement_needed = target_performance[i] - current_performance[i]
            priority_score = weighted_importance[i] * improvement_needed
            
            improvement_priorities.append({
                'characteristic': char,
                'weighted_importance': weighted_importance[i],
                'current_performance': current_performance[i],
                'target_performance': target_performance[i],
                'improvement_needed': round(improvement_needed, 1),
                'priority_score': round(priority_score, 1)
            })
        
        # Sort by priority score
        improvement_priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        
        qfd_matrix = {
            'customer_requirements': customer_requirements,
            'technical_characteristics': technical_characteristics,
            'relationship_matrix': relationship_matrix,
            'weighted_importance': weighted_importance,
            'improvement_priorities': improvement_priorities,
            'top_3_priorities': improvement_priorities[:3]
        }
        
        return qfd_matrix
    
    def calculate_cost_of_poor_quality(self) -> Dict[str, float]:
        """Calculate Cost of Poor Quality (COPQ)"""
        conn = sqlite3.connect(self.db_path)
        
        # Get defect data from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        query = '''
        SELECT COUNT(*) as total_phases,
               SUM(CASE WHEN compliance = 0 THEN 1 ELSE 0 END) as defective_phases
        FROM trading_phases 
        WHERE timestamp >= ?
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (thirty_days_ago,))
        result = cursor.fetchone()
        
        total_phases = result[0] if result[0] else 0
        defective_phases = result[1] if result[1] else 0
        
        # Estimate costs
        avg_trade_value = 560.0  # Average risk per trade (0.55% of 102K)
        defect_cost_per_trade = avg_trade_value * 0.5  # 50% of trade value lost per defect
        
        # Calculate COPQ components
        internal_failure_cost = defective_phases * defect_cost_per_trade
        external_failure_cost = defective_phases * defect_cost_per_trade * 0.3  # Customer impact
        appraisal_cost = total_phases * 5.0  # Cost of monitoring/testing
        prevention_cost = 1000.0  # Monthly cost of quality system
        
        total_copq = internal_failure_cost + external_failure_cost + appraisal_cost + prevention_cost
        
        # Calculate potential savings with Six Sigma
        current_defect_rate = (defective_phases / total_phases) if total_phases > 0 else 0
        six_sigma_defect_rate = 0.0000034  # 3.4 PPM
        
        potential_defects_prevented = total_phases * (current_defect_rate - six_sigma_defect_rate)
        potential_savings = potential_defects_prevented * defect_cost_per_trade
        
        conn.close()
        
        return {
            'internal_failure_cost': round(internal_failure_cost, 2),
            'external_failure_cost': round(external_failure_cost, 2),
            'appraisal_cost': round(appraisal_cost, 2),
            'prevention_cost': round(prevention_cost, 2),
            'total_copq': round(total_copq, 2),
            'current_defect_rate': round(current_defect_rate * 100, 2),
            'potential_savings_six_sigma': round(potential_savings, 2),
            'roi_six_sigma': round((potential_savings / prevention_cost - 1) * 100, 1) if prevention_cost > 0 else 0
        }
    
    def store_control_chart_data(self, chart_data: Dict[str, Any]):
        """Store control chart data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store X-bar chart data points
        if 'xbar_chart' in chart_data:
            xbar = chart_data['xbar_chart']
            for i, value in enumerate(xbar['values']):
                cursor.execute('''
                INSERT INTO spc_data 
                (process_name, measurement_value, ucl, lcl, center_line, violation_type, special_cause)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (f"{chart_data['process_name']}_XBAR", value, xbar['ucl'], xbar['lcl'], 
                      xbar['center_line'], 'none', len(xbar['violations']) > 0))
        
        conn.commit()
        conn.close()
    
    def store_pareto_analysis(self, pareto_items: List[ParetoItem], analysis_type: str):
        """Store Pareto analysis results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in pareto_items:
            cursor.execute('''
            INSERT OR REPLACE INTO defect_analysis 
            (defect_category, frequency, cost_impact, status)
            VALUES (?, ?, ?, ?)
            ''', (item.category, item.frequency, item.cost_impact, 'analyzed'))
        
        conn.commit()
        conn.close()
    
    def generate_six_sigma_report(self) -> Dict[str, Any]:
        """Generate comprehensive Six Sigma quality report"""
        
        # Create control charts for key processes
        m5_bos_chart = self.create_xbar_r_chart("M5_BOS_DETECTION")
        m1_retest_chart = self.create_xbar_r_chart("M1_RETEST_VALIDATION")
        
        # Perform Pareto analysis
        defect_pareto = self.perform_pareto_analysis('defects')
        error_pareto = self.perform_pareto_analysis('errors')
        
        # Identify vital few
        vital_few_defects = self.identify_vital_few(defect_pareto)
        
        # Create QFD matrix
        qfd_matrix = self.create_qfd_matrix()
        
        # Calculate COPQ
        copq = self.calculate_cost_of_poor_quality()
        
        # Overall quality metrics
        overall_cpk = 0.0
        if m5_bos_chart and m1_retest_chart:
            cpk_values = [
                m5_bos_chart.get('process_capability', {}).get('cpk', 0),
                m1_retest_chart.get('process_capability', {}).get('cpk', 0)
            ]
            overall_cpk = np.mean([cpk for cpk in cpk_values if cpk > 0])
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'report_type': 'Six Sigma Quality Analysis',
            'target_cpk': self.target_cpk,
            'current_cpk': round(overall_cpk, 3),
            'target_achieved': overall_cpk >= self.target_cpk,
            'control_charts': {
                'm5_bos_detection': m5_bos_chart,
                'm1_retest_validation': m1_retest_chart
            },
            'pareto_analysis': {
                'defects': defect_pareto[:5],  # Top 5
                'vital_few': vital_few_defects
            },
            'qfd_analysis': qfd_matrix,
            'cost_of_poor_quality': copq,
            'recommendations': self.generate_action_plan(vital_few_defects, qfd_matrix, overall_cpk)
        }
        
        return report
    
    def generate_action_plan(self, vital_few: Dict[str, Any], qfd: Dict[str, Any], 
                           current_cpk: float) -> List[Dict[str, str]]:
        """Generate action plan to reach Cp/Cpk = 3.0"""
        actions = []
        
        # Actions based on Cpk gap
        cpk_gap = self.target_cpk - current_cpk
        
        if cpk_gap > 1.0:
            actions.append({
                'priority': 'critical',
                'action': 'Implement systematic process improvement (DMAIC)',
                'timeline': '4 weeks',
                'expected_impact': f'Improve Cpk by {cpk_gap/2:.1f}'
            })
        
        # Actions from vital few
        if 'vital_few' in vital_few:
            for item in vital_few['vital_few'][:3]:
                actions.append({
                    'priority': 'high',
                    'action': f'Address {item.category} (represents {item.percentage}% of defects)',
                    'timeline': '2 weeks',
                    'expected_impact': f'Reduce defects by {item.percentage}%'
                })
        
        # Actions from QFD top priorities
        if 'top_3_priorities' in qfd:
            for priority in qfd['top_3_priorities'][:2]:
                actions.append({
                    'priority': 'medium',
                    'action': f'Improve {priority["characteristic"]}',
                    'timeline': '3 weeks',
                    'expected_impact': f'Increase performance by {priority["improvement_needed"]:.1f} points'
                })
        
        # Above Robust! culture action
        actions.append({
            'priority': 'ongoing',
            'action': 'Establish Above Robust! culture with continuous monitoring',
            'timeline': 'continuous',
            'expected_impact': 'Sustain Six Sigma quality levels'
        })
        
        return actions

def main():
    """Main function for Six Sigma Quality Engine"""
    ascii_print("SIX SIGMA QUALITY ENGINE")
    ascii_print("Above Robust! Excellence")
    ascii_print("=" * 40)
    
    engine = SixSigmaQualityEngine()
    
    # Generate comprehensive Six Sigma report
    ascii_print("Generating Six Sigma quality report...")
    report = engine.generate_six_sigma_report()
    
    # Save report
    report_file = f"six_sigma_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    write_ascii_json(report_file, report)
    
    ascii_print(f"Six Sigma report generated: {report_file}")
    ascii_print(f"Current Cp/Cpk: {report['current_cpk']:.3f}")
    ascii_print(f"Target achieved: {'YES' if report['target_achieved'] else 'NO'}")
    
    # Display key recommendations
    ascii_print("\nKEY RECOMMENDATIONS:")
    for i, action in enumerate(report['recommendations'][:3], 1):
        ascii_print(f"{i}. {action['action']} ({action['priority']})")

if __name__ == "__main__":
    main()