#!/usr/bin/env python3
"""
Quick test of MIKROBOT position sizing vs current trades
"""

import MetaTrader5 as mt5

def quick_test():
    if not mt5.initialize():
        print("ERROR: MT5 failed")
        return
    
    account = mt5.account_info()
    print(f"ACCOUNT BALANCE: ${account.balance:.2f}")
    print(f"TARGET RISK PER TRADE: 0.55% = ${account.balance * 0.0055:.2f}")
    print()
    
    positions = mt5.positions_get()
    print(f"CURRENT POSITIONS: {len(positions) if positions else 0}")
    
    if positions:
        for pos in positions:
            print(f"{pos.symbol}: {pos.volume:.2f} lots")
            print(f"  P&L: ${pos.profit:.2f}")
            
            # Estimate current risk (rough calculation)
            if 'JPY' in pos.symbol:
                estimated_risk = pos.volume * 100 * 8  # ~$8 per 0.01 lot for 8 pips
            else:
                estimated_risk = pos.volume * 10 * 8   # ~$8 per 0.01 lot for 8 pips
            
            risk_percent = (estimated_risk / account.balance) * 100
            print(f"  Current Risk: ~${estimated_risk:.2f} ({risk_percent:.3f}%)")
            
            # What it SHOULD be for 0.55% risk
            target_risk = account.balance * 0.0055
            should_be_lots = target_risk / (estimated_risk / pos.volume)
            print(f"  SHOULD BE: {should_be_lots:.2f} lots for 0.55% risk")
            print()
    
    print("ISSUE IDENTIFIED:")
    print("Current positions use fixed 0.01 lots")
    print("MIKROBOT_FASTVERSION.md requires ATR-dynamic sizing:")
    print("- Risk per trade: 0.55% account balance")
    print("- Position size = Risk$ / (ATR_pips * pip_value)")
    print("- ATR must be 4-15 pips range")
    
    mt5.shutdown()

if __name__ == "__main__":
    quick_test()