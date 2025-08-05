"""
Above Robust Trading URL Configuration
Submarine-grade trading endpoints
"""

from django.urls import path
from . import views

app_name = 'trading'

urlpatterns = [
    path('sessions/', views.trading_sessions, name='sessions'),
    path('sessions/create/', views.create_trading_session, name='create-session'),
    path('trades/', views.trades, name='trades'),
    path('signals/', views.signals, name='signals'),
    path('dashboard/', views.trading_dashboard, name='dashboard'),
]