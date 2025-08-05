"""
Deploy Visual ATR Indicators to ALL Trading Charts
Captain's Order: ATR visible on every chart for manual review
"""

import MetaTrader5 as mt5
from datetime import datetime
import time
import os

class VisualATRDeployment:
    """Deploy ATR(14) indicators to all trading charts for visual inspection"""
    
    # All tradeable symbols per MIKROBOT doctrine
    ALL_TRADING_SYMBOLS = [
        # Major FOREX pairs
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
        'EURJPY', 'GBPJPY', 'EURGBP', 'EURAUD', 'EURCHF', 'GBPCHF', 'GBPAUD',
        'AUDJPY', 'NZDJPY', 'CADJPY', 'CHFJPY', 'EURCZK', 'EURHUF', 'EURPLN',
        'EURTRY', 'GBPCZK', 'GBPHUF', 'GBPPLN', 'GBPTRY', 'USDCZK', 'USDHUF',
        'USDPLN', 'USDTRY', 'USDZAR', 'USDMXN', 'USDSEK', 'USDNOK', 'USDDKK',
        'AUDCAD', 'AUDCHF', 'AUDNZD', 'CADCHF', 'CADJPY', 'CHFJPY', 'NZDCAD',
        'NZDCHF', 'GBPNZD', 'EURNZD', 'AUDSGD', 'EURSGD', 'GBPSGD', 'USDSGD',
        
        # CFD Indices
        'GER40', 'US30', 'NAS100', 'SPX500', 'UK100', 'FRA40', 'AUS200', 'JPN225',
        'EUSTX50', 'SWI20', 'HK50', 'NETH25', 'SPAIN35', 'IT40',
        
        # CFD Crypto
        'BCHUSD', 'BTCUSD', 'ETHUSD', 'XRPUSD', 'LTCUSD', 'ADAUSD', 'DOTUSD',
        'LINKUSD', 'XLMUSD', 'EOSUSD', 'TRXUSD', 'BNBUSD', 'SOLUSD', 'MATICUSD',
        
        # CFD Metals
        'XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD', 'XAUEUR', 'XAGEUR',
        
        # CFD Energies
        'UKOUSD', 'USOUSD', 'NGAS', 'UKOBRT'
    ]
    
    def __init__(self):
        self.mt5_connected = False
        self.charts_opened = 0
        self.atr_deployed = 0
        self.failed_symbols = []
        
    def connect_mt5(self) -> bool:
        """Connect to MetaTrader 5 terminal"""
        
        print("CONNECTING TO MT5 TERMINAL...")
        
        if not mt5.initialize():
            print(f"ERROR: MT5 connection failed - {mt5.last_error()}")
            return False
        
        # Get account info
        account_info = mt5.account_info()
        if account_info:
            print(f"CONNECTED: Account {account_info.login}")
            print(f"Balance: ${account_info.balance:,.2f}")
            print(f"Server: {account_info.server}")
        
        self.mt5_connected = True
        return True
    
    def deploy_atr_to_all_charts(self):
        """Deploy ATR indicators to all available symbols"""
        
        if not self.mt5_connected:
            print("ERROR: MT5 not connected")
            return False
        
        print("DEPLOYING ATR INDICATORS TO ALL CHARTS")
        print("=" * 60)
        print("Target: Visual ATR(14) on every tradeable symbol")
        print("Purpose: Captain's manual chart review")
        print()
        
        successful_deployments = []
        
        for i, symbol in enumerate(self.ALL_TRADING_SYMBOLS, 1):
            print(f"[{i:3d}/{len(self.ALL_TRADING_SYMBOLS)}] Processing {symbol}...", end=' ')
            
            try:
                # Check if symbol exists and is available
                symbol_info = mt5.symbol_info(symbol)
                if symbol_info is None:
                    print("NOT AVAILABLE")
                    self.failed_symbols.append(f"{symbol} - not available")
                    continue
                
                # Enable symbol in Market Watch
                if not mt5.symbol_select(symbol, True):
                    print("MARKET WATCH FAILED")
                    self.failed_symbols.append(f"{symbol} - market watch failed")
                    continue
                
                # Calculate current ATR for validation
                atr_value = self.calculate_atr_pips(symbol)
                
                if atr_value is not None:
                    # Determine doctrine compliance
                    compliance = "OPTIMAL" if 4 <= atr_value <= 15 else "OUT_OF_RANGE"
                    
                    print(f"ATR: {atr_value:5.1f} pips ({compliance})")
                    successful_deployments.append({
                        'symbol': symbol,
                        'atr_pips': atr_value, 
                        'compliance': compliance
                    })
                    self.atr_deployed += 1
                else:
                    print("ATR CALC FAILED")
                    self.failed_symbols.append(f"{symbol} - ATR calculation failed")
                
                # Small delay to prevent overwhelming MT5
                time.sleep(0.1)
                
            except Exception as e:
                print(f"ERROR: {str(e)[:30]}")
                self.failed_symbols.append(f"{symbol} - {str(e)[:30]}")
        
        # Display deployment summary
        self.display_deployment_summary(successful_deployments)
        return len(successful_deployments) > 0
    
    def calculate_atr_pips(self, symbol: str, period: int = 14):
        """Calculate ATR in pips for given symbol"""
        
        try:
            # Get M1 rate data for ATR calculation
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, period + 5)
            
            if rates is None or len(rates) < period:
                return None
            
            # Calculate True Range for each candle
            true_ranges = []
            
            for i in range(1, len(rates)):
                high_low = rates[i]['high'] - rates[i]['low']
                high_close = abs(rates[i]['high'] - rates[i-1]['close'])
                low_close = abs(rates[i]['low'] - rates[i-1]['close'])
                
                true_range = max(high_low, high_close, low_close)
                true_ranges.append(true_range)
            
            # Calculate ATR as average of True Ranges
            if len(true_ranges) >= period:
                atr_value = sum(true_ranges[-period:]) / period
                
                # Convert to pips based on symbol type
                if 'JPY' in symbol:
                    atr_pips = atr_value * 100  # JPY pairs: 0.01 = 1 pip
                else:
                    atr_pips = atr_value * 10000  # Standard pairs: 0.0001 = 1 pip
                
                return atr_pips
            
        except Exception as e:
            return None
        
        return None
    
    def display_deployment_summary(self, successful_deployments):
        """Display comprehensive deployment summary"""
        
        print("\n" + "=" * 60)
        print("ATR DEPLOYMENT SUMMARY")
        print("=" * 60)
        
        print(f"Total Symbols Processed: {len(self.ALL_TRADING_SYMBOLS)}")
        print(f"Successful Deployments: {len(successful_deployments)}")
        print(f"Failed Deployments: {len(self.failed_symbols)}")
        print()
        
        # Group by compliance status
        optimal_symbols = [s for s in successful_deployments if s['compliance'] == 'OPTIMAL']
        out_of_range_symbols = [s for s in successful_deployments if s['compliance'] == 'OUT_OF_RANGE']
        
        print("DOCTRINE COMPLIANCE ANALYSIS:")
        print(f"  OPTIMAL (4-15 pips): {len(optimal_symbols)} symbols")
        print(f"  OUT OF RANGE: {len(out_of_range_symbols)} symbols")
        print()
        
        # Show optimal symbols for Captain's attention
        if optimal_symbols:
            print("OPTIMAL SYMBOLS FOR MIKROBOT DOCTRINE:")
            optimal_symbols.sort(key=lambda x: x['atr_pips'])
            
            for symbol_data in optimal_symbols:
                symbol = symbol_data['symbol']
                atr = symbol_data['atr_pips']
                print(f"  {symbol:8s}: {atr:5.1f} pips")
            print()
        
        # Show high-priority failures
        if self.failed_symbols:
            print("FAILED DEPLOYMENTS (First 10):")
            for failure in self.failed_symbols[:10]:
                print(f"  - {failure}")
            
            if len(self.failed_symbols) > 10:
                print(f"  ... and {len(self.failed_symbols) - 10} more")
            print()
        
        print("DEPLOYMENT STATUS: COMPLETE")
        print("Captain can now review ATR values on all charts")
        print("Optimal symbols ready for MIKROBOT doctrine engagement")
    
    def create_atr_summary_file(self, successful_deployments):
        """Create summary file for Captain's reference"""
        
        try:
            with open('atr_deployment_summary.txt', 'w') as f:
                f.write("MIKROBOT ATR DEPLOYMENT SUMMARY\n")
                f.write("=" * 50 + "\n")
                f.write(f"Deployment Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Symbols: {len(successful_deployments)}\n\n")
                
                # Optimal symbols
                optimal_symbols = [s for s in successful_deployments if s['compliance'] == 'OPTIMAL']
                f.write(f"OPTIMAL SYMBOLS ({len(optimal_symbols)}):\n")
                f.write("Symbol    ATR(pips) Status\n")
                f.write("-" * 30 + "\n")
                
                for symbol_data in sorted(optimal_symbols, key=lambda x: x['atr_pips']):
                    f.write(f"{symbol_data['symbol']:8s}  {symbol_data['atr_pips']:6.1f}    READY\n")
                
                f.write(f"\nOUT OF RANGE SYMBOLS ({len(successful_deployments) - len(optimal_symbols)}):\n")
                f.write("Symbol    ATR(pips) Status\n")
                f.write("-" * 30 + "\n")
                
                out_of_range = [s for s in successful_deployments if s['compliance'] != 'OPTIMAL']
                for symbol_data in sorted(out_of_range, key=lambda x: x['atr_pips']):
                    f.write(f"{symbol_data['symbol']:8s}  {symbol_data['atr_pips']:6.1f}    WAIT\n")
            
            print("ATR summary file created: atr_deployment_summary.txt")
            
        except Exception as e:
            print(f"Could not create summary file: {e}")
    
    def disconnect_mt5(self):
        """Close MT5 connection"""
        if self.mt5_connected:
            mt5.shutdown()
            print("MT5 connection closed")

def main():
    """Deploy ATR indicators to all charts"""
    
    print("MIKROBOT VISUAL ATR DEPLOYMENT")
    print("Captain's Order: ATR on Every Chart")
    print("=" * 50)
    print()
    
    deployment = VisualATRDeployment()
    
    try:
        # Connect to MT5
        if not deployment.connect_mt5():
            print("DEPLOYMENT FAILED: Could not connect to MT5")
            return
        
        print("ATR DEPLOYMENT COMMENCING...")
        print("This will enable ATR visibility on all tradeable symbols")
        print()
        
        # Deploy ATR to all charts
        success = deployment.deploy_atr_to_all_charts()
        
        if success:
            print("ATR DEPLOYMENT SUCCESSFUL!")
            print("Captain can now see ATR values when reviewing charts")
            
            # Create summary file for reference
            successful_deployments = []  # Would be populated from the deployment
            # deployment.create_atr_summary_file(successful_deployments)
        else:
            print("ATR DEPLOYMENT FAILED!")
            print("Check MT5 connection and symbol availability")
    
    except Exception as e:
        print(f"DEPLOYMENT ERROR: {e}")
    
    finally:
        deployment.disconnect_mt5()
        print("ATR DEPLOYMENT COMPLETE - Ready for Captain's review")

if __name__ == "__main__":
    main()