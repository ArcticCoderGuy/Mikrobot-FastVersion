#!/usr/bin/env python3
"""
IMMEDIATE DEPLOYMENT - Ferrari.IT SELL Signal
============================================
Execute the fresh Ferrari.IT BEAR signal immediately
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def deploy_ferrari_trade():
    print("FERRARI.IT LIVE TRADE DEPLOYMENT")
    print("=" * 35)
    
    # Ferrari.IT signal data (from system notification 08:10)
    ferrari_signal = {
        'timestamp': '2025.08.04 08:10',
        'symbol': '_FERRARI.IT',
        'strategy': 'MIKROBOT_FASTVERSION_4PHASE',
        'phase_1_m5_bos': {
            'time': '2025.08.04 07:15',
            'price': 376.28000,
            'direction': 'BEAR'
        },
        'phase_2_m1_break': {
            'time': '2025.08.04 07:18', 
            'price': 376.28000
        },
        'phase_3_m1_retest': {
            'time': '2025.08.04 08:08',
            'price': 376.28000
        },
        'phase_4_ylipip': {
            'target': 376.22000,
            'current': 376.18000,
            'triggered': True
        },
        'trade_direction': 'BEAR',
        'current_price': 376.18000,
        'ylipip_trigger': 0.60,
        'confidence': 0.95
    }
    
    print("FRESH SIGNAL ANALYSIS:")
    print(f"Symbol: {ferrari_signal['symbol']}")
    print(f"Direction: {ferrari_signal['trade_direction']} (SELL)")
    print(f"Current Price: €{ferrari_signal['current_price']}")
    print(f"All 4 Phases: COMPLETE")
    print(f"Confidence: {ferrari_signal['confidence']}")
    print()
    
    # Calculate precise trade parameters for Ferrari stock CFD
    current_price = ferrari_signal['current_price']
    retest_price = ferrari_signal['phase_3_m1_retest']['price']
    
    # Ferrari.IT is a stock CFD - use points, not pips
    price_risk = abs(current_price - retest_price)  # Very tight retest
    sl_points = max(price_risk, 0.50)  # Minimum 50 cents stop
    tp_points = sl_points * 2  # 1:2 risk/reward
    
    # SELL trade parameters
    entry_price = current_price  # 376.18
    sl_price = entry_price + sl_points  # Above entry for SELL
    tp_price = entry_price - tp_points  # Below entry for SELL
    
    # Conservative position size
    lot_size = 0.01  # Very small for validation
    
    # Risk calculation (€0.01 per point for stock CFDs)
    risk_euros = sl_points * lot_size * 100  # ~€50 risk
    
    trade_params = {
        'symbol': '_FERRARI.IT',
        'action': 'SELL',
        'lot_size': lot_size,
        'entry_price': entry_price,
        'sl_price': sl_price,
        'tp_price': tp_price,
        'sl_points': sl_points,
        'tp_points': tp_points,
        'risk_euros': risk_euros,
        'asset_class': 'CFD_STOCK'
    }
    
    print("CALCULATED TRADE PARAMETERS:")
    print("=" * 32)
    print(f"Action: SELL {ferrari_signal['symbol']}")
    print(f"Lot Size: {lot_size}")
    print(f"Entry: €{entry_price:.2f}")
    print(f"Stop Loss: €{sl_price:.2f} (+{sl_points:.2f} points)")
    print(f"Take Profit: €{tp_price:.2f} (-{tp_points:.2f} points)")
    print(f"Risk: €{risk_euros:.2f}")
    print(f"Risk/Reward: 1:2")
    print()
    
    print("DEPLOYMENT STATUS:")
    print("- Signal: FRESH (08:10)")
    print("- Phases: ALL COMPLETE")
    print("- Risk: CONSERVATIVE")
    print("- Validation: BLACKROCK-READY")
    print()
    
    # Create deployment record
    deployment_record = {
        'deployment_id': 'FERRARI_001',
        'deployment_time': datetime.now().isoformat(),
        'signal_data': ferrari_signal,
        'trade_parameters': trade_params,
        'deployment_purpose': 'BLACKROCK_VALIDATION',
        'status': 'READY_FOR_EXECUTION',
        'validation_type': 'REAL_MONEY_REAL_TRADE'
    }
    
    # Save deployment record
    with open('FERRARI_DEPLOYMENT_001.json', 'w') as f:
        json.dump(deployment_record, f, indent=2)
    
    print("DEPLOYMENT READY!")
    print(f"Record saved: FERRARI_DEPLOYMENT_001.json")
    print()
    print("EXECUTION COMMANDS:")
    print("1. python live_trading_system.py  # Start live system")
    print("2. Check live_trading.log for execution")
    print("3. Monitor MT5 for Ferrari.IT SELL position")
    print()
    print("THIS WILL BE A REAL TRADE WITH REAL MONEY!")
    
    return deployment_record

if __name__ == "__main__":
    deploy_ferrari_trade()