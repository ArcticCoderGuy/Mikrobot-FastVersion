from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MQL5 Webhook Endpoint
Specialized endpoint for MikroBot_BOS_M5M1.mq5 signals
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/signals", tags=["mql5-signals"])


class MQL5SignalPayload(BaseModel):
    """MQL5 signal payload matching MikroBot EA output"""
    ea_name: str = Field(..., description="EA name (MikroBot_BOS_M5M1)")
    ea_version: str = Field(..., description="EA version")
    signal_type: str = Field(..., description="Signal type (M5_M1_BOS_RETEST)")
    symbol: str = Field(..., description="Trading symbol")
    direction: str = Field(..., description="Trade direction (BUY/SELL)")
    trigger_price: float = Field(..., description="Trigger price")
    m5_bos_level: float = Field(..., description="M5 BOS level")
    m5_bos_direction: str = Field(..., description="M5 BOS direction")
    m1_break_high: float = Field(..., description="M1 break candle high")
    m1_break_low: float = Field(..., description="M1 break candle low")
    pip_trigger: float = Field(..., description="Pip trigger distance")
    timestamp: str = Field(..., description="Signal timestamp (ISO 8601)")
    primary_timeframe: str = Field(default="M5", description="Primary timeframe")
    confirmation_timeframe: str = Field(default="M1", description="Confirmation timeframe")
    signal_frequency: str = Field(default="HIGH", description="Signal frequency")
    account: int = Field(..., description="MT5 account number")
    
    @validator('direction')
    def validate_direction(cls, v):
        if v.upper() not in ['BUY', 'SELL']:
            raise ValueError('Direction must be BUY or SELL')
        return v.upper()
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v or len(v) < 6:
            raise ValueError('Invalid symbol format')
        return v.upper()
    
    @validator('trigger_price', 'm5_bos_level', 'm1_break_high', 'm1_break_low')
    def validate_prices(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('pip_trigger')
    def validate_pip_trigger(cls, v):
        if v <= 0 or v > 10:
            raise ValueError('Pip trigger must be between 0 and 10')
        return v


class MQL5SignalResponse(BaseModel):
    """Response for MQL5 signal submission"""
    status: str
    message: str
    signal_id: Optional[str] = None
    processing_time_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Global reference to enhanced orchestrator
enhanced_orchestrator = None


@router.post("/receive/", response_model=MQL5SignalResponse)
async def receive_mql5_signal(
    signal: MQL5SignalPayload,
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Receive MQL5 signal from MikroBot_BOS_M5M1.mq5
    Enhanced with ML/MCP processing pipeline
    """
    start_time = datetime.utcnow()
    
    try:
        # Log incoming signal
        logger.info(f" MQL5 Signal received: {signal.symbol} {signal.direction} @ {signal.trigger_price}")
        
        if not enhanced_orchestrator:
            raise HTTPException(status_code=503, detail="Enhanced orchestrator not available")
        
        # Convert to dictionary for processing
        signal_data = signal.dict()
        
        # Add processing metadata
        signal_data['received_at'] = start_time.isoformat()
        signal_data['client_ip'] = request.client.host
        signal_data['processing_pipeline'] = 'mql5_enhanced'
        
        # Queue for enhanced processing
        background_tasks.add_task(
            enhanced_orchestrator.process_mql5_signal,
            signal_data
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return MQL5SignalResponse(
            status="accepted",
            message=f"MQL5 signal queued for enhanced processing",
            signal_id=f"mql5_{int(start_time.timestamp())}_{signal.symbol}",
            processing_time_ms=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"ERROR MQL5 signal processing error: {str(e)}")
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return MQL5SignalResponse(
            status="error",
            message=f"Signal processing failed: {str(e)}",
            processing_time_ms=round(processing_time, 2)
        )


@router.get("/status")
async def mql5_endpoint_status():
    """Get MQL5 endpoint status"""
    return {
        "endpoint": "MQL5 Signal Receiver",
        "status": "active",
        "ea_support": "MikroBot_BOS_M5M1.mq5 v2.00+",
        "features": [
            "High-frequency M5/M1 signal processing",
            "ML enhancement pipeline",
            "MCP agent coordination", 
            "Real-time quality analysis",
            "FTMO-compliant risk management"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/test")
async def test_mql5_endpoint():
    """Test MQL5 endpoint with sample signal"""
    test_signal = MQL5SignalPayload(
        ea_name="MikroBot_BOS_M5M1",
        ea_version="2.00",
        signal_type="M5_M1_BOS_RETEST",
        symbol="EURUSD",
        direction="BUY",
        trigger_price=1.0855,
        m5_bos_level=1.0850,
        m5_bos_direction="BULLISH",
        m1_break_high=1.0857,
        m1_break_low=1.0852,
        pip_trigger=0.2,
        timestamp=datetime.utcnow().isoformat(),
        account=12345678
    )
    
    return {
        "status": "test_mode",
        "sample_signal": test_signal.dict(),
        "validation": "passed",
        "message": "MQL5 endpoint ready for production signals",
        "timestamp": datetime.utcnow().isoformat()
    }


def initialize_mql5_endpoint(orchestrator):
    """Initialize MQL5 endpoint with enhanced orchestrator"""
    global enhanced_orchestrator
    enhanced_orchestrator = orchestrator
    logger.info("OK MQL5 endpoint initialized with enhanced orchestrator")