"""
Error Recovery System
Comprehensive error handling and recovery mechanisms for the Mikrobot trading system
Implements circuit breakers, retry policies, fallback strategies, and automatic recovery
"""

from typing import Dict, Any, Optional, List, Callable, Union
from datetime import datetime, timedelta
import asyncio
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import traceback
import json

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    """Available recovery actions"""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    EMERGENCY_STOP = "emergency_stop"
    RESTART_COMPONENT = "restart_component"
    NOTIFICATION = "notification"
    MANUAL_INTERVENTION = "manual_intervention"


@dataclass
class ErrorContext:
    """Error context information"""
    error_id: str
    timestamp: datetime
    component: str
    operation: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    stack_trace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RecoveryStrategy:
    """Recovery strategy configuration"""
    name: str
    actions: List[RecoveryAction]
    max_attempts: int = 3
    delay_seconds: float = 1.0
    exponential_backoff: bool = True
    timeout_seconds: float = 30.0
    fallback_handler: Optional[Callable] = None
    notification_handler: Optional[Callable] = None


class RetryPolicy:
    """Retry policy with exponential backoff"""
    
    def __init__(self, max_attempts: int = 3, initial_delay: float = 1.0, 
                 max_delay: float = 60.0, exponential_base: float = 2.0):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for specific attempt"""
        if attempt <= 0:
            return 0.0
        
        delay = self.initial_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)
    
    async def execute_with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with retry policy"""
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(operation):
                    return await operation(*args, **kwargs)
                else:
                    return operation(*args, **kwargs)
                    
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_attempts:
                    break
                
                delay = self.get_delay(attempt)
                logger.warning(f"Operation failed (attempt {attempt}/{self.max_attempts}), "
                             f"retrying in {delay:.1f}s: {str(e)}")
                
                await asyncio.sleep(delay)
        
        # All attempts failed
        raise last_exception


class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: float = 60.0, 
                 success_threshold: int = 3):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.success_threshold = success_threshold
        
        # State
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == 'CLOSED':
            return True
        elif self.state == 'OPEN':
            # Check if timeout has passed
            if (self.last_failure_time and 
                datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout_seconds)):
                self.state = 'HALF_OPEN'
                self.success_count = 0
                return True
            return False
        elif self.state == 'HALF_OPEN':
            return True
        
        return False
    
    def record_success(self):
        """Record successful operation"""
        if self.state == 'HALF_OPEN':
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info("Circuit breaker CLOSED after successful recovery")
        elif self.state == 'CLOSED':
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")
        elif self.state == 'HALF_OPEN':
            self.state = 'OPEN'
            logger.warning("Circuit breaker returned to OPEN state during recovery")


class ErrorRecoverySystem:
    """
    Comprehensive error recovery system
    
    Features:
    - Circuit breaker protection
    - Retry policies with exponential backoff
    - Fallback strategies
    - Error classification and routing
    - Recovery action orchestration
    - Error analytics and learning
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Error tracking
        self.error_history: List[ErrorContext] = []
        self.error_patterns: Dict[str, List[ErrorContext]] = {}
        
        # Recovery strategies by component
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        
        # Circuit breakers by component
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Retry policies by operation type
        self.retry_policies: Dict[str, RetryPolicy] = {}
        
        # Component health status
        self.component_health: Dict[str, Dict[str, Any]] = {}
        
        # Recovery metrics
        self.recovery_metrics = {
            'total_errors': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'circuit_breaker_trips': 0,
            'emergency_stops': 0,
            'manual_interventions': 0
        }
        
        # Initialize default strategies
        self._initialize_default_strategies()
        
        logger.info("Error Recovery System initialized")
    
    def _initialize_default_strategies(self):
        """Initialize default recovery strategies"""
        # MT5 Connection Recovery
        self.recovery_strategies['mt5_connection'] = RecoveryStrategy(
            name="MT5 Connection Recovery",
            actions=[RecoveryAction.RETRY, RecoveryAction.RESTART_COMPONENT, RecoveryAction.NOTIFICATION],
            max_attempts=3,
            delay_seconds=5.0,
            exponential_backoff=True
        )
        
        # Signal Processing Recovery
        self.recovery_strategies['signal_processing'] = RecoveryStrategy(
            name="Signal Processing Recovery",
            actions=[RecoveryAction.RETRY, RecoveryAction.FALLBACK],
            max_attempts=2,
            delay_seconds=1.0
        )
        
        # Trade Execution Recovery
        self.recovery_strategies['trade_execution'] = RecoveryStrategy(
            name="Trade Execution Recovery", 
            actions=[RecoveryAction.RETRY, RecoveryAction.EMERGENCY_STOP],
            max_attempts=3,
            delay_seconds=2.0
        )
        
        # Agent Communication Recovery
        self.recovery_strategies['agent_communication'] = RecoveryStrategy(
            name="Agent Communication Recovery",
            actions=[RecoveryAction.CIRCUIT_BREAK, RecoveryAction.FALLBACK],
            max_attempts=2,
            delay_seconds=1.0
        )
        
        # Default retry policies
        self.retry_policies['default'] = RetryPolicy(max_attempts=3, initial_delay=1.0)
        self.retry_policies['mt5_operation'] = RetryPolicy(max_attempts=5, initial_delay=2.0, max_delay=30.0)
        self.retry_policies['database_operation'] = RetryPolicy(max_attempts=3, initial_delay=0.5, max_delay=10.0)
    
    async def handle_error(self, error: Exception, component: str, operation: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle error with appropriate recovery strategy
        
        Returns:
            bool: True if recovery was successful, False otherwise
        """
        error_context = ErrorContext(
            error_id=f"{component}_{operation}_{datetime.utcnow().timestamp()}",
            timestamp=datetime.utcnow(),
            component=component,
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            severity=self._classify_error_severity(error, component),
            stack_trace=traceback.format_exc(),
            metadata=metadata or {}
        )
        
        # Log error
        self._log_error(error_context)
        
        # Update metrics
        self.recovery_metrics['total_errors'] += 1
        
        # Execute recovery strategy
        recovery_successful = await self._execute_recovery(error_context)
        
        if recovery_successful:
            self.recovery_metrics['successful_recoveries'] += 1
        else:
            self.recovery_metrics['failed_recoveries'] += 1
        
        return recovery_successful
    
    def _classify_error_severity(self, error: Exception, component: str) -> ErrorSeverity:
        """Classify error severity based on error type and component"""
        error_type = type(error).__name__
        
        # Critical errors
        if any(critical in error_type.lower() for critical in ['connection', 'authentication', 'authorization']):
            return ErrorSeverity.CRITICAL
        
        # High severity for trading components
        if component in ['trade_execution', 'mt5_connection'] and 'timeout' not in error_type.lower():
            return ErrorSeverity.HIGH
        
        # Medium severity for processing errors
        if any(medium in error_type.lower() for medium in ['validation', 'processing', 'timeout']):
            return ErrorSeverity.MEDIUM
        
        # Default to low severity
        return ErrorSeverity.LOW
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level"""
        self.error_history.append(error_context)
        
        # Keep only last 1000 errors
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
        
        # Group by error pattern
        pattern_key = f"{error_context.component}_{error_context.error_type}"
        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = []
        
        self.error_patterns[pattern_key].append(error_context)
        
        # Log with appropriate level
        log_message = f"Error in {error_context.component}.{error_context.operation}: {error_context.error_message}"
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_context.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_context.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    async def _execute_recovery(self, error_context: ErrorContext) -> bool:
        """Execute recovery strategy for error"""
        component = error_context.component
        
        # Get recovery strategy
        if component in self.recovery_strategies:
            strategy = self.recovery_strategies[component]
        else:
            strategy = self._get_default_strategy(error_context.severity)
        
        logger.info(f"Executing recovery strategy '{strategy.name}' for {component}")
        
        # Execute recovery actions
        for action in strategy.actions:
            try:
                success = await self._execute_recovery_action(action, error_context, strategy)
                if success:
                    logger.info(f"Recovery successful with action: {action.value}")
                    return True
                    
            except Exception as e:
                logger.error(f"Recovery action {action.value} failed: {str(e)}")
                continue
        
        # All recovery actions failed
        logger.error(f"All recovery actions failed for {component}")
        return False
    
    def _get_default_strategy(self, severity: ErrorSeverity) -> RecoveryStrategy:
        """Get default recovery strategy based on severity"""
        if severity == ErrorSeverity.CRITICAL:
            return RecoveryStrategy(
                name="Critical Error Recovery",
                actions=[RecoveryAction.EMERGENCY_STOP, RecoveryAction.MANUAL_INTERVENTION],
                max_attempts=1
            )
        elif severity == ErrorSeverity.HIGH:
            return RecoveryStrategy(
                name="High Severity Recovery", 
                actions=[RecoveryAction.RETRY, RecoveryAction.CIRCUIT_BREAK, RecoveryAction.NOTIFICATION],
                max_attempts=3
            )
        else:
            return RecoveryStrategy(
                name="Standard Recovery",
                actions=[RecoveryAction.RETRY, RecoveryAction.FALLBACK],
                max_attempts=2
            )
    
    async def _execute_recovery_action(self, action: RecoveryAction, 
                                     error_context: ErrorContext, 
                                     strategy: RecoveryStrategy) -> bool:
        """Execute specific recovery action"""
        component = error_context.component
        
        if action == RecoveryAction.RETRY:
            return await self._retry_operation(error_context, strategy)
            
        elif action == RecoveryAction.FALLBACK:
            return await self._execute_fallback(error_context, strategy)
            
        elif action == RecoveryAction.CIRCUIT_BREAK:
            return self._activate_circuit_breaker(component)
            
        elif action == RecoveryAction.EMERGENCY_STOP:
            return await self._emergency_stop(error_context)
            
        elif action == RecoveryAction.RESTART_COMPONENT:
            return await self._restart_component(component)
            
        elif action == RecoveryAction.NOTIFICATION:
            return await self._send_notification(error_context)
            
        elif action == RecoveryAction.MANUAL_INTERVENTION:
            return await self._request_manual_intervention(error_context)
        
        return False
    
    async def _retry_operation(self, error_context: ErrorContext, strategy: RecoveryStrategy) -> bool:
        """Retry the failed operation"""
        # This would need to be implemented with actual operation retry logic
        # For now, simulate retry with delay
        await asyncio.sleep(strategy.delay_seconds)
        
        # In real implementation, this would re-execute the original operation
        # For demonstration, we'll return success based on error severity
        return error_context.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]
    
    async def _execute_fallback(self, error_context: ErrorContext, strategy: RecoveryStrategy) -> bool:
        """Execute fallback strategy"""
        if strategy.fallback_handler:
            try:
                if asyncio.iscoroutinefunction(strategy.fallback_handler):
                    await strategy.fallback_handler(error_context)
                else:
                    strategy.fallback_handler(error_context)
                return True
            except Exception as e:
                logger.error(f"Fallback handler failed: {str(e)}")
                return False
        
        # Default fallback behavior
        logger.info(f"Executing default fallback for {error_context.component}")
        return True
    
    def _activate_circuit_breaker(self, component: str) -> bool:
        """Activate circuit breaker for component"""
        if component not in self.circuit_breakers:
            self.circuit_breakers[component] = CircuitBreaker()
        
        self.circuit_breakers[component].record_failure()
        self.recovery_metrics['circuit_breaker_trips'] += 1
        
        logger.warning(f"Circuit breaker activated for {component}")
        return True
    
    async def _emergency_stop(self, error_context: ErrorContext) -> bool:
        """Execute emergency stop"""
        self.recovery_metrics['emergency_stops'] += 1
        
        logger.critical(f"EMERGENCY STOP triggered by {error_context.component}: {error_context.error_message}")
        
        # In real implementation, this would stop all trading activities
        # For now, just log the emergency stop
        return True
    
    async def _restart_component(self, component: str) -> bool:
        """Restart component"""
        logger.info(f"Restarting component: {component}")
        
        # In real implementation, this would restart the specific component
        # For now, simulate restart with delay
        await asyncio.sleep(2.0)
        
        return True
    
    async def _send_notification(self, error_context: ErrorContext) -> bool:
        """Send error notification"""
        logger.info(f"Sending notification for error: {error_context.error_id}")
        
        # In real implementation, this would send emails, Slack messages, etc.
        return True
    
    async def _request_manual_intervention(self, error_context: ErrorContext) -> bool:
        """Request manual intervention"""
        self.recovery_metrics['manual_interventions'] += 1
        
        logger.critical(f"MANUAL INTERVENTION REQUIRED: {error_context.component} - {error_context.error_message}")
        
        # In real implementation, this would create tickets, send alerts, etc.
        return True
    
    def get_component_health(self, component: str) -> Dict[str, Any]:
        """Get health status for component"""
        if component not in self.component_health:
            self.component_health[component] = {
                'status': 'healthy',
                'error_count': 0,
                'last_error': None,
                'circuit_breaker_state': 'CLOSED'
            }
        
        health = self.component_health[component].copy()
        
        # Update circuit breaker state
        if component in self.circuit_breakers:
            health['circuit_breaker_state'] = self.circuit_breakers[component].state
        
        return health
    
    def get_error_analytics(self) -> Dict[str, Any]:
        """Get error analytics and patterns"""
        return {
            'metrics': self.recovery_metrics,
            'error_patterns': {
                pattern: len(errors) for pattern, errors in self.error_patterns.items()
            },
            'recent_errors': [asdict(error) for error in self.error_history[-10:]],
            'component_health': {
                component: self.get_component_health(component) 
                for component in self.recovery_strategies.keys()
            },
            'circuit_breaker_states': {
                component: breaker.state 
                for component, breaker in self.circuit_breakers.items()
            }
        }
    
    def register_recovery_strategy(self, component: str, strategy: RecoveryStrategy):
        """Register custom recovery strategy for component"""
        self.recovery_strategies[component] = strategy
        logger.info(f"Registered recovery strategy '{strategy.name}' for {component}")
    
    def register_retry_policy(self, operation_type: str, policy: RetryPolicy):
        """Register custom retry policy for operation type"""
        self.retry_policies[operation_type] = policy
        logger.info(f"Registered retry policy for {operation_type}")
    
    async def test_recovery_system(self) -> Dict[str, Any]:
        """Test recovery system with simulated errors"""
        test_results = []
        
        # Test different error scenarios
        test_scenarios = [
            ('mt5_connection', 'connect', ConnectionError("MT5 connection failed")),
            ('signal_processing', 'validate', ValueError("Invalid signal format")),
            ('trade_execution', 'place_order', TimeoutError("Order placement timeout")),
            ('agent_communication', 'send_message', RuntimeError("Agent not responding"))
        ]
        
        for component, operation, error in test_scenarios:
            logger.info(f"Testing recovery for {component}.{operation}")
            
            start_time = datetime.utcnow()
            success = await self.handle_error(error, component, operation, {'test': True})
            duration = (datetime.utcnow() - start_time).total_seconds()
            
            test_results.append({
                'component': component,
                'operation': operation,
                'error_type': type(error).__name__,
                'recovery_successful': success,
                'duration_seconds': duration
            })
        
        return {
            'test_results': test_results,
            'system_metrics': self.recovery_metrics,
            'timestamp': datetime.utcnow().isoformat()
        }