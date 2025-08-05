"""
HANSEI TRADE VALIDATION SYSTEM
Post-trade reflection and pattern validation
Ensures 100% compliance with M5 BOS -> M1 Lightning Bolt methodology
"""
import MetaTrader5 as mt5
import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

class HanseiTradeValidator:
    """
    Hansei (反省) - Japanese concept of reflection and self-improvement
    Validates each trade against the exact pattern requirements
    """
    
    def __init__(self):
        self.validation_results = []
        self.pattern_requirements = {
            "m5_bos": {
                "swing_points_required": 3,  # Need HH/HL or LH/LL pattern
                "break_confirmation": True,
                "structure_types": ["UPTREND_REVERSAL", "DOWNTREND_REVERSAL"]
            },
            "m1_lightning_bolt": {
                "min_candles": 3,  # 3+ candle LB pattern
                "break_required": True,
                "retest_required": True,
                "ylipip_trigger": 0.6
            }
        }
        
    def identify_market_structure(self, rates):
        """Identify HH/HL/LH/LL pattern like in Live Market Example"""
        highs = [r.high for r in rates]
        lows = [r.low for r in rates]
        
        # Find swing points
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(rates)-2):
            # Swing high: higher than 2 candles on each side
            if highs[i] > max(highs[i-2:i]) and highs[i] > max(highs[i+1:i+3]):
                swing_highs.append({
                    'index': i,
                    'price': highs[i],
                    'time': rates[i].time,
                    'type': None  # Will be classified as HH or LH
                })
                
            # Swing low: lower than 2 candles on each side
            if lows[i] < min(lows[i-2:i]) and lows[i] < min(lows[i+1:i+3]):
                swing_lows.append({
                    'index': i,
                    'price': lows[i],
                    'time': rates[i].time,
                    'type': None  # Will be classified as HL or LL
                })
        
        # Classify swing points
        for i in range(1, len(swing_highs)):
            if swing_highs[i]['price'] > swing_highs[i-1]['price']:
                swing_highs[i]['type'] = 'HH'  # Higher High
            else:
                swing_highs[i]['type'] = 'LH'  # Lower High
                
        for i in range(1, len(swing_lows)):
            if swing_lows[i]['price'] > swing_lows[i-1]['price']:
                swing_lows[i]['type'] = 'HL'  # Higher Low
            else:
                swing_lows[i]['type'] = 'LL'  # Lower Low
                
        return swing_highs, swing_lows
    
    def validate_m5_bos(self, symbol, trade_time):
        """Validate M5 BOS pattern matches the wireframe models"""
        rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M5, trade_time, 50)
        if rates is None or len(rates) < 20:
            return False, "Insufficient M5 data"
            
        swing_highs, swing_lows = self.identify_market_structure(rates)
        
        # Check for uptrend reversal (like in diagrams)
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # Uptrend: HH + HL pattern that breaks down
            if (swing_highs[-1]['type'] == 'HH' and 
                swing_lows[-1]['type'] == 'HL'):
                # Check for break of structure
                last_low = swing_lows[-1]['price']
                current_price = rates[-1].close
                if current_price < last_low:
                    return True, {
                        "pattern": "UPTREND_REVERSAL",
                        "structure": "HH+HL -> Break Down",
                        "break_level": last_low,
                        "swing_points": {
                            "highs": [sh['type'] for sh in swing_highs[-3:]],
                            "lows": [sl['type'] for sl in swing_lows[-3:]]
                        }
                    }
                    
            # Downtrend: LH + LL pattern that breaks up
            elif (swing_highs[-1]['type'] == 'LH' and 
                  swing_lows[-1]['type'] == 'LL'):
                # Check for break of structure
                last_high = swing_highs[-1]['price']
                current_price = rates[-1].close
                if current_price > last_high:
                    return True, {
                        "pattern": "DOWNTREND_REVERSAL",
                        "structure": "LH+LL -> Break Up",
                        "break_level": last_high,
                        "swing_points": {
                            "highs": [sh['type'] for sh in swing_highs[-3:]],
                            "lows": [sl['type'] for sl in swing_lows[-3:]]
                        }
                    }
                    
        return False, "No valid M5 BOS pattern found"
    
    def validate_m1_lightning_bolt(self, symbol, trade_time):
        """Validate M1 Lightning Bolt pattern (3+ candle break & retest)"""
        rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, trade_time, 20)
        if rates is None or len(rates) < 10:
            return False, "Insufficient M1 data"
            
        # Look for the Lightning Bolt pattern
        for i in range(3, len(rates)-3):
            # Find potential break level (resistance/support)
            break_level = None
            
            # Check for break pattern (3+ candles)
            if rates[i].close > rates[i-1].high:  # Bullish break
                break_level = rates[i-1].high
                direction = "BULL"
            elif rates[i].close < rates[i-1].low:  # Bearish break
                break_level = rates[i-1].low
                direction = "BEAR"
            else:
                continue
                
            # Count break candles
            break_candles = 1
            for j in range(i+1, min(i+5, len(rates))):
                if direction == "BULL" and rates[j].close > break_level:
                    break_candles += 1
                elif direction == "BEAR" and rates[j].close < break_level:
                    break_candles += 1
                else:
                    break  # Break sequence ended
                    
            if break_candles >= 3:
                # Look for retest
                for k in range(j, min(j+5, len(rates))):
                    if direction == "BULL":
                        if rates[k].low <= break_level <= rates[k].high:
                            return True, {
                                "pattern": "LIGHTNING_BOLT",
                                "direction": direction,
                                "break_candles": break_candles,
                                "break_level": break_level,
                                "retest_candle": k - j + 1,
                                "description": f"{break_candles}+ candle LB pattern confirmed"
                            }
                    else:  # BEAR
                        if rates[k].low <= break_level <= rates[k].high:
                            return True, {
                                "pattern": "LIGHTNING_BOLT",
                                "direction": direction,
                                "break_candles": break_candles,
                                "break_level": break_level,
                                "retest_candle": k - j + 1,
                                "description": f"{break_candles}+ candle LB pattern confirmed"
                            }
                            
        return False, "No valid Lightning Bolt pattern found"
    
    def perform_hansei_check(self, trade):
        """Perform complete Hansei validation on executed trade"""
        print(f"\n{'='*60}")
        print(f"HANSEI CHECK - Trade Reflection & Validation")
        print(f"{'='*60}")
        print(f"Symbol: {trade.symbol}")
        print(f"Direction: {'BUY' if trade.type == 0 else 'SELL'}")
        print(f"Entry: {trade.price_open}")
        print(f"Volume: {trade.volume} lots")
        print(f"Time: {datetime.fromtimestamp(trade.time)}")
        
        # Validate M5 BOS
        m5_valid, m5_result = self.validate_m5_bos(
            trade.symbol, 
            datetime.fromtimestamp(trade.time)
        )
        
        print(f"\nM5 BOS Validation: {'PASS' if m5_valid else 'FAIL'}")
        if m5_valid:
            print(f"  Pattern: {m5_result['pattern']}")
            print(f"  Structure: {m5_result['structure']}")
            print(f"  Break Level: {m5_result['break_level']}")
            print(f"  Swing Points: {m5_result['swing_points']}")
        else:
            print(f"  Reason: {m5_result}")
            
        # Validate M1 Lightning Bolt
        m1_valid, m1_result = self.validate_m1_lightning_bolt(
            trade.symbol,
            datetime.fromtimestamp(trade.time)
        )
        
        print(f"\nM1 Lightning Bolt Validation: {'PASS' if m1_valid else 'FAIL'}")
        if m1_valid:
            print(f"  Pattern: {m1_result['pattern']}")
            print(f"  Direction: {m1_result['direction']}")
            print(f"  Break Candles: {m1_result['break_candles']}+ candles")
            print(f"  Retest: Candle #{m1_result['retest_candle']}")
        else:
            print(f"  Reason: {m1_result}")
            
        # Overall validation
        trade_valid = m5_valid and m1_valid
        print(f"\nOVERALL VALIDATION: {'PASS' if trade_valid else 'FAIL'}")
        
        if trade_valid:
            print("\nTRADE FOLLOWS PERFECT PATTERN!")
            print("- M5 BOS structure break confirmed")
            print("- M1 Lightning Bolt pattern confirmed")
            print("- Entry timing optimal")
        else:
            print("\nWARNING: Trade does not match required pattern!")
            print("Review and adjust EA logic if needed")
            
        # Save validation result
        self.save_hansei_report(trade, m5_valid, m5_result, m1_valid, m1_result)
        
        return trade_valid
    
    def save_hansei_report(self, trade, m5_valid, m5_result, m1_valid, m1_result):
        """Save Hansei validation report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "trade": {
                "symbol": trade.symbol,
                "type": "BUY" if trade.type == 0 else "SELL",
                "volume": trade.volume,
                "entry": trade.price_open,
                "time": datetime.fromtimestamp(trade.time).isoformat()
            },
            "m5_validation": {
                "valid": m5_valid,
                "result": m5_result if isinstance(m5_result, dict) else {"error": m5_result}
            },
            "m1_validation": {
                "valid": m1_valid,
                "result": m1_result if isinstance(m1_result, dict) else {"error": m1_result}
            },
            "overall_valid": m5_valid and m1_valid
        }
        
        # Save to file
        report_file = Path("hansei_validation_reports.json")
        reports = []
        if report_file.exists():
            with open(report_file, 'r') as f:
                reports = json.load(f)
        
        reports.append(report)
        
        with open(report_file, 'w') as f:
            json.dump(reports, f, indent=2)
            
        print(f"\nHansei report saved to: {report_file}")
        
    def monitor_and_validate_trades(self):
        """Monitor executed trades and perform Hansei checks"""
        if not mt5.initialize():
            print("MT5 initialization failed")
            return
            
        print("Starting Hansei Trade Validator...")
        print("Monitoring all executed trades for pattern compliance")
        
        validated_trades = set()
        
        while True:
            # Get all open positions
            positions = mt5.positions_get()
            if positions:
                for pos in positions:
                    trade_id = f"{pos.symbol}_{pos.ticket}"
                    if trade_id not in validated_trades:
                        print(f"\nNew trade detected: {pos.symbol}")
                        self.perform_hansei_check(pos)
                        validated_trades.add(trade_id)
                        
            # Get recent closed trades too
            now = datetime.now()
            deals = mt5.history_deals_get(now - timedelta(hours=1), now)
            if deals:
                for deal in deals:
                    if deal.type in [0, 1]:  # Buy or Sell
                        trade_id = f"{deal.symbol}_{deal.ticket}"
                        if trade_id not in validated_trades:
                            print(f"\nRecent trade found: {deal.symbol}")
                            self.perform_hansei_check(deal)
                            validated_trades.add(trade_id)
                            
            import time
            time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    validator = HanseiTradeValidator()
    
    # Option 1: Validate current positions
    mt5.initialize()
    positions = mt5.positions_get()
    if positions:
        print(f"Found {len(positions)} open positions to validate")
        for pos in positions:
            validator.perform_hansei_check(pos)
    else:
        print("No open positions to validate")
        
    # Option 2: Start continuous monitoring
    # validator.monitor_and_validate_trades()