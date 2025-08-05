"""
Start Live MT5 Crypto Trading Bot
Using credentials from .env file
"""

import asyncio
import MetaTrader5 as mt5
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MT5 Configuration from .env
MT5_LOGIN = int(os.getenv('MT5_LOGIN', 107034605))
MT5_PASSWORD = os.getenv('MT5_PASSWORD', 'RcEw_s7w')
MT5_SERVER = os.getenv('MT5_SERVER', 'AVA-Demo 1-MT5')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def start_live_trading():
    """Connect to real MT5 and start trading"""
    try:
        logger.info("[INIT] Connecting to MT5...")
        
        # Initialize MT5
        if not mt5.initialize():
            logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False
        
        # Login with credentials from .env
        logger.info(f"[LOGIN] Account: {MT5_LOGIN}, Server: {MT5_SERVER}")
        authorized = mt5.login(
            login=MT5_LOGIN,
            password=MT5_PASSWORD,
            server=MT5_SERVER
        )
        
        if not authorized:
            logger.error(f"Login failed: {mt5.last_error()}")
            # Try with MetaQuotes-Demo server as fallback
            logger.info("[RETRY] Trying MetaQuotes-Demo server...")
            authorized = mt5.login(
                login=MT5_LOGIN,
                password=MT5_PASSWORD,
                server="MetaQuotes-Demo"
            )
            
            if not authorized:
                mt5.shutdown()
                return False
        
        # Get account info
        account_info = mt5.account_info()
        if account_info is None:
            logger.error("Failed to get account info")
            return False
        
        logger.info(f"[SUCCESS] Connected to MT5!")
        logger.info(f"[ACCOUNT] Number: {account_info.login}")
        logger.info(f"[BALANCE] EUR {account_info.balance:.2f}")
        logger.info(f"[EQUITY] EUR {account_info.equity:.2f}")
        logger.info(f"[LEVERAGE] {account_info.leverage}:1")
        
        # Check existing positions
        positions = mt5.positions_get()
        if positions:
            logger.info(f"[POSITIONS] Found {len(positions)} open positions:")
            for pos in positions:
                logger.info(f"  - {pos.symbol}: {pos.volume} lots, P&L: {pos.profit:.2f}")
                if pos.ticket == 398 or str(pos.ticket).startswith('398'):
                    logger.info(f"  *** This is your manual trade!")
        else:
            logger.info("[POSITIONS] No open positions")
        
        # Check crypto symbols
        crypto_symbols = ["BTCUSD", "ETHUSD", "XRPUSD", "ADAUSD"]
        available = []
        
        logger.info("[SYMBOLS] Checking crypto availability...")
        for symbol in crypto_symbols:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is not None:
                if mt5.symbol_select(symbol, True):
                    available.append(symbol)
                    logger.info(f"  - {symbol}: Available")
                else:
                    logger.warning(f"  - {symbol}: Cannot enable")
            else:
                logger.warning(f"  - {symbol}: Not found")
        
        if not available:
            logger.warning("[WARNING] No crypto symbols available")
            logger.info("[INFO] Checking what symbols ARE available...")
            
            # Get all symbols
            symbols = mt5.symbols_get()
            crypto_found = []
            for s in symbols:
                if any(crypto in s.name.upper() for crypto in ['BTC', 'ETH', 'XRP', 'ADA', 'CRYPTO']):
                    crypto_found.append(s.name)
            
            if crypto_found:
                logger.info(f"[FOUND] Crypto-related symbols: {', '.join(crypto_found[:10])}")
            else:
                logger.info("[INFO] No crypto symbols found. This might be a forex-only account.")
        
        logger.info("[STATUS] MT5 connection established and ready!")
        logger.info("[NOTE] Your manual position (398xxx) is visible in the same account")
        
        # Keep connection alive for monitoring
        logger.info("[MONITOR] Keeping connection alive... Press Ctrl+C to stop")
        while True:
            await asyncio.sleep(10)
            # Update account status
            account_info = mt5.account_info()
            if account_info:
                positions = mt5.positions_get()
                pos_count = len(positions) if positions else 0
                logger.info(f"[HEARTBEAT] Connected | Equity: {account_info.equity:.2f} | Positions: {pos_count}")
            
    except KeyboardInterrupt:
        logger.info("[STOP] Manual stop requested")
    except Exception as e:
        logger.error(f"[ERROR] {e}")
    finally:
        mt5.shutdown()
        logger.info("[CLEANUP] MT5 connection closed")

if __name__ == "__main__":
    print("=" * 60)
    print("MIKROBOT - LIVE MT5 CONNECTION TEST")
    print("=" * 60)
    print(f"Account: {MT5_LOGIN}")
    print(f"Server: {MT5_SERVER}")
    print("=" * 60)
    
    asyncio.run(start_live_trading())