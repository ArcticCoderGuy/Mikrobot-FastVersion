#!/usr/bin/env python3
"""
Test the MIKROBOT position sizing system - ASCII safe
"""

import MetaTrader5 as mt5
from mikrobot_position_sizer import MikrobotPositionSizer

def test_position_sizing():
    if not mt5.initialize():
        print("ERROR: MT5 initialization failed")
        return
    
    print("TESTING MIKROBOT ATR-BASED POSITION SIZING")
    print("=" * 50)
    
    # Get account info
    account_info = mt5.account_info()
    print(f"Account Balance: ${account_info.balance:.2f}")
    print(f"Target Risk Per Trade: 0.55% = ${account_info.balance * 0.0055:.2f}")
    print()
    
    sizer = MikrobotPositionSizer()
    test_symbols = ['EURJPY', 'USDCAD', '_FERRARI.IT']
    
    for symbol in test_symbols:
        print(f"TESTING: {symbol}")
        print("-" * 30)
        
        try:
            # Test ATR validation
            atr_valid, atr_value, atr_pips = sizer.validate_atr_range(symbol)
            
            if atr_valid:
                print(f"ATR VALIDATION: PASSED")
                print(f"  ATR: {atr_pips:.1f} pips (valid range: 4-15)")
                
                # Calculate position size
                result = sizer.calculate_position_size(symbol)
                if result:
                    print(f"POSITION SIZING: SUCCESS")
                    print(f"  Lot Size: {result['lot_size']:.2f}")
                    print(f"  Risk: ${result['actual_risk']:.2f} ({result['actual_risk_percent']:.3f}%)")
                    print(f"  Status: APPROVED FOR TRADING")
                else:
                    print(f"POSITION SIZING: FAILED")
            else:
                print(f"ATR VALIDATION: REJECTED")
                print(f"  ATR: {atr_pips:.1f} pips")
                if atr_pips < 4:
                    print(f"  Reason: Too tight (< 4 pips)")
                else:
                    print(f"  Reason: Too volatile (> 15 pips)")
                print(f"  Status: TRADE SKIPPED")
        
        except Exception as e:
            print(f"ERROR: {e}")
        
        print()
    
    print("CURRENT POSITION COMPARISON:")
    print("=" * 30)
    positions = mt5.positions_get()
    if positions:
        for pos in positions:
            current_risk = pos.volume * 100 * 8  # Assuming ~8 pip risk
            risk_percent = (current_risk / account_info.balance) * 100
            print(f"{pos.symbol}: {pos.volume:.2f} lots")
            print(f"  Current Risk: ~${current_risk:.2f} (~{risk_percent:.3f}%)")
            print(f"  SHOULD BE: ~{account_info.balance * 0.0055 / current_risk * pos.volume:.2f} lots for 0.55% risk")
    else:
        print("No positions to compare")
    
    mt5.shutdown()

if __name__ == "__main__":
    test_position_sizing()