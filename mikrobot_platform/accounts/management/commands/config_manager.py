"""
Django Management Command for MIKROBOT Configuration
Above Robust configuration management through Django admin
"""

from django.core.management.base import BaseCommand
from config.mikrobot_config import mikrobot_config
import json


class Command(BaseCommand):
    help = 'Manage MIKROBOT configuration settings'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['show', 'export', 'validate', 'sync'],
            help='Configuration action to perform'
        )
        parser.add_argument(
            '--key',
            help='Configuration key to display (dot notation)'
        )
        parser.add_argument(
            '--value',
            help='Value to set for configuration key'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'show':
            self.show_config(options.get('key'))
        elif action == 'export':
            self.export_config()
        elif action == 'validate':
            self.validate_config()
        elif action == 'sync':
            self.sync_config()
    
    def show_config(self, key=None):
        """Show configuration values"""
        if key:
            value = mikrobot_config.get(key)
            self.stdout.write(f"{key}: {value}")
        else:
            # Show all configuration
            config_json = mikrobot_config.export_config_json()
            self.stdout.write("MIKROBOT CONFIGURATION:")
            self.stdout.write("=" * 50)
            
            # Parse and display in organized way
            config = json.loads(config_json)
            
            self.stdout.write("\nPOSITION SIZING:")
            for key, value in config['POSITION_SIZING'].items():
                self.stdout.write(f"  {key}: {value}")
            
            self.stdout.write("\nSUBSCRIPTION TIERS:")
            for tier, settings in config['SUBSCRIPTION_TIERS'].items():
                self.stdout.write(f"  {tier}: ${settings['price_monthly']}/month")
                self.stdout.write(f"    Max Daily Trades: {settings['max_trades_daily']}")
            
            self.stdout.write("\nQUALITY CONTROL:")
            for key, value in config['QUALITY_CONTROL'].items():
                self.stdout.write(f"  {key}: {value}")
    
    def export_config(self):
        """Export configuration to JSON file"""
        config_json = mikrobot_config.export_config_json()
        
        output_file = 'mikrobot_config_export.json'
        with open(output_file, 'w') as f:
            f.write(config_json)
        
        self.stdout.write(f"Configuration exported to {output_file}")
    
    def validate_config(self):
        """Validate configuration compliance"""
        self.stdout.write("ABOVE ROBUST COMPLIANCE CHECK:")
        self.stdout.write("=" * 40)
        
        compliant = mikrobot_config.is_above_robust_compliant()
        
        checks = [
            ("ASCII Only Enforced", mikrobot_config.get('PLATFORM.ASCII_ONLY_ENFORCED')),
            ("Submarine Grade Precision", mikrobot_config.get('PLATFORM.SUBMARINE_GRADE_PRECISION')),
            ("Position Sizing 0.55%", mikrobot_config.get('POSITION_SIZING.DEFAULT_RISK_PERCENT') == 0.55),
            ("4-Phase Validation", mikrobot_config.get('SIGNAL_VALIDATION.REQUIRED_PHASES') == 4),
        ]
        
        for check_name, result in checks:
            status = "PASS" if result else "FAIL"
            self.stdout.write(f"{check_name}: {status}")
        
        overall_status = "COMPLIANT" if compliant else "NON-COMPLIANT"
        self.stdout.write(f"\nOVERALL STATUS: {overall_status}")
        
        if compliant:
            self.stdout.write(self.style.SUCCESS("Above Robust standards met!"))
        else:
            self.stdout.write(self.style.ERROR("Above Robust standards NOT met!"))
    
    def sync_config(self):
        """Sync configuration with MIKROBOT_FASTVERSION.md"""
        self.stdout.write("Syncing configuration with MIKROBOT_FASTVERSION.md...")
        
        success = mikrobot_config.save_to_mikrobot_fastversion()
        
        if success:
            self.stdout.write(self.style.SUCCESS("Configuration synced successfully!"))
        else:
            self.stdout.write(self.style.ERROR("Failed to sync configuration!"))