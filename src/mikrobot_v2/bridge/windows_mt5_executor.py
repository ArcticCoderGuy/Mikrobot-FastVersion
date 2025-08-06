"""
WINDOWS MT5 EXECUTOR
====================

Runs on Windows machine with MT5 installed
Receives signals from Mac and executes real trades
"""

import MetaTrader5 as mt5
from flask import Flask, request, jsonify
import threading
import time
import json
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class MT5Executor:
    """Execute trades on Windows MT5"""
    
    def __init__(self):
        self.account = 95244786
        self.password = "Ua@tOnLp"
        self.server = "MetaQuotesDemo"
        self.connected = False
        self.mac_webhook = "http://192.168.0.114:8000/bridge/webhook/mt5-confirmation"
        
    def connect(self):
        """Connect to MT5"""
        if not mt5.initialize():
            logger.error(f"MT5 initialization failed: {mt5.last_error()}")
            return False
            
        if not mt5.login(self.account, self.password, self.server):
            logger.error(f"MT5 login failed: {mt5.last_error()}")
            mt5.shutdown()
            return False
        
        self.connected = True
        account_info = mt5.account_info()
        logger.info(f"✅ Connected to MT5: {account_info.login}, Balance: {account_info.balance}")
        return True
    
    def execute_trade(self, signal):
        """Execute trade on MT5"""
        if not self.connected:
            if not self.connect():
                return {'error': 'MT5 connection failed'}
        
        symbol = signal['symbol']
        action = signal['action']
        volume = float(signal.get('volume', 0.01))
        
        # Get current price if not specified
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            return {'error': f'Symbol {symbol} not found'}
        
        price = signal.get('price', tick.ask if action == 'BUY' else tick.bid)
        
        # Prepare request
        order_type = mt5.ORDER_TYPE_BUY if action == 'BUY' else mt5.ORDER_TYPE_SELL
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": signal.get('stop_loss', 0),
            "tp": signal.get('take_profit', 0),
            "deviation": 20,
            "magic": signal.get('magic', 20250806),
            "comment": signal.get('comment', 'MIKROBOT'),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Send order
        result = mt5.order_send(request)
        
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"Order failed: {result.retcode}")
            return {
                'error': f'Order failed: {result.retcode}',
                'comment': result.comment
            }
        
        logger.info(f"✅ Order executed: {result.order}")
        
        # Send confirmation back to Mac
        self.send_confirmation(signal, result)
        
        return {
            'success': True,
            'ticket': result.order,
            'deal': result.deal,
            'volume': result.volume,
            'price': result.price,
            'symbol': symbol,
            'action': action
        }
    
    def send_confirmation(self, signal, result):
        """Send trade confirmation back to Mac"""
        try:
            confirmation = {
                'signal_id': signal.get('signal_id'),
                'ticket': result.order,
                'deal': result.deal,
                'status': 'EXECUTED',
                'execution_time': datetime.now().isoformat(),
                'price': result.price,
                'volume': result.volume
            }
            
            requests.post(self.mac_webhook, json=confirmation, timeout=5)
            logger.info(f"✅ Confirmation sent to Mac")
            
        except Exception as e:
            logger.error(f"Failed to send confirmation: {e}")

executor = MT5Executor()

@app.route('/execute', methods=['POST'])
def execute_trade_endpoint():
    """Receive trade signal and execute on MT5"""
    try:
        signal = request.json
        logger.info(f"📨 Received signal: {signal}")
        
        result = executor.execute_trade(signal)
        
        return jsonify(result), 200 if 'success' in result else 400
        
    except Exception as e:
        logger.error(f"Execution error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Check MT5 connection status"""
    if executor.connected:
        account_info = mt5.account_info()
        return jsonify({
            'status': 'CONNECTED',
            'account': account_info.login,
            'balance': account_info.balance,
            'equity': account_info.equity,
            'margin': account_info.margin,
            'server': account_info.server
        })
    else:
        return jsonify({'status': 'DISCONNECTED'})

@app.route('/positions', methods=['GET'])
def get_positions():
    """Get open positions"""
    if not executor.connected:
        return jsonify({'error': 'Not connected'}), 400
    
    positions = mt5.positions_get()
    if positions:
        pos_list = []
        for pos in positions:
            pos_list.append({
                'ticket': pos.ticket,
                'symbol': pos.symbol,
                'type': 'BUY' if pos.type == 0 else 'SELL',
                'volume': pos.volume,
                'price': pos.price_open,
                'profit': pos.profit
            })
        return jsonify({'positions': pos_list})
    
    return jsonify({'positions': []})

def start_mt5_bridge():
    """Start the MT5 bridge server"""
    # Connect to MT5
    if executor.connect():
        logger.info("🚀 MT5 Bridge started on port 8001")
        app.run(host='0.0.0.0', port=8001)
    else:
        logger.error("Failed to start MT5 Bridge")

if __name__ == '__main__':
    start_mt5_bridge()