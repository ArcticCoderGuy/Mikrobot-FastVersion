# 📖 MIKROBOT FASTVERSION - User Manual

**Document Version:** 1.0  
**Last Updated:** 2025-08-03  
**Classification:** User Guide  
**Target Audience:** Traders, Account Managers, End Users

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Trading Strategy Overview](#trading-strategy-overview)
3. [XPWS System Operation](#xpws-system-operation)
4. [Risk Management Controls](#risk-management-controls)
5. [Performance Monitoring](#performance-monitoring)
6. [Daily Operations](#daily-operations)
7. [Mobile Trading](#mobile-trading)
8. [Troubleshooting Guide](#troubleshooting-guide)

---

## 🚀 Getting Started

### Welcome to MIKROBOT FASTVERSION

MIKROBOT FASTVERSION is an advanced automated trading system that executes the proven M5/M1 break-and-retest strategy with the innovative 0.6 ylipip trigger. The system is designed to work seamlessly across all MT5 asset classes while maintaining strict FTMO compliance.

### Key Benefits

✅ **Fully Automated Trading** - No manual intervention required  
✅ **FTMO Compliant** - Built-in risk management for prop firm trading  
✅ **Multi-Asset Support** - Works on Forex, Indices, Metals, Crypto, and more  
✅ **XPWS Enhanced Profits** - Automatic profit optimization system  
✅ **24/7 Operation** - Continuous market monitoring and execution  
✅ **Mobile Monitoring** - Real-time trade tracking on your phone  

### Quick Start Checklist

Before using MIKROBOT FASTVERSION, ensure:

- [ ] MetaTrader 5 is installed and running
- [ ] Trading account is connected and funded
- [ ] Expert Advisor is properly attached to chart
- [ ] AutoTrading is enabled (green "AutoTrading" button)
- [ ] Internet connection is stable
- [ ] Mobile MT5 app is configured (optional)

---

## 📈 Trading Strategy Overview

### The MIKROBOT Method

MIKROBOT FASTVERSION uses a systematic 4-phase approach to identify and execute high-probability trades:

#### Phase 1: M5 Structure Break Detection
- **What it does:** Monitors M5 timeframe for structure breaks
- **Your role:** None - fully automated
- **Indicator:** System status shows "Monitoring M5 BOS"

#### Phase 2: M1 Break Identification  
- **What it does:** Detects first M1 break after M5 confirmation
- **Your role:** None - system records break candle automatically
- **Indicator:** System status shows "M1 Break Detected"

#### Phase 3: M1 Retest Validation
- **What it does:** Waits for and validates price retest of break level
- **Your role:** None - automated quality assessment
- **Indicator:** System status shows "Retest Confirmed"

#### Phase 4: 0.6 Ylipip Entry Trigger
- **What it does:** Calculates precise entry point and executes trade
- **Your role:** None - automatic trade execution
- **Indicator:** You'll see trade appear in MT5 terminal

### Understanding the 0.6 Ylipip Trigger

The ylipip trigger is a sophisticated calculation that determines the exact entry point:

- **"Ylipip"** = Advanced pip calculation that works across all asset types
- **"0.6"** = The precise threshold that triggers trade execution
- **Universal** = Same 0.6 value works for Forex, Indices, Metals, Crypto, etc.

**Example:**
```
EURUSD M1 Break at 1.1000
Ylipip calculation: 1.1000 + (0.6 × pip value) = 1.1006
Entry trigger: When price reaches 1.1006
```

---

## 🎖️ XPWS System Operation

### What is XPWS?

**XPWS (Extra-Profit-Weekly-Strategy)** is an intelligent profit enhancement system that automatically activates when you achieve 10% weekly profit on any trading pair.

### How XPWS Works

#### Normal Operation (Standard Mode)
- **Risk-Reward:** 1:1 ratio
- **Trade Management:** Standard take-profit at 1:1
- **Weekly Tracking:** System monitors profit per symbol

#### XPWS Activation (Enhanced Mode)
- **Trigger:** 10% weekly profit achieved on any pair
- **Risk-Reward:** Switches to 1:2 ratio
- **Trade Management:** Move to breakeven at 1:1, continue to 1:2
- **Duration:** Remainder of the week
- **Reset:** Every Monday at market open

### XPWS Example Scenario

**Week Start (Monday):**
- EURUSD trades with 1:1 take-profit
- System tracks weekly performance

**Wednesday - 10% Weekly Profit Achieved:**
- XPWS automatically activates for EURUSD
- New EURUSD trades now target 1:2 risk-reward
- Other pairs remain in standard mode

**Trade Management in XPWS Mode:**
1. Trade enters at 1.1000, SL at 1.0990 (10 pip risk)
2. At 1.1010 (1:1 profit): Stop-loss moves to breakeven (1.1000)
3. Target remains at 1.1020 (1:2 profit)
4. Risk eliminated, only profit potential remains

**Benefits:**
- **No Additional Risk:** Once 1:1 is reached, trade is risk-free
- **Enhanced Profits:** Double the profit potential
- **Automatic Management:** No manual intervention required

---

## 🛡️ Risk Management Controls

### Built-in Protection Systems

MIKROBOT FASTVERSION includes multiple layers of risk protection:

#### ATR Dynamic Risk Control
- **Risk Per Trade:** Fixed at 0.55% of account balance
- **Position Sizing:** Automatically calculated based on ATR
- **Volatility Filter:** Only trades when ATR is between 4-15 pips
- **Stop Loss:** Positioned at ATR-calculated setup box boundary

#### FTMO Compliance Protection
- **Daily Loss Limit:** Maximum 5% daily loss (system enforced)
- **Maximum Drawdown:** 10% maximum drawdown protection
- **Position Correlation:** Prevents highly correlated positions
- **Trading Hours:** Respects major session times only

#### Account Safety Features
- **Emergency Stop:** Automatic trading halt if limits approached
- **Real-time Monitoring:** Continuous risk assessment
- **Alert System:** Immediate notifications of risk events
- **Recovery Protocols:** Automatic system recovery procedures

### Risk Monitoring Dashboard

You can monitor your risk levels in real-time:

| Risk Metric | Current | Limit | Status |
|-------------|---------|--------|--------|
| Daily Risk | 2.3% | 5.0% | ✅ Safe |
| Account Drawdown | 1.2% | 10.0% | ✅ Safe |
| Position Count | 3 | 10 | ✅ Normal |
| Correlation Risk | 0.45 | 0.70 | ✅ Low |

---

## 📊 Performance Monitoring

### Real-Time Performance Tracking

MIKROBOT provides comprehensive performance monitoring:

#### Trade Statistics
- **Total Trades:** Running count of executed trades
- **Win Rate:** Percentage of profitable trades
- **Average Profit:** Average profit per winning trade
- **Average Loss:** Average loss per losing trade
- **Profit Factor:** Ratio of total profits to total losses

#### System Performance
- **Signal Latency:** Time from signal to execution
- **Execution Speed:** Order processing time
- **System Uptime:** Operational availability percentage
- **Error Rate:** Frequency of system errors

#### Weekly XPWS Tracking
- **Symbol Performance:** Profit tracking per trading pair
- **XPWS Status:** Which symbols have XPWS active
- **Enhanced Profits:** Additional profits from XPWS mode
- **Weekly Reset:** Automatic Monday reset confirmation

### Performance Reports

The system generates automatic reports:

**Daily Summary (End of Trading Day):**
- Trades executed today
- P&L for the day
- Risk utilization
- System health status

**Weekly Performance Report (Monday Morning):**
- Weekly profit/loss breakdown
- XPWS activation summary
- Top performing symbols
- Risk management effectiveness

---

## 🔄 Daily Operations

### Morning Routine (Market Open)

1. **System Health Check**
   - Verify green AutoTrading button in MT5
   - Check Expert Advisor status (green smiley ☺️)
   - Confirm internet connection stability

2. **Account Status Review**
   - Current account balance
   - Open positions overview
   - Daily risk allocation remaining

3. **XPWS Status Check**
   - Review which symbols have XPWS active
   - Check weekly profit progress
   - Note any Monday resets

### During Trading Hours

**Hands-Free Operation:**
- MIKROBOT operates fully automatically
- No manual intervention required
- System handles all trade decisions

**Optional Monitoring:**
- Watch for trade notifications on mobile
- Review performance metrics periodically
- Monitor risk levels if desired

### Evening Routine (Market Close)

1. **Daily Performance Review**
   - Check daily P&L results
   - Review trades executed
   - Assess weekly progress toward XPWS activation

2. **System Status Verification**
   - Confirm system is ready for next session
   - Check for any error messages
   - Verify sufficient account balance

### Weekend Maintenance

**Saturday:**
- Review weekly performance report
- Check system logs for any issues
- Verify XPWS weekly resets occurred

**Sunday:**
- Prepare for new trading week
- Check for any system updates
- Confirm market schedule for the week

---

## 📱 Mobile Trading

### MT5 Mobile App Setup

MIKROBOT FASTVERSION provides full mobile visibility:

#### iPhone/Android Setup
1. Download "MetaTrader 5" from app store
2. Login with your trading account credentials
3. Enable push notifications
4. Configure alert preferences

#### Mobile Features
- **Real-time Trade Monitoring:** See all MIKROBOT trades live
- **Push Notifications:** Instant trade confirmations
- **Performance Tracking:** View profits, losses, and statistics
- **Account Balance:** Real-time balance updates
- **Position Management:** Monitor open trades

#### Push Notification Types
- **Trade Opened:** "MIKROBOT: EURUSD BUY opened at 1.1000"
- **Trade Closed:** "MIKROBOT: EURUSD BUY closed +15 pips profit"
- **XPWS Activation:** "MIKROBOT: XPWS activated for EURUSD"
- **Risk Alert:** "MIKROBOT: Daily risk approaching limit"

### Mobile Best Practices

**Do:**
✅ Keep notifications enabled for important alerts  
✅ Check mobile app during major news events  
✅ Monitor performance during first week of use  
✅ Use mobile for quick balance checks  

**Don't:**
❌ Manually close MIKROBOT trades from mobile  
❌ Change EA settings from mobile  
❌ Disable push notifications completely  
❌ Trade manually while MIKROBOT is active  

---

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### Issue: No Trades Being Executed

**Possible Causes:**
- AutoTrading is disabled
- Expert Advisor not properly attached
- No suitable market conditions
- ATR outside 4-15 pip range

**Solutions:**
1. Check AutoTrading button is green in MT5
2. Verify EA shows green smiley ☺️ on chart
3. Wait for suitable market conditions
4. Review Experts tab for error messages

#### Issue: Trades Closed Too Early

**Cause:** Manual intervention or settings error

**Solution:**
- Never manually close MIKROBOT trades
- Let the system manage trades automatically
- Check EA parameters are correct

#### Issue: XPWS Not Activating

**Possible Causes:**
- Weekly profit not yet at 10%
- Different trading pair needs to reach threshold
- Weekly reset occurred on Monday

**Solutions:**
1. Check weekly profit tracking in performance report
2. Verify profit calculation includes all trades
3. Wait for sufficient trades to accumulate profit

#### Issue: Risk Limit Warnings

**Possible Causes:**
- Multiple losing trades in one day
- Account balance decreased
- Position correlation too high

**Solutions:**
1. System will automatically stop new trades
2. Allow current trades to close naturally
3. Review risk settings if needed

#### Issue: Mobile Notifications Not Working

**Solutions:**
1. Check MT5 mobile app notification settings
2. Verify internet connection on mobile device
3. Re-link mobile app to MT5 account
4. Test notifications from MT5 desktop

### Emergency Procedures

#### If System Stops Working
1. **Immediate Action:** Manually close any open trades if necessary
2. **Diagnosis:** Check MT5 Experts tab for error messages
3. **Recovery:** Restart EA by removing and re-attaching
4. **Support:** Contact technical support if issues persist

#### If Account Hits Risk Limits
1. **Automatic Protection:** System stops new trades automatically
2. **Assessment:** Review what caused the limit to be reached
3. **Recovery:** Wait for trades to close and limits to reset
4. **Prevention:** Consider reducing risk per trade if needed

---

## 📞 Support and Resources

### Getting Help

**Technical Support:**
- System logs location: MT5 Experts tab
- Error messages: Always note exact error text
- Performance issues: Check system requirements

**Trading Support:**
- Strategy questions: Refer to MIKROBOT_FASTVERSION.md
- FTMO compliance: Built-in protection active
- Risk management: Automatic systems in place

### Additional Resources

**Documentation:**
- Complete system architecture documentation available
- Technical specifications for developers
- API documentation for integrations
- Maintenance and support procedures

**Performance Optimization:**
- Custom configuration for specific needs
- Enhanced monitoring solutions
- Professional setup services
- Training and education materials

---

## 🎯 Success Tips

### Maximizing MIKROBOT Performance

1. **Let It Work:** Allow the system to operate without manual intervention
2. **Monitor Performance:** Review daily and weekly reports regularly
3. **Understand XPWS:** Learn how the enhanced profit system works
4. **Respect Risk Limits:** Trust the built-in protection systems
5. **Stay Informed:** Keep up with system updates and improvements

### Best Practices

**For New Users:**
- Start with demo account to understand the system
- Monitor closely for first week to learn patterns
- Read all documentation thoroughly
- Ask questions when unsure

**For Experienced Users:**
- Focus on weekly performance trends
- Utilize XPWS system effectively
- Monitor correlation between different assets
- Consider scaling up after consistent performance

### Setting Realistic Expectations

**MIKROBOT FASTVERSION is designed for:**
- Consistent long-term performance
- FTMO challenge and funded account trading
- Professional risk management
- Automated, stress-free trading

**Realistic Performance Targets:**
- 5-15% monthly returns (depends on market conditions)
- 60-70% win rate typical for break-and-retest strategy
- XPWS activation 1-2 times per month on active pairs
- Minimal drawdown with proper risk management

---

## ✅ User Manual Summary

MIKROBOT FASTVERSION provides a complete automated trading solution with:

🎯 **Fully Automated Operation** - No manual trading required  
📈 **XPWS Profit Enhancement** - Automatic optimization when profitable  
🛡️ **FTMO Compliance** - Built-in risk protection  
📱 **Mobile Integration** - Complete visibility on your phone  
⚡ **Professional Performance** - Enterprise-grade execution  

**Remember:** MIKROBOT works best when allowed to operate automatically. Trust the system, monitor performance, and enjoy the benefits of professional automated trading.

---

*This user manual provides everything you need to successfully operate MIKROBOT FASTVERSION. For technical support or advanced configuration, refer to the complete documentation package.*