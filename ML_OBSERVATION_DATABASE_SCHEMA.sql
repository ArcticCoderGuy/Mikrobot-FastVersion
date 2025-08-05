-- ML OBSERVATION SYSTEM DATABASE SCHEMA
-- Six Sigma Quality Monitoring for Mikrobot Trading System
-- Target: Cp/Cpk 3.0+ Achievement through Statistical Process Control
-- Owner: LeanSixSigmaMasterBlackBelt Agent

-- ========================================
-- CORE CONFIGURATION TABLES
-- ========================================

-- System configuration and metadata
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT DEFAULT 'SYSTEM'
);

-- Quality specifications and control limits
CREATE TABLE IF NOT EXISTS quality_specifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT UNIQUE NOT NULL,
    lower_spec_limit REAL,
    upper_spec_limit REAL,
    target_value REAL,
    measurement_unit TEXT,
    chart_type TEXT CHECK (chart_type IN ('XBAR_R', 'P_CHART', 'NP_CHART', 'U_CHART', 'C_CHART', 'CUSUM', 'EWMA')),
    sample_size INTEGER,
    control_limit_factor REAL DEFAULT 3.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trading phases configuration
CREATE TABLE IF NOT EXISTS trading_phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_name TEXT UNIQUE NOT NULL,
    phase_order INTEGER NOT NULL,
    description TEXT,
    quality_requirements TEXT, -- JSON format
    spc_requirements TEXT,     -- JSON format
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- RAW DATA COLLECTION TABLES
-- ========================================

-- MT5 Journal data collection
CREATE TABLE IF NOT EXISTS mt5_journal_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_timestamp TIMESTAMP NOT NULL,
    event_type TEXT NOT NULL,
    event_category TEXT CHECK (event_category IN ('CONNECTION', 'EXECUTION', 'ERROR', 'WARNING', 'INFO')),
    severity_level INTEGER CHECK (severity_level BETWEEN 1 AND 5),
    message TEXT,
    symbol TEXT,
    account_number TEXT,
    raw_data TEXT, -- JSON format for additional data
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_journal_timestamp (event_timestamp),
    INDEX idx_journal_category (event_category),
    INDEX idx_journal_symbol (symbol)
);

-- MT5 Expert Advisor monitoring
CREATE TABLE IF NOT EXISTS mt5_expert_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_timestamp TIMESTAMP NOT NULL,
    expert_name TEXT NOT NULL,
    event_type TEXT CHECK (event_type IN ('SIGNAL_GENERATED', 'TRADE_OPENED', 'TRADE_CLOSED', 'ERROR', 'WARNING')),
    symbol TEXT,
    signal_strength REAL,
    execution_time_ms INTEGER,
    success_flag BOOLEAN,
    error_code INTEGER,
    error_message TEXT,
    raw_data TEXT, -- JSON format
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_expert_timestamp (event_timestamp),
    INDEX idx_expert_symbol (symbol),
    INDEX idx_expert_success (success_flag)
);

-- MT5 Calendar and News impact data
CREATE TABLE IF NOT EXISTS mt5_calendar_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_timestamp TIMESTAMP NOT NULL,
    event_title TEXT,
    currency TEXT,
    importance_level INTEGER CHECK (importance_level BETWEEN 1 AND 3),
    impact_type TEXT CHECK (impact_type IN ('POSITIVE', 'NEGATIVE', 'NEUTRAL')),
    volatility_impact REAL,
    price_change_impact REAL,
    execution_quality_impact REAL,
    raw_data TEXT, -- JSON format
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_calendar_timestamp (event_timestamp),
    INDEX idx_calendar_currency (currency),
    INDEX idx_calendar_importance (importance_level)
);

-- ========================================
-- TRADING PHASE QUALITY METRICS
-- ========================================

-- M5 BOS Detection Phase Quality
CREATE TABLE IF NOT EXISTS m5_bos_quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_timestamp TIMESTAMP NOT NULL,
    detection_accuracy REAL CHECK (detection_accuracy BETWEEN 0 AND 1),
    detection_latency_ms INTEGER,
    false_positive_rate REAL CHECK (false_positive_rate BETWEEN 0 AND 1),
    structure_validation_success BOOLEAN,
    trend_direction_accuracy REAL CHECK (trend_direction_accuracy BETWEEN 0 AND 1),
    bos_confirmation_time_ms INTEGER,
    symbol TEXT,
    timeframe TEXT DEFAULT 'M5',
    raw_signal_data TEXT, -- JSON format
    quality_score REAL, -- Composite quality score
    INDEX idx_m5_timestamp (measurement_timestamp),
    INDEX idx_m5_symbol (symbol),
    INDEX idx_m5_quality (quality_score)
);

-- M1 Break Identification Phase Quality
CREATE TABLE IF NOT EXISTS m1_break_quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_timestamp TIMESTAMP NOT NULL,
    direction_alignment_accuracy REAL CHECK (direction_alignment_accuracy BETWEEN 0 AND 1),
    break_level_precision_pips REAL,
    break_candle_recording_accuracy REAL CHECK (break_candle_recording_accuracy BETWEEN 0 AND 1),
    phase_transition_time_ms INTEGER,
    break_strength REAL,
    validation_success BOOLEAN,
    symbol TEXT,
    timeframe TEXT DEFAULT 'M1',
    raw_signal_data TEXT, -- JSON format
    quality_score REAL,
    INDEX idx_m1_break_timestamp (measurement_timestamp),
    INDEX idx_m1_break_symbol (symbol),
    INDEX idx_m1_break_quality (quality_score)
);

-- M1 Retest Validation Phase Quality
CREATE TABLE IF NOT EXISTS m1_retest_quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_timestamp TIMESTAMP NOT NULL,
    retest_quality_assessment REAL CHECK (retest_quality_assessment BETWEEN 0 AND 1),
    bounce_rejection_confirmation BOOLEAN,
    level_test_precision_pips REAL,
    validation_completeness REAL CHECK (validation_completeness BETWEEN 0 AND 1),
    retest_strength REAL,
    time_to_validation_ms INTEGER,
    symbol TEXT,
    timeframe TEXT DEFAULT 'M1',
    raw_signal_data TEXT, -- JSON format
    quality_score REAL,
    INDEX idx_m1_retest_timestamp (measurement_timestamp),
    INDEX idx_m1_retest_symbol (symbol),
    INDEX idx_m1_retest_quality (quality_score)
);

-- YLIPIP Entry Trigger Phase Quality
CREATE TABLE IF NOT EXISTS ylipip_quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_timestamp TIMESTAMP NOT NULL,
    calculation_accuracy_pips REAL,
    entry_trigger_precision REAL CHECK (entry_trigger_precision BETWEEN 0 AND 1),
    execution_latency_ms INTEGER,
    trade_direction_validation BOOLEAN,
    ylipip_value REAL,
    threshold_breach_accuracy REAL CHECK (threshold_breach_accuracy BETWEEN 0 AND 1),
    symbol TEXT,
    timeframe TEXT DEFAULT 'M1',
    raw_signal_data TEXT, -- JSON format
    quality_score REAL,
    INDEX idx_ylipip_timestamp (measurement_timestamp),
    INDEX idx_ylipip_symbol (symbol),
    INDEX idx_ylipip_quality (quality_score)
);

-- ========================================
-- STATISTICAL PROCESS CONTROL DATA
-- ========================================

-- Control chart data for all metrics
CREATE TABLE IF NOT EXISTS spc_control_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_timestamp TIMESTAMP NOT NULL,
    metric_name TEXT NOT NULL,
    chart_type TEXT NOT NULL,
    sample_values TEXT NOT NULL, -- JSON array of sample values
    x_bar REAL,         -- Sample mean
    r_value REAL,       -- Range for X-bar R charts
    p_value REAL,       -- Proportion for p-charts
    np_value INTEGER,   -- Count for np-charts
    u_value REAL,       -- Defects per unit for u-charts
    c_value INTEGER,    -- Count for c-charts
    cusum_value REAL,   -- CUSUM statistic
    ewma_value REAL,    -- EWMA statistic
    sample_size INTEGER,
    subgroup_id TEXT,
    symbol TEXT,
    phase_name TEXT,
    raw_data TEXT, -- JSON format for additional data
    INDEX idx_spc_timestamp (measurement_timestamp),
    INDEX idx_spc_metric (metric_name),
    INDEX idx_spc_chart_type (chart_type),
    INDEX idx_spc_symbol (symbol),
    INDEX idx_spc_phase (phase_name)
);

-- Control limits and statistical parameters
CREATE TABLE IF NOT EXISTS spc_control_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    chart_type TEXT NOT NULL,
    calculation_timestamp TIMESTAMP NOT NULL,
    center_line REAL NOT NULL,
    upper_control_limit REAL NOT NULL,
    lower_control_limit REAL NOT NULL,
    upper_warning_limit REAL,
    lower_warning_limit REAL,
    sample_size INTEGER,
    calculation_method TEXT,
    data_points_used INTEGER,
    validity_start TIMESTAMP,
    validity_end TIMESTAMP,
    parameters TEXT, -- JSON format for chart-specific parameters
    INDEX idx_limits_metric (metric_name),
    INDEX idx_limits_validity (validity_start, validity_end)
);

-- Control chart violations and out-of-control points
CREATE TABLE IF NOT EXISTS spc_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_timestamp TIMESTAMP NOT NULL,
    metric_name TEXT NOT NULL,
    chart_type TEXT NOT NULL,
    violation_type TEXT CHECK (violation_type IN ('RULE_1', 'RULE_2', 'RULE_3', 'RULE_4', 'RULE_5', 'RULE_6', 'RULE_7', 'RULE_8')),
    violation_description TEXT,
    severity_level INTEGER CHECK (severity_level BETWEEN 1 AND 5),
    data_point_value REAL,
    control_limit_value REAL,
    violation_magnitude REAL,
    sample_id INTEGER,
    symbol TEXT,
    phase_name TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMP,
    resolution_action TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    INDEX idx_violations_timestamp (detection_timestamp),
    INDEX idx_violations_metric (metric_name),
    INDEX idx_violations_severity (severity_level),
    INDEX idx_violations_resolved (resolved)
);

-- ========================================
-- PROCESS CAPABILITY ANALYSIS
-- ========================================

-- Process capability measurements
CREATE TABLE IF NOT EXISTS process_capability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_timestamp TIMESTAMP NOT NULL,
    metric_name TEXT NOT NULL,
    sample_size INTEGER NOT NULL,
    sample_mean REAL NOT NULL,
    sample_std_dev REAL NOT NULL,
    lower_spec_limit REAL,
    upper_spec_limit REAL,
    target_value REAL,
    cp_value REAL,
    cpk_value REAL,
    cpu_value REAL,
    cpl_value REAL,
    pp_value REAL,
    ppk_value REAL,
    sigma_level REAL,
    capability_level TEXT,
    ppm_defective REAL,
    yield_percentage REAL,
    symbol TEXT,
    phase_name TEXT,
    calculation_period_hours INTEGER DEFAULT 24,
    INDEX idx_capability_timestamp (measurement_timestamp),
    INDEX idx_capability_metric (metric_name),
    INDEX idx_capability_cpk (cpk_value),
    INDEX idx_capability_symbol (symbol)
);

-- Capability trends and historical analysis
CREATE TABLE IF NOT EXISTS capability_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_timestamp TIMESTAMP NOT NULL,
    metric_name TEXT NOT NULL,
    trend_period_days INTEGER NOT NULL,
    cp_trend_slope REAL,
    cpk_trend_slope REAL,
    trend_direction TEXT CHECK (trend_direction IN ('IMPROVING', 'DEGRADING', 'STABLE')),
    trend_significance REAL, -- R-squared value
    predicted_cp_24h REAL,
    predicted_cpk_24h REAL,
    confidence_interval_lower REAL,
    confidence_interval_upper REAL,
    symbol TEXT,
    phase_name TEXT,
    INDEX idx_trends_timestamp (analysis_timestamp),
    INDEX idx_trends_metric (metric_name),
    INDEX idx_trends_direction (trend_direction)
);

-- ========================================
-- PARETO ANALYSIS DATA
-- ========================================

-- Failure mode categorization
CREATE TABLE IF NOT EXISTS failure_modes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    failure_category TEXT NOT NULL,
    failure_subcategory TEXT,
    failure_type TEXT NOT NULL,
    description TEXT,
    severity_level INTEGER CHECK (severity_level BETWEEN 1 AND 5),
    frequency_weight REAL DEFAULT 1.0,
    impact_weight REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pareto analysis results
CREATE TABLE IF NOT EXISTS pareto_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_timestamp TIMESTAMP NOT NULL,
    analysis_period_hours INTEGER NOT NULL,
    pareto_level INTEGER CHECK (pareto_level BETWEEN 1 AND 3), -- Nested Pareto levels
    failure_category TEXT NOT NULL,
    failure_count INTEGER NOT NULL,
    failure_percentage REAL NOT NULL,
    cumulative_percentage REAL NOT NULL,
    pareto_rank INTEGER NOT NULL,
    is_vital_few BOOLEAN, -- True if in 80% category
    impact_score REAL,
    cost_of_poor_quality REAL,
    symbol TEXT,
    phase_name TEXT,
    root_causes TEXT, -- JSON array of root causes
    recommended_actions TEXT, -- JSON array of actions
    INDEX idx_pareto_timestamp (analysis_timestamp),
    INDEX idx_pareto_category (failure_category),
    INDEX idx_pareto_rank (pareto_rank),
    INDEX idx_pareto_vital (is_vital_few)
);

-- Root cause analysis tracking
CREATE TABLE IF NOT EXISTS root_cause_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_timestamp TIMESTAMP NOT NULL,
    failure_id INTEGER,
    pareto_analysis_id INTEGER,
    root_cause_level INTEGER CHECK (root_cause_level BETWEEN 1 AND 5), -- 5-Why levels
    cause_description TEXT NOT NULL,
    evidence TEXT,
    verification_method TEXT,
    corrective_action TEXT,
    preventive_action TEXT,
    action_owner TEXT,
    target_completion_date DATE,
    actual_completion_date DATE,
    effectiveness_score REAL,
    status TEXT CHECK (status IN ('IDENTIFIED', 'ANALYZING', 'ACTION_PLANNED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED')),
    FOREIGN KEY (pareto_analysis_id) REFERENCES pareto_analysis(id),
    INDEX idx_rca_timestamp (analysis_timestamp),
    INDEX idx_rca_status (status),
    INDEX idx_rca_level (root_cause_level)
);

-- ========================================
-- QUALITY FUNCTION DEPLOYMENT (QFD)
-- ========================================

-- Customer requirements (Voice of Customer)
CREATE TABLE IF NOT EXISTS customer_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_name TEXT UNIQUE NOT NULL,
    description TEXT,
    importance_weight INTEGER CHECK (importance_weight BETWEEN 1 AND 10),
    current_performance REAL,
    target_performance REAL,
    competitive_benchmark REAL,
    gap_analysis REAL,
    priority_level TEXT CHECK (priority_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    measurement_unit TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Technical characteristics (How's)
CREATE TABLE IF NOT EXISTS technical_characteristics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    characteristic_name TEXT UNIQUE NOT NULL,
    description TEXT,
    measurement_method TEXT,
    target_value REAL,
    current_value REAL,
    measurement_unit TEXT,
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    cost_impact INTEGER CHECK (cost_impact BETWEEN 1 AND 5),
    technical_priority REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- QFD relationship matrix
CREATE TABLE IF NOT EXISTS qfd_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_requirement_id INTEGER NOT NULL,
    technical_characteristic_id INTEGER NOT NULL,
    relationship_strength INTEGER CHECK (relationship_strength IN (1, 3, 9)), -- Weak, Medium, Strong
    contribution_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_requirement_id) REFERENCES customer_requirements(id),
    FOREIGN KEY (technical_characteristic_id) REFERENCES technical_characteristics(id),
    UNIQUE(customer_requirement_id, technical_characteristic_id),
    INDEX idx_qfd_customer (customer_requirement_id),
    INDEX idx_qfd_technical (technical_characteristic_id)
);

-- QFD correlation matrix (roof of house)
CREATE TABLE IF NOT EXISTS qfd_correlations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    technical_char_1_id INTEGER NOT NULL,
    technical_char_2_id INTEGER NOT NULL,
    correlation_type TEXT CHECK (correlation_type IN ('STRONG_POSITIVE', 'POSITIVE', 'NEUTRAL', 'NEGATIVE', 'STRONG_NEGATIVE')),
    correlation_value REAL CHECK (correlation_value BETWEEN -1 AND 1),
    impact_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (technical_char_1_id) REFERENCES technical_characteristics(id),
    FOREIGN KEY (technical_char_2_id) REFERENCES technical_characteristics(id),
    UNIQUE(technical_char_1_id, technical_char_2_id),
    INDEX idx_corr_char1 (technical_char_1_id),
    INDEX idx_corr_char2 (technical_char_2_id)
);

-- ========================================
-- PREDICTIVE ANALYTICS DATA
-- ========================================

-- ML model predictions and results
CREATE TABLE IF NOT EXISTS ml_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_timestamp TIMESTAMP NOT NULL,
    model_name TEXT NOT NULL,
    model_version TEXT,
    prediction_type TEXT CHECK (prediction_type IN ('CAPABILITY_DEGRADATION', 'FAILURE_PROBABILITY', 'TREND_FORECAST', 'RISK_ASSESSMENT')),
    target_metric TEXT,
    prediction_horizon_hours INTEGER,
    predicted_value REAL,
    confidence_level REAL CHECK (confidence_level BETWEEN 0 AND 1),
    confidence_interval_lower REAL,
    confidence_interval_upper REAL,
    feature_importance TEXT, -- JSON format
    model_inputs TEXT, -- JSON format
    risk_level TEXT CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    recommended_actions TEXT, -- JSON array
    symbol TEXT,
    phase_name TEXT,
    INDEX idx_predictions_timestamp (prediction_timestamp),
    INDEX idx_predictions_model (model_name),
    INDEX idx_predictions_type (prediction_type),
    INDEX idx_predictions_risk (risk_level)
);

-- Prediction accuracy tracking
CREATE TABLE IF NOT EXISTS prediction_accuracy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    validation_timestamp TIMESTAMP NOT NULL,
    prediction_id INTEGER NOT NULL,
    actual_value REAL,
    predicted_value REAL,
    absolute_error REAL,
    percentage_error REAL,
    accuracy_score REAL,
    model_performance_rating TEXT CHECK (model_performance_rating IN ('EXCELLENT', 'GOOD', 'FAIR', 'POOR')),
    FOREIGN KEY (prediction_id) REFERENCES ml_predictions(id),
    INDEX idx_accuracy_timestamp (validation_timestamp),
    INDEX idx_accuracy_prediction (prediction_id),
    INDEX idx_accuracy_performance (model_performance_rating)
);

-- Early warning alerts
CREATE TABLE IF NOT EXISTS early_warning_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_timestamp TIMESTAMP NOT NULL,
    alert_type TEXT CHECK (alert_type IN ('CAPABILITY_DECLINE', 'TREND_REVERSAL', 'THRESHOLD_BREACH', 'ANOMALY_DETECTED')),
    severity_level INTEGER CHECK (severity_level BETWEEN 1 AND 5),
    metric_name TEXT NOT NULL,
    current_value REAL,
    threshold_value REAL,
    deviation_magnitude REAL,
    trend_direction TEXT,
    time_to_critical_hours REAL,
    confidence_level REAL,
    recommended_actions TEXT, -- JSON array
    symbol TEXT,
    phase_name TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by TEXT,
    acknowledged_at TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    INDEX idx_alerts_timestamp (alert_timestamp),
    INDEX idx_alerts_type (alert_type),
    INDEX idx_alerts_severity (severity_level),
    INDEX idx_alerts_resolved (resolved)
);

-- ========================================
-- DASHBOARD AND REPORTING DATA
-- ========================================

-- Dashboard metrics aggregation
CREATE TABLE IF NOT EXISTS dashboard_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calculation_timestamp TIMESTAMP NOT NULL,
    metric_category TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    aggregation_method TEXT CHECK (aggregation_method IN ('AVG', 'SUM', 'COUNT', 'MIN', 'MAX', 'MEDIAN')),
    aggregation_period_hours INTEGER,
    data_points_count INTEGER,
    quality_flag BOOLEAN DEFAULT TRUE,
    symbol TEXT,
    phase_name TEXT,
    metadata TEXT, -- JSON format for additional context
    INDEX idx_dashboard_timestamp (calculation_timestamp),
    INDEX idx_dashboard_category (metric_category),
    INDEX idx_dashboard_metric (metric_name)
);

-- System performance tracking
CREATE TABLE IF NOT EXISTS system_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_timestamp TIMESTAMP NOT NULL,
    cpu_usage_percent REAL,
    memory_usage_mb REAL,
    disk_usage_percent REAL,
    database_size_mb REAL,
    query_response_time_ms REAL,
    data_collection_rate_per_sec REAL,
    processing_lag_seconds REAL,
    active_alerts_count INTEGER,
    system_health_score REAL CHECK (system_health_score BETWEEN 0 AND 100),
    INDEX idx_system_timestamp (measurement_timestamp),
    INDEX idx_system_health (system_health_score)
);

-- ========================================
-- VIEWS FOR COMMON QUERIES
-- ========================================

-- Overall quality summary view
CREATE VIEW IF NOT EXISTS v_overall_quality_summary AS
SELECT 
    DATE(measurement_timestamp) as measurement_date,
    AVG(cp_value) as avg_cp,
    AVG(cpk_value) as avg_cpk,
    AVG(sigma_level) as avg_sigma_level,
    COUNT(*) as measurement_count,
    AVG(yield_percentage) as avg_yield,
    symbol,
    phase_name
FROM process_capability 
WHERE measurement_timestamp >= datetime('now', '-7 days')
GROUP BY DATE(measurement_timestamp), symbol, phase_name;

-- SPC violations summary view
CREATE VIEW IF NOT EXISTS v_spc_violations_summary AS
SELECT 
    DATE(detection_timestamp) as violation_date,
    metric_name,
    COUNT(*) as violation_count,
    AVG(severity_level) as avg_severity,
    COUNT(CASE WHEN resolved = 1 THEN 1 END) as resolved_count,
    COUNT(CASE WHEN resolved = 0 THEN 1 END) as pending_count,
    symbol,
    phase_name
FROM spc_violations 
WHERE detection_timestamp >= datetime('now', '-30 days')
GROUP BY DATE(detection_timestamp), metric_name, symbol, phase_name;

-- Pareto analysis summary view
CREATE VIEW IF NOT EXISTS v_pareto_summary AS
SELECT 
    failure_category,
    SUM(failure_count) as total_failures,
    AVG(failure_percentage) as avg_failure_percentage,
    MAX(is_vital_few) as is_in_vital_few,
    SUM(cost_of_poor_quality) as total_copq,
    symbol,
    phase_name
FROM pareto_analysis 
WHERE analysis_timestamp >= datetime('now', '-7 days')
GROUP BY failure_category, symbol, phase_name
ORDER BY total_failures DESC;

-- ========================================
-- TRIGGERS FOR DATA INTEGRITY
-- ========================================

-- Update timestamps automatically
CREATE TRIGGER IF NOT EXISTS update_system_config_timestamp 
AFTER UPDATE ON system_config
BEGIN
    UPDATE system_config SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_quality_specs_timestamp 
AFTER UPDATE ON quality_specifications
BEGIN
    UPDATE quality_specifications SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Automatic quality score calculation for trading phases
CREATE TRIGGER IF NOT EXISTS calculate_m5_quality_score
AFTER INSERT ON m5_bos_quality_metrics
BEGIN
    UPDATE m5_bos_quality_metrics 
    SET quality_score = (
        NEW.detection_accuracy * 0.3 +
        (CASE WHEN NEW.detection_latency_ms <= 500 THEN 1.0 ELSE 500.0/NEW.detection_latency_ms END) * 0.2 +
        (1.0 - NEW.false_positive_rate) * 0.3 +
        (CASE WHEN NEW.structure_validation_success THEN 1.0 ELSE 0.0 END) * 0.1 +
        NEW.trend_direction_accuracy * 0.1
    )
    WHERE id = NEW.id;
END;

-- ========================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ========================================

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_quality_metrics_symbol_time ON m5_bos_quality_metrics(symbol, measurement_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_capability_metric_time ON process_capability(metric_name, measurement_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_violations_metric_severity ON spc_violations(metric_name, severity_level, detection_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_model_time ON ml_predictions(model_name, prediction_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dashboard_category_time ON dashboard_metrics(metric_category, calculation_timestamp DESC);

-- ========================================
-- INITIAL DATA POPULATION
-- ========================================

-- Insert default system configuration
INSERT OR IGNORE INTO system_config (config_key, config_value, description) VALUES
('target_cpk', '3.0', 'Six Sigma target Cpk value'),
('control_limit_factor', '3.0', 'Standard control limit factor (3-sigma)'),
('data_retention_days', '365', 'Number of days to retain historical data'),
('alert_response_time_target', '30', 'Target alert response time in seconds'),
('dashboard_refresh_interval', '60', 'Dashboard refresh interval in seconds'),
('prediction_horizon_hours', '24', 'Default prediction horizon in hours'),
('capability_calculation_window', '100', 'Number of data points for capability calculation'),
('system_health_threshold', '85', 'Minimum system health score threshold');

-- Insert trading phases configuration
INSERT OR IGNORE INTO trading_phases (phase_name, phase_order, description, quality_requirements, spc_requirements) VALUES
('M5_BOS_DETECTION', 1, 'M5 timeframe Break of Structure detection and monitoring activation', 
 '{"detection_accuracy": 0.95, "detection_latency_ms": 500, "false_positive_rate": 0.05}',
 '{"chart_type": "P_CHART", "sample_size": 50, "update_frequency": "4_HOURS"}'),
('M1_BREAK_IDENTIFICATION', 2, 'M1 timeframe initial break detection and recording',
 '{"direction_alignment": 1.0, "level_precision_pips": 2.0, "recording_accuracy": 1.0}',
 '{"chart_type": "XBAR_R", "sample_size": 5, "update_frequency": "REAL_TIME"}'),
('M1_RETEST_VALIDATION', 3, 'M1 timeframe retest validation and confirmation',
 '{"retest_quality_cpk": 3.0, "bounce_confirmation": 1.0, "level_precision_pips": 1.0}',
 '{"chart_type": "CUSUM", "sample_size": 1, "update_frequency": "REAL_TIME"}'),
('YLIPIP_ENTRY_TRIGGER', 4, '0.6 YLIPIP calculation and entry trigger execution',
 '{"calculation_accuracy_pips": 0.1, "trigger_precision": 1.0, "execution_latency_ms": 50}',
 '{"chart_type": "XBAR_R", "sample_size": 5, "update_frequency": "REAL_TIME"}');

-- Insert default quality specifications
INSERT OR IGNORE INTO quality_specifications (metric_name, lower_spec_limit, upper_spec_limit, target_value, measurement_unit, chart_type, sample_size) VALUES
('detection_accuracy', 0.70, 1.00, 0.95, 'percentage', 'P_CHART', 50),
('detection_latency_ms', 0, 1000, 500, 'milliseconds', 'XBAR_R', 5),
('false_positive_rate', 0.00, 0.10, 0.05, 'percentage', 'P_CHART', 50),
('direction_alignment', 0.90, 1.00, 1.00, 'percentage', 'NP_CHART', 25),
('level_precision_pips', 0, 5, 2, 'pips', 'XBAR_R', 5),
('retest_quality_score', 0.70, 1.00, 0.95, 'score', 'CUSUM', 1),
('ylipip_accuracy_pips', 0, 0.5, 0.1, 'pips', 'XBAR_R', 5),
('execution_latency_ms', 0, 100, 50, 'milliseconds', 'EWMA', 1);

-- Insert default customer requirements for QFD
INSERT OR IGNORE INTO customer_requirements (requirement_name, description, importance_weight, target_performance, measurement_unit, priority_level) VALUES
('high_win_rate', 'Achieve high trading win rate for consistent profitability', 10, 0.75, 'percentage', 'CRITICAL'),
('low_drawdown', 'Minimize account drawdown to preserve capital', 9, 0.02, 'percentage', 'CRITICAL'),
('fast_execution', 'Execute trades quickly to capture optimal entry points', 8, 50, 'milliseconds', 'HIGH'),
('consistent_profits', 'Generate consistent profitable trading results', 10, 0.95, 'percentage', 'CRITICAL'),
('risk_compliance', 'Maintain full compliance with risk management rules', 10, 1.0, 'percentage', 'CRITICAL'),
('system_reliability', 'Ensure high system uptime and reliability', 9, 0.999, 'percentage', 'HIGH');

-- Insert default technical characteristics for QFD
INSERT OR IGNORE INTO technical_characteristics (characteristic_name, description, target_value, measurement_unit, technical_priority) VALUES
('signal_accuracy', 'Accuracy of trading signal generation', 3.0, 'cpk_value', 52),
('execution_latency', 'Speed of trade execution', 3.0, 'cpk_value', 28),
('system_reliability', 'Overall system reliability and uptime', 3.0, 'cpk_value', 58),
('compliance_monitoring', 'Risk compliance monitoring effectiveness', 3.0, 'cpk_value', 46),
('predictive_capability', 'Quality prediction and forecasting accuracy', 3.0, 'cpk_value', 44),
('performance_monitoring', 'Real-time performance monitoring capability', 3.0, 'cpk_value', 42),
('automated_response', 'Automated quality response and correction', 3.0, 'cpk_value', 38),
('alert_responsiveness', 'Speed and accuracy of quality alerts', 3.0, 'cpk_value', 40);

-- Insert default failure modes for Pareto analysis
INSERT OR IGNORE INTO failure_modes (failure_category, failure_subcategory, failure_type, description, severity_level, frequency_weight, impact_weight) VALUES
('execution_failures', 'entry_signals', 'entry_missed', 'Trade entry signal missed or not executed', 5, 1.0, 1.0),
('execution_failures', 'stop_management', 'sl_not_placed', 'Stop loss not placed correctly', 5, 0.8, 1.0),
('execution_failures', 'profit_taking', 'tp_not_executed', 'Take profit not executed properly', 4, 0.7, 0.8),
('signal_failures', 'bos_detection', 'bos_false_positive', 'False positive BOS detection', 3, 0.9, 0.6),
('signal_failures', 'break_identification', 'break_error', 'Incorrect break identification', 4, 0.8, 0.7),
('signal_failures', 'retest_validation', 'retest_fail', 'Retest validation failure', 4, 0.6, 0.7),
('connection_issues', 'mt5_connection', 'mt5_disconnect', 'MT5 platform disconnection', 4, 0.5, 0.9),
('connection_issues', 'data_feed', 'data_interruption', 'Market data feed interruption', 3, 0.6, 0.8),
('connection_issues', 'network', 'latency_spike', 'Network latency spike affecting execution', 3, 0.7, 0.6),
('timing_issues', 'phase_transitions', 'transition_delay', 'Delay in trading phase transitions', 2, 0.8, 0.4),
('timing_issues', 'signal_processing', 'processing_lag', 'Signal processing lag affecting timing', 3, 0.7, 0.5),
('data_quality', 'tick_data', 'incomplete_ticks', 'Incomplete or missing tick data', 3, 0.4, 0.6),
('data_quality', 'price_feeds', 'price_errors', 'Errors in price feed data', 4, 0.3, 0.8);

-- ========================================
-- MAINTENANCE PROCEDURES
-- ========================================

-- Create maintenance log table
CREATE TABLE IF NOT EXISTS maintenance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    maintenance_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    maintenance_type TEXT CHECK (maintenance_type IN ('DATA_CLEANUP', 'INDEX_REBUILD', 'VACUUM', 'ANALYZE', 'BACKUP')),
    description TEXT,
    duration_seconds INTEGER,
    records_affected INTEGER,
    success BOOLEAN,
    error_message TEXT
);

-- Enable Write-Ahead Logging for better performance
PRAGMA journal_mode = WAL;

-- Set optimal performance settings
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456; -- 256MB

-- Analyze statistics for query optimization
ANALYZE;