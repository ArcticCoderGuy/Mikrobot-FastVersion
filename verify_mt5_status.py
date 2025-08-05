#!/usr/bin/env python3
"""
MT5 Status Verification - Check agent claims
"""
import MetaTrader5 as mt5
import json
from datetime import datetime, timedelta

def verify_mt5_status():
    print('=== VERIFICATION: MT5 AGENT CLAIMS ===')
    
    # Initialize MT5
    if not mt5.initialize():
        print('CRITICAL: MT5 not initialized - agent claims FALSE')
        return False
    
    # Check account info
    account_info = mt5.account_info()
    if account_info is None:
        print('CRITICAL: No account info - agent claims FALSE')
        mt5.shutdown()
        return False
    
    print(f'Account: {account_info.login}')
    print(f'Balance: ${account_info.balance:.2f}')
    print(f'Equity: ${account_info.equity:.2f}')
    print(f'Profit: ${account_info.profit:.2f}')
    
    # Check for recent trades
    from_date = datetime.now() - timedelta(hours=1)
    deals = mt5.history_deals_get(from_date, datetime.now())
    
    print(f'\nRECENT DEALS (last hour): {len(deals) if deals else 0}')
    if deals:
        for deal in deals[-5:]:  # Last 5 deals
            deal_time = datetime.fromtimestamp(deal.time)
            print(f'Ticket: {deal.ticket}, Symbol: {deal.symbol}, Type: {deal.type}, Volume: {deal.volume}, Price: {deal.price}, Time: {deal_time}')
    
    # Check current positions
    positions = mt5.positions_get()
    print(f'\nCURRENT POSITIONS: {len(positions) if positions else 0}')
    if positions:
        for pos in positions:
            print(f'Ticket: {pos.ticket}, Symbol: {pos.symbol}, Type: {pos.type}, Volume: {pos.volume}, Price: {pos.price_open}, Profit: ${pos.profit:.2f}')
    
    # Check orders
    orders = mt5.orders_get()
    print(f'\nPENDING ORDERS: {len(orders) if orders else 0}')
    if orders:
        for order in orders:
            print(f'Ticket: {order.ticket}, Symbol: {order.symbol}, Type: {order.type}, Volume: {order.volume}, Price: {order.price_open}')
    
    mt5.shutdown()
    print('\n=== VERIFICATION COMPLETE ===')
    
    # Check if agent claims match reality
    agent_claims_valid = False
    if deals and len(deals) > 0:
        # Look for claimed GBPUSD BEAR trade
        for deal in deals:
            if deal.symbol == 'GBPUSD' and deal.ticket == 39931292:
                print(f'VERIFIED: Found claimed trade ticket {deal.ticket}')
                agent_claims_valid = True
                break
    
    return agent_claims_valid

if __name__ == "__main__":
    verify_mt5_status()