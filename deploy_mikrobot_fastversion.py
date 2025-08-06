"""
MIKROBOT FASTVERSION DEPLOYMENT SCRIPT
Complete system deployment to account 95244786
"""
import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime
import time

class MikrobotFastversionDeployment:
    """Deploy complete MIKROBOT_FASTVERSION system"""
    
    def __init__(self):
        self.account = 95244786
        self.base_path = Path("C:/Users/HP/Dev/Mikrobot Fastversion")
        self.common_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
        self.experts_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Experts")
        
        self.deployment_log = []
        
    def log_step(self, message, status="INFO"):
        """Log deployment step"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
        
    def run_component(self, script_name, description):
        """Run individual component"""
        self.log_step(f"Deploying {description}...")
        
        script_path = self.base_path / script_name
        if not script_path.exists():
            self.log_step(f"ERROR: Script not found: {script_path}", "ERROR")
            return False
            
        try:
            result = subprocess.run([sys.executable, str(script_path)], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log_step(f"SUCCESS: {description} deployed successfully", "SUCCESS")
                if result.stdout:
                    print(result.stdout.strip())
                return True
            else:
                self.log_step(f"ERROR: {description} deployment failed: {result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_step(f"WARNING: {description} deployment timed out", "WARNING")
            return False
        except Exception as e:
            self.log_step(f"ERROR: {description} deployment error: {e}", "ERROR")
            return False
    
    def check_mt5_connection(self):
        """Verify MT5 connection"""
        self.log_step("Checking MT5 connection...")
        
        try:
            import MetaTrader5 as mt5
            
            if not mt5.initialize():
                self.log_step("ERROR: MT5 initialization failed", "ERROR")
                return False
                
            if not mt5.login(95244786, "Ua@tOnLp", "Ava-Demo 1-MT5"):
                self.log_step("ERROR: MT5 login failed", "ERROR")
                mt5.shutdown()
                return False
                
            account_info = mt5.account_info()
            if account_info:
                self.log_step(f"SUCCESS: Connected to MT5 account: {account_info.login}", "SUCCESS")
                self.log_step(f"   Balance: ${account_info.balance}", "INFO")
                self.log_step(f"   Server: {account_info.server}", "INFO")
                mt5.shutdown()
                return True
            else:
                self.log_step("ERROR: Could not get account info", "ERROR")
                mt5.shutdown()
                return False
                
        except ImportError:
            self.log_step("ERROR: MetaTrader5 package not installed", "ERROR")
            return False
        except Exception as e:
            self.log_step(f"ERROR: MT5 connection error: {e}", "ERROR")
            return False
    
    def create_activation_signal(self):
        """Create activation signal for EA"""
        self.log_step("Creating EA activation signal...")
        
        activation_signal = {
            "timestamp": datetime.now().isoformat(),
            "account": self.account,
            "strategy": "MIKROBOT_FASTVERSION",
            "version": "1.0.0",
            "status": "ACTIVATED",
            "components": {
                "atr_dynamic_positioning": True,
                "universal_ylipip_trigger": True,
                "xpws_weekly_tracker": True,
                "dual_phase_tp_system": True
            },
            "parameters": {
                "risk_percent": 0.55,
                "atr_min_pips": 4,
                "atr_max_pips": 15,
                "ylipip_standard": 0.6,
                "xpws_threshold": 10.0
            }
        }
        
        signal_file = self.common_path / "mikrobot_fastversion_signal.json"
        
        try:
            with open(signal_file, 'w') as f:
                json.dump(activation_signal, f, indent=2)
            self.log_step(f"SUCCESS: Activation signal created: {signal_file}", "SUCCESS")
            return True
        except Exception as e:
            self.log_step(f"ERROR: Failed to create activation signal: {e}", "ERROR")
            return False
    
    def verify_ea_installation(self):
        """Verify EA is installed"""
        ea_file = self.experts_path / "MikrobotFastversionEA.mq5"
        
        if ea_file.exists():
            self.log_step(f"SUCCESS: EA installed: {ea_file}", "SUCCESS")
            return True
        else:
            self.log_step(f"ERROR: EA not found: {ea_file}", "ERROR")
            return False
    
    def create_startup_script(self):
        """Create startup script for continuous operation"""
        startup_script = '''
@echo off
echo Starting MIKROBOT FASTVERSION System...

echo Updating XPWS Status...
python "C:\\Users\\HP\\Dev\\Mikrobot Fastversion\\xpws_weekly_tracker.py"

echo Starting Dual Phase TP Monitoring...
python "C:\\Users\\HP\\Dev\\Mikrobot Fastversion\\dual_phase_tp_system.py"

echo Updating Universal Ylipip Configuration...
python "C:\\Users\\HP\\Dev\\Mikrobot Fastversion\\universal_ylipip_trigger.py"

echo MIKROBOT FASTVERSION System Ready!
echo Account: 95244786
echo Strategy: MIKROBOT_FASTVERSION.md
echo Status: ACTIVE

pause
'''
        
        startup_file = self.base_path / "start_mikrobot_fastversion.bat"
        
        try:
            with open(startup_file, 'w') as f:
                f.write(startup_script)
            self.log_step(f"SUCCESS: Startup script created: {startup_file}", "SUCCESS")
            return True
        except Exception as e:
            self.log_step(f"ERROR: Failed to create startup script: {e}", "ERROR")
            return False
    
    def run_full_deployment(self):
        """Run complete MIKROBOT FASTVERSION deployment"""
        self.log_step("STARTING MIKROBOT FASTVERSION DEPLOYMENT", "INFO")
        self.log_step(f"   Account: {self.account}", "INFO")
        self.log_step(f"   Strategy: MIKROBOT_FASTVERSION.md", "INFO")
        self.log_step("=" * 60, "INFO")
        
        deployment_success = True
        
        # Step 1: Check MT5 connection
        if not self.check_mt5_connection():
            deployment_success = False
        
        # Step 2: Deploy ATR Dynamic Positioning
        if not self.run_component("atr_dynamic_positioning.py", "ATR Dynamic Positioning System"):
            deployment_success = False
        
        # Step 3: Deploy Universal Ylipip Trigger
        if not self.run_component("universal_ylipip_trigger.py", "Universal 0.6 Ylipip Trigger System"):
            deployment_success = False
        
        # Step 4: Deploy XPWS Weekly Tracker
        if not self.run_component("xpws_weekly_tracker.py", "XPWS Weekly Profit Tracking System"):
            deployment_success = False
        
        # Step 5: Deploy Dual Phase TP System
        if not self.run_component("dual_phase_tp_system.py", "Dual Phase TP System"):
            deployment_success = False
        
        # Step 6: Verify EA Installation
        if not self.verify_ea_installation():
            deployment_success = False
        
        # Step 7: Create activation signal
        if not self.create_activation_signal():
            deployment_success = False
        
        # Step 8: Create startup script
        if not self.create_startup_script():
            deployment_success = False
        
        # Final status
        self.log_step("=" * 60, "INFO")
        
        if deployment_success:
            self.log_step("SUCCESS: MIKROBOT FASTVERSION DEPLOYMENT COMPLETED SUCCESSFULLY!", "SUCCESS")
            self.log_step("SUCCESS: All components deployed and operational", "SUCCESS")
            self.log_step(f"SUCCESS: Account {self.account} ready for 24/7/365 trading", "SUCCESS")
            self.log_step("SUCCESS: MIKROBOT_FASTVERSION.md strategy ACTIVE", "SUCCESS")
        else:
            self.log_step("ERROR: DEPLOYMENT FAILED - Some components had errors", "ERROR")
            self.log_step("WARNING: Review errors above and retry deployment", "WARNING")
        
        # Save deployment log
        self.save_deployment_log()
        
        return deployment_success
    
    def save_deployment_log(self):
        """Save deployment log"""
        log_file = self.base_path / f"deployment_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(log_file, 'w') as f:
                f.write("MIKROBOT FASTVERSION DEPLOYMENT LOG\\n")
                f.write("=" * 50 + "\\n")
                for entry in self.deployment_log:
                    f.write(entry + "\\n")
            
            print(f"\\nDeployment log saved: {log_file}")
        except Exception as e:
            print(f"ERROR: Failed to save deployment log: {e}")

if __name__ == "__main__":
    print("MIKROBOT FASTVERSION COMPLETE DEPLOYMENT")
    print("Account: 95244786")
    print("Strategy: MIKROBOT_FASTVERSION.md")
    print("=" * 50)
    
    deployer = MikrobotFastversionDeployment()
    success = deployer.run_full_deployment()
    
    if success:
        print("\\n" + "=" * 50)
        print("NEXT STEPS:")
        print("1. Open MetaTrader 5")
        print("2. Attach MikrobotFastversionEA.mq5 to any chart")
        print("3. Enable automated trading")
        print("4. Monitor through start_mikrobot_fastversion.bat")
        print("5. System will trade 24/7/365 according to MIKROBOT_FASTVERSION.md")
        print("=" * 50)
    else:
        print("\\nERROR: Deployment failed. Check errors above.")