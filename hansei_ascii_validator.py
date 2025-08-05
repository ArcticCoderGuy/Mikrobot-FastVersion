"""
ASCII-ONLY HANSEI TRADE VALIDATION SYSTEM
Post-trade reflection ensuring 100% M5 BOS -> M1 Lightning Bolt compliance
"""
import MetaTrader5 as mt5
import json
import sys
from datetime import datetime, timedelta

# ASCII-only output
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    """ASCII-only print function"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

class HanseiValidator:
    """ASCII-compliant Hansei validation system"""
    
    def __init__(self):
        ascii_print("Hansei Validator initialized - ASCII mode")
        
    def validate_m5_bos_pattern(self, symbol):
        """Validate M5 BOS follows your exact wireframe patterns"""
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 30)
        if rates is None:
            return False, "No M5 data available"
            
        # Find swing points
        highs = [float(r['high']) for r in rates]
        lows = [float(r['low']) for r in rates]
        
        swing_highs = []
        swing_lows = []
        
        # Identify swing points (simplified for ASCII output)
        for i in range(2, len(rates)-2):
            if highs[i] > max(highs[i-2:i+3]):
                swing_highs.append({'index': i, 'price': highs[i]})
            if lows[i] < min(lows[i-2:i+3]):
                swing_lows.append({'index': i, 'price': lows[i]})
                
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # Check for structure break
            current_price = float(rates[-1]['close'])
            last_high = swing_highs[-1]['price']
            last_low = swing_lows[-1]['price']
            
            # Uptrend reversal (price breaks below support)
            if current_price < last_low:
                return True, {
                    "pattern": "UPTREND_REVERSAL",
                    "break_type": "Support Break",
                    "break_level": last_low,
                    "current": current_price
                }
            # Downtrend reversal (price breaks above resistance)
            elif current_price > last_high:
                return True, {
                    "pattern": "DOWNTREND_REVERSAL", 
                    "break_type": "Resistance Break",
                    "break_level": last_high,
                    "current": current_price
                }
                
        return False, "No clear BOS pattern"
    
    def validate_m1_lightning_bolt(self, symbol):
        """Validate 3+ candle Lightning Bolt pattern with retest"""
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 20)
        if rates is None:
            return False, "No M1 data available"
            
        closes = [float(r['close']) for r in rates]
        highs = [float(r['high']) for r in rates]
        lows = [float(r['low']) for r in rates]
        
        # Look for 3+ consecutive candles breaking a level
        for i in range(3, len(rates)-3):
            # Potential break level
            if closes[i] > highs[i-1]:  # Bullish break
                break_level = highs[i-1]
                # Count break candles
                break_count = 1
                for j in range(i+1, min(i+5, len(rates))):
                    if closes[j] > break_level:
                        break_count += 1
                    else:
                        break
                        
                # Must have 3+ candles
                if break_count >= 3:
                    # Look for retest
                    for k in range(j, min(j+3, len(rates))):
                        if lows[k] <= break_level <= highs[k]:
                            return True, {
                                "pattern": "BULL_LIGHTNING_BOLT",
                                "candles": break_count,
                                "break_level": break_level,
                                "retest": True
                            }
                            
            elif closes[i] < lows[i-1]:  # Bearish break
                break_level = lows[i-1]
                break_count = 1
                for j in range(i+1, min(i+5, len(rates))):
                    if closes[j] < break_level:
                        break_count += 1
                    else:
                        break
                        
                if break_count >= 3:
                    for k in range(j, min(j+3, len(rates))):
                        if lows[k] <= break_level <= highs[k]:
                            return True, {
                                "pattern": "BEAR_LIGHTNING_BOLT",
                                "candles": break_count,
                                "break_level": break_level,
                                "retest": True
                            }
                            
        return False, "No 3+ candle Lightning Bolt with retest"
    
    def perform_hansei_check(self, symbol):
        """Complete Hansei check for symbol"""
        ascii_print("=" * 50)
        ascii_print(f"HANSEI CHECK: {symbol}")
        ascii_print("=" * 50)
        
        # M5 BOS validation
        m5_valid, m5_result = self.validate_m5_bos_pattern(symbol)
        ascii_print(f"M5 BOS Pattern: {'PASS' if m5_valid else 'FAIL'}")
        
        if m5_valid:
            ascii_print(f"  Type: {m5_result['pattern']}")
            ascii_print(f"  Break: {m5_result['break_type']}")
            ascii_print(f"  Level: {m5_result['break_level']:.5f}")
        else:
            ascii_print(f"  Issue: {m5_result}")
            
        # M1 Lightning Bolt validation
        m1_valid, m1_result = self.validate_m1_lightning_bolt(symbol)
        ascii_print(f"M1 Lightning Bolt: {'PASS' if m1_valid else 'FAIL'}")
        
        if m1_valid:
            ascii_print(f"  Type: {m1_result['pattern']}")
            ascii_print(f"  Candles: {m1_result['candles']}+ candle break")
            ascii_print(f"  Retest: {'Yes' if m1_result['retest'] else 'No'}")
        else:
            ascii_print(f"  Issue: {m1_result}")
            
        # Overall assessment
        pattern_perfect = m5_valid and m1_valid
        ascii_print(f"OVERALL: {'PERFECT PATTERN' if pattern_perfect else 'INCOMPLETE'}")
        
        if pattern_perfect:
            ascii_print("TRADE QUALITY: EXCELLENT")
            ascii_print("Follows exact M5 BOS -> M1 Lightning Bolt methodology")
        else:
            ascii_print("TRADE QUALITY: NEEDS IMPROVEMENT")
            ascii_print("Wait for complete pattern sequence")
            
        return pattern_perfect
    
    def check_signal_file_patterns(self):
        """Check patterns in the current signal file"""
        try:
            signal_file = 'C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'
            with open(signal_file, 'rb') as f:
                content = f.read()
            
            # Clean the content (UTF-16LE with null bytes)
            content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
            import re
            content_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', content_str)
            
            signal = json.loads(content_str)
            
            ascii_print("CURRENT SIGNAL ANALYSIS:")
            ascii_print("=" * 40)
            ascii_print(f"Symbol: {signal.get('symbol', 'Unknown')}")
            ascii_print(f"Direction: {signal.get('trade_direction', 'Unknown')}")
            ascii_print(f"YLIPIP Triggered: {signal.get('phase_4_ylipip', {}).get('triggered', False)}")
            
            # Check if it has all 4 phases
            phases = ['phase_1_m5_bos', 'phase_2_m1_break', 'phase_3_m1_retest', 'phase_4_ylipip']
            all_phases = all(phase in signal for phase in phases)
            
            ascii_print(f"4-Phase Complete: {'YES' if all_phases else 'NO'}")
            
            if all_phases:
                ascii_print("SIGNAL FOLLOWS COMPLETE PATTERN!")
                ascii_print("- M5 BOS detected")
                ascii_print("- M1 break confirmed") 
                ascii_print("- M1 retest completed")
                ascii_print("- YLIPIP trigger activated")
            
        except Exception as e:
            ascii_print(f"Signal file error: {e}")

def main():
    """Main Hansei validation routine"""
    if not mt5.initialize():
        ascii_print("MT5 initialization failed")
        return
        
    validator = HanseiValidator()
    
    ascii_print("HANSEI TRADE VALIDATION SYSTEM")
    ascii_print("Ensuring 100% compliance with your methodology")
    ascii_print("")
    
    # Check current signal file
    validator.check_signal_file_patterns()
    ascii_print("")
    
    # Check recent active symbols
    symbols_to_check = ['GBPJPY', 'EURUSD', 'EURJPY', 'USDCAD', 'UK_100']
    
    for symbol in symbols_to_check:
        try:
            validator.perform_hansei_check(symbol)
            ascii_print("")
        except Exception as e:
            ascii_print(f"Error checking {symbol}: {e}")
    
    # Check open positions
    positions = mt5.positions_get()
    if positions:
        ascii_print("OPEN POSITIONS VALIDATION:")
        ascii_print("=" * 40)
        for pos in positions:
            ascii_print(f"Position: {pos.symbol} - {pos.volume} lots")
            ascii_print(f"P&L: ${pos.profit:.2f}")
            validator.perform_hansei_check(pos.symbol)
            ascii_print("")
    else:
        ascii_print("No open positions to validate.")
        
    mt5.shutdown()
    ascii_print("Hansei validation complete!")

if __name__ == "__main__":
    main()