# Mikrobot Trading Platform

Professional automated trading platform built with Django, providing enterprise-grade trading signal processing and portfolio management for prop traders and institutions.

## 🚀 Features

### Core Trading Platform
- **Multi-Strategy Support**: M5 BOS + M1 Retest, Submarine Gold Standard, Ferrari Scalping
- **Real-time Signal Processing**: Sub-5-second signal validation and execution
- **Multi-Asset Trading**: Forex, CFDs, Crypto, Indices, Metals, Energies
- **Risk Management**: FTMO-compliant position sizing with ATR-based calculations
- **Performance Analytics**: Real-time P&L tracking, win rates, risk metrics

### User Management
- **Subscription Tiers**: Basic ($99), Professional ($199), Enterprise ($499)
- **Secure Authentication**: 2FA, encrypted credentials, login history
- **Account Isolation**: Complete separation of customer trading accounts
- **Profile Management**: Risk preferences, trading sessions, notifications

### Technology Stack
- **Backend**: Django 4.2, Django REST Framework, PostgreSQL
- **Background Tasks**: Celery with Redis broker
- **Real-time**: WebSockets with Django Channels
- **Monitoring**: Structured logging, performance metrics
- **Deployment**: Docker, Nginx, production-ready configuration

## 🛠️ Quick Start

### 1. Development Setup

```bash
# Clone the repository
cd mikrobot_platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Setup development environment
python setup_development.py

# Run the development server
python manage.py runserver
```

### 2. Background Services

```bash
# Terminal 1: Celery Worker
celery -A mikrobot_platform worker --loglevel=info

# Terminal 2: Celery Beat Scheduler
celery -A mikrobot_platform beat --loglevel=info

# Terminal 3: Django Development Server
python manage.py runserver
```

### 3. Docker Deployment

```bash
# Build and start services
docker-compose up -d

# Check services status
docker-compose ps

# View logs
docker-compose logs -f web
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────┐
│          Web Interface (React/Django)           │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│         Django REST API                          │
│  ┌──────────┐  ┌─────────────┐  ┌────────────┐ │
│  │Auth/Users│  │Trading Logic│  │Risk Mgmt   │ │
│  └──────────┘  └─────────────┘  └────────────┘ │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│         Celery Background Tasks                  │
│  ┌──────────────┐  ┌─────────────────────────┐  │
│  │Signal Monitor│  │Trade Execution & Updates│  │
│  └──────────────┘  └─────────────────────────┘  │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│           MetaTrader 5 Integration               │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │User1 │  │User2 │  │User3 │  │UserN │       │
│  │ MT5  │  │ MT5  │  │ MT5  │  │ MT5  │       │
│  └──────┘  └──────┘  └──────┘  ┌──────┘       │
└─────────────────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DB_NAME=mikrobot_platform
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost

# Redis
REDIS_URL=redis://localhost:6379/1
CELERY_BROKER_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Payments
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key

# Security
SECRET_KEY=your-django-secret-key
ENCRYPTION_KEY=your-32-byte-encryption-key
```

### Trading Configuration

```python
MIKROBOT_SETTINGS = {
    'DEFAULT_RISK_PERCENT': 0.55,  # 0.55% risk per trade
    'MAX_CONCURRENT_TRADES': 5,
    'SIGNAL_TIMEOUT_SECONDS': 30,
    'SUPPORTED_STRATEGIES': [
        'M5_BOS_M1_RETEST',
        'SUBMARINE_GOLD_STANDARD',
    ],
}
```

## 📱 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/profile/` - User profile

### Trading
- `GET /api/v1/trading/sessions/` - Trading sessions
- `POST /api/v1/trading/sessions/` - Create trading session
- `GET /api/v1/trading/trades/` - Trade history
- `GET /api/v1/trading/signals/` - Signal history

### Risk Management
- `GET /api/v1/risk/metrics/` - Performance metrics
- `POST /api/v1/risk/calculate/` - Position size calculation
- `GET /api/v1/risk/limits/` - Risk limits status

## 🔐 Security Features

### Data Protection
- **Encrypted Credentials**: MT5 passwords encrypted with Fernet
- **User Isolation**: Complete account separation
- **Audit Logging**: Full action history tracking
- **Rate Limiting**: API endpoint protection
- **HTTPS Enforcement**: TLS 1.3 in production

### Authentication
- **JWT Tokens**: Secure API authentication
- **2FA Support**: TOTP-based two-factor authentication
- **Session Management**: Secure session handling
- **Login History**: Security monitoring

## 📈 Monitoring & Analytics

### Performance Metrics
- Real-time P&L tracking
- Win rate calculations
- Risk-adjusted returns
- Drawdown monitoring

### System Monitoring
- Celery task monitoring
- Database performance
- API response times
- Error rate tracking

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report

# Run specific app tests
python manage.py test trading.tests
```

## 🚀 Deployment

### Production Setup

1. **Server Requirements**
   - Ubuntu 20.04+ or similar
   - 4GB+ RAM
   - PostgreSQL 13+
   - Redis 6+
   - Nginx

2. **Environment Setup**
   ```bash
   # Copy production environment
   cp .env.example .env.production
   
   # Update production settings
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com
   ```

3. **Database Migration**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

4. **Service Deployment**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Scaling

- **Horizontal Scaling**: Multiple Celery workers
- **Load Balancing**: Nginx upstream configuration
- **Database**: PostgreSQL read replicas
- **Caching**: Redis cluster setup

## 📚 Documentation

- [API Documentation](docs/api.md)
- [Trading Strategies](docs/strategies.md)
- [Risk Management](docs/risk_management.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Support

- **Documentation**: [docs.mikrobot-platform.com](https://docs.mikrobot-platform.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/mikrobot-platform/issues)
- **Email**: support@mikrobot-platform.com

## 📄 License

This project is proprietary software. All rights reserved.

---

**Mikrobot Trading Platform** - Professional automated trading solution for the modern trader.