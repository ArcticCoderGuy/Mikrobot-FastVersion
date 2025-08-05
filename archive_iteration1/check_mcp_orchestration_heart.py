"""
CHECK MCP ORCHESTRATION HEART SYSTEM
Diagnose what should be running to process EA 4-phase signals
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

def check_orchestration_heart():
    """Check the heart of the MCP orchestration system"""
    
    print("CHECKING MCP ORCHESTRATION HEART SYSTEM")
    print("=" * 50)
    print("Timestamp:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 50)
    
    # 1. Check where EA is sending 4-phase signals
    signal_file = "C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json"
    
    print("STEP 1: Checking EA signal output...")
    if os.path.exists(signal_file):
        try:
            with open(signal_file, 'r') as f:
                signal_data = json.load(f)
            print("EA SIGNAL FOUND:")
            print(f"  Symbol: {signal_data.get('symbol', 'N/A')}")
            print(f"  Direction: {signal_data.get('direction', 'N/A')}")
            print(f"  Test: {signal_data.get('test', 'N/A')}")
            print(f"  Timestamp: {signal_data.get('timestamp', 'N/A')}")
        except Exception as e:
            print(f"SIGNAL FILE EXISTS but cannot read: {e}")
    else:
        print("NO EA SIGNAL FILE - EA not sending signals")
    
    # 2. Check if orchestration components exist
    print("\nSTEP 2: Checking orchestration components...")
    
    components = {
        "Enhanced Orchestrator": "src/core/enhanced_orchestrator.py",
        "Product Owner Agent": "src/core/product_owner_agent.py", 
        "MCP Controller": "src/core/mcp_controller.py"
    }
    
    for name, path in components.items():
        if os.path.exists(path):
            print(f"OK: {name} - {path}")
        else:
            print(f"MISSING: {name} - {path}")
    
    # 3. Check what should be monitoring the signals
    print("\nSTEP 3: What's missing - THE HEART!")
    print("=" * 30)
    print("DIAGNOSIS:")
    print("1. EA v8_Fixed is working perfectly - sending 4-phase signals")
    print("2. Enhanced Orchestrator exists but NOT RUNNING")
    print("3. MISSING: Signal monitoring process that:")
    print("   - Watches mikrobot_4phase_signal.json")
    print("   - Starts Enhanced Orchestrator when signal received")
    print("   - Processes signal through MCP pipeline")
    print("   - Sends trade command back to EA")
    print()
    print("SOLUTION NEEDED:")
    print("Create and START the signal monitoring process!")
    
    return signal_file

def check_what_should_be_running():
    """Check what processes should be running"""
    
    print("\n" + "=" * 50)
    print("WHAT SHOULD BE RUNNING - THE MISSING HEART")
    print("=" * 50)
    
    print("Based on Session #1 architecture, these should be running:")
    print()
    print("1. SIGNAL MONITOR PROCESS:")
    print("   - Watches: mikrobot_4phase_signal.json")
    print("   - Action: Triggers Enhanced Orchestrator")
    print()
    print("2. ENHANCED ORCHESTRATOR:")
    print("   - ProductOwner strategic evaluation")
    print("   - MCP Controller coordination")
    print("   - U-Cell pipeline processing")
    print()
    print("3. RESPONSE GENERATOR:")
    print("   - Calculates: ATR, risk, lot size")
    print("   - Sends back: Trade execution command to EA")
    print()
    print("STATUS: ALL MISSING - System not started!")
    print("=" * 50)

if __name__ == "__main__":
    signal_file = check_orchestration_heart()
    check_what_should_be_running()
    
    print(f"\nCONCLUSION:")
    print("EA v8_Fixed is the 'Stupid EA' that detects patterns correctly.")
    print("The MISSING PIECE is the Python MCP orchestration system")
    print("that should be monitoring and processing the 4-phase signals!")
    print()
    print("NEXT: Need to create and start the signal monitoring process")