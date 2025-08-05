#!/usr/bin/env python3
"""
Get First MT5 News Item
Simple script to display the first news item from MetaTrader 5 News tab
"""

import sys
import re
from pathlib import Path

# ASCII-only print function
def ascii_print(text):
    """Print text using only ASCII characters"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

# Configure stdout for UTF-8 with error handling
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

def get_first_news():
    """Get and display the first news item from MT5"""
    
    # MT5 terminal path
    mt5_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075")
    news_file = mt5_path / "bases" / "Ava-Demo 1-MT5" / "news" / "news.dat"
    
    if not news_file.exists():
        ascii_print("MT5 news file not found")
        return
    
    try:
        # Read binary data
        with open(news_file, 'rb') as f:
            data = f.read()
        
        ascii_print(f"Reading MT5 news data ({len(data)} bytes)...")
        
        # Decode and clean
        text_data = data.decode('utf-8', errors='ignore').replace('\x00', '')
        
        # Find news segments
        segments = re.split(r'[\x00-\x1F]+', text_data)
        
        # Look for first meaningful news item
        for segment in segments:
            segment = segment.strip()
            if len(segment) < 30:
                continue
            
            # Check if this looks like a news item
            segment_lower = segment.lower()
            news_indicators = ['usd', 'eur', 'gbp', 'jpy', 'dollar', 'euro', 'trading', 'market']
            
            if any(indicator in segment_lower for indicator in news_indicators):
                # Clean for ASCII output
                clean_segment = re.sub(r'[^\x20-\x7E]', ' ', segment)
                clean_segment = re.sub(r'\s+', ' ', clean_segment).strip()
                
                if len(clean_segment) > 50:
                    ascii_print("FIRST MT5 NEWS ITEM:")
                    ascii_print("-" * 50)
                    
                    # Extract headline (first sentence or first 100 chars)
                    sentences = clean_segment.split('.')
                    headline = sentences[0][:100] if sentences else clean_segment[:100]
                    
                    ascii_print(f"HEADLINE: {headline}")
                    ascii_print("")
                    ascii_print("FULL CONTENT:")
                    ascii_print(clean_segment[:300] + "..." if len(clean_segment) > 300 else clean_segment)
                    ascii_print("-" * 50)
                    return
        
        ascii_print("No readable news items found in MT5 News tab")
        
    except Exception as e:
        ascii_print(f"Error reading MT5 news: {str(e)}")

if __name__ == "__main__":
    get_first_news()