#!/usr/bin/env python3
"""
Performance Monitor
Tracks system performance metrics and optimization opportunities
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    latency_ms: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    cache_hit_rate: float = 0.0
    connection_pool_usage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """System performance monitoring and optimization"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.operation_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Performance thresholds
        self.thresholds = {
            'max_latency_ms': 1000,
            'max_cpu_usage': 80.0,
            'max_memory_usage': 80.0,
            'min_cache_hit_rate': 70.0
        }
        
        # Real-time monitoring
        self.is_monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
    async def initialize(self) -> bool:
        """Initialize performance monitor"""
        return True
    
    def record_operation_time(self, operation: str, duration_ms: float):
        """Record operation execution time"""
        self.operation_times[operation].append(duration_ms)
    
    def get_operation_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for specific operation"""
        times = list(self.operation_times[operation])
        if not times:
            return {'count': 0, 'avg': 0.0, 'min': 0.0, 'max': 0.0}
        
        return {
            'count': len(times),
            'avg': sum(times) / len(times),
            'min': min(times),
            'max': max(times)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        if not self.metrics_history:
            return {'status': 'no_data'}
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements
        
        avg_latency = sum(m.latency_ms for m in recent_metrics) / len(recent_metrics)
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        
        # Performance status
        status = 'optimal'
        if avg_latency > self.thresholds['max_latency_ms']:
            status = 'degraded'
        elif avg_cpu > self.thresholds['max_cpu_usage']:
            status = 'high_cpu'
        elif avg_memory > self.thresholds['max_memory_usage']:
            status = 'high_memory'
        
        return {
            'status': status,
            'avg_latency_ms': round(avg_latency, 2),
            'avg_cpu_usage': round(avg_cpu, 2),
            'avg_memory_usage': round(avg_memory, 2),
            'total_operations': sum(len(times) for times in self.operation_times.values()),
            'operation_stats': {op: self.get_operation_stats(op) for op in self.operation_times.keys()}
        }
