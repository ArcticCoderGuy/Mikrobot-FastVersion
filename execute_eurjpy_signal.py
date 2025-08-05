"""
Execute EURJPY Signal According to MIKROBOT_FASTVERSION.md Doctrine
Current Signal: EURJPY BUY - ylipip triggered
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from submarine_command_center import SubmarineCommandCenter

async def execute_eurjpy_signal():
    """Execute EURJPY BUY signal with full doctrine compliance"""
    
    print("SUBMARINE EXECUTING EURJPY SIGNAL")
    print("=" * 50)
    
    # Read current EURJPY signal
    signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
    
    if not signal_file.exists():
        print("ERROR: No signal file found")
        return False
    
    try:
        # Read EURJPY signal with UTF-16 encoding
        with open(signal_file, 'r', encoding='utf-16') as f:
            signal_content = f.read()
        
        signal_data = json.loads(signal_content)
        
        print("EURJPY SIGNAL ANALYSIS:")
        print(f"  Symbol: {signal_data.get('symbol')}")
        print(f"  Strategy: {signal_data.get('strategy')}")
        print(f"  Trade Direction: {signal_data.get('trade_direction')}")
        print(f"  Current Price: {signal_data.get('current_price')}")
        print(f"  Timestamp: {signal_data.get('timestamp')}")
        
        # Check ylipip trigger
        ylipip_data = signal_data.get('phase_4_ylipip', {})
        ylipip_triggered = ylipip_data.get('triggered', False)
        ylipip_target = ylipip_data.get('target', 0)
        ylipip_current = ylipip_data.get('current', 0)
        
        print(f"  Ylipip Target: {ylipip_target}")
        print(f"  Ylipip Current: {ylipip_current}")
        print(f"  Ylipip Triggered: {ylipip_triggered}")
        print()
        
        # Verify signal is EURJPY
        if signal_data.get('symbol') != 'EURJPY':
            print(f"ERROR: Signal is for {signal_data.get('symbol')}, not EURJPY")
            return False
        
        # Verify ylipip is triggered
        if not ylipip_triggered:
            print("DOCTRINE COMPLIANCE: ylipip not triggered - no execution")
            return False
        
        print("DOCTRINE VALIDATION: EURJPY BUY SIGNAL APPROVED")
        print("SUBMARINE ENGAGING...")
        print()
        
        # Create submarine and process signal
        submarine = SubmarineCommandCenter()
        
        # Process the signal through submarine doctrine validation
        print("SUBMARINE DOCTRINE VALIDATION:")
        
        # Validate MIKROBOT doctrine
        is_doctrine_valid = submarine._validate_mikrobot_doctrine(signal_data)
        print(f"  Doctrine Valid: {is_doctrine_valid}")
        
        if not is_doctrine_valid:
            print("DOCTRINE VIOLATION: Signal rejected")
            return False
        
        # Validate ATR range
        atr_validation = submarine._validate_atr_range(signal_data)
        print(f"  ATR Valid: {atr_validation['valid']}")
        print(f"  ATR Pips: {atr_validation['atr_pips']:.1f}")
        print(f"  ATR Method: {atr_validation['reason']}")
        
        if not atr_validation['valid']:
            print(f"ATR VALIDATION FAILED: {atr_validation['reason']}")
            return False
        
        print()
        print("ALL VALIDATIONS PASSED - EXECUTING TRADE")
        print()
        
        # Calculate risk for EURJPY
        account_balance = 100000  # Demo account
        risk_percent = 0.55  # MIKROBOT doctrine: 0.55% per trade
        
        risk_calculation = submarine.risk_reactor.calculate_submarine_risk(
            'EURJPY', atr_validation['atr_pips'], account_balance, risk_percent
        )
        
        print("RISK CALCULATION:")
        print(f"  Symbol: {risk_calculation['symbol']}")
        print(f"  Asset Class: {risk_calculation['asset_class']}")
        print(f"  Lot Size: {risk_calculation['lot_size']}")
        print(f"  Stop Loss Pips: {risk_calculation['stop_loss_pips']}")
        print(f"  Risk Amount: ${risk_calculation['risk_amount']:.2f}")
        print()
        
        # Generate doctrine compliant response
        response = await submarine._generate_doctrine_compliant_response(
            signal_data, risk_calculation, atr_validation
        )
        
        print("TRADE RESPONSE GENERATED:")
        print(f"  Action: {response['action']}")
        print(f"  Symbol: {response['symbol']}")
        print(f"  Direction: {response['direction']}")
        print(f"  Lot Size: {response['lot_size']}")
        print(f"  Entry Price: {response['entry_price']}")
        print(f"  Stop Loss: {response['stop_loss']}")
        print(f"  Take Profit: {response['take_profit']}")
        print(f"  Magic Number: {response['magic_number']}")
        print(f"  Comment: {response['comment']}")
        print()
        
        # Fire torpedo (write response file)
        response_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_submarine_response.json")
        with open(response_file, 'w') as f:
            json.dump(response, f, indent=2)
        
        print("TORPEDO FIRED!")
        print("EURJPY BUY trade response sent to EA")
        print()
        print("SUBMARINE MISSION ACCOMPLISHED!")
        print("EA should execute EURJPY BUY trade now")
        
        # Calculate expected profit/loss
        entry = response['entry_price']
        sl = response['stop_loss']
        tp = response['take_profit']
        lot_size = response['lot_size']
        
        # JPY pair calculations
        risk_pips = abs(entry - sl) * 100  # JPY pairs: 0.01 = 1 pip
        reward_pips = abs(tp - entry) * 100
        
        print()
        print("TRADE METRICS:")
        print(f"  Risk: {risk_pips:.1f} pips")
        print(f"  Reward: {reward_pips:.1f} pips")
        print(f"  R:R Ratio: 1:{reward_pips/risk_pips:.1f}")
        print(f"  Lot Size: {lot_size}")
        print(f"  Account Risk: 0.55%")
        
        return True
        
    except Exception as e:
        print(f"EXECUTION ERROR: {e}")
        return False

if __name__ == "__main__":
    print("MIKROBOT SUBMARINE - EURJPY EXECUTION")
    print("Processing Current Signal...")
    print()
    
    success = asyncio.run(execute_eurjpy_signal())
    
    if success:
        print()
        print("EURJPY TRADE EXECUTED SUCCESSFULLY!")
        print("Captain, your submarine has fired the torpedo!")
    else:
        print()
        print("EURJPY EXECUTION FAILED")
        print("Check signal file and doctrine compliance")