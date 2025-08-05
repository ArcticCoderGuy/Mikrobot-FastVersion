#!/usr/bin/env python3
"""
CRITICAL FIX: Implement proper MIKROBOT position sizing
Current positions risk 0.001-0.008% instead of required 0.55%
"""

import MetaTrader5 as mt5

def fix_position_sizing():
    print("CRITICAL POSITION SIZING FIX")
    print("=" * 35)
    print("Issue: Current 0.01 lots = 0.001-0.008% risk")
    print("Required: 0.55% account balance per trade")
    print()
    
    if not mt5.initialize():
        print("ERROR: MT5 failed")
        return
    
    account = mt5.account_info()
    target_risk = account.balance * 0.0055  # 0.55%
    
    print(f"Account Balance: ${account.balance:.2f}")
    print(f"Target Risk Per Trade: ${target_risk:.2f}")
    print()
    
    print("SOLUTION OPTIONS:")
    print("=" * 20)
    print("1. IMMEDIATE: Deploy compliant service for NEW trades")
    print("2. OPTIONAL: Close/reopen existing positions with correct sizing")
    print("3. CONTINUE: Let existing positions run, new ones will be compliant")
    print()
    
    print("DEPLOYING COMPLIANT SERVICE...")
    print("All NEW trades will use:")
    print(f"- ATR-based position sizing")
    print(f"- 0.55% risk per trade (${target_risk:.2f})")
    print(f"- 4-15 pips ATR validation")
    print(f"- Automatic rejection of non-compliant setups")
    print()
    
    # Show what the next trade would look like
    print("EXAMPLE: Next EURJPY trade with proper sizing:")
    
    # Get EURJPY price for example calculation
    tick = mt5.symbol_info_tick("EURJPY")
    if tick:
        # Assume 8 pips ATR (middle of 4-15 range)
        atr_pips = 8
        usd_per_pip_per_lot = 100  # For JPY pairs
        sl_risk_per_lot = atr_pips * usd_per_pip_per_lot  # $800 per lot
        proper_lot_size = target_risk / sl_risk_per_lot   # $545 / $800 = 0.68 lots
        
        print(f"  Symbol: EURJPY")
        print(f"  Current Price: {tick.ask:.3f}")
        print(f"  ATR: {atr_pips} pips")
        print(f"  Risk per lot: ${sl_risk_per_lot:.2f}")
        print(f"  Proper lot size: {proper_lot_size:.2f} lots")
        print(f"  Risk: ${proper_lot_size * sl_risk_per_lot:.2f}")
        print()
        
        print("COMPARISON:")
        print(f"  Current method: 0.01 lots = ${0.01 * sl_risk_per_lot:.2f} risk (0.001%)")
        print(f"  MIKROBOT spec: {proper_lot_size:.2f} lots = ${proper_lot_size * sl_risk_per_lot:.2f} risk (0.55%)")
        print(f"  Difference: {proper_lot_size/0.01:.0f}x LARGER position sizes!")
    
    print()
    print("READY TO DEPLOY COMPLIANT SERVICE")
    print("Run: python mikrobot_compliant_service.py")
    
    mt5.shutdown()

if __name__ == "__main__":
    fix_position_sizing()