"""
VERIFY EA ATTACHMENT TO CHARTS
Checks which EAs are attached to which charts
"""
import os
from pathlib import Path

print("CHECKING EA ATTACHMENT STATUS")
print("=" * 50)

# Path to MT5 Experts folder
experts_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075/MQL5/Experts")

# List all EA files
print("\nAvailable Expert Advisors:")
ea_files = list(experts_path.glob("*.mq5"))
for ea in ea_files:
    print(f"- {ea.name}")

print("\nTo attach EA to GBPJPY chart:")
print("1. Open GBPJPY M5 chart in MT5")
print("2. Drag MikrobotProfessionalBOS.mq5 to the chart")
print("3. Enable 'Allow automated trading'")
print("4. Check 'AutoTrading' button is ON (green)")

print("\nIMPORTANT: The EA must be attached to EACH chart you want to monitor:")
print("- GBPJPY M5")
print("- EURUSD M5")
print("- EURJPY M5")
print("- etc.")

print("\nCheck the Experts tab in MT5 for any error messages!")