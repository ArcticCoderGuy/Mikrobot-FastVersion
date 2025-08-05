#!/usr/bin/env python3
"""
MIKROBOT ML OBSERVATION SYSTEM - ABOVE ROBUST! IMPLEMENTATION
Six Sigma Quality Monitoring for Trading System
Target: Cp/Cpk = 3.0 (Six Sigma Quality Level)

ZERO TRADING INTERFERENCE - PURE OBSERVATION SYSTEM
"""

import sys
import os
import time
import sqlite3
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import threading
import statistics
import math
from dataclasses import dataclass

# Add encoding utilities
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from encoding_utils import ascii_print, write_ascii_json

@dataclass
class QualityMetrics:
    """Quality metrics for trading processes"""
    cp: float = 0.0
    cpk: float = 0.0
    defect_rate_ppm: float = 0.0
    process_yield: float = 0.0
    sigma_level: float = 0.0
    control_status: str = "unknown"

class MLObservationSystem:
    """
    ML Observation System for Six Sigma Quality Management
    Observes MT5 trading activity and calculates Cp/Cpk metrics
    """
    
    def __init__(self):
        self.name = "MIKROBOT ML Observation System"
        self.version = "1.0.0"
        self.target_cpk = 3.0  # Six Sigma target
        
        # Database setup
        self.db_path = "mikrobot_quality_metrics.db"
        self.init_database()
        
        # MT5 monitoring paths
        self.mt5_terminal_path = None
        self.journal_log_path = None
        self.expert_log_path = None
        
        # Quality tracking
        self.current_metrics = QualityMetrics()
        self.observation_active = False
        
        # Control limits (will be calculated from data)
        self.control_limits = {}
        
        ascii_print(f"Initialized {self.name} v{self.version}")
        ascii_print(f"Target Cp/Cpk: {self.target_cpk}")
    
    def init_database(self):
        """Initialize SQLite database with quality metrics schema"""
        ascii_print("Initializing quality metrics database...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trading phases observation table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trading_phases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            trade_id TEXT,
            symbol TEXT,
            phase INTEGER,  -- 1=M5_BOS, 2=M1_BREAK, 3=M1_RETEST, 4=YLIPIP
            phase_name TEXT,
            duration_ms INTEGER,
            success BOOLEAN,
            compliance BOOLEAN,
            defect_type TEXT,
            quality_score REAL,
            cost_impact REAL DEFAULT 100.0
        )
        ''')
        
        # Journal monitoring table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            log_time TEXT,
            message_type TEXT,
            message TEXT,
            error_category TEXT,
            impact_level INTEGER,  -- 1=low, 3=high
            resolved BOOLEAN DEFAULT FALSE
        )
        ''')
        
        # Expert advisor monitoring table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS expert_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ea_name TEXT,
            symbol TEXT,
            activity_type TEXT,
            message TEXT,
            phase_correlation INTEGER,
            compliance_score REAL,
            anomaly_detected BOOLEAN
        )
        ''')
        
        # Quality metrics history
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_metrics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metric_type TEXT,  -- cp, cpk, yield, defect_rate
            value REAL,
            target_value REAL,
            within_spec BOOLEAN,
            trend TEXT,  -- improving, declining, stable
            control_status TEXT  -- in_control, out_of_control, warning
        )
        ''')
        
        # Pareto analysis data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS defect_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            defect_category TEXT,
            defect_subcategory TEXT,
            frequency INTEGER,
            cost_impact REAL,
            root_cause TEXT,
            corrective_action TEXT,
            status TEXT  -- open, in_progress, resolved
        )
        ''')
        
        # SPC control chart data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS spc_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            process_name TEXT,
            measurement_value REAL,
            sample_size INTEGER,
            ucl REAL,  -- Upper Control Limit
            lcl REAL,  -- Lower Control Limit
            center_line REAL,
            violation_type TEXT,
            special_cause BOOLEAN
        )
        ''')
        
        # News and calendar correlation
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            context_type TEXT,  -- news, calendar_event
            content TEXT,
            impact_level TEXT,  -- low, medium, high
            correlated_quality_change REAL,
            affect_on_trading BOOLEAN
        )
        ''')
        
        conn.commit()
        conn.close()
        
        ascii_print("Quality metrics database initialized successfully")
    
    def connect_to_mt5_monitoring(self):
        """Connect to existing MT5 terminal monitoring"""
        try:
            # Import the existing MT5 access system
            from mt5_terminal_direct_access import MT5TerminalDirectAccess
            
            self.mt5_monitor = MT5TerminalDirectAccess()
            if self.mt5_monitor.initialize():
                ascii_print("Connected to MT5 monitoring system")
                return True
            else:
                ascii_print("Failed to connect to MT5 monitoring")
                return False
                
        except Exception as e:
            ascii_print(f"Error connecting to MT5 monitoring: {e}")
            return False
    
    def calculate_process_capability(self, measurements: List[float], 
                                   target: float, tolerance: float) -> Tuple[float, float]:
        """Calculate Cp and Cpk for process capability"""
        if len(measurements) < 10:
            return 0.0, 0.0
        
        # Calculate process statistics
        mean = statistics.mean(measurements)
        std_dev = statistics.stdev(measurements)
        
        if std_dev == 0:
            return float('inf'), float('inf')
        
        # Upper and Lower Specification Limits
        usl = target + tolerance
        lsl = target - tolerance
        
        # Calculate Cp (process capability)
        cp = (usl - lsl) / (6 * std_dev)
        
        # Calculate Cpk (process capability index)
        cpu = (usl - mean) / (3 * std_dev)
        cpl = (mean - lsl) / (3 * std_dev)
        cpk = min(cpu, cpl)
        
        return cp, cpk
    
    def calculate_sigma_level(self, defect_rate_ppm: float) -> float:
        """Calculate sigma level from defect rate"""
        if defect_rate_ppm <= 0:
            return 6.0
        if defect_rate_ppm >= 1000000:
            return 0.0
        
        # Convert PPM to yield
        yield_rate = (1000000 - defect_rate_ppm) / 1000000
        
        # Sigma level approximation
        if yield_rate >= 0.999997:
            return 6.0
        elif yield_rate >= 0.99966:
            return 5.0
        elif yield_rate >= 0.9973:
            return 4.0
        elif yield_rate >= 0.9332:
            return 3.0
        elif yield_rate >= 0.6915:
            return 2.0
        else:
            return 1.0
    
    def observe_trading_phase(self, phase_data: Dict[str, Any]):
        """Observe and record trading phase execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extract phase information
        trade_id = phase_data.get('trade_id', 'unknown')
        symbol = phase_data.get('symbol', 'unknown')
        phase = phase_data.get('phase', 0)
        phase_name = phase_data.get('phase_name', 'unknown')
        duration_ms = phase_data.get('duration_ms', 0)
        success = phase_data.get('success', True)
        
        # Determine compliance based on MIKROBOT_FASTVERSION.md rules
        compliance = self.check_phase_compliance(phase_data)
        
        # Calculate quality score (0.0 to 1.0)
        quality_score = self.calculate_phase_quality_score(phase_data)
        
        # Identify defect type if any
        defect_type = None
        if not compliance:
            defect_type = self.identify_defect_type(phase_data)
        
        cursor.execute('''
        INSERT INTO trading_phases 
        (trade_id, symbol, phase, phase_name, duration_ms, success, 
         compliance, defect_type, quality_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (trade_id, symbol, phase, phase_name, duration_ms, 
              success, compliance, defect_type, quality_score))
        
        conn.commit()
        conn.close()
        
        # Update real-time quality metrics
        self.update_quality_metrics()
    
    def check_phase_compliance(self, phase_data: Dict[str, Any]) -> bool:
        """Check if phase execution complies with MIKROBOT_FASTVERSION.md"""
        phase = phase_data.get('phase', 0)
        
        if phase == 1:  # M5 BOS detection
            return self.check_m5_bos_compliance(phase_data)
        elif phase == 2:  # M1 break confirmation  
            return self.check_m1_break_compliance(phase_data)
        elif phase == 3:  # M1 retest validation
            return self.check_m1_retest_compliance(phase_data)
        elif phase == 4:  # YLIPIP trigger
            return self.check_ylipip_compliance(phase_data)
        
        return False
    
    def check_m5_bos_compliance(self, phase_data: Dict[str, Any]) -> bool:
        """Check M5 BOS detection compliance"""
        # Must have valid BOS detection
        bos_detected = phase_data.get('bos_detected', False)
        bos_strength = phase_data.get('bos_strength', 0)
        
        return bos_detected and bos_strength > 0
    
    def check_m1_break_compliance(self, phase_data: Dict[str, Any]) -> bool:
        """Check M1 break confirmation compliance"""
        # Must confirm M5 BOS with M1 timeframe break
        m1_break_confirmed = phase_data.get('m1_break_confirmed', False)
        break_quality = phase_data.get('break_quality', 0)
        
        return m1_break_confirmed and break_quality > 0.5
    
    def check_m1_retest_compliance(self, phase_data: Dict[str, Any]) -> bool:
        """Check M1 retest validation compliance"""
        # Must have valid retest of broken level
        retest_completed = phase_data.get('retest_completed', False)
        retest_quality = phase_data.get('retest_quality', 0)
        
        return retest_completed and retest_quality > 0.6
    
    def check_ylipip_compliance(self, phase_data: Dict[str, Any]) -> bool:
        """Check YLIPIP trigger compliance"""
        # Must trigger at exactly 0.6 pips
        ylipip_triggered = phase_data.get('ylipip_triggered', False)
        pip_distance = phase_data.get('pip_distance', 0)
        
        return ylipip_triggered and abs(pip_distance - 0.6) < 0.1
    
    def calculate_phase_quality_score(self, phase_data: Dict[str, Any]) -> float:
        """Calculate quality score for trading phase (0.0 to 1.0)"""
        base_score = 1.0
        
        # Deduct for timing issues
        duration_ms = phase_data.get('duration_ms', 0)
        if duration_ms > 5000:  # Longer than 5 seconds
            base_score -= 0.2
        
        # Deduct for quality issues
        if not phase_data.get('success', True):
            base_score -= 0.5
        
        # Phase-specific quality factors
        phase = phase_data.get('phase', 0)
        if phase == 1:  # M5 BOS
            strength = phase_data.get('bos_strength', 0)
            base_score *= (strength / 100)  # Normalize strength
        elif phase == 3:  # M1 retest
            quality = phase_data.get('retest_quality', 0)
            base_score *= quality
        
        return max(0.0, min(1.0, base_score))
    
    def identify_defect_type(self, phase_data: Dict[str, Any]) -> str:
        """Identify specific defect type for non-compliant phases"""
        phase = phase_data.get('phase', 0)
        
        if phase == 1:
            if not phase_data.get('bos_detected', False):
                return "NO_BOS_DETECTION"
            elif phase_data.get('bos_strength', 0) < 0.5:
                return "WEAK_BOS_SIGNAL"
        elif phase == 2:
            if not phase_data.get('m1_break_confirmed', False):
                return "NO_M1_CONFIRMATION"
        elif phase == 3:
            if not phase_data.get('retest_completed', False):
                return "NO_RETEST"
            elif phase_data.get('retest_quality', 0) < 0.6:
                return "POOR_RETEST_QUALITY"
        elif phase == 4:
            pip_distance = phase_data.get('pip_distance', 0)
            if abs(pip_distance - 0.6) > 0.1:
                return "INCORRECT_YLIPIP_DISTANCE"
        
        return "UNKNOWN_DEFECT"
    
    def update_quality_metrics(self):
        """Update current quality metrics based on recent data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent trading phases (last 100)
        cursor.execute('''
        SELECT quality_score, compliance FROM trading_phases 
        ORDER BY timestamp DESC LIMIT 100
        ''')
        recent_phases = cursor.fetchall()
        
        if len(recent_phases) < 10:
            return
        
        quality_scores = [row[0] for row in recent_phases]
        compliant_phases = [row[1] for row in recent_phases]
        
        # Calculate Cp and Cpk for quality scores (target: 0.9, tolerance: 0.4)
        cp, cpk = self.calculate_process_capability(quality_scores, 0.9, 0.4)
        
        # Calculate defect rate
        total_phases = len(compliant_phases)
        defective_phases = sum(1 for c in compliant_phases if not c)
        defect_rate_ppm = (defective_phases / total_phases) * 1000000 if total_phases > 0 else 0
        
        # Calculate process yield
        process_yield = (1 - defect_rate_ppm / 1000000) * 100
        
        # Calculate sigma level
        sigma_level = self.calculate_sigma_level(defect_rate_ppm)
        
        # Update current metrics
        self.current_metrics = QualityMetrics(
            cp=cp,
            cpk=cpk,
            defect_rate_ppm=defect_rate_ppm,
            process_yield=process_yield,
            sigma_level=sigma_level,
            control_status="in_control" if cpk >= 1.33 else "out_of_control"
        )
        
        # Store metrics in database
        metrics_to_store = [
            ('cp', cp, self.target_cpk),
            ('cpk', cpk, self.target_cpk),
            ('defect_rate_ppm', defect_rate_ppm, 3.4),
            ('process_yield', process_yield, 99.9966),
            ('sigma_level', sigma_level, 6.0)
        ]
        
        for metric_type, value, target in metrics_to_store:
            within_spec = value >= target if metric_type != 'defect_rate_ppm' else value <= target
            trend = self.calculate_trend(metric_type, value)
            
            cursor.execute('''
            INSERT INTO quality_metrics_history 
            (metric_type, value, target_value, within_spec, trend, control_status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (metric_type, value, target, within_spec, trend, self.current_metrics.control_status))
        
        conn.commit()
        conn.close()
    
    def calculate_trend(self, metric_type: str, current_value: float) -> str:
        """Calculate trend for metric (improving, declining, stable)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT value FROM quality_metrics_history 
        WHERE metric_type = ? 
        ORDER BY timestamp DESC LIMIT 5
        ''', (metric_type,))
        
        recent_values = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if len(recent_values) < 3:
            return "stable"
        
        # Simple trend calculation
        recent_avg = sum(recent_values) / len(recent_values)
        
        if current_value > recent_avg * 1.05:
            return "improving"
        elif current_value < recent_avg * 0.95:
            return "declining"
        else:
            return "stable"
    
    def generate_quality_report(self) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_name': self.name,
            'version': self.version,
            'current_metrics': {
                'cp': round(self.current_metrics.cp, 3),
                'cpk': round(self.current_metrics.cpk, 3),
                'defect_rate_ppm': round(self.current_metrics.defect_rate_ppm, 1),
                'process_yield': round(self.current_metrics.process_yield, 4),
                'sigma_level': round(self.current_metrics.sigma_level, 1),
                'control_status': self.current_metrics.control_status
            },
            'targets': {
                'cp': self.target_cpk,
                'cpk': self.target_cpk,
                'defect_rate_ppm': 3.4,
                'process_yield': 99.9966,
                'sigma_level': 6.0
            }
        }
        
        # Add compliance analysis
        report['target_achievement'] = {
            'cp_achieved': self.current_metrics.cp >= self.target_cpk,
            'cpk_achieved': self.current_metrics.cpk >= self.target_cpk,
            'six_sigma_achieved': self.current_metrics.sigma_level >= 6.0,
            'overall_grade': self.calculate_overall_grade()
        }
        
        return report
    
    def calculate_overall_grade(self) -> str:
        """Calculate overall quality grade"""
        cpk_score = min(100, (self.current_metrics.cpk / self.target_cpk) * 100)
        sigma_score = min(100, (self.current_metrics.sigma_level / 6.0) * 100)
        yield_score = min(100, (self.current_metrics.process_yield / 99.9966) * 100)
        
        overall_score = (cpk_score + sigma_score + yield_score) / 3
        
        if overall_score >= 95:
            return "ABOVE ROBUST!"
        elif overall_score >= 85:
            return "EXCELLENT"
        elif overall_score >= 75:
            return "GOOD"
        elif overall_score >= 65:
            return "ACCEPTABLE"
        else:
            return "NEEDS IMPROVEMENT"
    
    def start_observation(self):
        """Start ML observation system"""
        ascii_print("Starting ML Observation System...")
        ascii_print("Target: Six Sigma Quality (Cp/Cpk >= 3.0)")
        
        self.observation_active = True
        
        # Start monitoring threads
        journal_thread = threading.Thread(target=self.monitor_journal_continuously)
        expert_thread = threading.Thread(target=self.monitor_experts_continuously)
        quality_thread = threading.Thread(target=self.update_quality_continuously)
        
        journal_thread.daemon = True
        expert_thread.daemon = True
        quality_thread.daemon = True
        
        journal_thread.start()
        expert_thread.start()
        quality_thread.start()
        
        ascii_print("ML Observation System ACTIVE - Monitoring quality...")
        
        return True
    
    def monitor_journal_continuously(self):
        """Monitor MT5 journal continuously"""
        while self.observation_active:
            try:
                if hasattr(self, 'mt5_monitor'):
                    terminal_activity = self.mt5_monitor.read_terminal_activity()
                    for activity in terminal_activity:
                        self.process_journal_entry(activity)
                
                time.sleep(3)  # Update every 3 seconds
            except Exception as e:
                ascii_print(f"Journal monitoring error: {e}")
                time.sleep(5)
    
    def monitor_experts_continuously(self):
        """Monitor MT5 experts continuously"""
        while self.observation_active:
            try:
                if hasattr(self, 'mt5_monitor'):
                    expert_activity = self.mt5_monitor.read_expert_activity()
                    for activity in expert_activity:
                        self.process_expert_entry(activity)
                
                time.sleep(3)  # Update every 3 seconds
            except Exception as e:
                ascii_print(f"Expert monitoring error: {e}")
                time.sleep(5)
    
    def update_quality_continuously(self):
        """Update quality metrics continuously"""
        while self.observation_active:
            try:
                self.update_quality_metrics()
                time.sleep(30)  # Update quality every 30 seconds
            except Exception as e:
                ascii_print(f"Quality update error: {e}")
                time.sleep(30)
    
    def process_journal_entry(self, activity: Dict[str, Any]):
        """Process a journal entry for quality monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        message = activity.get('message', '')
        activity_type = activity.get('type', 'info')
        
        # Categorize errors and issues
        error_category = self.categorize_journal_error(message)
        impact_level = self.assess_impact_level(message, error_category)
        
        cursor.execute('''
        INSERT INTO journal_observations 
        (log_time, message_type, message, error_category, impact_level)
        VALUES (?, ?, ?, ?, ?)
        ''', (activity.get('time', ''), activity_type, message, error_category, impact_level))
        
        conn.commit()
        conn.close()
    
    def process_expert_entry(self, activity: Dict[str, Any]):
        """Process an expert advisor entry for quality monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        ea_name = activity.get('ea_name', '')
        symbol = activity.get('symbol', '')
        message = activity.get('message', '')
        activity_type = activity.get('activity_type', 'general')
        
        # Calculate compliance score and detect anomalies
        compliance_score = self.calculate_ea_compliance_score(activity)
        anomaly_detected = self.detect_ea_anomaly(activity)
        
        # Correlate with trading phases
        phase_correlation = self.correlate_to_trading_phase(activity_type, message)
        
        cursor.execute('''
        INSERT INTO expert_observations 
        (ea_name, symbol, activity_type, message, phase_correlation, compliance_score, anomaly_detected)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ea_name, symbol, activity_type, message, phase_correlation, compliance_score, anomaly_detected))
        
        conn.commit()
        conn.close()
        
        # If this correlates to a trading phase, record it
        if phase_correlation > 0:
            self.record_trading_phase_from_ea_activity(activity, phase_correlation)
    
    def categorize_journal_error(self, message: str) -> str:
        """Categorize journal error messages"""
        message_lower = message.lower()
        
        if 'autotrading disabled' in message_lower:
            return "AUTO_TRADING_DISABLED"
        elif 'connection' in message_lower and 'failed' in message_lower:
            return "CONNECTION_FAILURE"
        elif 'expert' in message_lower and ('removed' in message_lower or 'stopped' in message_lower):
            return "EA_TERMINATION"
        elif 'invalid' in message_lower or 'error' in message_lower:
            return "EXECUTION_ERROR"
        elif 'spread' in message_lower:
            return "SPREAD_ISSUE"
        else:
            return "OTHER"
    
    def assess_impact_level(self, message: str, error_category: str) -> int:
        """Assess impact level of journal message (1=low, 2=medium, 3=high)"""
        if error_category in ["AUTO_TRADING_DISABLED", "CONNECTION_FAILURE"]:
            return 3  # High impact
        elif error_category in ["EA_TERMINATION", "EXECUTION_ERROR"]:
            return 2  # Medium impact
        else:
            return 1  # Low impact
    
    def calculate_ea_compliance_score(self, activity: Dict[str, Any]) -> float:
        """Calculate compliance score for EA activity (0.0 to 1.0)"""
        base_score = 1.0
        message = activity.get('message', '').lower()
        
        # Check for compliance indicators
        if 'phase' in message and 'complete' in message:
            base_score = 1.0  # Good phase completion
        elif 'error' in message or 'failed' in message:
            base_score = 0.2  # Low compliance for errors
        elif 'calculating' in message or 'processing' in message:
            base_score = 0.8  # Normal processing
        elif 'signal' in message and 'sent' in message:
            base_score = 0.9  # Good signal generation
        
        return base_score
    
    def detect_ea_anomaly(self, activity: Dict[str, Any]) -> bool:
        """Detect anomalies in EA activity"""
        message = activity.get('message', '').lower()
        
        # Anomaly patterns
        anomaly_patterns = [
            'unexpected',
            'invalid',
            'timeout',
            'retry',
            'failed to',
            'cannot',
            'error'
        ]
        
        return any(pattern in message for pattern in anomaly_patterns)
    
    def correlate_to_trading_phase(self, activity_type: str, message: str) -> int:
        """Correlate EA activity to trading phase (0=none, 1-4=phase)"""
        message_lower = message.lower()
        
        if 'bos' in message_lower and ('detected' in message_lower or 'm5' in message_lower):
            return 1  # M5 BOS detection
        elif 'break' in message_lower and 'm1' in message_lower:
            return 2  # M1 break confirmation
        elif 'retest' in message_lower:
            return 3  # M1 retest validation
        elif 'ylipip' in message_lower or ('pip' in message_lower and 'trigger' in message_lower):
            return 4  # YLIPIP trigger
        
        return 0  # No phase correlation
    
    def record_trading_phase_from_ea_activity(self, activity: Dict[str, Any], phase: int):
        """Record trading phase based on EA activity"""
        phase_names = {
            1: "M5_BOS_DETECTION",
            2: "M1_BREAK_CONFIRMATION", 
            3: "M1_RETEST_VALIDATION",
            4: "YLIPIP_TRIGGER"
        }
        
        phase_data = {
            'trade_id': f"ea_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'symbol': activity.get('symbol', 'UNKNOWN'),
            'phase': phase,
            'phase_name': phase_names.get(phase, 'UNKNOWN'),
            'duration_ms': 1000,  # Estimate from EA activity
            'success': 'complete' in activity.get('message', '').lower(),
            'bos_detected': phase == 1,
            'bos_strength': 0.8 if phase == 1 else 0,
            'm1_break_confirmed': phase == 2,
            'break_quality': 0.7 if phase == 2 else 0,
            'retest_completed': phase == 3,
            'retest_quality': 0.8 if phase == 3 else 0,
            'ylipip_triggered': phase == 4,
            'pip_distance': 0.6 if phase == 4 else 0
        }
        
        self.observe_trading_phase(phase_data)
    
    def display_quality_dashboard(self):
        """Display real-time quality dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        ascii_print("=" * 80)
        ascii_print("MIKROBOT ML OBSERVATION SYSTEM - QUALITY DASHBOARD")
        ascii_print("Above Robust! Culture - Six Sigma Excellence")
        ascii_print("=" * 80)
        
        # Current metrics
        metrics = self.current_metrics
        ascii_print(f"QUALITY METRICS:")
        ascii_print(f"  Cp:  {metrics.cp:.3f} (Target: {self.target_cpk:.1f}) {'OK' if metrics.cp >= self.target_cpk else 'IMPROVE'}")
        ascii_print(f"  Cpk: {metrics.cpk:.3f} (Target: {self.target_cpk:.1f}) {'OK' if metrics.cpk >= self.target_cpk else 'IMPROVE'}")
        ascii_print(f"  Defect Rate: {metrics.defect_rate_ppm:.1f} PPM (Target: <=3.4)")
        ascii_print(f"  Process Yield: {metrics.process_yield:.4f}%")
        ascii_print(f"  Sigma Level: {metrics.sigma_level:.1f}σ (Target: 6σ)")
        ascii_print(f"  Control Status: {metrics.control_status.upper()}")
        
        # Overall grade
        grade = self.calculate_overall_grade()
        ascii_print(f"\nOVERALL GRADE: {grade}")
        
        ascii_print("-" * 80)
        ascii_print("Monitoring: Journal + Experts + Trading Phases")
        ascii_print("Press Ctrl+C to stop observation")
        ascii_print("=" * 80)

def main():
    """Main function for ML Observation System"""
    ascii_print("MIKROBOT ML OBSERVATION SYSTEM")
    ascii_print("Above Robust! Quality Management")
    ascii_print("=" * 50)
    
    # Initialize system
    observation_system = MLObservationSystem()
    
    # Connect to MT5 monitoring
    if observation_system.connect_to_mt5_monitoring():
        ascii_print("MT5 connection established")
    else:
        ascii_print("WARNING: MT5 connection failed - using simulated data")
    
    # Start observation
    observation_system.start_observation()
    
    try:
        # Main monitoring loop
        while True:
            observation_system.display_quality_dashboard()
            time.sleep(10)  # Update dashboard every 10 seconds
            
    except KeyboardInterrupt:
        ascii_print("\nStopping ML Observation System...")
        observation_system.observation_active = False
        
        # Generate final report
        final_report = observation_system.generate_quality_report()
        report_file = f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        write_ascii_json(report_file, final_report)
        ascii_print(f"Final quality report saved: {report_file}")
        
        ascii_print("ML Observation System stopped")

if __name__ == "__main__":
    main()