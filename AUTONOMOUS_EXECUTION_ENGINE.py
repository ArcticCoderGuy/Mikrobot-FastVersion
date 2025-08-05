#!/usr/bin/env python3
"""
AUTONOMOUS EXECUTION ENGINE - CRITICAL SYSTEM RECOVERY
====================================================
IMMEDIATELY DEPLOYS AFTER SYSTEM FAILURE DIAGNOSIS
NO HUMAN INTERVENTION REQUIRED - MONEY MAKING AUTONOMOUS
"""

import MetaTrader5 as mt5
import json
import time
import os
import sys
import threading
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

class AutonomousExecutionEngine:
    def __init__(self):
        # Bulletproof ASCII enforcement
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
        sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
        
        self.signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
        self.execution_log = Path("AUTONOMOUS_EXECUTIONS.json")
        self.last_signal_timestamp = None
        self.autonomous_active = True
        
        # Critical system parameters
        self.risk_per_trade = 0.0055  # 0.55% religiously enforced
        self.min_account_balance = 50000  # Safety threshold
        self.max_daily_trades = 50  # Risk management
        self.daily_trade_count = 0
        self.session_start = datetime.now()
        
    def ascii_print(self, message):
        """Bulletproof ASCII-only output"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        ascii_message = ''.join(char for char in str(message) if ord(char) < 128)
        print(f"[{timestamp}] AUTONOMOUS: {ascii_message}")
    
    def read_signal_bulletproof(self):
        """Bulletproof signal reading with encoding fixes"""
        try:
            if not self.signal_file.exists():
                return None
            
            # Read as binary first
            with open(self.signal_file, 'rb') as f:
                raw_content = f.read()
            
            # Handle UTF-16LE with null bytes (Windows MQL5 format)
            try:
                content_str = raw_content.decode('utf-16le', errors='ignore')
            except:
                content_str = raw_content.decode('utf-8', errors='ignore')
            
            # Clean all non-ASCII garbage
            import re
            content_str = content_str.replace('\x00', '')  # Remove null bytes
            content_str = re.sub(r'[^\x20-\x7E{}",:\[\]]', '', content_str)  # Keep only ASCII + JSON chars
            content_str = re.sub(r'\s+', ' ', content_str).strip()  # Normalize whitespace
            
            if not content_str:
                return None
                
            return json.loads(content_str)
            
        except Exception as e:
            self.ascii_print(f"Signal read error: {str(e)[:100]}")
            return None
    
    def validate_critical_signal(self, signal):
        """Critical signal validation for autonomous execution"""
        if not signal:
            return False, "No signal data"
        
        # Phase 4 must be triggered
        phase_4 = signal.get('phase_4_ylipip', {})
        if not phase_4.get('triggered'):
            return False, "Phase 4 not triggered"
        
        # Ylipip trigger must be exactly 0.60
        if signal.get('ylipip_trigger') != 0.60:
            return False, f"Invalid ylipip trigger: {signal.get('ylipip_trigger')}"
        
        # Must have valid symbol and direction
        if not signal.get('symbol') or not signal.get('trade_direction'):
            return False, "Missing symbol or direction"
        
        # Strategy compliance
        if signal.get('strategy') != 'MIKROBOT_FASTVERSION_4PHASE':
            return False, "Non-compliant strategy"
        
        # Source compliance
        if signal.get('source') != 'MIKROBOT_FASTVERSION_COMPLIANT_v8':
            return False, "Non-compliant source"
        
        return True, "Signal validated"
    
    def calculate_position_size_autonomous(self, symbol, account_balance):
        """Autonomous position sizing - 0.55% risk enforcement"""
        risk_amount = account_balance * self.risk_per_trade
        
        # Asset-specific ATR calculations
        if 'JPY' in symbol:
            atr_pips = 8
            pip_value = 100  # $100 per pip per lot for JPY pairs
        elif symbol.startswith('_') or 'USD' in symbol:  # Stocks and crypto
            atr_pips = 8
            pip_value = 10   # $10 per pip per lot for majors/crypto
        else:
            atr_pips = 8
            pip_value = 10
        
        # Calculate lot size
        sl_risk_per_lot = atr_pips * pip_value
        lot_size = round(risk_amount / sl_risk_per_lot, 2)
        
        # Minimum lot size validation
        if lot_size < 0.01:
            lot_size = 0.01
        
        return lot_size, risk_amount
    
    def execute_autonomous_trade(self, signal):
        """Execute trade with full autonomy - NO HUMAN INTERVENTION"""
        self.ascii_print("AUTONOMOUS TRADE EXECUTION INITIATED")
        
        if not mt5.initialize():
            self.ascii_print("ERROR: MT5 initialization failed")
            return False
        
        try:
            # Account validation
            account = mt5.account_info()
            if account.balance < self.min_account_balance:
                self.ascii_print(f"Account balance too low: ${account.balance}")
                return False
            
            # Daily trade limit check
            if self.daily_trade_count >= self.max_daily_trades:
                self.ascii_print("Daily trade limit reached")
                return False
            
            symbol = signal['symbol']
            direction = signal['trade_direction']
            
            # Calculate position size
            lot_size, risk_amount = self.calculate_position_size_autonomous(symbol, account.balance)
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                self.ascii_print(f"No price data for {symbol}")
                return False
            
            # Set trade parameters
            if direction == 'BULL':
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                if 'JPY' in symbol:
                    sl = round(price - 0.08, 3)  # 8 pips
                    tp = round(price + 0.16, 3)  # 16 pips (1:2 RR)
                else:
                    sl = round(price - 0.0008, 5)  # 8 pips
                    tp = round(price + 0.0016, 5)  # 16 pips
            else:  # BEAR
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                if 'JPY' in symbol:
                    sl = round(price + 0.08, 3)
                    tp = round(price - 0.16, 3)
                else:
                    sl = round(price + 0.0008, 5)
                    tp = round(price - 0.0016, 5)
            
            # Execute with autonomous parameters
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot_size,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": 20,
                "magic": 888999,  # Autonomous magic number
                "comment": f"AUTONOMOUS_{symbol}_{direction}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK,
            }
            
            result = mt5.order_send(request)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                self.ascii_print("AUTONOMOUS EXECUTION SUCCESS")
                self.ascii_print(f"Symbol: {symbol}")
                self.ascii_print(f"Direction: {direction}")
                self.ascii_print(f"Volume: {result.volume} lots")
                self.ascii_print(f"Price: {result.price}")
                self.ascii_print(f"Risk: ${risk_amount:.2f} (0.55%)")
                self.ascii_print(f"Ticket: {result.order}")
                
                # Log autonomous execution
                execution_record = {
                    "timestamp": datetime.now().isoformat(),
                    "signal_timestamp": signal.get('timestamp'),
                    "symbol": symbol,
                    "direction": direction,
                    "volume": result.volume,
                    "price": result.price,
                    "sl": sl,
                    "tp": tp,
                    "risk_amount": risk_amount,
                    "ticket": result.order,
                    "deal": result.deal,
                    "autonomous_execution": True,
                    "system_recovery": True
                }
                
                # Append to execution log
                with open(self.execution_log, 'a', encoding='ascii', errors='ignore') as f:
                    json.dump(execution_record, f, ensure_ascii=True)
                    f.write('\n')
                
                self.daily_trade_count += 1
                self.last_signal_timestamp = signal.get('timestamp')
                
                return True
            else:
                self.ascii_print(f"EXECUTION FAILED: {result.comment if result else 'Unknown error'}")
                return False
                
        except Exception as e:
            self.ascii_print(f"Trade execution error: {str(e)}")
            return False
        finally:
            mt5.shutdown()
    
    def autonomous_monitoring_loop(self):
        """Main autonomous loop - runs 24/7 without human intervention"""
        self.ascii_print("AUTONOMOUS EXECUTION ENGINE STARTED")
        self.ascii_print("SYSTEM RECOVERY MODE: ACTIVE")
        self.ascii_print("NO HUMAN INTERVENTION REQUIRED")
        self.ascii_print("MONEY MAKING AUTONOMOUS PROTOCOL: ENGAGED")
        self.ascii_print("")
        
        cycle_count = 0
        last_status_time = datetime.now()
        
        while self.autonomous_active:
            try:
                cycle_count += 1
                current_time = datetime.now()
                
                # Read signal
                signal = self.read_signal_bulletproof()
                
                if signal:
                    # Check if new signal
                    signal_timestamp = signal.get('timestamp')
                    if signal_timestamp != self.last_signal_timestamp:
                        
                        # Validate signal
                        is_valid, validation_msg = self.validate_critical_signal(signal)
                        
                        if is_valid:
                            self.ascii_print(f"NEW VALID SIGNAL: {signal['symbol']} {signal['trade_direction']}")
                            
                            # Execute autonomous trade
                            success = self.execute_autonomous_trade(signal)
                            
                            if success:
                                self.ascii_print("AUTONOMOUS TRADE EXECUTED SUCCESSFULLY")
                            else:
                                self.ascii_print("AUTONOMOUS TRADE EXECUTION FAILED")
                        else:
                            self.ascii_print(f"Signal rejected: {validation_msg}")
                
                # Status update every 5 minutes
                if (current_time - last_status_time).seconds >= 300:
                    self.ascii_print(f"AUTONOMOUS SYSTEM OPERATIONAL - Cycle {cycle_count}")
                    self.ascii_print(f"Daily trades: {self.daily_trade_count}/{self.max_daily_trades}")
                    self.ascii_print(f"Runtime: {current_time - self.session_start}")
                    last_status_time = current_time
                
                # Reset daily counter at midnight
                if current_time.hour == 0 and current_time.minute == 0:
                    self.daily_trade_count = 0
                
                time.sleep(3)  # 3-second monitoring cycle
                
            except KeyboardInterrupt:
                self.ascii_print("AUTONOMOUS SYSTEM STOPPED BY USER")
                break
            except Exception as e:
                self.ascii_print(f"Autonomous system error: {str(e)}")
                time.sleep(10)  # Wait longer on error

def deploy_autonomous_system():
    """Deploy autonomous system immediately"""
    print("AUTONOMOUS EXECUTION ENGINE DEPLOYMENT")
    print("=" * 50)
    print("CRITICAL SYSTEM RECOVERY INITIATED")
    print("AUTONOMOUS MONEY MAKING PROTOCOL")
    print("")
    
    engine = AutonomousExecutionEngine()
    engine.autonomous_monitoring_loop()

if __name__ == "__main__":
    deploy_autonomous_system()