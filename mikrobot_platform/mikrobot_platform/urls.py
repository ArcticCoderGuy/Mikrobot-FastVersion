"""
Mikrobot Trading Platform URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from dashboard.views import dashboard_view

urlpatterns = [
    # Admin (includes automatically registered admin_config URLs)
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/trading/', include('trading.urls')),
    # Above Robust temporary exclusions for immediate operational capability
    # path('api/v1/signals/', include('signals.urls')),
    # path('api/v1/risk/', include('risk_management.urls')),
    # path('api/v1/notifications/', include('notifications.urls')),
    
    # Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Authentication
    path('accounts/', include('allauth.urls')),
    
    # Health check
    path('health/', TemplateView.as_view(template_name='health.html'), name='health_check'),
    
    # Landing page
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Admin customization
admin.site.site_header = "Mikrobot Trading Platform Admin"
admin.site.site_title = "Mikrobot Admin"
admin.site.index_title = "Trading Platform Administration"