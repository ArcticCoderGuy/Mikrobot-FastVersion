"""
Django URL patterns for Mikrobot MT5 Bridge
"""

from django.urls import path
from . import mikrobot_mt5_bridge

app_name = 'bridge'

urlpatterns = [
    # Main trading signal webhook
    path('webhook/trading-signal/', mikrobot_mt5_bridge.webhook_trading_signal, name='trading_signal'),
    
    # Lightning Bolt specific webhook
    path('webhook/lightning-bolt/', mikrobot_mt5_bridge.webhook_lightning_bolt, name='lightning_bolt'),
    
    # MT5 confirmation from Windows
    path('webhook/mt5-confirmation/', mikrobot_mt5_bridge.mt5_confirmation, name='mt5_confirmation'),
    
    # Status endpoint
    path('status/', mikrobot_mt5_bridge.get_bridge_status, name='bridge_status'),
]