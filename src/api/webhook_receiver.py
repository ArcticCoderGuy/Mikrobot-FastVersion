"""
Webhook Signal Receiver
FastAPI endpoint for receiving trading signals
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Header, Request
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import hmac
import hashlib
import json
from ..core.enhanced_orchestrator import EnhancedOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


class PriceLevel(BaseModel):
    """Price level information"""
    entry: float
    stop_loss: float
    take_profit: float
    current_price: Optional[float] = None
    previous_high: Optional[float] = None
    previous_low: Optional[float] = None
    break_level: Optional[float] = None
    retest_level: Optional[float] = None


class TradingSignal(BaseModel):
    """Trading signal model with validation"""
    symbol: str = Field(..., description="Trading symbol (e.g., EURUSD)")
    timeframe: str = Field(..., description="Timeframe (M1 or M5)")
    pattern_type: str = Field(..., description="Pattern type (M5_BOS or M1_BREAK_RETEST)")
    direction: str = Field(..., description="Trade direction (BUY or SELL)")
    price_levels: PriceLevel
    volume: float = Field(default=0.01, ge=0.01, le=100.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('symbol')
    def validate_symbol(cls, v):
        # Basic symbol validation
        if not v or len(v) < 6:
            raise ValueError('Invalid symbol format')
        return v.upper()
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        valid_timeframes = ['M1', 'M5']
        if v not in valid_timeframes:
            raise ValueError(f'Timeframe must be one of {valid_timeframes}')
        return v
    
    @validator('pattern_type')
    def validate_pattern_type(cls, v):
        valid_patterns = ['M5_BOS', 'M1_BREAK_RETEST']
        if v not in valid_patterns:
            raise ValueError(f'Pattern type must be one of {valid_patterns}')
        return v
    
    @validator('direction')
    def validate_direction(cls, v):
        valid_directions = ['BUY', 'SELL']
        if v.upper() not in valid_directions:
            raise ValueError(f'Direction must be one of {valid_directions}')
        return v.upper()


class WebhookResponse(BaseModel):
    """Webhook response model"""
    status: str
    message: str
    trace_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebhookReceiver:
    """Handles webhook signal reception and validation"""
    
    def __init__(self, orchestrator: EnhancedOrchestrator, config: Optional[Dict[str, Any]] = None):
        self.orchestrator = orchestrator
        self.config = config or {}
        
        # Security configuration
        self.webhook_secret = self.config.get('webhook_secret', '')
        self.allowed_ips = self.config.get('allowed_ips', [])
        self.rate_limit = self.config.get('rate_limit', 60)  # signals per minute
        
        # Metrics
        self.metrics = {
            'total_received': 0,
            'valid_signals': 0,
            'invalid_signals': 0,
            'auth_failures': 0
        }
        
        # Rate limiting
        self.signal_timestamps = []
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        if not self.webhook_secret:
            return True  # Skip verification if no secret configured
        
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    def check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        now = datetime.utcnow()
        minute_ago = now.timestamp() - 60
        
        # Remove old timestamps
        self.signal_timestamps = [ts for ts in self.signal_timestamps if ts > minute_ago]
        
        # Check limit
        if len(self.signal_timestamps) >= self.rate_limit:
            return False
        
        # Add current timestamp
        self.signal_timestamps.append(now.timestamp())
        return True
    
    def validate_ip(self, client_ip: str) -> bool:
        """Validate client IP if whitelist is configured"""
        if not self.allowed_ips:
            return True  # No IP filtering if not configured
        
        return client_ip in self.allowed_ips
    
    async def process_signal(self, signal: TradingSignal, 
                           background_tasks: BackgroundTasks) -> WebhookResponse:
        """Process incoming trading signal"""
        self.metrics['total_received'] += 1
        
        try:
            # Convert signal to dict format for orchestrator
            signal_data = {
                'symbol': signal.symbol,
                'timeframe': signal.timeframe,
                'pattern_type': signal.pattern_type,
                'direction': signal.direction,
                'price_levels': signal.price_levels.dict(),
                'volume': signal.volume,
                'timestamp': signal.timestamp.isoformat(),
                'metadata': signal.metadata or {}
            }
            
            # Process through enhanced orchestrator (async)
            background_tasks.add_task(
                self.orchestrator.add_signal_to_queue,
                signal_data
            )
            
            self.metrics['valid_signals'] += 1
            
            return WebhookResponse(
                status='accepted',
                message='Signal queued for processing',
                trace_id=None  # Will be assigned by orchestrator
            )
            
        except Exception as e:
            logger.error(f"Signal processing error: {str(e)}")
            self.metrics['invalid_signals'] += 1
            
            return WebhookResponse(
                status='error',
                message=f'Signal processing failed: {str(e)}'
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get receiver metrics"""
        return {
            **self.metrics,
            'rate_limit': f"{len(self.signal_timestamps)}/{self.rate_limit} per minute"
        }


# Global webhook receiver instance (will be initialized in main app)
webhook_receiver: Optional[WebhookReceiver] = None


@router.post("/signal", response_model=WebhookResponse)
async def receive_signal(
    signal: TradingSignal,
    background_tasks: BackgroundTasks,
    request: Request,
    x_signature: Optional[str] = Header(None)
):
    """
    Receive trading signal via webhook
    
    Security features:
    - Optional signature verification
    - IP whitelist support
    - Rate limiting
    """
    if not webhook_receiver:
        raise HTTPException(status_code=500, detail="Webhook receiver not initialized")
    
    # Get client IP
    client_ip = request.client.host
    
    # Validate IP
    if not webhook_receiver.validate_ip(client_ip):
        webhook_receiver.metrics['auth_failures'] += 1
        raise HTTPException(status_code=403, detail="Unauthorized IP address")
    
    # Verify signature if provided
    if x_signature:
        # Reconstruct payload for verification
        payload = signal.json(sort_keys=True)
        if not webhook_receiver.verify_signature(payload, x_signature):
            webhook_receiver.metrics['auth_failures'] += 1
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Check rate limit
    if not webhook_receiver.check_rate_limit():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Process signal
    return await webhook_receiver.process_signal(signal, background_tasks)


@router.get("/status")
async def webhook_status():
    """Get webhook receiver status and metrics"""
    if not webhook_receiver:
        raise HTTPException(status_code=500, detail="Webhook receiver not initialized")
    
    return {
        'status': 'active',
        'metrics': webhook_receiver.get_metrics(),
        'timestamp': datetime.utcnow().isoformat()
    }


@router.post("/test")
async def test_webhook():
    """Test webhook endpoint (development only)"""
    test_signal = TradingSignal(
        symbol="EURUSD",
        timeframe="M5",
        pattern_type="M5_BOS",
        direction="BUY",
        price_levels=PriceLevel(
            entry=1.0850,
            stop_loss=1.0830,
            take_profit=1.0890,
            current_price=1.0851,
            previous_high=1.0845
        ),
        volume=0.01,
        metadata={'test': True}
    )
    
    return {
        'status': 'test_mode',
        'signal': test_signal.dict(),
        'validation': 'passed',
        'timestamp': datetime.utcnow().isoformat()
    }


def initialize_webhook_receiver(orchestrator: EnhancedOrchestrator, config: Dict[str, Any]):
    """Initialize the webhook receiver"""
    global webhook_receiver
    webhook_receiver = WebhookReceiver(orchestrator, config)
    logger.info("Webhook receiver initialized")