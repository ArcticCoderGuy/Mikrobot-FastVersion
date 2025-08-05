from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
MIKROBOT POSITION SIZER - ATR Dynamic Positioning
=================================================
Implements MIKROBOT_FASTVERSION.md compliant position sizing
- Risk per trade: 0.55% account balance
- ATR range validation: 4-15 pips only
- Dynamic lot calculation: Risk% / ATR_SL_distance
"""

import MetaTrader5 as mt5
import numpy as np
from datetime import datetime, timedelta

class MikrobotPositionSizer:
    def __init__(self):
        self.risk_per_trade_percent = 0.55  # 0.55% per MIKROBOT_FASTVERSION.md
        self.min_atr_pips = 4   # Minimum ATR in pips
        self.max_atr_pips = 15  # Maximum ATR in pips
        
    def get_account_balance(self):
        """Get current account balance"""
        account_info = mt5.account_info()
        if account_info is None:
            raise Exception("Cannot get account info")
        return account_info.balance
    
    def calculate_m1_atr(self, symbol, periods=14):
        """Calculate M1 ATR for the symbol"""
        # Get M1 data for ATR calculation
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, periods + 1)
        if rates is None or len(rates) < periods:
            raise Exception(f"Cannot get M1 data for {symbol}")
        
        # Calculate True Range for each period
        true_ranges = []
        for i in range(1, len(rates)):
            high = rates[i]['high']
            low = rates[i]['low']
            prev_close = rates[i-1]['close']
            
            tr = max(
                high - low,                    # Current high - low
                abs(high - prev_close),        # Current high - previous close
                abs(low - prev_close)          # Current low - previous close
            )
            true_ranges.append(tr)
        
        # Calculate ATR (Average True Range)
        atr = np.mean(true_ranges)
        return atr
    
    def convert_atr_to_pips(self, symbol, atr_value):
        """Convert ATR value to pips based on symbol type"""
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            raise Exception(f"Cannot get symbol info for {symbol}")
        
        # Symbol-specific pip conversion
        if 'JPY' in symbol:
            # JPY pairs: 1 pip = 0.01
            pips = atr_value / 0.01
        elif symbol.startswith('_'):
            # CFD stocks: 1 pip = 1.0 (points)
            pips = atr_value / 1.0
        else:
            # Major pairs: 1 pip = 0.0001
            pips = atr_value / 0.0001
            
        return pips
    
    def validate_atr_range(self, symbol):
        """Validate ATR is within 4-15 pips range"""
        try:
            atr_value = self.calculate_m1_atr(symbol)
            atr_pips = self.convert_atr_to_pips(symbol, atr_value)
            
            print(f"ATR Analysis for {symbol}:")
            print(f"  ATR Value: {atr_value:.5f}")
            print(f"  ATR Pips: {atr_pips:.1f}")
            print(f"  Valid Range: {self.min_atr_pips}-{self.max_atr_pips} pips")
            
            is_valid = self.min_atr_pips <= atr_pips <= self.max_atr_pips
            
            if not is_valid:
                if atr_pips < self.min_atr_pips:
                    print(f"  ERROR REJECTED: ATR {atr_pips:.1f} < {self.min_atr_pips} (too tight)")
                else:
                    print(f"  ERROR REJECTED: ATR {atr_pips:.1f} > {self.max_atr_pips} (too volatile)")
                return False, atr_value, atr_pips
            
            print(f"  OK APPROVED: ATR within valid range")
            return True, atr_value, atr_pips
            
        except Exception as e:
            print(f"ATR validation failed for {symbol}: {e}")
            return False, 0, 0
    
    def calculate_position_size(self, symbol, signal_data=None):
        """Calculate MIKROBOT_FASTVERSION.md compliant position size"""
        print(f"CALCULATING POSITION SIZE FOR {symbol}")
        print("=" * 50)
        
        # Step 1: Validate ATR range (4-15 pips)
        atr_valid, atr_value, atr_pips = self.validate_atr_range(symbol)
        if not atr_valid:
            return None  # Skip trade if ATR invalid
        
        # Step 2: Get account balance and calculate risk amount
        account_balance = self.get_account_balance()
        risk_amount = account_balance * (self.risk_per_trade_percent / 100)
        
        print(f"Risk Calculation:")
        print(f"  Account Balance: ${account_balance:.2f}")
        print(f"  Risk Per Trade: {self.risk_per_trade_percent}%")
        print(f"  Risk Amount: ${risk_amount:.2f}")
        
        # Step 3: Calculate SL distance based on ATR
        # Use ATR as the stop loss distance (ATR-positioned at setup box boundary)
        sl_distance_raw = atr_value
        
        # Step 4: Convert SL distance to USD value per lot
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"ERROR: Cannot get symbol info for {symbol}")
            return None
        
        # Get current price for value calculation
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print(f"ERROR: Cannot get current price for {symbol}")
            return None
        
        current_price = (tick.ask + tick.bid) / 2
        
        # Calculate pip value (USD per pip per lot)
        if 'JPY' in symbol:
            # JPY pairs: $1 per pip per 0.01 lot, so $100 per pip per lot
            usd_per_pip_per_lot = 100
            sl_pips = atr_pips
        elif symbol.startswith('_'):
            # CFD stocks: Contract size varies, use point value
            contract_size = getattr(symbol_info, 'trade_contract_size', 1.0)
            usd_per_pip_per_lot = contract_size * symbol_info.point
            sl_pips = atr_pips
        else:
            # Major pairs: ~$10 per pip per lot (varies by currency)
            if 'USD' in symbol:
                usd_per_pip_per_lot = 10  # Approximate for USD pairs
            else:
                usd_per_pip_per_lot = 10  # Default approximation
            sl_pips = atr_pips
        
        # Calculate total SL risk in USD per lot
        sl_risk_per_lot = sl_pips * usd_per_pip_per_lot
        
        # Step 5: Calculate optimal lot size
        # Position_size = Risk_amount / SL_risk_per_lot
        optimal_lot_size = risk_amount / sl_risk_per_lot
        
        # Step 6: Apply broker constraints
        min_lot = getattr(symbol_info, 'volume_min', 0.01)
        max_lot = getattr(symbol_info, 'volume_max', 100.0)
        lot_step = getattr(symbol_info, 'volume_step', 0.01)
        
        # Round to valid lot size
        final_lot_size = max(min_lot, min(optimal_lot_size, max_lot))
        final_lot_size = round(final_lot_size / lot_step) * lot_step
        
        # Calculate actual risk with final lot size
        actual_risk = final_lot_size * sl_risk_per_lot
        actual_risk_percent = (actual_risk / account_balance) * 100
        
        print(f"Position Sizing Results:")
        print(f"  SL Distance: {sl_pips:.1f} pips")
        print(f"  USD per pip per lot: ${usd_per_pip_per_lot:.2f}")
        print(f"  SL Risk per lot: ${sl_risk_per_lot:.2f}")
        print(f"  Optimal Lot Size: {optimal_lot_size:.4f}")
        print(f"  Final Lot Size: {final_lot_size:.2f}")
        print(f"  Actual Risk: ${actual_risk:.2f} ({actual_risk_percent:.3f}%)")
        
        # Validation check
        if actual_risk_percent > (self.risk_per_trade_percent * 1.5):
            print(f"WARNING: Actual risk {actual_risk_percent:.3f}% exceeds target {self.risk_per_trade_percent}%")
        
        return {
            'lot_size': final_lot_size,
            'atr_value': atr_value,
            'atr_pips': atr_pips,
            'sl_distance': sl_distance_raw,
            'sl_pips': sl_pips,
            'risk_amount': risk_amount,
            'actual_risk': actual_risk,
            'actual_risk_percent': actual_risk_percent,
            'compliant': True,
            'validation_passed': True
        }
    
    def get_compliant_stops(self, symbol, entry_price, direction, sizing_result):
        """Calculate compliant SL/TP based on ATR"""
        atr_distance = sizing_result['sl_distance']
        
        if direction.upper() in ['BUY', 'BULL']:
            sl_price = entry_price - atr_distance
            tp_price = entry_price + (atr_distance * 2)  # 1:2 RR minimum
        else:  # SELL/BEAR
            sl_price = entry_price + atr_distance
            tp_price = entry_price - (atr_distance * 2)
        
        return sl_price, tp_price

def test_position_sizer():
    """Test the position sizer with current symbols"""
    if not mt5.initialize():
        print("ERROR: MT5 initialization failed")
        return
    
    sizer = MikrobotPositionSizer()
    test_symbols = ['EURJPY', 'USDCAD', '_FERRARI.IT']
    
    for symbol in test_symbols:
        print(f"\nTESTING: {symbol}")
        print("=" * 40)
        
        result = sizer.calculate_position_size(symbol)
        if result:
            print(f"OK {symbol}: {result['lot_size']:.2f} lots (ATR: {result['atr_pips']:.1f} pips)")
        else:
            print(f"ERROR {symbol}: REJECTED (ATR out of range)")
    
    mt5.shutdown()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    test_position_sizer()