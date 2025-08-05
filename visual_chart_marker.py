"""
VISUAL CHART MARKING SYSTEM
Marks charts with HH/HL/LH/LL labels like in Live Market Example
Creates visual validation of M5 BOS patterns
"""
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime, timedelta
import numpy as np

class ChartMarker:
    """Visual chart marking system for pattern validation"""
    
    def __init__(self):
        self.colors = {
            'HH': 'green',
            'HL': 'lightgreen', 
            'LH': 'red',
            'LL': 'darkred',
            'BOS': 'blue',
            'RETEST': 'orange'
        }
        
    def identify_swing_points(self, rates, lookback=5):
        """Identify swing points for HH/HL/LH/LL marking"""
        highs = np.array([r.high for r in rates])
        lows = np.array([r.low for r in rates])
        times = np.array([datetime.fromtimestamp(r.time) for r in rates])
        
        swing_highs = []
        swing_lows = []
        
        # Find swing highs and lows
        for i in range(lookback, len(rates) - lookback):
            # Swing high: higher than surrounding candles
            if highs[i] == max(highs[i-lookback:i+lookback+1]):
                swing_highs.append({
                    'index': i,
                    'price': highs[i],
                    'time': times[i],
                    'type': None
                })
                
            # Swing low: lower than surrounding candles  
            if lows[i] == min(lows[i-lookback:i+lookback+1]):
                swing_lows.append({
                    'index': i,
                    'price': lows[i], 
                    'time': times[i],
                    'type': None
                })
        
        # Classify swing points
        for i in range(1, len(swing_highs)):
            if swing_highs[i]['price'] > swing_highs[i-1]['price']:
                swing_highs[i]['type'] = 'HH'
            else:
                swing_highs[i]['type'] = 'LH'
                
        for i in range(1, len(swing_lows)):
            if swing_lows[i]['price'] > swing_lows[i-1]['price']:
                swing_lows[i]['type'] = 'HL'
            else:
                swing_lows[i]['type'] = 'LL'
        
        return swing_highs[1:], swing_lows[1:]  # Skip first unmarked ones
        
    def create_marked_chart(self, symbol, timeframe=mt5.TIMEFRAME_M5, bars=100):
        """Create chart with HH/HL/LH/LL markings like Live Market Example"""
        # Get data
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        if rates is None:
            print(f"Failed to get rates for {symbol}")
            return None
            
        # Convert to arrays
        times = [datetime.fromtimestamp(r.time) for r in rates]
        opens = [r.open for r in rates]
        highs = [r.high for r in rates]
        lows = [r.low for r in rates]
        closes = [r.close for r in rates]
        
        # Identify swing points
        swing_highs, swing_lows = self.identify_swing_points(rates)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(15, 8))
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        # Plot candlesticks
        for i in range(len(rates)):
            color = 'lime' if closes[i] >= opens[i] else 'red'
            
            # Draw candle body
            body_height = abs(closes[i] - opens[i])
            body_bottom = min(opens[i], closes[i])
            
            rect = patches.Rectangle(
                (i - 0.3, body_bottom), 0.6, body_height,
                linewidth=1, edgecolor=color, facecolor=color, alpha=0.8
            )
            ax.add_patch(rect)
            
            # Draw wicks
            ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1)
            
        # Mark swing highs with labels
        for swing in swing_highs:
            if swing['type']:
                ax.plot(swing['index'], swing['price'], 'o', 
                       color=self.colors[swing['type']], markersize=8)
                ax.text(swing['index'], swing['price'] + (max(highs) - min(lows)) * 0.01,
                       swing['type'], color=self.colors[swing['type']], 
                       fontweight='bold', ha='center', fontsize=10)
                       
        # Mark swing lows with labels
        for swing in swing_lows:
            if swing['type']:
                ax.plot(swing['index'], swing['price'], 's',
                       color=self.colors[swing['type']], markersize=8)
                ax.text(swing['index'], swing['price'] - (max(highs) - min(lows)) * 0.02,
                       swing['type'], color=self.colors[swing['type']],
                       fontweight='bold', ha='center', fontsize=10)
                       
        # Draw structure lines (like in your example)
        if len(swing_highs) >= 2:
            for i in range(len(swing_highs) - 1):
                ax.plot([swing_highs[i]['index'], swing_highs[i+1]['index']],
                       [swing_highs[i]['price'], swing_highs[i+1]['price']],
                       '--', color='white', alpha=0.7, linewidth=1)
                       
        if len(swing_lows) >= 2:
            for i in range(len(swing_lows) - 1):
                ax.plot([swing_lows[i]['index'], swing_lows[i+1]['index']],
                       [swing_lows[i]['price'], swing_lows[i+1]['price']],
                       '--', color='white', alpha=0.7, linewidth=1)
        
        # Styling
        ax.set_title(f'{symbol} - Market Structure Analysis', 
                    color='white', fontsize=16, fontweight='bold')
        ax.set_xlabel('Time', color='white')
        ax.set_ylabel('Price', color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', 
                      markersize=8, label='HH (Higher High)'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightgreen',
                      markersize=8, label='HL (Higher Low)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red',
                      markersize=8, label='LH (Lower High)'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='darkred',
                      markersize=8, label='LL (Lower Low)')
        ]
        ax.legend(handles=legend_elements, loc='upper left', 
                 facecolor='black', edgecolor='white', labelcolor='white')
        
        plt.tight_layout()
        
        # Save chart
        chart_file = f"{symbol}_marked_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_file, facecolor='black', dpi=300)
        print(f"Marked chart saved: {chart_file}")
        
        # Display structure analysis
        self.analyze_structure(swing_highs, swing_lows, symbol)
        
        return fig
        
    def analyze_structure(self, swing_highs, swing_lows, symbol):
        """Analyze market structure like in your methodology"""
        print(f"\n{symbol} MARKET STRUCTURE ANALYSIS")
        print("=" * 50)
        
        # Analyze trend
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            recent_highs = [sh['type'] for sh in swing_highs[-2:]]
            recent_lows = [sl['type'] for sl in swing_lows[-2:]]
            
            print(f"Recent Highs: {' -> '.join(recent_highs)}")
            print(f"Recent Lows: {' -> '.join(recent_lows)}")
            
            # Determine trend
            if 'HH' in recent_highs and 'HL' in recent_lows:
                trend = "UPTREND"
                bos_watch = "Watch for break below last HL"
            elif 'LH' in recent_highs and 'LL' in recent_lows:
                trend = "DOWNTREND" 
                bos_watch = "Watch for break above last LH"
            else:
                trend = "TRANSITION/CONSOLIDATION"
                bos_watch = "Watch for clear structure break"
                
            print(f"Current Trend: {trend}")
            print(f"BOS Signal: {bos_watch}")
            
            # BOS levels
            if swing_lows:
                last_low = swing_lows[-1]['price']
                print(f"Key Support: {last_low:.5f}")
                
            if swing_highs:
                last_high = swing_highs[-1]['price']
                print(f"Key Resistance: {last_high:.5f}")
        else:
            print("Insufficient swing points for analysis")

def validate_current_trades():
    """Validate current trades with visual charts"""
    print("CREATING VISUAL VALIDATION CHARTS FOR OPEN TRADES")
    print("=" * 60)
    
    if not mt5.initialize():
        print("MT5 initialization failed")
        return
        
    marker = ChartMarker()
    
    # Get open positions
    positions = mt5.positions_get()
    if positions:
        for pos in positions:
            print(f"\nCreating marked chart for {pos.symbol}")
            marker.create_marked_chart(pos.symbol)
    else:
        print("No open positions found")
        
    # Also create charts for recently signaled symbols
    symbols_to_check = ['GBPJPY', 'EURUSD', 'EURJPY', 'HK_50', 'UK_100']
    for symbol in symbols_to_check:
        print(f"\nCreating marked chart for {symbol}")
        marker.create_marked_chart(symbol)
        
    print("\nAll marked charts created!")
    print("Charts show HH/HL/LH/LL structure like in your Live Market Example")
    
if __name__ == "__main__":
    validate_current_trades()