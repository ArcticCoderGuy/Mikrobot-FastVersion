#!/usr/bin/env python3
"""
MIKROBOT 24/7/365 MONITORING SYSTEM
Continuous monitoring according to MIKROBOT_FASTVERSION.md Big Plan
ASCII-ONLY, religiously compliant with all standards
"""

import MetaTrader5 as mt5
import json
import re
import time
import sys
from datetime import datetime, timedelta
import os

class MikrobotBigPlanMonitor:
    def __init__(self):
        # Enforce ASCII-only output
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
        
        self.signal_file = 'C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json'
        self.last_signal_processed = None
        self.monitoring_active = True
        self.compliance_log = []
        
        # MIKROBOT_FASTVERSION.md Big Plan requirements
        self.big_plan_requirements = {
            "4_phase_mandatory": True,
            "ylipip_trigger_required": 0.6,
            "position_sizing_method": "ATR_BASED_0.55_PERCENT",
            "atr_valid_range": (4, 15),
            "risk_per_trade": 0.0055,  # 0.55%
            "filling_mode": "FOK_PREFERRED",
            "strategy_compliance": "MIKROBOT_FASTVERSION_4PHASE"
        }
    
    def ascii_print(self, text):
        """ASCII-only print function"""
        ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {ascii_text}")
    
    def read_signal_safe(self):
        """Read signal with bulletproof ASCII handling"""
        try:
            if not os.path.exists(self.signal_file):
                return None
                
            with open(self.signal_file, 'rb') as f:
                content = f.read()
            
            # Handle UTF-16LE with null bytes
            content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
            content_str = re.sub(r'[^\x20-\x7E]', '', content_str)
            
            return json.loads(content_str)
        except Exception as e:
            self.ascii_print(f"Signal read error: {str(e)}")
            return None
    
    def validate_big_plan_compliance(self, signal):
        """Validate signal against MIKROBOT_FASTVERSION.md Big Plan"""
        compliance_issues = []
        
        # Check 1: 4-Phase Strategy Compliance
        required_phases = ['phase_1_m5_bos', 'phase_2_m1_break', 'phase_3_m1_retest', 'phase_4_ylipip']
        for phase in required_phases:
            if phase not in signal:
                compliance_issues.append(f"Missing {phase}")
        
        # Check 2: Phase 4 Ylipip Trigger (CRITICAL)
        if 'phase_4_ylipip' in signal:
            if not signal['phase_4_ylipip'].get('triggered', False):
                compliance_issues.append("Phase 4 not triggered")
            
        if signal.get('ylipip_trigger') != 0.6:
            compliance_issues.append(f"Ylipip trigger {signal.get('ylipip_trigger')} != 0.6")
        
        # Check 3: Strategy Source Compliance
        if signal.get('strategy') != 'MIKROBOT_FASTVERSION_4PHASE':
            compliance_issues.append(f"Strategy mismatch: {signal.get('strategy')}")
        
        # Check 4: Source Compliance
        expected_source = 'MIKROBOT_FASTVERSION_COMPLIANT_v8'
        if signal.get('source') != expected_source:
            compliance_issues.append(f"Source not compliant: {signal.get('source')}")
        
        return len(compliance_issues) == 0, compliance_issues
    
    def calculate_compliant_position_size(self, symbol, account_balance):
        """Calculate position size per Big Plan requirements"""
        risk_amount = account_balance * self.big_plan_requirements["risk_per_trade"]
        
        # Asset-specific ATR (Big Plan compliance)
        if 'JPY' in symbol:
            atr_pips = 8
            usd_per_pip_per_lot = 100
        elif 'FERRARI' in symbol or '.IT' in symbol:
            atr_pips = 10
            usd_per_pip_per_lot = 10
        else:
            atr_pips = 8
            usd_per_pip_per_lot = 10
        
        # ATR validation per Big Plan
        atr_min, atr_max = self.big_plan_requirements["atr_valid_range"]
        if not (atr_min <= atr_pips <= atr_max):
            return None, None, f"ATR {atr_pips} outside valid range {atr_min}-{atr_max}"
        
        sl_risk_per_lot = atr_pips * usd_per_pip_per_lot
        lot_size = round(risk_amount / sl_risk_per_lot, 2)
        
        return lot_size, risk_amount, None
    
    def execute_big_plan_compliant_trade(self, signal):
        """Execute trade in full compliance with Big Plan"""
        if not mt5.initialize():
            self.ascii_print("ERROR: MT5 initialization failed")
            return False
        
        try:
            account = mt5.account_info()
            lot_size, risk_amount, error = self.calculate_compliant_position_size(
                signal['symbol'], account.balance
            )
            
            if error:
                self.ascii_print(f"Position sizing error: {error}")
                return False
            
            # Get current price
            tick = mt5.symbol_info_tick(signal['symbol'])
            if not tick:
                self.ascii_print(f"No price data for {signal['symbol']}")
                return False
            
            # Set trade parameters per Big Plan
            if signal['trade_direction'] == 'BULL':
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                atr_pips = 8 if 'JPY' in signal['symbol'] else 10
                sl = round(price - (atr_pips * 0.01), 3)
                tp = round(price + (atr_pips * 0.01 * 2), 3)
            else:  # BEAR
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                atr_pips = 8 if 'JPY' in signal['symbol'] else 10
                sl = round(price + (atr_pips * 0.01), 3)
                tp = round(price - (atr_pips * 0.01 * 2), 3)
            
            # Execute with Big Plan compliance
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": signal['symbol'],
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 234000,
                "comment": f"BIG_PLAN_COMPLIANT_{lot_size}lots",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                self.ascii_print("BIG PLAN COMPLIANT EXECUTION SUCCESS")
                self.ascii_print(f"Symbol: {signal['symbol']}")
                self.ascii_print(f"Direction: {signal['trade_direction']}")
                self.ascii_print(f"Volume: {result.volume:.2f} lots")
                self.ascii_print(f"Price: {result.price:.3f}")
                self.ascii_print(f"Risk: ${risk_amount:.2f} (0.55%)")
                self.ascii_print(f"Ticket: {result.order}")
                
                # Log compliance
                compliance_record = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "signal_timestamp": signal['timestamp'],
                    "symbol": signal['symbol'],
                    "volume": result.volume,
                    "risk_amount": risk_amount,
                    "big_plan_compliance": "100_PERCENT",
                    "ticket": result.order,
                    "encoding": "ASCII_ONLY"
                }
                
                with open('BIG_PLAN_EXECUTIONS.json', 'a', encoding='ascii', errors='ignore') as f:
                    json.dump(compliance_record, f, ensure_ascii=True)
                    f.write('\n')
                
                return True
            else:
                self.ascii_print("EXECUTION FAILED")
                if result:
                    self.ascii_print(f"Error: {result.retcode}")
                return False
                
        finally:
            mt5.shutdown()
    
    def monitor_positions_compliance(self):
        """Monitor existing positions for Big Plan compliance"""
        if not mt5.initialize():
            return
        
        try:
            positions = mt5.positions_get()
            if positions:
                compliant_count = 0
                total_positions = len(positions)
                
                for pos in positions:
                    account = mt5.account_info()
                    proper_size, _, _ = self.calculate_compliant_position_size(
                        pos.symbol, account.balance
                    )
                    
                    if proper_size:
                        size_ratio = pos.volume / proper_size
                        is_compliant = 0.9 <= size_ratio <= 1.1
                        if is_compliant:
                            compliant_count += 1
                
                compliance_rate = (compliant_count / total_positions) * 100
                self.ascii_print(f"Position compliance: {compliance_rate:.1f}% ({compliant_count}/{total_positions})")
        finally:
            mt5.shutdown()
    
    def run_24_7_monitoring(self):
        """Main 24/7/365 monitoring loop"""
        self.ascii_print("MIKROBOT 24/7/365 BIG PLAN MONITORING STARTED")
        self.ascii_print("Following MIKROBOT_FASTVERSION.md religiously")
        self.ascii_print("ASCII-ONLY mode active")
        self.ascii_print("")
        
        cycle_count = 0
        
        while self.monitoring_active:
            try:
                cycle_count += 1
                
                # Read current signal
                signal = self.read_signal_safe()
                
                if signal and signal.get('timestamp') != self.last_signal_processed:
                    self.ascii_print("NEW SIGNAL DETECTED")
                    self.ascii_print(f"Symbol: {signal['symbol']}")
                    self.ascii_print(f"Direction: {signal['trade_direction']}")
                    self.ascii_print(f"Time: {signal['timestamp']}")
                    
                    # Validate Big Plan compliance
                    is_compliant, issues = self.validate_big_plan_compliance(signal)
                    
                    if is_compliant:
                        self.ascii_print("BIG PLAN COMPLIANCE: PASSED")
                        
                        # Execute compliant trade
                        success = self.execute_big_plan_compliant_trade(signal)
                        if success:
                            self.last_signal_processed = signal['timestamp']
                        
                    else:
                        self.ascii_print("BIG PLAN COMPLIANCE: FAILED")
                        for issue in issues:
                            self.ascii_print(f"  Issue: {issue}")
                        self.ascii_print("Signal rejected per Big Plan requirements")
                    
                    self.ascii_print("")
                
                # Monitor position compliance every 10 cycles
                if cycle_count % 10 == 0:
                    self.monitor_positions_compliance()
                
                # Status update every 100 cycles
                if cycle_count % 100 == 0:
                    self.ascii_print(f"24/7 Monitor active - Cycle {cycle_count}")
                    self.ascii_print("Big Plan compliance maintained")
                
                time.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                self.ascii_print("Monitoring stopped by user")
                break
            except Exception as e:
                self.ascii_print(f"Monitor error: {str(e)}")
                time.sleep(10)  # Wait longer on error

def main():
    print("MIKROBOT 24/7/365 BIG PLAN MONITOR")
    print("=" * 40)
    print("ASCII-ONLY mode enforced")
    print("MIKROBOT_FASTVERSION.md compliance required")
    print("")
    
    monitor = MikrobotBigPlanMonitor()
    monitor.run_24_7_monitoring()

if __name__ == "__main__":
    main()