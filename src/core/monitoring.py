"""
Comprehensive Monitoring and Logging System
Advanced monitoring, metrics collection, and logging for the Mikrobot trading system
Includes performance tracking, alerting, and real-time dashboards
"""

from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import json
import time
from collections import defaultdict, deque
import statistics
import threading
import psutil
import os

# Configure structured logging
import structlog

# Configure structlog for structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """Metric data point"""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime
    tags: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class Alert:
    """Alert definition"""
    alert_id: str
    name: str
    condition: str
    severity: AlertSeverity
    timestamp: datetime
    message: str
    component: str
    tags: Optional[Dict[str, str]] = None
    resolved: bool = False
    resolved_timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


class MetricsCollector:
    """Metrics collection and aggregation"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: deque = deque(maxlen=max_metrics)
        self.metric_aggregates: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        
        # Background aggregation
        self._aggregation_task: Optional[asyncio.Task] = None
        self._aggregation_interval = 60  # seconds
        
        logger.info("Metrics collector initialized")
    
    def record_metric(self, name: str, value: Union[int, float], 
                     metric_type: MetricType, tags: Optional[Dict[str, str]] = None):
        """Record a metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.utcnow(),
            tags=tags or {}
        )
        
        self.metrics.append(metric)
        
        # Update type-specific storage
        metric_key = f"{name}:{':'.join(f'{k}={v}' for k, v in (tags or {}).items())}"
        
        if metric_type == MetricType.COUNTER:
            self.counters[metric_key] += value
        elif metric_type == MetricType.GAUGE:
            self.gauges[metric_key] = value
        elif metric_type == MetricType.HISTOGRAM:
            self.histograms[metric_key].append(value)
            # Keep only last 1000 values
            if len(self.histograms[metric_key]) > 1000:
                self.histograms[metric_key] = self.histograms[metric_key][-1000:]
        elif metric_type == MetricType.TIMER:
            self.timers[metric_key].append(value)
            if len(self.timers[metric_key]) > 1000:
                self.timers[metric_key] = self.timers[metric_key][-1000:]
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> int:
        """Get counter value"""
        metric_key = f"{name}:{':'.join(f'{k}={v}' for k, v in (tags or {}).items())}"
        return self.counters.get(metric_key, 0)
    
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get gauge value"""
        metric_key = f"{name}:{':'.join(f'{k}={v}' for k, v in (tags or {}).items())}"
        return self.gauges.get(metric_key, 0.0)
    
    def get_histogram_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics"""
        metric_key = f"{name}:{':'.join(f'{k}={v}' for k, v in (tags or {}).items())}"
        values = self.histograms.get(metric_key, [])
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'p95': self._percentile(values, 95),
            'p99': self._percentile(values, 99)
        }
    
    def get_timer_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get timer statistics"""
        return self.get_histogram_stats(name, tags)
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100.0) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    async def start_aggregation(self):
        """Start background aggregation task"""
        if self._aggregation_task is None:
            self._aggregation_task = asyncio.create_task(self._aggregation_loop())
    
    async def stop_aggregation(self):
        """Stop background aggregation task"""
        if self._aggregation_task:
            self._aggregation_task.cancel()
            try:
                await self._aggregation_task
            except asyncio.CancelledError:
                pass
            self._aggregation_task = None
    
    async def _aggregation_loop(self):
        """Background aggregation loop"""
        while True:
            try:
                await asyncio.sleep(self._aggregation_interval)
                await self._aggregate_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Aggregation error", error=str(e))
    
    async def _aggregate_metrics(self):
        """Aggregate metrics for reporting"""
        # This could send metrics to external systems like Prometheus, InfluxDB, etc.
        logger.debug("Aggregating metrics", 
                    counters_count=len(self.counters),
                    gauges_count=len(self.gauges),
                    histograms_count=len(self.histograms))


class AlertManager:
    """Alert management and notification system"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.alerts: Dict[str, Alert] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.notification_handlers: List[Callable] = []
        
        # Alert thresholds
        self.default_thresholds = {
            'error_rate': 0.05,      # 5% error rate
            'latency_p95': 5000,     # 5 seconds
            'memory_usage': 0.8,     # 80% memory usage
            'cpu_usage': 0.8,        # 80% CPU usage
            'disk_usage': 0.9        # 90% disk usage
        }
        
        self.thresholds = {**self.default_thresholds, **self.config.get('thresholds', {})}
        
        logger.info("Alert manager initialized")
    
    def add_notification_handler(self, handler: Callable):
        """Add notification handler"""
        self.notification_handlers.append(handler)
    
    def create_alert(self, name: str, condition: str, severity: AlertSeverity,
                    message: str, component: str, tags: Optional[Dict[str, str]] = None) -> Alert:
        """Create new alert"""
        alert_id = f"{component}_{name}_{datetime.utcnow().timestamp()}"
        
        alert = Alert(
            alert_id=alert_id,
            name=name,
            condition=condition,
            severity=severity,
            timestamp=datetime.utcnow(),
            message=message,
            component=component,
            tags=tags or {}
        )
        
        self.alerts[alert_id] = alert
        
        # Send notifications
        asyncio.create_task(self._send_alert_notifications(alert))
        
        logger.warning("Alert created", 
                      alert_id=alert_id,
                      name=name,
                      severity=severity.value,
                      component=component,
                      message=message)
        
        return alert
    
    def resolve_alert(self, alert_id: str):
        """Resolve alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolved_timestamp = datetime.utcnow()
            
            logger.info("Alert resolved",
                       alert_id=alert_id,
                       name=alert.name,
                       component=alert.component)
    
    async def _send_alert_notifications(self, alert: Alert):
        """Send alert notifications"""
        for handler in self.notification_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error("Notification handler error",
                           handler=str(handler),
                           error=str(e))
    
    def get_active_alerts(self) -> List[Alert]:
        """Get active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary"""
        active_alerts = self.get_active_alerts()
        
        return {
            'total_alerts': len(self.alerts),
            'active_alerts': len(active_alerts),
            'alerts_by_severity': {
                severity.value: len([a for a in active_alerts if a.severity == severity])
                for severity in AlertSeverity
            },
            'alerts_by_component': defaultdict(int),
            'recent_alerts': [asdict(alert) for alert in list(self.alerts.values())[-10:]]
        }


class PerformanceMonitor:
    """System and application performance monitoring"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.monitoring_interval = 30  # seconds
        
        logger.info("Performance monitor initialized")
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
            logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Performance monitoring error", error=str(e))
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics.record_metric("system.cpu.usage_percent", cpu_percent, MetricType.GAUGE)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics.record_metric("system.memory.usage_percent", memory.percent, MetricType.GAUGE)
        self.metrics.record_metric("system.memory.available_mb", memory.available / 1024 / 1024, MetricType.GAUGE)
        self.metrics.record_metric("system.memory.used_mb", memory.used / 1024 / 1024, MetricType.GAUGE)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.metrics.record_metric("system.disk.usage_percent", disk_percent, MetricType.GAUGE)
        self.metrics.record_metric("system.disk.free_gb", disk.free / 1024 / 1024 / 1024, MetricType.GAUGE)
        
        # Process metrics
        process = psutil.Process(os.getpid())
        self.metrics.record_metric("process.memory.rss_mb", process.memory_info().rss / 1024 / 1024, MetricType.GAUGE)
        self.metrics.record_metric("process.memory.vms_mb", process.memory_info().vms / 1024 / 1024, MetricType.GAUGE)
        self.metrics.record_metric("process.cpu.percent", process.cpu_percent(), MetricType.GAUGE)
        self.metrics.record_metric("process.threads", process.num_threads(), MetricType.GAUGE)
        
        # Network metrics (if available)
        try:
            network = psutil.net_io_counters()
            self.metrics.record_metric("system.network.bytes_sent", network.bytes_sent, MetricType.COUNTER)
            self.metrics.record_metric("system.network.bytes_recv", network.bytes_recv, MetricType.COUNTER)
        except:
            pass  # Network metrics may not be available


class MonitoringSystem:
    """
    Comprehensive monitoring system
    
    Features:
    - Metrics collection and aggregation
    - Alert management and notifications
    - Performance monitoring
    - Real-time dashboards
    - Health checks
    - Structured logging
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize components
        self.metrics = MetricsCollector(max_metrics=self.config.get('max_metrics', 10000))
        self.alerts = AlertManager(config.get('alerts', {}))
        self.performance = PerformanceMonitor(self.metrics)
        
        # Component health tracking
        self.component_health: Dict[str, Dict[str, Any]] = {}
        
        # Monitoring state
        self.is_running = False
        self.start_time = datetime.utcnow()
        
        # Add default notification handlers
        self._setup_default_handlers()
        
        logger.info("Monitoring system initialized")
    
    def _setup_default_handlers(self):
        """Setup default notification handlers"""
        # Log alert handler
        async def log_alert_handler(alert: Alert):
            log_level = {
                AlertSeverity.INFO: logger.info,
                AlertSeverity.WARNING: logger.warning,
                AlertSeverity.ERROR: logger.error,
                AlertSeverity.CRITICAL: logger.critical
            }.get(alert.severity, logger.info)
            
            log_level("Alert triggered",
                     alert_id=alert.alert_id,
                     name=alert.name,
                     severity=alert.severity.value,
                     component=alert.component,
                     message=alert.message)
        
        self.alerts.add_notification_handler(log_alert_handler)
    
    async def start(self):
        """Start monitoring system"""
        if not self.is_running:
            self.is_running = True
            
            # Start components
            await self.metrics.start_aggregation()
            await self.performance.start_monitoring()
            
            logger.info("Monitoring system started")
    
    async def stop(self):
        """Stop monitoring system"""
        if self.is_running:
            self.is_running = False
            
            # Stop components
            await self.metrics.stop_aggregation()
            await self.performance.stop_monitoring()
            
            logger.info("Monitoring system stopped")
    
    # Convenience methods for metrics
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment counter metric"""
        self.metrics.record_metric(name, value, MetricType.COUNTER, tags)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set gauge metric"""
        self.metrics.record_metric(name, value, MetricType.GAUGE, tags)
    
    def record_histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record histogram value"""
        self.metrics.record_metric(name, value, MetricType.HISTOGRAM, tags)
    
    def record_timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record timer duration"""
        self.metrics.record_metric(name, duration_ms, MetricType.TIMER, tags)
    
    # Context manager for timing operations
    class Timer:
        def __init__(self, monitoring_system: 'MonitoringSystem', name: str, tags: Optional[Dict[str, str]] = None):
            self.monitoring_system = monitoring_system
            self.name = name
            self.tags = tags
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time:
                duration_ms = (time.time() - self.start_time) * 1000
                self.monitoring_system.record_timer(self.name, duration_ms, self.tags)
    
    def timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> 'MonitoringSystem.Timer':
        """Create timer context manager"""
        return self.Timer(self, name, tags)
    
    # Health checks
    def update_component_health(self, component: str, status: str, metadata: Optional[Dict[str, Any]] = None):
        """Update component health status"""
        self.component_health[component] = {
            'status': status,
            'last_updated': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        # Record health metric
        health_value = 1.0 if status == 'healthy' else 0.0
        self.set_gauge(f"component.{component}.health", health_value)
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        unhealthy_components = [
            comp for comp, health in self.component_health.items()
            if health.get('status') != 'healthy'
        ]
        
        overall_status = 'healthy' if not unhealthy_components else 'degraded'
        if len(unhealthy_components) > len(self.component_health) / 2:
            overall_status = 'unhealthy'
        
        return {
            'status': overall_status,
            'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
            'components': self.component_health,
            'unhealthy_components': unhealthy_components,
            'active_alerts': len(self.alerts.get_active_alerts()),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        return {
            'system_health': self.get_system_health(),
            'metrics_summary': {
                'counters_count': len(self.metrics.counters),
                'gauges_count': len(self.metrics.gauges),
                'histograms_count': len(self.metrics.histograms),
                'total_metrics': len(self.metrics.metrics)
            },
            'alert_summary': self.alerts.get_alert_summary(),
            'performance_metrics': {
                'cpu_usage': self.metrics.get_gauge('system.cpu.usage_percent'),
                'memory_usage': self.metrics.get_gauge('system.memory.usage_percent'),
                'disk_usage': self.metrics.get_gauge('system.disk.usage_percent')
            },
            'monitoring_config': {
                'is_running': self.is_running,
                'start_time': self.start_time.isoformat(),
                'metrics_interval': self.performance.monitoring_interval
            }
        }
    
    async def create_performance_alert(self, metric_name: str, threshold: float, 
                                     comparison: str = 'greater_than', 
                                     severity: AlertSeverity = AlertSeverity.WARNING):
        """Create performance-based alert"""
        current_value = self.metrics.get_gauge(metric_name)
        
        should_alert = False
        if comparison == 'greater_than' and current_value > threshold:
            should_alert = True
        elif comparison == 'less_than' and current_value < threshold:
            should_alert = True
        elif comparison == 'equals' and current_value == threshold:
            should_alert = True
        
        if should_alert:
            self.alerts.create_alert(
                name=f"{metric_name}_threshold",
                condition=f"{metric_name} {comparison} {threshold}",
                severity=severity,
                message=f"{metric_name} is {current_value}, threshold is {threshold}",
                component="performance_monitor",
                tags={'metric': metric_name, 'threshold': str(threshold)}
            )


# Global monitoring instance
monitoring_system: Optional[MonitoringSystem] = None


def get_monitoring_system(config: Optional[Dict[str, Any]] = None) -> MonitoringSystem:
    """Get global monitoring system instance"""
    global monitoring_system
    if monitoring_system is None:
        monitoring_system = MonitoringSystem(config)
    return monitoring_system


def initialize_monitoring(config: Optional[Dict[str, Any]] = None) -> MonitoringSystem:
    """Initialize global monitoring system"""
    global monitoring_system
    monitoring_system = MonitoringSystem(config)
    return monitoring_system