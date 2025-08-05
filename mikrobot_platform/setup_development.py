#!/usr/bin/env python3
"""
Development setup script for Mikrobot Trading Platform
Creates initial data and configuration for development environment
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from pathlib import Path

# Add the project directory to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mikrobot_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from trading.models import Strategy
from accounts.models import TradingAccount, UserProfile

User = get_user_model()

def create_superuser():
    """Create a superuser if it doesn't exist"""
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating superuser...")
        User.objects.create_superuser(
            username='admin',
            email='admin@mikrobot-platform.com',
            password='admin123',
            subscription_tier='ENTERPRISE',
            subscription_active=True
        )
        print("PASS: Superuser created: admin@mikrobot-platform.com / admin123")
    else:
        print("PASS: Superuser already exists")

def create_demo_user():
    """Create a demo user for testing"""
    demo_email = 'demo@mikrobot-platform.com'
    if not User.objects.filter(email=demo_email).exists():
        print("Creating demo user...")
        demo_user = User.objects.create_user(
            username='demo',
            email=demo_email,
            password='demo123',
            subscription_tier='PROFESSIONAL',
            subscription_active=True,
            risk_level='MODERATE',
            is_verified=True
        )
        
        # Create user profile
        UserProfile.objects.create(
            user=demo_user,
            first_name='Demo',
            last_name='User',
            country='Finland',
            trading_experience='INTERMEDIATE',
            preferred_trading_sessions=['LONDON', 'NEW_YORK']
        )
        
        print("PASS: Demo user created: demo@mikrobot-platform.com / demo123")
    else:
        print("PASS: Demo user already exists")

def create_strategies():
    """Create default trading strategies"""
    strategies = [
        {
            'name': 'M5 BOS + M1 Retest',
            'strategy_type': 'M5_BOS_M1_RETEST',
            'description': 'M5 Break of Structure with M1 Retest confirmation strategy',
            'default_risk_percent': 0.55,
            'min_atr_pips': 4,
            'max_atr_pips': 15,
            'max_concurrent_trades': 3,
            'supported_symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'EURJPY', 'GBPJPY'],
            'status': 'ACTIVE',
            'version': '1.0.0'
        },
        {
            'name': 'Submarine Gold Standard',
            'strategy_type': 'SUBMARINE_GOLD_STANDARD',
            'description': 'Los Angeles-class submarine operations with nuclear-grade risk management',
            'default_risk_percent': 0.55,
            'min_atr_pips': 4,
            'max_atr_pips': 15,
            'max_concurrent_trades': 5,
            'supported_symbols': [
                'EURUSD', 'GBPUSD', 'USDJPY', 'EURJPY', 'GBPJPY',
                'XAUUSD', 'GER40', 'BCHUSD', '_FERRARI.IT'
            ],
            'status': 'ACTIVE',
            'version': '3.0.0'
        },
        {
            'name': 'Ferrari Scalping',
            'strategy_type': 'FERRARI_SCALPING',
            'description': 'High-frequency scalping strategy for Italian stocks',
            'default_risk_percent': 0.75,
            'min_atr_pips': 5,
            'max_atr_pips': 20,
            'max_concurrent_trades': 2,
            'supported_symbols': ['_FERRARI.IT', '_STELLANTIS.IT'],
            'status': 'BETA',
            'version': '0.9.0'
        }
    ]
    
    for strategy_data in strategies:
        strategy, created = Strategy.objects.get_or_create(
            name=strategy_data['name'],
            defaults=strategy_data
        )
        if created:
            print(f"PASS: Strategy created: {strategy.name}")
        else:
            print(f"PASS: Strategy exists: {strategy.name}")

def setup_development_environment():
    """Main setup function"""
    print("ABOVE ROBUST: Setting up Mikrobot Trading Platform Development Environment")
    print("=" * 60)
    
    # Run migrations
    print("\n1. Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Create initial data
    print("\n2. Creating initial data...")
    create_superuser()
    create_demo_user()
    create_strategies()
    
    # Create directories
    print("\n3. Creating required directories...")
    directories = ['logs', 'media', 'staticfiles']
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"PASS: Directory created: {directory}")
    
    print("\n4. Development setup complete!")
    print("=" * 60)
    print("ABOVE ROBUST: Mikrobot Trading Platform is ready for development!")
    print("\nAccess URLs:")
    print("  - Admin Panel: http://localhost:8000/admin/")
    print("  - API Docs: http://localhost:8000/api/v1/")
    print("  - Dashboard: http://localhost:8000/dashboard/")
    print("\nCredentials:")
    print("  - Admin: admin@mikrobot-platform.com / admin123")
    print("  - Demo User: demo@mikrobot-platform.com / demo123")
    print("\nNext Steps:")
    print("  1. Copy .env.example to .env and configure your settings")
    print("  2. Run: python manage.py runserver")
    print("  3. Run: celery -A mikrobot_platform worker --loglevel=info")
    print("  4. Run: celery -A mikrobot_platform beat --loglevel=info")

if __name__ == '__main__':
    setup_development_environment()