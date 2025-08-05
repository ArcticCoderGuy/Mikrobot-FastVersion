"""
MIKROBOT TRADING SYSTEM - SECURE CONFIGURATION MODULE
Emergency Security Implementation - Zero Hardcoded Credentials
Production-Ready Security Framework

CRITICAL: This module replaces ALL hardcoded credentials with secure environment variables
"""

import os
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from pathlib import Path
import json
import base64
from functools import wraps

# Security configuration logger
security_logger = logging.getLogger('mikrobot.security')

class SecurityConfigError(Exception):
    """Custom exception for security configuration errors"""
    pass

class SecureConfig:
    """
    Secure configuration manager for Mikrobot Trading System
    Handles all credentials, API keys, and sensitive parameters
    """
    
    def __init__(self):
        self.config_loaded = False
        self.encryption_key = None
        self._load_security_config()
    
    def _load_security_config(self):
        """Load security configuration from environment variables"""
        try:
            # Check for required environment variables
            required_vars = [
                'MIKROBOT_MT5_LOGIN',
                'MIKROBOT_MT5_PASSWORD', 
                'MIKROBOT_MT5_SERVER',
                'MIKROBOT_SECRET_KEY',
                'MIKROBOT_ENCRYPTION_KEY'
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                raise SecurityConfigError(
                    f"Missing required environment variables: {', '.join(missing_vars)}"
                )
            
            # Initialize encryption
            self.encryption_key = os.getenv('MIKROBOT_ENCRYPTION_KEY').encode()
            if len(self.encryption_key) != 44:  # Fernet key must be 32 bytes base64 encoded (44 chars)
                self.encryption_key = base64.urlsafe_b64encode(
                    os.getenv('MIKROBOT_ENCRYPTION_KEY').encode()[:32].ljust(32, b'0')
                )
            
            self.config_loaded = True
            security_logger.info("Security configuration loaded successfully")
            
        except Exception as e:
            security_logger.error(f"Failed to load security configuration: {e}")
            raise SecurityConfigError(f"Security configuration failed: {e}")
    
    def get_mt5_credentials(self) -> Dict[str, Any]:
        """Get MT5 connection credentials securely"""
        if not self.config_loaded:
            raise SecurityConfigError("Security configuration not loaded")
        
        return {
            'login': int(os.getenv('MIKROBOT_MT5_LOGIN')),
            'password': os.getenv('MIKROBOT_MT5_PASSWORD'),
            'server': os.getenv('MIKROBOT_MT5_SERVER'),
            'path': os.getenv('MIKROBOT_MT5_PATH', ''),
            'timeout': int(os.getenv('MIKROBOT_MT5_TIMEOUT', '60000'))
        }
    
    def get_database_config(self) -> Dict[str, str]:
        """Get database configuration securely"""
        return {
            'name': os.getenv('MIKROBOT_DB_NAME', 'mikrobot_platform'),
            'user': os.getenv('MIKROBOT_DB_USER', 'postgres'),
            'password': os.getenv('MIKROBOT_DB_PASSWORD', ''),
            'host': os.getenv('MIKROBOT_DB_HOST', 'localhost'),
            'port': os.getenv('MIKROBOT_DB_PORT', '5432')
        }
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get API keys and tokens securely"""
        return {
            'stripe_publishable': os.getenv('MIKROBOT_STRIPE_PUBLISHABLE_KEY', ''),
            'stripe_secret': os.getenv('MIKROBOT_STRIPE_SECRET_KEY', ''),
            'stripe_webhook': os.getenv('MIKROBOT_STRIPE_WEBHOOK_SECRET', ''),
            'email_password': os.getenv('MIKROBOT_EMAIL_PASSWORD', ''),
            'redis_url': os.getenv('MIKROBOT_REDIS_URL', 'redis://localhost:6379/0')
        }
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data for storage"""
        if not self.encryption_key:
            raise SecurityConfigError("Encryption key not available")
        
        f = Fernet(self.encryption_key)
        encrypted_data = f.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data from storage"""
        if not self.encryption_key:
            raise SecurityConfigError("Encryption key not available")
        
        f = Fernet(self.encryption_key)
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        return f.decrypt(decoded_data).decode()
    
    def validate_environment(self) -> bool:
        """Validate that all security requirements are met"""
        try:
            # Check environment variables
            self.get_mt5_credentials()
            self.get_database_config()
            self.get_api_keys()
            
            # Check Django secret key
            if not os.getenv('MIKROBOT_SECRET_KEY'):
                return False
            
            # Check debug mode is disabled in production
            debug_mode = os.getenv('MIKROBOT_DEBUG', 'False').lower()
            if debug_mode == 'true' and os.getenv('MIKROBOT_ENVIRONMENT') == 'production':
                security_logger.warning("DEBUG mode enabled in production environment")
                return False
            
            return True
            
        except Exception as e:
            security_logger.error(f"Environment validation failed: {e}")
            return False

def require_secure_config(func):
    """Decorator to ensure secure configuration is loaded before function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not hasattr(wrapper, '_config'):
            wrapper._config = SecureConfig()
        
        if not wrapper._config.config_loaded:
            raise SecurityConfigError("Secure configuration required but not loaded")
        
        return func(*args, **kwargs)
    return wrapper

# Global secure configuration instance
secure_config = SecureConfig()

def get_secure_config() -> SecureConfig:
    """Get the global secure configuration instance"""
    return secure_config

# Input validation framework
class InputValidator:
    """Comprehensive input validation for trading system"""
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate trading symbol format"""
        if not symbol or not isinstance(symbol, str):
            return False
        
        # Allow only alphanumeric characters and common forex pairs
        import re
        pattern = r'^[A-Z]{6}$|^[A-Z]{3}USD$|^USD[A-Z]{3}$|^[A-Z]+\d*$'
        return bool(re.match(pattern, symbol.upper()))
    
    @staticmethod
    def validate_lot_size(lot_size: float) -> bool:
        """Validate lot size within reasonable bounds"""
        if not isinstance(lot_size, (int, float)):
            return False
        
        return 0.01 <= lot_size <= 100.0
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate price value"""
        if not isinstance(price, (int, float)):
            return False
        
        return price > 0 and price < 1000000
    
    @staticmethod
    def validate_account_id(account_id: int) -> bool:
        """Validate MT5 account ID"""
        if not isinstance(account_id, int):
            return False
        
        return 1000000 <= account_id <= 999999999
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        if not filename or not isinstance(filename, str):
            return ""
        
        import re
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
        sanitized = re.sub(r'\.\.', '', sanitized)  # Remove parent directory references
        return sanitized[:255]  # Limit length
    
    @staticmethod
    def validate_json_input(json_str: str) -> bool:
        """Validate JSON input safely"""
        if not json_str or not isinstance(json_str, str):
            return False
        
        try:
            # Limit JSON size to prevent DoS
            if len(json_str) > 10000:
                return False
            
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, ValueError):
            return False

# Command injection protection
def safe_system_call(command: str, allowed_commands: list = None) -> str:
    """
    Safe system command execution with whitelist protection
    Replaces all os.system() calls in the codebase
    """
    if allowed_commands is None:
        allowed_commands = ['cls', 'clear']  # Only allow screen clearing
    
    # Extract base command
    base_command = command.split()[0] if command.split() else ""
    
    if base_command not in allowed_commands:
        security_logger.warning(f"Blocked potentially dangerous command: {command}")
        return ""
    
    # Use subprocess instead of os.system for better security
    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout
    except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
        security_logger.error(f"Safe system call failed: {e}")
        return ""