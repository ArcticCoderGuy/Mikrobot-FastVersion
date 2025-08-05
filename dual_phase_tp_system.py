"""
DUAL PHASE TP SYSTEM
MIKROBOT_FASTVERSION.md Implementation
Phase 1: 1:1 → Breakeven | Phase 2: Continue to 1:2
Account: 107034605
"""
import MetaTrader5 as mt5
import json
from pathlib import Path
from datetime import datetime
import time
import threading

class DualPhaseTPSystem:
    """
    Dual Phase Take Profit System according to MIKROBOT_FASTVERSION.md
    Standard Phase: 1:1 take-profit (close full position)
    XPWS Phase: 1:1 → move to breakeven, continue to 1:2
    """
    
    def __init__(self):
        self.common_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files")
        self.monitoring_active = False
        self.monitoring_thread = None
        self.positions_status = {}
        
    def connect_mt5(self):
        """Connect to MT5 account 107034605"""
        if not mt5.initialize():
            return False
        
        login = 107034605
        password = "RcEw_s7w"
        server = "Ava-Demo 1-MT5"
        
        return mt5.login(login, password, server)
    
    def calculate_profit_ratio(self, position):
        """Calculate current profit ratio for position"""
        entry_price = position.price_open
        current_price = position.price_current
        sl_price = position.sl
        
        if sl_price == 0:
            return 0.0  # No SL set
            
        if position.type == mt5.POSITION_TYPE_BUY:
            # BUY position
            risk_distance = entry_price - sl_price
            profit_distance = current_price - entry_price
        else:
            # SELL position
            risk_distance = sl_price - entry_price
            profit_distance = entry_price - current_price
            
        if risk_distance <= 0:
            return 0.0
            
        profit_ratio = profit_distance / risk_distance
        return profit_ratio
    
    def is_xpws_active_for_symbol(self, symbol):
        """Check if XPWS mode is active for symbol"""
        xpws_file = self.common_path / "xpws_status.json"
        
        try:
            if xpws_file.exists():
                with open(xpws_file, 'r') as f:
                    xpws_data = json.load(f)
                    symbol_data = xpws_data.get("symbols", {}).get(symbol, {})
                    return symbol_data.get("xpws_active", False)
        except Exception as e:
            print(f"Error reading XPWS status: {e}")
            
        return False
    
    def move_sl_to_breakeven(self, position):
        """Move stop loss to breakeven (entry price)"""
        ticket = position.ticket
        symbol = position.symbol
        entry_price = position.price_open
        current_sl = position.sl
        current_tp = position.tp
        
        # Check if already at breakeven
        if abs(current_sl - entry_price) < 0.00001:
            return True, "Already at breakeven"
            
        # Prepare modify request
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": entry_price,
            "tp": current_tp,
            "symbol": symbol,
        }
        
        # Send modify request
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True, f"SL moved to breakeven: {entry_price}"
        else:
            return False, f"Failed to move SL: {result.comment}"
    
    def set_phase2_tp(self, position, ratio_2_0=True):
        """Set Phase 2 take profit (1:2 ratio)"""
        ticket = position.ticket
        symbol = position.symbol
        entry_price = position.price_open
        sl_price = position.sl  # Should be at breakeven now
        
        if position.type == mt5.POSITION_TYPE_BUY:
            # BUY position - TP above entry
            risk_distance = entry_price - sl_price
            tp_price = entry_price + (risk_distance * 2.0)  # 1:2 ratio
        else:
            # SELL position - TP below entry
            risk_distance = sl_price - entry_price
            tp_price = entry_price - (risk_distance * 2.0)  # 1:2 ratio
            
        # Prepare modify request
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": sl_price,  # Keep current SL (breakeven)
            "tp": tp_price,
            "symbol": symbol,
        }
        
        # Send modify request
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True, f"Phase 2 TP set: {tp_price} (1:2 ratio)"
        else:
            return False, f"Failed to set Phase 2 TP: {result.comment}"
    
    def close_position_at_1_1(self, position):
        """Close full position at 1:1 ratio (Standard mode)"""
        ticket = position.ticket
        symbol = position.symbol
        volume = position.volume
        
        if position.type == mt5.POSITION_TYPE_BUY:
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid
        else:
            trade_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
            
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": symbol,
            "volume": volume,
            "type": trade_type,
            "price": price,
            "comment": "1:1 TP - Standard Mode"
        }
        
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            return True, f"Position closed at 1:1 ratio"
        else:
            return False, f"Failed to close position: {result.comment}"
    
    def monitor_position(self, position):
        """Monitor individual position for dual phase TP"""
        ticket = position.ticket
        symbol = position.symbol
        
        # Check current profit ratio
        profit_ratio = self.calculate_profit_ratio(position)
        
        # Get position status
        pos_status = self.positions_status.get(ticket, {
            "phase": 1,
            "breakeven_moved": False,
            "xpws_mode": self.is_xpws_active_for_symbol(symbol)
        })
        
        # Update position status
        self.positions_status[ticket] = pos_status
        
        action_taken = None
        
        # Phase 1: Check if 1:1 ratio reached
        if profit_ratio >= 1.0 and pos_status["phase"] == 1:
            
            if pos_status["xpws_mode"]:
                # XPWS Mode: Move to breakeven and continue to 1:2
                if not pos_status["breakeven_moved"]:
                    success, message = self.move_sl_to_breakeven(position)
                    if success:
                        pos_status["breakeven_moved"] = True
                        pos_status["phase"] = 2
                        action_taken = f"XPWS Phase 1→2: {message}"
                        
                        # Set Phase 2 TP (1:2)
                        success2, message2 = self.set_phase2_tp(position)
                        if success2:
                            action_taken += f" | {message2}"
                    else:
                        action_taken = f"Failed breakeven move: {message}"
            else:
                # Standard Mode: Close at 1:1
                success, message = self.close_position_at_1_1(position)
                if success:
                    action_taken = f"Standard Mode: {message}"
                    # Remove from monitoring
                    if ticket in self.positions_status:
                        del self.positions_status[ticket]
                else:
                    action_taken = f"Failed 1:1 close: {message}"
        
        return {
            "ticket": ticket,
            "symbol": symbol,
            "profit_ratio": round(profit_ratio, 3),
            "phase": pos_status["phase"],
            "xpws_mode": pos_status["xpws_mode"],
            "breakeven_moved": pos_status["breakeven_moved"],
            "action_taken": action_taken
        }
    
    def monitor_all_positions(self):
        """Monitor all open positions for dual phase TP"""
        positions = mt5.positions_get()
        if not positions:
            return []
            
        monitoring_results = []
        
        for position in positions:
            result = self.monitor_position(position)
            monitoring_results.append(result)
            
            if result["action_taken"]:
                print(f"TARGET: {result['symbol']} | Phase {result['phase']} | {result['action_taken']}")
        
        return monitoring_results
    
    def start_continuous_monitoring(self, interval_seconds=5):
        """Start continuous monitoring of positions"""
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    if self.connect_mt5():
                        self.monitor_all_positions()
                    time.sleep(interval_seconds)
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(interval_seconds)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        return "Dual Phase TP monitoring started"
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1)
        return "Dual Phase TP monitoring stopped"
    
    def get_monitoring_status(self):
        """Get current monitoring status"""
        status = {
            "monitoring_active": self.monitoring_active,
            "monitored_positions": len(self.positions_status),
            "positions_detail": self.positions_status,
            "timestamp": datetime.now().isoformat()
        }
        
        return status
    
    def save_monitoring_status(self):
        """Save monitoring status to file"""
        status = self.get_monitoring_status()
        status_file = self.common_path / "dual_phase_tp_status.json"
        
        try:
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving monitoring status: {e}")
            return False

if __name__ == "__main__":
    # Test Dual Phase TP System
    tp_system = DualPhaseTPSystem()
    
    if tp_system.connect_mt5():
        print("SUCCESS: Dual Phase TP System Test")
        print("Account: 107034605")
        
        # Get current positions
        positions = mt5.positions_get()
        
        if positions:
            print(f"\nMonitoring {len(positions)} position(s):")
            
            # Monitor all positions once
            results = tp_system.monitor_all_positions()
            
            for result in results:
                xpws_status = "XPWS" if result["xpws_mode"] else "STD"
                print(f"  {result['symbol']:8} | Phase {result['phase']} | {xpws_status} | R:R {result['profit_ratio']:.2f}")
                
                if result["action_taken"]:
                    print(f"    ACTION: {result['action_taken']}")
        else:
            print("\nNo open positions to monitor")
        
        # Start continuous monitoring
        print(f"\nStarting continuous monitoring...")
        tp_system.start_continuous_monitoring(interval_seconds=5)
        
        # Save status
        if tp_system.save_monitoring_status():
            print(f"SUCCESS: Monitoring status saved to: {tp_system.common_path / 'dual_phase_tp_status.json'}")
        
        # Let it run for a few cycles
        try:
            time.sleep(30)  # Monitor for 30 seconds
        except KeyboardInterrupt:
            pass
        
        tp_system.stop_monitoring()
        print("STOP: Monitoring stopped")
        
        mt5.shutdown()
    else:
        print("ERROR: Failed to connect to MT5")