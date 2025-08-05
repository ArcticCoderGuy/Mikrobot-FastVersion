from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MT5 Position Management for M5/M1 BOS Strategy
Manages existing positions on account 107034605 according to strategy rules
"""

import MetaTrader5 as mt5
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class M5M1PositionManager:
    """Manages existing MT5 positions according to M5/M1 BOS strategy rules"""
    
    def __init__(self):
        self.account_number = 107034605
        self.password = "RcEw_s7w"
        self.server = "Ava-Demo 1-MT5"
        
        # M5/M1 BOS Strategy Risk Management Rules
        self.strategy_config = {
            "stop_loss_method": "BREAK_LEVEL",
            "take_profit_ratio": 2.5,
            "pip_precision": 0.2,
            "max_risk_per_trade": 1.0,  # 1% per trade
            "max_daily_loss": 5.0,      # 5% daily limit
            "trailing_stop": True,
            "break_even_threshold": 1.0,  # Move to BE after 1R profit
            "partial_close_levels": [1.5, 2.5]  # Partial closes at 1.5R and 2.5R
        }
        
        self.pip_values = {
            "BTCUSD": 1.0,
            "ETHUSD": 0.1,
            "XRPUSD": 0.0001,
            "LTCUSD": 0.1,
            "EURUSD": 0.0001,
            "GBPUSD": 0.0001,
            "USDJPY": 0.01,
            "AUDUSD": 0.0001
        }
    
    def connect_mt5(self) -> bool:
        """Connect to MT5 terminal"""
        try:
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
            
            # Login to account
            authorized = mt5.login(
                login=self.account_number,
                password=self.password,
                server=self.server
            )
            
            if not authorized:
                logger.error(f"Login failed: {mt5.last_error()}")
                return False
            
            account_info = mt5.account_info()
            logger.info(f"OK Connected to MT5 Account: {account_info.login}")
            logger.info(f"   Server: {account_info.server}")
            logger.info(f"   Balance: ${account_info.balance:.2f}")
            logger.info(f"   Equity: ${account_info.equity:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            return False
    
    def get_current_positions(self) -> List[Dict]:
        """Get all current open positions"""
        try:
            positions = mt5.positions_get()
            if positions is None:
                logger.info("No positions found")
                return []
            
            position_list = []
            for pos in positions:
                position_data = {
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': pos.type,
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'commission': getattr(pos, 'commission', 0.0),  # Handle missing commission
                    'comment': pos.comment,
                    'time': pos.time,
                    'magic': pos.magic,
                    'price_current': getattr(pos, 'price_current', pos.price_open),
                    'identifier': getattr(pos, 'identifier', pos.ticket)
                }
                position_list.append(position_data)
            
            logger.info(f"Found {len(position_list)} open positions")
            return position_list
            
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def analyze_position_levels(self, position: Dict) -> Dict:
        """Analyze position and calculate optimal SL/TP levels according to M5/M1 BOS strategy"""
        symbol = position['symbol']
        entry_price = position['price_open']
        position_type = position['type']  # 0=BUY, 1=SELL
        current_sl = position['sl']
        current_tp = position['tp']
        
        # Get current price
        current_price = self.get_current_price(symbol)
        if not current_price:
            return {'error': 'Cannot get current price'}
        
        # Calculate pip value for symbol
        pip_value = self.pip_values.get(symbol, 0.0001)
        
        # Calculate current P&L in pips
        if position_type == 0:  # BUY position
            pnl_pips = (current_price['bid'] - entry_price) / pip_value
            direction = "BUY"
        else:  # SELL position
            pnl_pips = (entry_price - current_price['ask']) / pip_value
            direction = "SELL"
        
        # Analyze M5/M1 levels for optimal SL/TP
        optimal_levels = self.calculate_m5m1_levels(symbol, entry_price, direction, pip_value)
        
        # Determine recommended action
        recommendation = self.get_position_recommendation(
            position, optimal_levels, pnl_pips, current_price
        )
        
        return {
            'ticket': position['ticket'],
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'current_price': current_price,
            'current_sl': current_sl,
            'current_tp': current_tp,
            'current_pnl_pips': round(pnl_pips, 1),
            'current_pnl_usd': position['profit'],
            'optimal_levels': optimal_levels,
            'recommendation': recommendation,
            'pip_value': pip_value
        }
    
    def calculate_m5m1_levels(self, symbol: str, entry_price: float, direction: str, pip_value: float) -> Dict:
        """Calculate optimal SL/TP levels based on M5/M1 BOS strategy"""
        
        # Get recent M5 and M1 data for structure analysis
        m5_data = self.get_timeframe_data(symbol, mt5.TIMEFRAME_M5, 50)
        m1_data = self.get_timeframe_data(symbol, mt5.TIMEFRAME_M1, 100)
        
        if not m5_data or not m1_data:
            # Fallback to basic strategy levels
            return self.get_fallback_levels(entry_price, direction, pip_value)
        
        # Analyze break of structure levels
        bos_levels = self.identify_bos_levels(m5_data, m1_data, direction)
        
        # Calculate stop loss based on break level
        if direction == "BUY":
            # SL below recent low/break level
            stop_loss = min(bos_levels['support_level'], entry_price - (20 * pip_value))
            # TP based on 2.5R ratio
            sl_distance = entry_price - stop_loss
            take_profit = entry_price + (sl_distance * self.strategy_config['take_profit_ratio'])
        else:  # SELL
            # SL above recent high/break level
            stop_loss = max(bos_levels['resistance_level'], entry_price + (20 * pip_value))
            # TP based on 2.5R ratio
            sl_distance = stop_loss - entry_price
            take_profit = entry_price - (sl_distance * self.strategy_config['take_profit_ratio'])
        
        return {
            'stop_loss': round(stop_loss, 5),
            'take_profit': round(take_profit, 5),
            'risk_reward_ratio': self.strategy_config['take_profit_ratio'],
            'sl_distance_pips': round(abs(entry_price - stop_loss) / pip_value, 1),
            'tp_distance_pips': round(abs(take_profit - entry_price) / pip_value, 1),
            'bos_analysis': bos_levels
        }
    
    def get_timeframe_data(self, symbol: str, timeframe: int, count: int) -> Optional[List]:
        """Get historical data for timeframe analysis"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is not None:
                return rates
            return None
        except Exception as e:
            logger.error(f"Error getting {timeframe} data for {symbol}: {e}")
            return None
    
    def identify_bos_levels(self, m5_data, m1_data, direction: str) -> Dict:
        """Identify break of structure levels from M5/M1 data"""
        
        # Analyze recent M5 structure
        m5_highs = [bar['high'] for bar in m5_data[-20:]]
        m5_lows = [bar['low'] for bar in m5_data[-20:]]
        
        # Analyze recent M1 structure
        m1_highs = [bar['high'] for bar in m1_data[-50:]]
        m1_lows = [bar['low'] for bar in m1_data[-50:]]
        
        if direction == "BUY":
            # For BUY, find support levels
            support_level = min(m5_lows[-10:])  # Recent M5 support
            m1_support = min(m1_lows[-20:])     # Recent M1 support
            
            return {
                'support_level': min(support_level, m1_support),
                'resistance_level': max(m5_highs[-5:]),
                'structure_type': 'BULLISH_BOS',
                'm5_support': support_level,
                'm1_support': m1_support
            }
        else:  # SELL
            # For SELL, find resistance levels
            resistance_level = max(m5_highs[-10:])  # Recent M5 resistance
            m1_resistance = max(m1_highs[-20:])     # Recent M1 resistance
            
            return {
                'resistance_level': max(resistance_level, m1_resistance),
                'support_level': min(m5_lows[-5:]),
                'structure_type': 'BEARISH_BOS',
                'm5_resistance': resistance_level,
                'm1_resistance': m1_resistance
            }
    
    def get_fallback_levels(self, entry_price: float, direction: str, pip_value: float) -> Dict:
        """Fallback SL/TP calculation when market data unavailable"""
        sl_pips = 20  # Default 20 pip stop loss
        tp_pips = sl_pips * self.strategy_config['take_profit_ratio']
        
        if direction == "BUY":
            stop_loss = entry_price - (sl_pips * pip_value)
            take_profit = entry_price + (tp_pips * pip_value)
        else:
            stop_loss = entry_price + (sl_pips * pip_value)
            take_profit = entry_price - (tp_pips * pip_value)
        
        return {
            'stop_loss': round(stop_loss, 5),
            'take_profit': round(take_profit, 5),
            'risk_reward_ratio': self.strategy_config['take_profit_ratio'],
            'sl_distance_pips': sl_pips,
            'tp_distance_pips': tp_pips,
            'bos_analysis': {'type': 'FALLBACK_LEVELS'}
        }
    
    def get_position_recommendation(self, position: Dict, optimal_levels: Dict, pnl_pips: float, current_price: Dict) -> Dict:
        """Get recommendation for position management"""
        
        current_sl = position['sl']
        current_tp = position['tp']
        optimal_sl = optimal_levels['stop_loss']
        optimal_tp = optimal_levels['take_profit']
        
        recommendations = []
        actions = []
        
        # Check if SL/TP need to be set
        if current_sl == 0.0:
            recommendations.append(" CRITICAL: No Stop Loss set - High Risk!")
            actions.append({
                'action': 'SET_STOP_LOSS',
                'level': optimal_sl,
                'reason': 'Position has no stop loss protection'
            })
        
        if current_tp == 0.0:
            recommendations.append("WARNING No Take Profit set")
            actions.append({
                'action': 'SET_TAKE_PROFIT',
                'level': optimal_tp,
                'reason': 'Position has no take profit target'
            })
        
        # Check if current levels are suboptimal
        if current_sl != 0.0:
            sl_diff_pips = abs(current_sl - optimal_sl) / optimal_levels.get('pip_value', 0.0001)
            if sl_diff_pips > 5:  # More than 5 pips difference
                recommendations.append(f"TOOL Adjust Stop Loss (current: {current_sl:.5f}, optimal: {optimal_sl:.5f})")
                actions.append({
                    'action': 'MODIFY_STOP_LOSS',
                    'current': current_sl,
                    'optimal': optimal_sl,
                    'reason': f'SL optimization: {sl_diff_pips:.1f} pip improvement'
                })
        
        if current_tp != 0.0:
            tp_diff_pips = abs(current_tp - optimal_tp) / optimal_levels.get('pip_value', 0.0001)
            if tp_diff_pips > 5:  # More than 5 pips difference
                recommendations.append(f"TOOL Adjust Take Profit (current: {current_tp:.5f}, optimal: {optimal_tp:.5f})")
                actions.append({
                    'action': 'MODIFY_TAKE_PROFIT',
                    'current': current_tp,
                    'optimal': optimal_tp,
                    'reason': f'TP optimization: {tp_diff_pips:.1f} pip improvement'
                })
        
        # Check for break-even opportunity
        if pnl_pips >= 10:  # Position in profit
            if abs(current_sl - position['price_open']) > 2 * optimal_levels.get('pip_value', 0.0001):
                recommendations.append("TARGET Consider moving Stop Loss to Break Even")
                actions.append({
                    'action': 'MOVE_TO_BREAKEVEN',
                    'level': position['price_open'],
                    'reason': f'Position is {pnl_pips:.1f} pips in profit'
                })
        
        # Check for position closure if severely underwater
        if pnl_pips < -50:  # More than 50 pips loss
            recommendations.append(" Consider closing position - Severe loss")
            actions.append({
                'action': 'CLOSE_POSITION',
                'reason': f'Position is {abs(pnl_pips):.1f} pips underwater'
            })
        
        # Priority recommendation
        if not actions:
            priority = "OK HOLD - Position levels are optimal"
        elif any(action['action'] == 'SET_STOP_LOSS' for action in actions):
            priority = " SET STOP LOSS IMMEDIATELY"
        elif any(action['action'] == 'CLOSE_POSITION' for action in actions):
            priority = "ERROR CLOSE POSITION"
        elif len(actions) >= 2:
            priority = "TOOL MODIFY LEVELS"
        else:
            priority = " MONITOR"
        
        return {
            'priority': priority,
            'recommendations': recommendations,
            'actions': actions,
            'position_health': self.assess_position_health(pnl_pips, current_sl)
        }
    
    def assess_position_health(self, pnl_pips: float, current_sl: float) -> str:
        """Assess overall position health"""
        if current_sl == 0.0:
            return "CRITICAL - No Stop Loss"
        elif pnl_pips < -30:
            return "POOR - Significant Loss"
        elif pnl_pips < -10:
            return "BELOW_PAR - Minor Loss"
        elif pnl_pips < 10:
            return "NEUTRAL - Break Even"
        elif pnl_pips < 25:
            return "GOOD - Moderate Profit"
        else:
            return "EXCELLENT - Strong Profit"
    
    def execute_position_action(self, ticket: int, action: Dict) -> bool:
        """Execute the recommended action on a position"""
        try:
            action_type = action['action']
            
            if action_type == 'SET_STOP_LOSS':
                return self.modify_position(ticket, sl=action['level'])
            
            elif action_type == 'SET_TAKE_PROFIT':
                return self.modify_position(ticket, tp=action['level'])
            
            elif action_type == 'MODIFY_STOP_LOSS':
                return self.modify_position(ticket, sl=action['optimal'])
            
            elif action_type == 'MODIFY_TAKE_PROFIT':
                return self.modify_position(ticket, tp=action['optimal'])
            
            elif action_type == 'MOVE_TO_BREAKEVEN':
                return self.modify_position(ticket, sl=action['level'])
            
            elif action_type == 'CLOSE_POSITION':
                return self.close_position(ticket)
            
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing action {action_type} for ticket {ticket}: {e}")
            return False
    
    def modify_position(self, ticket: int, sl: Optional[float] = None, tp: Optional[float] = None) -> bool:
        """Modify position SL/TP levels"""
        try:
            # Get position info
            position = mt5.positions_get(ticket=ticket)
            if not position:
                logger.error(f"Position {ticket} not found")
                return False
            
            pos = position[0]
            
            # Prepare modification request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": pos.symbol,
                "position": ticket,
                "sl": sl if sl is not None else pos.sl,
                "tp": tp if tp is not None else pos.tp,
                "magic": pos.magic,
                "comment": "M5M1_BOS_Management"
            }
            
            # Send modification request
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"OK Position {ticket} modified successfully")
                if sl is not None:
                    logger.info(f"   New Stop Loss: {sl:.5f}")
                if tp is not None:
                    logger.info(f"   New Take Profit: {tp:.5f}")
                return True
            else:
                logger.error(f"ERROR Position modification failed: {result.retcode} - {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"Error modifying position {ticket}: {e}")
            return False
    
    def close_position(self, ticket: int) -> bool:
        """Close a position"""
        try:
            # Get position info
            position = mt5.positions_get(ticket=ticket)
            if not position:
                logger.error(f"Position {ticket} not found")
                return False
            
            pos = position[0]
            
            # Determine close order type
            if pos.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(pos.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(pos.symbol).ask
            
            # Prepare close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": pos.magic,
                "comment": "M5M1_BOS_Close"
            }
            
            # Send close request
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"OK Position {ticket} closed successfully at {price:.5f}")
                return True
            else:
                logger.error(f"ERROR Position close failed: {result.retcode} - {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"Error closing position {ticket}: {e}")
            return False
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """Get current bid/ask prices for symbol"""
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None
            
            return {
                'bid': tick.bid,
                'ask': tick.ask,
                'spread': tick.ask - tick.bid,
                'time': tick.time
            }
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def generate_position_report(self, analyses: List[Dict]) -> str:
        """Generate comprehensive position management report"""
        report = []
        report.append("="*80)
        report.append(" MIKROBOT M5/M1 BOS POSITION MANAGEMENT REPORT")
        report.append("="*80)
        report.append(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Account: {self.account_number}")
        report.append(f"Total Positions: {len(analyses)}")
        report.append("")
        
        # Summary statistics
        total_pnl = sum(analysis['current_pnl_usd'] for analysis in analyses)
        positions_in_profit = sum(1 for analysis in analyses if analysis['current_pnl_pips'] > 0)
        positions_in_loss = sum(1 for analysis in analyses if analysis['current_pnl_pips'] < 0)
        positions_no_sl = sum(1 for analysis in analyses if analysis['current_sl'] == 0.0)
        
        report.append("CHART POSITION SUMMARY:")
        report.append(f"   Total P&L: ${total_pnl:.2f}")
        report.append(f"   Positions in Profit: {positions_in_profit}")
        report.append(f"   Positions in Loss: {positions_in_loss}")
        report.append(f"   Positions without SL: {positions_no_sl} {'' if positions_no_sl > 0 else 'OK'}")
        report.append("")
        
        # Individual position analysis
        for i, analysis in enumerate(analyses, 1):
            report.append(f"GRAPH_UP POSITION #{i} - Ticket: {analysis['ticket']}")
            report.append(f"   Symbol: {analysis['symbol']} | Direction: {analysis['direction']}")
            report.append(f"   Entry: {analysis['entry_price']:.5f}")
            report.append(f"   Current: {analysis['current_price']['bid']:.5f} / {analysis['current_price']['ask']:.5f}")
            report.append(f"   P&L: {analysis['current_pnl_pips']:.1f} pips (${analysis['current_pnl_usd']:.2f})")
            report.append(f"   Health: {analysis['recommendation']['position_health']}")
            report.append("")
            
            # Current levels
            report.append("    CURRENT LEVELS:")
            report.append(f"      Stop Loss: {analysis['current_sl']:.5f if analysis['current_sl'] != 0 else 'NOT SET ERROR'}")
            report.append(f"      Take Profit: {analysis['current_tp']:.5f if analysis['current_tp'] != 0 else 'NOT SET WARNING'}")
            report.append("")
            
            # Optimal levels
            optimal = analysis['optimal_levels']
            report.append("   TARGET OPTIMAL LEVELS (M5/M1 BOS):")
            report.append(f"      Stop Loss: {optimal['stop_loss']:.5f} ({optimal['sl_distance_pips']:.1f} pips)")
            report.append(f"      Take Profit: {optimal['take_profit']:.5f} ({optimal['tp_distance_pips']:.1f} pips)")
            report.append(f"      Risk/Reward: 1:{optimal['risk_reward_ratio']}")
            report.append("")
            
            # Recommendations
            rec = analysis['recommendation']
            report.append(f"    PRIORITY: {rec['priority']}")
            if rec['recommendations']:
                report.append("    RECOMMENDATIONS:")
                for recommendation in rec['recommendations']:
                    report.append(f"       {recommendation}")
            
            if rec['actions']:
                report.append("   FAST SUGGESTED ACTIONS:")
                for action in rec['actions']:
                    report.append(f"       {action['action']}: {action['reason']}")
            
            report.append("")
            report.append("-" * 60)
            report.append("")
        
        return "\n".join(report)

def main():
    """Main execution function"""
    logger.info("ROCKET Starting M5/M1 BOS Position Management")
    
    # Initialize position manager
    manager = M5M1PositionManager()
    
    # Connect to MT5
    if not manager.connect_mt5():
        logger.error("ERROR Failed to connect to MT5")
        return
    
    try:
        # Get current positions
        positions = manager.get_current_positions()
        
        if not positions:
            logger.info("OK No positions to manage")
            return
        
        # Analyze each position
        analyses = []
        for position in positions:
            logger.info(f" Analyzing position {position['ticket']} ({position['symbol']})")
            analysis = manager.analyze_position_levels(position)
            
            if 'error' not in analysis:
                analyses.append(analysis)
            else:
                logger.error(f"ERROR Failed to analyze position {position['ticket']}: {analysis['error']}")
        
        # Generate and display report
        if analyses:
            report = manager.generate_position_report(analyses)
            print(report)
            
            # Ask user for action
            print("\n" + "="*80)
            print(" POSITION MANAGEMENT OPTIONS:")
            print("1. Apply all recommended modifications automatically")
            print("2. Apply modifications manually (one by one)")
            print("3. Export report only (no modifications)")
            print("4. Exit without changes")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                # Apply all modifications automatically
                logger.info(" Applying all recommended modifications...")
                for analysis in analyses:
                    for action in analysis['recommendation']['actions']:
                        if action['action'] != 'CLOSE_POSITION':  # Don't auto-close
                            success = manager.execute_position_action(analysis['ticket'], action)
                            if success:
                                logger.info(f"OK {action['action']} applied to ticket {analysis['ticket']}")
                            else:
                                logger.error(f"ERROR Failed to apply {action['action']} to ticket {analysis['ticket']}")
                        else:
                            logger.info(f"WARNING Skipping auto-close for ticket {analysis['ticket']} - manual review required")
            
            elif choice == "2":
                # Apply modifications manually
                for analysis in analyses:
                    print(f"\nGRAPH_UP Position {analysis['ticket']} ({analysis['symbol']}):")
                    print(f"Priority: {analysis['recommendation']['priority']}")
                    
                    for i, action in enumerate(analysis['recommendation']['actions'], 1):
                        print(f"\n{i}. {action['action']}: {action['reason']}")
                        apply = input(f"Apply this action? (y/n): ").strip().lower()
                        
                        if apply == 'y':
                            success = manager.execute_position_action(analysis['ticket'], action)
                            if success:
                                print(f"OK {action['action']} applied successfully")
                            else:
                                print(f"ERROR Failed to apply {action['action']}")
                        else:
                            print(" Skipped")
            
            elif choice == "3":
                # Export report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = f"position_report_{timestamp}.txt"
                with open(report_file, 'w', encoding='ascii', errors='ignore') as f:
                    f.write(report)
                logger.info(f" Report exported to {report_file}")
            
            else:
                logger.info(" Exiting without changes")
        
    except Exception as e:
        logger.error(f"ERROR Error during position management: {e}")
    
    finally:
        # Cleanup
        mt5.shutdown()
        logger.info(" MT5 connection closed")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()