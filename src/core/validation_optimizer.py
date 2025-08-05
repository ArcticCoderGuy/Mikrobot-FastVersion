from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Validation Optimizer
High-performance validation coordination between ProductOwner and U-Cell #1
Implements <100ms total validation with parallel processing and caching
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
import time
import hashlib
from dataclasses import dataclass
from enum import Enum

from .mcp_controller import MCPMessage, MessageType
from .u_cells.signal_validation import SignalValidationCell
from .u_cells import CellInput, CellOutput

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Comprehensive validation result"""
    trace_id: str
    strategic_approved: bool
    technical_valid: bool
    overall_approved: bool
    strategic_confidence: float
    technical_confidence: float
    combined_confidence: float
    validation_latency_ms: float
    strategic_latency_ms: float
    technical_latency_ms: float
    cache_hit: bool
    reasons: List[str]
    details: Dict[str, Any]
    timestamp: datetime


class ValidationOptimizer:
    """
    High-performance validation coordinator for <100ms total validation
    
    Features:
    - Parallel strategic and technical validation
    - Smart caching with pattern recognition
    - Performance monitoring and optimization
    - Dynamic threshold adjustment
    - Circuit breaker protection
    """
    
    def __init__(self, mcp_controller, product_owner_agent):
        self.mcp_controller = mcp_controller
        self.product_owner = product_owner_agent
        
        # Direct U-Cell integration for performance
        self.signal_validation_cell = SignalValidationCell()
        
        # Performance targets
        self.performance_targets = {
            'total_validation_ms': 100.0,
            'strategic_validation_ms': 50.0,
            'technical_validation_ms': 50.0,
            'parallel_overhead_ms': 10.0
        }
        
        # Validation cache
        self.validation_cache = {}
        self.cache_ttl_seconds = 300  # 5 minutes
        self.cache_hit_count = 0
        self.cache_miss_count = 0
        
        # Performance metrics
        self.validation_metrics = {
            'total_validations': 0,
            'sub_100ms_validations': 0,
            'parallel_validations': 0,
            'cache_hits': 0,
            'performance_target_met_rate': 0.0,
            'avg_validation_latency_ms': 0.0,
            'avg_strategic_latency_ms': 0.0,
            'avg_technical_latency_ms': 0.0
        }
        
        # Performance history for trend analysis
        self.validation_times = []
        self.strategic_times = []
        self.technical_times = []
        
        # Circuit breaker for performance protection
        self.circuit_breaker = {
            'failure_threshold': 5,
            'consecutive_failures': 0,
            'last_failure_time': None,
            'recovery_timeout_seconds': 60,
            'is_open': False
        }
    
    async def validate_signal_optimized(self, signal_data: Dict[str, Any], trace_id: str) -> ValidationResult:
        """
        Optimized signal validation with <100ms target
        
        Process:
        1. Check validation cache first
        2. Parallel strategic and technical validation
        3. Combine results with confidence scoring
        4. Cache successful validations
        5. Update performance metrics
        """
        validation_start = time.perf_counter()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(signal_data)
            cached_result = self._get_cached_validation(cache_key)
            
            if cached_result:
                self.cache_hit_count += 1
                self.validation_metrics['cache_hits'] += 1
                logger.debug(f"Cache hit for validation {trace_id}")
                
                # Update cache hit result with current trace_id
                cached_result.trace_id = trace_id
                cached_result.cache_hit = True
                cached_result.validation_latency_ms = 2.0
                
                return cached_result
            
            self.cache_miss_count += 1
            
            # Check circuit breaker
            if self._is_circuit_breaker_open():
                return self._create_circuit_breaker_result(trace_id)
            
            # Parallel validation execution
            strategic_task = asyncio.create_task(
                self._strategic_validation_optimized(signal_data, trace_id)
            )
            technical_task = asyncio.create_task(
                self._technical_validation_direct(signal_data, trace_id)
            )
            
            # Execute validations in parallel with timeout
            try:
                strategic_result, technical_result = await asyncio.wait_for(
                    asyncio.gather(strategic_task, technical_task, return_exceptions=True),
                    timeout=0.09  # 90ms timeout
                )
                
                # Handle exceptions from parallel execution
                if isinstance(strategic_result, Exception):
                    logger.error(f"Strategic validation error for {trace_id}: {strategic_result}")
                    strategic_result = self._create_fallback_strategic_result(signal_data)
                
                if isinstance(technical_result, Exception):
                    logger.error(f"Technical validation error for {trace_id}: {technical_result}")
                    technical_result = self._create_fallback_technical_result(signal_data)
                
            except asyncio.TimeoutError:
                logger.warning(f"Parallel validation timeout for {trace_id}")
                self._record_circuit_breaker_failure()
                return self._create_timeout_result(trace_id)
            
            # Combine validation results
            validation_result = self._combine_validation_results(
                trace_id, strategic_result, technical_result, validation_start
            )
            
            # Cache successful validations
            if validation_result.overall_approved or validation_result.combined_confidence > 0.5:
                self._cache_validation_result(cache_key, validation_result)
            
            # Update performance metrics
            self._update_performance_metrics(validation_result)
            
            # Reset circuit breaker on success
            if validation_result.validation_latency_ms < 100.0:
                self._reset_circuit_breaker()
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Validation optimizer error for {trace_id}: {str(e)}")
            self._record_circuit_breaker_failure()
            return self._create_error_result(trace_id, str(e))
    
    async def _strategic_validation_optimized(self, signal_data: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """Optimized strategic validation with <50ms target"""
        strategic_start = time.perf_counter()
        
        try:
            # Create high-priority strategic evaluation message
            evaluation_message = MCPMessage(
                id=f"strategic_fast_{trace_id}",
                method="evaluate_signal",
                params={
                    'signal_data': signal_data,
                    'trace_id': trace_id,
                    'fast_mode': True,  # Enable fast-track processing
                    'skip_deep_analysis': True  # Skip heavy analysis for speed
                },
                recipient='product_owner'
            )
            
            # Route with critical priority and short timeout
            response = await asyncio.wait_for(
                self.mcp_controller.route_message(evaluation_message, priority='critical'),
                timeout=0.045  # 45ms timeout
            )
            
            strategic_latency = (time.perf_counter() - strategic_start) * 1000
            self.strategic_times.append(strategic_latency)
            
            if response and response.method == "signal_evaluation_result":
                evaluation = response.params.get('evaluation', {})
                evaluation['latency_ms'] = strategic_latency
                return evaluation
            else:
                return self._create_fallback_strategic_result(signal_data)
                
        except asyncio.TimeoutError:
            strategic_latency = (time.perf_counter() - strategic_start) * 1000
            logger.warning(f"Strategic validation timeout ({strategic_latency:.2f}ms) for {trace_id}")
            return self._create_fallback_strategic_result(signal_data)
        except Exception as e:
            strategic_latency = (time.perf_counter() - strategic_start) * 1000
            logger.error(f"Strategic validation error ({strategic_latency:.2f}ms) for {trace_id}: {str(e)}")
            return self._create_fallback_strategic_result(signal_data)
    
    async def _technical_validation_direct(self, signal_data: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """Direct technical validation bypassing MCP for performance"""
        technical_start = time.perf_counter()
        
        try:
            # Create cell input for direct validation
            cell_input = CellInput(
                timestamp=datetime.utcnow(),
                data=signal_data,
                trace_id=trace_id
            )
            
            # Direct validation through U-Cell (no MCP overhead)
            if not self.signal_validation_cell.validate_input(cell_input):
                return {
                    'valid': False,
                    'reason': 'Invalid input structure',
                    'confidence': 0.0,
                    'latency_ms': (time.perf_counter() - technical_start) * 1000
                }
            
            # Process validation directly
            validation_output = self.signal_validation_cell.process(cell_input)
            technical_latency = (time.perf_counter() - technical_start) * 1000
            self.technical_times.append(technical_latency)
            
            if validation_output.status == 'success':
                validation_data = validation_output.data.get('validation', {})
                return {
                    'valid': validation_data.get('valid', False),
                    'confidence': validation_data.get('confidence', 0.0),
                    'reason': 'Technical validation passed',
                    'validation_details': validation_data,
                    'latency_ms': technical_latency
                }
            else:
                return {
                    'valid': False,
                    'reason': validation_output.errors[0] if validation_output.errors else 'Technical validation failed',
                    'confidence': 0.0,
                    'latency_ms': technical_latency
                }
                
        except Exception as e:
            technical_latency = (time.perf_counter() - technical_start) * 1000
            logger.error(f"Direct technical validation error ({technical_latency:.2f}ms) for {trace_id}: {str(e)}")
            return {
                'valid': False,
                'reason': f'Technical validation error: {str(e)}',
                'confidence': 0.0,
                'latency_ms': technical_latency
            }
    
    def _combine_validation_results(self, trace_id: str, strategic_result: Dict[str, Any], 
                                  technical_result: Dict[str, Any], validation_start: float) -> ValidationResult:
        """Combine strategic and technical validation results"""
        
        strategic_approved = strategic_result.get('approved', False)
        strategic_confidence = strategic_result.get('confidence', 0.0)
        strategic_latency = strategic_result.get('latency_ms', 50.0)
        
        technical_valid = technical_result.get('valid', False)
        technical_confidence = technical_result.get('confidence', 0.0)
        technical_latency = technical_result.get('latency_ms', 50.0)
        
        # Combined decision logic
        overall_approved = strategic_approved and technical_valid
        
        # Combined confidence scoring
        if overall_approved:
            # Both approved: weighted average with bias towards strategic
            combined_confidence = (strategic_confidence * 0.6 + technical_confidence * 0.4)
        else:
            # One or both rejected: take minimum with penalty
            combined_confidence = min(strategic_confidence, technical_confidence) * 0.5
        
        # Calculate total validation latency
        total_latency = (time.perf_counter() - validation_start) * 1000
        
        # Collect reasons
        reasons = []
        if not strategic_approved:
            reasons.extend(strategic_result.get('reasons', ['Strategic validation failed']))
        if not technical_valid:
            reasons.append(technical_result.get('reason', 'Technical validation failed'))
        if overall_approved:
            reasons.append('Both strategic and technical validation passed')
        
        return ValidationResult(
            trace_id=trace_id,
            strategic_approved=strategic_approved,
            technical_valid=technical_valid,
            overall_approved=overall_approved,
            strategic_confidence=strategic_confidence,
            technical_confidence=technical_confidence,
            combined_confidence=combined_confidence,
            validation_latency_ms=round(total_latency, 2),
            strategic_latency_ms=round(strategic_latency, 2),
            technical_latency_ms=round(technical_latency, 2),
            cache_hit=False,
            reasons=reasons,
            details={
                'strategic_result': strategic_result,
                'technical_result': technical_result
            },
            timestamp=datetime.utcnow()
        )
    
    def _generate_cache_key(self, signal_data: Dict[str, Any]) -> str:
        """Generate cache key for validation caching"""
        # Create hash based on key signal characteristics
        key_data = {
            'symbol': signal_data.get('symbol', ''),
            'pattern_type': signal_data.get('pattern_type', ''),
            'direction': signal_data.get('direction', ''),
            'timeframe': signal_data.get('timeframe', ''),
            'price_level': str(signal_data.get('price_levels', {}).get('current_price', 0))[:8]
        }
        
        key_string = '_'.join(f"{k}:{v}" for k, v in key_data.items())
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def _get_cached_validation(self, cache_key: str) -> Optional[ValidationResult]:
        """Get cached validation result if still valid"""
        if cache_key in self.validation_cache:
            cached_entry = self.validation_cache[cache_key]
            cache_age = (datetime.utcnow() - cached_entry['timestamp']).total_seconds()
            
            if cache_age < self.cache_ttl_seconds:
                return cached_entry['result']
            else:
                # Remove expired entry
                del self.validation_cache[cache_key]
        
        return None
    
    def _cache_validation_result(self, cache_key: str, validation_result: ValidationResult):
        """Cache validation result for future use"""
        self.validation_cache[cache_key] = {
            'timestamp': datetime.utcnow(),
            'result': validation_result
        }
        
        # Cleanup old cache entries (keep last 1000)
        if len(self.validation_cache) > 1000:
            oldest_key = min(self.validation_cache.keys(), 
                           key=lambda k: self.validation_cache[k]['timestamp'])
            del self.validation_cache[oldest_key]
    
    def _update_performance_metrics(self, validation_result: ValidationResult):
        """Update performance metrics"""
        self.validation_metrics['total_validations'] += 1
        
        # Track sub-100ms performance
        if validation_result.validation_latency_ms < 100.0:
            self.validation_metrics['sub_100ms_validations'] += 1
        
        # Update average latencies
        total_validations = self.validation_metrics['total_validations']
        
        # Overall validation latency
        current_avg = self.validation_metrics['avg_validation_latency_ms']
        self.validation_metrics['avg_validation_latency_ms'] = (
            (current_avg * (total_validations - 1)) + validation_result.validation_latency_ms
        ) / total_validations
        
        # Strategic validation latency
        current_strategic_avg = self.validation_metrics['avg_strategic_latency_ms']
        self.validation_metrics['avg_strategic_latency_ms'] = (
            (current_strategic_avg * (total_validations - 1)) + validation_result.strategic_latency_ms
        ) / total_validations
        
        # Technical validation latency
        current_technical_avg = self.validation_metrics['avg_technical_latency_ms']
        self.validation_metrics['avg_technical_latency_ms'] = (
            (current_technical_avg * (total_validations - 1)) + validation_result.technical_latency_ms
        ) / total_validations
        
        # Performance target achievement rate
        self.validation_metrics['performance_target_met_rate'] = (
            self.validation_metrics['sub_100ms_validations'] / total_validations
        )
        
        # Store timing for trend analysis
        self.validation_times.append(validation_result.validation_latency_ms)
        if len(self.validation_times) > 1000:  # Keep last 1000
            self.validation_times = self.validation_times[-1000:]
    
    def _create_fallback_strategic_result(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback strategic result when primary fails"""
        return {
            'approved': False,
            'confidence': 0.1,
            'reasons': ['Strategic validation fallback - service unavailable'],
            'fallback': True,
            'latency_ms': 50.0
        }
    
    def _create_fallback_technical_result(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback technical result when primary fails"""
        return {
            'valid': False,
            'confidence': 0.1,
            'reason': 'Technical validation fallback - service unavailable',
            'fallback': True,
            'latency_ms': 50.0
        }
    
    def _create_timeout_result(self, trace_id: str) -> ValidationResult:
        """Create result for validation timeout"""
        return ValidationResult(
            trace_id=trace_id,
            strategic_approved=False,
            technical_valid=False,
            overall_approved=False,
            strategic_confidence=0.0,
            technical_confidence=0.0,
            combined_confidence=0.0,
            validation_latency_ms=100.0,
            strategic_latency_ms=50.0,
            technical_latency_ms=50.0,
            cache_hit=False,
            reasons=['Validation timeout'],
            details={'timeout': True},
            timestamp=datetime.utcnow()
        )
    
    def _create_error_result(self, trace_id: str, error_message: str) -> ValidationResult:
        """Create result for validation error"""
        return ValidationResult(
            trace_id=trace_id,
            strategic_approved=False,
            technical_valid=False,
            overall_approved=False,
            strategic_confidence=0.0,
            technical_confidence=0.0,
            combined_confidence=0.0,
            validation_latency_ms=100.0,
            strategic_latency_ms=50.0,
            technical_latency_ms=50.0,
            cache_hit=False,
            reasons=[f'Validation error: {error_message}'],
            details={'error': error_message},
            timestamp=datetime.utcnow()
        )
    
    def _create_circuit_breaker_result(self, trace_id: str) -> ValidationResult:
        """Create result when circuit breaker is open"""
        return ValidationResult(
            trace_id=trace_id,
            strategic_approved=False,
            technical_valid=False,
            overall_approved=False,
            strategic_confidence=0.0,
            technical_confidence=0.0,
            combined_confidence=0.0,
            validation_latency_ms=1.0,
            strategic_latency_ms=0.5,
            technical_latency_ms=0.5,
            cache_hit=False,
            reasons=['Circuit breaker open - validation service degraded'],
            details={'circuit_breaker_open': True},
            timestamp=datetime.utcnow()
        )
    
    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open"""
        if not self.circuit_breaker['is_open']:
            return False
        
        # Check if enough time has passed for recovery
        if self.circuit_breaker['last_failure_time']:
            time_since_failure = (datetime.utcnow() - self.circuit_breaker['last_failure_time']).total_seconds()
            if time_since_failure > self.circuit_breaker['recovery_timeout_seconds']:
                self._reset_circuit_breaker()
                return False
        
        return True
    
    def _record_circuit_breaker_failure(self):
        """Record circuit breaker failure"""
        self.circuit_breaker['consecutive_failures'] += 1
        self.circuit_breaker['last_failure_time'] = datetime.utcnow()
        
        if self.circuit_breaker['consecutive_failures'] >= self.circuit_breaker['failure_threshold']:
            self.circuit_breaker['is_open'] = True
            logger.warning("Circuit breaker opened due to consecutive validation failures")
    
    def _reset_circuit_breaker(self):
        """Reset circuit breaker on success"""
        self.circuit_breaker['consecutive_failures'] = 0
        self.circuit_breaker['is_open'] = False
        self.circuit_breaker['last_failure_time'] = None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        cache_hit_rate = 0.0
        total_requests = self.cache_hit_count + self.cache_miss_count
        if total_requests > 0:
            cache_hit_rate = self.cache_hit_count / total_requests
        
        performance_stats = {}
        if self.validation_times:
            performance_stats = {
                'min_validation_ms': round(min(self.validation_times), 2),
                'max_validation_ms': round(max(self.validation_times), 2),
                'median_validation_ms': round(self._calculate_median(self.validation_times), 2),
                'p95_validation_ms': round(self._calculate_percentile(self.validation_times, 95), 2),
                'p99_validation_ms': round(self._calculate_percentile(self.validation_times, 99), 2)
            }
        
        return {
            'validation_metrics': self.validation_metrics,
            'performance_targets': self.performance_targets,
            'performance_stats': performance_stats,
            'cache_metrics': {
                'cache_size': len(self.validation_cache),
                'cache_hit_rate': round(cache_hit_rate, 3),
                'cache_hits': self.cache_hit_count,
                'cache_misses': self.cache_miss_count
            },
            'circuit_breaker_status': self.circuit_breaker,
            'recent_validation_times': self.validation_times[-10:] if self.validation_times else []
        }
    
    def _calculate_median(self, values: List[float]) -> float:
        """Calculate median of values"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            return sorted_values[n//2]
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100.0) * (len(sorted_values) - 1))
        return sorted_values[index]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        metrics = self.get_performance_metrics()
        
        # Performance grade calculation
        target_met_rate = self.validation_metrics['performance_target_met_rate']
        if target_met_rate >= 0.95:
            performance_grade = 'A+'
        elif target_met_rate >= 0.90:
            performance_grade = 'A'
        elif target_met_rate >= 0.80:
            performance_grade = 'B'
        elif target_met_rate >= 0.70:
            performance_grade = 'C'
        elif target_met_rate >= 0.60:
            performance_grade = 'D'
        else:
            performance_grade = 'F'
        
        # Optimization recommendations
        recommendations = []
        
        avg_validation = self.validation_metrics['avg_validation_latency_ms']
        if avg_validation > 100:
            recommendations.append(f"Average validation time {avg_validation:.1f}ms exceeds 100ms target")
        
        avg_strategic = self.validation_metrics['avg_strategic_latency_ms']
        if avg_strategic > 50:
            recommendations.append(f"Strategic validation averaging {avg_strategic:.1f}ms - optimize ProductOwner processing")
        
        avg_technical = self.validation_metrics['avg_technical_latency_ms']
        if avg_technical > 50:
            recommendations.append(f"Technical validation averaging {avg_technical:.1f}ms - optimize U-Cell processing")
        
        cache_hit_rate = metrics['cache_metrics']['cache_hit_rate']
        if cache_hit_rate < 0.3:
            recommendations.append(f"Low cache hit rate {cache_hit_rate:.1%} - consider pattern similarity improvements")
        
        if self.circuit_breaker['consecutive_failures'] > 0:
            recommendations.append("Recent validation failures detected - investigate system stability")
        
        return {
            'performance_grade': performance_grade,
            'target_achievement_rate': round(target_met_rate, 3),
            'recommendations': recommendations,
            'detailed_metrics': metrics,
            'system_health': {
                'circuit_breaker_healthy': not self.circuit_breaker['is_open'],
                'cache_operational': len(self.validation_cache) > 0,
                'performance_stable': avg_validation < 120  # 20% tolerance
            }
        }