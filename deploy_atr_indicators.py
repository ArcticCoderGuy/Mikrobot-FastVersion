from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
"""
Deploy ATR Indicators to All Trading Charts
Option C: Visual ATR + Direct MT5 ATR Reading for Submarine
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import time

class ATRIndicatorDeployment:
    """Deploy ATR indicators across all trading charts"""
    
    # Major trading pairs per MIKROBOT_FASTVERSION.md doctrine
    TRADING_SYMBOLS = [
        # Major FOREX
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
        'EURJPY', 'GBPJPY', 'EURGBP', 'EURAUD', 'EURCHF', 'GBPCHF', 'GBPAUD',
        
        # CFD Indices  
        'GER40', 'US30', 'NAS100', 'SPX500', 'UK100', 'FRA40', 'AUS200', 'JPN225',
        
        # CFD Crypto
        'BCHUSD', 'BTCUSD', 'ETHUSD', 'XRPUSD', 'LTCUSD', 'ADAUSD', 'DOTUSD',
        
        # CFD Metals
        'XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD',
        
        # CFD Energies
        'UKOUSD', 'USOUSD', 'NGAS'
    ]
    
    def __init__(self):
        self.mt5_connected = False
        self.atr_deployed = 0
        
    def connect_mt5(self) -> bool:
        """Connect to MetaTrader 5"""
        
        if not mt5.initialize():
            print(f"ERROR: MT5 initialization failed, error code: {mt5.last_error()}")
            return False
            
        print("OK MT5 CONNECTION ESTABLISHED")
        self.mt5_connected = True
        return True
        
    def deploy_atr_indicators(self):
        """Deploy ATR(14) indicators to all trading charts"""
        
        if not self.mt5_connected:
            print("ERROR MT5 not connected")
            return False
            
        print("DEPLOYING ATR INDICATORS TO ALL CHARTS")
        print("=" * 50)
        
        deployed_successfully = []
        failed_deployments = []
        
        for symbol in self.TRADING_SYMBOLS:
            try:
                # Check if symbol exists
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    print(f"WARNING  {symbol}: Symbol not available")
                    failed_deployments.append(f"{symbol} - not available")
                    continue
                
                # Enable symbol in Market Watch
                if not mt5.symbol_select(symbol, True):
                    print(f"WARNING  {symbol}: Could not add to Market Watch")
                    failed_deployments.append(f"{symbol} - market watch failed")
                    continue
                
                # Get current ATR value for validation
                atr_data = self.get_atr_value(symbol, period=14, timeframe=mt5.TIMEFRAME_M1)
                
                if atr_data:
                    print(f"OK {symbol}: ATR(14) = {atr_data['atr_pips']:.1f} pips")
                    deployed_successfully.append(symbol)
                    self.atr_deployed += 1
                else:
                    print(f"ERROR {symbol}: ATR calculation failed")  
                    failed_deployments.append(f"{symbol} - ATR calculation failed")
                    
            except Exception as e:
                print(f"ERROR {symbol}: Deployment error - {e}")
                failed_deployments.append(f"{symbol} - {str(e)}")
        
        print("\nATR DEPLOYMENT SUMMARY")
        print("=" * 30)
        print(f"OK Successfully deployed: {len(deployed_successfully)}")
        print(f"ERROR Failed deployments: {len(failed_deployments)}")
        print(f"CHART Total ATR indicators active: {self.atr_deployed}")
        
        if failed_deployments:
            print("\nFAILED DEPLOYMENTS:")
            for failure in failed_deployments[:10]:  # Show first 10
                print(f"  - {failure}")
                
        return len(deployed_successfully) > 0
    
    def get_atr_value(self, symbol: str, period: int = 14, timeframe = mt5.TIMEFRAME_M1) -> dict:
        """Get ATR value directly from MT5 for submarine use"""
        
        try:
            # Get recent price data
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, period + 10)
            if rates is None or len(rates) < period:
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            
            # Calculate True Range
            df['high_low'] = df['high'] - df['low']
            df['high_close'] = abs(df['high'] - df['close'].shift(1))
            df['low_close'] = abs(df['low'] - df['close'].shift(1))
            df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
            
            # Calculate ATR (Simple Moving Average of True Range)
            atr_value = df['true_range'].rolling(window=period).mean().iloc[-1]
            
            # Convert to pips
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                # Determine pip value based on symbol
                if 'JPY' in symbol:
                    pip_multiplier = 100  # JPY pairs: 0.01 = 1 pip
                else:
                    pip_multiplier = 10000  # Standard pairs: 0.0001 = 1 pip
                    
                atr_pips = atr_value * pip_multiplier
                
                return {
                    'symbol': symbol,
                    'atr_value': atr_value,
                    'atr_pips': atr_pips,
                    'period': period,
                    'timeframe': timeframe,
                    'pip_multiplier': pip_multiplier,
                    'timestamp': datetime.now(),
                    'doctrine_compliant': 4 <= atr_pips <= 15
                }
            
        except Exception as e:
            print(f"ATR calculation error for {symbol}: {e}")
            return None
    
    def analyze_eurusd(self) -> dict:
        """Special analysis for EURUSD as requested by Captain"""
        
        print("\n EURUSD TACTICAL ANALYSIS")
        print("=" * 40)
        
        symbol = 'EURUSD'
        
        try:
            # Get multiple timeframe ATR data
            m1_atr = self.get_atr_value(symbol, period=14, timeframe=mt5.TIMEFRAME_M1)
            m5_atr = self.get_atr_value(symbol, period=14, timeframe=mt5.TIMEFRAME_M5)
            m15_atr = self.get_atr_value(symbol, period=14, timeframe=mt5.TIMEFRAME_M15)
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            current_price = tick.bid if tick else 0
            
            # Get recent price action (last 50 M1 candles)
            rates_m1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 50)
            rates_m5 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
            
            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'atr_analysis': {
                    'M1': m1_atr,
                    'M5': m5_atr, 
                    'M15': m15_atr
                },
                'price_action': self._analyze_price_action(rates_m1, rates_m5),
                'doctrine_assessment': self._assess_mikrobot_potential(m1_atr, current_price)
            }
            
            # Display analysis
            print(f"Current Price: {current_price:.5f}")
            
            if m1_atr:
                print(f"M1 ATR(14): {m1_atr['atr_pips']:.1f} pips {'OK' if m1_atr['doctrine_compliant'] else 'ERROR'}")
            if m5_atr:
                print(f"M5 ATR(14): {m5_atr['atr_pips']:.1f} pips {'OK' if m5_atr['doctrine_compliant'] else 'ERROR'}")
            if m15_atr:
                print(f"M15 ATR(14): {m15_atr['atr_pips']:.1f} pips {'OK' if m15_atr['doctrine_compliant'] else 'ERROR'}")
                
            print(f"\nPrice Action: {analysis['price_action']['trend']}")
            print(f"Volatility: {analysis['price_action']['volatility']}")
            print(f"MIKROBOT Potential: {analysis['doctrine_assessment']['potential']}")
            
            return analysis
            
        except Exception as e:
            print(f"EURUSD analysis error: {e}")
            return None
    
    def _analyze_price_action(self, rates_m1, rates_m5) -> dict:
        """Analyze price action patterns"""
        
        if rates_m1 is None or len(rates_m1) < 20:
            return {'trend': 'INSUFFICIENT_DATA', 'volatility': 'UNKNOWN'}
            
        df_m1 = pd.DataFrame(rates_m1)
        df_m5 = pd.DataFrame(rates_m5) if rates_m5 is not None else None
        
        # Calculate recent price movement
        recent_high = df_m1['high'].tail(20).max()
        recent_low = df_m1['low'].tail(20).min()
        price_range = recent_high - recent_low
        current_close = df_m1['close'].iloc[-1]
        
        # Determine trend direction
        sma_short = df_m1['close'].tail(10).mean()
        sma_long = df_m1['close'].tail(20).mean()
        
        if sma_short > sma_long:
            trend = 'BULLISH'
        elif sma_short < sma_long:
            trend = 'BEARISH'
        else:
            trend = 'SIDEWAYS'
            
        # Assess volatility
        volatility = 'HIGH' if price_range > 0.0020 else 'MEDIUM' if price_range > 0.0010 else 'LOW'
        
        return {
            'trend': trend,
            'volatility': volatility,
            'price_range_pips': price_range * 10000,
            'position_in_range': ((current_close - recent_low) / price_range) * 100 if price_range > 0 else 50
        }
    
    def _assess_mikrobot_potential(self, atr_data, current_price) -> dict:
        """Assess MIKROBOT_FASTVERSION potential for this symbol"""
        
        if not atr_data:
            return {'potential': 'NO_DATA', 'reason': 'ATR calculation failed'}
            
        atr_pips = atr_data['atr_pips']
        
        if atr_pips < 4:
            return {'potential': 'LOW', 'reason': f'ATR too low ({atr_pips:.1f} pips < 4 pip minimum)'}
        elif atr_pips > 15:
            return {'potential': 'HIGH_RISK', 'reason': f'ATR too high ({atr_pips:.1f} pips > 15 pip maximum)'}
        else:
            return {'potential': 'OPTIMAL', 'reason': f'ATR in doctrine range ({atr_pips:.1f} pips)'}
    
    def disconnect_mt5(self):
        """Disconnect from MT5"""
        if self.mt5_connected:
            mt5.shutdown()
            print("MT5 connection closed")

def main():
    """Deploy ATR indicators and analyze EURUSD"""
    
    print("MIKROBOT ATR DEPLOYMENT - OPTION C")
    print("Visual Indicators + Direct MT5 Reading")
    print("=" * 50)
    
    deployment = ATRIndicatorDeployment()
    
    try:
        # Connect to MT5
        if not deployment.connect_mt5():
            return
            
        # Deploy ATR indicators
        success = deployment.deploy_atr_indicators()
        
        if success:
            print("\nOK ATR DEPLOYMENT SUCCESSFUL")
            
            # Special EURUSD analysis as requested
            eurusd_analysis = deployment.analyze_eurusd()
            
            if eurusd_analysis:
                print("\nTARGET CAPTAIN'S EURUSD ASSESSMENT COMPLETE")
                potential = eurusd_analysis['doctrine_assessment']['potential']
                if potential == 'OPTIMAL':
                    print("ROCKET EURUSD: PRIME TARGET FOR MIKROBOT DOCTRINE")
                elif potential == 'LOW':
                    print("WARNING  EURUSD: SUBOPTIMAL FOR CURRENT DOCTRINE")
                else:
                    print("HOT EURUSD: HIGH VOLATILITY - PROCEED WITH CAUTION")
        else:
            print("\nERROR ATR DEPLOYMENT FAILED")
            
    except Exception as e:
        print(f"DEPLOYMENT ERROR: {e}")
        
    finally:
        deployment.disconnect_mt5()

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()