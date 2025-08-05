from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
MIKROBOT ML REAL-TIME TERMINAL
VS Code Terminal Integration - See M5 BOS & M1 Break-and-Retest Live
Session #2: ML-Enhanced Core with Real-time MT5 Toolbox Integration
"""

import asyncio
import json
import time
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
from colorama import init, Fore, Back, Style
import os
import sys

# Initialize colorama for Windows terminal colors
init(autoreset=True)

class MLRealTimeTerminal:
    """
    ML-Enhanced Real-time Terminal for MIKROBOT trading
    Displays live M5 BOS & M1 Break-and-Retest with ML analysis
    """
    
    def __init__(self):
        self.signal_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_4phase_signal.json")
        self.response_file = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/Common/Files/mikrobot_submarine_response.json") 
        
        self.mt5_connected = False
        self.last_signal = None
        self.trade_count = 0
        self.session_start = datetime.now()
        
        # ML Feature tracking
        self.feature_history = []
        self.pattern_confidence = 0.0
        self.ml_predictions = []
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print terminal header with ML status"""
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*80}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}ROCKET MIKROBOT ML REAL-TIME TERMINAL - SESSION #2")
        print(f"{Fore.GREEN}ML-Enhanced Core | Live MT5 Tykalupakki Integration")
        print(f"{Fore.CYAN}{'='*80}")
        print(f"{Fore.WHITE}Session Start: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Trade Count: {Fore.GREEN}{self.trade_count}")
        print(f"ML Pattern Confidence: {Fore.YELLOW}{self.pattern_confidence:.1%}")
        print(f"MT5 Connection: {Fore.GREEN if self.mt5_connected else Fore.RED}{'CONNECTED' if self.mt5_connected else 'DISCONNECTED'}")
        print(f"{Fore.CYAN}{'-'*80}")
    
    async def connect_mt5(self):
        """Connect to MT5 for live data"""
        if mt5.initialize():
            self.mt5_connected = True
            account_info = mt5.account_info()
            print(f"{Fore.GREEN}OK MT5 CONNECTED: Account {account_info.login}")
            print(f"   Balance: EUR{account_info.balance:,.2f}")
            print(f"   Server: {account_info.server}")
        else:
            print(f"{Fore.RED}ERROR MT5 CONNECTION FAILED")
    
    async def analyze_signal_with_ml(self, signal_data):
        """ML Analysis of trading signal"""
        
        symbol = signal_data.get('symbol', 'UNKNOWN')
        trade_direction = signal_data.get('trade_direction', 'UNKNOWN')
        
        # Extract phases for ML feature engineering
        phase_1 = signal_data.get('phase_1_m5_bos', {})
        phase_2 = signal_data.get('phase_2_m1_break', {})
        phase_3 = signal_data.get('phase_3_m1_retest', {})
        phase_4 = signal_data.get('phase_4_ylipip', {})
        
        # ML FEATURE EXTRACTION
        features = {
            'symbol': symbol,
            'direction': trade_direction,
            'timestamp': signal_data.get('timestamp'),
            
            # Price action features
            'm5_bos_price': phase_1.get('price', 0),
            'm1_break_price': phase_2.get('price', 0), 
            'm1_retest_price': phase_3.get('price', 0),
            'current_price': signal_data.get('current_price', 0),
            'ylipip_target': phase_4.get('target', 0),
            'ylipip_current': phase_4.get('current', 0),
            'ylipip_triggered': phase_4.get('triggered', False),
            
            # Calculated ML features
            'price_momentum': 0,
            'retest_quality': 0,
            'volatility_score': 0,
            'pattern_strength': 0
        }
        
        # Calculate ML features
        if features['m5_bos_price'] and features['current_price']:
            features['price_momentum'] = abs(features['current_price'] - features['m5_bos_price'])
            
            # Retest quality (how close retest came to break level)
            if features['m1_break_price'] and features['m1_retest_price']:
                retest_distance = abs(features['m1_retest_price'] - features['m1_break_price'])
                features['retest_quality'] = 1.0 / (1.0 + retest_distance * 10000)  # Normalize
            
            # Pattern strength based on price progression
            prices = [features['m5_bos_price'], features['m1_break_price'], 
                     features['m1_retest_price'], features['current_price']]
            if all(prices):
                price_range = max(prices) - min(prices)
                features['volatility_score'] = price_range * 10000  # Convert to pips
                
                # Pattern strength (0-1 score)
                if trade_direction == 'BULL':
                    features['pattern_strength'] = min(1.0, (features['current_price'] - min(prices)) / price_range) if price_range > 0 else 0
                else:
                    features['pattern_strength'] = min(1.0, (max(prices) - features['current_price']) / price_range) if price_range > 0 else 0
        
        # ML PREDICTION (simplified model)
        confidence_factors = [
            features['retest_quality'] * 0.3,
            min(1.0, features['volatility_score'] / 50) * 0.2,  # Optimal volatility around 50 pips
            features['pattern_strength'] * 0.3,
            (1.0 if features['ylipip_triggered'] else 0.0) * 0.2
        ]
        
        self.pattern_confidence = sum(confidence_factors)
        
        # Store for ML learning
        self.feature_history.append(features)
        if len(self.feature_history) > 100:  # Keep last 100 patterns
            self.feature_history.pop(0)
        
        return features
    
    def display_signal_analysis(self, signal_data, ml_features):
        """Display detailed signal analysis with ML insights"""
        
        symbol = signal_data.get('symbol', 'UNKNOWN')
        direction = signal_data.get('trade_direction', 'UNKNOWN')
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}CHART LIVE SIGNAL ANALYSIS - ML ENHANCED")
        print(f"{Fore.CYAN}{'-'*50}")
        
        # Basic signal info
        print(f"{Fore.WHITE}Symbol: {Fore.YELLOW}{symbol}")
        print(f"{Fore.WHITE}Direction: {Fore.GREEN if direction == 'BULL' else Fore.RED}{direction}")
        print(f"{Fore.WHITE}Timestamp: {Fore.WHITE}{signal_data.get('timestamp')}")
        
        # 4-Phase breakdown with ML analysis
        print(f"\n{Fore.MAGENTA}TARGET MIKROBOT 4-PHASE ANALYSIS:")
        
        phase_1 = signal_data.get('phase_1_m5_bos', {})
        phase_2 = signal_data.get('phase_2_m1_break', {})
        phase_3 = signal_data.get('phase_3_m1_retest', {})
        phase_4 = signal_data.get('phase_4_ylipip', {})
        
        print(f"{Fore.BLUE}Phase 1 - M5 BOS:")
        print(f"  Time: {phase_1.get('time', 'N/A')}")
        print(f"  Price: {phase_1.get('price', 'N/A')}")
        print(f"  Direction: {phase_1.get('direction', 'N/A')}")
        
        print(f"{Fore.BLUE}Phase 2 - M1 Break:")
        print(f"  Time: {phase_2.get('time', 'N/A')}")
        print(f"  Price: {phase_2.get('price', 'N/A')}")
        
        print(f"{Fore.BLUE}Phase 3 - M1 Retest:")
        print(f"  Time: {phase_3.get('time', 'N/A')}")
        print(f"  Price: {phase_3.get('price', 'N/A')}")
        print(f"  ML Retest Quality: {Fore.YELLOW}{ml_features['retest_quality']:.3f}")
        
        print(f"{Fore.BLUE}Phase 4 - Ylipip:")
        print(f"  Target: {phase_4.get('target', 'N/A')}")
        print(f"  Current: {phase_4.get('current', 'N/A')}")
        print(f"  Triggered: {Fore.GREEN if phase_4.get('triggered') else Fore.RED}{phase_4.get('triggered', False)}")
        
        # ML INSIGHTS
        print(f"\n{Fore.GREEN}{Style.BRIGHT} ML ANALYSIS:")
        print(f"{Fore.WHITE}Pattern Confidence: {Fore.YELLOW}{self.pattern_confidence:.1%}")
        print(f"{Fore.WHITE}Price Momentum: {Fore.CYAN}{ml_features['price_momentum']:.5f}")
        print(f"{Fore.WHITE}Volatility Score: {Fore.CYAN}{ml_features['volatility_score']:.1f} pips")
        print(f"{Fore.WHITE}Pattern Strength: {Fore.CYAN}{ml_features['pattern_strength']:.3f}")
        
        # Trading recommendation
        if phase_4.get('triggered', False) and self.pattern_confidence > 0.7:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}OK ML RECOMMENDATION: EXECUTE TRADE")
            print(f"{Fore.GREEN}High confidence pattern detected!")
        elif phase_4.get('triggered', False):
            print(f"\n{Fore.YELLOW}{Style.BRIGHT}WARNING ML RECOMMENDATION: CAUTION")
            print(f"{Fore.YELLOW}Ylipip triggered but pattern confidence moderate")
        else:
            print(f"\n{Fore.BLUE}{Style.BRIGHT} ML RECOMMENDATION: MONITOR")
            print(f"{Fore.BLUE}Pattern developing, waiting for ylipip trigger")
    
    def display_mt5_toolbox_status(self):
        """Display MT5 Toolbox equivalent information"""
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT} MT5 TYKALUPAKKI STATUS:")
        print(f"{Fore.CYAN}{'-'*50}")
        
        if self.mt5_connected:
            # Account info
            account_info = mt5.account_info()
            if account_info:
                print(f"{Fore.WHITE}Account: {account_info.login}")
                print(f"Balance: EUR{account_info.balance:,.2f}")
                print(f"Equity: EUR{account_info.equity:,.2f}")
                print(f"Free Margin: EUR{account_info.margin_free:,.2f}")
            
            # Positions (Trade tab equivalent)
            positions = mt5.positions_get()
            print(f"\n{Fore.YELLOW}GRAPH_UP OPEN POSITIONS: {len(positions) if positions else 0}")
            
            if positions:
                for pos in positions:
                    color = Fore.GREEN if pos.profit > 0 else Fore.RED
                    print(f"  {pos.symbol} {pos.type_str} {pos.volume} lots")
                    print(f"  Profit: {color}EUR{pos.profit:.2f}")
            else:
                print(f"  {Fore.BLUE}No open positions")
            
            # Orders (pending orders)
            orders = mt5.orders_get()
            print(f"\n{Fore.YELLOW} PENDING ORDERS: {len(orders) if orders else 0}")
            
        else:
            print(f"{Fore.RED}ERROR MT5 not connected - cannot display toolbox status")
    
    async def run_ml_terminal(self):
        """Main ML terminal loop"""
        
        await self.connect_mt5()
        
        print(f"\n{Fore.GREEN}ROCKET ML REAL-TIME TERMINAL STARTED")
        print(f"{Fore.BLUE}Monitoring: {self.signal_file}")
        print(f"{Fore.BLUE}Press Ctrl+C to stop")
        print(f"{Fore.CYAN}{'-'*80}")
        
        last_signal_content = None
        
        while True:
            try:
                # Clear screen and show header
                if os.name == 'nt':  # Windows
                    os.system('cls')
                
                self.print_header()
                self.display_mt5_toolbox_status()
                
                # Check for new signals
                if self.signal_file.exists():
                    with open(self.signal_file, 'r', encoding='utf-16') as f:
                        signal_content = f.read()
                    
                    if signal_content != last_signal_content and signal_content.strip():
                        try:
                            signal_data = json.loads(signal_content)
                            
                            # ML Analysis of signal
                            ml_features = await self.analyze_signal_with_ml(signal_data)
                            
                            # Display analysis
                            self.display_signal_analysis(signal_data, ml_features)
                            
                            # Auto-execute if conditions met
                            if (signal_data.get('phase_4_ylipip', {}).get('triggered', False) and 
                                self.pattern_confidence > 0.7):
                                
                                print(f"\n{Fore.GREEN}{Style.BRIGHT}ROCKET AUTO-EXECUTING TRADE...")
                                await self.auto_execute_trade(signal_data)
                                self.trade_count += 1
                            
                            last_signal_content = signal_content
                            self.last_signal = signal_data
                            
                        except json.JSONDecodeError:
                            print(f"{Fore.RED}WARNING Signal file being updated...")
                
                else:
                    print(f"\n{Fore.YELLOW} Waiting for signals...")
                
                # Update every 2 seconds for smooth real-time experience
                await asyncio.sleep(2)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW} ML Terminal stopped by user")
                break
            except Exception as e:
                print(f"\n{Fore.RED}ERROR Error: {e}")
                await asyncio.sleep(5)
        
        if self.mt5_connected:
            mt5.shutdown()
    
    async def auto_execute_trade(self, signal_data):
        """Auto-execute trade with ML validation"""
        
        from submarine_command_center import SubmarineCommandCenter
        
        try:
            submarine = SubmarineCommandCenter()
            
            # Validate with submarine
            if submarine._validate_mikrobot_doctrine(signal_data):
                atr_result = submarine._validate_atr_range(signal_data)
                
                risk_calc = submarine.risk_reactor.calculate_submarine_risk(
                    signal_data.get('symbol'), atr_result['atr_pips'], 100000, 0.55
                )
                
                response = await submarine._generate_doctrine_compliant_response(
                    signal_data, risk_calc, atr_result
                )
                
                # Write response file
                with open(self.response_file, 'w', encoding='ascii', errors='ignore') as f:
                    json.dump(response, f, indent=2)
                
                print(f"{Fore.GREEN}OK TRADE EXECUTED: {response['symbol']} {response['direction']}")
                print(f"   Lot Size: {response['lot_size']}")
                print(f"   Entry: {response['entry_price']}")
                print(f"   ML Confidence: {self.pattern_confidence:.1%}")
                
        except Exception as e:
            print(f"{Fore.RED}ERROR Auto-execution failed: {e}")

async def main():
    """Start ML Real-time Terminal"""
    
    terminal = MLRealTimeTerminal()
    
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("")
    print("                      ROCKET MIKROBOT ML REAL-TIME TERMINAL                      ")
    print("                    SESSION #2: ML-Enhanced Core Integration                 ")
    print("                                                                              ")
    print("  CHART Live M5 BOS & M1 Break-and-Retest Analysis                             ")
    print("   ML Pattern Recognition & Confidence Scoring                            ")
    print("   Real-time MT5 Tykalupakki Integration                                 ")
    print("  FAST Automatic Trade Execution with ML Validation                           ")
    print("")
    print()
    
    await terminal.run_ml_terminal()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    asyncio.run(main())