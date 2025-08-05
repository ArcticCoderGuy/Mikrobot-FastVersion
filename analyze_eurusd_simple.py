"""
Simple EURUSD Analysis for Captain
Option C: Direct MT5 ATR Reading + EURUSD Assessment
"""

import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd

def analyze_eurusd():
    """Analyze EURUSD for Captain's tactical assessment"""
    
    print("EURUSD TACTICAL ANALYSIS")
    print("=" * 40)
    
    # Connect to MT5
    if not mt5.initialize():
        print(f"ERROR: MT5 initialization failed, error code: {mt5.last_error()}")
        return None
        
    symbol = 'EURUSD'
    
    try:
        # Check if EURUSD is available
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print("ERROR: EURUSD not available")
            return None
            
        # Enable in Market Watch
        mt5.symbol_select(symbol, True)
        
        # Get current price
        tick = mt5.symbol_info_tick(symbol)
        current_price = tick.bid if tick else 0
        
        print(f"Current Price: {current_price:.5f}")
        print()
        
        # Get ATR data for different timeframes
        print("ATR ANALYSIS (14-period):")
        
        # M1 ATR
        m1_atr = calculate_atr(symbol, mt5.TIMEFRAME_M1, 14)
        if m1_atr:
            m1_pips = m1_atr * 10000
            m1_status = "OPTIMAL" if 4 <= m1_pips <= 15 else "OUT_OF_RANGE"
            print(f"  M1 ATR: {m1_pips:.1f} pips ({m1_status})")
        
        # M5 ATR
        m5_atr = calculate_atr(symbol, mt5.TIMEFRAME_M5, 14)
        if m5_atr:
            m5_pips = m5_atr * 10000
            m5_status = "OPTIMAL" if 4 <= m5_pips <= 15 else "OUT_OF_RANGE"  
            print(f"  M5 ATR: {m5_pips:.1f} pips ({m5_status})")
            
        # M15 ATR
        m15_atr = calculate_atr(symbol, mt5.TIMEFRAME_M15, 14)
        if m15_atr:
            m15_pips = m15_atr * 10000
            m15_status = "OPTIMAL" if 4 <= m15_pips <= 15 else "OUT_OF_RANGE"
            print(f"  M15 ATR: {m15_pips:.1f} pips ({m15_status})")
        
        print()
        
        # Price action analysis
        rates_m1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
        rates_m5 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
        
        if rates_m1 is not None and len(rates_m1) > 20:
            df_m1 = pd.DataFrame(rates_m1)
            
            # Recent price range
            recent_high = df_m1['high'].tail(20).max()
            recent_low = df_m1['low'].tail(20).min()
            price_range_pips = (recent_high - recent_low) * 10000
            
            # Trend analysis
            sma_10 = df_m1['close'].tail(10).mean()
            sma_20 = df_m1['close'].tail(20).mean()
            
            if sma_10 > sma_20:
                trend = "BULLISH"
            elif sma_10 < sma_20:
                trend = "BEARISH"
            else:
                trend = "SIDEWAYS"
            
            print("PRICE ACTION ANALYSIS:")
            print(f"  Recent Range: {price_range_pips:.1f} pips")
            print(f"  Trend (M1): {trend}")
            print(f"  Current vs SMA10: {((current_price - sma_10) * 10000):.1f} pips")
            print(f"  Current vs SMA20: {((current_price - sma_20) * 10000):.1f} pips")
            
        print()
        
        # MIKROBOT DOCTRINE ASSESSMENT
        print("MIKROBOT DOCTRINE ASSESSMENT:")
        
        # Check if any timeframe is in optimal range
        optimal_timeframes = []
        if m1_atr and 4 <= (m1_atr * 10000) <= 15:
            optimal_timeframes.append("M1")
        if m5_atr and 4 <= (m5_atr * 10000) <= 15:
            optimal_timeframes.append("M5")
        if m15_atr and 4 <= (m15_atr * 10000) <= 15:
            optimal_timeframes.append("M15")
            
        if optimal_timeframes:
            print(f"  STATUS: TARGET ACQUIRED")
            print(f"  Optimal Timeframes: {', '.join(optimal_timeframes)}")
            print(f"  RECOMMENDATION: PROCEED WITH MIKROBOT DOCTRINE")
        else:
            print(f"  STATUS: SUBOPTIMAL CONDITIONS")
            print(f"  REASON: ATR outside 4-15 pip doctrine range")
            print(f"  RECOMMENDATION: MONITOR FOR BETTER ENTRY CONDITIONS")
            
        # Check for potential BOS setups
        if rates_m5 is not None and len(rates_m5) > 10:
            df_m5 = pd.DataFrame(rates_m5)
            recent_m5_high = df_m5['high'].tail(10).max()
            recent_m5_low = df_m5['low'].tail(10).min()
            
            print()
            print("M5 BOS POTENTIAL:")
            print(f"  Recent M5 High: {recent_m5_high:.5f}")
            print(f"  Recent M5 Low: {recent_m5_low:.5f}")
            print(f"  Current Price: {current_price:.5f}")
            
            # Check if price is near key levels
            high_distance = abs(current_price - recent_m5_high) * 10000
            low_distance = abs(current_price - recent_m5_low) * 10000
            
            if high_distance < 5:
                print(f"  ALERT: Near M5 resistance ({high_distance:.1f} pips away)")
            elif low_distance < 5:
                print(f"  ALERT: Near M5 support ({low_distance:.1f} pips away)")
            else:
                print(f"  STATUS: In middle range")
                
        return {
            'symbol': symbol,
            'current_price': current_price,
            'atr_m1_pips': m1_pips if m1_atr else None,
            'atr_m5_pips': m5_pips if m5_atr else None,
            'optimal_timeframes': optimal_timeframes,
            'trend': trend if 'trend' in locals() else 'UNKNOWN'
        }
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return None
        
    finally:
        mt5.shutdown()

def calculate_atr(symbol, timeframe, period):
    """Calculate ATR for given symbol and timeframe"""
    
    try:
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, period + 10)
        if rates is None or len(rates) < period:
            return None
            
        df = pd.DataFrame(rates)
        
        # Calculate True Range
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = abs(df['high'] - df['close'].shift(1))
        df['low_close'] = abs(df['low'] - df['close'].shift(1))
        df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        
        # Calculate ATR (Simple Moving Average of True Range)
        atr_value = df['true_range'].rolling(window=period).mean().iloc[-1]
        
        return atr_value
        
    except Exception as e:
        print(f"ATR calculation error: {e}")
        return None

if __name__ == "__main__":
    print("CAPTAIN'S EURUSD TACTICAL ASSESSMENT")
    print("Direct MT5 ATR Analysis")
    print()
    
    result = analyze_eurusd()
    
    if result:
        print()
        print("TACTICAL SUMMARY:")
        print(f"  EURUSD @ {result['current_price']:.5f}")
        print(f"  Trend: {result['trend']}")
        if result['optimal_timeframes']:
            print(f"  DOCTRINE STATUS: READY FOR ENGAGEMENT")
            print(f"  Optimal Timeframes: {', '.join(result['optimal_timeframes'])}")
        else:
            print(f"  DOCTRINE STATUS: HOLD POSITION - WAIT FOR OPTIMAL CONDITIONS")
    else:
        print("TACTICAL ASSESSMENT FAILED")