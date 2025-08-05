#!/usr/bin/env python3
"""
MIKROBOT COMPLIANT SERVICE - Production Trading System
======================================================
Ensures 100% MIKROBOT_FASTVERSION.md compliance for ALL trades
- ATR Dynamic Position Sizing (0.55% risk per trade)
- 4-Phase Signal Validation 
- ATR Range Validation (4-15 pips)
- Complete audit trail and compliance records
"""

import MetaTrader5 as mt5
import json
import time
import re
from datetime import datetime
from pathlib import Path
from mikrobot_compliance_engine import MikrobotComplianceEngine

class MikrobotCompliantService:
    def __init__(self):
        self.signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
        self.compliance_engine = MikrobotComplianceEngine()
        self.last_signal_timestamp = None
        self.service_log = []
        self.trades_executed = 0
        self.trades_rejected = 0
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.service_log.append(log_entry)
        
        # Keep last 200 entries
        if len(self.service_log) > 200:
            self.service_log = self.service_log[-200:]
    
    def initialize_service(self):
        """Initialize MT5 and compliance service"""
        if not mt5.initialize():
            self.log("ERROR: MT5 initialization failed")
            return False
        
        account_info = mt5.account_info()
        self.log("MIKROBOT COMPLIANT SERVICE STARTED")
        self.log("=" * 45)
        self.log(f"Master Document: MIKROBOT_FASTVERSION.MD")
        self.log(f"Compliance: ATR Dynamic Positioning ACTIVE")
        self.log(f"Risk Per Trade: 0.55% account balance")
        self.log(f"ATR Range: 4-15 pips (enforced)")
        self.log(f"Account: {account_info.login}")
        self.log(f"Balance: ${account_info.balance:.2f}")
        self.log("Monitoring EA 4-phase signals...")
        return True
    
    def read_ea_signal(self):
        """Read and parse EA 4-phase signal"""
        try:
            if not self.signal_file.exists():
                return None
                
            with open(self.signal_file, 'r', encoding='utf-16-le') as f:
                content = f.read()
                
            # Clean Unicode issues
            content = re.sub(r'\x00', '', content)
            content = re.sub(r' +', ' ', content)
            
            signal_data = json.loads(content)
            
            # Check if new signal
            if signal_data.get('timestamp') == self.last_signal_timestamp:
                return None  # Already processed
                
            return signal_data
                
        except Exception as e:
            self.log(f"Signal read error: {e}")
            return None
    
    def process_signal(self, signal_data):
        """Process signal through compliance engine"""
        self.log(f"NEW SIGNAL DETECTED: {signal_data.get('symbol')} {signal_data.get('trade_direction')}")
        self.log(f"Signal Time: {signal_data.get('timestamp')}")
        
        # Run compliance validation
        validation_result = self.compliance_engine.validate_and_size_trade(signal_data)
        
        if validation_result.get('approved'):
            self.log("COMPLIANCE VALIDATION: APPROVED")
            self.log(f"Position Size: {validation_result['lot_size']:.2f} lots (ATR-based)")
            self.log(f"Risk: ${validation_result['risk_amount']:.2f} ({validation_result['risk_percent']:.3f}%)")
            self.log(f"ATR: {validation_result['atr_pips']:.1f} pips (valid range)")
            
            # Execute compliant trade
            if self.compliance_engine.execute_compliant_trade(validation_result):
                self.trades_executed += 1
                self.log(f"TRADE EXECUTED SUCCESSFULLY! (Total: {self.trades_executed})")
                self.last_signal_timestamp = signal_data.get('timestamp')
            else:
                self.log("TRADE EXECUTION FAILED!")
                
        else:
            self.trades_rejected += 1
            self.log("COMPLIANCE VALIDATION: REJECTED")
            self.log(f"Reason: {validation_result.get('rejection_reason')}")
            self.log(f"Total Rejected: {self.trades_rejected}")
            self.last_signal_timestamp = signal_data.get('timestamp')  # Mark as processed
    
    def monitor_positions(self):
        """Monitor active positions"""
        positions = mt5.positions_get()
        if not positions:
            return
        
        total_pnl = sum(pos.profit for pos in positions)
        self.log(f"Portfolio: {len(positions)} positions, P&L: ${total_pnl:.2f}")
        
        # Log individual positions
        for pos in positions:
            direction = "BUY" if pos.type == 0 else "SELL"
            pnl_sign = "+" if pos.profit >= 0 else ""
            self.log(f"  {pos.symbol} {direction} {pos.volume}: {pnl_sign}${pos.profit:.2f}")
    
    def log_service_stats(self):
        """Log service statistics"""
        account_info = mt5.account_info()
        runtime = datetime.now() - self.service_start_time
        
        self.log("SERVICE STATISTICS:")
        self.log(f"  Runtime: {runtime}")
        self.log(f"  Trades Executed: {self.trades_executed}")
        self.log(f"  Trades Rejected: {self.trades_rejected}")
        self.log(f"  Success Rate: {(self.trades_executed/(self.trades_executed+self.trades_rejected)*100) if (self.trades_executed+self.trades_rejected) > 0 else 0:.1f}%")
        self.log(f"  Current Balance: ${account_info.balance:.2f}")
    
    def save_service_log(self):
        """Save service log to file"""
        log_data = {
            'service_name': 'MIKROBOT_COMPLIANT_SERVICE',
            'start_time': self.service_start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'trades_executed': self.trades_executed,
            'trades_rejected': self.trades_rejected,
            'compliance_version': self.compliance_engine.compliance_version,
            'log_entries': self.service_log
        }
        
        filename = f"mikrobot_service_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        self.log(f"Service log saved: {filename}")
    
    def run_compliant_service(self):
        """Main compliant service loop"""
        if not self.initialize_service():
            return
        
        self.service_start_time = datetime.now()
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                
                # Check for new signals
                signal_data = self.read_ea_signal()
                if signal_data:
                    self.process_signal(signal_data)
                
                # Monitor positions every 12 cycles (1 minute)
                if cycle_count % 12 == 0:
                    self.monitor_positions()
                
                # Service stats every 120 cycles (10 minutes)
                if cycle_count % 120 == 0:
                    self.log_service_stats()
                    cycle_count = 0  # Reset counter
                
                time.sleep(5)  # 5-second monitoring cycle
                
        except KeyboardInterrupt:
            self.log("Service stopped by user")
        except Exception as e:
            self.log(f"Service error: {e}")
        finally:
            self.log("Shutting down compliant service...")
            self.log_service_stats()
            self.save_service_log()
            mt5.shutdown()
            self.log("MT5 connection closed")
            self.log("MIKROBOT COMPLIANT SERVICE STOPPED")

def main():
    """Run the compliant service"""
    service = MikrobotCompliantService()
    service.run_compliant_service()

if __name__ == "__main__":
    main()