"""
Admin interface for user management
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, TradingAccount, UserProfile, LoginHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced user admin with trading platform fields"""
    
    list_display = [
        'email', 'username', 'subscription_tier', 'subscription_active', 
        'is_verified', 'last_login', 'created_at'
    ]
    list_filter = [
        'subscription_tier', 'subscription_active', 'is_verified', 
        'risk_level', 'is_active', 'is_staff'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Subscription', {
            'fields': (
                'subscription_tier', 'subscription_active', 'subscription_expires',
                'stripe_customer_id'
            )
        }),
        ('Trading Settings', {
            'fields': (
                'risk_level', 'custom_risk_percent', 'max_concurrent_trades'
            )
        }),
        ('Verification', {
            'fields': (
                'is_verified', 'verification_documents_uploaded'
            )
        }),
        ('Security', {
            'fields': ('last_login_ip',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(TradingAccount)
class TradingAccountAdmin(admin.ModelAdmin):
    """Trading account management"""
    
    list_display = [
        'user_email', 'name', 'broker', 'account_type', 'is_active',
        'auto_trading_enabled', 'connection_status', 'current_balance',
        'last_connection'
    ]
    list_filter = [
        'broker', 'account_type', 'is_active', 'auto_trading_enabled',
        'connection_status'
    ]
    search_fields = ['user__email', 'name', 'broker']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'name', 'broker', 'account_type')
        }),
        ('Connection Details', {
            'fields': ('mt5_server',),
            'description': 'MT5 credentials are encrypted and not displayed for security'
        }),
        ('Settings', {
            'fields': (
                'is_active', 'auto_trading_enabled', 'daily_loss_limit',
                'total_loss_limit'
            )
        }),
        ('Status', {
            'fields': (
                'connection_status', 'current_balance', 'last_connection',
                'last_balance_update'
            )
        }),
    )
    
    readonly_fields = [
        'connection_status', 'last_connection', 'last_balance_update',
        'current_balance', 'created_at', 'updated_at'
    ]
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User profile management"""
    
    list_display = [
        'user_email', 'full_name', 'country', 'trading_experience',
        'email_notifications', 'dashboard_theme'
    ]
    list_filter = [
        'trading_experience', 'country', 'email_notifications',
        'sms_notifications', 'dashboard_theme'
    ]
    search_fields = ['user__email', 'first_name', 'last_name', 'country']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'user', 'first_name', 'last_name', 'date_of_birth',
                'country', 'timezone'
            )
        }),
        ('Trading Experience', {
            'fields': ('trading_experience', 'preferred_trading_sessions')
        }),
        ('Notifications', {
            'fields': (
                'email_notifications', 'sms_notifications', 'push_notifications'
            )
        }),
        ('UI Preferences', {
            'fields': ('dashboard_theme', 'dashboard_layout')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Login history for security monitoring"""
    
    list_display = [
        'user_email', 'ip_address', 'success_status', 'login_time', 'user_agent_short'
    ]
    list_filter = ['success', 'login_time']
    search_fields = ['user__email', 'ip_address']
    ordering = ['-login_time']
    
    def has_add_permission(self, request):
        return False  # No manual adding
    
    def has_change_permission(self, request, obj=None):
        return False  # Read only
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def success_status(self, obj):
        if obj.success:
            return format_html('<span style="color: green;">SUCCESS</span>')
        else:
            return format_html('<span style="color: red;">FAILED: {}</span>', obj.failure_reason)
    success_status.short_description = 'Status'
    
    def user_agent_short(self, obj):
        return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
    user_agent_short.short_description = 'User Agent'