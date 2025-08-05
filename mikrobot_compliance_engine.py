from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
MIKROBOT COMPLIANCE ENGINE
==========================
Ensures ALL trades comply with MIKROBOT_FASTVERSION.md standard
- Validates 4-phase signals
- Enforces ATR range (4-15 pips)
- Calculates proper position sizing (0.55% risk)
- Rejects non-compliant setups
"""

import MetaTrader5 as mt5
import json
from datetime import datetime
from mikrobot_position_sizer import MikrobotPositionSizer

class MikrobotComplianceEngine:
    def __init__(self):
        self.position_sizer = MikrobotPositionSizer()
        self.master_document = "MIKROBOT_FASTVERSION.MD"
        self.compliance_version = "v1.0"
        
    def validate_4_phase_signal(self, signal_data):
        """Validate signal meets 4-phase criteria"""
        print("4-PHASE SIGNAL VALIDATION:")
        print("-" * 30)
        
        required_fields = [
            'timestamp', 'symbol', 'trade_direction', 
            'ylipip_trigger', 'phase_4_ylipip'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in signal_data:
                print(f"ERROR Missing required field: {field}")
                return False
        
        # Validate ylipip trigger is exactly 0.60
        if signal_data.get('ylipip_trigger') != 0.60:
            print(f"ERROR Invalid ylipip trigger: {signal_data.get('ylipip_trigger')} (must be 0.60)")
            return False
        
        # Validate phase 4 is triggered
        phase_4 = signal_data.get('phase_4_ylipip', {})
        if not phase_4.get('triggered'):
            print(f"ERROR Phase 4 ylipip not triggered")
            return False
        
        # Validate trade direction
        direction = signal_data.get('trade_direction', '').upper()
        if direction not in ['BULL', 'BEAR']:
            print(f"ERROR Invalid trade direction: {direction}")
            return False
        
        print(f"OK 4-Phase validation PASSED")
        print(f"   Symbol: {signal_data['symbol']}")
        print(f"   Direction: {signal_data['trade_direction']}")
        print(f"   Ylipip: {signal_data['ylipip_trigger']}")
        print(f"   Phase 4: {'TRIGGERED' if phase_4.get('triggered') else 'NOT TRIGGERED'}")
        
        return True
    
    def validate_and_size_trade(self, signal_data):
        """Complete validation and position sizing for a trade"""
        print("MIKROBOT COMPLIANCE VALIDATION")
        print("=" * 40)
        print(f"Master Document: {self.master_document}")
        print(f"Compliance Version: {self.compliance_version}")
        print()
        
        # Step 1: Validate 4-phase signal
        if not self.validate_4_phase_signal(signal_data):
            return self._create_rejection_result("4-phase validation failed")
        
        symbol = signal_data['symbol']
        direction = signal_data['trade_direction']
        
        # Step 2: ATR validation and position sizing
        print()
        sizing_result = self.position_sizer.calculate_position_size(symbol, signal_data)
        
        if sizing_result is None:
            return self._create_rejection_result("ATR validation failed - outside 4-15 pips range")
        
        # Step 3: Get current price and calculate stops
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return self._create_rejection_result(f"Cannot get current price for {symbol}")
        
        if direction.upper() in ['BULL', 'BUY']:
            entry_price = tick.ask
            order_type = mt5.ORDER_TYPE_BUY
        else:
            entry_price = tick.bid
            order_type = mt5.ORDER_TYPE_SELL
        
        # Calculate ATR-based stops
        sl_price, tp_price = self.position_sizer.get_compliant_stops(
            symbol, entry_price, direction, sizing_result
        )
        
        print()
        print("COMPLIANCE APPROVED TRADE:")
        print("=" * 30)
        print(f"Symbol: {symbol}")
        print(f"Direction: {direction}")
        print(f"Lot Size: {sizing_result['lot_size']:.2f} (ATR-based)")
        print(f"Entry: {entry_price:.5f}")
        print(f"Stop Loss: {sl_price:.5f}")
        print(f"Take Profit: {tp_price:.5f}")
        print(f"Risk: ${sizing_result['actual_risk']:.2f} ({sizing_result['actual_risk_percent']:.3f}%)")
        print(f"ATR: {sizing_result['atr_pips']:.1f} pips (valid range)")
        
        return {
            'approved': True,
            'symbol': symbol,
            'direction': direction,
            'lot_size': sizing_result['lot_size'],
            'entry_price': entry_price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'order_type': order_type,
            'risk_amount': sizing_result['actual_risk'],
            'risk_percent': sizing_result['actual_risk_percent'],
            'atr_pips': sizing_result['atr_pips'],
            'sizing_result': sizing_result,
            'signal_data': signal_data,
            'compliance_version': self.compliance_version,
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def _create_rejection_result(self, reason):
        """Create rejection result"""
        print()
        print("TRADE REJECTED:")
        print("=" * 20)
        print(f"Reason: {reason}")
        print(f"Compliance: {self.master_document}")
        print()
        
        return {
            'approved': False,
            'rejection_reason': reason,
            'compliance_version': self.compliance_version,
            'validation_timestamp': datetime.now().isoformat()
        }
    
    def execute_compliant_trade(self, validation_result):
        """Execute a compliance-approved trade"""
        if not validation_result.get('approved'):
            print(f"ERROR: Cannot execute rejected trade")
            return False
        
        print("EXECUTING COMPLIANT TRADE:")
        print("=" * 30)
        
        # Prepare order with calculated parameters
        order_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": validation_result['symbol'],
            "volume": validation_result['lot_size'],
            "type": validation_result['order_type'],
            "price": validation_result['entry_price'],
            "sl": validation_result['sl_price'],
            "tp": validation_result['tp_price'],
            "deviation": 20,
            "magic": 999888,
            "comment": f"MIKROBOT_COMPLIANT_{validation_result['symbol']}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        
        # Try multiple filling modes
        filling_modes = [mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_RETURN]
        
        for filling_mode in filling_modes:
            order_request["type_filling"] = filling_mode
            result = mt5.order_send(order_request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"OK TRADE EXECUTED SUCCESSFULLY!")
                print(f"   Order ID: {result.order}")
                print(f"   Deal ID: {result.deal}")
                print(f"   Execution Price: {result.price:.5f}")
                print(f"   Lot Size: {result.volume:.2f}")
                print(f"   Risk: ${validation_result['risk_amount']:.2f}")
                
                # Create compliance record
                compliance_record = {
                    'trade_id': f"COMPLIANT_{validation_result['symbol']}_{int(datetime.now().timestamp())}",
                    'timestamp': datetime.now().isoformat(),
                    'mt5_result': {
                        'order_id': result.order,
                        'deal_id': result.deal,
                        'execution_price': result.price,
                        'volume': result.volume
                    },
                    'validation_result': validation_result,
                    'mikrobot_compliance': {
                        'master_document': self.master_document,
                        'version': self.compliance_version,
                        '4_phase_validated': True,
                        'atr_range_validated': True,
                        'position_sizing_compliant': True,
                        'risk_management_active': True
                    }
                }
                
                # Save compliance record
                filename = f"COMPLIANT_{validation_result['symbol']}_{int(datetime.now().timestamp())}.json"
                with open(filename, 'w', encoding='ascii', errors='ignore') as f:
                    json.dump(compliance_record, f, indent=2)
                
                print(f"   Compliance Record: {filename}")
                return True
            else:
                print(f"Filling mode {filling_mode} failed: {result.comment}")
        
        print(f"ERROR ALL EXECUTION ATTEMPTS FAILED")
        return False

def test_compliance_engine():
    """Test the compliance engine"""
    if not mt5.initialize():
        print("ERROR: MT5 initialization failed")
        return
    
    # Mock signal data
    test_signal = {
        'timestamp': '2025.08.04 08:40',
        'symbol': 'EURJPY',
        'strategy': 'MIKROBOT_FASTVERSION_4PHASE',
        'phase_1_m5_bos': {'direction': 'BULL'},
        'phase_4_ylipip': {'triggered': True},
        'trade_direction': 'BULL',
        'ylipip_trigger': 0.60
    }
    
    engine = MikrobotComplianceEngine()
    
    # Test validation
    result = engine.validate_and_size_trade(test_signal)
    
    if result.get('approved'):
        print("\n" + "="*50)
        print("COMPLIANCE ENGINE TEST: PASSED")
        print("Ready for production deployment")
    else:
        print("\n" + "="*50)
        print("COMPLIANCE ENGINE TEST: REJECTED")
        print(f"Reason: {result.get('rejection_reason')}")
    
    mt5.shutdown()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    test_compliance_engine()