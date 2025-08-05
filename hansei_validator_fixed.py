"""
HANSEI TRADE VALIDATION SYSTEM - FIXED VERSION
Post-trade reflection and pattern validation  
Ensures 100% compliance with M5 BOS -> M1 Lightning Bolt methodology
"""
import MetaTrader5 as mt5
import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

class HanseiTradeValidator:
    """Fixed version with proper MT5 data handling"""
    
    def __init__(self):
        self.validation_results = []
        
    def identify_market_structure(self, rates):
        """Identify HH/HL/LH/LL pattern - FIXED version"""
        # Properly access MT5 structured array data
        highs = np.array([float(r['high']) for r in rates])
        lows = np.array([float(r['low']) for r in rates])
        times = np.array([datetime.fromtimestamp(int(r['time'])) for r in rates])
        
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(rates)-2):
            # Swing high: higher than 2 candles on each side
            if highs[i] > max(highs[i-2:i]) and highs[i] > max(highs[i+1:i+3]):
                swing_highs.append({
                    'index': i,
                    'price': highs[i],
                    'time': times[i],
                    'type': None
                })
                
            # Swing low: lower than 2 candles on each side
            if lows[i] < min(lows[i-2:i]) and lows[i] < min(lows[i+1:i+3]):
                swing_lows.append({
                    'index': i,
                    'price': lows[i],
                    'time': times[i],
                    'type': None
                })
        
        # Classify swing points
        for i in range(1, len(swing_highs)):
            if swing_highs[i]['price'] > swing_highs[i-1]['price']:
                swing_highs[i]['type'] = 'HH'
            else:
                swing_highs[i]['type'] = 'LH'
                
        for i in range(1, len(swing_lows)):
            if swing_lows[i]['price'] > swing_lows[i-1]['price']:
                swing_lows[i]['type'] = 'HL'
            else:
                swing_lows[i]['type'] = 'LL'
                
        return swing_highs, swing_lows
    
    def validate_m5_bos(self, symbol, trade_time):
        """Validate M5 BOS pattern matches your wireframe models"""
        rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M5, trade_time, 50)
        if rates is None or len(rates) < 20:
            return False, "Insufficient M5 data"
            
        swing_highs, swing_lows = self.identify_market_structure(rates)
        
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # Get current price
            current_price = float(rates[-1]['close'])
            
            # Check for uptrend reversal (HH+HL -> Break Down)
            if (len(swing_highs) > 0 and swing_highs[-1]['type'] == 'HH' and 
                len(swing_lows) > 0 and swing_lows[-1]['type'] == 'HL'):
                last_low = swing_lows[-1]['price']
                if current_price < last_low:
                    return True, {
                        "pattern": "UPTREND_REVERSAL_BOS",
                        "structure": "HH+HL -> Break Down",
                        "break_level": last_low,
                        "current_price": current_price,
                        "break_distance": abs(current_price - last_low),
                        "swing_analysis": f"Last HH: {swing_highs[-1]['price']:.5f}, Last HL: {last_low:.5f}"
                    }
                    
            # Check for downtrend reversal (LH+LL -> Break Up)
            elif (len(swing_highs) > 0 and swing_highs[-1]['type'] == 'LH' and 
                  len(swing_lows) > 0 and swing_lows[-1]['type'] == 'LL'):
                last_high = swing_highs[-1]['price']
                if current_price > last_high:
                    return True, {
                        "pattern": "DOWNTREND_REVERSAL_BOS",
                        "structure": "LH+LL -> Break Up",
                        "break_level": last_high,
                        "current_price": current_price,
                        "break_distance": abs(current_price - last_high),
                        "swing_analysis": f"Last LH: {last_high:.5f}, Last LL: {swing_lows[-1]['price']:.5f}"
                    }
                    
        return False, "No valid M5 BOS pattern detected"
    
    def validate_m1_lightning_bolt(self, symbol, trade_time):
        """Validate M1 Lightning Bolt (3+ candle break & retest) pattern"""
        rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, trade_time, 30)
        if rates is None or len(rates) < 10:
            return False, "Insufficient M1 data"
            
        # Convert to proper arrays
        highs = [float(r['high']) for r in rates]
        lows = [float(r['low']) for r in rates]
        closes = [float(r['close']) for r in rates]
        
        # Look for Lightning Bolt pattern
        for i in range(3, len(rates)-3):
            break_level = None
            direction = None
            
            # Bullish break (break above resistance)
            if closes[i] > highs[i-1]:
                break_level = highs[i-1]
                direction = "BULL"
            # Bearish break (break below support)
            elif closes[i] < lows[i-1]:
                break_level = lows[i-1]
                direction = "BEAR"
            else:
                continue
                
            # Count consecutive break candles
            break_candles = 1
            for j in range(i+1, min(i+6, len(rates))):
                if direction == "BULL" and closes[j] > break_level:
                    break_candles += 1
                elif direction == "BEAR" and closes[j] < break_level:
                    break_candles += 1
                else:
                    break
                    
            # Must have 3+ candle Lightning Bolt
            if break_candles >= 3:
                # Look for retest within next 5 candles
                for k in range(j, min(j+5, len(rates))):
                    # Retest: price touches the break level
                    if lows[k] <= break_level <= highs[k]:
                        return True, {
                            "pattern": "LIGHTNING_BOLT_CONFIRMED",
                            "direction": direction,
                            "break_candles": break_candles,
                            "break_level": break_level,
                            "retest_found": True,
                            "retest_candle_offset": k - i,
                            "description": f"{break_candles}+ candle {direction} Lightning Bolt with retest"
                        }
                        
        return False, "No valid 3+ candle Lightning Bolt pattern with retest found"
    
    def quick_hansei_check(self, symbol):
        """Quick Hansei check for any symbol"""
        print(f"\n{'='*60}")
        print(f"HANSEI CHECK - {symbol}")
        print(f"{'='*60}")
        
        current_time = datetime.now()
        
        # Check M5 BOS
        m5_valid, m5_result = self.validate_m5_bos(symbol, current_time)
        print(f"M5 BOS Pattern: {'✓ VALID' if m5_valid else '✗ NOT FOUND'}")
        if m5_valid:
            print(f"  Pattern: {m5_result['pattern']}")
            print(f"  Structure: {m5_result['structure']}")
            print(f"  Break Level: {m5_result['break_level']:.5f}")
            print(f"  Analysis: {m5_result['swing_analysis']}")
        else:
            print(f"  Status: {m5_result}")
            
        # Check M1 Lightning Bolt
        m1_valid, m1_result = self.validate_m1_lightning_bolt(symbol, current_time)
        print(f"\nM1 Lightning Bolt: {'✓ VALID' if m1_valid else '✗ NOT FOUND'}")
        if m1_valid:
            print(f"  Type: {m1_result['description']}")
            print(f"  Break Level: {m1_result['break_level']:.5f}")
            print(f"  Retest: {'Yes' if m1_result['retest_found'] else 'No'}")
        else:
            print(f"  Status: {m1_result}")
            
        # Overall assessment
        trade_quality = m5_valid and m1_valid
        print(f"\nTRADE QUALITY: {'EXCELLENT' if trade_quality else 'INCOMPLETE PATTERN'}")
        
        if trade_quality:
            print("✓ Perfect M5 BOS -> M1 Lightning Bolt sequence!")
            print("✓ Trade follows your exact methodology")
        else:
            print("⚠ Pattern incomplete - wait for full sequence")
            
        return trade_quality

def validate_recent_signals():
    """Validate the recent signals that triggered"""
    if not mt5.initialize():
        print("MT5 initialization failed")
        return
        
    validator = HanseiTradeValidator()
    
    print("HANSEI VALIDATION OF RECENT SIGNAL ACTIVITY")
    print("=" * 60)
    
    # Check recent signals from the json file
    recent_symbols = ['GBPJPY', 'HK_50', 'UK_100', 'BCHUSD']
    
    for symbol in recent_symbols:
        try:
            validator.quick_hansei_check(symbol)
        except Exception as e:
            print(f"Error checking {symbol}: {e}")
            
    # Check open positions
    positions = mt5.positions_get()
    if positions:
        print(f"\nOPEN POSITIONS VALIDATION")
        print("=" * 40)
        for pos in positions:
            print(f"\nPosition: {pos.symbol} - {pos.volume} lots")
            print(f"Entry: {pos.price_open} | Current P&L: ${pos.profit:.2f}")
            validator.quick_hansei_check(pos.symbol)
    
    mt5.shutdown()

if __name__ == "__main__":
    validate_recent_signals()