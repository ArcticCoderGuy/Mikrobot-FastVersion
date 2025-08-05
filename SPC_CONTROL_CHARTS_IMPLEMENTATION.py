"""
SPC CONTROL CHARTS IMPLEMENTATION
Six Sigma Quality Control for Mikrobot Trading System

This module implements comprehensive Statistical Process Control charts
for all four trading phases to achieve Cp/Cpk 3.0+ quality levels.

Owner: LeanSixSigmaMasterBlackBelt Agent
Target: Six Sigma Quality Achievement (3.4 defects per million)
"""

import numpy as np
import sqlite3
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from collections import deque
from enum import Enum
import warnings
import logging

# Configure logging for quality monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """Western Electric Rules for control chart violations"""
    RULE_1 = "Single point beyond 3-sigma control limits"
    RULE_2 = "Nine consecutive points on same side of centerline" 
    RULE_3 = "Six consecutive points steadily increasing or decreasing"
    RULE_4 = "Fourteen consecutive points alternating up and down"
    RULE_5 = "Two out of three consecutive points beyond 2-sigma limits"
    RULE_6 = "Four out of five consecutive points beyond 1-sigma limits"
    RULE_7 = "Fifteen consecutive points within 1-sigma of centerline"
    RULE_8 = "Eight consecutive points beyond 1-sigma from centerline"

@dataclass
class ControlLimits:
    """Control limits structure for SPC charts"""
    center_line: float
    upper_control_limit: float
    lower_control_limit: float
    upper_warning_limit: Optional[float] = None
    lower_warning_limit: Optional[float] = None
    calculation_method: str = "3_SIGMA"
    sample_size: int = 1
    
@dataclass
class ViolationResult:
    """Structure for control chart violations"""
    violation_type: ViolationType
    point_index: int
    value: float
    severity: int  # 1-5 scale
    description: str
    recommended_action: str

class BaseControlChart:
    """Base class for all control charts with common functionality"""
    
    def __init__(self, metric_name: str, sample_size: int = 1):
        self.metric_name = metric_name
        self.sample_size = sample_size
        self.data_points = deque(maxlen=1000)  # Store last 1000 points
        self.control_limits = None
        self.violations = []
        self.last_update = None
        
    def add_data_point(self, value: float, timestamp: datetime = None) -> Dict[str, Any]:
        """Add new data point and check for violations"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        self.data_points.append({
            'value': value,
            'timestamp': timestamp,
            'index': len(self.data_points)
        })
        
        # Update control limits if we have enough data
        if len(self.data_points) >= 25:  # Minimum for reliable limits
            self.update_control_limits()
            
        # Check for violations
        violations = self.check_violations()
        
        self.last_update = timestamp
        
        return {
            'value': value,
            'timestamp': timestamp,
            'control_limits': self.control_limits.__dict__ if self.control_limits else None,
            'violations': [v.__dict__ for v in violations],
            'in_control': len(violations) == 0
        }
    
    def update_control_limits(self):
        """Update control limits - implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement update_control_limits")
    
    def check_violations(self) -> List[ViolationResult]:
        """Check for Western Electric rule violations"""
        if not self.control_limits or len(self.data_points) < 9:
            return []
            
        violations = []
        values = [dp['value'] for dp in list(self.data_points)[-50:]]  # Check last 50 points
        
        # Rule 1: Single point beyond control limits
        violations.extend(self._check_rule_1(values))
        
        # Rule 2: Nine consecutive points on same side
        violations.extend(self._check_rule_2(values))
        
        # Rule 3: Six consecutive trending points
        violations.extend(self._check_rule_3(values))
        
        # Rule 4: Fourteen alternating points
        violations.extend(self._check_rule_4(values))
        
        # Rule 5: Two of three beyond 2-sigma
        violations.extend(self._check_rule_5(values))
        
        # Rule 6: Four of five beyond 1-sigma
        violations.extend(self._check_rule_6(values))
        
        # Rule 7: Fifteen within 1-sigma
        violations.extend(self._check_rule_7(values))
        
        # Rule 8: Eight beyond 1-sigma from centerline
        violations.extend(self._check_rule_8(values))
        
        return violations
    
    def _check_rule_1(self, values: List[float]) -> List[ViolationResult]:
        """Rule 1: Single point beyond 3-sigma control limits"""
        violations = []
        ucl = self.control_limits.upper_control_limit
        lcl = self.control_limits.lower_control_limit
        
        for i, value in enumerate(values):
            if value > ucl or value < lcl:
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_1,
                    point_index=len(self.data_points) - len(values) + i,
                    value=value,
                    severity=5,  # Critical
                    description=f"Point {value:.3f} beyond control limits [{lcl:.3f}, {ucl:.3f}]",
                    recommended_action="IMMEDIATE_INVESTIGATION_REQUIRED"
                ))
        return violations
    
    def _check_rule_2(self, values: List[float]) -> List[ViolationResult]:
        """Rule 2: Nine consecutive points on same side of centerline"""
        violations = []
        cl = self.control_limits.center_line
        
        consecutive_count = 0
        last_side = None
        
        for i, value in enumerate(values):
            current_side = 'above' if value > cl else 'below'
            
            if current_side == last_side:
                consecutive_count += 1
            else:
                consecutive_count = 1
                last_side = current_side
                
            if consecutive_count >= 9:
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_2,
                    point_index=len(self.data_points) - len(values) + i,
                    value=value,
                    severity=4,  # High
                    description=f"Nine consecutive points {current_side} centerline",
                    recommended_action="PROCESS_SHIFT_INVESTIGATION"
                ))
                
        return violations
    
    def _check_rule_3(self, values: List[float]) -> List[ViolationResult]:
        """Rule 3: Six consecutive points steadily increasing or decreasing"""
        violations = []
        
        if len(values) < 6:
            return violations
            
        for i in range(len(values) - 5):
            sequence = values[i:i+6]
            
            # Check for increasing trend
            if all(sequence[j] < sequence[j+1] for j in range(5)):
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_3,
                    point_index=len(self.data_points) - len(values) + i + 5,
                    value=sequence[-1],
                    severity=3,  # Medium
                    description="Six consecutive increasing points detected",
                    recommended_action="TREND_ANALYSIS_REQUIRED"
                ))
                
            # Check for decreasing trend
            if all(sequence[j] > sequence[j+1] for j in range(5)):
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_3,
                    point_index=len(self.data_points) - len(values) + i + 5,
                    value=sequence[-1],
                    severity=3,  # Medium
                    description="Six consecutive decreasing points detected",
                    recommended_action="TREND_ANALYSIS_REQUIRED"
                ))
                
        return violations
    
    def _check_rule_4(self, values: List[float]) -> List[ViolationResult]:
        """Rule 4: Fourteen consecutive points alternating up and down"""
        violations = []
        
        if len(values) < 14:
            return violations
            
        for i in range(len(values) - 13):
            sequence = values[i:i+14]
            alternating = True
            
            for j in range(1, 13):
                if j % 2 == 1:  # Odd index - should alternate
                    if not ((sequence[j-1] < sequence[j] and sequence[j] > sequence[j+1]) or
                           (sequence[j-1] > sequence[j] and sequence[j] < sequence[j+1])):
                        alternating = False
                        break
                        
            if alternating:
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_4,
                    point_index=len(self.data_points) - len(values) + i + 13,
                    value=sequence[-1],
                    severity=2,  # Low-Medium
                    description="Fourteen consecutive alternating points detected",
                    recommended_action="SYSTEMATIC_VARIATION_INVESTIGATION"
                ))
                
        return violations
    
    def _check_rule_5(self, values: List[float]) -> List[ViolationResult]:
        """Rule 5: Two out of three consecutive points beyond 2-sigma limits"""
        violations = []
        cl = self.control_limits.center_line
        ucl = self.control_limits.upper_control_limit
        lcl = self.control_limits.lower_control_limit
        
        # Calculate 2-sigma limits
        two_sigma_upper = cl + 2 * (ucl - cl) / 3
        two_sigma_lower = cl - 2 * (cl - lcl) / 3
        
        for i in range(len(values) - 2):
            three_points = values[i:i+3]
            beyond_count = sum(1 for v in three_points if v > two_sigma_upper or v < two_sigma_lower)
            
            if beyond_count >= 2:
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_5,
                    point_index=len(self.data_points) - len(values) + i + 2,
                    value=three_points[-1],
                    severity=3,  # Medium
                    description="Two of three consecutive points beyond 2-sigma limits",
                    recommended_action="PROCESS_CAPABILITY_REVIEW"
                ))
                
        return violations
    
    def _check_rule_6(self, values: List[float]) -> List[ViolationResult]:
        """Rule 6: Four out of five consecutive points beyond 1-sigma limits"""
        violations = []
        cl = self.control_limits.center_line
        ucl = self.control_limits.upper_control_limit
        lcl = self.control_limits.lower_control_limit
        
        # Calculate 1-sigma limits
        one_sigma_upper = cl + (ucl - cl) / 3
        one_sigma_lower = cl - (cl - lcl) / 3
        
        for i in range(len(values) - 4):
            five_points = values[i:i+5]
            beyond_count = sum(1 for v in five_points if v > one_sigma_upper or v < one_sigma_lower)
            
            if beyond_count >= 4:
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_6,
                    point_index=len(self.data_points) - len(values) + i + 4,
                    value=five_points[-1],
                    severity=3,  # Medium
                    description="Four of five consecutive points beyond 1-sigma limits",
                    recommended_action="PROCESS_VARIATION_ANALYSIS"
                ))
                
        return violations
    
    def _check_rule_7(self, values: List[float]) -> List[ViolationResult]:
        """Rule 7: Fifteen consecutive points within 1-sigma of centerline"""
        violations = []
        cl = self.control_limits.center_line
        ucl = self.control_limits.upper_control_limit
        lcl = self.control_limits.lower_control_limit
        
        # Calculate 1-sigma limits
        one_sigma_upper = cl + (ucl - cl) / 3
        one_sigma_lower = cl - (cl - lcl) / 3
        
        for i in range(len(values) - 14):
            fifteen_points = values[i:i+15]
            within_count = sum(1 for v in fifteen_points if one_sigma_lower <= v <= one_sigma_upper)
            
            if within_count == 15:
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_7,
                    point_index=len(self.data_points) - len(values) + i + 14,
                    value=fifteen_points[-1],
                    severity=2,  # Low-Medium
                    description="Fifteen consecutive points within 1-sigma (possible over-control)",
                    recommended_action="OVER_CONTROL_INVESTIGATION"
                ))
                
        return violations
    
    def _check_rule_8(self, values: List[float]) -> List[ViolationResult]:
        """Rule 8: Eight consecutive points beyond 1-sigma from centerline"""
        violations = []
        cl = self.control_limits.center_line
        ucl = self.control_limits.upper_control_limit
        lcl = self.control_limits.lower_control_limit
        
        # Calculate 1-sigma limits
        one_sigma_upper = cl + (ucl - cl) / 3
        one_sigma_lower = cl - (cl - lcl) / 3
        
        for i in range(len(values) - 7):
            eight_points = values[i:i+8]
            all_beyond = all(v > one_sigma_upper or v < one_sigma_lower for v in eight_points)
            
            if all_beyond:
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_8,
                    point_index=len(self.data_points) - len(values) + i + 7,
                    value=eight_points[-1],
                    severity=3,  # Medium
                    description="Eight consecutive points beyond 1-sigma from centerline",
                    recommended_action="PROCESS_CENTERING_ADJUSTMENT"
                ))
                
        return violations

class XBarRChart(BaseControlChart):
    """X-bar and R Chart for continuous data with subgroups"""
    
    def __init__(self, metric_name: str, sample_size: int = 5):
        super().__init__(metric_name, sample_size)
        self.subgroups = deque(maxlen=200)  # Store subgroups for R chart
        self.x_bar_values = deque(maxlen=200)
        self.r_values = deque(maxlen=200)
        
        # Constants for control chart calculations
        self.constants = {
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
    
    def add_subgroup(self, values: List[float], timestamp: datetime = None) -> Dict[str, Any]:
        """Add a subgroup of values and calculate X-bar and R"""
        if len(values) != self.sample_size:
            raise ValueError(f"Subgroup size must be {self.sample_size}, got {len(values)}")
            
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        x_bar = np.mean(values)
        r_value = np.max(values) - np.min(values)
        
        self.subgroups.append({
            'values': values,
            'x_bar': x_bar,
            'r_value': r_value,
            'timestamp': timestamp
        })
        
        self.x_bar_values.append(x_bar)
        self.r_values.append(r_value)
        
        # Update control limits
        if len(self.subgroups) >= 25:
            self.update_control_limits()
            
        # Check violations for both X-bar and R charts
        x_bar_violations = self._check_x_bar_violations()
        r_violations = self._check_r_violations()
        
        return {
            'x_bar': x_bar,
            'r_value': r_value,
            'timestamp': timestamp,
            'x_bar_control_limits': self.x_bar_limits.__dict__ if hasattr(self, 'x_bar_limits') else None,
            'r_control_limits': self.r_limits.__dict__ if hasattr(self, 'r_limits') else None,
            'x_bar_violations': [v.__dict__ for v in x_bar_violations],
            'r_violations': [v.__dict__ for v in r_violations],
            'in_control': len(x_bar_violations) == 0 and len(r_violations) == 0
        }
    
    def update_control_limits(self):
        """Calculate control limits for X-bar and R charts"""
        if len(self.subgroups) < 25:
            return
            
        constants = self.constants.get(self.sample_size, self.constants[5])
        A2, D3, D4 = constants['A2'], constants['D3'], constants['D4']
        
        x_double_bar = np.mean(list(self.x_bar_values))
        r_bar = np.mean(list(self.r_values))
        
        # X-bar chart limits
        self.x_bar_limits = ControlLimits(
            center_line=x_double_bar,
            upper_control_limit=x_double_bar + A2 * r_bar,
            lower_control_limit=x_double_bar - A2 * r_bar,
            sample_size=self.sample_size,
            calculation_method="XBAR_R_METHOD"
        )
        
        # R chart limits
        self.r_limits = ControlLimits(
            center_line=r_bar,
            upper_control_limit=D4 * r_bar,
            lower_control_limit=D3 * r_bar,
            sample_size=self.sample_size,
            calculation_method="XBAR_R_METHOD"
        )
        
        # Set the main control limits to X-bar limits for violation checking
        self.control_limits = self.x_bar_limits
    
    def _check_x_bar_violations(self) -> List[ViolationResult]:
        """Check violations for X-bar chart"""
        if not hasattr(self, 'x_bar_limits') or len(self.x_bar_values) < 9:
            return []
            
        # Temporarily set control limits to X-bar limits for violation checking
        original_limits = self.control_limits
        self.control_limits = self.x_bar_limits
        
        values = list(self.x_bar_values)[-50:]  # Last 50 X-bar values
        violations = []
        
        # Check all Western Electric rules for X-bar chart
        violations.extend(self._check_rule_1(values))
        violations.extend(self._check_rule_2(values))
        violations.extend(self._check_rule_3(values))
        violations.extend(self._check_rule_4(values))
        violations.extend(self._check_rule_5(values))
        violations.extend(self._check_rule_6(values))
        violations.extend(self._check_rule_7(values))
        violations.extend(self._check_rule_8(values))
        
        # Restore original limits
        self.control_limits = original_limits
        
        return violations
    
    def _check_r_violations(self) -> List[ViolationResult]:
        """Check violations for R chart"""
        if not hasattr(self, 'r_limits') or len(self.r_values) < 9:
            return []
            
        violations = []
        r_values = list(self.r_values)[-50:]  # Last 50 R values
        ucl = self.r_limits.upper_control_limit
        lcl = self.r_limits.lower_control_limit
        
        # Rule 1 for R chart (most critical for range charts)
        for i, r_value in enumerate(r_values):
            if r_value > ucl or r_value < lcl:
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_1,
                    point_index=len(self.r_values) - len(r_values) + i,
                    value=r_value,
                    severity=5,  # Critical
                    description=f"R-chart point {r_value:.3f} beyond control limits [{lcl:.3f}, {ucl:.3f}]",
                    recommended_action="PROCESS_VARIATION_INVESTIGATION"
                ))
                
        return violations

class PChart(BaseControlChart):
    """p-Chart for proportion of defective items"""
    
    def __init__(self, metric_name: str, target_sample_size: int = 100):
        super().__init__(metric_name, 1)
        self.target_sample_size = target_sample_size
        self.sample_data = deque(maxlen=200)
        
    def add_sample(self, total_items: int, defective_items: int, timestamp: datetime = None) -> Dict[str, Any]:
        """Add sample data for p-chart"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        proportion = defective_items / total_items if total_items > 0 else 0
        
        sample = {
            'total_items': total_items,
            'defective_items': defective_items,
            'proportion': proportion,
            'timestamp': timestamp
        }
        
        self.sample_data.append(sample)
        
        # Update control limits
        if len(self.sample_data) >= 25:
            self.update_control_limits()
            
        # Check violations
        violations = self._check_p_violations()
        
        return {
            'proportion': proportion,
            'total_items': total_items,
            'defective_items': defective_items,
            'timestamp': timestamp,
            'control_limits': self._get_variable_control_limits(total_items) if self.control_limits else None,
            'violations': [v.__dict__ for v in violations],
            'in_control': len(violations) == 0
        }
    
    def update_control_limits(self):
        """Calculate control limits for p-chart"""
        if len(self.sample_data) < 25:
            return
            
        # Calculate p-bar (average proportion)
        total_defective = sum(s['defective_items'] for s in self.sample_data)
        total_items = sum(s['total_items'] for s in self.sample_data)
        p_bar = total_defective / total_items if total_items > 0 else 0
        
        # Use target sample size for standard control limits
        n = self.target_sample_size
        std_error = np.sqrt(p_bar * (1 - p_bar) / n)
        
        self.control_limits = ControlLimits(
            center_line=p_bar,
            upper_control_limit=p_bar + 3 * std_error,
            lower_control_limit=max(0, p_bar - 3 * std_error),
            sample_size=n,
            calculation_method="P_CHART_METHOD"
        )
    
    def _get_variable_control_limits(self, sample_size: int) -> Dict[str, float]:
        """Get control limits for specific sample size"""
        if not self.control_limits:
            return None
            
        p_bar = self.control_limits.center_line
        std_error = np.sqrt(p_bar * (1 - p_bar) / sample_size)
        
        return {
            'center_line': p_bar,
            'upper_control_limit': p_bar + 3 * std_error,
            'lower_control_limit': max(0, p_bar - 3 * std_error),
            'sample_size': sample_size
        }
    
    def _check_p_violations(self) -> List[ViolationResult]:
        """Check violations for p-chart with variable sample sizes"""
        if not self.control_limits or len(self.sample_data) < 9:
            return []
            
        violations = []
        recent_samples = list(self.sample_data)[-50:]  # Last 50 samples
        
        for i, sample in enumerate(recent_samples):
            limits = self._get_variable_control_limits(sample['total_items'])
            proportion = sample['proportion']
            
            # Rule 1: Beyond control limits
            if proportion > limits['upper_control_limit'] or proportion < limits['lower_control_limit']:
                violations.append(ViolationResult(
                    violation_type=ViolationType.RULE_1,
                    point_index=len(self.sample_data) - len(recent_samples) + i,
                    value=proportion,
                    severity=5,  # Critical
                    description=f"Proportion {proportion:.3f} beyond control limits [{limits['lower_control_limit']:.3f}, {limits['upper_control_limit']:.3f}]",
                    recommended_action="PROCESS_INVESTIGATION_REQUIRED"
                ))
                
        return violations

class CUSUMChart(BaseControlChart):
    """CUSUM Chart for detecting small shifts in process mean"""
    
    def __init__(self, metric_name: str, target_mean: float = None, k_factor: float = 0.5, h_factor: float = 5.0):
        super().__init__(metric_name, 1)
        self.target_mean = target_mean
        self.k_factor = k_factor  # Reference value (typically 0.5 * sigma)
        self.h_factor = h_factor  # Decision interval (typically 4-5 * sigma)
        self.cusum_high = deque(maxlen=1000)
        self.cusum_low = deque(maxlen=1000)
        self.process_std = None
        
    def add_value(self, value: float, timestamp: datetime = None) -> Dict[str, Any]:
        """Add value to CUSUM chart"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        # Calculate process parameters if not available
        if self.target_mean is None or self.process_std is None:
            self._update_process_parameters()
            
        if self.target_mean is None:
            # Not enough data yet
            self.data_points.append({
                'value': value,
                'timestamp': timestamp,
                'index': len(self.data_points)
            })
            return {
                'value': value,
                'timestamp': timestamp,
                'cusum_high': 0,
                'cusum_low': 0,
                'violations': [],
                'in_control': True
            }
        
        # Calculate CUSUM values
        k = self.k_factor * self.process_std
        
        # Initialize if first point
        if len(self.cusum_high) == 0:
            cusum_h = max(0, value - self.target_mean - k)
            cusum_l = max(0, self.target_mean - value - k)
        else:
            cusum_h = max(0, self.cusum_high[-1] + value - self.target_mean - k)
            cusum_l = max(0, self.cusum_low[-1] + self.target_mean - value - k)
        
        self.cusum_high.append(cusum_h)
        self.cusum_low.append(cusum_l)
        
        self.data_points.append({
            'value': value,
            'timestamp': timestamp,
            'index': len(self.data_points),
            'cusum_high': cusum_h,
            'cusum_low': cusum_l
        })
        
        # Check for violations
        violations = self._check_cusum_violations(cusum_h, cusum_l)
        
        return {
            'value': value,
            'timestamp': timestamp,
            'cusum_high': cusum_h,
            'cusum_low': cusum_l,
            'decision_interval': self.h_factor * self.process_std,
            'violations': [v.__dict__ for v in violations],
            'in_control': len(violations) == 0
        }
    
    def _update_process_parameters(self):
        """Update target mean and standard deviation"""
        if len(self.data_points) < 25:
            return
            
        values = [dp['value'] for dp in self.data_points]
        self.target_mean = np.mean(values)
        self.process_std = np.std(values, ddof=1)
    
    def _check_cusum_violations(self, cusum_h: float, cusum_l: float) -> List[ViolationResult]:
        """Check for CUSUM violations"""
        violations = []
        h_limit = self.h_factor * self.process_std
        
        if cusum_h > h_limit:
            violations.append(ViolationResult(
                violation_type=ViolationType.RULE_1,  # Using Rule 1 for CUSUM
                point_index=len(self.data_points) - 1,
                value=cusum_h,
                severity=4,  # High
                description=f"CUSUM High {cusum_h:.3f} exceeds decision interval {h_limit:.3f}",
                recommended_action="UPWARD_SHIFT_INVESTIGATION"
            ))
            
        if cusum_l > h_limit:
            violations.append(ViolationResult(
                violation_type=ViolationType.RULE_1,  # Using Rule 1 for CUSUM
                point_index=len(self.data_points) - 1,
                value=cusum_l,
                severity=4,  # High
                description=f"CUSUM Low {cusum_l:.3f} exceeds decision interval {h_limit:.3f}",
                recommended_action="DOWNWARD_SHIFT_INVESTIGATION"
            ))
            
        return violations

class EWMAChart(BaseControlChart):
    """EWMA Chart for detecting small shifts with exponential weighting"""
    
    def __init__(self, metric_name: str, lambda_factor: float = 0.2, target_mean: float = None):
        super().__init__(metric_name, 1)
        self.lambda_factor = lambda_factor
        self.target_mean = target_mean
        self.ewma_values = deque(maxlen=1000)
        self.process_std = None
        
    def add_value(self, value: float, timestamp: datetime = None) -> Dict[str, Any]:
        """Add value to EWMA chart"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        # Calculate process parameters if not available
        if self.target_mean is None or self.process_std is None:
            self._update_process_parameters()
            
        if self.target_mean is None:
            # Not enough data yet
            self.data_points.append({
                'value': value,
                'timestamp': timestamp,
                'index': len(self.data_points)
            })
            return {
                'value': value,
                'timestamp': timestamp,
                'ewma_value': value,
                'violations': [],
                'in_control': True
            }
        
        # Calculate EWMA value
        if len(self.ewma_values) == 0:
            ewma_value = self.target_mean  # Initialize with target
        else:
            ewma_value = self.lambda_factor * value + (1 - self.lambda_factor) * self.ewma_values[-1]
        
        self.ewma_values.append(ewma_value)
        
        self.data_points.append({
            'value': value,
            'timestamp': timestamp,
            'index': len(self.data_points),
            'ewma_value': ewma_value
        })
        
        # Update control limits
        self.update_control_limits()
        
        # Check violations
        violations = self._check_ewma_violations(ewma_value)
        
        return {
            'value': value,
            'timestamp': timestamp,
            'ewma_value': ewma_value,
            'control_limits': self.control_limits.__dict__ if self.control_limits else None,
            'violations': [v.__dict__ for v in violations],
            'in_control': len(violations) == 0
        }
    
    def update_control_limits(self):
        """Calculate EWMA control limits"""
        if self.target_mean is None or self.process_std is None:
            return
            
        # Number of samples
        n = len(self.ewma_values)
        if n == 0:
            return
            
        # EWMA standard deviation
        ewma_std = self.process_std * np.sqrt(self.lambda_factor * (1 - (1 - self.lambda_factor)**(2 * n)) / (2 - self.lambda_factor))
        
        self.control_limits = ControlLimits(
            center_line=self.target_mean,
            upper_control_limit=self.target_mean + 3 * ewma_std,
            lower_control_limit=self.target_mean - 3 * ewma_std,
            sample_size=1,
            calculation_method="EWMA_METHOD"
        )
    
    def _update_process_parameters(self):
        """Update target mean and standard deviation"""
        if len(self.data_points) < 25:
            return
            
        values = [dp['value'] for dp in self.data_points]
        self.target_mean = np.mean(values)
        self.process_std = np.std(values, ddof=1)
    
    def _check_ewma_violations(self, ewma_value: float) -> List[ViolationResult]:
        """Check for EWMA violations"""
        if not self.control_limits:
            return []
            
        violations = []
        ucl = self.control_limits.upper_control_limit
        lcl = self.control_limits.lower_control_limit
        
        if ewma_value > ucl or ewma_value < lcl:
            violations.append(ViolationResult(
                violation_type=ViolationType.RULE_1,
                point_index=len(self.data_points) - 1,
                value=ewma_value,
                severity=4,  # High
                description=f"EWMA value {ewma_value:.3f} beyond control limits [{lcl:.3f}, {ucl:.3f}]",
                recommended_action="PROCESS_SHIFT_INVESTIGATION"
            ))
            
        return violations

class TradingPhaseControlCharts:
    """Comprehensive control chart system for all four trading phases"""
    
    def __init__(self, db_path: str = "ml_observation_system.db"):
        self.db_path = db_path
        self.charts = self._initialize_charts()
        self._init_database()
        
    def _initialize_charts(self) -> Dict[str, BaseControlChart]:
        """Initialize all control charts for trading phases"""
        return {
            # M5 BOS Detection Phase
            'm5_bos_detection_accuracy': PChart('m5_bos_detection_accuracy', target_sample_size=50),
            'm5_bos_detection_latency': XBarRChart('m5_bos_detection_latency', sample_size=5),
            'm5_bos_false_positive_rate': PChart('m5_bos_false_positive_rate', target_sample_size=50),
            
            # M1 Break Identification Phase
            'm1_break_direction_alignment': PChart('m1_break_direction_alignment', target_sample_size=25),
            'm1_break_level_precision': XBarRChart('m1_break_level_precision', sample_size=5),
            'm1_break_recording_accuracy': PChart('m1_break_recording_accuracy', target_sample_size=25),
            
            # M1 Retest Validation Phase
            'm1_retest_quality_score': CUSUMChart('m1_retest_quality_score', k_factor=0.5, h_factor=5.0),
            'm1_retest_validation_time': XBarRChart('m1_retest_validation_time', sample_size=5),
            'm1_retest_bounce_confirmation': PChart('m1_retest_bounce_confirmation', target_sample_size=25),
            
            # YLIPIP Entry Trigger Phase
            'ylipip_calculation_accuracy': XBarRChart('ylipip_calculation_accuracy', sample_size=5),
            'ylipip_execution_latency': EWMAChart('ylipip_execution_latency', lambda_factor=0.2),
            'ylipip_trigger_precision': PChart('ylipip_trigger_precision', target_sample_size=25)
        }
    
    def _init_database(self):
        """Initialize database connection and tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check if tables exist
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spc_control_data'")
                if not cursor.fetchone():
                    logger.warning("SPC tables not found. Please run the database schema script first.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def update_m5_bos_metrics(self, detection_accuracy: float, detection_latency_values: List[float], 
                             false_positive_rate: float, total_detections: int, false_positives: int,
                             timestamp: datetime = None) -> Dict[str, Any]:
        """Update M5 BOS phase control charts"""
        results = {}
        
        try:
            # Detection accuracy (p-chart)
            results['detection_accuracy'] = self.charts['m5_bos_detection_accuracy'].add_sample(
                total_items=total_detections,
                defective_items=int(total_detections * (1 - detection_accuracy)),
                timestamp=timestamp
            )
            
            # Detection latency (X-bar R chart)
            if len(detection_latency_values) >= 5:
                results['detection_latency'] = self.charts['m5_bos_detection_latency'].add_subgroup(
                    values=detection_latency_values[:5],
                    timestamp=timestamp
                )
            
            # False positive rate (p-chart)
            results['false_positive_rate'] = self.charts['m5_bos_false_positive_rate'].add_sample(
                total_items=total_detections,
                defective_items=false_positives,
                timestamp=timestamp
            )
            
            # Store in database
            self._store_spc_data('M5_BOS_DETECTION', results, timestamp)
            
        except Exception as e:
            logger.error(f"Error updating M5 BOS metrics: {e}")
            
        return results
    
    def update_m1_break_metrics(self, direction_alignment_rate: float, level_precision_values: List[float],
                               recording_accuracy: float, total_breaks: int, alignment_failures: int,
                               recording_failures: int, timestamp: datetime = None) -> Dict[str, Any]:
        """Update M1 Break phase control charts"""
        results = {}
        
        try:
            # Direction alignment (p-chart)
            results['direction_alignment'] = self.charts['m1_break_direction_alignment'].add_sample(
                total_items=total_breaks,
                defective_items=alignment_failures,
                timestamp=timestamp
            )
            
            # Level precision (X-bar R chart)
            if len(level_precision_values) >= 5:
                results['level_precision'] = self.charts['m1_break_level_precision'].add_subgroup(
                    values=level_precision_values[:5],
                    timestamp=timestamp
                )
            
            # Recording accuracy (p-chart)
            results['recording_accuracy'] = self.charts['m1_break_recording_accuracy'].add_sample(
                total_items=total_breaks,
                defective_items=recording_failures,
                timestamp=timestamp
            )
            
            # Store in database
            self._store_spc_data('M1_BREAK_IDENTIFICATION', results, timestamp)
            
        except Exception as e:
            logger.error(f"Error updating M1 Break metrics: {e}")
            
        return results
    
    def update_m1_retest_metrics(self, quality_score: float, validation_time_values: List[float],
                                bounce_confirmation_rate: float, total_retests: int, 
                                bounce_failures: int, timestamp: datetime = None) -> Dict[str, Any]:
        """Update M1 Retest phase control charts"""
        results = {}
        
        try:
            # Quality score (CUSUM chart)
            results['quality_score'] = self.charts['m1_retest_quality_score'].add_value(
                value=quality_score,
                timestamp=timestamp
            )
            
            # Validation time (X-bar R chart)
            if len(validation_time_values) >= 5:
                results['validation_time'] = self.charts['m1_retest_validation_time'].add_subgroup(
                    values=validation_time_values[:5],
                    timestamp=timestamp
                )
            
            # Bounce confirmation (p-chart)
            results['bounce_confirmation'] = self.charts['m1_retest_bounce_confirmation'].add_sample(
                total_items=total_retests,
                defective_items=bounce_failures,
                timestamp=timestamp
            )
            
            # Store in database
            self._store_spc_data('M1_RETEST_VALIDATION', results, timestamp)
            
        except Exception as e:
            logger.error(f"Error updating M1 Retest metrics: {e}")
            
        return results
    
    def update_ylipip_metrics(self, calculation_accuracy_values: List[float], execution_latency: float,
                             trigger_precision_rate: float, total_triggers: int, precision_failures: int,
                             timestamp: datetime = None) -> Dict[str, Any]:
        """Update YLIPIP phase control charts"""
        results = {}
        
        try:
            # Calculation accuracy (X-bar R chart)
            if len(calculation_accuracy_values) >= 5:
                results['calculation_accuracy'] = self.charts['ylipip_calculation_accuracy'].add_subgroup(
                    values=calculation_accuracy_values[:5],
                    timestamp=timestamp
                )
            
            # Execution latency (EWMA chart)
            results['execution_latency'] = self.charts['ylipip_execution_latency'].add_value(
                value=execution_latency,
                timestamp=timestamp
            )
            
            # Trigger precision (p-chart)
            results['trigger_precision'] = self.charts['ylipip_trigger_precision'].add_sample(
                total_items=total_triggers,
                defective_items=precision_failures,
                timestamp=timestamp
            )
            
            # Store in database
            self._store_spc_data('YLIPIP_ENTRY_TRIGGER', results, timestamp)
            
        except Exception as e:
            logger.error(f"Error updating YLIPIP metrics: {e}")
            
        return results
    
    def _store_spc_data(self, phase_name: str, results: Dict[str, Any], timestamp: datetime):
        """Store SPC data in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for metric_name, result in results.items():
                    # Store control data
                    conn.execute("""
                        INSERT INTO spc_control_data 
                        (measurement_timestamp, metric_name, chart_type, sample_values, 
                         x_bar, r_value, p_value, cusum_value, ewma_value, phase_name, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        timestamp,
                        metric_name,
                        self._get_chart_type(metric_name),
                        json.dumps(result.get('values', [])),
                        result.get('x_bar'),
                        result.get('r_value'),
                        result.get('proportion'),
                        result.get('cusum_high'),
                        result.get('ewma_value'),
                        phase_name,
                        json.dumps(result)
                    ))
                    
                    # Store violations if any
                    violations = result.get('violations', [])
                    for violation in violations:
                        conn.execute("""
                            INSERT INTO spc_violations
                            (detection_timestamp, metric_name, chart_type, violation_type,
                             violation_description, severity_level, data_point_value, phase_name)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            timestamp,
                            metric_name,
                            self._get_chart_type(metric_name),
                            violation['violation_type'],
                            violation['description'],
                            violation['severity'],
                            violation['value'],
                            phase_name
                        ))
                        
        except Exception as e:
            logger.error(f"Error storing SPC data: {e}")
    
    def _get_chart_type(self, metric_name: str) -> str:
        """Get chart type for a metric"""
        chart = self.charts.get(metric_name)
        if isinstance(chart, XBarRChart):
            return 'XBAR_R'
        elif isinstance(chart, PChart):
            return 'P_CHART'
        elif isinstance(chart, CUSUMChart):
            return 'CUSUM'
        elif isinstance(chart, EWMAChart):
            return 'EWMA'
        else:
            return 'UNKNOWN'
    
    def get_overall_control_status(self) -> Dict[str, Any]:
        """Get overall control status for all charts"""
        total_charts = len(self.charts)
        in_control_count = 0
        active_violations = []
        
        for chart_name, chart in self.charts.items():
            if hasattr(chart, 'control_limits') and chart.control_limits:
                # Check if chart is in control (no recent violations)
                recent_violations = [v for v in chart.violations if 
                                   v.point_index >= len(chart.data_points) - 10]
                if not recent_violations:
                    in_control_count += 1
                else:
                    active_violations.extend(recent_violations)
        
        control_percentage = (in_control_count / total_charts) * 100 if total_charts > 0 else 0
        
        return {
            'total_charts': total_charts,
            'in_control_count': in_control_count,
            'control_percentage': control_percentage,
            'active_violations': len(active_violations),
            'violation_details': [v.__dict__ for v in active_violations[:10]],  # Top 10
            'overall_status': 'IN_CONTROL' if control_percentage >= 90 else 'OUT_OF_CONTROL',
            'last_update': datetime.utcnow()
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the trading phase control charts
    trading_charts = TradingPhaseControlCharts()
    
    # Example: Update M5 BOS metrics
    m5_results = trading_charts.update_m5_bos_metrics(
        detection_accuracy=0.92,
        detection_latency_values=[450, 520, 380, 490, 410],
        false_positive_rate=0.06,
        total_detections=100,
        false_positives=6
    )
    
    print("M5 BOS Results:")
    print(json.dumps(m5_results, indent=2, default=str))
    
    # Example: Update M1 Break metrics
    m1_break_results = trading_charts.update_m1_break_metrics(
        direction_alignment_rate=0.98,
        level_precision_values=[1.8, 2.1, 1.6, 2.0, 1.9],
        recording_accuracy=0.99,
        total_breaks=50,
        alignment_failures=1,
        recording_failures=0
    )
    
    print("\nM1 Break Results:")
    print(json.dumps(m1_break_results, indent=2, default=str))
    
    # Get overall control status
    control_status = trading_charts.get_overall_control_status()
    print("\nOverall Control Status:")
    print(json.dumps(control_status, indent=2, default=str))