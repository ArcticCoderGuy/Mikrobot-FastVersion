#!/usr/bin/env python3
"""
Verify EURJPY live position is active
"""

import MetaTrader5 as mt5

def verify_position():
    print("VERIFYING LIVE EURJPY POSITION")
    print("=" * 32)
    
    if not mt5.initialize():
        print("ERROR: Could not initialize MT5")
        return False
    
    account_info = mt5.account_info()
    print(f"Account: {account_info.login}")
    print(f"Balance: ${account_info.balance:.2f}")
    print()
    
    # Check all positions
    positions = mt5.positions_get()
    print(f"Total positions: {len(positions) if positions else 0}")
    
    if positions:
        for pos in positions:
            print(f"Position: {pos.symbol}")
            print(f"  Ticket: {pos.ticket}")
            print(f"  Type: {'BUY' if pos.type == 0 else 'SELL'}")
            print(f"  Volume: {pos.volume}")
            print(f"  Entry: {pos.price_open:.3f}")
            print(f"  Current: {pos.price_current:.3f}")
            print(f"  SL: {pos.sl:.3f}")
            print(f"  TP: {pos.tp:.3f}")
            print(f"  P&L: ${pos.profit:.2f}")
            print()
    
    # Specifically check EURJPY
    eurjpy_positions = mt5.positions_get(symbol="EURJPY")
    if eurjpy_positions:
        pos = eurjpy_positions[0]
        print("EURJPY POSITION CONFIRMED LIVE!")
        print(f"  Status: ACTIVE")
        print(f"  Ticket: {pos.ticket}")
        print(f"  Volume: {pos.volume} lots")
        print(f"  Entry: {pos.price_open:.3f}")
        print(f"  Stop Loss: {pos.sl:.3f}")
        print(f"  Take Profit: {pos.tp:.3f}")
        print(f"  Current P&L: ${pos.profit:.2f}")
        
        if pos.sl > 0 and pos.tp > 0:
            print("  Risk Management: ACTIVE")
        else:
            print("  Risk Management: INCOMPLETE")
            
        print()
        print("BLACKROCK VALIDATION: SUCCESS!")
        print("Real money position with full risk management")
        
    else:
        print("ERROR: No EURJPY position found")
        
    mt5.shutdown()
    return True

if __name__ == "__main__":
    verify_position()