from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Mikrobot FastVersion - Main FastAPI Application
FoxBox Framework Implementation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Core imports
from ..core.enhanced_orchestrator import EnhancedOrchestrator
from ..core.connectors.mt5_connector import MT5Connector, MT5Config
from ..core.mcp_controller import MCPController
from ..core.hansei import HanseiAgent
from .webhook_receiver import router as webhook_router, initialize_webhook_receiver
from .health import router as health_router
from .metrics import router as metrics_router

# Configuration
from ..config.settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MikrobotApplication:
    """Main application class managing all components"""
    
    def __init__(self):
        self.settings = get_settings()
        self.orchestrator: Optional[EnhancedOrchestrator] = None
        self.mt5_connector: Optional[MT5Connector] = None
        self.mcp_controller: Optional[MCPController] = None
        self.hansei_agent: Optional[HanseiAgent] = None
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize all system components"""
        try:
            logger.info("ROCKET Initializing Mikrobot FastVersion...")
            
            # Initialize MT5 connector
            await self._initialize_mt5()
            
            # Initialize MCP controller
            await self._initialize_mcp()
            
            # Initialize U-Cell orchestrator
            await self._initialize_orchestrator()
            
            # Initialize webhook receiver
            await self._initialize_webhook()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.is_initialized = True
            logger.info("OK Mikrobot FastVersion initialized successfully")
            
        except Exception as e:
            logger.error(f"ERROR Initialization failed: {str(e)}")
            raise
    
    async def _initialize_mt5(self):
        """Initialize MetaTrader 5 connector"""
        logger.info("TOOL Initializing MT5 connector...")
        
        mt5_config = MT5Config(
            path=self.settings.MT5_PATH,
            login=self.settings.MT5_LOGIN,
            password=self.settings.MT5_PASSWORD,
            server=self.settings.MT5_SERVER
        )
        
        self.mt5_connector = MT5Connector(mt5_config)
        
        # Attempt connection
        if await self.mt5_connector.connect():
            logger.info("OK MT5 connector initialized and connected")
        else:
            logger.warning("WARNING MT5 connector initialized but not connected")
    
    async def _initialize_mcp(self):
        """Initialize MCP controller and agents"""
        logger.info(" Initializing MCP controller...")
        
        self.mcp_controller = MCPController({
            'log_level': self.settings.MCP_LOG_LEVEL
        })
        
        # Initialize Hansei agent
        if self.settings.ENABLE_HANSEI:
            self.hansei_agent = HanseiAgent()
            self.mcp_controller.register_agent(self.hansei_agent)
            logger.info("OK Hansei reflection agent registered")
        
        logger.info("OK MCP controller initialized")
    
    async def _initialize_orchestrator(self):
        """Initialize Enhanced Orchestrator"""
        logger.info(" Initializing Enhanced Orchestrator (ProductOwner -> MCP -> U-Cells)...")
        
        orchestrator_config = {
            'mcp_config': {
                'log_level': self.settings.MCP_LOG_LEVEL
            },
            'ucell_config': {
                'mt5_connection': self.mt5_connector,
                'account_config': {
                    'balance': self.settings.ACCOUNT_BALANCE,
                    'max_daily_loss_percent': self.settings.MAX_DAILY_LOSS_PERCENT,
                    'max_total_loss_percent': self.settings.MAX_TOTAL_LOSS_PERCENT,
                    'max_position_risk_percent': self.settings.MAX_POSITION_RISK_PERCENT
                },
                'ml_model_path': self.settings.ML_MODEL_PATH,
                'alert_callback': self._handle_alert
            }
        }
        
        self.orchestrator = EnhancedOrchestrator(orchestrator_config)
        logger.info("OK Enhanced Orchestrator initialized with ProductOwner strategic oversight")
    
    async def _initialize_webhook(self):
        """Initialize webhook receiver"""
        logger.info(" Initializing webhook receiver...")
        
        webhook_config = {
            'webhook_secret': self.settings.WEBHOOK_SECRET,
            'allowed_ips': self.settings.ALLOWED_IPS.split(',') if self.settings.ALLOWED_IPS else [],
            'rate_limit': 60  # signals per minute
        }
        
        initialize_webhook_receiver(self.orchestrator, webhook_config)
        logger.info("OK Webhook receiver initialized")
    
    async def _start_background_tasks(self):
        """Start background tasks"""
        logger.info(" Starting background tasks...")
        
        # Start enhanced orchestrator (includes MCP controller)
        if self.orchestrator:
            asyncio.create_task(self.orchestrator.start())
        
        logger.info("OK Background tasks started")
    
    async def _handle_alert(self, alerts: list):
        """Handle system alerts"""
        for alert in alerts:
            logger.warning(f" ALERT: {alert.get('type')} - {alert.get('message')}")
            
            # Could send notifications, emails, etc.
    
    async def shutdown(self):
        """Shutdown all components"""
        logger.info(" Shutting down Mikrobot FastVersion...")
        
        if self.orchestrator:
            await self.orchestrator.stop()
        
        if self.mt5_connector:
            await self.mt5_connector.disconnect()
        
        logger.info("OK Shutdown complete")


# Global application instance
mikrobot_app = MikrobotApplication()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await mikrobot_app.initialize()
    yield
    # Shutdown
    await mikrobot_app.shutdown()


# Create FastAPI application
app = FastAPI(
    title="Mikrobot FastVersion",
    description="Automated Trading System with AI-Driven Price Action Analysis",
    version="1.0.0",
    docs_url="/docs" if mikrobot_app.settings.APP_ENV == "development" else None,
    redoc_url="/redoc" if mikrobot_app.settings.APP_ENV == "development" else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if mikrobot_app.settings.APP_ENV == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if mikrobot_app.settings.APP_ENV == "development" else ["localhost", "127.0.0.1"]
)

# Include routers
app.include_router(webhook_router)
app.include_router(health_router)
app.include_router(metrics_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Mikrobot FastVersion",
        "version": "1.0.0",
        "status": "operational" if mikrobot_app.is_initialized else "initializing",
        "framework": "FoxBox Framework",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "ProductOwner Strategic Orchestration",
            "Enhanced MCP Controller with Circuit Breakers",
            "5 U-Cell Deterministic Pipeline",
            "MT5 Price Action Analysis",
            "FTMO-Compliant Risk Management",
            "Six Sigma Quality Control",
            "Event Sourcing for Decision Replay",
            "Priority-Based Message Routing",
            "Hansei Self-Reflection"
        ]
    }


@app.get("/system/status")
async def system_status():
    """Get comprehensive system status"""
    if not mikrobot_app.is_initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "initialized": mikrobot_app.is_initialized,
        "components": {}
    }
    
    # MT5 status
    if mikrobot_app.mt5_connector:
        status["components"]["mt5"] = {
            "connected": mikrobot_app.mt5_connector.is_connected,
            "metrics": mikrobot_app.mt5_connector.get_metrics()
        }
    
    # Enhanced Orchestrator status
    if mikrobot_app.orchestrator:
        orchestrator_metrics = mikrobot_app.orchestrator.get_comprehensive_metrics()
        status["components"]["enhanced_orchestrator"] = {
            "active_pipelines": orchestrator_metrics.get('active_pipelines', 0),
            "completed_pipelines": orchestrator_metrics.get('completed_pipelines', 0),
            "orchestration_metrics": orchestrator_metrics.get('orchestration', {}),
            "product_owner_status": {
                "performance": orchestrator_metrics.get('product_owner', {}).get('performance', {}),
                "active_strategy": orchestrator_metrics.get('product_owner', {}).get('active_strategy', {})
            },
            "mcp_controller": orchestrator_metrics.get('mcp_controller', {}),
            "system_status": orchestrator_metrics.get('system_status', {})
        }
    
    return status


@app.post("/system/emergency-stop")
async def emergency_stop():
    """Emergency stop all trading activities"""
    if not mikrobot_app.is_initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Emergency stop orchestrator
    if mikrobot_app.orchestrator:
        await mikrobot_app.orchestrator.emergency_stop("API emergency stop requested")
    
    # Close all positions
    if mikrobot_app.mt5_connector and mikrobot_app.mt5_connector.is_connected:
        positions = await mikrobot_app.mt5_connector.get_positions()
        for position in positions:
            await mikrobot_app.mt5_connector.close_position(position['ticket'], reason='emergency_stop')
    
    logger.warning(" EMERGENCY STOP ACTIVATED")
    
    return {
        "status": "emergency_stop_activated",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "All trading activities stopped"
    }


if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=mikrobot_app.settings.APP_ENV == "development"
    )