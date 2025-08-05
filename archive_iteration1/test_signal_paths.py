from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Test different MT5 file paths to find the correct one
"""
import os
import json
from pathlib import Path

# Different possible paths
paths = {
    "MQL5_Files": Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Files"),
    "Common_Files": Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files"),
    "Terminal_Common": Path("C:/ProgramData/MetaQuotes/Terminal/Common/Files"),
}

print("Testing MT5 file paths...")
print("=" * 60)

for name, path in paths.items():
    print(f"\n{name}:")
    print(f"Path: {path}")
    print(f"Exists: {path.exists()}")
    
    if path.exists():
        # Try to write a test file
        test_file = path / "test_signal.json"
        try:
            with open(test_file, 'w', encoding='ascii', errors='ignore') as f:
                json.dump({"test": "signal", "path": name}, f)
            print(f"Write test: SUCCESS OK")
            
            # Check if file exists
            if test_file.exists():
                print(f"File created: {test_file}")
                # Clean up
                test_file.unlink()
        except Exception as e:
            print(f"Write test: FAILED ERROR - {e}")

# Also check what the EA might be looking for
print("\n" + "=" * 60)
print("EA uses FILE_COMMON flag, which typically means:")
print("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
print("\nCreate this directory if it doesn't exist!")

# Create common directory if needed
common_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
if not common_path.exists():
    print(f"\nCreating common directory: {common_path}")
    common_path.mkdir(parents=True, exist_ok=True)
    print("Directory created!")
else:
    print(f"\nCommon directory already exists: {common_path}")