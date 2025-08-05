#!/usr/bin/env python3
"""
MCP Orchestration Startup Script - Complete System Launch
Starts the unified MCP trading orchestration system
"""
import sys
import asyncio
import subprocess
import time
from pathlib import Path
import signal
import os

# ASCII-only encoding enforcement
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    """Enforce ASCII-only output"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

class MCPOrchestrationStarter:
    """Startup coordinator for MCP orchestration system"""
    
    def __init__(self):
        self.processes = {}
        self.shutdown_requested = False
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(sig, frame):
            ascii_print("\nShutdown signal received...")
            self.shutdown_requested = True
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        ascii_print("=== CHECKING PREREQUISITES ===")
        
        # Check MT5 availability
        try:
            import MetaTrader5 as mt5
            if mt5.initialize():
                mt5.shutdown()
                ascii_print("PASS: MT5 available")
            else:
                ascii_print("FAIL: MT5 not available")
                return False
        except ImportError:
            ascii_print("FAIL: MetaTrader5 module not installed")
            return False
            
        # Check signal directory
        signal_dir = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
        if signal_dir.exists():
            ascii_print("PASS: Signal directory accessible")
        else:
            ascii_print("FAIL: Signal directory not found")
            return False
            
        # Check orchestrator file
        orchestrator_file = Path("mcp_trading_orchestrator.py")
        if orchestrator_file.exists():
            ascii_print("PASS: Orchestrator file found")
        else:
            ascii_print("FAIL: Orchestrator file missing")
            return False
            
        ascii_print("SUCCESS: All prerequisites met")
        return True
        
    def start_orchestrator(self) -> bool:
        """Start the main orchestrator process"""
        ascii_print("=== STARTING MCP ORCHESTRATOR ===")
        
        try:
            # Start orchestrator as subprocess
            cmd = [sys.executable, "mcp_trading_orchestrator.py"]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes['orchestrator'] = proc
            ascii_print("SUCCESS: Orchestrator process started")
            return True
            
        except Exception as e:
            ascii_print(f"FAIL: Could not start orchestrator - {e}")
            return False
            
    def start_monitoring_dashboard(self) -> bool:
        """Start the monitoring dashboard"""
        ascii_print("=== STARTING MONITORING DASHBOARD ===")
        
        try:
            # Start dashboard as subprocess
            cmd = [sys.executable, "mcp_monitoring_dashboard.py"]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes['dashboard'] = proc
            ascii_print("SUCCESS: Monitoring dashboard started")
            return True
            
        except Exception as e:
            ascii_print(f"FAIL: Could not start dashboard - {e}")
            return False
            
    def monitor_processes(self):
        """Monitor all running processes"""
        ascii_print("=== MONITORING SYSTEM PROCESSES ===")
        ascii_print("Press Ctrl+C for graceful shutdown")
        ascii_print("")
        
        while not self.shutdown_requested:
            # Check process health
            for name, proc in self.processes.items():
                if proc.poll() is not None:
                    ascii_print(f"WARNING: {name} process terminated unexpectedly")
                    
            # Show brief status
            ascii_print(f"System Status: {len([p for p in self.processes.values() if p.poll() is None])}/{len(self.processes)} processes running")
            
            time.sleep(10)  # Check every 10 seconds
            
    def shutdown_all_processes(self):
        """Gracefully shutdown all processes"""
        ascii_print("=== INITIATING GRACEFUL SHUTDOWN ===")
        
        for name, proc in self.processes.items():
            if proc.poll() is None:  # Still running
                ascii_print(f"Stopping {name}...")
                try:
                    proc.terminate()
                    proc.wait(timeout=10)
                    ascii_print(f"SUCCESS: {name} stopped")
                except subprocess.TimeoutExpired:
                    ascii_print(f"WARNING: Force killing {name}")
                    proc.kill()
                    proc.wait()
                except Exception as e:
                    ascii_print(f"ERROR stopping {name}: {e}")
                    
        ascii_print("SUCCESS: All processes stopped")
        
    def run_complete_system(self):
        """Run the complete MCP orchestration system"""
        ascii_print("=" * 80)
        ascii_print("  MCP TRADING ORCHESTRATION SYSTEM - STARTUP")
        ascii_print("=" * 80)
        ascii_print("")
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Check prerequisites
        if not self.check_prerequisites():
            ascii_print("CRITICAL: Prerequisites not met - cannot start")
            return False
            
        # Start orchestrator
        if not self.start_orchestrator():
            ascii_print("CRITICAL: Could not start orchestrator")
            return False
            
        # Give orchestrator time to initialize
        ascii_print("Waiting for orchestrator initialization...")
        time.sleep(5)
        
        # Start monitoring dashboard in separate window
        ascii_print("To view real-time monitoring, run in another terminal:")
        ascii_print("python mcp_monitoring_dashboard.py")
        ascii_print("")
        
        try:
            # Monitor the orchestrator process
            orchestrator_proc = self.processes['orchestrator']
            
            ascii_print("=== MCP ORCHESTRATION SYSTEM RUNNING ===")
            ascii_print("Real-time trading coordination active")
            ascii_print("Press Ctrl+C for graceful shutdown")
            ascii_print("")
            
            # Stream orchestrator output
            while not self.shutdown_requested and orchestrator_proc.poll() is None:
                try:
                    output = orchestrator_proc.stdout.readline()
                    if output:
                        ascii_print(f"ORCHESTRATOR: {output.strip()}")
                    time.sleep(0.1)
                except Exception as e:
                    ascii_print(f"Error reading orchestrator output: {e}")
                    break
                    
        except KeyboardInterrupt:
            ascii_print("\nShutdown requested by user")
            
        finally:
            self.shutdown_all_processes()
            
        ascii_print("=" * 80)
        ascii_print("  MCP ORCHESTRATION SYSTEM SHUTDOWN COMPLETE")
        ascii_print("=" * 80)
        
        return True

def main():
    """Main entry point"""
    starter = MCPOrchestrationStarter()
    starter.run_complete_system()

if __name__ == "__main__":
    main()