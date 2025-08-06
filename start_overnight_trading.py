#!/usr/bin/env python3
"""
🌙 OVERNIGHT TRADING LAUNCHER
============================

Complete overnight trading setup that:
1. Prevents Mac from sleeping
2. Starts trading engine
3. Monitors both processes
"""

import subprocess
import time
import signal
import sys
import os
from pathlib import Path

class OvernightTradingManager:
    """Manages overnight trading with Mac awake"""
    
    def __init__(self):
        self.caffeinate_process = None
        self.trading_process = None
        self.running = True
        
    def start_caffeinate(self):
        """Start caffeinate to prevent Mac sleep"""
        try:
            print("☕ Starting Mac awake mode...")
            self.caffeinate_process = subprocess.Popen([
                'caffeinate', 
                '-d',  # prevent display sleep
                '-i',  # prevent idle sleep  
                '-u',  # prevent user idle system sleep
                '-s'   # prevent system sleep
            ])
            print("✅ Mac will stay awake during trading")
            return True
            
        except Exception as e:
            print(f"❌ Error starting caffeinate: {e}")
            return False
    
    def start_trading(self):
        """Start the trading engine"""
        try:
            print("🚀 Starting trading engine...")
            
            # Change to project directory
            project_dir = Path(__file__).parent
            os.chdir(project_dir)
            
            # Start trading with automatic yes
            self.trading_process = subprocess.Popen([
                'python3', 'mikrobot_v2_launcher.py'
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            # Send 'y' to confirm launch
            self.trading_process.stdin.write('y\n')
            self.trading_process.stdin.flush()
            
            print("✅ Trading engine started")
            return True
            
        except Exception as e:
            print(f"❌ Error starting trading: {e}")
            return False
    
    def monitor_processes(self):
        """Monitor both processes"""
        print("📊 Monitoring overnight trading...")
        print("🌙 System will trade until 10:00 Finnish time")
        print("🛑 Press Ctrl+C to stop early")
        print()
        
        try:
            while self.running:
                # Check if trading process is still running
                if self.trading_process and self.trading_process.poll() is not None:
                    print("🌅 Trading process completed normally")
                    break
                
                # Check if caffeinate is still running
                if self.caffeinate_process and self.caffeinate_process.poll() is not None:
                    print("⚠️ Caffeinate stopped, restarting...")
                    self.start_caffeinate()
                
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Manual stop requested...")
            self.stop_all()
    
    def stop_all(self):
        """Stop all processes"""
        print("🛑 Stopping overnight trading...")
        
        self.running = False
        
        # Stop trading process
        if self.trading_process:
            try:
                self.trading_process.terminate()
                self.trading_process.wait(timeout=10)
                print("✅ Trading engine stopped")
            except:
                self.trading_process.kill()
                print("🔄 Trading engine force stopped")
        
        # Stop caffeinate
        if self.caffeinate_process:
            try:
                self.caffeinate_process.terminate()
                self.caffeinate_process.wait(timeout=5)
                print("✅ Mac can now sleep normally")
            except:
                self.caffeinate_process.kill()
                print("🔄 Caffeinate force stopped")
        
        print("✅ Overnight trading shutdown complete")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🔔 Shutdown signal received")

def main():
    """Main overnight trading function"""
    
    print("🌙 MIKROBOT OVERNIGHT TRADING SETUP")
    print("=" * 50)
    print("🍎 Prevents Mac from sleeping")
    print("🚀 Runs trading until 10:00 Finnish time")
    print("📊 Monitors both processes")
    print("=" * 50)
    print()
    
    # Create manager
    manager = OvernightTradingManager()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start caffeinate
        if not manager.start_caffeinate():
            print("❌ Failed to prevent Mac sleep")
            return 1
        
        # Wait a moment
        time.sleep(2)
        
        # Start trading
        if not manager.start_trading():
            print("❌ Failed to start trading")
            manager.stop_all()
            return 1
        
        # Monitor both processes
        manager.monitor_processes()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        manager.stop_all()
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Overnight trading interrupted")
        sys.exit(0)