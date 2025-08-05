# 🔌 MIKROBOT FASTVERSION - API Documentation

**Document Version:** 1.0  
**Last Updated:** 2025-08-03  
**Classification:** Technical Reference  
**Target Audience:** Developers, Integrators, System Architects

---

## 📋 Table of Contents

1. [API Overview](#api-overview)
2. [Authentication & Security](#authentication--security)
3. [Core Strategy API](#core-strategy-api)
4. [Signal Processing API](#signal-processing-api)
5. [Risk Management API](#risk-management-api)
6. [Performance Monitoring API](#performance-monitoring-api)
7. [XPWS Management API](#xpws-management-api)
8. [Integration Examples](#integration-examples)

---

## 🌐 API Overview

### Architecture

MIKROBOT FASTVERSION provides a comprehensive REST API and Python SDK for system integration, monitoring, and control.

```
┌─────────────────────────────────────────────────────────────┐
│                    MIKROBOT API LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  REST API Endpoints                                         │
│  ├── /api/v1/strategy/*     Strategy control & monitoring   │
│  ├── /api/v1/signals/*      Signal management               │
│  ├── /api/v1/risk/*         Risk management                 │
│  ├── /api/v1/performance/*  Performance metrics             │
│  └── /api/v1/xpws/*         XPWS system control             │
├─────────────────────────────────────────────────────────────┤
│  Python SDK                                                 │
│  ├── MikrobotClient         Main client class               │
│  ├── StrategyManager        Strategy operations             │
│  ├── SignalProcessor        Signal handling                 │
│  ├── RiskManager           Risk management                  │
│  └── PerformanceMonitor    Metrics and monitoring           │
├─────────────────────────────────────────────────────────────┤
│  WebSocket Streams                                          │
│  ├── /ws/signals           Real-time signals               │
│  ├── /ws/trades            Trade updates                   │
│  ├── /ws/performance       Performance metrics             │
│  └── /ws/alerts            System alerts                   │
└─────────────────────────────────────────────────────────────┘
```

### Base URLs

```
Production:  https://api.mikrobot.trading/v1
Staging:     https://staging-api.mikrobot.trading/v1
Development: http://localhost:8080/api/v1
```

### Response Format

All API responses follow a consistent format:

```json
{
    "success": true,
    "timestamp": "2025-08-03T15:30:00.000Z",
    "data": {
        // Response data
    },
    "meta": {
        "version": "1.0",
        "request_id": "req_123456789",
        "execution_time_ms": 45
    },
    "errors": []
}
```

---

## 🔐 Authentication & Security

### API Key Authentication

```http
GET /api/v1/strategy/status
Authorization: Bearer your_api_key_here
X-API-Version: 1.0
```

### Python SDK Authentication

```python
from mikrobot_api import MikrobotClient

client = MikrobotClient(
    api_key="your_api_key",
    account_id="your_mt5_account",
    environment="production"  # or "staging", "development"
)
```

### Rate Limiting

```
Rate Limits:
- General API: 1000 requests/hour
- Signal Processing: 100 requests/minute
- Real-time Monitoring: 10 requests/second
- Bulk Operations: 10 requests/minute
```

---

## 🎯 Core Strategy API

### Strategy Control Endpoints

#### Get Strategy Status

```http
GET /api/v1/strategy/status
```

**Response:**
```json
{
    "success": true,
    "data": {
        "strategy_active": true,
        "current_phase": "M1_MONITORING",
        "symbols_monitored": ["EURUSD", "GBPUSD", "USDJPY"],
        "active_positions": 3,
        "last_signal_time": "2025-08-03T15:25:00.000Z",
        "performance_summary": {
            "daily_pnl": 150.25,
            "weekly_pnl": 450.75,
            "win_rate": 0.68,
            "total_trades": 25
        }
    }
}
```

#### Start/Stop Strategy

```http
POST /api/v1/strategy/control
Content-Type: application/json

{
    "action": "start",  // "start", "stop", "pause", "resume"
    "symbols": ["EURUSD", "GBPUSD"],  // optional: specific symbols
    "parameters": {
        "risk_per_trade": 0.0055,
        "atr_min_pips": 4,
        "atr_max_pips": 15
    }
}
```

#### Get Strategy Configuration

```http
GET /api/v1/strategy/config
```

**Response:**
```json
{
    "success": true,
    "data": {
        "risk_per_trade": 0.0055,
        "ylipip_trigger": 0.6,
        "atr_min_pips": 4,
        "atr_max_pips": 15,
        "xpws_threshold": 0.10,
        "magic_number": 999888,
        "supported_symbols": {
            "forex_majors": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF"],
            "cfd_indices": ["US30", "US500", "NAS100", "GER40"],
            "cfd_metals": ["XAUUSD", "XAGUSD"],
            "cfd_crypto": ["BTCUSD", "ETHUSD"]
        }
    }
}
```

### Python SDK - Strategy Manager

```python
from mikrobot_api import MikrobotClient

client = MikrobotClient(api_key="your_key")
strategy = client.strategy

# Get current status
status = strategy.get_status()
print(f"Strategy active: {status.active}")
print(f"Current phase: {status.phase}")

# Start strategy
result = strategy.start(
    symbols=["EURUSD", "GBPUSD"],
    risk_per_trade=0.0055
)

# Stop strategy
strategy.stop()

# Update configuration
strategy.update_config({
    "atr_min_pips": 5,
    "atr_max_pips": 12
})
```

---

## 📡 Signal Processing API

### Signal Endpoints

#### Get Recent Signals

```http
GET /api/v1/signals?limit=50&status=executed
```

**Response:**
```json
{
    "success": true,
    "data": {
        "signals": [
            {
                "signal_id": "sig_20250803_153000_001",
                "symbol": "EURUSD",
                "signal_type": "ENTRY_SIGNAL",
                "action": "BUY",
                "timestamp": "2025-08-03T15:30:00.000Z",
                "execution_price": 1.1000,
                "status": "EXECUTED",
                "strategy_data": {
                    "m5_bos_confirmed": true,
                    "m1_retest_completed": true,
                    "ylipip_trigger": 0.6,
                    "atr_value": 10.5
                }
            }
        ],
        "pagination": {
            "total": 150,
            "page": 1,
            "per_page": 50
        }
    }
}
```

#### Create Manual Signal

```http
POST /api/v1/signals
Content-Type: application/json

{
    "symbol": "EURUSD",
    "action": "BUY",
    "signal_type": "MANUAL_ENTRY",
    "volume": 0.01,
    "entry_price": 1.1000,
    "stop_loss": 1.0990,
    "take_profit": 1.1010,
    "comment": "Manual override signal"
}
```

#### Get Signal Details

```http
GET /api/v1/signals/{signal_id}
```

### Python SDK - Signal Processor

```python
from mikrobot_api import MikrobotClient

client = MikrobotClient(api_key="your_key")
signals = client.signals

# Get recent signals
recent_signals = signals.get_recent(limit=10, status="executed")

# Get specific signal
signal_detail = signals.get_by_id("sig_20250803_153000_001")

# Create manual signal
manual_signal = signals.create({
    "symbol": "EURUSD",
    "action": "BUY",
    "volume": 0.01,
    "signal_type": "MANUAL_ENTRY"
})

# Subscribe to real-time signals
def on_signal(signal_data):
    print(f"New signal: {signal_data.symbol} {signal_data.action}")

signals.subscribe(on_signal)
```

### WebSocket Signal Stream

```javascript
const ws = new WebSocket('wss://api.mikrobot.trading/ws/signals');

ws.onmessage = function(event) {
    const signal = JSON.parse(event.data);
    console.log('New signal:', signal);
    
    // Signal structure:
    // {
    //     "signal_id": "sig_123",
    //     "symbol": "EURUSD",
    //     "action": "BUY",
    //     "timestamp": "2025-08-03T15:30:00.000Z",
    //     "strategy_phase": "YLIPIP_TRIGGER"
    // }
};
```

---

## 🛡️ Risk Management API

### Risk Control Endpoints

#### Get Current Risk Status

```http
GET /api/v1/risk/status
```

**Response:**
```json
{
    "success": true,
    "data": {
        "daily_risk_used": 0.023,
        "daily_risk_limit": 0.05,
        "max_drawdown": 0.012,
        "drawdown_limit": 0.10,
        "position_count": 3,
        "position_limit": 10,
        "correlation_risk": 0.45,
        "correlation_limit": 0.70,
        "risk_level": "LOW",
        "ftmo_compliant": true
    }
}
```

#### Validate Trade Risk

```http
POST /api/v1/risk/validate
Content-Type: application/json

{
    "symbol": "EURUSD",
    "action": "BUY",
    "volume": 0.01,
    "stop_loss_pips": 10
}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "risk_valid": true,
        "risk_percentage": 0.0055,
        "position_size_valid": true,
        "correlation_check": "PASS",
        "ftmo_compliant": true,
        "warnings": [],
        "risk_metrics": {
            "estimated_loss": 55.00,
            "account_impact": 0.0055,
            "total_exposure": 1100.00
        }
    }
}
```

#### Get Risk Limits

```http
GET /api/v1/risk/limits
```

### Python SDK - Risk Manager

```python
from mikrobot_api import MikrobotClient

client = MikrobotClient(api_key="your_key")
risk = client.risk

# Get current risk status
status = risk.get_status()
print(f"Daily risk used: {status.daily_risk_used:.2%}")
print(f"FTMO compliant: {status.ftmo_compliant}")

# Validate trade before execution
validation = risk.validate_trade(
    symbol="EURUSD",
    action="BUY",
    volume=0.01,
    stop_loss_pips=10
)

if validation.risk_valid:
    print("Trade approved for execution")
else:
    print(f"Trade rejected: {validation.warnings}")

# Set custom risk limits
risk.update_limits({
    "daily_risk_limit": 0.03,  # 3% instead of default 5%
    "position_limit": 5        # Max 5 positions
})

# Get risk metrics history
risk_history = risk.get_history(days=30)
```

---

## 📊 Performance Monitoring API

### Performance Endpoints

#### Get Performance Summary

```http
GET /api/v1/performance/summary?period=30d
```

**Response:**
```json
{
    "success": true,
    "data": {
        "period": "30d",
        "total_trades": 156,
        "winning_trades": 106,
        "losing_trades": 50,
        "win_rate": 0.679,
        "profit_factor": 1.85,
        "total_pnl": 2450.75,
        "avg_profit": 35.20,
        "avg_loss": -18.90,
        "max_consecutive_wins": 8,
        "max_consecutive_losses": 3,
        "sharpe_ratio": 1.45,
        "max_drawdown": 0.085,
        "recovery_factor": 2.1
    }
}
```

#### Get Trade History

```http
GET /api/v1/performance/trades?symbol=EURUSD&limit=100
```

#### Get System Metrics

```http
GET /api/v1/performance/system
```

**Response:**
```json
{
    "success": true,
    "data": {
        "system_health": {
            "uptime_percentage": 99.95,
            "signal_latency_avg_ms": 45,
            "execution_latency_avg_ms": 320,
            "error_rate": 0.002
        },
        "resource_usage": {
            "cpu_usage_percent": 15,
            "memory_usage_mb": 180,
            "disk_io_mb_per_hour": 12
        },
        "mt5_connectivity": {
            "connection_status": "CONNECTED",
            "last_heartbeat": "2025-08-03T15:30:00.000Z",
            "ping_ms": 25
        }
    }
}
```

### Python SDK - Performance Monitor

```python
from mikrobot_api import MikrobotClient

client = MikrobotClient(api_key="your_key")
performance = client.performance

# Get performance summary
summary = performance.get_summary(period="30d")
print(f"Win rate: {summary.win_rate:.2%}")
print(f"Profit factor: {summary.profit_factor:.2f}")

# Get trade history with filters
trades = performance.get_trades(
    symbol="EURUSD",
    date_from="2025-07-01",
    date_to="2025-08-03",
    status="closed"
)

# Get real-time system metrics
metrics = performance.get_system_metrics()
print(f"Signal latency: {metrics.signal_latency_avg_ms}ms")
print(f"System uptime: {metrics.uptime_percentage:.2%}")

# Subscribe to performance updates
def on_performance_update(data):
    print(f"New trade closed: {data.symbol} {data.pnl}")

performance.subscribe_updates(on_performance_update)

# Generate performance report
report = performance.generate_report(
    period="weekly",
    include_charts=True,
    format="pdf"
)
```

---

## 🎖️ XPWS Management API

### XPWS Endpoints

#### Get XPWS Status

```http
GET /api/v1/xpws/status
```

**Response:**
```json
{
    "success": true,
    "data": {
        "xpws_enabled": true,
        "current_week": "2025-W31",
        "active_symbols": ["EURUSD", "GBPUSD"],
        "weekly_profits": {
            "EURUSD": {
                "profit_percentage": 12.5,
                "xpws_active": true,
                "activation_date": "2025-08-01T14:30:00.000Z"
            },
            "GBPUSD": {
                "profit_percentage": 8.2,
                "xpws_active": false
            },
            "USDJPY": {
                "profit_percentage": 15.1,
                "xpws_active": true,
                "activation_date": "2025-07-31T09:15:00.000Z"
            }
        },
        "enhanced_trades": 8,
        "additional_profit": 350.25
    }
}
```

#### Manual XPWS Control

```http
POST /api/v1/xpws/control
Content-Type: application/json

{
    "action": "activate",  // "activate", "deactivate", "reset"
    "symbol": "EURUSD",
    "force": false  // Force activation even if threshold not met
}
```

#### Get XPWS Performance

```http
GET /api/v1/xpws/performance?weeks=4
```

### Python SDK - XPWS Manager

```python
from mikrobot_api import MikrobotClient

client = MikrobotClient(api_key="your_key")
xpws = client.xpws

# Get current XPWS status
status = xpws.get_status()
print(f"XPWS active symbols: {status.active_symbols}")

# Check specific symbol XPWS status
eurusd_status = xpws.get_symbol_status("EURUSD")
if eurusd_status.xpws_active:
    print(f"EURUSD XPWS active since {eurusd_status.activation_date}")

# Manual XPWS activation (for testing)
xpws.activate_symbol("GBPUSD", force=True)

# Get XPWS performance history
performance = xpws.get_performance(weeks=8)
print(f"Additional profit from XPWS: ${performance.additional_profit}")

# Configure XPWS settings
xpws.update_config({
    "weekly_threshold": 0.12,  # Change to 12% threshold
    "risk_reward_ratio": 2.5   # Change to 1:2.5 instead of 1:2
})

# Subscribe to XPWS events
def on_xpws_event(event):
    if event.type == "ACTIVATION":
        print(f"XPWS activated for {event.symbol}")
    elif event.type == "WEEKLY_RESET":
        print("Weekly XPWS reset completed")

xpws.subscribe_events(on_xpws_event)
```

---

## 🔧 Integration Examples

### Complete Trading Bot Integration

```python
import asyncio
from mikrobot_api import MikrobotClient

class TradingBotIntegration:
    def __init__(self, api_key, account_id):
        self.client = MikrobotClient(
            api_key=api_key,
            account_id=account_id
        )
        
    async def start_monitoring(self):
        """Start comprehensive monitoring and control"""
        
        # Initialize components
        strategy = self.client.strategy
        risk = self.client.risk
        performance = self.client.performance
        xpws = self.client.xpws
        
        # Start strategy
        await strategy.start(symbols=["EURUSD", "GBPUSD", "USDJPY"])
        
        # Setup real-time monitoring
        await self.setup_monitoring()
        
        # Main monitoring loop
        while True:
            await self.monitor_cycle()
            await asyncio.sleep(30)  # Check every 30 seconds
            
    async def setup_monitoring(self):
        """Setup real-time event handlers"""
        
        # Signal monitoring
        def on_signal(signal):
            print(f"New signal: {signal.symbol} {signal.action}")
            self.log_signal(signal)
            
        # Trade monitoring
        def on_trade_update(trade):
            print(f"Trade update: {trade.symbol} P&L: {trade.pnl}")
            self.update_dashboard(trade)
            
        # Risk monitoring
        def on_risk_alert(alert):
            if alert.severity == "CRITICAL":
                self.handle_risk_emergency(alert)
            else:
                self.log_risk_warning(alert)
                
        # XPWS monitoring
        def on_xpws_event(event):
            if event.type == "ACTIVATION":
                self.notify_xpws_activation(event.symbol)
                
        # Subscribe to events
        self.client.signals.subscribe(on_signal)
        self.client.trades.subscribe(on_trade_update)
        self.client.risk.subscribe_alerts(on_risk_alert)
        self.client.xpws.subscribe_events(on_xpws_event)
        
    async def monitor_cycle(self):
        """Periodic monitoring and health checks"""
        
        # Check strategy status
        strategy_status = await self.client.strategy.get_status()
        if not strategy_status.active:
            await self.handle_strategy_stop()
            
        # Check risk levels
        risk_status = await self.client.risk.get_status()
        if risk_status.daily_risk_used > 0.04:  # 4% warning level
            await self.send_risk_warning()
            
        # Check system performance
        metrics = await self.client.performance.get_system_metrics()
        if metrics.signal_latency_avg_ms > 100:
            await self.optimize_performance()
            
        # Generate reports if needed
        if self.should_generate_report():
            await self.generate_daily_report()
            
    async def handle_risk_emergency(self, alert):
        """Emergency risk management"""
        
        # Stop all new trades
        await self.client.strategy.stop()
        
        # Close risky positions if needed
        if alert.type == "DRAWDOWN_CRITICAL":
            await self.emergency_position_closure()
            
        # Send urgent notifications
        await self.send_urgent_alert(alert)
        
    async def generate_daily_report(self):
        """Generate comprehensive daily report"""
        
        # Get performance data
        performance = await self.client.performance.get_summary(period="1d")
        
        # Get XPWS status
        xpws_status = await self.client.xpws.get_status()
        
        # Get risk metrics
        risk_status = await self.client.risk.get_status()
        
        # Compile report
        report = {
            "date": "2025-08-03",
            "trades_executed": performance.total_trades,
            "daily_pnl": performance.total_pnl,
            "win_rate": performance.win_rate,
            "risk_utilization": risk_status.daily_risk_used,
            "xpws_active_symbols": xpws_status.active_symbols,
            "system_health": "EXCELLENT"
        }
        
        # Send report
        await self.send_report(report)

# Usage
async def main():
    bot = TradingBotIntegration(
        api_key="your_api_key",
        account_id="your_mt5_account"
    )
    
    await bot.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Dashboard Integration

```javascript
// JavaScript/React Dashboard Integration
import { MikrobotAPIClient } from '@mikrobot/api-client';

class MikrobotDashboard {
    constructor(apiKey) {
        this.client = new MikrobotAPIClient(apiKey);
        this.wsConnections = {};
    }
    
    async initialize() {
        // Setup WebSocket connections
        await this.setupWebSockets();
        
        // Load initial data
        await this.loadInitialData();
        
        // Start real-time updates
        this.startRealTimeUpdates();
    }
    
    async setupWebSockets() {
        // Signals stream
        this.wsConnections.signals = new WebSocket(
            'wss://api.mikrobot.trading/ws/signals'
        );
        this.wsConnections.signals.onmessage = (event) => {
            const signal = JSON.parse(event.data);
            this.updateSignalsDisplay(signal);
        };
        
        // Performance stream
        this.wsConnections.performance = new WebSocket(
            'wss://api.mikrobot.trading/ws/performance'
        );
        this.wsConnections.performance.onmessage = (event) => {
            const metrics = JSON.parse(event.data);
            this.updatePerformanceDisplay(metrics);
        };
        
        // Trade updates stream
        this.wsConnections.trades = new WebSocket(
            'wss://api.mikrobot.trading/ws/trades'
        );
        this.wsConnections.trades.onmessage = (event) => {
            const trade = JSON.parse(event.data);
            this.updateTradesDisplay(trade);
        };
    }
    
    async loadInitialData() {
        try {
            // Load strategy status
            const strategyStatus = await this.client.strategy.getStatus();
            this.displayStrategyStatus(strategyStatus);
            
            // Load performance summary
            const performance = await this.client.performance.getSummary('7d');
            this.displayPerformanceSummary(performance);
            
            // Load XPWS status
            const xpwsStatus = await this.client.xpws.getStatus();
            this.displayXPWSStatus(xpwsStatus);
            
            // Load recent trades
            const recentTrades = await this.client.performance.getTrades({
                limit: 10,
                status: 'closed'
            });
            this.displayRecentTrades(recentTrades);
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.displayError(error);
        }
    }
    
    updateSignalsDisplay(signal) {
        const signalElement = document.createElement('div');
        signalElement.className = 'signal-item';
        signalElement.innerHTML = `
            <div class="signal-header">
                <span class="symbol">${signal.symbol}</span>
                <span class="action ${signal.action.toLowerCase()}">${signal.action}</span>
                <span class="time">${new Date(signal.timestamp).toLocaleTimeString()}</span>
            </div>
            <div class="signal-details">
                <span>Entry: ${signal.entry_price}</span>
                <span>SL: ${signal.stop_loss}</span>
                <span>TP: ${signal.take_profit}</span>
            </div>
        `;
        
        document.getElementById('signals-list').prepend(signalElement);
    }
    
    updatePerformanceDisplay(metrics) {
        document.getElementById('daily-pnl').textContent = 
            `$${metrics.daily_pnl.toFixed(2)}`;
        document.getElementById('win-rate').textContent = 
            `${(metrics.win_rate * 100).toFixed(1)}%`;
        document.getElementById('signal-latency').textContent = 
            `${metrics.signal_latency_ms}ms`;
        document.getElementById('uptime').textContent = 
            `${metrics.uptime_percentage.toFixed(2)}%`;
    }
    
    // Control functions
    async startStrategy() {
        try {
            await this.client.strategy.start();
            this.showNotification('Strategy started successfully', 'success');
        } catch (error) {
            this.showNotification('Failed to start strategy', 'error');
        }
    }
    
    async stopStrategy() {
        try {
            await this.client.strategy.stop();
            this.showNotification('Strategy stopped successfully', 'success');
        } catch (error) {
            this.showNotification('Failed to stop strategy', 'error');
        }
    }
    
    async activateXPWS(symbol) {
        try {
            await this.client.xpws.activateSymbol(symbol);
            this.showNotification(`XPWS activated for ${symbol}`, 'success');
        } catch (error) {
            this.showNotification('Failed to activate XPWS', 'error');
        }
    }
}

// Initialize dashboard
const dashboard = new MikrobotDashboard('your_api_key');
dashboard.initialize();
```

### Risk Management Integration

```python
from mikrobot_api import MikrobotClient
import pandas as pd
import numpy as np

class AdvancedRiskManager:
    def __init__(self, api_key):
        self.client = MikrobotClient(api_key=api_key)
        self.risk_limits = {
            'max_daily_risk': 0.03,
            'max_drawdown': 0.08,
            'max_correlation': 0.60,
            'max_positions': 8
        }
        
    async def enhanced_risk_monitoring(self):
        """Advanced risk monitoring with custom rules"""
        
        while True:
            # Get current positions
            positions = await self.client.performance.get_open_positions()
            
            # Analyze portfolio risk
            portfolio_risk = self.analyze_portfolio_risk(positions)
            
            # Check custom risk rules
            violations = self.check_custom_rules(portfolio_risk)
            
            if violations:
                await self.handle_risk_violations(violations)
                
            # Dynamic position sizing
            await self.adjust_position_sizing(portfolio_risk)
            
            await asyncio.sleep(60)  # Check every minute
            
    def analyze_portfolio_risk(self, positions):
        """Analyze current portfolio risk metrics"""
        
        if not positions:
            return {'total_risk': 0, 'correlation_matrix': None}
            
        # Calculate position correlations
        symbols = [pos['symbol'] for pos in positions]
        correlation_matrix = self.calculate_correlations(symbols)
        
        # Calculate total portfolio risk
        total_exposure = sum(pos['volume'] * pos['entry_price'] for pos in positions)
        total_risk = sum(pos['risk_amount'] for pos in positions)
        
        return {
            'total_risk': total_risk,
            'total_exposure': total_exposure,
            'correlation_matrix': correlation_matrix,
            'position_count': len(positions),
            'risk_concentration': self.calculate_risk_concentration(positions)
        }
        
    def check_custom_rules(self, portfolio_risk):
        """Check custom risk management rules"""
        
        violations = []
        
        # Check total risk
        if portfolio_risk['total_risk'] > self.risk_limits['max_daily_risk']:
            violations.append({
                'type': 'TOTAL_RISK_EXCEEDED',
                'current': portfolio_risk['total_risk'],
                'limit': self.risk_limits['max_daily_risk']
            })
            
        # Check position count
        if portfolio_risk['position_count'] > self.risk_limits['max_positions']:
            violations.append({
                'type': 'POSITION_LIMIT_EXCEEDED',
                'current': portfolio_risk['position_count'],
                'limit': self.risk_limits['max_positions']
            })
            
        # Check correlation risk
        max_correlation = self.get_max_correlation(portfolio_risk['correlation_matrix'])
        if max_correlation > self.risk_limits['max_correlation']:
            violations.append({
                'type': 'CORRELATION_RISK_HIGH',
                'current': max_correlation,
                'limit': self.risk_limits['max_correlation']
            })
            
        return violations
        
    async def handle_risk_violations(self, violations):
        """Handle risk rule violations"""
        
        for violation in violations:
            if violation['type'] == 'TOTAL_RISK_EXCEEDED':
                # Reduce position sizes
                await self.reduce_position_sizes(0.8)  # Reduce by 20%
                
            elif violation['type'] == 'CORRELATION_RISK_HIGH':
                # Close most correlated positions
                await self.close_correlated_positions()
                
            # Log violation
            await self.log_risk_violation(violation)
            
            # Send alert
            await self.send_risk_alert(violation)
```

---

## 📞 Support and Resources

### API Support

**Documentation:**
- Complete endpoint reference
- Code examples in multiple languages
- Integration guides and tutorials
- Best practices documentation

**Developer Resources:**
- Python SDK source code
- JavaScript/TypeScript client library
- Postman collection for testing
- OpenAPI specification

**Technical Support:**
- API key management
- Rate limit optimization
- Custom integration assistance
- Performance optimization guidance

### Rate Limits and Quotas

```
API Tier Limits:
Starter:    1,000 requests/hour
Professional: 10,000 requests/hour  
Enterprise: 100,000 requests/hour
Custom:     Unlimited with SLA
```

---

This API documentation provides comprehensive integration capabilities for the MIKROBOT FASTVERSION system, enabling developers to build custom applications, dashboards, and automated trading solutions.