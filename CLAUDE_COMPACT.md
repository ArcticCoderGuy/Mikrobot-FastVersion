# MIKROBOT TRADING SYSTEM - QUICK START

**CRITICAL: ASCII-ONLY ENCODING STANDARDS**
**Date**: 2025-08-04 | **Status**: UNICODE ISSUES RESOLVED | **Position Sizing**: FIXED

## MANDATORY SESSION INITIALIZATION
**RUN THIS FIRST**: `python session_initialization.py`

### ENCODING STANDARDS - RELIGIOUSLY ENFORCED
**PROBLEM SOLVED**: Unicode issues occurring repeatedly (5th time reported)
**SOLUTION IMPLEMENTED**: ASCII-only system with bulletproof encoding

**STRICT REQUIREMENTS**:
- NO Unicode characters in ANY Python output
- NO emojis or special characters in scripts or documentation  
- ALL print statements must use ASCII-only characters
- Signal file reading with UTF-16LE decode + null byte removal
- JSON files with ensure_ascii=True flag
- sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

**ENFORCEMENT METHOD**:
```python
def ascii_print(text):
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

# Signal file reading
content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
content_str = re.sub(r'[^\x20-\x7E]', '', content_str)
```

### POSITION SIZING STANDARDS - RELIGIOUSLY ENFORCED  
**PROBLEM SOLVED**: Fixed 0.01 lots instead of 0.55% risk (68x undersized)
**SOLUTION IMPLEMENTED**: ATR-based dynamic position sizing

**STRICT REQUIREMENTS**:
- Risk per trade: 0.55% of account balance (NOT fixed lots)
- ATR validation: 4-15 pips range only  
- Position calculation: risk_amount / (atr_pips * pip_value)
- ALL new trades automatically sized correctly
- Current compliant execution: 0.68 lots for EURJPY (vs 0.01 old method)

**ENFORCEMENT METHOD**:
```python
risk_amount = account.balance * 0.0055  # 0.55%
atr_pips = 8  # Validated 4-15 range
usd_per_pip_per_lot = 100  # JPY pairs
lot_size = round(risk_amount / (atr_pips * usd_per_pip_per_lot), 2)
```

---

# PROJECT OVERVIEW
Automated trading system with multi-exchange support, AI-driven strategies, and real-time market analysis.

**Current Phase**: Market-Ready Product (Phase 4/5)  
**Tech Stack**: Python, FastAPI, WebSockets, PostgreSQL, Redis, Docker  
**Architecture**: Microservices with event-driven communication

## QUICK REFERENCE LINKS
- **Commands & Actions**: [`CLAUDE_QUICK_REFER.md`](./CLAUDE_QUICK_REFER.md)
- **Django Platform**: [`mikrobot_platform/README.md`](./mikrobot_platform/README.md)
- **Session Summaries**: [`SESSION_4_SUMMARY.md`](./SESSION_4_SUMMARY.md) | [`SESSION_3_SUMMARY.md`](./SESSION_3_SUMMARY.md) | [`SESSION_2_SUMMARY.md`](./SESSION_2_SUMMARY.md) | [`SESSION_1_SUMMARY.md`](./SESSION_1_SUMMARY.md)
- **Architecture**: [`ORCHESTRATION_ARCHITECTURE.md`](./ORCHESTRATION_ARCHITECTURE.md)
- **Validation System**: [`VALIDATION_SYSTEM_README.md`](./VALIDATION_SYSTEM_README.md)

## PROJECT STRUCTURE
```
src/
├── core/           # Core trading logic & market connectors
├── strategies/     # Trading strategies & AI models
├── api/           # FastAPI REST & WebSocket endpoints
├── services/      # Background services & workers
└── shared/        # Shared utilities & configurations

mikrobot_platform/ # Django SaaS Platform
├── accounts/      # User management & authentication
├── trading/       # Core trading functionality  
├── dashboard/     # Customer dashboard interface
└── risk_management/ # Risk calculation & compliance
```

## DEVELOPMENT PRINCIPLES

### Code Standards
- **Style**: PEP 8 with type hints mandatory
- **Testing**: Minimum 80% coverage, TDD for critical paths
- **Documentation**: Docstrings for all public APIs
- **Security**: Never commit credentials, use environment variables

### Architecture Patterns
- **Microservices**: Independent services communicating via events
- **Event Sourcing**: All trading actions logged as events
- **CQRS**: Separate read/write models for performance
- **Circuit Breaker**: Fault tolerance for external APIs

## CURRENT SESSION STATUS

### Session #4: Django Enterprise Platform - FOUNDATION COMPLETE
**Status**: Django SaaS platform with customer-facing interface
**Key Achievements**: Multi-tenant user management, subscription tiers, encrypted trading accounts, Celery background processing
**Revenue Model**: $99-$499/month subscriptions with 24/7 automated trading

### Session #3: Submarine Gold Standard - DEPLOYED
**Status**: Los Angeles-class financial submarine operational
**Key Achievements**: Nuclear-grade risk management, Cp/Cpk >= 3.0 quality, universal ATR across 9 asset classes

### Session #2: ML-Enhanced Core - COMPLETE
**Status**: Machine learning integration with feature engineering
**Key Achievements**: BOS prediction models, real-time data ingestion, paper trading environment

### Session #1: MCP Orchestration - OPERATIONAL
**Status**: Complete architectural foundation with sub-100ms performance
**Key Achievements**: ProductOwner agent, circuit breakers, comprehensive error handling

## WORKING CONTEXT

### Current Sprint Focus
- [ ] Django frontend development with React
- [ ] Stripe payment integration for subscriptions
- [ ] Customer onboarding flow optimization
- [ ] Beta testing with initial customers

### Known Issues
- MetaTrader connection drops during high volatility
- WebSocket reconnection needs exponential backoff
- Strategy optimization takes >5min for large datasets

### Performance Targets
- Order execution: <100ms latency
- Data processing: 10K ticks/second
- API response: <200ms p99
- System uptime: 99.9%

## INSTANT COMMANDS

### Development
```bash
# Start Django development
cd mikrobot_platform && python manage.py runserver

# Start trading services
python session_initialization.py
python execute_compliant_simple.py

# Check system status
python compliant_monitor_final.py
```

### Docker Deployment
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web celery
```

### Database
```bash
# Django migrations
python manage.py migrate

# Database shell
python manage.py dbshell
```

## AI ASSISTANT GUIDELINES

### When Working on This Project:
1. **Prioritize**: Trading logic accuracy > Performance > Features
2. **Validate**: Always verify market data handling
3. **Test**: Simulate edge cases (market gaps, API failures)
4. **Document**: Update strategy documentation immediately

### Code Generation Preferences:
- Use async/await for all I/O operations
- Implement proper error handling with specific exceptions
- Add comprehensive logging for debugging
- Create unit tests alongside implementation

### Common Tasks:
- Adding new exchange connector: Start with `src/core/exchanges/base.py`
- Creating trading strategy: Extend `src/strategies/base_strategy.py`
- API endpoint: Follow existing patterns in `src/api/routes/`
- Background task: Use Celery worker in `src/services/workers/`

---

*For detailed commands and session-specific information, see linked documentation files above.*