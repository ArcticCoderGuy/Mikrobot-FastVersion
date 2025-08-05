"""
Above Robust Accounts App Configuration
Submarine-grade user authentication and account management
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Above Robust accounts app configuration"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Above Robust User Accounts'
    
    def ready(self):
        """Above Robust app initialization"""
        # Import signal handlers when app is ready
        try:
            import accounts.signals  # noqa
        except ImportError:
            pass