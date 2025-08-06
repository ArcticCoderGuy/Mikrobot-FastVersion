"""
MIKROBOT MT5 CROSS-PLATFORM BRIDGE
===================================

Complete solution for Mac → Windows MT5 trading
Uses Django webhook + MT5 Bridge for real trades
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MikrobotMT5Bridge:
    """
    Cross-platform bridge for Mac → Windows MT5 trading
    """
    
    def __init__(self):
        self.active_signals = []
        self.executed_trades = []
        self.windows_bridge_url = "http://192.168.1.100:8001"  # Windows MT5 machine
        self.account_id = 95244786
        
    async def send_to_windows_mt5(self, signal: Dict) -> Dict:
        """Send trade signal to Windows MT5 machine"""
        
        async with aiohttp.ClientSession() as session:
            try:
                # Add Mikrobot-specific fields
                signal['magic'] = 20250806
                signal['comment'] = f"MIKROBOT_{signal.get('strategy', 'LB')}"
                signal['account'] = self.account_id
                
                async with session.post(
                    f"{self.windows_bridge_url}/execute",
                    json=signal,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        logger.info(f"✅ Trade sent to MT5: {signal['symbol']} {signal['action']}")
                        return result
                    else:
                        logger.error(f"❌ MT5 Bridge error: {result}")
                        return {'error': result}
                        
            except Exception as e:
                logger.error(f"Bridge connection failed: {e}")
                return {'error': str(e)}
    
    async def process_lightning_bolt_signal(self, lb_signal: Dict) -> Dict:
        """Process Lightning Bolt signal from Mikrobot v2"""
        
        # Convert Lightning Bolt signal to MT5 format
        mt5_signal = {
            'symbol': lb_signal['symbol'],
            'action': 'BUY' if lb_signal['direction'] == 'BULLISH' else 'SELL',
            'volume': lb_signal.get('atr_info', {}).get('position_size', 0.01),
            'price': lb_signal['entry_price'],
            'stop_loss': lb_signal['stop_loss'],
            'take_profit': lb_signal['take_profit'],
            'strategy': 'LIGHTNING_BOLT',
            'confidence': lb_signal['confidence'],
            'phase': lb_signal['phase'],
            'ylipip_offset': lb_signal.get('ylipip_offset', 0.6),
            'timestamp': datetime.now().isoformat(),
            'signal_id': f"LB_{int(datetime.now().timestamp())}"
        }
        
        # Send to Windows MT5
        result = await self.send_to_windows_mt5(mt5_signal)
        
        # Store signal
        self.active_signals.append({
            **mt5_signal,
            'mt5_result': result,
            'status': 'SENT' if 'error' not in result else 'FAILED'
        })
        
        return result

# Django webhook endpoints
mikrobot_bridge = MikrobotMT5Bridge()

@csrf_exempt
@require_http_methods(["POST"])
async def webhook_trading_signal(request):
    """
    Webhook endpoint for Mac Mikrobot → Windows MT5
    """
    try:
        signal = json.loads(request.body)
        
        # Validate required fields
        required = ['symbol', 'action', 'volume']
        if not all(field in signal for field in required):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # Process through bridge
        result = await mikrobot_bridge.send_to_windows_mt5(signal)
        
        return JsonResponse({
            'status': 'success',
            'signal_id': signal.get('signal_id'),
            'mt5_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
async def webhook_lightning_bolt(request):
    """
    Special webhook for Lightning Bolt signals
    """
    try:
        lb_signal = json.loads(request.body)
        result = await mikrobot_bridge.process_lightning_bolt_signal(lb_signal)
        
        return JsonResponse({
            'status': 'success',
            'strategy': 'LIGHTNING_BOLT',
            'result': result
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_bridge_status(request):
    """Get current bridge status and active signals"""
    
    return JsonResponse({
        'bridge_status': 'OPERATIONAL',
        'account': mikrobot_bridge.account_id,
        'active_signals': mikrobot_bridge.active_signals[-10:],
        'total_signals': len(mikrobot_bridge.active_signals),
        'executed_trades': len(mikrobot_bridge.executed_trades),
        'windows_bridge': mikrobot_bridge.windows_bridge_url
    })

@csrf_exempt
@require_http_methods(["POST"])
def mt5_confirmation(request):
    """Receive confirmation from Windows MT5"""
    
    try:
        confirmation = json.loads(request.body)
        signal_id = confirmation.get('signal_id')
        
        # Update signal status
        for signal in mikrobot_bridge.active_signals:
            if signal.get('signal_id') == signal_id:
                signal['mt5_ticket'] = confirmation.get('ticket')
                signal['status'] = 'EXECUTED'
                signal['execution_time'] = confirmation.get('execution_time')
                
                # Move to executed trades
                mikrobot_bridge.executed_trades.append(signal)
                break
        
        logger.info(f"✅ MT5 Confirmation: {confirmation}")
        return JsonResponse({'status': 'confirmed'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)