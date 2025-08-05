"""
PARETO ANALYSIS FRAMEWORK
Nested 80/20 Analysis for Root Cause Identification in Mikrobot Trading System

This module implements comprehensive Pareto analysis with nested drilling
to identify the critical 4% root causes generating 64% of quality issues.

Owner: LeanSixSigmaMasterBlackBelt Agent
Target: Systematic identification of vital few causes for maximum impact
"""

import numpy as np
import sqlite3
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict, Counter
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FailureSeverity(Enum):
    """Failure severity levels for risk-based prioritization"""
    CRITICAL = 5  # System failure, trading stopped
    HIGH = 4      # Significant impact on performance
    MEDIUM = 3    # Moderate impact, degraded performance
    LOW = 2       # Minor impact, still functional
    MINIMAL = 1   # Negligible impact

class FailureCategory(Enum):
    """Primary failure categories based on trading system analysis"""
    EXECUTION_FAILURES = "execution_failures"
    SIGNAL_FAILURES = "signal_failures"
    CONNECTION_ISSUES = "connection_issues"
    TIMING_ISSUES = "timing_issues"
    DATA_QUALITY_ISSUES = "data_quality"
    RISK_MANAGEMENT_FAILURES = "risk_management"
    PLATFORM_ISSUES = "platform_issues"

@dataclass
class FailureEvent:
    """Individual failure event data structure"""
    timestamp: datetime
    category: str
    subcategory: str
    failure_type: str
    description: str
    severity: int
    impact_score: float
    cost_estimate: float
    symbol: Optional[str] = None
    phase: Optional[str] = None
    recovery_time_minutes: Optional[int] = None
    root_cause: Optional[str] = None
    
@dataclass
class ParetoItem:
    """Pareto analysis item with frequency and impact data"""
    name: str
    count: int
    percentage: float
    cumulative_percentage: float
    impact_score: float
    cost_of_poor_quality: float
    severity_weighted_count: float
    is_vital_few: bool
    rank: int
    
@dataclass
class ParetoAnalysisResult:
    """Complete Pareto analysis results"""
    analysis_timestamp: datetime
    analysis_period_hours: int
    total_failures: int
    pareto_items: List[ParetoItem]
    vital_few_threshold: float
    vital_few_items: List[ParetoItem]
    trivial_many_items: List[ParetoItem]
    level: int  # Pareto drilling level (1, 2, 3)
    parent_category: Optional[str] = None

class NestedParetoAnalyzer:
    """Advanced Pareto analyzer with nested drilling capability"""
    
    def __init__(self, db_path: str = "ml_observation_system.db"):
        self.db_path = db_path
        self.failure_events = []
        self.pareto_thresholds = {
            1: 0.80,   # Level 1: 80% (traditional Pareto)
            2: 0.64,   # Level 2: 64% (80% of 80%)
            3: 0.512   # Level 3: 51.2% (80% of 64%)
        }
        self._init_database()
        
    def _init_database(self):
        """Initialize database connection"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pareto_analysis'")
                if not cursor.fetchone():
                    logger.warning("Pareto analysis tables not found. Please run the database schema script first.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def collect_failure_data(self, hours_back: int = 24) -> List[FailureEvent]:
        """Collect failure data from multiple sources"""
        failure_events = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Collect from SPC violations
                spc_failures = self._collect_spc_violations(conn, hours_back)
                failure_events.extend(spc_failures)
                
                # Collect from MT5 journal data
                journal_failures = self._collect_journal_failures(conn, hours_back)
                failure_events.extend(journal_failures)
                
                # Collect from expert advisor data
                ea_failures = self._collect_ea_failures(conn, hours_back)
                failure_events.extend(ea_failures)
                
                # Collect from early warning alerts
                alert_failures = self._collect_alert_failures(conn, hours_back)
                failure_events.extend(alert_failures)
                
        except Exception as e:
            logger.error(f"Error collecting failure data: {e}")
            
        self.failure_events = failure_events
        logger.info(f"Collected {len(failure_events)} failure events from last {hours_back} hours")
        return failure_events
    
    def _collect_spc_violations(self, conn: sqlite3.Connection, hours_back: int) -> List[FailureEvent]:
        """Collect failures from SPC violations"""
        failures = []
        
        query = """
        SELECT detection_timestamp, metric_name, violation_type, violation_description,
               severity_level, data_point_value, phase_name, symbol
        FROM spc_violations 
        WHERE detection_timestamp >= datetime('now', '-{} hours')
        """.format(hours_back)
        
        try:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                failures.append(FailureEvent(
                    timestamp=datetime.fromisoformat(row[0]),
                    category=FailureCategory.SIGNAL_FAILURES.value,
                    subcategory="spc_violation",
                    failure_type=row[2],  # violation_type
                    description=row[3],   # violation_description
                    severity=row[4],      # severity_level
                    impact_score=self._calculate_spc_impact(row[4], row[5]),
                    cost_estimate=self._estimate_spc_violation_cost(row[4]),
                    symbol=row[7],
                    phase=row[6]
                ))
        except Exception as e:
            logger.error(f"Error collecting SPC violations: {e}")
            
        return failures
    
    def _collect_journal_failures(self, conn: sqlite3.Connection, hours_back: int) -> List[FailureEvent]:
        """Collect failures from MT5 journal data"""
        failures = []
        
        query = """
        SELECT event_timestamp, event_type, event_category, severity_level, 
               message, symbol, raw_data
        FROM mt5_journal_data 
        WHERE event_timestamp >= datetime('now', '-{} hours')
        AND event_category IN ('ERROR', 'WARNING')
        """.format(hours_back)
        
        try:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                category = self._classify_journal_failure(row[1], row[4])  # event_type, message
                
                failures.append(FailureEvent(
                    timestamp=datetime.fromisoformat(row[0]),
                    category=category,
                    subcategory=row[1],  # event_type
                    failure_type=row[2],  # event_category
                    description=row[4],   # message
                    severity=row[3],      # severity_level
                    impact_score=self._calculate_journal_impact(row[3]),
                    cost_estimate=self._estimate_journal_cost(row[3], category),
                    symbol=row[5]
                ))
        except Exception as e:
            logger.error(f"Error collecting journal failures: {e}")
            
        return failures
    
    def _collect_ea_failures(self, conn: sqlite3.Connection, hours_back: int) -> List[FailureEvent]:
        """Collect failures from Expert Advisor data"""
        failures = []
        
        query = """
        SELECT event_timestamp, expert_name, event_type, symbol, 
               execution_time_ms, success_flag, error_code, error_message
        FROM mt5_expert_data 
        WHERE event_timestamp >= datetime('now', '-{} hours')
        AND (success_flag = 0 OR event_type = 'ERROR')
        """.format(hours_back)
        
        try:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                failures.append(FailureEvent(
                    timestamp=datetime.fromisoformat(row[0]),
                    category=FailureCategory.EXECUTION_FAILURES.value,
                    subcategory="ea_failure",
                    failure_type=row[2],  # event_type
                    description=row[7] or f"EA execution failed: {row[6]}",  # error_message or error_code
                    severity=self._determine_ea_severity(row[6], row[4]),  # error_code, execution_time
                    impact_score=self._calculate_ea_impact(row[4], row[5]),  # execution_time, success_flag
                    cost_estimate=self._estimate_ea_failure_cost(row[6]),
                    symbol=row[3]
                ))
        except Exception as e:
            logger.error(f"Error collecting EA failures: {e}")
            
        return failures
    
    def _collect_alert_failures(self, conn: sqlite3.Connection, hours_back: int) -> List[FailureEvent]:
        """Collect failures from early warning alerts"""
        failures = []
        
        query = """
        SELECT alert_timestamp, alert_type, severity_level, metric_name,
               current_value, threshold_value, deviation_magnitude, phase_name, symbol
        FROM early_warning_alerts 
        WHERE alert_timestamp >= datetime('now', '-{} hours')
        """.format(hours_back)
        
        try:
            cursor = conn.execute(query)
            for row in cursor.fetchall():
                failures.append(FailureEvent(
                    timestamp=datetime.fromisoformat(row[0]),
                    category=self._classify_alert_failure(row[1]),  # alert_type
                    subcategory="early_warning",
                    failure_type=row[1],  # alert_type
                    description=f"Alert: {row[3]} = {row[4]}, threshold = {row[5]}",
                    severity=row[2],      # severity_level
                    impact_score=self._calculate_alert_impact(row[6], row[2]),  # deviation, severity
                    cost_estimate=self._estimate_alert_cost(row[2]),
                    symbol=row[8],
                    phase=row[7]
                ))
        except Exception as e:
            logger.error(f"Error collecting alert failures: {e}")
            
        return failures
    
    def perform_nested_pareto_analysis(self, hours_back: int = 24, max_levels: int = 3) -> Dict[str, ParetoAnalysisResult]:
        """Perform comprehensive nested Pareto analysis"""
        # Collect failure data
        failure_events = self.collect_failure_data(hours_back)
        
        if not failure_events:
            logger.warning("No failure events found for Pareto analysis")
            return {}
        
        results = {}
        
        # Level 1: Primary category analysis (80/20)
        level1_result = self._perform_pareto_analysis(
            failure_events, 
            grouping_field='category',
            level=1,
            threshold=self.pareto_thresholds[1]
        )
        results['level_1_categories'] = level1_result
        
        # Level 2: Subcategory analysis for vital few categories (64/16)
        if max_levels >= 2:
            for vital_item in level1_result.vital_few_items:
                category_failures = [f for f in failure_events if f.category == vital_item.name]
                if category_failures:
                    level2_result = self._perform_pareto_analysis(
                        category_failures,
                        grouping_field='subcategory',
                        level=2,
                        threshold=self.pareto_thresholds[2],
                        parent_category=vital_item.name
                    )
                    results[f'level_2_{vital_item.name}'] = level2_result
        
        # Level 3: Failure type analysis for vital few subcategories (51.2/12.8)
        if max_levels >= 3:
            for key, level2_result in results.items():
                if key.startswith('level_2_'):
                    parent_category = key.replace('level_2_', '')
                    for vital_subitem in level2_result.vital_few_items:
                        subcat_failures = [f for f in failure_events 
                                         if f.category == parent_category and f.subcategory == vital_subitem.name]
                        if subcat_failures:
                            level3_result = self._perform_pareto_analysis(
                                subcat_failures,
                                grouping_field='failure_type',
                                level=3,
                                threshold=self.pareto_thresholds[3],
                                parent_category=f"{parent_category}_{vital_subitem.name}"
                            )
                            results[f'level_3_{parent_category}_{vital_subitem.name}'] = level3_result
        
        # Store results in database
        self._store_pareto_results(results, hours_back)
        
        return results
    
    def _perform_pareto_analysis(self, failure_events: List[FailureEvent], grouping_field: str,
                                level: int, threshold: float, parent_category: Optional[str] = None) -> ParetoAnalysisResult:
        """Perform Pareto analysis on failure events"""
        
        # Group failures by specified field
        failure_groups = defaultdict(list)
        for failure in failure_events:
            key = getattr(failure, grouping_field)
            failure_groups[key].append(failure)
        
        # Calculate metrics for each group
        pareto_items = []
        total_failures = len(failure_events)
        total_impact = sum(f.impact_score for f in failure_events)
        total_cost = sum(f.cost_estimate for f in failure_events)
        
        for group_name, group_failures in failure_groups.items():
            count = len(group_failures)
            percentage = (count / total_failures) * 100 if total_failures > 0 else 0
            impact_score = sum(f.impact_score for f in group_failures)
            cost_of_poor_quality = sum(f.cost_estimate for f in group_failures)
            
            # Severity-weighted count for better prioritization
            severity_weighted_count = sum(f.severity * f.impact_score for f in group_failures)
            
            pareto_items.append(ParetoItem(
                name=group_name,
                count=count,
                percentage=percentage,
                cumulative_percentage=0,  # Will be calculated after sorting
                impact_score=impact_score,
                cost_of_poor_quality=cost_of_poor_quality,
                severity_weighted_count=severity_weighted_count,
                is_vital_few=False,  # Will be determined after sorting
                rank=0  # Will be assigned after sorting
            ))
        
        # Sort by severity-weighted count (descending)
        pareto_items.sort(key=lambda x: x.severity_weighted_count, reverse=True)
        
        # Calculate cumulative percentages and determine vital few
        cumulative_percentage = 0
        vital_few_items = []
        trivial_many_items = []
        
        for i, item in enumerate(pareto_items):
            item.rank = i + 1
            cumulative_percentage += item.percentage
            item.cumulative_percentage = cumulative_percentage
            
            if cumulative_percentage <= threshold * 100:
                item.is_vital_few = True
                vital_few_items.append(item)
            else:
                trivial_many_items.append(item)
        
        return ParetoAnalysisResult(
            analysis_timestamp=datetime.utcnow(),
            analysis_period_hours=24,  # Default to 24 hours
            total_failures=total_failures,
            pareto_items=pareto_items,
            vital_few_threshold=threshold,
            vital_few_items=vital_few_items,
            trivial_many_items=trivial_many_items,
            level=level,
            parent_category=parent_category
        )
    
    def generate_root_cause_analysis(self, pareto_results: Dict[str, ParetoAnalysisResult]) -> Dict[str, Any]:
        """Generate comprehensive root cause analysis from nested Pareto results"""
        
        root_cause_analysis = {
            'analysis_timestamp': datetime.utcnow(),
            'critical_root_causes': [],
            'improvement_priorities': [],
            'cost_impact_analysis': {},
            'recommended_actions': []
        }
        
        # Identify critical root causes (Level 3 vital few)
        level3_results = {k: v for k, v in pareto_results.items() if k.startswith('level_3_')}
        
        for key, result in level3_results.items():
            for vital_item in result.vital_few_items:
                root_cause_analysis['critical_root_causes'].append({
                    'root_cause': vital_item.name,
                    'category_path': key.replace('level_3_', '').replace('_', ' → '),
                    'failure_count': vital_item.count,
                    'impact_percentage': vital_item.percentage,
                    'cumulative_impact': vital_item.cumulative_percentage,
                    'severity_score': vital_item.severity_weighted_count,
                    'cost_of_poor_quality': vital_item.cost_of_poor_quality,
                    'priority_rank': vital_item.rank
                })
        
        # Sort by severity score for prioritization
        root_cause_analysis['critical_root_causes'].sort(
            key=lambda x: x['severity_score'], reverse=True
        )
        
        # Generate improvement priorities
        total_copq = sum(item['cost_of_poor_quality'] for item in root_cause_analysis['critical_root_causes'])
        
        for i, cause in enumerate(root_cause_analysis['critical_root_causes'][:10]):  # Top 10
            improvement_impact = (cause['cost_of_poor_quality'] / total_copq) * 100 if total_copq > 0 else 0
            
            root_cause_analysis['improvement_priorities'].append({
                'priority_rank': i + 1,
                'root_cause': cause['root_cause'],
                'improvement_impact_percentage': improvement_impact,
                'estimated_savings': cause['cost_of_poor_quality'] * 0.8,  # Assume 80% reduction
                'implementation_difficulty': self._assess_implementation_difficulty(cause['root_cause']),
                'roi_score': self._calculate_roi_score(cause['cost_of_poor_quality'], cause['root_cause'])
            })
        
        # Cost impact analysis
        root_cause_analysis['cost_impact_analysis'] = {
            'total_cost_of_poor_quality': total_copq,
            'top_10_causes_cost': sum(c['cost_of_poor_quality'] for c in root_cause_analysis['critical_root_causes'][:10]),
            'potential_annual_savings': total_copq * 0.8 * 52,  # Weekly * 52 weeks * 80% reduction
            'roi_if_top_5_fixed': self._calculate_top_5_roi(root_cause_analysis['critical_root_causes'][:5])
        }
        
        # Generate recommended actions
        root_cause_analysis['recommended_actions'] = self._generate_action_recommendations(
            root_cause_analysis['critical_root_causes'][:5]
        )
        
        return root_cause_analysis
    
    def _calculate_spc_impact(self, severity: int, value: float) -> float:
        """Calculate impact score for SPC violations"""
        base_impact = severity * 10  # Base impact from severity
        value_impact = abs(value) * 0.1 if value else 0  # Additional impact from deviation
        return base_impact + value_impact
    
    def _estimate_spc_violation_cost(self, severity: int) -> float:
        """Estimate cost of SPC violations"""
        cost_matrix = {
            5: 500.0,   # Critical - $500
            4: 200.0,   # High - $200
            3: 100.0,   # Medium - $100
            2: 50.0,    # Low - $50
            1: 20.0     # Minimal - $20
        }
        return cost_matrix.get(severity, 100.0)
    
    def _classify_journal_failure(self, event_type: str, message: str) -> str:
        """Classify journal failures by category"""
        message_lower = message.lower() if message else ""
        
        if any(word in message_lower for word in ['connection', 'disconnect', 'network', 'server']):
            return FailureCategory.CONNECTION_ISSUES.value
        elif any(word in message_lower for word in ['execution', 'order', 'trade', 'position']):
            return FailureCategory.EXECUTION_FAILURES.value
        elif any(word in message_lower for word in ['data', 'price', 'tick', 'quote']):
            return FailureCategory.DATA_QUALITY_ISSUES.value
        elif any(word in message_lower for word in ['timeout', 'delay', 'slow']):
            return FailureCategory.TIMING_ISSUES.value
        else:
            return FailureCategory.PLATFORM_ISSUES.value
    
    def _calculate_journal_impact(self, severity: int) -> float:
        """Calculate impact score for journal events"""
        return severity * 15  # Journal events have higher base impact
    
    def _estimate_journal_cost(self, severity: int, category: str) -> float:
        """Estimate cost of journal failures"""
        base_cost = {
            5: 800.0,   # Critical
            4: 400.0,   # High
            3: 200.0,   # Medium
            2: 100.0,   # Low
            1: 50.0     # Minimal
        }.get(severity, 200.0)
        
        # Category multiplier
        category_multiplier = {
            FailureCategory.EXECUTION_FAILURES.value: 2.0,
            FailureCategory.CONNECTION_ISSUES.value: 1.5,
            FailureCategory.DATA_QUALITY_ISSUES.value: 1.3,
            FailureCategory.TIMING_ISSUES.value: 1.2,
            FailureCategory.PLATFORM_ISSUES.value: 1.0
        }.get(category, 1.0)
        
        return base_cost * category_multiplier
    
    def _determine_ea_severity(self, error_code: int, execution_time: int) -> int:
        """Determine EA failure severity"""
        if error_code in [1, 2, 3, 4]:  # Critical errors
            return 5
        elif error_code in [130, 131, 132, 133]:  # Trade errors
            return 4
        elif execution_time and execution_time > 5000:  # > 5 seconds
            return 3
        else:
            return 2
    
    def _calculate_ea_impact(self, execution_time: int, success_flag: bool) -> float:
        """Calculate EA failure impact"""
        base_impact = 0 if success_flag else 50
        time_impact = (execution_time / 1000) * 5 if execution_time else 0  # 5 points per second
        return base_impact + time_impact
    
    def _estimate_ea_failure_cost(self, error_code: int) -> float:
        """Estimate EA failure cost"""
        cost_matrix = {
            1: 1000.0,    # No error (but failed)
            2: 1200.0,    # Common error
            3: 800.0,     # Invalid trade request
            4: 1500.0,    # Trade server busy
            130: 2000.0,  # Invalid stops
            131: 1800.0,  # Invalid trade volume
            132: 1600.0,  # Market closed
            133: 1400.0,  # Trade disabled
        }
        return cost_matrix.get(error_code, 500.0)
    
    def _classify_alert_failure(self, alert_type: str) -> str:
        """Classify alert failures by category"""
        alert_classification = {
            'CAPABILITY_DECLINE': FailureCategory.SIGNAL_FAILURES.value,
            'TREND_REVERSAL': FailureCategory.SIGNAL_FAILURES.value,
            'THRESHOLD_BREACH': FailureCategory.EXECUTION_FAILURES.value,
            'ANOMALY_DETECTED': FailureCategory.DATA_QUALITY_ISSUES.value
        }
        return alert_classification.get(alert_type, FailureCategory.PLATFORM_ISSUES.value)
    
    def _calculate_alert_impact(self, deviation_magnitude: float, severity: int) -> float:
        """Calculate alert failure impact"""
        deviation_impact = deviation_magnitude * 20 if deviation_magnitude else 0
        severity_impact = severity * 10
        return deviation_impact + severity_impact
    
    def _estimate_alert_cost(self, severity: int) -> float:
        """Estimate alert failure cost"""
        return {
            5: 600.0,   # Critical alert
            4: 300.0,   # High alert
            3: 150.0,   # Medium alert
            2: 75.0,    # Low alert
            1: 25.0     # Minimal alert
        }.get(severity, 150.0)
    
    def _assess_implementation_difficulty(self, root_cause: str) -> str:
        """Assess implementation difficulty for fixing root cause"""
        # Simple heuristic based on root cause type
        if any(word in root_cause.lower() for word in ['connection', 'network', 'server']):
            return 'HIGH'
        elif any(word in root_cause.lower() for word in ['configuration', 'setting', 'parameter']):
            return 'LOW'
        elif any(word in root_cause.lower() for word in ['algorithm', 'logic', 'calculation']):
            return 'MEDIUM'
        else:
            return 'MEDIUM'
    
    def _calculate_roi_score(self, cost_saving: float, root_cause: str) -> float:
        """Calculate ROI score for fixing root cause"""
        difficulty_cost = {
            'LOW': 1000.0,
            'MEDIUM': 5000.0,
            'HIGH': 15000.0
        }
        
        difficulty = self._assess_implementation_difficulty(root_cause)
        implementation_cost = difficulty_cost.get(difficulty, 5000.0)
        
        # ROI = (Annual Savings - Implementation Cost) / Implementation Cost
        annual_savings = cost_saving * 52  # Weekly to annual
        roi = (annual_savings - implementation_cost) / implementation_cost if implementation_cost > 0 else 0
        
        return max(roi, 0)  # Return 0 if negative ROI
    
    def _calculate_top_5_roi(self, top_5_causes: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate ROI if top 5 causes are fixed"""
        total_weekly_savings = sum(cause['cost_of_poor_quality'] for cause in top_5_causes) * 0.8
        total_annual_savings = total_weekly_savings * 52
        
        # Estimate implementation cost
        total_implementation_cost = sum(
            {'LOW': 1000, 'MEDIUM': 5000, 'HIGH': 15000}.get(
                self._assess_implementation_difficulty(cause['root_cause']), 5000
            ) for cause in top_5_causes
        )
        
        roi = (total_annual_savings - total_implementation_cost) / total_implementation_cost
        payback_months = total_implementation_cost / (total_weekly_savings * 4.33)  # 4.33 weeks per month
        
        return {
            'total_annual_savings': total_annual_savings,
            'total_implementation_cost': total_implementation_cost,
            'roi_percentage': roi * 100,
            'payback_period_months': payback_months
        }
    
    def _generate_action_recommendations(self, top_causes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific action recommendations for top causes"""
        recommendations = []
        
        for cause in top_causes:
            root_cause = cause['root_cause'].lower()
            
            if 'connection' in root_cause or 'disconnect' in root_cause:
                recommendations.append({
                    'root_cause': cause['root_cause'],
                    'primary_action': 'Implement redundant connection monitoring with automatic failover',
                    'secondary_actions': [
                        'Add connection health checks every 30 seconds',
                        'Implement exponential backoff for reconnection attempts',
                        'Set up multiple broker connections for redundancy'
                    ],
                    'success_metrics': ['Connection uptime >99.5%', 'Reconnection time <10 seconds'],
                    'implementation_timeline': '2-3 weeks',
                    'estimated_effort': 'Medium'
                })
            elif 'execution' in root_cause or 'order' in root_cause:
                recommendations.append({
                    'root_cause': cause['root_cause'],
                    'primary_action': 'Optimize order execution pipeline with pre-validation',
                    'secondary_actions': [
                        'Add order validation before submission',
                        'Implement execution timeout handling',
                        'Add order status monitoring and retry logic'
                    ],
                    'success_metrics': ['Execution success rate >99%', 'Average execution time <100ms'],
                    'implementation_timeline': '3-4 weeks',
                    'estimated_effort': 'High'
                })
            elif 'signal' in root_cause or 'detection' in root_cause:
                recommendations.append({
                    'root_cause': cause['root_cause'],
                    'primary_action': 'Enhance signal validation with multi-timeframe confirmation',
                    'secondary_actions': [
                        'Add signal strength scoring',
                        'Implement signal quality filters',
                        'Add backtesting validation for new signals'
                    ],
                    'success_metrics': ['Signal accuracy >95%', 'False positive rate <5%'],
                    'implementation_timeline': '4-5 weeks',
                    'estimated_effort': 'High'
                })
            elif 'data' in root_cause or 'price' in root_cause:
                recommendations.append({
                    'root_cause': cause['root_cause'],
                    'primary_action': 'Implement real-time data quality monitoring',
                    'secondary_actions': [
                        'Add tick data validation rules',
                        'Implement data source redundancy',
                        'Add automated data quality alerts'
                    ],
                    'success_metrics': ['Data accuracy >99.9%', 'Data latency <50ms'],
                    'implementation_timeline': '2-3 weeks',
                    'estimated_effort': 'Medium'
                })
            else:
                recommendations.append({
                    'root_cause': cause['root_cause'],
                    'primary_action': 'Conduct detailed root cause analysis and implement specific fixes',
                    'secondary_actions': [
                        'Gather additional diagnostic data',
                        'Implement monitoring for this specific issue',
                        'Create automated alerts for early detection'
                    ],
                    'success_metrics': ['Issue recurrence rate <10%', 'Detection time <5 minutes'],
                    'implementation_timeline': '1-2 weeks',
                    'estimated_effort': 'Low-Medium'
                })
        
        return recommendations
    
    def _store_pareto_results(self, results: Dict[str, ParetoAnalysisResult], analysis_period: int):
        """Store Pareto analysis results in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for key, result in results.items():
                    for item in result.pareto_items:
                        conn.execute("""
                            INSERT INTO pareto_analysis 
                            (analysis_timestamp, analysis_period_hours, pareto_level, failure_category, 
                             failure_count, failure_percentage, cumulative_percentage, pareto_rank, 
                             is_vital_few, impact_score, cost_of_poor_quality, recommended_actions)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            result.analysis_timestamp,
                            analysis_period,
                            result.level,
                            item.name,
                            item.count,
                            item.percentage,
                            item.cumulative_percentage,
                            item.rank,
                            item.is_vital_few,
                            item.impact_score,
                            item.cost_of_poor_quality,
                            json.dumps([])  # Placeholder for recommended actions
                        ))
                        
        except Exception as e:
            logger.error(f"Error storing Pareto results: {e}")
    
    def generate_pareto_report(self, results: Dict[str, ParetoAnalysisResult]) -> Dict[str, Any]:
        """Generate comprehensive Pareto analysis report"""
        report = {
            'executive_summary': {},
            'detailed_analysis': {},
            'cost_benefit_analysis': {},
            'implementation_roadmap': {},
            'monitoring_recommendations': {}
        }
        
        # Executive Summary
        level1_result = results.get('level_1_categories')
        if level1_result:
            vital_few_categories = len(level1_result.vital_few_items)
            total_categories = len(level1_result.pareto_items)
            vital_few_impact = sum(item.percentage for item in level1_result.vital_few_items)
            
            report['executive_summary'] = {
                'total_failure_events': level1_result.total_failures,
                'analysis_period_hours': level1_result.analysis_period_hours,
                'vital_few_categories': vital_few_categories,
                'total_categories': total_categories,
                'vital_few_impact_percentage': vital_few_impact,
                'pareto_efficiency': f"{vital_few_categories}/{total_categories} categories cause {vital_few_impact:.1f}% of issues",
                'top_failure_category': level1_result.pareto_items[0].name if level1_result.pareto_items else None,
                'total_cost_of_poor_quality': sum(item.cost_of_poor_quality for item in level1_result.pareto_items)
            }
        
        # Detailed Analysis
        report['detailed_analysis'] = {
            'level_1_breakdown': self._format_pareto_level(results.get('level_1_categories')),
            'level_2_breakdown': {},
            'level_3_breakdown': {}
        }
        
        # Add level 2 and 3 breakdowns
        for key, result in results.items():
            if key.startswith('level_2_'):
                category = key.replace('level_2_', '')
                report['detailed_analysis']['level_2_breakdown'][category] = self._format_pareto_level(result)
            elif key.startswith('level_3_'):
                path = key.replace('level_3_', '')
                report['detailed_analysis']['level_3_breakdown'][path] = self._format_pareto_level(result)
        
        # Generate root cause analysis
        root_cause_analysis = self.generate_root_cause_analysis(results)
        report['cost_benefit_analysis'] = root_cause_analysis['cost_impact_analysis']
        report['implementation_roadmap'] = root_cause_analysis['recommended_actions']
        
        # Monitoring Recommendations
        report['monitoring_recommendations'] = {
            'critical_metrics_to_watch': self._identify_critical_metrics(results),
            'alert_thresholds': self._recommend_alert_thresholds(results),
            'review_frequency': self._recommend_review_frequency(results),
            'escalation_procedures': self._create_escalation_procedures(results)
        }
        
        return report
    
    def _format_pareto_level(self, result: Optional[ParetoAnalysisResult]) -> Dict[str, Any]:
        """Format Pareto analysis result for reporting"""
        if not result:
            return {}
            
        return {
            'total_failures': result.total_failures,
            'vital_few_count': len(result.vital_few_items),
            'vital_few_items': [
                {
                    'name': item.name,
                    'count': item.count,
                    'percentage': item.percentage,
                    'cumulative_percentage': item.cumulative_percentage,
                    'cost_of_poor_quality': item.cost_of_poor_quality,
                    'rank': item.rank
                } for item in result.vital_few_items
            ],
            'trivial_many_count': len(result.trivial_many_items),
            'analysis_timestamp': result.analysis_timestamp
        }
    
    def _identify_critical_metrics(self, results: Dict[str, ParetoAnalysisResult]) -> List[str]:
        """Identify critical metrics to monitor based on Pareto analysis"""
        critical_metrics = set()
        
        # Add metrics from vital few items across all levels
        for result in results.values():
            for item in result.vital_few_items:
                if 'latency' in item.name.lower():
                    critical_metrics.add('execution_latency_ms')
                    critical_metrics.add('detection_latency_ms')
                elif 'accuracy' in item.name.lower():
                    critical_metrics.add('signal_accuracy')
                    critical_metrics.add('detection_accuracy')
                elif 'connection' in item.name.lower():
                    critical_metrics.add('connection_uptime')
                    critical_metrics.add('connection_stability')
                elif 'execution' in item.name.lower():
                    critical_metrics.add('execution_success_rate')
                    critical_metrics.add('order_fill_rate')
        
        return list(critical_metrics)
    
    def _recommend_alert_thresholds(self, results: Dict[str, ParetoAnalysisResult]) -> Dict[str, Dict[str, float]]:
        """Recommend alert thresholds based on failure patterns"""
        return {
            'execution_latency_ms': {'warning': 100, 'critical': 200},
            'detection_accuracy': {'warning': 0.90, 'critical': 0.85},
            'connection_uptime': {'warning': 0.995, 'critical': 0.990},
            'signal_accuracy': {'warning': 0.92, 'critical': 0.88},
            'execution_success_rate': {'warning': 0.95, 'critical': 0.90}
        }
    
    def _recommend_review_frequency(self, results: Dict[str, ParetoAnalysisResult]) -> Dict[str, str]:
        """Recommend review frequency for different aspects"""
        level1_result = results.get('level_1_categories')
        if not level1_result:
            return {}
            
        failure_rate = level1_result.total_failures / level1_result.analysis_period_hours
        
        if failure_rate > 10:  # >10 failures per hour
            return {
                'pareto_analysis': 'Daily',
                'root_cause_review': 'Weekly',
                'improvement_progress': 'Bi-weekly',
                'threshold_adjustment': 'Monthly'
            }
        elif failure_rate > 5:  # 5-10 failures per hour
            return {
                'pareto_analysis': 'Weekly',
                'root_cause_review': 'Bi-weekly',
                'improvement_progress': 'Monthly',
                'threshold_adjustment': 'Quarterly'
            }
        else:  # <5 failures per hour
            return {
                'pareto_analysis': 'Bi-weekly',
                'root_cause_review': 'Monthly',
                'improvement_progress': 'Quarterly',
                'threshold_adjustment': 'Semi-annually'
            }
    
    def _create_escalation_procedures(self, results: Dict[str, ParetoAnalysisResult]) -> List[Dict[str, Any]]:
        """Create escalation procedures based on failure patterns"""
        return [
            {
                'trigger': 'Critical failure (severity 5) occurs',
                'immediate_action': 'Stop trading immediately',
                'notification': 'Alert system administrator within 5 minutes',
                'investigation_timeline': '1 hour',
                'resolution_timeline': '4 hours'
            },
            {
                'trigger': 'High failure rate (>20 failures/hour)',
                'immediate_action': 'Enable safe mode trading',
                'notification': 'Alert operations team within 15 minutes',
                'investigation_timeline': '2 hours',
                'resolution_timeline': '8 hours'
            },
            {
                'trigger': 'Vital few category shows increasing trend',
                'immediate_action': 'Increase monitoring frequency',
                'notification': 'Alert quality team within 1 hour',
                'investigation_timeline': '1 day',
                'resolution_timeline': '1 week'
            }
        ]

# Example usage and testing
if __name__ == "__main__":
    # Initialize the Pareto analyzer
    analyzer = NestedParetoAnalyzer()
    
    # Perform nested Pareto analysis
    print("Performing nested Pareto analysis...")
    results = analyzer.perform_nested_pareto_analysis(hours_back=24, max_levels=3)
    
    # Generate comprehensive report
    print("Generating Pareto analysis report...")
    report = analyzer.generate_pareto_report(results)
    
    # Display results
    print("\n=== PARETO ANALYSIS RESULTS ===")
    print(json.dumps(report['executive_summary'], indent=2, default=str))
    
    print("\n=== ROOT CAUSE ANALYSIS ===")
    root_cause_analysis = analyzer.generate_root_cause_analysis(results)
    print(json.dumps(root_cause_analysis['critical_root_causes'][:5], indent=2, default=str))
    
    print("\n=== IMPLEMENTATION PRIORITIES ===")
    print(json.dumps(root_cause_analysis['improvement_priorities'][:3], indent=2, default=str))