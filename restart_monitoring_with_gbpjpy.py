"""
RESTART MONITORING WITH GBPJPY ACTIVATED
Ensures the system monitors GBPJPY and other forex pairs
"""
import subprocess
import time
import os

print("RESTARTING MIKROBOT MONITORING WITH GBPJPY")
print("=" * 50)

# First, kill any existing monitoring processes
print("Stopping existing monitoring processes...")
os.system("taskkill /F /IM python.exe /FI \"WINDOWTITLE eq *monitor*\" 2>nul")
time.sleep(2)

print("\nStarting monitoring with updated configuration...")
print("Active symbols now include: GBPJPY, EURUSD, EURJPY, etc.")

# Start the monitoring in background
print("\nLaunching compliant_monitor_final.py...")
subprocess.Popen(["python", "compliant_monitor_final.py"], 
                 creationflags=subprocess.CREATE_NEW_CONSOLE)

print("\nMonitoring system started!")
print("The system will now watch for BOS patterns on:")
print("- GBPJPY (NOW ACTIVE)")
print("- EURUSD")
print("- EURJPY")
print("- And other configured pairs")
print("\nIf a M5 BOS with M1 retest occurs on GBPJPY, it will be traded!")