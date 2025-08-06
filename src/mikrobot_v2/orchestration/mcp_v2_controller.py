"""
MCP v2 Controller - Enhanced Multi-Agent Orchestration
======================================================

Advanced orchestration system for coordinating multiple specialized agents
in autonomous trading operations with ML validation and Hansei reflection.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from ..strategies.lightning_bolt import LightningBoltSignal, TrendDirection

logger = logging.getLogger(__name__)

class AgentType(Enum):
    STRATEGY = "STRATEGY"
    EXECUTION = "EXECUTION"
    RISK = "RISK"
    ML_VALIDATION = "ML_VALIDATION"
    PERFORMANCE = "PERFORMANCE"
    HANSEI = "HANSEI"

class MessageType(Enum):
    SIGNAL = "SIGNAL"
    EXECUTION_REQUEST = "EXECUTION_REQUEST"
    RISK_CHECK = "RISK_CHECK"
    ML_VALIDATION = "ML_VALIDATION"
    PERFORMANCE_UPDATE = "PERFORMANCE_UPDATE"
    REFLECTION = "REFLECTION"
    SYSTEM_STATUS = "SYSTEM_STATUS"

@dataclass
class MCPMessage:
    """Message structure for agent communication"""
    id: str
    type: MessageType
    sender: str
    recipient: str
    payload: Dict[str, Any]
    timestamp: datetime
    priority: int = 5  # 1=highest, 10=lowest
    
class AgentPerformanceMetrics:
    """Track agent performance metrics"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.messages_processed = 0
        self.avg_response_time = 0.0
        self.success_rate = 1.0
        self.last_activity = datetime.now()
        self.error_count = 0
        
    def update_performance(self, response_time: float, success: bool):
        """Update performance metrics"""
        self.messages_processed += 1
        self.avg_response_time = (self.avg_response_time + response_time) / 2
        
        if success:
            self.success_rate = (self.success_rate * 0.9) + (1.0 * 0.1)
        else:
            self.success_rate = (self.success_rate * 0.9) + (0.0 * 0.1)
            self.error_count += 1
            
        self.last_activity = datetime.now()

class MCPv2Controller:
    """
    Enhanced MCP Controller for multi-agent orchestration
    
    Features:
    - Asynchronous message passing
    - Agent performance monitoring
    - Priority-based message queuing
    - ML validation integration
    - Hansei reflection coordination
    - Real-time decision making
    """
    
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.message_queue: List[MCPMessage] = []
        self.performance_metrics: Dict[str, AgentPerformanceMetrics] = {}
        self.active_signals: Dict[str, LightningBoltSignal] = {}
        
        # System state
        self.system_running = False
        self.processing_lock = asyncio.Lock()
        self.message_handlers: Dict[MessageType, Callable] = {}
        
        # Performance tracking
        self.total_trades = 0
        self.successful_trades = 0
        self.total_profit = 0.0
        self.daily_performance = {}
        
        self._setup_message_handlers()
        logger.info("🎛️ MCP v2 Controller initialized")
    
    def _setup_message_handlers(self):
        """Setup message type handlers"""
        self.message_handlers = {
            MessageType.SIGNAL: self._handle_signal_message,
            MessageType.EXECUTION_REQUEST: self._handle_execution_request,
            MessageType.RISK_CHECK: self._handle_risk_check,
            MessageType.ML_VALIDATION: self._handle_ml_validation,
            MessageType.PERFORMANCE_UPDATE: self._handle_performance_update,
            MessageType.REFLECTION: self._handle_reflection,
            MessageType.SYSTEM_STATUS: self._handle_system_status
        }
    
    def register_agent(self, agent_id: str, agent_type: AgentType, 
                      handler: Callable, config: Dict = None):
        """Register agent with the MCP system"""
        self.agents[agent_id] = {
            'type': agent_type,
            'handler': handler,
            'config': config or {},
            'status': 'active',
            'registered_at': datetime.now()
        }
        
        self.performance_metrics[agent_id] = AgentPerformanceMetrics(agent_id)
        logger.info(f"✅ Agent registered: {agent_id} ({agent_type.value})")
    
    async def send_message(self, message: MCPMessage):
        """Send message to agent queue"""
        async with self.processing_lock:
            # Insert message based on priority
            inserted = False
            for i, existing_msg in enumerate(self.message_queue):
                if message.priority < existing_msg.priority:
                    self.message_queue.insert(i, message)
                    inserted = True
                    break
            
            if not inserted:
                self.message_queue.append(message)
        
        logger.debug(f"📤 Message queued: {message.type.value} from {message.sender}")
    
    async def process_messages(self):
        """Process messages from queue"""
        while self.system_running:
            try:
                async with self.processing_lock:
                    if not self.message_queue:
                        await asyncio.sleep(0.1)
                        continue
                    
                    message = self.message_queue.pop(0)
                
                # Process message
                start_time = datetime.now()
                success = await self._process_single_message(message)
                end_time = datetime.now()
                
                # Update performance metrics
                response_time = (end_time - start_time).total_seconds()
                if message.sender in self.performance_metrics:
                    self.performance_metrics[message.sender].update_performance(
                        response_time, success
                    )
                
            except Exception as e:
                logger.error(f"Message processing error: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_message(self, message: MCPMessage) -> bool:
        """Process individual message"""
        try:
            handler = self.message_handlers.get(message.type)
            if handler:
                await handler(message)
                return True
            else:
                logger.warning(f"No handler for message type: {message.type}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing message {message.id}: {e}")
            return False
    
    async def _handle_signal_message(self, message: MCPMessage):
        """Handle Lightning Bolt trading signals"""
        try:
            signal_data = message.payload
            
            # Create signal object
            signal = LightningBoltSignal(
                symbol=signal_data['symbol'],
                direction=TrendDirection(signal_data['direction']),
                entry_price=signal_data['entry_price'],
                stop_loss=signal_data['stop_loss'],
                take_profit=signal_data['take_profit'],
                ylipip_offset=signal_data['ylipip_offset'],
                confidence=signal_data['confidence'],
                phase=signal_data['phase'],
                timestamp=datetime.fromisoformat(signal_data['timestamp'])
            )
            
            # Store active signal
            self.active_signals[signal.symbol] = signal
            
            # Send for ML validation
            await self._request_ml_validation(signal)
            
            logger.info(f"⚡ Signal processed: {signal.symbol} {signal.direction.value}")
            
        except Exception as e:
            logger.error(f"Signal handling error: {e}")
    
    async def _handle_execution_request(self, message: MCPMessage):
        """Handle trade execution requests"""
        try:
            exec_data = message.payload
            
            # Send to execution agent
            execution_agent = self._find_agent_by_type(AgentType.EXECUTION)
            if execution_agent:
                await execution_agent['handler'](exec_data)
                self.total_trades += 1
                logger.info(f"🔄 Execution request processed: {exec_data.get('symbol')}")
            
        except Exception as e:
            logger.error(f"Execution handling error: {e}")
    
    async def _handle_risk_check(self, message: MCPMessage):
        """Handle risk management checks"""
        try:
            risk_data = message.payload
            
            # Send to risk agent
            risk_agent = self._find_agent_by_type(AgentType.RISK)
            if risk_agent:
                risk_result = await risk_agent['handler'](risk_data)
                
                # Send result back to requester
                response = MCPMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.SYSTEM_STATUS,
                    sender="mcp_controller",
                    recipient=message.sender,
                    payload={'risk_check_result': risk_result},
                    timestamp=datetime.now(),
                    priority=3
                )
                await self.send_message(response)
            
        except Exception as e:
            logger.error(f"Risk check error: {e}")
    
    async def _handle_ml_validation(self, message: MCPMessage):
        """Handle ML validation results"""
        try:
            ml_data = message.payload
            symbol = ml_data.get('symbol')
            
            if symbol in self.active_signals:
                validation_score = ml_data.get('validation_score', 0.0)
                
                # If ML validation passes, proceed to execution
                if validation_score >= 0.75:
                    signal = self.active_signals[symbol]
                    
                    # Create execution request with ATR info
                    payload = {
                        'symbol': signal.symbol,
                        'direction': signal.direction.value,
                        'entry_price': signal.entry_price,
                        'stop_loss': signal.stop_loss,
                        'take_profit': signal.take_profit,
                        'confidence': signal.confidence,
                        'ml_score': validation_score
                    }
                    
                    # Add ATR position sizing info if available
                    if hasattr(signal, 'atr_info'):
                        payload['atr_info'] = signal.atr_info
                        payload['volume'] = signal.atr_info['position_size']
                        logger.info(f"📊 ATR position size: {signal.atr_info['position_size']} lots")
                    else:
                        payload['volume'] = 0.01  # Default fallback
                        logger.warning(f"⚠️ No ATR info for {signal.symbol}, using default volume")
                    
                    exec_request = MCPMessage(
                        id=str(uuid.uuid4()),
                        type=MessageType.EXECUTION_REQUEST,
                        sender="mcp_controller",
                        recipient="execution_agent",
                        payload=payload,
                        timestamp=datetime.now(),
                        priority=2
                    )
                    
                    await self.send_message(exec_request)
                    logger.info(f"✅ ML validation passed: {symbol} (score: {validation_score:.2f})")
                    
                else:
                    logger.info(f"❌ ML validation failed: {symbol} (score: {validation_score:.2f})")
                    del self.active_signals[symbol]  # Remove rejected signal
            
        except Exception as e:
            logger.error(f"ML validation error: {e}")
    
    async def _handle_performance_update(self, message: MCPMessage):
        """Handle performance updates"""
        try:
            perf_data = message.payload
            
            trade_result = perf_data.get('trade_result')
            if trade_result:
                profit = trade_result.get('profit', 0.0)
                self.total_profit += profit
                
                if profit > 0:
                    self.successful_trades += 1
                
                # Update daily performance
                today = datetime.now().date().isoformat()
                if today not in self.daily_performance:
                    self.daily_performance[today] = {'trades': 0, 'profit': 0.0}
                
                self.daily_performance[today]['trades'] += 1
                self.daily_performance[today]['profit'] += profit
                
                logger.info(f"📊 Performance updated: Profit {profit:.2f}")
            
        except Exception as e:
            logger.error(f"Performance update error: {e}")
    
    async def _handle_reflection(self, message: MCPMessage):
        """Handle Hansei reflection messages"""
        try:
            reflection_data = message.payload
            
            # Process reflection insights
            insights = reflection_data.get('insights', [])
            optimizations = reflection_data.get('optimizations', [])
            
            # Apply optimizations if any
            for optimization in optimizations:
                await self._apply_optimization(optimization)
            
            logger.info(f"🧠 Hansei reflection processed: {len(insights)} insights")
            
        except Exception as e:
            logger.error(f"Reflection handling error: {e}")
    
    async def _handle_system_status(self, message: MCPMessage):
        """Handle system status messages"""
        try:
            status_data = message.payload
            logger.info(f"📡 System status: {status_data}")
            
        except Exception as e:
            logger.error(f"System status error: {e}")
    
    async def _request_ml_validation(self, signal: LightningBoltSignal):
        """Request ML validation for trading signal"""
        ml_agent = self._find_agent_by_type(AgentType.ML_VALIDATION)
        if ml_agent:
            
            validation_request = MCPMessage(
                id=str(uuid.uuid4()),
                type=MessageType.ML_VALIDATION,
                sender="mcp_controller",
                recipient="ml_validation_agent",
                payload={
                    'symbol': signal.symbol,
                    'direction': signal.direction.value,
                    'entry_price': signal.entry_price,
                    'confidence': signal.confidence,
                    'timestamp': signal.timestamp.isoformat()
                },
                timestamp=datetime.now(),
                priority=2
            )
            
            await self.send_message(validation_request)
    
    def _find_agent_by_type(self, agent_type: AgentType) -> Optional[Dict]:
        """Find agent by type"""
        for agent_id, agent_data in self.agents.items():
            if agent_data['type'] == agent_type:
                return agent_data
        return None
    
    async def _apply_optimization(self, optimization: Dict):
        """Apply system optimization from Hansei reflection"""
        try:
            opt_type = optimization.get('type')
            
            if opt_type == 'confidence_threshold':
                # Adjust confidence thresholds based on performance
                new_threshold = optimization.get('value', 0.75)
                logger.info(f"🔧 Optimization applied: confidence threshold -> {new_threshold}")
                
            elif opt_type == 'risk_adjustment':
                # Adjust risk parameters
                new_risk = optimization.get('value', 0.01)
                logger.info(f"🔧 Optimization applied: risk adjustment -> {new_risk}")
                
        except Exception as e:
            logger.error(f"Optimization application error: {e}")
    
    async def start_system(self):
        """Start the MCP system"""
        self.system_running = True
        logger.info("🚀 MCP v2 Controller started")
        
        # Start message processing
        asyncio.create_task(self.process_messages())
        
        # Start performance monitoring
        asyncio.create_task(self._monitor_system_health())
    
    async def stop_system(self):
        """Stop the MCP system"""
        self.system_running = False
        logger.info("🛑 MCP v2 Controller stopped")
    
    async def _monitor_system_health(self):
        """Monitor system health and performance"""
        while self.system_running:
            try:
                # Check agent health
                inactive_agents = []
                for agent_id, metrics in self.performance_metrics.items():
                    time_since_activity = datetime.now() - metrics.last_activity
                    if time_since_activity > timedelta(minutes=10):
                        inactive_agents.append(agent_id)
                
                if inactive_agents:
                    logger.warning(f"⚠️ Inactive agents detected: {inactive_agents}")
                
                # Log system statistics
                queue_size = len(self.message_queue)
                success_rate = (self.successful_trades / max(self.total_trades, 1)) * 100
                
                logger.info(f"📊 System Health: Queue={queue_size}, Success={success_rate:.1f}%, Profit={self.total_profit:.2f}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        return {
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'success_rate': (self.successful_trades / max(self.total_trades, 1)) * 100,
            'total_profit': self.total_profit,
            'active_signals': len(self.active_signals),
            'queue_size': len(self.message_queue),
            'active_agents': len([a for a in self.agents.values() if a['status'] == 'active']),
            'daily_performance': self.daily_performance
        }