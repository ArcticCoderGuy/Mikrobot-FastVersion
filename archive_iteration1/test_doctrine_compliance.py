from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Test MIKROBOT_FASTVERSION.md doctrine compliance with current signal
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from submarine_command_center import SubmarineCommandCenter

async def test_doctrine_compliance():
    """Test the current signal against doctrine"""
    
    print("TESTING MIKROBOT_FASTVERSION.md DOCTRINE COMPLIANCE")
    print("=" * 60)
    
    # Read current signal
    signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
    
    if not signal_file.exists():
        print("ERROR No signal file found")
        return
    
    try:
        # Read with UTF-16 encoding
        with open(signal_file, 'r', encoding='utf-16') as f:
            signal_content = f.read()
        
        # Parse JSON
        signal_data = json.loads(signal_content)
        
        print("CURRENT SIGNAL DATA:")
        print(f"  Symbol: {signal_data.get('symbol')}")
        print(f"  Strategy: {signal_data.get('strategy')}")
        print(f"  Trade Direction: {signal_data.get('trade_direction')}")
        print(f"  Current Price: {signal_data.get('current_price')}")
        
        # Check ylipip
        ylipip_data = signal_data.get('phase_4_ylipip', {})
        print(f"  Ylipip Triggered: {ylipip_data.get('triggered')}")
        print(f"  Ylipip Target: {ylipip_data.get('target')}")
        
        print()
        print("DOCTRINE VALIDATION TEST:")
        
        # Create submarine and test validation
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
                print("OK SIGNAL MEETS ALL MIKROBOT_FASTVERSION.md REQUIREMENTS!")
                print("ROCKET Should execute trade immediately!")
                
                # Test response generation
                risk_calc = submarine.risk_reactor.calculate_submarine_risk(
                    signal_data.get('symbol'), atr_result['atr_pips'], 100000, 0.55
                )
                
                response = await submarine._generate_doctrine_compliant_response(
                    signal_data, risk_calc, atr_result
                )
                
                print()
                print("GENERATED TRADE RESPONSE:")
                print(f"  Action: {response['action']}")
                print(f"  Symbol: {response['symbol']}")
                print(f"  Direction: {response['direction']}")
                print(f"  Lot Size: {response['lot_size']}")
                print(f"  Entry: {response['entry_price']}")
                print(f"  Stop Loss: {response['stop_loss']}")
                print(f"  Take Profit: {response['take_profit']}")
                
                # Write the response
                response_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_submarine_response.json")
                with open(response_file, 'w', encoding='ascii', errors='ignore') as f:
                    json.dump(response, f, indent=2)
                
                print()
                print("TARGET TRADE RESPONSE WRITTEN TO EA!")
                print("OK ITERATION 1 COMPLETE - Trade execution ready!")
                
            else:
                print(f"ERROR ATR validation failed: {atr_result['reason']}")
        else:
            print("ERROR Signal does not meet doctrine requirements")
            
    except Exception as e:
        print(f"ERROR Error: {e}")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(test_doctrine_compliance())