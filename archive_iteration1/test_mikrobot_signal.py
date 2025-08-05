"""
Test using the existing mikrobot_signal.json file
"""
import json
import time
from pathlib import Path

# Use the mikrobot_signal.json that already exists
COMMON_PATH = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
SIGNAL_FILE = COMMON_PATH / "mikrobot_signal.json"
STATUS_FILE = COMMON_PATH / "mikrobot_status.txt"

print("Testing with mikrobot_signal.json")
print("=" * 60)

# Write a test signal
signal = {
    "command": "GET_INFO",
    "timestamp": time.time(),
    "id": 1
}

print(f"Writing to: {SIGNAL_FILE}")
with open(SIGNAL_FILE, 'w') as f:
    json.dump(signal, f, indent=2)

print("Signal written!")
print(f"Content: {json.dumps(signal, indent=2)}")

# Check if status file gets updated
print("\nWaiting for response...")
for i in range(5):
    if STATUS_FILE.exists():
        with open(STATUS_FILE, 'r') as f:
            status = f.read()
        print(f"Status file content: {status}")
    
    # Also check for any response files
    for file in COMMON_PATH.glob("*.json"):
        print(f"Found JSON file: {file.name}")
        if file.name not in ["mikrobot_signal.json", "signal.json"]:
            with open(file, 'r') as f:
                content = f.read()
            print(f"Content of {file.name}: {content[:200]}...")
    
    time.sleep(1)

print("\nDone!")