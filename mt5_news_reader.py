#!/usr/bin/env python3
"""
MT5 News Reader - Access MetaTrader 5 News Tab Data
Reads and parses news data from MT5 terminal files

ENCODING STANDARDS COMPLIANCE:
- ASCII-only output (no Unicode characters)
- UTF-8 with ignore errors for file reading
- Null byte removal and ASCII filtering
"""

import os
import sys
import struct
import datetime
import re
from pathlib import Path

# ASCII-only print function
def ascii_print(text):
    """Print text using only ASCII characters"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

# Configure stdout for UTF-8 with error handling
sys.stdout.reconfigure(encoding='utf-8', errors='ignore')

class MT5NewsReader:
    def __init__(self):
        self.mt5_terminal_path = Path("C:/Users/HP/AppData/Roaming/MetaQuotes/Terminal/D0E8209F77C8CF37AD8BF550E51FF075")
        self.news_paths = []
        self.find_news_files()
    
    def find_news_files(self):
        """Find all news.dat files in MT5 bases directory"""
        bases_path = self.mt5_terminal_path / "bases"
        
        if not bases_path.exists():
            ascii_print("ERROR: MT5 bases directory not found")
            return
        
        # Search for news.dat files in broker directories
        for broker_dir in bases_path.iterdir():
            if broker_dir.is_dir():
                news_file = broker_dir / "news" / "news.dat"
                if news_file.exists():
                    self.news_paths.append(news_file)
                    ascii_print(f"Found news file: {broker_dir.name}")
    
    def read_binary_data(self, file_path):
        """Read binary data from news.dat file"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            return data
        except Exception as e:
            ascii_print(f"ERROR reading file: {str(e)}")
            return None
    
    def parse_news_data(self, binary_data):
        """Parse binary news data to extract news items"""
        if not binary_data:
            return []
        
        news_items = []
        
        try:
            # MT5 news.dat format analysis
            if len(binary_data) < 16:
                ascii_print("File too small to contain news data")
                return []
            
            # Decode with multiple encodings and clean
            text_data = ""
            for encoding in ['utf-8', 'utf-16le', 'latin1']:
                try:
                    text_data = binary_data.decode(encoding, errors='ignore')
                    break
                except:
                    continue
            
            # Remove null bytes and clean up
            text_data = text_data.replace('\x00', '')
            
            # Find news segments - look for common news patterns
            news_segments = []
            
            # Split on common delimiters and look for news-like content
            potential_segments = re.split(r'[\x00-\x1F]+', text_data)
            
            for segment in potential_segments:
                segment = segment.strip()
                if len(segment) < 20:
                    continue
                
                # Look for news indicators
                news_indicators = [
                    'USD', 'EUR', 'GBP', 'JPY', 'Trading Central', 'Analyst',
                    'Dollar', 'Euro', 'Pound', 'Yen', 'Market', 'Economic',
                    'Fed', 'ECB', 'Bank', 'Rate', 'GDP', 'Inflation'
                ]
                
                segment_lower = segment.lower()
                if any(indicator.lower() in segment_lower for indicator in news_indicators):
                    # Clean the segment for ASCII output
                    clean_segment = re.sub(r'[^\x20-\x7E]', ' ', segment)
                    clean_segment = re.sub(r'\s+', ' ', clean_segment).strip()
                    
                    if len(clean_segment) > 30:
                        news_segments.append(clean_segment)
            
            # Process segments into news items
            for i, segment in enumerate(news_segments[:10]):  # Limit to first 10
                # Try to separate headline from content
                sentences = segment.split('.')
                headline = sentences[0][:100] if sentences else segment[:100]
                
                news_items.append({
                    'headline': headline.strip(),
                    'content': segment[:500],  # First 500 chars
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'item_number': i + 1
                })
                
        except Exception as e:
            ascii_print(f"ERROR parsing news data: {str(e)}")
        
        return news_items
    
    def try_alternative_news_sources(self):
        """Try alternative sources for news data"""
        ascii_print("Trying alternative news sources...")
        
        # Check for recent log files that might contain news
        logs_path = self.mt5_terminal_path / "logs"
        if logs_path.exists():
            recent_logs = sorted([f for f in logs_path.glob("*.log")], reverse=True)[:3]
            
            for log_file in recent_logs:
                ascii_print(f"Checking log file: {log_file.name}")
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Look for news-related entries
                    news_patterns = ['news', 'headline', 'economic', 'report', 'announcement']
                    lines = content.split('\n')
                    
                    for line in lines:
                        line_lower = line.lower()
                        if any(pattern in line_lower for pattern in news_patterns):
                            # Clean line for ASCII output
                            clean_line = re.sub(r'[^\x20-\x7E]', '', line)
                            if len(clean_line) > 20:
                                ascii_print(f"News-related log entry: {clean_line[:200]}")
                                return [{'headline': clean_line[:100], 'content': clean_line, 'source': 'log'}]
                
                except Exception as e:
                    ascii_print(f"ERROR reading log {log_file.name}: {str(e)}")
        
        return []
    
    def get_first_news_item(self):
        """Get the first/most recent news item"""
        if not self.news_paths:
            ascii_print("No news files found. Trying alternative sources...")
            return self.try_alternative_news_sources()
        
        for news_path in self.news_paths:
            ascii_print(f"Reading news from: {news_path.parent.parent.name}")
            
            binary_data = self.read_binary_data(news_path)
            if not binary_data:
                continue
            
            ascii_print(f"News file size: {len(binary_data)} bytes")
            
            news_items = self.parse_news_data(binary_data)
            
            if news_items:
                return news_items
            else:
                ascii_print("No readable news items found in standard format")
                
                # Try hex dump analysis for debugging
                hex_sample = binary_data[:200].hex()
                ascii_print(f"Binary sample (hex): {hex_sample[:100]}...")
                
                # Try to find readable strings
                readable_strings = []
                current_string = ""
                
                for byte in binary_data[:1000]:  # Check first 1000 bytes
                    if 32 <= byte <= 126:  # Printable ASCII
                        current_string += chr(byte)
                    else:
                        if len(current_string) > 10:
                            readable_strings.append(current_string)
                        current_string = ""
                
                if readable_strings:
                    ascii_print("Readable strings found:")
                    for i, string in enumerate(readable_strings[:5]):
                        ascii_print(f"  {i+1}: {string[:100]}")
                    
                    # Return first readable string as potential news
                    return [{
                        'headline': readable_strings[0][:100],
                        'content': readable_strings[0],
                        'source': 'binary_extract',
                        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }]
        
        return []

def main():
    """Main function to read and display first news item"""
    ascii_print("=== MT5 News Reader ===")
    ascii_print("Reading MetaTrader 5 News Tab data...")
    ascii_print("")
    
    reader = MT5NewsReader()
    news_items = reader.get_first_news_item()
    
    if news_items:
        ascii_print("MT5 NEWS TAB - FIRST NEWS ITEM:")
        ascii_print("=" * 60)
        
        first_news = news_items[0]
        headline = first_news.get('headline', 'No headline available')
        content = first_news.get('content', 'No content available')
        
        ascii_print(f"HEADLINE: {headline}")
        ascii_print("")
        ascii_print("CONTENT:")
        ascii_print(content[:400] + "..." if len(content) > 400 else content)
        ascii_print("")
        ascii_print(f"Source: MT5 {first_news.get('source', 'news.dat')}")
        ascii_print(f"Retrieved: {first_news.get('timestamp', 'Unknown')}")
        ascii_print("=" * 60)
        
        if len(news_items) > 1:
            ascii_print(f"Total news items available: {len(news_items)}")
            ascii_print("")
            ascii_print("Additional news headlines:")
            for i, item in enumerate(news_items[1:6], 2):  # Show next 5 headlines
                ascii_print(f"{i}. {item.get('headline', 'No headline')[:80]}...")
    else:
        ascii_print("UNABLE TO READ NEWS FROM MT5")
        ascii_print("=" * 40)
        ascii_print("Possible reasons:")
        ascii_print("1. News service not enabled in MT5 terminal")
        ascii_print("2. No internet connection for news feed")
        ascii_print("3. Binary format encryption/compression")
        ascii_print("4. MT5 news database is empty")
        ascii_print("5. Different MT5 version with incompatible format")

if __name__ == "__main__":
    main()