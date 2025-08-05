from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MCP Controller
Model Context Protocol controller for agent communication and coordination
"""

from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from datetime import datetime, timedelta
import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """MCP message types"""
    INITIALIZE = "initialize"
    REQUEST = "request"
    RESPONSE = "response" 
    NOTIFICATION = "notification"
    ERROR = "error"


class AgentRole(Enum):
    """Agent roles in the system"""
    SIGNAL_VALIDATOR = "signal_validator"
    ML_ANALYST = "ml_analyst"
    RISK_MANAGER = "risk_manager"
    TRADE_EXECUTOR = "trade_executor"
    MONITOR = "monitor"
    ORCHESTRATOR = "orchestrator"
    HANSEI_REFLECTOR = "hansei_reflector"
    PRODUCT_OWNER = "product_owner"
    SPECIALIST = "specialist"  # Added for MT5 Expert Agent


@dataclass
class MCPMessage:
    """MCP protocol message"""
    id: str
    method: str
    params: Dict[str, Any]
    type: MessageType = MessageType.REQUEST
    timestamp: datetime = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create from dictionary"""
        data['type'] = MessageType(data['type'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class MCPAgent(ABC):
    """Base MCP Agent interface"""
    
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        self.is_active = True
        self.controller: Optional['MCPController'] = None
        
        # Agent metrics
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'average_response_time': 0.0
        }
    
    @abstractmethod
    async def handle_message(self, message: MCPMessage) -> Optional[MCPMessage]:
        """Handle incoming MCP message"""
        pass
    
    async def send_message(self, method: str, params: Dict[str, Any], 
                          recipient: Optional[str] = None) -> Optional[MCPMessage]:
        """Send message through controller"""
        if not self.controller:
            logger.error(f"Agent {self.agent_id} has no controller")
            return None
        
        message = MCPMessage(
            id=f"{self.agent_id}_{datetime.utcnow().timestamp()}",
            method=method,
            params=params,
            sender=self.agent_id,
            recipient=recipient
        )
        
        self.metrics['messages_sent'] += 1
        return await self.controller.route_message(message)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics"""
        return {
            'agent_id': self.agent_id,
            'role': self.role.value,
            'is_active': self.is_active,
            **self.metrics
        }


class MCPController:
    """
    Enhanced MCP Controller with deterministic processing pipeline
    Implements ProductOwner -> MCPController -> U-Cells orchestration
    Features: Event sourcing, circuit breakers, priority queues, state management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.agents: Dict[str, MCPAgent] = {}
        self.message_handlers: Dict[str, Callable] = {}
        
        # Priority queue system
        self.priority_queues = {
            'critical': asyncio.Queue(),
            'high': asyncio.Queue(), 
            'normal': asyncio.Queue(),
            'low': asyncio.Queue()
        }
        
        self.is_running = False
        
        # Enhanced communication metrics
        self.metrics = {
            'total_messages': 0,
            'successful_routes': 0,
            'failed_routes': 0,
            'average_latency': 0.0,
            'active_agents': 0,
            'circuit_breaker_trips': 0,
            'priority_queue_sizes': {},
            'event_store_size': 0
        }
        
        # Context storage for cross-agent communication
        self.shared_context: Dict[str, Any] = {}
        
        # Event sourcing for decision replay
        self.event_store: List[Dict[str, Any]] = []
        
        # Circuit breaker state for each agent
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Agent health monitoring
        self.agent_health: Dict[str, Dict[str, Any]] = {}
        
        # Pipeline state management
        self.pipeline_state = {
            'active_pipelines': {},
            'completed_pipelines': [],
            'failed_pipelines': [],
            'pipeline_metrics': defaultdict(int)
        }
        
        # Initialize built-in handlers
        self._register_handlers()
    
    def register_agent(self, agent: MCPAgent):
        """Register an agent with the controller"""
        agent.controller = self
        self.agents[agent.agent_id] = agent
        self.metrics['active_agents'] = len([a for a in self.agents.values() if a.is_active])
        
        # Initialize circuit breaker for agent
        self.circuit_breakers[agent.agent_id] = {
            'state': 'CLOSED',  # CLOSED, OPEN, HALF_OPEN
            'failure_count': 0,
            'failure_threshold': 5,
            'recovery_timeout': 30,  # seconds
            'last_failure_time': None,
            'success_count': 0
        }
        
        # Initialize health monitoring
        self.agent_health[agent.agent_id] = {
            'status': 'healthy',
            'last_ping': datetime.utcnow(),
            'response_times': [],
            'error_rate': 0.0,
            'availability': 1.0
        }
        
        logger.info(f"Registered agent: {agent.agent_id} ({agent.role.value})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.metrics['active_agents'] = len([a for a in self.agents.values() if a.is_active])
            logger.info(f"Unregistered agent: {agent_id}")
    
    async def route_message(self, message: MCPMessage, priority: str = 'normal') -> Optional[MCPMessage]:
        """Route message with priority handling and circuit breaker protection"""
        self.metrics['total_messages'] += 1
        start_time = datetime.utcnow()
        
        # Add to priority queue
        if priority in self.priority_queues:
            await self.priority_queues[priority].put((message, start_time))
        else:
            await self.priority_queues['normal'].put((message, start_time))
        
        # Process from queue
        return await self._process_priority_queues()
    
    async def _process_priority_queues(self) -> Optional[MCPMessage]:
        """Process messages from priority queues"""
        # Process in priority order
        for priority in ['critical', 'high', 'normal', 'low']:
            queue = self.priority_queues[priority]
            
            if not queue.empty():
                message, start_time = await queue.get()
                return await self._route_message_internal(message, start_time)
        
        return None
    
    async def _route_message_internal(self, message: MCPMessage, start_time: datetime) -> Optional[MCPMessage]:
        """Internal message routing with circuit breaker and event sourcing"""
        try:
            # Log event for replay capability
            self._log_event('message_received', {
                'message_id': message.id,
                'method': message.method,
                'sender': message.sender,
                'recipient': message.recipient,
                'timestamp': start_time.isoformat()
            })
            
            # Handle built-in methods
            if message.method in self.message_handlers:
                response = await self.message_handlers[message.method](message)
                self.metrics['successful_routes'] += 1
                self._log_event('message_handled', {'message_id': message.id, 'handler': 'built_in'})
                return response
            
            # Route to specific agent with circuit breaker
            if message.recipient and message.recipient in self.agents:
                if not self._is_circuit_breaker_open(message.recipient):
                    agent = self.agents[message.recipient]
                    if agent.is_active:
                        try:
                            agent.metrics['messages_received'] += 1
                            response = await asyncio.wait_for(
                                agent.handle_message(message), 
                                timeout=30.0  # 30 second timeout
                            )
                            
                            # Record successful response
                            self._record_agent_success(message.recipient)
                            self.metrics['successful_routes'] += 1
                            
                            self._log_event('message_routed', {
                                'message_id': message.id, 
                                'recipient': message.recipient,
                                'status': 'success'
                            })
                            
                            return response
                            
                        except asyncio.TimeoutError:
                            self._record_agent_failure(message.recipient, 'timeout')
                            raise Exception(f"Agent {message.recipient} timeout")
                        except Exception as e:
                            self._record_agent_failure(message.recipient, str(e))
                            raise
                    else:
                        raise Exception(f"Agent {message.recipient} is not active")
                else:
                    raise Exception(f"Circuit breaker OPEN for agent {message.recipient}")
            
            # Broadcast to all agents of specific role
            if hasattr(AgentRole, message.method.upper()):
                role = AgentRole(message.method.lower())
                responses = []
                
                for agent in self.agents.values():
                    if (agent.role == role and agent.is_active and 
                        not self._is_circuit_breaker_open(agent.agent_id)):
                        
                        try:
                            agent.metrics['messages_received'] += 1
                            response = await asyncio.wait_for(
                                agent.handle_message(message),
                                timeout=30.0
                            )
                            if response:
                                responses.append(response)
                                self._record_agent_success(agent.agent_id)
                        except Exception as e:
                            self._record_agent_failure(agent.agent_id, str(e))
                            logger.warning(f"Agent {agent.agent_id} failed: {str(e)}")
                
                if responses:
                    self.metrics['successful_routes'] += 1
                    return responses[0]  # Return first response
            
            # No handler found
            self.metrics['failed_routes'] += 1
            raise Exception(f"No handler for method: {message.method}")
            
        except Exception as e:
            logger.error(f"Message routing error: {str(e)}")
            self.metrics['failed_routes'] += 1
            
            self._log_event('message_failed', {
                'message_id': message.id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return MCPMessage(
                id=f"error_{datetime.utcnow().timestamp()}",
                method="error",
                params={'error': str(e), 'original_message': message.to_dict()},
                type=MessageType.ERROR
            )
        
        finally:
            # Update latency metrics
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            current_avg = self.metrics['average_latency']
            total = self.metrics['total_messages']
            if total > 0:
                self.metrics['average_latency'] = ((current_avg * (total - 1)) + latency) / total
    
    def _register_handlers(self):
        """Register built-in message handlers"""
        self.message_handlers.update({
            'ping': self._handle_ping,
            'get_agents': self._handle_get_agents,
            'get_metrics': self._handle_get_metrics,
            'get_context': self._handle_get_context,
            'set_context': self._handle_set_context,
            'broadcast': self._handle_broadcast,
            'health_check': self._handle_health_check,
            'start_pipeline': self._handle_start_pipeline,
            'pipeline_status': self._handle_pipeline_status,
            'reset_circuit_breaker': self._handle_reset_circuit_breaker,
            'get_event_history': self._handle_get_event_history,
            'emergency_shutdown': self._handle_emergency_shutdown
        })
    
    async def _handle_ping(self, message: MCPMessage) -> MCPMessage:
        """Handle ping message"""
        return MCPMessage(
            id=f"pong_{message.id}",
            method="pong",
            params={'timestamp': datetime.utcnow().isoformat()},
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _handle_get_agents(self, message: MCPMessage) -> MCPMessage:
        """Get list of registered agents"""
        agents_info = [agent.get_metrics() for agent in self.agents.values()]
        
        return MCPMessage(
            id=f"agents_{message.id}",
            method="agents_list",
            params={'agents': agents_info},
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _handle_get_metrics(self, message: MCPMessage) -> MCPMessage:
        """Get controller metrics"""
        return MCPMessage(
            id=f"metrics_{message.id}",
            method="metrics",
            params={'controller_metrics': self.metrics},
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _handle_get_context(self, message: MCPMessage) -> MCPMessage:
        """Get shared context"""
        key = message.params.get('key')
        if key:
            value = self.shared_context.get(key)
        else:
            value = self.shared_context
        
        return MCPMessage(
            id=f"context_{message.id}",
            method="context_value",
            params={'key': key, 'value': value},
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _handle_set_context(self, message: MCPMessage) -> MCPMessage:
        """Set shared context"""
        key = message.params.get('key')
        value = message.params.get('value')
        
        if key:
            self.shared_context[key] = value
        
        return MCPMessage(
            id=f"context_set_{message.id}",
            method="context_updated",
            params={'key': key, 'success': True},
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _handle_broadcast(self, message: MCPMessage) -> MCPMessage:
        """Broadcast message to all active agents"""
        broadcast_message = MCPMessage(
            id=f"broadcast_{datetime.utcnow().timestamp()}",
            method=message.params.get('method', 'notification'),
            params=message.params.get('params', {}),
            type=MessageType.NOTIFICATION
        )
        
        responses = []
        for agent in self.agents.values():
            if agent.is_active:
                try:
                    response = await agent.handle_message(broadcast_message)
                    if response:
                        responses.append(response.to_dict())
                except Exception as e:
                    logger.error(f"Broadcast error to {agent.agent_id}: {str(e)}")
        
        return MCPMessage(
            id=f"broadcast_result_{message.id}",
            method="broadcast_complete",
            params={'responses': responses, 'agent_count': len(responses)},
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _handle_health_check(self, message: MCPMessage) -> MCPMessage:
        """Health check for all agents"""
        health_status = {}
        
        for agent_id, agent in self.agents.items():
            try:
                # Try to send ping to agent
                ping_msg = MCPMessage(
                    id=f"health_ping_{datetime.utcnow().timestamp()}",
                    method="ping",
                    params={},
                    recipient=agent_id
                )
                
                response = await asyncio.wait_for(
                    agent.handle_message(ping_msg),
                    timeout=5.0
                )
                
                health_status[agent_id] = {
                    'status': 'healthy',
                    'response_time': response.timestamp if response else None,
                    'metrics': agent.get_metrics()
                }
                
            except Exception as e:
                health_status[agent_id] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'metrics': agent.get_metrics()
                }
        
        return MCPMessage(
            id=f"health_{message.id}",
            method="health_status",
            params={'agents': health_status},
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def start(self):
        """Start the MCP controller"""
        self.is_running = True
        logger.info("MCP Controller started")
        
        # Start message processing loop
        await self._process_messages()
    
    async def stop(self):
        """Stop the MCP controller"""
        self.is_running = False
        logger.info("MCP Controller stopped")
    
    async def _process_messages(self):
        """Process messages from queue"""
        while self.is_running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )
                
                # Route message
                await self.route_message(message)
                
            except asyncio.TimeoutError:
                # No message in queue, continue
                continue
            except Exception as e:
                logger.error(f"Message processing error: {str(e)}")
    
    def _is_circuit_breaker_open(self, agent_id: str) -> bool:
        """Check if circuit breaker is open for agent"""
        if agent_id not in self.circuit_breakers:
            return False
            
        breaker = self.circuit_breakers[agent_id]
        
        if breaker['state'] == 'OPEN':
            # Check if recovery timeout has passed
            if breaker['last_failure_time']:
                time_since_failure = (datetime.utcnow() - breaker['last_failure_time']).total_seconds()
                if time_since_failure > breaker['recovery_timeout']:
                    breaker['state'] = 'HALF_OPEN'
                    breaker['success_count'] = 0
                    logger.info(f"Circuit breaker for {agent_id} moved to HALF_OPEN")
                    return False
            return True
            
        return False
    
    def _record_agent_success(self, agent_id: str):
        """Record successful agent interaction"""
        if agent_id in self.circuit_breakers:
            breaker = self.circuit_breakers[agent_id]
            
            if breaker['state'] == 'HALF_OPEN':
                breaker['success_count'] += 1
                if breaker['success_count'] >= 3:  # 3 successes to close
                    breaker['state'] = 'CLOSED'
                    breaker['failure_count'] = 0
                    logger.info(f"Circuit breaker for {agent_id} CLOSED")
            elif breaker['state'] == 'CLOSED':
                breaker['failure_count'] = max(0, breaker['failure_count'] - 1)
    
    def _record_agent_failure(self, agent_id: str, error: str):
        """Record agent failure and update circuit breaker"""
        if agent_id in self.circuit_breakers:
            breaker = self.circuit_breakers[agent_id]
            breaker['failure_count'] += 1
            breaker['last_failure_time'] = datetime.utcnow()
            
            if breaker['failure_count'] >= breaker['failure_threshold']:
                breaker['state'] = 'OPEN'
                self.metrics['circuit_breaker_trips'] += 1
                logger.warning(f"Circuit breaker OPENED for {agent_id} after {breaker['failure_count']} failures")
    
    def _log_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log event for replay and analysis"""
        event = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'data': event_data
        }
        
        self.event_store.append(event)
        self.metrics['event_store_size'] = len(self.event_store)
        
        # Keep only last 10000 events
        if len(self.event_store) > 10000:
            self.event_store = self.event_store[-10000:]
    
    async def start_pipeline(self, pipeline_id: str, pipeline_config: Dict[str, Any]) -> str:
        """Start a deterministic processing pipeline"""
        pipeline_state = {
            'id': pipeline_id,
            'config': pipeline_config,
            'status': 'running',
            'start_time': datetime.utcnow(),
            'current_stage': 'initialization',
            'stages_completed': [],
            'errors': [],
            'results': {}
        }
        
        self.pipeline_state['active_pipelines'][pipeline_id] = pipeline_state
        self.pipeline_state['pipeline_metrics']['started'] += 1
        
        self._log_event('pipeline_started', {
            'pipeline_id': pipeline_id,
            'config': pipeline_config
        })
        
        logger.info(f"Pipeline {pipeline_id} started")
        return pipeline_id
    
    async def _handle_start_pipeline(self, message: MCPMessage) -> MCPMessage:
        """Handle pipeline start request"""
        pipeline_config = message.params.get('config', {})
        pipeline_id = message.params.get('pipeline_id', str(uuid.uuid4()))
        
        try:
            pipeline_id = await self.start_pipeline(pipeline_id, pipeline_config)
            
            return MCPMessage(
                id=f"pipeline_started_{message.id}",
                method="pipeline_started",
                params={
                    'pipeline_id': pipeline_id,
                    'status': 'started',
                    'timestamp': datetime.utcnow().isoformat()
                },
                type=MessageType.RESPONSE,
                recipient=message.sender
            )
            
        except Exception as e:
            return MCPMessage(
                id=f"pipeline_error_{message.id}",
                method="pipeline_error",
                params={
                    'error': str(e),
                    'pipeline_id': pipeline_id
                },
                type=MessageType.ERROR,
                recipient=message.sender
            )
    
    async def _handle_pipeline_status(self, message: MCPMessage) -> MCPMessage:
        """Get pipeline status"""
        pipeline_id = message.params.get('pipeline_id')
        
        if pipeline_id and pipeline_id in self.pipeline_state['active_pipelines']:
            pipeline = self.pipeline_state['active_pipelines'][pipeline_id]
        else:
            pipeline = None
        
        return MCPMessage(
            id=f"pipeline_status_{message.id}",
            method="pipeline_status_response",
            params={
                'pipeline': pipeline,
                'all_pipelines': list(self.pipeline_state['active_pipelines'].keys())
            },
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _handle_reset_circuit_breaker(self, message: MCPMessage) -> MCPMessage:
        """Reset circuit breaker for an agent"""
        agent_id = message.params.get('agent_id')
        
        if agent_id and agent_id in self.circuit_breakers:
            self.circuit_breakers[agent_id] = {
                'state': 'CLOSED',
                'failure_count': 0,
                'failure_threshold': 5,
                'recovery_timeout': 30,
                'last_failure_time': None,
                'success_count': 0
            }
            
            logger.info(f"Circuit breaker reset for {agent_id}")
            
            return MCPMessage(
                id=f"breaker_reset_{message.id}",
                method="circuit_breaker_reset",
                params={
                    'agent_id': agent_id,
                    'status': 'reset',
                    'timestamp': datetime.utcnow().isoformat()
                },
                type=MessageType.RESPONSE,
                recipient=message.sender
            )
        else:
            return MCPMessage(
                id=f"breaker_error_{message.id}",
                method="error",
                params={
                    'error': f"Agent {agent_id} not found or no circuit breaker"
                },
                type=MessageType.ERROR,
                recipient=message.sender
            )
    
    async def _handle_get_event_history(self, message: MCPMessage) -> MCPMessage:
        """Get event history for analysis"""
        limit = message.params.get('limit', 100)
        event_type = message.params.get('event_type')
        
        events = self.event_store[-limit:] if not event_type else [
            e for e in self.event_store[-limit*2:] if e['type'] == event_type
        ][-limit:]
        
        return MCPMessage(
            id=f"events_{message.id}",
            method="event_history",
            params={
                'events': events,
                'total_events': len(self.event_store),
                'filtered_count': len(events)
            },
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    async def _handle_emergency_shutdown(self, message: MCPMessage) -> MCPMessage:
        """Handle emergency shutdown"""
        reason = message.params.get('reason', 'Emergency shutdown requested')
        
        # Stop all agents
        for agent in self.agents.values():
            agent.is_active = False
        
        # Clear all queues
        for queue in self.priority_queues.values():
            while not queue.empty():
                try:
                    queue.get_nowait()
                except:
                    break
        
        # Stop controller
        self.is_running = False
        
        self._log_event('emergency_shutdown', {
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        logger.critical(f"EMERGENCY SHUTDOWN: {reason}")
        
        return MCPMessage(
            id=f"shutdown_{message.id}",
            method="emergency_shutdown_complete",
            params={
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            },
            type=MessageType.RESPONSE,
            recipient=message.sender
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        agent_metrics = {
            agent_id: agent.get_metrics() 
            for agent_id, agent in self.agents.items()
        }
        
        # Update priority queue sizes
        self.metrics['priority_queue_sizes'] = {
            priority: queue.qsize() if hasattr(queue, 'qsize') else 0 
            for priority, queue in self.priority_queues.items()
        }
        
        return {
            'controller': self.metrics,
            'agents': agent_metrics,
            'shared_context_size': len(self.shared_context),
            'circuit_breakers': self.circuit_breakers,
            'agent_health': self.agent_health,
            'pipeline_state': {
                'active_count': len(self.pipeline_state['active_pipelines']),
                'completed_count': len(self.pipeline_state['completed_pipelines']),
                'failed_count': len(self.pipeline_state['failed_pipelines']),
                'metrics': dict(self.pipeline_state['pipeline_metrics'])
            }
        }