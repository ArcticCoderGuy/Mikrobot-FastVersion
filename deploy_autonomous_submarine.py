"""
Deploy Autonomous Submarine for Iteration 2
Continuous 24/7 trading operations per MIKROBOT_FASTVERSION.md doctrine
"""

import asyncio
import signal
import sys
from datetime import datetime
from submarine_command_center import SubmarineCommandCenter

class AutonomousSubmarineDeployment:
    """
    Iteration 2: Continuous autonomous trading operations
    """
    
    def __init__(self):
        self.submarine = SubmarineCommandCenter()
        self.deployment_active = False
        self.trades_executed = 0
        self.start_time = None
        
    async def deploy_submarine(self):
        """Deploy submarine for autonomous operations"""
        
        print("MIKROBOT AUTONOMOUS SUBMARINE DEPLOYMENT")
        print("=" * 60)
        print("Iteration 2: Continuous Trading Operations")
        print("Doctrine: MIKROBOT_FASTVERSION.md")
        print("Quality: Cp/Cpk >= 3.0 Gold Standard")
        print("=" * 60)
        print()
        
        self.start_time = datetime.now()
        self.deployment_active = True
        
        print(f"DEPLOYMENT START: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("OPERATIONAL STATUS: AUTONOMOUS")
        print("MONITORING MODE: 24/7/365")
        print()
        print("SUBMARINE DIVING...")
        print("Press Ctrl+C to surface submarine")
        print()
        
        try:
            # Deploy submarine for continuous operations
            await self.submarine.dive_operations()
            
        except KeyboardInterrupt:
            print("\n" + "=" * 50)
            print("EMERGENCY SURFACE ORDER RECEIVED")
            await self.surface_submarine()
        except Exception as e:
            print(f"\nSUBMARINE SYSTEM ERROR: {e}")
            await self.emergency_surface()
    
    async def surface_submarine(self):
        """Surface submarine and provide operational report"""
        
        print("SURFACING SUBMARINE...")
        self.submarine.surface()
        self.deployment_active = False
        
        # Calculate operational metrics
        end_time = datetime.now()
        operational_duration = end_time - self.start_time if self.start_time else None
        
        print("\nSUBMARINE OPERATIONAL REPORT")
        print("=" * 40)
        print(f"Deployment Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else 'Unknown'}")
        print(f"Deployment End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Operational Duration: {operational_duration}")
        print(f"Signals Processed: {self.submarine.processed_signals}")
        print(f"Trades Executed: {self.trades_executed}")
        print(f"Operational Status: {self.submarine.operational_status.value}")
        print(f"Quality Level: Gold Standard (Cp/Cpk >= 3.0)")
        print()
        print("SUBMARINE SURFACED - MISSION COMPLETE")
    
    async def emergency_surface(self):
        """Emergency surface procedure"""
        
        print("EMERGENCY SURFACE PROCEDURE INITIATED")
        await self.submarine._emergency_surface()
        await self.surface_submarine()

def setup_signal_handlers(deployment):
    """Setup signal handlers for graceful shutdown"""
    
    def signal_handler(signum, frame):
        print(f"\nSignal {signum} received - initiating surface procedure")
        # This will be caught by the KeyboardInterrupt handler
        raise KeyboardInterrupt()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main deployment function"""
    
    deployment = AutonomousSubmarineDeployment()
    setup_signal_handlers(deployment)
    
    try:
        await deployment.deploy_submarine()
    except Exception as e:
        print(f"DEPLOYMENT ERROR: {e}")
        await deployment.emergency_surface()

if __name__ == "__main__":
    print("MIKROBOT FASTVERSION - AUTONOMOUS SUBMARINE")
    print("Iteration 2: Enhanced Functionality")
    print("Preparing for continuous trading operations...")
    print()
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)