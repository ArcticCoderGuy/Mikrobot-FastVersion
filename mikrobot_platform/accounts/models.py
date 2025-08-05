"""
User models for Mikrobot Trading Platform
Secure customer account management with encrypted credentials
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from cryptography.fernet import Fernet
from django.conf import settings
import uuid


class User(AbstractUser):
    """Extended user model with trading platform specific fields"""
    
    SUBSCRIPTION_CHOICES = [
        ('BASIC', 'Basic - $99/month'),
        ('PROFESSIONAL', 'Professional - $199/month'), 
        ('ENTERPRISE', 'Enterprise - $499/month'),
        ('TRIAL', 'Free Trial'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('CONSERVATIVE', 'Conservative (0.25%)'),
        ('MODERATE', 'Moderate (0.55%)'),
        ('AGGRESSIVE', 'Aggressive (1.0%)'),
        ('CUSTOM', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Subscription
    subscription_tier = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_CHOICES, 
        default='TRIAL'
    )
    subscription_active = models.BooleanField(default=False)
    subscription_expires = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Trading Preferences
    risk_level = models.CharField(
        max_length=20,
        choices=RISK_LEVEL_CHOICES,
        default='MODERATE'
    )
    custom_risk_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=3,
        default=0.55,
        validators=[MinValueValidator(0.1), MaxValueValidator(5.0)]
    )
    max_concurrent_trades = models.PositiveIntegerField(default=3)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    verification_documents_uploaded = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.email} ({self.subscription_tier})"
    
    @property
    def effective_risk_percent(self):
        """Get the actual risk percentage to use"""
        if self.risk_level == 'CUSTOM':
            return float(self.custom_risk_percent)
        
        risk_mapping = {
            'CONSERVATIVE': 0.25,
            'MODERATE': 0.55,
            'AGGRESSIVE': 1.0,
        }
        return risk_mapping.get(self.risk_level, 0.55)
    
    @property
    def max_trades_per_day(self):
        """Get daily trade limit based on subscription"""
        limits = {
            'BASIC': 10,
            'PROFESSIONAL': 50,
            'ENTERPRISE': -1,  # Unlimited
            'TRIAL': 3,
        }
        return limits.get(self.subscription_tier, 3)


class TradingAccount(models.Model):
    """Customer's MT5 trading account details"""
    
    BROKER_CHOICES = [
        ('FTMO', 'FTMO'),
        ('MYFOREXFUNDS', 'MyForexFunds'),
        ('FUNDEDNEXT', 'FundedNext'),
        ('TOPSTEPTRADER', 'TopstepTrader'),
        ('INTERACTIVE_BROKERS', 'Interactive Brokers'),
        ('OANDA', 'OANDA'),
        ('OTHER', 'Other'),
    ]
    
    ACCOUNT_TYPE_CHOICES = [
        ('DEMO', 'Demo Account'),
        ('LIVE', 'Live Account'),
        ('PROP', 'Prop Firm Account'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trading_accounts')
    
    # Account Details
    name = models.CharField(max_length=100, help_text="Account nickname")
    broker = models.CharField(max_length=50, choices=BROKER_CHOICES)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    
    # Encrypted Connection Details
    mt5_login = models.CharField(max_length=255)  # Encrypted
    mt5_password = models.TextField()  # Encrypted
    mt5_server = models.CharField(max_length=100)
    
    # Account Settings
    is_active = models.BooleanField(default=False)
    auto_trading_enabled = models.BooleanField(default=False)
    
    # Risk Management
    daily_loss_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=500.00,
        help_text="Maximum daily loss in USD"
    )
    total_loss_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=2000.00,
        help_text="Maximum total loss in USD"
    )
    
    # Status Tracking
    last_connection = models.DateTimeField(null=True, blank=True)
    connection_status = models.CharField(max_length=50, default='DISCONNECTED')
    last_balance_update = models.DateTimeField(null=True, blank=True)
    current_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trading_accounts'
        verbose_name = 'Trading Account'
        verbose_name_plural = 'Trading Accounts'
        unique_together = ['user', 'mt5_login', 'mt5_server']
    
    def __str__(self):
        return f"{self.user.email} - {self.name} ({self.broker})"
    
    def encrypt_credentials(self, login, password):
        """Encrypt MT5 credentials"""
        key = getattr(settings, 'ENCRYPTION_KEY', Fernet.generate_key())
        f = Fernet(key)
        
        self.mt5_login = f.encrypt(login.encode()).decode()
        self.mt5_password = f.encrypt(password.encode()).decode()
    
    def decrypt_credentials(self):
        """Decrypt MT5 credentials"""
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            raise ValueError("Encryption key not configured")
        
        f = Fernet(key)
        login = f.decrypt(self.mt5_login.encode()).decode()
        password = f.decrypt(self.mt5_password.encode()).decode()
        
        return login, password
    
    def save(self, *args, **kwargs):
        # Only one active account per user
        if self.is_active:
            TradingAccount.objects.filter(
                user=self.user, 
                is_active=True
            ).exclude(id=self.id).update(is_active=False)
        
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """Extended user profile information"""
    
    EXPERIENCE_CHOICES = [
        ('BEGINNER', 'Beginner (< 1 year)'),
        ('INTERMEDIATE', 'Intermediate (1-3 years)'),
        ('ADVANCED', 'Advanced (3-5 years)'),
        ('EXPERT', 'Expert (5+ years)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Trading Experience
    trading_experience = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_CHOICES, 
        default='BEGINNER'
    )
    preferred_trading_sessions = models.JSONField(
        default=list,
        help_text="Array of preferred trading sessions: ['LONDON', 'NEW_YORK', 'TOKYO', 'SYDNEY']"
    )
    
    # Notification Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    # UI Preferences
    dashboard_theme = models.CharField(
        max_length=10, 
        choices=[('LIGHT', 'Light'), ('DARK', 'Dark')], 
        default='LIGHT'
    )
    dashboard_layout = models.JSONField(
        default=dict,
        help_text="Custom dashboard layout configuration"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} Profile"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class LoginHistory(models.Model):
    """Track user login history for security"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'login_history'
        verbose_name = 'Login History'
        verbose_name_plural = 'Login History'
        ordering = ['-login_time']
    
    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"{self.user.email} - {status} - {self.login_time}"