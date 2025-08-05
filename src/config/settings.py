"""
Mikrobot FastVersion - Configuration Settings
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
from dataclasses import dataclass
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings using Pydantic"""
    
    # Application
    APP_ENV: str = "production"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "mikrobot_super_secret_key_change_in_production"
    
    # Database
    DATABASE_URL: str = "postgresql://mikrobot:password@localhost:5432/mikrobot"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # MT5 Configuration
    MT5_PATH: Optional[str] = None
    MT5_LOGIN: Optional[int] = None
    MT5_PASSWORD: Optional[str] = None
    MT5_SERVER: Optional[str] = None
    
    # Webhook Security
    WEBHOOK_SECRET: str = "webhook_secret_key"
    ALLOWED_IPS: str = ""  # Comma-separated IPs
    
    # Risk Management (FTMO Rules)
    ACCOUNT_BALANCE: float = 100000.0
    MAX_DAILY_LOSS_PERCENT: float = 5.0
    MAX_TOTAL_LOSS_PERCENT: float = 10.0
    MAX_POSITION_RISK_PERCENT: float = 1.0
    PROFIT_TARGET_PERCENT: float = 10.0
    MIN_TRADING_DAYS: int = 10
    MAX_OPEN_POSITIONS: int = 3
    LEVERAGE: int = 100
    
    # ML Model Configuration
    ML_MODEL_PATH: str = "/app/models/signal_classifier.pkl"
    ENABLE_ML_TRAINING: bool = False
    FEATURE_SCALER_PATH: str = "/app/models/feature_scaler.pkl"
    
    # MCP Configuration
    ENABLE_MCP: bool = True
    MCP_LOG_LEVEL: str = "INFO"
    
    # Hansei Configuration
    ENABLE_HANSEI: bool = True
    REFLECTION_INTERVALS: str = "3600,86400,604800"  # hourly, daily, weekly
    HANSEI_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Trading Configuration
    MAGIC_NUMBER: int = 20240101
    MAX_SLIPPAGE_PIPS: float = 2.0
    MAX_RETRY_ATTEMPTS: int = 3
    ORDER_TIMEOUT_SECONDS: int = 5
    
    # Six Sigma Quality Control
    TARGET_CPK: float = 2.9
    MIN_CPK: float = 1.67
    QUALITY_SAMPLE_SIZE: int = 30
    
    # API Configuration
    API_RATE_LIMIT: int = 60  # requests per minute
    MAX_REQUEST_SIZE: int = 1024 * 1024  # 1MB
    
    # Monitoring
    ENABLE_PROMETHEUS: bool = True
    PROMETHEUS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL: int = 30
    
    # Logging
    LOG_FILE_PATH: str = "/app/logs/mikrobot.log"
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_reflection_intervals() -> List[int]:
    """Get reflection intervals as list of integers"""
    settings = get_settings()
    return [int(x.strip()) for x in settings.REFLECTION_INTERVALS.split(',')]


@dataclass
class TradingConfig:
    """Simplified trading configuration for the new architecture"""
    
    # MT5 Configuration
    mt5_path: Optional[str] = None
    mt5_login: Optional[int] = None
    mt5_password: Optional[str] = None
    mt5_server: Optional[str] = None
    
    # Connection settings
    connection_timeout: int = 60000
    retry_count: int = 3
    retry_delay: int = 5
    
    # Risk management
    default_risk_percent: float = 0.55
    max_daily_risk: float = 2.0
    max_positions_per_symbol: int = 3
    max_total_positions: int = 10
    
    # Performance settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 30
    max_concurrent_executions: int = 5
    
    # Logging
    log_level: str = "INFO"
    log_directory: str = "logs"
    
    def __post_init__(self):
        """Load configuration from environment variables"""
        self.mt5_login = int(os.getenv('MT5_LOGIN', '0')) or None
        self.mt5_password = os.getenv('MT5_PASSWORD') or None
        self.mt5_server = os.getenv('MT5_SERVER') or None
        self.mt5_path = os.getenv('MT5_PATH') or None
        
        # Create log directory
        Path(self.log_directory).mkdir(exist_ok=True)