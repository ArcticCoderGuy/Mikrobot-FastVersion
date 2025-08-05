"""
Simple test for trade execution - no emojis for Windows console
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from submarine_command_center import SubmarineCommandCenter

async def test_simple_execution():
    """Test trade execution without Unicode issues"""
    
    print("MIKROBOT DOCTRINE COMPLIANCE TEST")
    print("=" * 50)
    
    # Read current signal
    signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
    
    if not signal_file.exists():
        print("ERROR: No signal file found")
        return
    
    try:
        # Read with UTF-16 encoding
        with open(signal_file, 'r', encoding='utf-16') as f:
            signal_content = f.read()
        
        signal_data = json.loads(signal_content)
        
        print("SIGNAL DATA:")
        print(f"  Symbol: {signal_data.get('symbol')}")
        print(f"  Strategy: {signal_data.get('strategy')}")
        print(f"  Trade Direction: {signal_data.get('trade_direction')}")
        print(f"  Current Price: {signal_data.get('current_price')}")
        
        ylipip_data = signal_data.get('phase_4_ylipip', {})
        print(f"  Ylipip Triggered: {ylipip_data.get('triggered')}")
        print(f"  Ylipip Target: {ylipip_data.get('target')}")
        
        print()
        print("SUBMARINE VALIDATION:")
        
        # Create submarine and test
        submarine = SubmarineCommandCenter()
        
        # Test doctrine validation
        is_valid = submarine._validate_mikrobot_doctrine(signal_data)
        print(f"  Doctrine Valid: {is_valid}")
        
        if is_valid:
            # Test ATR validation
            atr_result = submarine._validate_atr_range(signal_data)
            print(f"  ATR Valid: {atr_result['valid']}")
            print(f"  ATR Pips: {atr_result['atr_pips']:.1f}")
            
            if atr_result['valid']:
                print()
                print("SUCCESS: Signal meets all doctrine requirements!")
                print("EXECUTING TRADE:")
                
                # Generate trade response
                risk_calc = submarine.risk_reactor.calculate_submarine_risk(
                    signal_data.get('symbol'), atr_result['atr_pips'], 100000, 0.55
                )
                
                response = await submarine._generate_doctrine_compliant_response(
                    signal_data, risk_calc, atr_result
                )
                
                print()
                print("TRADE RESPONSE GENERATED:")
                print(f"  Action: {response['action']}")
                print(f"  Symbol: {response['symbol']}")
                print(f"  Direction: {response['direction']}")
                print(f"  Lot Size: {response['lot_size']}")
                print(f"  Entry: {response['entry_price']}")
                print(f"  Stop Loss: {response['stop_loss']}")
                print(f"  Take Profit: {response['take_profit']}")
                print(f"  Magic Number: {response['magic_number']}")
                print(f"  Comment: {response['comment']}")
                
                # Write response file
                response_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_submarine_response.json")
                with open(response_file, 'w') as f:
                    json.dump(response, f, indent=2)
                
                print()
                print("TRADE RESPONSE WRITTEN TO EA!")
                print("ITERATION 1 COMPLETE!")
                print("Submarine can now execute trades according to doctrine!")
                
            else:
                print(f"FAILED: ATR validation failed: {atr_result['reason']}")
        else:
            print("FAILED: Signal does not meet doctrine requirements")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_execution())