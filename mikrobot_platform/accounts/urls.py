"""
Authentication API URLs
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'trading-accounts', views.TradingAccountViewSet)
router.register(r'profiles', views.UserProfileViewSet)

urlpatterns = [
    # DRF Router URLs
    path('', include(router.urls)),
    
    # Custom authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Account management
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
    path('subscription/', views.SubscriptionView.as_view(), name='subscription'),
    path('billing/', views.BillingView.as_view(), name='billing'),
    
    # Security
    path('login-history/', views.LoginHistoryView.as_view(), name='login_history'),
    path('security-settings/', views.SecuritySettingsView.as_view(), name='security_settings'),
]