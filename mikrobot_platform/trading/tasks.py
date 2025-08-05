"""
Celery tasks for background trading operations
Continuous monitoring and execution of trading signals
"""

from celery import shared_task
from django.utils import timezone
from django.conf import settings
import MetaTrader5 as mt5
import json
import re
import logging
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, Optional

from .models import TradingSession, Signal, Trade, PerformanceMetrics
from accounts.models import TradingAccount
from .services.mt5_connector import MT5ConnectionManager
from .services.signal_processor import SignalProcessor
from .services.risk_calculator import RiskCalculator

logger = logging.getLogger('trading')


@shared_task(bind=True, max_retries=3)
def monitor_all_customer_signals(self):
    """
    Monitor signals for all active trading sessions
    Runs every 5 seconds via Celery Beat
    """
    try:
        active_sessions = TradingSession.objects.filter(
            is_active=True,
            auto_trading_enabled=True,
            trading_account__is_active=True
        ).select_related('user', 'trading_account', 'strategy')
        
        logger.info(f"Monitoring {active_sessions.count()} active trading sessions")
        
        processed_count = 0
        error_count = 0
        
        for session in active_sessions:
            try:
                result = process_session_signals.delay(session.id)
                processed_count += 1
                logger.debug(f"Queued signal processing for session {session.id}")
                
            except Exception as e:
                logger.error(f"Failed to queue session {session.id}: {str(e)}")
                error_count += 1
        
        logger.info(f"Signal monitoring complete: {processed_count} queued, {error_count} errors")
        
        return {
            'status': 'completed',
            'sessions_processed': processed_count,
            'errors': error_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as exc:
        logger.error(f"Critical error in monitor_all_customer_signals: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=5)
def process_session_signals(self, session_id):
    """
    Process signals for a specific trading session
    """
    try:
        session = TradingSession.objects.select_related(
            'user', 'trading_account', 'strategy'
        ).get(id=session_id)
        
        # Check if session can still trade today
        if not session.can_trade_today():
            logger.info(f"Session {session_id} has reached daily trade limit")
            return {'status': 'daily_limit_reached'}
        
        # Check daily loss limit
        if session.check_daily_loss_limit():
            logger.warning(f"Session {session_id} has exceeded daily loss limit")
            session.auto_trading_enabled = False
            session.save()
            return {'status': 'daily_loss_limit_exceeded'}
        
        # Read signal file
        signal_data = read_mt5_signal_file()
        if not signal_data:
            return {'status': 'no_signal'}
        
        # Check if signal is new
        last_timestamp = session.last_signal_time
        signal_timestamp = signal_data.get('timestamp')
        
        if last_timestamp and signal_timestamp <= last_timestamp:
            return {'status': 'signal_already_processed'}
        
        # Process the signal
        processor = SignalProcessor(session)
        result = processor.process_signal(signal_data)
        
        # Update session timestamp
        session.last_signal_time = timezone.make_aware(
            timezone.datetime.fromisoformat(signal_timestamp.replace('.', '-'))
        )
        session.save()
        
        logger.info(f"Signal processed for session {session_id}: {result['status']}")
        return result
        
    except TradingSession.DoesNotExist:
        logger.error(f"Trading session {session_id} not found")
        return {'status': 'session_not_found'}
        
    except Exception as exc:
        logger.error(f"Error processing session {session_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=30)


def read_mt5_signal_file() -> Optional[Dict[str, Any]]:
    """
    Read and parse MT5 signal file with proper encoding handling
    """
    signal_file_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
    
    try:
        if not signal_file_path.exists():
            return None
        
        # Read with binary mode and decode UTF-16LE
        with open(signal_file_path, 'rb') as f:
            content = f.read()
        
        # Decode UTF-16LE and clean
        content_str = content.decode('utf-16le', errors='ignore')
        content_str = content_str.replace('\x00', '')  # Remove null bytes
        content_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', content_str)  # ASCII only
        
        # Parse JSON
        signal_data = json.loads(content_str)
        
        # Validate required fields
        required_fields = [
            'timestamp', 'symbol', 'strategy', 'trade_direction',
            'phase_1_m5_bos', 'phase_2_m1_break', 'phase_3_m1_retest', 'phase_4_ylipip'
        ]
        
        for field in required_fields:
            if field not in signal_data:
                logger.error(f"Missing required field in signal: {field}")
                return None
        
        return signal_data
        
    except FileNotFoundError:
        logger.debug("Signal file not found")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse signal JSON: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reading signal file: {str(e)}")
        return None


@shared_task(bind=True)
def execute_trade(self, session_id, signal_id):
    """
    Execute a validated trading signal
    """
    try:
        session = TradingSession.objects.select_related(
            'trading_account', 'user', 'strategy'
        ).get(id=session_id)
        
        signal = Signal.objects.get(id=signal_id)
        
        # Connect to MT5
        connector = MT5ConnectionManager()
        if not connector.connect_account(session.trading_account):
            logger.error(f"Failed to connect to MT5 for session {session_id}")
            signal.status = 'REJECTED'
            signal.rejection_reason = 'MT5 connection failed'
            signal.save()
            return {'status': 'connection_failed'}
        
        try:
            # Calculate position size
            calculator = RiskCalculator(session)
            position_data = calculator.calculate_position_size(signal)
            
            if not position_data['can_trade']:
                signal.status = 'REJECTED'
                signal.rejection_reason = position_data['reason']
                signal.save()
                return {'status': 'rejected', 'reason': position_data['reason']}
            
            # Place trade
            trade_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": signal.symbol,
                "volume": position_data['lot_size'],
                "type": mt5.ORDER_TYPE_BUY if signal.trade_direction == 'BUY' else mt5.ORDER_TYPE_SELL,
                "price": float(signal.current_price),
                "sl": position_data['stop_loss'],
                "tp": position_data['take_profit'],
                "deviation": 20,
                "magic": 234000,
                "comment": f"MIKROBOT_{signal.strategy_type}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(trade_request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                # Create trade record
                trade = Trade.objects.create(
                    signal=signal,
                    trading_session=session,
                    mt5_ticket=result.order,
                    symbol=signal.symbol,
                    trade_type=signal.trade_direction,
                    volume=Decimal(str(result.volume)),
                    open_price=Decimal(str(result.price)),
                    stop_loss=Decimal(str(position_data['stop_loss'])),
                    take_profit=Decimal(str(position_data['take_profit'])),
                    risk_amount=Decimal(str(position_data['risk_amount'])),
                    status='OPEN',
                    open_time=timezone.now()
                )
                
                # Update signal status
                signal.status = 'EXECUTED'
                signal.processed_at = timezone.now()
                signal.save()
                
                # Update session statistics
                session.trades_today += 1
                session.save()
                
                logger.info(f"Trade executed successfully: {trade.mt5_ticket}")
                
                return {
                    'status': 'executed',
                    'trade_id': str(trade.id),
                    'mt5_ticket': result.order,
                    'volume': float(result.volume),
                    'price': float(result.price)
                }
            else:
                error_msg = f"Trade execution failed: {result.retcode if result else 'No result'}"
                logger.error(error_msg)
                
                signal.status = 'REJECTED'
                signal.rejection_reason = error_msg
                signal.save()
                
                return {'status': 'execution_failed', 'error': error_msg}
                
        finally:
            connector.disconnect()
            
    except Exception as exc:
        logger.error(f"Critical error in execute_trade: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def update_all_account_balances():
    """
    Update account balances for all active trading accounts
    Runs every minute
    """
    try:
        active_accounts = TradingAccount.objects.filter(
            is_active=True,
            auto_trading_enabled=True
        )
        
        updated_count = 0
        error_count = 0
        
        for account in active_accounts:
            try:
                connector = MT5ConnectionManager()
                if connector.connect_account(account):
                    account_info = mt5.account_info()
                    if account_info:
                        account.current_balance = Decimal(str(account_info.balance))
                        account.last_balance_update = timezone.now()
                        account.connection_status = 'CONNECTED'
                        account.save(update_fields=[
                            'current_balance', 'last_balance_update', 'connection_status'
                        ])
                        updated_count += 1
                    connector.disconnect()
                else:
                    account.connection_status = 'DISCONNECTED'
                    account.save(update_fields=['connection_status'])
                    
            except Exception as e:
                logger.error(f"Failed to update account {account.id}: {str(e)}")
                error_count += 1
        
        logger.info(f"Account balance update: {updated_count} updated, {error_count} errors")
        
        return {
            'status': 'completed',
            'updated': updated_count,
            'errors': error_count
        }
        
    except Exception as e:
        logger.error(f"Critical error in update_all_account_balances: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def monitor_open_trades():
    """
    Monitor and update open trades
    Check for TP/SL hits and update P&L
    """
    try:
        open_trades = Trade.objects.filter(status='OPEN').select_related(
            'trading_session__trading_account'
        )
        
        updated_count = 0
        closed_count = 0
        
        # Group trades by trading account to minimize connections
        accounts_trades = {}
        for trade in open_trades:
            account = trade.trading_session.trading_account
            if account not in accounts_trades:
                accounts_trades[account] = []
            accounts_trades[account].append(trade)
        
        for account, trades in accounts_trades.items():
            try:
                connector = MT5ConnectionManager()
                if not connector.connect_account(account):
                    continue
                
                for trade in trades:
                    # Get current position info from MT5
                    positions = mt5.positions_get(ticket=trade.mt5_ticket)
                    
                    if not positions:
                        # Position is closed, get from history
                        history = mt5.history_deals_get(ticket=trade.mt5_ticket)
                        if history and len(history) >= 2:  # Open + Close deals
                            close_deal = history[-1]  # Last deal should be close
                            
                            trade.close_price = Decimal(str(close_deal.price))
                            trade.close_time = timezone.make_aware(
                                timezone.datetime.fromtimestamp(close_deal.time)
                            )
                            trade.pnl = Decimal(str(close_deal.profit))
                            trade.commission = Decimal(str(close_deal.commission))
                            trade.swap = Decimal(str(close_deal.swap))
                            trade.status = 'CLOSED'
                            
                            # Determine close reason
                            if abs(float(close_deal.price) - float(trade.take_profit)) < 0.0001:
                                trade.close_reason = 'TP'
                            elif abs(float(close_deal.price) - float(trade.stop_loss)) < 0.0001:
                                trade.close_reason = 'SL'
                            else:
                                trade.close_reason = 'MANUAL'
                            
                            trade.save()
                            closed_count += 1
                            
                            # Update session daily P&L
                            session = trade.trading_session
                            session.daily_pnl += trade.pnl
                            session.save()
                            
                    else:
                        # Position is still open, update current P&L
                        position = positions[0]
                        trade.pnl = Decimal(str(position.profit))
                        trade.save(update_fields=['pnl'])
                        updated_count += 1
                
                connector.disconnect()
                
            except Exception as e:
                logger.error(f"Error monitoring trades for account {account.id}: {str(e)}")
        
        logger.info(f"Trade monitoring: {updated_count} updated, {closed_count} closed")
        
        return {
            'status': 'completed',
            'updated': updated_count,
            'closed': closed_count
        }
        
    except Exception as e:
        logger.error(f"Critical error in monitor_open_trades: {str(e)}")
        return {'status': 'error', 'message': str(e)}