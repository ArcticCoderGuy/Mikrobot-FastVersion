from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MIKROBOT ADMIN CONFIGURATION
Above Robust admin interface for central configuration management
"""

from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import path, reverse
from django.utils.html import format_html
from config.mikrobot_config import mikrobot_config
from .models import MikrobotConfig
import json


@admin.register(MikrobotConfig)
class MikrobotConfigAdmin(admin.ModelAdmin):
    """Above Robust configuration admin interface"""
    
    list_display = ['name', 'updated_at', 'config_actions']
    readonly_fields = ['name', 'updated_at']
    
    def config_actions(self, obj):
        return format_html(
            '<a class="button" href="{}"> Configure</a> '
            '<a class="button" href="{}">OK Validate</a> '
            '<a class="button" href="{}"> Export</a>',
            reverse('admin:mikrobot_config_view'),
            reverse('admin:mikrobot_config_validate'),
            reverse('admin:mikrobot_config_export'),
        )
    config_actions.short_description = 'Actions'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('config-view/', self.admin_site.admin_view(self.config_view), name='mikrobot_config_view'),
            path('config-export/', self.admin_site.admin_view(self.export_config), name='mikrobot_config_export'),
            path('config-validate/', self.admin_site.admin_view(self.validate_config), name='mikrobot_config_validate'),
        ]
        return custom_urls + urls
    
    def config_view(self, request):
        """Main configuration view"""
        if request.method == 'POST':
            # Handle configuration updates
            try:
                config_data = request.POST.dict()
                
                # Update position sizing
                if 'default_risk_percent' in config_data:
                    risk_percent = float(config_data['default_risk_percent'])
                    mikrobot_config.set('POSITION_SIZING.DEFAULT_RISK_PERCENT', risk_percent)
                
                # Update platform settings
                if 'max_concurrent_trades' in config_data:
                    max_trades = int(config_data['max_concurrent_trades'])
                    mikrobot_config.set('PLATFORM.MAX_CONCURRENT_TRADES', max_trades)
                
                # Update subscription pricing
                for tier in ['BASIC', 'PROFESSIONAL', 'ENTERPRISE']:
                    price_key = f'{tier.lower()}_price'
                    if price_key in config_data:
                        price = int(config_data[price_key])
                        mikrobot_config.set(f'SUBSCRIPTION_TIERS.{tier}.price_monthly', price)
                
                # Save to MIKROBOT_FASTVERSION.md
                mikrobot_config.save_to_mikrobot_fastversion()
                
                messages.success(request, 'Configuration updated successfully!')
                
            except Exception as e:
                messages.error(request, f'Configuration update failed: {str(e)}')
        
        # Get current configuration
        config = {
            'position_sizing': mikrobot_config.get('POSITION_SIZING'),
            'platform': mikrobot_config.get('PLATFORM'),
            'subscription_tiers': mikrobot_config.get('SUBSCRIPTION_TIERS'),
            'quality_control': mikrobot_config.get('QUALITY_CONTROL'),
            'asset_classes': mikrobot_config.get('ASSET_CLASSES'),
        }
        
        context = {
            'title': 'MIKROBOT Configuration',
            'config': config,
            'is_compliant': mikrobot_config.is_above_robust_compliant(),
        }
        
        return render(request, 'admin/mikrobot_config.html', context)
    
    def export_config(self, request):
        """Export configuration as JSON"""
        config_json = mikrobot_config.export_config_json()
        
        response = JsonResponse(json.loads(config_json), json_dumps_params={'indent': 2})
        response['Content-Disposition'] = 'attachment; filename="mikrobot_config.json"'
        
        return response
    
    def validate_config(self, request):
        """Validate Above Robust compliance"""
        validation_results = {
            'is_compliant': mikrobot_config.is_above_robust_compliant(),
            'checks': {
                'ascii_only': mikrobot_config.get('PLATFORM.ASCII_ONLY_ENFORCED'),
                'submarine_grade': mikrobot_config.get('PLATFORM.SUBMARINE_GRADE_PRECISION'),
                'position_sizing': mikrobot_config.get('POSITION_SIZING.DEFAULT_RISK_PERCENT') == 0.55,
                'signal_validation': mikrobot_config.get('SIGNAL_VALIDATION.REQUIRED_PHASES') == 4,
            },
            'revenue_potential': {
                'basic_monthly': mikrobot_config.get('SUBSCRIPTION_TIERS.BASIC.price_monthly') * 100,  # 100 customers
                'professional_monthly': mikrobot_config.get('SUBSCRIPTION_TIERS.PROFESSIONAL.price_monthly') * 50,  # 50 customers  
                'enterprise_monthly': mikrobot_config.get('SUBSCRIPTION_TIERS.ENTERPRISE.price_monthly') * 20,  # 20 customers
            }
        }
        
        return JsonResponse(validation_results)