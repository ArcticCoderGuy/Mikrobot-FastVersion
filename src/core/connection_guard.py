from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MT5 Connection Guard - Prevents connection conflicts
Ensures only ONE MT5 connection exists at a time
"""

import MetaTrader5 as mt5
import threading
import time
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MT5ConnectionGuard:
    """
    Singleton MT5 connection manager
    Prevents multiple simultaneous connections to same account
    """
    
    _instance = None
    _lock = threading.Lock()
    _connection_active = False
    _connection_owner = None
    _last_activity = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.connection_info = {}
            self.activity_log = []
    
    def is_connection_active(self) -> bool:
        """Check if MT5 connection is currently active"""
        try:
            # Test if MT5 is responsive
            version = mt5.version()
            if version:
                self._last_activity = datetime.now()
                return True
            return False
        except:
            return False
    
    def request_connection(self, requester_id: str, 
                          login: int, password: str, server: str,
                          timeout_seconds: int = 30) -> Dict[str, Any]:
        """
        Request exclusive MT5 connection
        
        Args:
            requester_id: Unique identifier for the requesting component
            login: MT5 account number
            password: MT5 password  
            server: MT5 server name
            timeout_seconds: Max wait time for existing connection to release
            
        Returns:
            Dict with connection status and info
        """
        
        with self._lock:
            current_time = datetime.now()
            
            # Check if connection already exists for same requester
            if (self._connection_active and 
                self._connection_owner == requester_id and
                self.is_connection_active()):
                
                logger.info(f"Connection already active for {requester_id}")
                return {
                    'status': 'already_connected',
                    'owner': requester_id,
                    'connection_time': self._last_activity,
                    'account': self.connection_info.get('login')
                }
            
            # If different owner has connection, wait or deny
            if self._connection_active and self._connection_owner != requester_id:
                logger.warning(f"Connection conflict: {self._connection_owner} has active connection, {requester_id} requesting")
                
                # For testing purposes, we'll force release after short wait
                time.sleep(2)
                self.force_release_connection()
            
            # Attempt to establish connection
            logger.info(f"Establishing MT5 connection for {requester_id}")
            
            try:
                # Ensure clean slate
                mt5.shutdown()
                time.sleep(1)
                
                # Initialize and login
                if not mt5.initialize():
                    error = mt5.last_error()
                    logger.error(f"MT5 initialization failed: {error}")
                    return {
                        'status': 'init_failed',
                        'error': error,
                        'requester': requester_id
                    }
                
                if not mt5.login(login, password, server):
                    error = mt5.last_error()
                    logger.error(f"MT5 login failed: {error}")
                    mt5.shutdown()
                    return {
                        'status': 'login_failed', 
                        'error': error,
                        'requester': requester_id
                    }
                
                # Connection successful
                self._connection_active = True
                self._connection_owner = requester_id
                self._last_activity = current_time
                
                # Store connection info
                account_info = mt5.account_info()
                self.connection_info = {
                    'login': login,
                    'server': server,
                    'owner': requester_id,
                    'established': current_time,
                    'account_name': account_info.name if account_info else 'Unknown'
                }
                
                self.activity_log.append({
                    'time': current_time,
                    'action': 'connection_established',
                    'owner': requester_id,
                    'account': login
                })
                
                logger.info(f"OK MT5 connection established for {requester_id} on account {login}")
                
                return {
                    'status': 'connected',
                    'owner': requester_id,
                    'account': login,
                    'server': server,
                    'connection_time': current_time,
                    'account_name': self.connection_info['account_name']
                }
                
            except Exception as e:
                logger.error(f"Connection establishment failed: {e}")
                self._connection_active = False
                self._connection_owner = None
                mt5.shutdown()
                
                return {
                    'status': 'error',
                    'error': str(e),
                    'requester': requester_id
                }
    
    def release_connection(self, requester_id: str) -> bool:
        """
        Release MT5 connection
        
        Args:
            requester_id: ID of the component releasing connection
            
        Returns:
            True if connection was released, False if requester didn't own it
        """
        
        with self._lock:
            if not self._connection_active:
                logger.info(f"No active connection to release for {requester_id}")
                return True
            
            if self._connection_owner != requester_id:
                logger.warning(f"Connection release denied: owned by {self._connection_owner}, requested by {requester_id}")
                return False
            
            # Release connection
            logger.info(f"Releasing MT5 connection for {requester_id}")
            
            mt5.shutdown()
            
            self._connection_active = False
            self._connection_owner = None
            self._last_activity = None
            
            self.activity_log.append({
                'time': datetime.now(),
                'action': 'connection_released',
                'owner': requester_id,
                'account': self.connection_info.get('login', 'unknown')
            })
            
            logger.info(f"OK MT5 connection released by {requester_id}")
            return True
    
    def force_release_connection(self) -> bool:
        """Force release any active connection (admin function)"""
        
        with self._lock:
            if self._connection_active:
                logger.warning(f"Force releasing connection owned by {self._connection_owner}")
                
                mt5.shutdown()
                
                self.activity_log.append({
                    'time': datetime.now(),
                    'action': 'connection_force_released',
                    'previous_owner': self._connection_owner,
                    'account': self.connection_info.get('login', 'unknown')
                })
                
                self._connection_active = False
                self._connection_owner = None
                self._last_activity = None
                
                return True
            
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        
        return {
            'active': self._connection_active,
            'owner': self._connection_owner,
            'last_activity': self._last_activity,
            'connection_info': self.connection_info.copy(),
            'is_responsive': self.is_connection_active() if self._connection_active else False
        }
    
    def get_activity_log(self, last_n: int = 10) -> list:
        """Get recent activity log"""
        return self.activity_log[-last_n:] if self.activity_log else []

# Global instance
connection_guard = MT5ConnectionGuard()


class MT5Context:
    """
    Context manager for safe MT5 operations
    Automatically handles connection acquisition and release
    """
    
    def __init__(self, requester_id: str, login: int, password: str, server: str):
        self.requester_id = requester_id
        self.login = login
        self.password = password
        self.server = server
        self.connection_result = None
    
    def __enter__(self):
        """Acquire MT5 connection"""
        self.connection_result = connection_guard.request_connection(
            self.requester_id, self.login, self.password, self.server
        )
        
        if self.connection_result['status'] not in ['connected', 'already_connected']:
            raise ConnectionError(f"Failed to acquire MT5 connection: {self.connection_result}")
        
        return self.connection_result
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release MT5 connection"""
        connection_guard.release_connection(self.requester_id)


def safe_mt5_operation(requester_id: str, login: int, password: str, server: str):
    """
    Decorator for safe MT5 operations
    
    Usage:
    @safe_mt5_operation("test_component", 95244786, "password", "server")
    def my_mt5_function():
        # MT5 operations here
        return mt5.account_info()
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with MT5Context(requester_id, login, password, server) as connection:
                return func(*args, **kwargs)
        return wrapper
    return decorator