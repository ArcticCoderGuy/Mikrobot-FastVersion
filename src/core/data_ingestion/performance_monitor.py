"""
Ingestion Performance Monitor
Real-time monitoring and alerting for data ingestion performance
"""

import asyncio
import time
import statistics
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
import logging
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class PerformanceAlert:
    """Performance alert data structure"""
    timestamp: datetime
    alert_type: str
    severity: str  # 'warning', 'error', 'critical'
    message: str
    data: Dict[str, Any]
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class PerformanceThresholds:
    """Performance thresholds for monitoring"""
    # Latency thresholds (milliseconds)
    latency_warning: float = 10.0
    latency_error: float = 50.0
    latency_critical: float = 100.0
    
    # Throughput thresholds (messages per second)
    throughput_warning: float = 10.0
    throughput_error: float = 5.0
    throughput_critical: float = 1.0
    
    # Error rate thresholds (percentage)
    error_rate_warning: float = 5.0
    error_rate_error: float = 10.0
    error_rate_critical: float = 25.0
    
    # Queue depth thresholds
    queue_depth_warning: int = 1000
    queue_depth_error: int = 5000
    queue_depth_critical: int = 9000
    
    # Memory thresholds (MB)
    memory_warning: float = 500.0
    memory_error: float = 1000.0
    memory_critical: float = 2000.0


class IngestionPerformanceMonitor:
    """
    Comprehensive performance monitoring for data ingestion
    
    Features:
    - Real-time latency tracking
    - Throughput monitoring
    - Error rate analysis
    - Resource usage tracking
    - Automated alerting
    - Performance analytics
    """
    
    def __init__(self, 
                 thresholds: Optional[PerformanceThresholds] = None,
                 alert_callback: Optional[Callable[[PerformanceAlert], None]] = None,
                 history_size: int = 10000):
        
        self.thresholds = thresholds or PerformanceThresholds()
        self.alert_callback = alert_callback
        self.history_size = history_size
        
        # Performance metrics tracking
        self.latency_history = deque(maxlen=history_size)
        self.throughput_history = deque(maxlen=history_size)
        self.error_history = deque(maxlen=history_size)
        
        # Real-time counters
        self.message_count = 0
        self.error_count = 0
        self.last_reset_time = datetime.now(timezone.utc)
        
        # Alert management
        self.active_alerts: List[PerformanceAlert] = []
        self.alert_history: List[PerformanceAlert] = []
        self.max_alert_history = 1000
        
        # Monitoring tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
        # Statistics cache
        self.stats_cache = {}
        self.stats_cache_timeout = 5  # 5 seconds
        self.last_stats_update = datetime.min
        
        # Symbol-specific tracking
        self.symbol_metrics: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Performance monitor initialized")
    
    async def start_monitoring(self):
        """Start performance monitoring"""
        if self.is_monitoring:
            logger.warning("Performance monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Performance monitoring stopped")
    
    def record_latency(self, latency_ms: float, symbol: Optional[str] = None):
        """Record latency measurement"""
        timestamp = datetime.now(timezone.utc)
        
        # Add to global history
        self.latency_history.append((timestamp, latency_ms))
        
        # Track symbol-specific metrics
        if symbol:
            if symbol not in self.symbol_metrics:
                self.symbol_metrics[symbol] = {
                    'latencies': deque(maxlen=1000),
                    'message_count': 0,
                    'error_count': 0
                }
            
            self.symbol_metrics[symbol]['latencies'].append((timestamp, latency_ms))
        
        # Check latency thresholds
        self._check_latency_thresholds(latency_ms)
    
    def record_message(self, symbol: Optional[str] = None, success: bool = True):
        """Record message processing"""
        self.message_count += 1
        
        if not success:
            self.error_count += 1
            timestamp = datetime.now(timezone.utc)
            self.error_history.append((timestamp, 1))
        
        # Track symbol-specific metrics
        if symbol:
            if symbol not in self.symbol_metrics:
                self.symbol_metrics[symbol] = {
                    'latencies': deque(maxlen=1000),
                    'message_count': 0,
                    'error_count': 0
                }
            
            self.symbol_metrics[symbol]['message_count'] += 1
            if not success:
                self.symbol_metrics[symbol]['error_count'] += 1
    
    def record_queue_depth(self, depth: int):
        """Record queue depth measurement"""
        # Check queue depth thresholds
        self._check_queue_depth_thresholds(depth)
    
    def record_memory_usage(self, memory_mb: float):
        """Record memory usage measurement"""
        # Check memory thresholds
        self._check_memory_thresholds(memory_mb)
    
    def get_performance_stats(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        now = datetime.now(timezone.utc)
        
        # Use cached stats if recent
        if (not force_refresh and 
            self.stats_cache and 
            (now - self.last_stats_update).total_seconds() < self.stats_cache_timeout):
            return self.stats_cache
        
        # Calculate fresh statistics
        stats = {
            'timestamp': now.isoformat(),
            'monitoring_duration': self._get_monitoring_duration(),
            'message_stats': self._calculate_message_stats(),
            'latency_stats': self._calculate_latency_stats(),
            'error_stats': self._calculate_error_stats(),
            'throughput_stats': self._calculate_throughput_stats(),
            'alert_stats': self._get_alert_stats(),
            'symbol_stats': self._get_symbol_stats()
        }
        
        # Cache results
        self.stats_cache = stats
        self.last_stats_update = now
        
        return stats
    
    def _calculate_latency_stats(self) -> Dict[str, Any]:
        """Calculate latency statistics"""
        if not self.latency_history:
            return {'count': 0}
        
        # Get recent latencies (last 5 minutes)
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        recent_latencies = [
            latency for timestamp, latency in self.latency_history 
            if timestamp > cutoff_time
        ]
        
        if not recent_latencies:
            return {'count': 0}
        
        # Calculate statistics
        sorted_latencies = sorted(recent_latencies)
        
        return {
            'count': len(recent_latencies),
            'avg_ms': statistics.mean(recent_latencies),
            'min_ms': min(recent_latencies),
            'max_ms': max(recent_latencies),
            'median_ms': statistics.median(recent_latencies),
            'p90_ms': sorted_latencies[int(len(sorted_latencies) * 0.9)],
            'p95_ms': sorted_latencies[int(len(sorted_latencies) * 0.95)],
            'p99_ms': sorted_latencies[int(len(sorted_latencies) * 0.99)],
            'std_dev': statistics.stdev(recent_latencies) if len(recent_latencies) > 1 else 0
        }
    
    def _calculate_message_stats(self) -> Dict[str, Any]:
        """Calculate message processing statistics"""
        duration = self._get_monitoring_duration()
        
        return {
            'total_messages': self.message_count,
            'total_errors': self.error_count,
            'success_rate': (self.message_count - self.error_count) / max(self.message_count, 1),
            'error_rate': self.error_count / max(self.message_count, 1),
            'messages_per_second': self.message_count / max(duration, 1),
            'monitoring_duration_seconds': duration
        }
    
    def _calculate_error_stats(self) -> Dict[str, Any]:
        """Calculate error rate statistics"""
        if not self.error_history:
            return {'recent_error_rate': 0.0, 'error_trend': 'stable'}
        
        # Calculate error rate over different time windows
        now = datetime.now(timezone.utc)
        windows = [60, 300, 900]  # 1 min, 5 min, 15 min
        
        error_rates = {}
        for window in windows:
            cutoff_time = now - timedelta(seconds=window)
            window_errors = sum(
                1 for timestamp, _ in self.error_history 
                if timestamp > cutoff_time
            )
            
            # Estimate total messages in window (simplified)
            window_messages = max(window_errors, int(window * (self.message_count / max(self._get_monitoring_duration(), 1))))
            error_rates[f'{window}s'] = window_errors / max(window_messages, 1)
        
        # Determine trend
        if len(error_rates) >= 2:
            recent_rate = error_rates['60s']
            older_rate = error_rates['300s']
            
            if recent_rate > older_rate * 1.5:
                trend = 'increasing'
            elif recent_rate < older_rate * 0.5:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'unknown'
        
        return {
            'recent_error_rate': error_rates.get('60s', 0.0),
            'error_rates_by_window': error_rates,
            'error_trend': trend
        }
    
    def _calculate_throughput_stats(self) -> Dict[str, Any]:
        """Calculate throughput statistics"""
        # Calculate throughput over different time windows
        now = datetime.now(timezone.utc)
        duration = self._get_monitoring_duration()
        
        # Overall throughput
        overall_throughput = self.message_count / max(duration, 1)
        
        # Recent throughput (last 5 minutes)
        recent_duration = min(duration, 300)  # 5 minutes max
        recent_messages = int(recent_duration * overall_throughput)
        recent_throughput = recent_messages / max(recent_duration, 1)
        
        return {
            'overall_throughput_mps': overall_throughput,
            'recent_throughput_mps': recent_throughput,
            'peak_throughput_estimate': overall_throughput * 1.5,  # Simplified estimate
            'throughput_trend': 'stable'  # Could be enhanced with trend analysis
        }
    
    def _get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        return {
            'active_alerts': len(self.active_alerts),
            'total_alerts': len(self.alert_history),
            'alert_summary': self._summarize_alerts()
        }
    
    def _get_symbol_stats(self) -> Dict[str, Any]:
        """Get symbol-specific statistics"""
        symbol_stats = {}
        
        for symbol, metrics in self.symbol_metrics.items():
            if metrics['latencies']:
                latencies = [lat for _, lat in metrics['latencies']]
                symbol_stats[symbol] = {
                    'message_count': metrics['message_count'],
                    'error_count': metrics['error_count'],
                    'error_rate': metrics['error_count'] / max(metrics['message_count'], 1),
                    'avg_latency_ms': statistics.mean(latencies),
                    'max_latency_ms': max(latencies)
                }
            else:
                symbol_stats[symbol] = {
                    'message_count': metrics['message_count'],
                    'error_count': metrics['error_count'],
                    'error_rate': metrics['error_count'] / max(metrics['message_count'], 1),
                    'avg_latency_ms': 0,
                    'max_latency_ms': 0
                }
        
        return symbol_stats
    
    def _get_monitoring_duration(self) -> float:
        """Get monitoring duration in seconds"""
        return (datetime.now(timezone.utc) - self.last_reset_time).total_seconds()
    
    def _check_latency_thresholds(self, latency_ms: float):
        """Check latency against thresholds and trigger alerts"""
        if latency_ms >= self.thresholds.latency_critical:
            self._create_alert(
                'latency_critical',
                'critical',
                f'Critical latency: {latency_ms:.1f}ms',
                {'latency_ms': latency_ms, 'threshold': self.thresholds.latency_critical}
            )
        elif latency_ms >= self.thresholds.latency_error:
            self._create_alert(
                'latency_error',
                'error',
                f'High latency: {latency_ms:.1f}ms',
                {'latency_ms': latency_ms, 'threshold': self.thresholds.latency_error}
            )
        elif latency_ms >= self.thresholds.latency_warning:
            self._create_alert(
                'latency_warning',
                'warning',
                f'Elevated latency: {latency_ms:.1f}ms',
                {'latency_ms': latency_ms, 'threshold': self.thresholds.latency_warning}
            )
    
    def _check_queue_depth_thresholds(self, depth: int):
        """Check queue depth against thresholds"""
        if depth >= self.thresholds.queue_depth_critical:
            self._create_alert(
                'queue_depth_critical',
                'critical',
                f'Critical queue depth: {depth}',
                {'queue_depth': depth, 'threshold': self.thresholds.queue_depth_critical}
            )
        elif depth >= self.thresholds.queue_depth_error:
            self._create_alert(
                'queue_depth_error',
                'error',
                f'High queue depth: {depth}',
                {'queue_depth': depth, 'threshold': self.thresholds.queue_depth_error}
            )
        elif depth >= self.thresholds.queue_depth_warning:
            self._create_alert(
                'queue_depth_warning',
                'warning',
                f'Elevated queue depth: {depth}',
                {'queue_depth': depth, 'threshold': self.thresholds.queue_depth_warning}
            )
    
    def _check_memory_thresholds(self, memory_mb: float):
        """Check memory usage against thresholds"""
        if memory_mb >= self.thresholds.memory_critical:
            self._create_alert(
                'memory_critical',
                'critical',
                f'Critical memory usage: {memory_mb:.1f}MB',
                {'memory_mb': memory_mb, 'threshold': self.thresholds.memory_critical}
            )
        elif memory_mb >= self.thresholds.memory_error:
            self._create_alert(
                'memory_error',
                'error',
                f'High memory usage: {memory_mb:.1f}MB',
                {'memory_mb': memory_mb, 'threshold': self.thresholds.memory_error}
            )
        elif memory_mb >= self.thresholds.memory_warning:
            self._create_alert(
                'memory_warning',
                'warning',
                f'Elevated memory usage: {memory_mb:.1f}MB',
                {'memory_mb': memory_mb, 'threshold': self.thresholds.memory_warning}
            )
    
    def _create_alert(self, alert_type: str, severity: str, message: str, data: Dict[str, Any]):
        """Create and manage performance alert"""
        alert = PerformanceAlert(
            timestamp=datetime.now(timezone.utc),
            alert_type=alert_type,
            severity=severity,
            message=message,
            data=data
        )
        
        # Add to active alerts
        self.active_alerts.append(alert)
        
        # Add to history
        self.alert_history.append(alert)
        
        # Maintain history size
        if len(self.alert_history) > self.max_alert_history:
            self.alert_history = self.alert_history[-self.max_alert_history:]
        
        # Log alert
        logger.warning(f"Performance Alert [{severity.upper()}]: {message}")
        
        # Invoke callback if provided
        if self.alert_callback:
            try:
                self.alert_callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def _summarize_alerts(self) -> Dict[str, int]:
        """Summarize alerts by type and severity"""
        summary = {'warning': 0, 'error': 0, 'critical': 0}
        
        for alert in self.active_alerts:
            if alert.severity in summary:
                summary[alert.severity] += 1
        
        return summary
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Started performance monitoring loop")
        
        try:
            while self.is_monitoring:
                # Periodic checks and cleanup
                await self._periodic_checks()
                
                # Wait before next cycle
                await asyncio.sleep(30)  # 30 second monitoring cycle
                
        except asyncio.CancelledError:
            logger.info("Performance monitoring loop cancelled")
        except Exception as e:
            logger.error(f"Performance monitoring loop error: {e}")
    
    async def _periodic_checks(self):
        """Perform periodic checks and cleanup"""
        try:
            # Auto-resolve old alerts (1 hour)
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
            
            for alert in self.active_alerts:
                if alert.timestamp < cutoff_time and not alert.resolved:
                    alert.resolved = True
                    logger.info(f"Auto-resolved alert: {alert.alert_type}")
            
            # Remove resolved alerts from active list
            self.active_alerts = [a for a in self.active_alerts if not a.resolved]
            
            # Log periodic status
            stats = self.get_performance_stats(force_refresh=True)
            logger.info(
                f"Performance Status: {stats['message_stats']['messages_per_second']:.1f} msg/s, "
                f"Avg Latency: {stats['latency_stats'].get('avg_ms', 0):.1f}ms, "
                f"Active Alerts: {len(self.active_alerts)}"
            )
            
        except Exception as e:
            logger.error(f"Periodic checks error: {e}")
    
    def acknowledge_alert(self, alert_type: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.active_alerts:
            if alert.alert_type == alert_type and not alert.acknowledged:
                alert.acknowledged = True
                logger.info(f"Acknowledged alert: {alert_type}")
                return True
        
        return False
    
    def resolve_alert(self, alert_type: str) -> bool:
        """Manually resolve an alert"""
        for alert in self.active_alerts:
            if alert.alert_type == alert_type:
                alert.resolved = True
                logger.info(f"Resolved alert: {alert_type}")
                return True
        
        return False
    
    def reset_metrics(self):
        """Reset all metrics and counters"""
        self.latency_history.clear()
        self.throughput_history.clear()
        self.error_history.clear()
        
        self.message_count = 0
        self.error_count = 0
        self.last_reset_time = datetime.now(timezone.utc)
        
        self.symbol_metrics.clear()
        self.stats_cache.clear()
        
        logger.info("Performance metrics reset")
    
    def get_active_alerts(self) -> List[PerformanceAlert]:
        """Get list of active alerts"""
        return [alert for alert in self.active_alerts if not alert.resolved]
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format"""
        stats = self.get_performance_stats(force_refresh=True)
        
        if format.lower() == 'json':
            import json
            return json.dumps(stats, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")