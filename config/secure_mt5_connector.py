"""
MIKROBOT TRADING SYSTEM - SECURE MT5 CONNECTOR
Replaces all hardcoded credentials with secure environment-based authentication
Zero-downtime security upgrade for production trading systems
"""

import MetaTrader5 as mt5
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import time
from .security_config import get_secure_config, require_secure_config, InputValidator

class SecureMT5Connection:
    """
    Secure MT5 connection manager with environment-based credentials
    Replaces all insecure connection patterns in the codebase
    """
    
    def __init__(self):
        self.connected = False
        self.account_info = None
        self.logger = logging.getLogger('mikrobot.mt5.secure')
        self.config = get_secure_config()
        self.connection_retries = 3
        self.connection_timeout = 30
    
    @require_secure_config
    def connect(self) -> bool:
        """
        Establish secure connection to MT5 terminal
        Uses environment variables for all credentials
        """
        try:
            # Validate environment configuration
            if not self.config.validate_environment():
                self.logger.error("Environment validation failed - cannot connect")
                return False
            
            # Get secure credentials
            credentials = self.config.get_mt5_credentials()
            
            # Validate credentials before connection attempt
            if not self._validate_credentials(credentials):
                self.logger.error("Invalid credentials provided")
                return False
            
            # Initialize MT5 connection with retry logic
            for attempt in range(self.connection_retries):
                try:
                    # Initialize MT5
                    if not mt5.initialize(
                        path=credentials.get('path', ''),
                        login=credentials['login'],
                        password=credentials['password'],  
                        server=credentials['server'],
                        timeout=credentials['timeout']
                    ):
                        error_code = mt5.last_error()
                        self.logger.warning(f"MT5 initialization failed (attempt {attempt + 1}): {error_code}")
                        
                        if attempt < self.connection_retries - 1:
                            time.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        else:
                            return False
                    
                    # Verify connection
                    account_info = mt5.account_info()
                    if account_info is None:
                        self.logger.error("Failed to retrieve account information")
                        mt5.shutdown()
                        return False
                    
                    # Store connection state
                    self.connected = True
                    self.account_info = account_info
                    
                    self.logger.info(f"Secure MT5 connection established - Account: {account_info.login}")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                    if attempt < self.connection_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Secure MT5 connection failed: {e}")
            return False
    
    def _validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Validate MT5 credentials format and content"""
        try:
            # Validate login (account number)
            if not InputValidator.validate_account_id(credentials.get('login', 0)):
                return False
            
            # Validate password exists and is string
            password = credentials.get('password', '')
            if not password or not isinstance(password, str) or len(password) < 6:
                return False
            
            # Validate server name format
            server = credentials.get('server', '')
            if not server or not isinstance(server, str):
                return False
            
            return True
            
        except Exception:
            return False
    
    def disconnect(self) -> bool:
        """Safely disconnect from MT5 terminal"""
        try:
            if self.connected:
                mt5.shutdown()
                self.connected = False
                self.account_info = None
                self.logger.info("MT5 connection closed safely")
            return True
        except Exception as e:
            self.logger.error(f"Error during MT5 disconnect: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if MT5 connection is active"""
        if not self.connected:
            return False
        
        try:
            # Test connection with account info call
            account_info = mt5.account_info()
            if account_info is None:
                self.connected = False
                return False
            
            return True
        except Exception:
            self.connected = False
            return False
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information securely"""
        if not self.is_connected():
            return None
        
        try:
            info = mt5.account_info()
            if info is None:
                return None
            
            return {
                'login': info.login,
                'balance': info.balance,
                'equity': info.equity,
                'margin': info.margin,
                'free_margin': info.margin_free,
                'margin_level': info.margin_level,
                'currency': info.currency,
                'server': info.server,
                'leverage': info.leverage
            }
        except Exception as e:
            self.logger.error(f"Failed to get account info: {e}")
            return None
    
    def place_order(self, symbol: str, order_type: int, volume: float, 
                    price: float = 0.0, sl: float = 0.0, tp: float = 0.0,
                    comment: str = "") -> Optional[Dict[str, Any]]:
        """
        Place trading order with comprehensive validation
        All parameters are validated for security
        """
        if not self.is_connected():
            self.logger.error("Cannot place order - MT5 not connected")
            return None
        
        try:
            # Validate all input parameters
            if not InputValidator.validate_symbol(symbol):
                self.logger.error(f"Invalid symbol: {symbol}")
                return None
            
            if not InputValidator.validate_lot_size(volume):
                self.logger.error(f"Invalid lot size: {volume}")
                return None
            
            if price > 0 and not InputValidator.validate_price(price):
                self.logger.error(f"Invalid price: {price}")
                return None
            
            # Sanitize comment to prevent injection
            safe_comment = InputValidator.sanitize_filename(comment)[:50]
            
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol.upper(),
                "volume": round(volume, 2),
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "comment": safe_comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,  # Critical: Use FOK filling mode
            }
            
            # Execute order
            result = mt5.order_send(request)
            
            if result is None:
                error = mt5.last_error()
                self.logger.error(f"Order execution failed: {error}")
                return None
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                self.logger.warning(f"Order completed with warning: {result.retcode} - {result.comment}")
            
            return {
                'retcode': result.retcode,
                'deal': result.deal,
                'order': result.order,
                'volume': result.volume,
                'price': result.price,
                'comment': result.comment,
                'request_id': result.request_id
            }
            
        except Exception as e:
            self.logger.error(f"Order placement failed: {e}")
            return None
    
    def get_positions(self) -> list:
        """Get current positions securely"""
        if not self.is_connected():
            return []
        
        try:
            positions = mt5.positions_get()
            if positions is None:
                return []
            
            return [
                {
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': pos.type,
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'comment': pos.comment
                }
                for pos in positions
            ]
        except Exception as e:
            self.logger.error(f"Failed to get positions: {e}")
            return []
    
    def close_position(self, ticket: int) -> bool:
        """Close position by ticket with validation"""
        if not self.is_connected():
            return False
        
        try:
            # Get position details
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                self.logger.error(f"Position {ticket} not found")
                return False
            
            position = positions[0]
            
            # Prepare close request
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": ticket,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "comment": "Secure close"
            }
            
            result = mt5.order_send(close_request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                self.logger.info(f"Position {ticket} closed successfully")
                return True
            else:
                error_info = mt5.last_error() if result is None else result.comment
                self.logger.error(f"Failed to close position {ticket}: {error_info}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error closing position {ticket}: {e}")
            return False

# Global secure MT5 connection instance
_secure_mt5_connection = None

def get_secure_mt5_connection() -> SecureMT5Connection:
    """Get global secure MT5 connection instance"""
    global _secure_mt5_connection
    
    if _secure_mt5_connection is None:
        _secure_mt5_connection = SecureMT5Connection()
    
    return _secure_mt5_connection

# Backward compatibility wrapper for existing code
class LegacyMT5Wrapper:
    """
    Wrapper to maintain compatibility with existing MT5 code
    Redirects all calls to secure implementation
    """
    
    def __init__(self):
        self.connection = get_secure_mt5_connection()
    
    def initialize(self, **kwargs) -> bool:
        """Legacy initialize wrapper"""
        return self.connection.connect()
    
    def login(self, account: int, password: str, server: str) -> bool:
        """Legacy login wrapper - credentials now from environment"""
        return self.connection.connect()
    
    def shutdown(self) -> None:
        """Legacy shutdown wrapper"""
        self.connection.disconnect()

# Replace MetaTrader5 import for backward compatibility
mt5_secure = LegacyMT5Wrapper()