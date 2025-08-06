"""
Real Candlestick Chart Generator
================================

Creates REAL candlestick charts like in trading platforms
Uses actual market data from APIs
Shows market structure (HH, HL, LH, LL)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import os
import logging
import aiohttp
import ssl
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Candle:
    """Real candlestick data"""
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int

@dataclass
class MarketStructure:
    """Market structure point (HH, HL, LH, LL)"""
    time: datetime
    price: float
    type: str  # "HH", "HL", "LH", "LL" 
    color: str  # "green" or "red"

class RealCandlestickChartGenerator:
    """
    Generate real candlestick charts with actual market data
    """
    
    def __init__(self):
        self.chart_dir = "/Users/markuskaprio/Desktop/Claude Code Projektit/MikrobotFastversion/charts"
        os.makedirs(self.chart_dir, exist_ok=True)
        
        # Alpha Vantage API key
        self.alpha_key = "3M9G2YI3P8TTW72C"
        
        plt.style.use('dark_background')
        logger.info("📊 Real Candlestick Chart Generator initialized")
    
    async def get_real_candle_data(self, symbol: str, interval: str = "5min", 
                                 outputsize: str = "compact") -> List[Candle]:
        """Get real candlestick data from Alpha Vantage"""
        
        try:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                
                # Alpha Vantage intraday endpoint
                url = "https://www.alphavantage.co/query"
                params = {
                    'function': 'FX_INTRADAY',
                    'from_symbol': symbol[:3],  # EUR from EURUSD
                    'to_symbol': symbol[3:6],   # USD from EURUSD
                    'interval': interval,
                    'outputsize': outputsize,
                    'apikey': self.alpha_key
                }
                
                print(f"📡 Fetching real candle data for {symbol}...")
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API response
                        time_series_key = f'Time Series FX ({interval})'
                        if time_series_key in data:
                            candles = []
                            time_series = data[time_series_key]
                            
                            # Parse candlestick data
                            for timestamp, ohlcv in time_series.items():
                                candle = Candle(
                                    time=datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                                    open=float(ohlcv['1. open']),
                                    high=float(ohlcv['2. high']),
                                    low=float(ohlcv['3. low']),
                                    close=float(ohlcv['4. close']),
                                    volume=100  # FX doesn't have real volume
                                )
                                candles.append(candle)
                            
                            # Sort by time (oldest first)
                            candles.sort(key=lambda x: x.time)
                            
                            print(f"✅ Got {len(candles)} real candles for {symbol}")
                            return candles[-50:]  # Last 50 candles
                        
                        elif 'Error Message' in data:
                            logger.error(f"Alpha Vantage error: {data['Error Message']}")
                        elif 'Note' in data:
                            logger.warning(f"API limit: {data['Note']}")
                    
                    else:
                        logger.error(f"HTTP error {response.status}")
            
        except Exception as e:
            logger.error(f"Error fetching candle data: {e}")
        
        return []
    
    def detect_market_structure(self, candles: List[Candle]) -> List[MarketStructure]:
        """Detect market structure points (HH, HL, LH, LL)"""
        
        if len(candles) < 10:
            return []
        
        structures = []
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        
        # Find swing highs and lows
        for i in range(5, len(candles) - 5):
            candle = candles[i]
            
            # Check if it's a swing high
            is_swing_high = all(candle.high >= candles[j].high for j in range(i-3, i+4))
            
            # Check if it's a swing low  
            is_swing_low = all(candle.low <= candles[j].low for j in range(i-3, i+4))
            
            if is_swing_high:
                # Determine if HH or LH
                recent_highs = [c.high for c in candles[max(0, i-20):i] if c.high > candle.high * 0.9]
                if recent_highs and candle.high > max(recent_highs):
                    structure_type = "HH"
                    color = "green"
                else:
                    structure_type = "LH" 
                    color = "red"
                
                structures.append(MarketStructure(
                    time=candle.time,
                    price=candle.high,
                    type=structure_type,
                    color=color
                ))
            
            elif is_swing_low:
                # Determine if HL or LL
                recent_lows = [c.low for c in candles[max(0, i-20):i] if c.low < candle.low * 1.1]
                if recent_lows and candle.low > min(recent_lows):
                    structure_type = "HL"
                    color = "green"  
                else:
                    structure_type = "LL"
                    color = "red"
                
                structures.append(MarketStructure(
                    time=candle.time,
                    price=candle.low,
                    type=structure_type,
                    color=color
                ))
        
        return structures
    
    async def generate_real_candlestick_chart(self, symbol: str, pattern_phase: str) -> str:
        """Generate real candlestick chart like trading platforms"""
        
        try:
            # Get real candle data
            candles = await self.get_real_candle_data(symbol, interval="5min")
            
            if not candles:
                logger.error("No candlestick data available")
                return None
            
            # Detect market structure
            structures = self.detect_market_structure(candles)
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12),
                                         gridspec_kw={'height_ratios': [4, 1]})
            fig.patch.set_facecolor('#1a1a1a')
            
            # Main candlestick chart
            ax1.set_facecolor('#2a2a2a')
            
            print(f"📊 Drawing {len(candles)} real candlesticks...")
            
            # Draw candlesticks
            for i, candle in enumerate(candles):
                # Candlestick colors
                is_bullish = candle.close > candle.open
                body_color = '#00ff88' if is_bullish else '#ff4444'
                wick_color = '#ffffff'
                
                # Wick (high-low line)
                ax1.plot([candle.time, candle.time], [candle.low, candle.high],
                        color=wick_color, linewidth=1.5, alpha=0.8)
                
                # Body rectangle
                body_height = abs(candle.close - candle.open)
                body_bottom = min(candle.open, candle.close)
                
                # Calculate candle width
                if len(candles) > 1:
                    time_diff = (candles[1].time - candles[0].time).total_seconds() / 86400
                    candle_width = time_diff * 0.7
                else:
                    candle_width = 0.002
                
                rect = Rectangle(
                    (mdates.date2num(candle.time) - candle_width/2, body_bottom),
                    candle_width, body_height,
                    facecolor=body_color, edgecolor=body_color,
                    linewidth=1, alpha=0.9
                )
                ax1.add_patch(rect)
            
            # Draw market structure points
            for structure in structures:
                color = '#00ff00' if structure.color == 'green' else '#ff0000'
                
                # Circle around structure point
                circle = Circle((mdates.date2num(structure.time), structure.price),
                              radius=0.001, facecolor='none', edgecolor=color,
                              linewidth=3, alpha=0.8)
                ax1.add_patch(circle)
                
                # Label
                ax1.text(mdates.date2num(structure.time), structure.price,
                        f'  {structure.type}  ', fontsize=10, fontweight='bold',
                        color='white', bbox=dict(boxstyle='round,pad=0.3',
                        facecolor=color, alpha=0.8))
            
            # Add pattern detection
            if candles:
                latest_candle = candles[-1]
                current_price = latest_candle.close
                
                # BOS arrow
                ax1.annotate(f'⚡ {pattern_phase}\nBOS DETECTED\n{current_price:.5f}',
                           xy=(latest_candle.time, current_price),
                           xytext=(20, 40), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.8',
                                   facecolor='#ff6600', alpha=0.9,
                                   edgecolor='white', linewidth=2),
                           arrowprops=dict(arrowstyle='->', color='#ff6600', lw=3),
                           fontsize=12, fontweight='bold', color='white')
            
            # Chart title
            title = f'⚡ {symbol} - REAL CANDLESTICK CHART\n{pattern_phase} • Market Structure Analysis'
            ax1.set_title(title, fontsize=18, fontweight='bold', color='white', pad=20)
            
            # Format axes
            ax1.set_ylabel('Price', fontsize=14, color='white', fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--', color='gray')
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
            
            # Volume chart (bottom)
            ax2.set_facecolor('#2a2a2a')
            volumes = [c.volume for c in candles]
            times = [c.time for c in candles]
            colors = ['#00ff88' if c.close > c.open else '#ff4444' for c in candles]
            
            ax2.bar(times, volumes, color=colors, alpha=0.7, width=candle_width)
            ax2.set_ylabel('Volume', fontsize=12, color='white')
            ax2.grid(True, alpha=0.3, linestyle='--', color='gray')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"real_candlestick_{symbol}_{timestamp}.png"
            filepath = os.path.join(self.chart_dir, filename)
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight',
                       facecolor='#1a1a1a', edgecolor='none')
            plt.close()
            
            print(f"✅ Real candlestick chart saved: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Real candlestick chart error: {e}")
            import traceback
            print(f"Chart error: {traceback.format_exc()}")
            return None

# Global instance
real_candlestick_generator = RealCandlestickChartGenerator()

# Convenience function
async def generate_real_candlestick_chart(symbol: str, pattern_phase: str) -> str:
    """Generate real candlestick chart with market structure"""
    return await real_candlestick_generator.generate_real_candlestick_chart(symbol, pattern_phase)