"""
LIVE HANSEI VALIDATION TEST
Test the Enhanced EA's pattern validation on current BCHUSD signal
"""
import MetaTrader5 as mt5
import json
import sys
from datetime import datetime
from enhanced_ea_with_hansei import EnhancedMikrobotEA

# ASCII-only enforcement
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    """ASCII-only print function"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def test_live_hansei_validation():
    """Test Hansei validation on live BCHUSD signal"""
    ascii_print("LIVE HANSEI VALIDATION TEST")
    ascii_print("=" * 50)
    
    if not mt5.initialize():
        ascii_print("MT5 initialization failed")
        return
    
    # Initialize Enhanced EA
    ea = EnhancedMikrobotEA()
    
    # Test signal reading and validation
    ascii_print("Testing signal reading and validation...")
    signal = ea.read_signal()
    
    if signal:
        ascii_print(f"Signal detected: {signal.get('symbol', 'Unknown')}")
        ascii_print(f"Direction: {signal.get('trade_direction', 'Unknown')}")
        ascii_print(f"Timestamp: {signal.get('timestamp', 'Unknown')}")
        
        # Test pattern validation
        ascii_print("\nTesting pattern validation...")
        is_valid = ea.validate_signal_pattern(signal)
        
        if is_valid:
            ascii_print("HANSEI PRE-TRADE VALIDATION: PASSED")
            ascii_print("Signal meets all pattern requirements!")
            
            # Test position sizing calculation
            account_info = mt5.account_info()
            if account_info:
                lot_size, risk_amount, atr_pips = ea.calculate_position_size(
                    signal['symbol'], account_info.balance
                )
                
                ascii_print(f"\nPosition Sizing Test:")
                ascii_print(f"  Symbol: {signal['symbol']}")
                ascii_print(f"  Account Balance: ${account_info.balance:.2f}")
                ascii_print(f"  Risk Amount (0.55%): ${risk_amount:.2f}")
                ascii_print(f"  ATR: {atr_pips} pips")
                ascii_print(f"  Calculated Lot Size: {lot_size}")
                
                # Compare to old system
                old_lot_size = 0.01
                improvement = lot_size / old_lot_size
                ascii_print(f"  Old System: {old_lot_size} lots")
                ascii_print(f"  Improvement: {improvement:.0f}x LARGER position!")
                
        else:
            ascii_print("HANSEI PRE-TRADE VALIDATION: FAILED") 
            ascii_print("Signal does not meet pattern requirements")
            
    else:
        ascii_print("No signal detected or signal validation failed")
    
    # Test current market conditions
    ascii_print("\nTesting current market data access...")
    symbols_to_test = ['BCHUSD', 'GBPJPY', 'EURUSD']
    
    for symbol in symbols_to_test:
        rates_m5 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 10)
        rates_m1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 10)
        
        if rates_m5 is not None and rates_m1 is not None:
            ascii_print(f"  {symbol}: M5 data OK ({len(rates_m5)} bars), M1 data OK ({len(rates_m1)} bars)")
        else:
            ascii_print(f"  {symbol}: Data access FAILED")
    
    mt5.shutdown()
    ascii_print("\nHansei validation test complete!")

def test_pattern_recognition():
    """Test pattern recognition capabilities"""
    ascii_print("\nPATTERN RECOGNITION TEST")
    ascii_print("=" * 40)
    
    if not mt5.initialize():
        ascii_print("MT5 initialization failed") 
        return
        
    ea = EnhancedMikrobotEA()
    
    # Test M1 Lightning Bolt detection on multiple symbols
    test_symbols = ['BCHUSD', 'GBPJPY', 'EURUSD', 'GOLD', 'UK_100']
    
    for symbol in test_symbols:
        ascii_print(f"\nTesting {symbol}:")
        
        # Get M1 data
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 20)
        if rates is None:
            ascii_print(f"  No M1 data available")
            continue
            
        # Look for Lightning Bolt pattern manually
        closes = [float(r['close']) for r in rates]
        highs = [float(r['high']) for r in rates]
        lows = [float(r['low']) for r in rates]
        
        lightning_bolt_found = False
        
        for i in range(3, len(rates)-3):
            # Check for bullish break
            if closes[i] > highs[i-1]:
                break_level = highs[i-1]
                break_candles = 1
                
                # Count consecutive break candles
                for j in range(i+1, min(i+6, len(rates))):
                    if closes[j] > break_level:
                        break_candles += 1
                    else:
                        break
                        
                if break_candles >= 3:
                    # Look for retest
                    for k in range(j, min(j+3, len(rates))):
                        if lows[k] <= break_level <= highs[k]:
                            ascii_print(f"  BULL Lightning Bolt: {break_candles}+ candles, retest confirmed")
                            lightning_bolt_found = True
                            break
                    if lightning_bolt_found:
                        break
                        
            # Check for bearish break
            elif closes[i] < lows[i-1]:
                break_level = lows[i-1]
                break_candles = 1
                
                for j in range(i+1, min(i+6, len(rates))):
                    if closes[j] < break_level:
                        break_candles += 1
                    else:
                        break
                        
                if break_candles >= 3:
                    for k in range(j, min(j+3, len(rates))):
                        if lows[k] <= break_level <= highs[k]:
                            ascii_print(f"  BEAR Lightning Bolt: {break_candles}+ candles, retest confirmed")
                            lightning_bolt_found = True
                            break
                    if lightning_bolt_found:
                        break
        
        if not lightning_bolt_found:
            ascii_print(f"  No Lightning Bolt pattern detected")
    
    mt5.shutdown()

if __name__ == "__main__":
    test_live_hansei_validation()
    test_pattern_recognition()