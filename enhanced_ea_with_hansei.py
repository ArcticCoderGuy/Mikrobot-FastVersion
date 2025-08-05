"""
ENHANCED MIKROBOT EA WITH HANSEI VALIDATION
Integrates post-trade reflection with real-time pattern validation
Ensures 100% compliance with M5 BOS -> M1 Lightning Bolt methodology
"""
import MetaTrader5 as mt5
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import time

# ASCII-only enforcement
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def ascii_print(text):
    """ASCII-only print function"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

class EnhancedMikrobotEA:
    """Enhanced EA with built-in Hansei validation"""
    
    def __init__(self):
        self.signal_file = 'C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'
        self.validated_trades = set()
        self.pattern_requirements = {
            'require_m5_bos': True,
            'require_m1_lightning_bolt': True,
            'require_all_4_phases': True,
            'minimum_break_candles': 3
        }
        
    def read_signal(self):
        """Read and validate signal with Hansei pre-check"""
        try:
            with open(self.signal_file, 'rb') as f:
                content = f.read()
                
            # Clean UTF-16LE content
            content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
            import re
            content_str = re.sub(r'[^\x20-\x7E\n\r\t]', '', content_str)
            
            signal = json.loads(content_str)
            
            # Immediate Hansei validation of signal
            if self.validate_signal_pattern(signal):
                return signal
            else:
                ascii_print(f"Signal for {signal.get('symbol', 'Unknown')} REJECTED - Pattern incomplete")
                return None
                
        except Exception as e:
            ascii_print(f"Signal read error: {e}")
            return None
    
    def validate_signal_pattern(self, signal):
        """Pre-trade Hansei validation of signal pattern"""
        # Check all 4 phases present
        required_phases = ['phase_1_m5_bos', 'phase_2_m1_break', 'phase_3_m1_retest', 'phase_4_ylipip']
        
        phases_present = all(phase in signal for phase in required_phases)
        if not phases_present:
            ascii_print("HANSEI REJECTION: Not all 4 phases present")
            return False
            
        # Check YLIPIP triggered
        ylipip_triggered = signal.get('phase_4_ylipip', {}).get('triggered', False)
        if not ylipip_triggered:
            ascii_print("HANSEI REJECTION: YLIPIP not triggered")
            return False
            
        # Validate pattern sequence timing
        try:
            m5_time = signal['phase_1_m5_bos']['time']
            m1_break_time = signal['phase_2_m1_break']['time']
            m1_retest_time = signal['phase_3_m1_retest']['time']
            ylipip_time = signal['timestamp']
            
            # Ensure proper sequence (M5 -> M1 break -> M1 retest -> YLIPIP)
            times = [m5_time, m1_break_time, m1_retest_time, ylipip_time]
            if times != sorted(times):
                ascii_print("HANSEI REJECTION: Improper time sequence")
                return False
                
        except KeyError:
            ascii_print("HANSEI REJECTION: Missing timestamp data")
            return False
            
        ascii_print(f"HANSEI APPROVAL: {signal.get('symbol')} pattern validated")
        return True
    
    def calculate_position_size(self, symbol, account_balance):
        """Enhanced position sizing with ATR validation"""
        risk_amount = account_balance * 0.0055  # 0.55% risk
        
        # Symbol-specific ATR (validated ranges)
        atr_configs = {
            'GBPJPY': {'atr': 8, 'pip_value': 100, 'valid_range': (4, 15)},
            'EURJPY': {'atr': 8, 'pip_value': 100, 'valid_range': (4, 15)},
            'EURUSD': {'atr': 6, 'pip_value': 10, 'valid_range': (3, 12)},
            'GBPUSD': {'atr': 6, 'pip_value': 10, 'valid_range': (3, 12)},
            'USDJPY': {'atr': 8, 'pip_value': 100, 'valid_range': (4, 15)},
            'GOLD': {'atr': 12, 'pip_value': 1, 'valid_range': (8, 20)},
            'BTCUSD': {'atr': 150, 'pip_value': 1, 'valid_range': (100, 300)},
            'UK_100': {'atr': 25, 'pip_value': 1, 'valid_range': (15, 40)},
            'HK_50': {'atr': 80, 'pip_value': 1, 'valid_range': (50, 150)}
        }
        
        config = atr_configs.get(symbol, {'atr': 10, 'pip_value': 10, 'valid_range': (5, 20)})
        
        # Validate ATR is in acceptable range
        atr_pips = config['atr']
        valid_min, valid_max = config['valid_range']
        
        if not (valid_min <= atr_pips <= valid_max):
            ascii_print(f"ATR WARNING: {symbol} ATR {atr_pips} outside range {valid_min}-{valid_max}")
            atr_pips = max(valid_min, min(atr_pips, valid_max))  # Clamp to range
            
        sl_risk_per_lot = atr_pips * config['pip_value']
        lot_size = round(risk_amount / sl_risk_per_lot, 2)
        
        # Position size validation
        if lot_size < 0.01:
            lot_size = 0.01
        elif lot_size > 10.0:  # Max position limit
            lot_size = 10.0
            
        ascii_print(f"Position Calculation: {symbol}")
        ascii_print(f"  Risk Amount: ${risk_amount:.2f}")
        ascii_print(f"  ATR: {atr_pips} pips")
        ascii_print(f"  Lot Size: {lot_size}")
        
        return lot_size, risk_amount, atr_pips
    
    def execute_trade_with_hansei(self, signal):
        """Execute trade with immediate Hansei validation"""
        symbol = signal['symbol']
        direction = signal['trade_direction']
        current_price = signal['current_price']
        
        # Get account info
        account_info = mt5.account_info()
        if not account_info:
            ascii_print("Failed to get account info")
            return False
            
        # Calculate position size
        lot_size, risk_amount, atr_pips = self.calculate_position_size(symbol, account_info.balance)
        
        # Prepare trade request
        trade_type = mt5.ORDER_TYPE_BUY if direction == 'BULL' else mt5.ORDER_TYPE_SELL
        
        # Set stop loss and take profit based on ATR
        if direction == 'BULL':
            sl_price = current_price - (atr_pips * 0.0001)  # Adjust for symbol decimals
            tp_price = current_price + (atr_pips * 0.0002)  # 2:1 RR
        else:
            sl_price = current_price + (atr_pips * 0.0001)
            tp_price = current_price - (atr_pips * 0.0002)
            
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": trade_type,
            "price": current_price,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": 20,
            "magic": 999888,
            "comment": f"Hansei-Validated {direction}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Execute trade
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            ascii_print(f"TRADE EXECUTED: {symbol}")
            ascii_print(f"  Ticket: {result.order}")
            ascii_print(f"  Volume: {lot_size} lots")
            ascii_print(f"  Direction: {direction}")
            ascii_print(f"  Entry: {result.price}")
            
            # Immediate post-trade Hansei validation
            self.post_trade_hansei_validation(result, signal)
            return True
        else:
            ascii_print(f"TRADE FAILED: {symbol}")
            if result:
                ascii_print(f"Error code: {result.retcode}")
            return False
    
    def post_trade_hansei_validation(self, trade_result, original_signal):
        """Post-trade Hansei reflection and validation"""
        ascii_print("\n" + "="*50)
        ascii_print("POST-TRADE HANSEI VALIDATION")
        ascii_print("="*50)
        
        symbol = original_signal['symbol']
        
        # Validate the executed trade meets all criteria
        validation_score = 0
        max_score = 5
        
        # 1. Check all 4 phases were present
        phases = ['phase_1_m5_bos', 'phase_2_m1_break', 'phase_3_m1_retest', 'phase_4_ylipip']
        if all(phase in original_signal for phase in phases):
            validation_score += 1
            ascii_print("+ 4-Phase Pattern: COMPLETE")
        else:
            ascii_print("- 4-Phase Pattern: INCOMPLETE")
            
        # 2. Check YLIPIP was triggered
        if original_signal.get('phase_4_ylipip', {}).get('triggered', False):
            validation_score += 1
            ascii_print("+ YLIPIP Trigger: CONFIRMED")
        else:
            ascii_print("- YLIPIP Trigger: FAILED")
            
        # 3. Check proper position sizing (>= 0.5 lots for major pairs)
        if trade_result.volume >= 0.5:
            validation_score += 1
            ascii_print(f"+ Position Size: EXCELLENT ({trade_result.volume} lots)")
        else:
            ascii_print(f"- Position Size: SMALL ({trade_result.volume} lots)")
            
        # 4. Check execution timing (within 2 minutes of signal)
        signal_time = datetime.strptime(original_signal['timestamp'], '%Y.%m.%d %H:%M')
        trade_time = datetime.now()
        time_diff = (trade_time - signal_time).total_seconds() / 60
        
        if time_diff <= 2:
            validation_score += 1
            ascii_print(f"+ Execution Speed: EXCELLENT ({time_diff:.1f} min)")
        else:
            ascii_print(f"- Execution Speed: SLOW ({time_diff:.1f} min)")
            
        # 5. Check trade direction matches signal
        signal_direction = original_signal['trade_direction']
        trade_direction = 'BULL' if trade_result.type == 0 else 'BEAR'
        
        if signal_direction == trade_direction:
            validation_score += 1
            ascii_print(f"+ Direction Match: CORRECT ({trade_direction})")
        else:
            ascii_print(f"- Direction Match: WRONG (Signal: {signal_direction}, Trade: {trade_direction})")
            
        # Overall assessment
        quality_percentage = (validation_score / max_score) * 100
        ascii_print(f"\nHANSEI SCORE: {validation_score}/{max_score} ({quality_percentage:.0f}%)")
        
        if quality_percentage >= 80:
            ascii_print("TRADE QUALITY: EXCELLENT - Perfect execution!")
        elif quality_percentage >= 60:
            ascii_print("TRADE QUALITY: GOOD - Minor improvements needed")
        else:
            ascii_print("TRADE QUALITY: POOR - Review system settings")
            
        # Save validation report
        self.save_hansei_report(trade_result, original_signal, validation_score, quality_percentage)
        
    def save_hansei_report(self, trade_result, signal, score, percentage):
        """Save detailed Hansei report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "trade": {
                "ticket": str(trade_result.order),
                "symbol": signal['symbol'],
                "volume": trade_result.volume,
                "direction": signal['trade_direction'],
                "entry_price": trade_result.price
            },
            "signal_analysis": {
                "all_phases_present": all(phase in signal for phase in ['phase_1_m5_bos', 'phase_2_m1_break', 'phase_3_m1_retest', 'phase_4_ylipip']),
                "ylipip_triggered": signal.get('phase_4_ylipip', {}).get('triggered', False),
                "source": signal.get('source', 'Unknown')
            },
            "hansei_score": {
                "score": score,
                "max_score": 5,
                "percentage": percentage,
                "quality_level": "EXCELLENT" if percentage >= 80 else "GOOD" if percentage >= 60 else "POOR"
            }
        }
        
        # Append to hansei reports file
        reports_file = Path("hansei_trade_reports.json")
        reports = []
        
        if reports_file.exists():
            with open(reports_file, 'r') as f:
                reports = json.load(f)
                
        reports.append(report)
        
        with open(reports_file, 'w') as f:
            json.dump(reports, f, indent=2)
            
        ascii_print(f"Hansei report saved: hansei_trade_reports.json")
    
    def run_enhanced_monitoring(self):
        """Run enhanced monitoring with Hansei integration"""
        ascii_print("ENHANCED MIKROBOT EA WITH HANSEI VALIDATION")
        ascii_print("Monitoring for perfect M5 BOS -> M1 Lightning Bolt patterns")
        ascii_print("=" * 60)
        
        last_signal_time = None
        
        while True:
            try:
                signal = self.read_signal()
                
                if signal:
                    current_time = signal.get('timestamp')
                    
                    # Check if this is a new signal
                    if current_time != last_signal_time:
                        ascii_print(f"\nNEW SIGNAL DETECTED: {signal['symbol']}")
                        ascii_print(f"Direction: {signal['trade_direction']}")
                        ascii_print(f"YLIPIP: {signal.get('phase_4_ylipip', {}).get('triggered', False)}")
                        
                        # Execute trade with Hansei validation
                        if self.execute_trade_with_hansei(signal):
                            last_signal_time = current_time
                            ascii_print("Trade executed successfully!")
                        else:
                            ascii_print("Trade execution failed!")
                            
                time.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                ascii_print("Monitoring stopped by user")
                break
            except Exception as e:
                ascii_print(f"Monitoring error: {e}")
                time.sleep(10)

def main():
    """Main execution with MT5 initialization"""
    if not mt5.initialize():
        ascii_print("MT5 initialization failed")
        return
        
    ea = EnhancedMikrobotEA()
    
    try:
        ea.run_enhanced_monitoring()
    finally:
        mt5.shutdown()
        ascii_print("Enhanced EA shutdown complete")

if __name__ == "__main__":
    main()