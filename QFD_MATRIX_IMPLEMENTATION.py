"""
QUALITY FUNCTION DEPLOYMENT (QFD) MATRIX IMPLEMENTATION
House of Quality for Mikrobot Trading System

This module implements comprehensive QFD analysis linking Voice of Customer
to technical characteristics for systematic quality improvement.

Owner: LeanSixSigmaMasterBlackBelt Agent
Target: Customer-focused quality improvement with quantified technical priorities
"""

import numpy as np
import sqlite3
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import logging
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RelationshipStrength(Enum):
    """QFD relationship strength between customer requirements and technical characteristics"""
    STRONG = 9      # ◉ Strong relationship
    MEDIUM = 3      # ○ Medium relationship  
    WEAK = 1        # △ Weak relationship
    NONE = 0        # No relationship

class CorrelationType(Enum):
    """Technical characteristic correlation types (roof of house)"""
    STRONG_POSITIVE = "STRONG_POSITIVE"    # ++ Strong synergy
    POSITIVE = "POSITIVE"                  # + Positive synergy
    NEUTRAL = "NEUTRAL"                    # ○ No correlation
    NEGATIVE = "NEGATIVE"                  # - Trade-off
    STRONG_NEGATIVE = "STRONG_NEGATIVE"    # -- Strong conflict

class PriorityLevel(Enum):
    """Priority levels for requirements and characteristics"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class CustomerRequirement:
    """Voice of Customer requirement definition"""
    id: int
    name: str
    description: str
    importance_weight: int  # 1-10 scale
    current_performance: float
    target_performance: float
    competitive_benchmark: float
    gap_analysis: float = field(init=False)
    priority_level: PriorityLevel = field(init=False)
    measurement_unit: str = ""
    
    def __post_init__(self):
        self.gap_analysis = self.target_performance - self.current_performance
        self.priority_level = self._determine_priority_level()
    
    def _determine_priority_level(self) -> PriorityLevel:
        """Determine priority based on importance weight and gap"""
        if self.importance_weight >= 9 and abs(self.gap_analysis) > 0.1:
            return PriorityLevel.CRITICAL
        elif self.importance_weight >= 7 and abs(self.gap_analysis) > 0.05:
            return PriorityLevel.HIGH
        elif self.importance_weight >= 5:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW

@dataclass
class TechnicalCharacteristic:
    """Technical 'How' to achieve customer requirements"""
    id: int
    name: str
    description: str
    measurement_method: str
    target_value: float
    current_value: float
    measurement_unit: str
    difficulty_level: int  # 1-5 scale (1=easy, 5=very difficult)
    cost_impact: int       # 1-5 scale (1=low cost, 5=high cost)
    technical_priority: float = field(init=False)
    improvement_potential: float = field(init=False)
    
    def __post_init__(self):
        self.improvement_potential = abs(self.target_value - self.current_value) / self.target_value if self.target_value != 0 else 0
        self.technical_priority = 0  # Will be calculated by QFD analysis

@dataclass
class QFDRelationship:
    """Relationship between customer requirement and technical characteristic"""
    customer_requirement_id: int
    technical_characteristic_id: int
    relationship_strength: RelationshipStrength
    contribution_score: float = field(init=False)
    
    def __post_init__(self):
        self.contribution_score = self.relationship_strength.value

@dataclass
class TechnicalCorrelation:
    """Correlation between technical characteristics (roof of house)"""
    tech_char_1_id: int
    tech_char_2_id: int
    correlation_type: CorrelationType
    correlation_value: float  # -1 to +1
    impact_description: str

@dataclass
class QFDAnalysisResult:
    """Complete QFD analysis results"""
    analysis_timestamp: datetime
    customer_requirements: List[CustomerRequirement]
    technical_characteristics: List[TechnicalCharacteristic]
    relationship_matrix: List[List[RelationshipStrength]]
    correlation_matrix: List[List[CorrelationType]]
    technical_priorities: Dict[int, float]
    improvement_roadmap: List[Dict[str, Any]]
    competitive_analysis: Dict[str, Any]
    cost_benefit_analysis: Dict[str, Any]

class QFDHouseOfQuality:
    """Comprehensive QFD House of Quality implementation"""
    
    def __init__(self, db_path: str = "ml_observation_system.db"):
        self.db_path = db_path
        self.customer_requirements: List[CustomerRequirement] = []
        self.technical_characteristics: List[TechnicalCharacteristic] = []
        self.relationships: List[QFDRelationship] = []
        self.correlations: List[TechnicalCorrelation] = []
        self._init_database()
        self._load_default_data()
    
    def _init_database(self):
        """Initialize database connection"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customer_requirements'")
                if not cursor.fetchone():
                    logger.warning("QFD tables not found. Please run the database schema script first.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def _load_default_data(self):
        """Load default customer requirements and technical characteristics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                self._load_customer_requirements(conn)
                self._load_technical_characteristics(conn)
                self._load_relationships(conn)
                self._load_correlations(conn)
        except Exception as e:
            logger.error(f"Error loading default data: {e}")
            self._create_default_data()
    
    def _load_customer_requirements(self, conn: sqlite3.Connection):
        """Load customer requirements from database"""
        cursor = conn.execute("""
            SELECT id, requirement_name, description, importance_weight, 
                   current_performance, target_performance, competitive_benchmark, measurement_unit
            FROM customer_requirements
        """)
        
        for row in cursor.fetchall():
            req = CustomerRequirement(
                id=row[0],
                name=row[1],
                description=row[2],
                importance_weight=row[3],
                current_performance=row[4] or 0,
                target_performance=row[5] or 0,
                competitive_benchmark=row[6] or 0,
                measurement_unit=row[7] or ""
            )
            self.customer_requirements.append(req)
    
    def _load_technical_characteristics(self, conn: sqlite3.Connection):
        """Load technical characteristics from database"""
        cursor = conn.execute("""
            SELECT id, characteristic_name, description, measurement_method,
                   target_value, current_value, measurement_unit, difficulty_level, cost_impact
            FROM technical_characteristics
        """)
        
        for row in cursor.fetchall():
            char = TechnicalCharacteristic(
                id=row[0],
                name=row[1],
                description=row[2],
                measurement_method=row[3],
                target_value=row[4] or 0,
                current_value=row[5] or 0,
                measurement_unit=row[6] or "",
                difficulty_level=row[7] or 3,
                cost_impact=row[8] or 3
            )
            self.technical_characteristics.append(char)
    
    def _load_relationships(self, conn: sqlite3.Connection):
        """Load QFD relationships from database"""
        cursor = conn.execute("""
            SELECT customer_requirement_id, technical_characteristic_id, relationship_strength
            FROM qfd_relationships
        """)
        
        for row in cursor.fetchall():
            strength = RelationshipStrength(row[2])
            relationship = QFDRelationship(
                customer_requirement_id=row[0],
                technical_characteristic_id=row[1],
                relationship_strength=strength
            )
            self.relationships.append(relationship)
    
    def _load_correlations(self, conn: sqlite3.Connection):
        """Load technical correlations from database"""
        cursor = conn.execute("""
            SELECT technical_char_1_id, technical_char_2_id, correlation_type, 
                   correlation_value, impact_description
            FROM qfd_correlations
        """)
        
        for row in cursor.fetchall():
            correlation = TechnicalCorrelation(
                tech_char_1_id=row[0],
                tech_char_2_id=row[1],
                correlation_type=CorrelationType(row[2]),
                correlation_value=row[3],
                impact_description=row[4]
            )
            self.correlations.append(correlation)
    
    def _create_default_data(self):
        """Create default QFD data if not loaded from database"""
        # Customer Requirements (Voice of Customer)
        self.customer_requirements = [
            CustomerRequirement(1, "high_win_rate", "Achieve high trading win rate for consistent profitability", 
                              10, 0.68, 0.75, 0.72, "percentage"),
            CustomerRequirement(2, "low_drawdown", "Minimize account drawdown to preserve capital", 
                              9, 0.035, 0.02, 0.025, "percentage"),
            CustomerRequirement(3, "fast_execution", "Execute trades quickly to capture optimal entry points", 
                              8, 75, 50, 60, "milliseconds"),
            CustomerRequirement(4, "consistent_profits", "Generate consistent profitable trading results", 
                              10, 0.82, 0.95, 0.88, "percentage"),
            CustomerRequirement(5, "risk_compliance", "Maintain full compliance with risk management rules", 
                              10, 0.97, 1.0, 0.99, "percentage"),
            CustomerRequirement(6, "system_reliability", "Ensure high system uptime and reliability", 
                              9, 0.991, 0.999, 0.995, "percentage"),
            CustomerRequirement(7, "trade_accuracy", "High accuracy in trade signal generation and execution",
                              8, 0.85, 0.95, 0.90, "percentage"),
            CustomerRequirement(8, "cost_efficiency", "Minimize trading costs and maximize net profits",
                              7, 0.92, 0.98, 0.95, "percentage")
        ]
        
        # Technical Characteristics (How's)
        self.technical_characteristics = [
            TechnicalCharacteristic(1, "signal_accuracy", "Accuracy of trading signal generation", 
                                  "SPC control charts", 3.0, 2.1, "cpk_value", 3, 2),
            TechnicalCharacteristic(2, "execution_latency", "Speed of trade execution", 
                                  "Latency measurement", 3.0, 1.8, "cpk_value", 2, 3),
            TechnicalCharacteristic(3, "system_reliability", "Overall system reliability and uptime", 
                                  "Uptime monitoring", 3.0, 2.5, "cpk_value", 4, 4),
            TechnicalCharacteristic(4, "compliance_monitoring", "Risk compliance monitoring effectiveness", 
                                  "Compliance audit", 3.0, 2.7, "cpk_value", 2, 2),
            TechnicalCharacteristic(5, "predictive_capability", "Quality prediction and forecasting accuracy", 
                                  "ML model validation", 3.0, 1.9, "cpk_value", 5, 4),
            TechnicalCharacteristic(6, "performance_monitoring", "Real-time performance monitoring capability", 
                                  "Dashboard metrics", 3.0, 2.3, "cpk_value", 3, 3),
            TechnicalCharacteristic(7, "automated_response", "Automated quality response and correction", 
                                  "Response time measurement", 3.0, 2.0, "cpk_value", 4, 3),
            TechnicalCharacteristic(8, "alert_responsiveness", "Speed and accuracy of quality alerts", 
                                  "Alert performance", 3.0, 2.2, "cpk_value", 3, 2)
        ]
        
        # Define relationships (simplified matrix)
        relationship_data = [
            # (customer_req_id, tech_char_id, strength)
            (1, 1, RelationshipStrength.STRONG),    # high_win_rate -> signal_accuracy
            (1, 3, RelationshipStrength.STRONG),    # high_win_rate -> system_reliability
            (1, 4, RelationshipStrength.STRONG),    # high_win_rate -> compliance_monitoring
            (1, 5, RelationshipStrength.STRONG),    # high_win_rate -> predictive_capability
            (2, 1, RelationshipStrength.STRONG),    # low_drawdown -> signal_accuracy
            (2, 4, RelationshipStrength.STRONG),    # low_drawdown -> compliance_monitoring
            (2, 5, RelationshipStrength.STRONG),    # low_drawdown -> predictive_capability
            (2, 6, RelationshipStrength.STRONG),    # low_drawdown -> performance_monitoring
            (2, 8, RelationshipStrength.STRONG),    # low_drawdown -> alert_responsiveness
            (3, 2, RelationshipStrength.STRONG),    # fast_execution -> execution_latency
            (3, 7, RelationshipStrength.STRONG),    # fast_execution -> automated_response
            (3, 8, RelationshipStrength.STRONG),    # fast_execution -> alert_responsiveness
            (4, 1, RelationshipStrength.STRONG),    # consistent_profits -> signal_accuracy
            (4, 3, RelationshipStrength.STRONG),    # consistent_profits -> system_reliability
            (4, 4, RelationshipStrength.STRONG),    # consistent_profits -> compliance_monitoring
            (4, 5, RelationshipStrength.STRONG),    # consistent_profits -> predictive_capability
            (4, 6, RelationshipStrength.STRONG),    # consistent_profits -> performance_monitoring
            (5, 4, RelationshipStrength.STRONG),    # risk_compliance -> compliance_monitoring
            (5, 6, RelationshipStrength.STRONG),    # risk_compliance -> performance_monitoring
            (5, 7, RelationshipStrength.STRONG),    # risk_compliance -> automated_response
            (5, 8, RelationshipStrength.STRONG),    # risk_compliance -> alert_responsiveness
            (6, 3, RelationshipStrength.STRONG),    # system_reliability -> system_reliability
            (6, 6, RelationshipStrength.STRONG),    # system_reliability -> performance_monitoring
            (6, 7, RelationshipStrength.STRONG),    # system_reliability -> automated_response
            (6, 8, RelationshipStrength.STRONG),    # system_reliability -> alert_responsiveness
            (7, 1, RelationshipStrength.STRONG),    # trade_accuracy -> signal_accuracy
            (7, 2, RelationshipStrength.MEDIUM),    # trade_accuracy -> execution_latency
            (7, 5, RelationshipStrength.STRONG),    # trade_accuracy -> predictive_capability
            (8, 2, RelationshipStrength.MEDIUM),    # cost_efficiency -> execution_latency
            (8, 6, RelationshipStrength.MEDIUM),    # cost_efficiency -> performance_monitoring
            (8, 7, RelationshipStrength.MEDIUM),    # cost_efficiency -> automated_response
        ]
        
        self.relationships = [
            QFDRelationship(cr_id, tc_id, strength) 
            for cr_id, tc_id, strength in relationship_data
        ]
        
        # Define technical correlations (roof of house)
        correlation_data = [
            # (tech_char_1_id, tech_char_2_id, correlation_type, correlation_value, description)
            (1, 5, CorrelationType.STRONG_POSITIVE, 0.8, "Signal accuracy enhances predictive capability"),
            (1, 6, CorrelationType.POSITIVE, 0.6, "Signal accuracy supports performance monitoring"),
            (2, 7, CorrelationType.STRONG_POSITIVE, 0.7, "Fast execution enables automated response"),
            (2, 8, CorrelationType.STRONG_POSITIVE, 0.8, "Fast execution improves alert responsiveness"),
            (3, 6, CorrelationType.POSITIVE, 0.6, "System reliability supports performance monitoring"),
            (3, 7, CorrelationType.POSITIVE, 0.5, "Reliability enables automated response"),
            (4, 6, CorrelationType.STRONG_POSITIVE, 0.9, "Compliance monitoring requires performance monitoring"),
            (4, 8, CorrelationType.STRONG_POSITIVE, 0.8, "Compliance monitoring requires alert responsiveness"),
            (5, 6, CorrelationType.POSITIVE, 0.6, "Predictive capability enhances performance monitoring"),
            (6, 7, CorrelationType.POSITIVE, 0.7, "Performance monitoring enables automated response"),
            (6, 8, CorrelationType.STRONG_POSITIVE, 0.8, "Performance monitoring drives alert responsiveness"),
            (7, 8, CorrelationType.POSITIVE, 0.6, "Automated response improves alert responsiveness"),
            # Trade-offs
            (1, 2, CorrelationType.NEGATIVE, -0.3, "Signal accuracy may conflict with execution speed"),
            (2, 3, CorrelationType.NEGATIVE, -0.2, "Fast execution may impact system reliability"),
            (5, 2, CorrelationType.NEGATIVE, -0.4, "Complex prediction models may slow execution")
        ]
        
        self.correlations = [
            TechnicalCorrelation(tc1_id, tc2_id, corr_type, corr_val, desc)
            for tc1_id, tc2_id, corr_type, corr_val, desc in correlation_data
        ]
    
    def perform_qfd_analysis(self) -> QFDAnalysisResult:
        """Perform comprehensive QFD analysis"""
        logger.info("Starting QFD House of Quality analysis...")
        
        # Build relationship matrix
        relationship_matrix = self._build_relationship_matrix()
        
        # Build correlation matrix
        correlation_matrix = self._build_correlation_matrix()
        
        # Calculate technical priorities
        technical_priorities = self._calculate_technical_priorities(relationship_matrix)
        
        # Update technical characteristics with calculated priorities
        self._update_technical_priorities(technical_priorities)
        
        # Generate improvement roadmap
        improvement_roadmap = self._generate_improvement_roadmap()
        
        # Perform competitive analysis
        competitive_analysis = self._perform_competitive_analysis()
        
        # Perform cost-benefit analysis
        cost_benefit_analysis = self._perform_cost_benefit_analysis()
        
        # Create analysis result
        result = QFDAnalysisResult(
            analysis_timestamp=datetime.utcnow(),
            customer_requirements=self.customer_requirements,
            technical_characteristics=self.technical_characteristics,
            relationship_matrix=relationship_matrix,
            correlation_matrix=correlation_matrix,
            technical_priorities=technical_priorities,
            improvement_roadmap=improvement_roadmap,
            competitive_analysis=competitive_analysis,
            cost_benefit_analysis=cost_benefit_analysis
        )
        
        # Store results in database
        self._store_qfd_results(result)
        
        logger.info("QFD analysis completed successfully")
        return result
    
    def _build_relationship_matrix(self) -> List[List[RelationshipStrength]]:
        """Build the relationship matrix between customer requirements and technical characteristics"""
        num_requirements = len(self.customer_requirements)
        num_characteristics = len(self.technical_characteristics)
        
        # Initialize matrix with no relationships
        matrix = [[RelationshipStrength.NONE for _ in range(num_characteristics)] 
                 for _ in range(num_requirements)]
        
        # Fill in defined relationships
        for rel in self.relationships:
            req_idx = next((i for i, req in enumerate(self.customer_requirements) 
                          if req.id == rel.customer_requirement_id), None)
            char_idx = next((i for i, char in enumerate(self.technical_characteristics) 
                           if char.id == rel.technical_characteristic_id), None)
            
            if req_idx is not None and char_idx is not None:
                matrix[req_idx][char_idx] = rel.relationship_strength
        
        return matrix
    
    def _build_correlation_matrix(self) -> List[List[CorrelationType]]:
        """Build the correlation matrix between technical characteristics (roof of house)"""
        num_characteristics = len(self.technical_characteristics)
        
        # Initialize matrix with neutral correlations
        matrix = [[CorrelationType.NEUTRAL for _ in range(num_characteristics)] 
                 for _ in range(num_characteristics)]
        
        # Set diagonal to neutral (self-correlation)
        for i in range(num_characteristics):
            matrix[i][i] = CorrelationType.NEUTRAL
        
        # Fill in defined correlations
        for corr in self.correlations:
            char1_idx = next((i for i, char in enumerate(self.technical_characteristics) 
                            if char.id == corr.tech_char_1_id), None)
            char2_idx = next((i for i, char in enumerate(self.technical_characteristics) 
                            if char.id == corr.tech_char_2_id), None)
            
            if char1_idx is not None and char2_idx is not None:
                matrix[char1_idx][char2_idx] = corr.correlation_type
                matrix[char2_idx][char1_idx] = corr.correlation_type  # Symmetric
        
        return matrix
    
    def _calculate_technical_priorities(self, relationship_matrix: List[List[RelationshipStrength]]) -> Dict[int, float]:
        """Calculate technical characteristic priorities based on customer importance and relationships"""
        technical_priorities = {}
        
        for char_idx, char in enumerate(self.technical_characteristics):
            priority_score = 0.0
            
            for req_idx, req in enumerate(self.customer_requirements):
                relationship_strength = relationship_matrix[req_idx][char_idx].value
                customer_weight = req.importance_weight
                gap_multiplier = 1 + abs(req.gap_analysis)  # Higher gap = higher priority
                
                # Priority calculation: Importance × Relationship × Gap
                contribution = customer_weight * relationship_strength * gap_multiplier
                priority_score += contribution
            
            technical_priorities[char.id] = priority_score
        
        return technical_priorities
    
    def _update_technical_priorities(self, technical_priorities: Dict[int, float]):
        """Update technical characteristics with calculated priorities"""
        for char in self.technical_characteristics:
            char.technical_priority = technical_priorities.get(char.id, 0.0)
    
    def _generate_improvement_roadmap(self) -> List[Dict[str, Any]]:
        """Generate prioritized improvement roadmap based on QFD analysis"""
        # Sort technical characteristics by priority (descending)
        sorted_chars = sorted(self.technical_characteristics, 
                             key=lambda x: x.technical_priority, reverse=True)
        
        roadmap = []
        
        for i, char in enumerate(sorted_chars[:10]):  # Top 10 priorities
            # Calculate implementation complexity
            complexity_score = (char.difficulty_level + char.cost_impact) / 2
            
            # Calculate ROI potential
            roi_potential = char.improvement_potential * char.technical_priority / complexity_score
            
            # Determine implementation phase
            if i < 3:
                phase = "Phase 1 (Immediate - Weeks 1-2)"
            elif i < 6:
                phase = "Phase 2 (Short-term - Weeks 3-6)"
            else:
                phase = "Phase 3 (Medium-term - Weeks 7-12)"
            
            roadmap.append({
                'rank': i + 1,
                'technical_characteristic': char.name,
                'description': char.description,
                'priority_score': char.technical_priority,
                'current_value': char.current_value,
                'target_value': char.target_value,
                'improvement_potential': char.improvement_potential,
                'difficulty_level': char.difficulty_level,
                'cost_impact': char.cost_impact,
                'complexity_score': complexity_score,
                'roi_potential': roi_potential,
                'implementation_phase': phase,
                'success_metrics': self._generate_success_metrics(char),
                'resource_requirements': self._estimate_resource_requirements(char),
                'dependencies': self._identify_dependencies(char),
                'risks': self._identify_risks(char)
            })
        
        return roadmap
    
    def _perform_competitive_analysis(self) -> Dict[str, Any]:
        """Perform competitive analysis based on customer requirements"""
        competitive_gaps = []
        total_gap_score = 0
        
        for req in self.customer_requirements:
            competitive_gap = req.competitive_benchmark - req.current_performance
            gap_percentage = (competitive_gap / req.competitive_benchmark * 100) if req.competitive_benchmark != 0 else 0
            
            competitive_gaps.append({
                'requirement': req.name,
                'current_performance': req.current_performance,
                'competitive_benchmark': req.competitive_benchmark,
                'gap': competitive_gap,
                'gap_percentage': gap_percentage,
                'importance_weight': req.importance_weight,
                'weighted_gap_score': abs(gap_percentage) * req.importance_weight
            })
            
            total_gap_score += abs(gap_percentage) * req.importance_weight
        
        # Sort by weighted gap score
        competitive_gaps.sort(key=lambda x: x['weighted_gap_score'], reverse=True)
        
        return {
            'total_gap_score': total_gap_score,
            'average_gap_score': total_gap_score / len(self.customer_requirements),
            'competitive_position': self._assess_competitive_position(total_gap_score),
            'gaps_by_requirement': competitive_gaps,
            'priority_areas': competitive_gaps[:5],  # Top 5 gaps
            'strengths': [gap for gap in competitive_gaps if gap['gap'] > 0],
            'weaknesses': [gap for gap in competitive_gaps if gap['gap'] < 0]
        }
    
    def _perform_cost_benefit_analysis(self) -> Dict[str, Any]:
        """Perform cost-benefit analysis for technical improvements"""
        total_implementation_cost = 0
        total_potential_benefit = 0
        
        cost_benefit_items = []
        
        for char in self.technical_characteristics:
            # Estimate implementation cost based on difficulty and cost impact
            implementation_cost = char.difficulty_level * char.cost_impact * 10000  # Base cost in dollars
            
            # Estimate potential benefit based on priority and improvement potential
            potential_benefit = char.technical_priority * char.improvement_potential * 5000  # Base benefit
            
            # Calculate ROI
            roi = (potential_benefit - implementation_cost) / implementation_cost if implementation_cost > 0 else 0
            
            # Calculate payback period (months)
            monthly_benefit = potential_benefit / 12
            payback_months = implementation_cost / monthly_benefit if monthly_benefit > 0 else float('inf')
            
            cost_benefit_items.append({
                'technical_characteristic': char.name,
                'implementation_cost': implementation_cost,
                'potential_annual_benefit': potential_benefit,
                'roi_percentage': roi * 100,
                'payback_months': min(payback_months, 999),  # Cap at 999 months
                'priority_score': char.technical_priority,
                'risk_adjusted_roi': roi * (1 - char.difficulty_level * 0.1)  # Adjust for risk
            })
            
            total_implementation_cost += implementation_cost
            total_potential_benefit += potential_benefit
        
        # Sort by risk-adjusted ROI
        cost_benefit_items.sort(key=lambda x: x['risk_adjusted_roi'], reverse=True)
        
        overall_roi = (total_potential_benefit - total_implementation_cost) / total_implementation_cost if total_implementation_cost > 0 else 0
        overall_payback = total_implementation_cost / (total_potential_benefit / 12) if total_potential_benefit > 0 else float('inf')
        
        return {
            'total_implementation_cost': total_implementation_cost,
            'total_potential_annual_benefit': total_potential_benefit,
            'overall_roi_percentage': overall_roi * 100,
            'overall_payback_months': min(overall_payback, 999),
            'cost_benefit_by_characteristic': cost_benefit_items,
            'high_roi_opportunities': [item for item in cost_benefit_items if item['roi_percentage'] > 100],
            'quick_wins': [item for item in cost_benefit_items if item['payback_months'] < 6 and item['roi_percentage'] > 50],
            'investment_recommendation': self._generate_investment_recommendation(cost_benefit_items)
        }
    
    def _generate_success_metrics(self, char: TechnicalCharacteristic) -> List[str]:
        """Generate success metrics for technical characteristic improvement"""
        metrics = []
        
        if 'accuracy' in char.name.lower():
            metrics.extend([
                f"Achieve Cp/Cpk ≥ {char.target_value}",
                "Error rate < 1%",
                "Signal quality score > 95%"
            ])
        elif 'latency' in char.name.lower():
            metrics.extend([
                f"Average response time < {int(char.target_value * 50)}ms",
                "99th percentile < 200ms",
                "Timeout rate < 0.1%"
            ])
        elif 'reliability' in char.name.lower():
            metrics.extend([
                "System uptime > 99.9%",
                "MTBF > 720 hours",
                "Recovery time < 5 minutes"
            ])
        else:
            metrics.extend([
                f"Target Cp/Cpk = {char.target_value}",
                "Performance improvement > 20%",
                "Customer satisfaction increase"
            ])
        
        return metrics
    
    def _estimate_resource_requirements(self, char: TechnicalCharacteristic) -> Dict[str, Any]:
        """Estimate resource requirements for improvement"""
        base_hours = char.difficulty_level * char.cost_impact * 40  # Base hours
        
        return {
            'development_hours': base_hours,
            'testing_hours': base_hours * 0.3,
            'deployment_hours': base_hours * 0.1,
            'total_hours': base_hours * 1.4,
            'team_size': min(max(1, char.difficulty_level), 5),
            'duration_weeks': max(1, int(base_hours * 1.4 / (40 * min(max(1, char.difficulty_level), 5)))),
            'estimated_cost': base_hours * 1.4 * 100  # $100/hour rate
        }
    
    def _identify_dependencies(self, char: TechnicalCharacteristic) -> List[str]:
        """Identify dependencies for technical characteristic improvement"""
        dependencies = []
        
        # Check correlations for dependencies
        for corr in self.correlations:
            if (corr.tech_char_1_id == char.id or corr.tech_char_2_id == char.id) and \
               corr.correlation_type in [CorrelationType.STRONG_POSITIVE, CorrelationType.POSITIVE]:
                other_char_id = corr.tech_char_2_id if corr.tech_char_1_id == char.id else corr.tech_char_1_id
                other_char = next((c for c in self.technical_characteristics if c.id == other_char_id), None)
                if other_char:
                    dependencies.append(f"Requires improvement in {other_char.name}")
        
        # Add general dependencies based on characteristic type
        if 'monitoring' in char.name.lower():
            dependencies.append("Database optimization required")
            dependencies.append("Dashboard infrastructure needed")
        elif 'automated' in char.name.lower():
            dependencies.append("Process automation framework")
            dependencies.append("Alert system integration")
        
        return dependencies[:5]  # Limit to top 5 dependencies
    
    def _identify_risks(self, char: TechnicalCharacteristic) -> List[Dict[str, Any]]:
        """Identify risks for technical characteristic improvement"""
        risks = []
        
        # High difficulty risks
        if char.difficulty_level >= 4:
            risks.append({
                'risk': 'Implementation complexity',
                'probability': 'Medium',
                'impact': 'High',
                'mitigation': 'Phased implementation with early prototyping'
            })
        
        # High cost risks
        if char.cost_impact >= 4:
            risks.append({
                'risk': 'Budget overrun',
                'probability': 'Medium',
                'impact': 'Medium',
                'mitigation': 'Detailed cost estimation and regular budget reviews'
            })
        
        # Technical risks based on characteristic type
        if 'predictive' in char.name.lower():
            risks.append({
                'risk': 'Model overfitting or poor generalization',
                'probability': 'Medium',
                'impact': 'High',
                'mitigation': 'Cross-validation and walk-forward testing'
            })
        elif 'automated' in char.name.lower():
            risks.append({
                'risk': 'System instability from automation',
                'probability': 'Low',
                'impact': 'High',
                'mitigation': 'Extensive testing and gradual rollout'
            })
        
        return risks
    
    def _assess_competitive_position(self, total_gap_score: float) -> str:
        """Assess competitive position based on gap score"""
        if total_gap_score < 50:
            return "Market Leader"
        elif total_gap_score < 100:
            return "Competitive"
        elif total_gap_score < 200:
            return "Below Average"
        else:
            return "Significantly Behind"
    
    def _generate_investment_recommendation(self, cost_benefit_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate investment recommendations based on cost-benefit analysis"""
        high_roi_items = [item for item in cost_benefit_items if item['roi_percentage'] > 100]
        quick_wins = [item for item in cost_benefit_items if item['payback_months'] < 6]
        
        total_quick_win_cost = sum(item['implementation_cost'] for item in quick_wins)
        total_quick_win_benefit = sum(item['potential_annual_benefit'] for item in quick_wins)
        
        return {
            'recommended_strategy': 'Focus on Quick Wins followed by High ROI projects',
            'phase_1_investment': total_quick_win_cost,
            'phase_1_annual_return': total_quick_win_benefit,
            'phase_1_projects': len(quick_wins),
            'high_roi_opportunities': len(high_roi_items),
            'investment_priority': 'Immediate' if quick_wins else 'Moderate',
            'risk_level': 'Low to Medium',
            'success_probability': '85%'
        }
    
    def _store_qfd_results(self, result: QFDAnalysisResult):
        """Store QFD analysis results in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Update technical priorities
                for char_id, priority in result.technical_priorities.items():
                    conn.execute("""
                        UPDATE technical_characteristics 
                        SET technical_priority = ?
                        WHERE id = ?
                    """, (priority, char_id))
                
                # Store improvement roadmap (simplified)
                for item in result.improvement_roadmap:
                    conn.execute("""
                        INSERT OR REPLACE INTO qfd_analysis_results 
                        (analysis_timestamp, technical_characteristic, priority_score, 
                         implementation_phase, roi_potential, success_metrics)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        result.analysis_timestamp,
                        item['technical_characteristic'],
                        item['priority_score'],
                        item['implementation_phase'],
                        item['roi_potential'],
                        json.dumps(item['success_metrics'])
                    ))
                    
        except Exception as e:
            logger.error(f"Error storing QFD results: {e}")
    
    def generate_qfd_report(self, result: QFDAnalysisResult) -> Dict[str, Any]:
        """Generate comprehensive QFD analysis report"""
        return {
            'executive_summary': {
                'analysis_date': result.analysis_timestamp,
                'total_customer_requirements': len(result.customer_requirements),
                'total_technical_characteristics': len(result.technical_characteristics),
                'top_priority_characteristic': max(result.technical_characteristics, 
                                                 key=lambda x: x.technical_priority).name,
                'highest_priority_score': max(result.technical_priorities.values()),
                'critical_requirements': len([req for req in result.customer_requirements 
                                            if req.priority_level == PriorityLevel.CRITICAL]),
                'investment_recommendation': result.cost_benefit_analysis['investment_recommendation']
            },
            'customer_voice_analysis': {
                'requirements_by_priority': self._group_requirements_by_priority(result.customer_requirements),
                'largest_performance_gaps': self._identify_largest_gaps(result.customer_requirements),
                'customer_satisfaction_potential': self._calculate_satisfaction_potential(result.customer_requirements)
            },
            'technical_priorities': {
                'ranked_characteristics': sorted(
                    [{'name': char.name, 'priority': char.technical_priority, 
                      'current': char.current_value, 'target': char.target_value}
                     for char in result.technical_characteristics],
                    key=lambda x: x['priority'], reverse=True
                ),
                'improvement_focus_areas': result.improvement_roadmap[:3],
                'resource_allocation_recommendation': self._recommend_resource_allocation(result.improvement_roadmap)
            },
            'relationship_analysis': {
                'strong_relationships': self._count_strong_relationships(result.relationship_matrix),
                'relationship_density': self._calculate_relationship_density(result.relationship_matrix),
                'coverage_analysis': self._analyze_coverage(result.relationship_matrix)
            },
            'correlation_insights': {
                'positive_synergies': len([corr for corr in self.correlations 
                                         if corr.correlation_type in [CorrelationType.POSITIVE, 
                                                                     CorrelationType.STRONG_POSITIVE]]),
                'negative_tradeoffs': len([corr for corr in self.correlations 
                                         if corr.correlation_type in [CorrelationType.NEGATIVE, 
                                                                     CorrelationType.STRONG_NEGATIVE]]),
                'critical_correlations': self._identify_critical_correlations()
            },
            'competitive_analysis': result.competitive_analysis,
            'cost_benefit_analysis': result.cost_benefit_analysis,
            'implementation_roadmap': result.improvement_roadmap,
            'success_metrics_framework': self._create_success_metrics_framework(result),
            'monitoring_recommendations': self._create_monitoring_recommendations(result)
        }
    
    def _group_requirements_by_priority(self, requirements: List[CustomerRequirement]) -> Dict[str, List[Dict[str, Any]]]:
        """Group customer requirements by priority level"""
        grouped = {level.value: [] for level in PriorityLevel}
        
        for req in requirements:
            grouped[req.priority_level.value].append({
                'name': req.name,
                'importance_weight': req.importance_weight,
                'gap_analysis': req.gap_analysis,
                'current_performance': req.current_performance,
                'target_performance': req.target_performance
            })
        
        return grouped
    
    def _identify_largest_gaps(self, requirements: List[CustomerRequirement]) -> List[Dict[str, Any]]:
        """Identify requirements with largest performance gaps"""
        gaps = [
            {
                'requirement': req.name,
                'gap': abs(req.gap_analysis),
                'gap_percentage': abs(req.gap_analysis / req.target_performance * 100) if req.target_performance != 0 else 0,
                'importance': req.importance_weight,
                'weighted_gap': abs(req.gap_analysis) * req.importance_weight
            }
            for req in requirements
        ]
        
        return sorted(gaps, key=lambda x: x['weighted_gap'], reverse=True)[:5]
    
    def _calculate_satisfaction_potential(self, requirements: List[CustomerRequirement]) -> Dict[str, float]:
        """Calculate customer satisfaction improvement potential"""
        total_potential = sum(abs(req.gap_analysis) * req.importance_weight for req in requirements)
        max_possible = sum(req.target_performance * req.importance_weight for req in requirements)
        
        return {
            'total_improvement_potential': total_potential,
            'max_possible_satisfaction': max_possible,
            'improvement_percentage': (total_potential / max_possible * 100) if max_possible > 0 else 0,
            'current_satisfaction_level': (max_possible - total_potential) / max_possible if max_possible > 0 else 0
        }
    
    def _recommend_resource_allocation(self, roadmap: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Recommend resource allocation based on improvement roadmap"""
        phase1_items = [item for item in roadmap if 'Phase 1' in item['implementation_phase']]
        phase2_items = [item for item in roadmap if 'Phase 2' in item['implementation_phase']]
        phase3_items = [item for item in roadmap if 'Phase 3' in item['implementation_phase']]
        
        return {
            'phase_1_allocation': {
                'projects': len(phase1_items),
                'total_hours': sum(item['resource_requirements']['total_hours'] for item in phase1_items),
                'estimated_cost': sum(item['resource_requirements']['estimated_cost'] for item in phase1_items),
                'team_size_needed': max([item['resource_requirements']['team_size'] for item in phase1_items] or [0])
            },
            'phase_2_allocation': {
                'projects': len(phase2_items),
                'total_hours': sum(item['resource_requirements']['total_hours'] for item in phase2_items),
                'estimated_cost': sum(item['resource_requirements']['estimated_cost'] for item in phase2_items),
                'team_size_needed': max([item['resource_requirements']['team_size'] for item in phase2_items] or [0])
            },
            'phase_3_allocation': {
                'projects': len(phase3_items),
                'total_hours': sum(item['resource_requirements']['total_hours'] for item in phase3_items),
                'estimated_cost': sum(item['resource_requirements']['estimated_cost'] for item in phase3_items),
                'team_size_needed': max([item['resource_requirements']['team_size'] for item in phase3_items] or [0])
            }
        }
    
    def _count_strong_relationships(self, matrix: List[List[RelationshipStrength]]) -> int:
        """Count strong relationships in the matrix"""
        count = 0
        for row in matrix:
            for strength in row:
                if strength == RelationshipStrength.STRONG:
                    count += 1
        return count
    
    def _calculate_relationship_density(self, matrix: List[List[RelationshipStrength]]) -> float:
        """Calculate relationship density (percentage of non-zero relationships)"""
        total_cells = len(matrix) * len(matrix[0]) if matrix else 0
        non_zero_cells = sum(1 for row in matrix for strength in row if strength != RelationshipStrength.NONE)
        
        return (non_zero_cells / total_cells * 100) if total_cells > 0 else 0
    
    def _analyze_coverage(self, matrix: List[List[RelationshipStrength]]) -> Dict[str, Any]:
        """Analyze requirement and characteristic coverage"""
        if not matrix:
            return {}
        
        # Requirements coverage (rows with at least one relationship)
        req_coverage = sum(1 for row in matrix if any(strength != RelationshipStrength.NONE for strength in row))
        req_coverage_pct = (req_coverage / len(matrix) * 100) if matrix else 0
        
        # Characteristics coverage (columns with at least one relationship)
        char_coverage = 0
        for col_idx in range(len(matrix[0])):
            if any(matrix[row_idx][col_idx] != RelationshipStrength.NONE for row_idx in range(len(matrix))):
                char_coverage += 1
        char_coverage_pct = (char_coverage / len(matrix[0]) * 100) if matrix and matrix[0] else 0
        
        return {
            'requirements_covered': req_coverage,
            'requirements_coverage_percentage': req_coverage_pct,
            'characteristics_covered': char_coverage,
            'characteristics_coverage_percentage': char_coverage_pct,
            'coverage_completeness': min(req_coverage_pct, char_coverage_pct)
        }
    
    def _identify_critical_correlations(self) -> List[Dict[str, Any]]:
        """Identify critical technical correlations"""
        critical_correlations = []
        
        for corr in self.correlations:
            if abs(corr.correlation_value) >= 0.7:  # Strong correlations
                char1 = next((c for c in self.technical_characteristics if c.id == corr.tech_char_1_id), None)
                char2 = next((c for c in self.technical_characteristics if c.id == corr.tech_char_2_id), None)
                
                if char1 and char2:
                    critical_correlations.append({
                        'characteristic_1': char1.name,
                        'characteristic_2': char2.name,
                        'correlation_type': corr.correlation_type.value,
                        'correlation_strength': corr.correlation_value,
                        'impact_description': corr.impact_description,
                        'management_priority': 'High' if abs(corr.correlation_value) >= 0.8 else 'Medium'
                    })
        
        return sorted(critical_correlations, key=lambda x: abs(x['correlation_strength']), reverse=True)
    
    def _create_success_metrics_framework(self, result: QFDAnalysisResult) -> Dict[str, Any]:
        """Create comprehensive success metrics framework"""
        return {
            'customer_satisfaction_metrics': [
                'Customer requirement gap closure rate',
                'Weighted satisfaction score improvement',
                'Priority requirement achievement percentage'
            ],
            'technical_performance_metrics': [
                'Technical characteristic Cp/Cpk achievement',
                'Priority score improvement rate',
                'Implementation milestone completion'
            ],
            'business_impact_metrics': [
                'ROI achievement vs. projections',
                'Cost reduction from quality improvements', 
                'Revenue impact from performance gains'
            ],
            'process_metrics': [
                'Implementation timeline adherence',
                'Resource utilization efficiency',
                'Risk mitigation effectiveness'
            ]
        }
    
    def _create_monitoring_recommendations(self, result: QFDAnalysisResult) -> Dict[str, Any]:
        """Create monitoring recommendations for QFD implementation"""
        return {
            'review_frequency': {
                'qfd_matrix_review': 'Quarterly',
                'customer_requirement_update': 'Bi-annually',
                'technical_priority_recalculation': 'Monthly',
                'competitive_analysis_refresh': 'Quarterly'
            },
            'key_indicators_to_track': [
                'Technical characteristic performance trends',
                'Customer satisfaction survey results',
                'Competitive benchmark changes',
                'Implementation progress vs. plan'
            ],
            'escalation_triggers': [
                'Technical characteristic falls below target for 2 consecutive periods',
                'Customer requirement gap increases beyond threshold',
                'Competitive position deteriorates significantly',
                'Implementation delays exceed 20% of timeline'
            ],
            'reporting_recommendations': {
                'executive_dashboard': 'Monthly QFD summary with key metrics',
                'technical_teams': 'Weekly characteristic performance reports',
                'customer_facing': 'Quarterly improvement communications',
                'stakeholders': 'Bi-annual comprehensive QFD analysis'
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize QFD House of Quality
    qfd = QFDHouseOfQuality()
    
    # Perform comprehensive QFD analysis
    print("Performing QFD House of Quality analysis...")
    result = qfd.perform_qfd_analysis()
    
    # Generate comprehensive report
    print("Generating QFD analysis report...")
    report = qfd.generate_qfd_report(result)
    
    # Display key results
    print("\n=== QFD ANALYSIS EXECUTIVE SUMMARY ===")
    print(json.dumps(report['executive_summary'], indent=2, default=str))
    
    print("\n=== TECHNICAL PRIORITIES (TOP 5) ===")
    for i, char in enumerate(report['technical_priorities']['ranked_characteristics'][:5]):
        print(f"{i+1}. {char['name']}: Priority Score = {char['priority']:.1f}")
        print(f"   Current: {char['current']:.2f}, Target: {char['target']:.2f}")
    
    print("\n=== IMPROVEMENT ROADMAP (TOP 3) ===")
    for item in report['technical_priorities']['improvement_focus_areas']:
        print(f"- {item['technical_characteristic']} ({item['implementation_phase']})")
        print(f"  Priority Score: {item['priority_score']:.1f}")
        print(f"  ROI Potential: {item['roi_potential']:.2f}")
    
    print("\n=== COST-BENEFIT SUMMARY ===")
    cba = report['cost_benefit_analysis']
    print(f"Total Implementation Cost: ${cba['total_implementation_cost']:,.0f}")
    print(f"Total Annual Benefit: ${cba['total_potential_annual_benefit']:,.0f}")
    print(f"Overall ROI: {cba['overall_roi_percentage']:.1f}%")
    print(f"Payback Period: {cba['overall_payback_months']:.1f} months")