"""
Trading models for Mikrobot Platform
Core trading functionality with position management and signal processing
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, TradingAccount
import uuid
from decimal import Decimal


class Strategy(models.Model):
    """Trading strategies available on the platform"""
    
    STRATEGY_TYPES = [
        ('M5_BOS_M1_RETEST', 'M5 Break of Structure + M1 Retest'),
        ('SUBMARINE_GOLD_STANDARD', 'Submarine Gold Standard'),
        ('FERRARI_SCALPING', 'Ferrari Scalping Strategy'),
        ('CUSTOM', 'Custom Strategy'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('BETA', 'Beta Testing'),
        ('DEPRECATED', 'Deprecated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    strategy_type = models.CharField(max_length=30, choices=STRATEGY_TYPES)
    description = models.TextField()
    
    # Strategy Parameters
    default_risk_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        default=0.55,
        validators=[MinValueValidator(0.1), MaxValueValidator(5.0)]
    )
    min_atr_pips = models.IntegerField(default=4)
    max_atr_pips = models.IntegerField(default=15)
    max_concurrent_trades = models.IntegerField(default=3)
    
    # Supported Assets
    supported_symbols = models.JSONField(
        default=list,
        help_text="List of supported trading symbols"
    )
    
    # Performance Tracking
    total_trades = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    total_pips = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'strategies'
        verbose_name = 'Strategy'
        verbose_name_plural = 'Strategies'
    
    def __str__(self):
        return f"{self.name} (v{self.version})"
    
    @property
    def win_rate(self):
        if self.total_trades == 0:
            return 0
        return (self.winning_trades / self.total_trades) * 100


class TradingSession(models.Model):
    """User's trading session configuration"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trading_sessions')
    trading_account = models.ForeignKey(TradingAccount, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    
    # Session Settings
    is_active = models.BooleanField(default=False)
    auto_trading_enabled = models.BooleanField(default=False)
    
    # Risk Management Override
    custom_risk_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.1), MaxValueValidator(5.0)]
    )
    daily_loss_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=500.00
    )
    
    # Session Statistics
    session_start = models.DateTimeField(auto_now_add=True)
    last_signal_time = models.DateTimeField(null=True, blank=True)
    trades_today = models.IntegerField(default=0)
    daily_pnl = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trading_sessions'
        verbose_name = 'Trading Session'
        verbose_name_plural = 'Trading Sessions'
        unique_together = ['user', 'strategy']
    
    def __str__(self):
        return f"{self.user.email} - {self.strategy.name}"
    
    @property
    def effective_risk_percent(self):
        """Get risk percentage to use for this session"""
        return float(self.custom_risk_percent or self.strategy.default_risk_percent)
    
    def can_trade_today(self):
        """Check if user can make more trades today"""
        max_trades = self.user.max_trades_per_day
        if max_trades == -1:  # Unlimited
            return True
        return self.trades_today < max_trades
    
    def check_daily_loss_limit(self):
        """Check if daily loss limit is exceeded"""
        return self.daily_pnl <= -abs(self.daily_loss_limit)


class Signal(models.Model):
    """Trading signals received from MT5 EAs"""
    
    SIGNAL_STATUS = [
        ('RECEIVED', 'Received'),
        ('VALIDATED', 'Validated'),
        ('EXECUTED', 'Executed'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]
    
    TRADE_DIRECTION = [
        ('BUY', 'Buy/Bull'),
        ('SELL', 'Sell/Bear'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Signal Source
    trading_session = models.ForeignKey(
        TradingSession, 
        on_delete=models.CASCADE, 
        related_name='signals'
    )
    source_ea = models.CharField(max_length=100, default='MIKROBOT_v8')
    
    # Signal Data
    symbol = models.CharField(max_length=20)
    strategy_type = models.CharField(max_length=50)
    trade_direction = models.CharField(max_length=4, choices=TRADE_DIRECTION)
    
    # 4-Phase Signal Data (M5 BOS + M1 Retest)
    phase_1_m5_bos = models.JSONField(help_text="M5 Break of Structure data")
    phase_2_m1_break = models.JSONField(help_text="M1 Break data")
    phase_3_m1_retest = models.JSONField(help_text="M1 Retest data")
    phase_4_ylipip = models.JSONField(help_text="Ylipip trigger data")
    
    # Price Data
    current_price = models.DecimalField(max_digits=10, decimal_places=5)
    ylipip_trigger = models.DecimalField(max_digits=5, decimal_places=2, default=0.6)
    
    # Processing
    status = models.CharField(max_length=20, choices=SIGNAL_STATUS, default='RECEIVED')
    validation_score = models.DecimalField(
        max_digits=5, 
        decimal_places=3, 
        null=True, 
        blank=True
    )
    rejection_reason = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    signal_timestamp = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'signals'
        verbose_name = 'Trading Signal'
        verbose_name_plural = 'Trading Signals'
        ordering = ['-received_at']
    
    def __str__(self):
        return f"{self.symbol} {self.trade_direction} - {self.status}"


class Trade(models.Model):
    """Executed trades tracking"""
    
    TRADE_STATUS = [
        ('PENDING', 'Pending'),
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    CLOSE_REASON = [
        ('TP', 'Take Profit'),
        ('SL', 'Stop Loss'),
        ('MANUAL', 'Manual Close'),
        ('TIMEOUT', 'Timeout'),
        ('SYSTEM', 'System Close'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Trade Source
    signal = models.OneToOneField(Signal, on_delete=models.CASCADE, related_name='trade')
    trading_session = models.ForeignKey(TradingSession, on_delete=models.CASCADE)
    
    # MT5 Trade Details
    mt5_ticket = models.BigIntegerField(unique=True)
    symbol = models.CharField(max_length=20)
    trade_type = models.CharField(max_length=4, choices=Signal.TRADE_DIRECTION)
    
    # Position Details
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    open_price = models.DecimalField(max_digits=10, decimal_places=5)
    close_price = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    
    # Risk Management
    stop_loss = models.DecimalField(max_digits=10, decimal_places=5)
    take_profit = models.DecimalField(max_digits=10, decimal_places=5)
    risk_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Trade Results
    status = models.CharField(max_length=20, choices=TRADE_STATUS, default='PENDING')
    pnl = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pips = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    commission = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    swap = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Close Details
    close_reason = models.CharField(max_length=20, choices=CLOSE_REASON, blank=True)
    close_comment = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    open_time = models.DateTimeField()
    close_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trades'
        verbose_name = 'Trade'
        verbose_name_plural = 'Trades'
        ordering = ['-open_time']
    
    def __str__(self):
        return f"{self.symbol} {self.trade_type} {self.volume} - {self.status}"
    
    @property
    def is_winning_trade(self):
        """Check if trade is profitable"""
        return self.pnl and self.pnl > 0
    
    @property
    def duration_minutes(self):
        """Trade duration in minutes"""
        if not self.close_time:
            return None
        delta = self.close_time - self.open_time
        return int(delta.total_seconds() / 60)


class PerformanceMetrics(models.Model):
    """Daily performance tracking per user"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performance_metrics')
    trading_account = models.ForeignKey(TradingAccount, on_delete=models.CASCADE)
    date = models.DateField()
    
    # Daily Statistics
    total_trades = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    
    # Financial Metrics
    gross_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_loss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Performance Ratios
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    profit_factor = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    risk_reward_ratio = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    
    # Risk Metrics
    max_drawdown = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    risk_percentage = models.DecimalField(max_digits=5, decimal_places=3, default=0)
    
    # Account Balance
    starting_balance = models.DecimalField(max_digits=15, decimal_places=2)
    ending_balance = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'performance_metrics'
        verbose_name = 'Performance Metrics'
        verbose_name_plural = 'Performance Metrics'
        unique_together = ['user', 'trading_account', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.email} - {self.date} - ${self.net_profit}"
    
    def calculate_metrics(self):
        """Calculate all performance metrics"""
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100
        
        if abs(self.gross_loss) > 0:
            self.profit_factor = abs(self.gross_profit / self.gross_loss)
        
        self.net_profit = self.gross_profit + self.gross_loss
        
        # Update ending balance
        self.ending_balance = self.starting_balance + self.net_profit