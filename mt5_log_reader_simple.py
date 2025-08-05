#!/usr/bin/env python3
"""
MT5 Simple Log Reader - Direct access to MT5 terminal logs
SOLVES the Unicode issue permanently with proper UTF-16LE handling
"""

import sys
import re
from datetime import datetime
from pathlib import Path
import MetaTrader5 as mt5

def ascii_print(text):
    """ASCII-only print to prevent Unicode issues"""
    ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
    print(ascii_text)

def read_mt5_log_properly(file_path):
    """Read MT5 UTF-16LE log file and extract readable content"""
    try:
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        # Try UTF-16LE decoding first
        try:
            decoded = raw_content.decode('utf-16le', errors='ignore')
        except:
            # Fallback to UTF-8
            decoded = raw_content.decode('utf-8', errors='ignore')
        
        # Clean up the content - remove null bytes and non-printable chars
        cleaned = decoded.replace('\x00', '')
        # Keep only ASCII printable characters plus newlines/tabs
        cleaned = re.sub(r'[^\x20-\x7E\n\r\t]', ' ', cleaned)
        
        # Split into lines and filter empty ones
        lines = [line.strip() for line in cleaned.split('\n') if line.strip()]
        
        return lines
        
    except Exception as e:
        ascii_print(f"Error reading {file_path}: {e}")
        return []

def parse_log_entry(line):
    """Parse a single log entry line"""
    # MT5 log format: ID TYPE TIME MESSAGE
    parts = line.split('\t')
    if len(parts) >= 4:
        return {
            'id': parts[0].strip(),
            'type': parts[1].strip(), 
            'time': parts[2].strip(),
            'message': '\t'.join(parts[3:]).strip()
        }
    else:
        # If tab splitting doesn't work, try space splitting
        parts = line.split(' ', 3)
        if len(parts) >= 4:
            return {
                'id': parts[0].strip(),
                'type': parts[1].strip(),
                'time': parts[2].strip(), 
                'message': parts[3].strip()
            }
    
    return None

def main():
    ascii_print("=== MT5 LOG READER - DIRECT ACCESS ===")
    
    # Initialize MT5 to get paths
    if not mt5.initialize():
        ascii_print("ERROR: Could not connect to MT5")
        return
    
    terminal_info = mt5.terminal_info()
    if not terminal_info:
        ascii_print("ERROR: Could not get terminal info")
        return
    
    data_path = Path(terminal_info.data_path)
    today = datetime.now().strftime('%Y%m%d')
    
    # Terminal log file
    terminal_log = data_path / 'logs' / f'{today}.log'
    expert_log = data_path / 'MQL5' / 'Logs' / f'{today}.log'
    
    ascii_print(f"Data Path: {data_path}")
    ascii_print(f"Terminal Log: {terminal_log}")
    ascii_print(f"Expert Log: {expert_log}")
    
    # Read terminal logs
    if terminal_log.exists():
        ascii_print(f"\n=== TERMINAL LOG ({today}) ===")
        terminal_lines = read_mt5_log_properly(terminal_log)
        ascii_print(f"Found {len(terminal_lines)} terminal log entries")
        
        # Show recent terminal activity
        for line in terminal_lines[-10:]:  # Last 10 entries
            entry = parse_log_entry(line)
            if entry:
                ascii_print(f"[{entry['time']}] {entry['type']}: {entry['message'][:80]}")
            else:
                ascii_print(f"RAW: {line[:80]}")
    else:
        ascii_print(f"Terminal log file not found: {terminal_log}")
    
    # Read expert logs
    if expert_log.exists():
        ascii_print(f"\n=== EXPERT ADVISOR LOG ({today}) ===")
        expert_lines = read_mt5_log_properly(expert_log)
        ascii_print(f"Found {len(expert_lines)} expert log entries")
        
        # Show recent expert activity
        for line in expert_lines[-15:]:  # Last 15 entries
            entry = parse_log_entry(line)
            if entry:
                # Extract EA name from message if possible
                message = entry['message']
                if '(' in message and ')' in message:
                    ea_part = message.split('(')[0].strip()
                    rest_part = message.split(')', 1)[1].strip() if ')' in message else message
                    ascii_print(f"[{entry['time']}] {ea_part}: {rest_part[:60]}")
                else:
                    ascii_print(f"[{entry['time']}] {message[:70]}")
            else:
                ascii_print(f"RAW: {line[:80]}")
    else:
        ascii_print(f"Expert log file not found: {expert_log}")
    
    # Read signal files
    signal_dir = data_path / 'MQL5' / 'Files'
    if signal_dir.exists():
        signal_files = list(signal_dir.glob('*signal*.json'))
        ascii_print(f"\n=== SIGNAL FILES ===")
        ascii_print(f"Found {len(signal_files)} signal files")
        
        for signal_file in signal_files:
            try:
                with open(signal_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Try to extract key info
                if 'symbol' in content.lower():
                    ascii_print(f"Signal file: {signal_file.name}")
                    ascii_print(f"  Content preview: {content[:100].replace(chr(0), '').strip()}")
                    
            except Exception as e:
                ascii_print(f"Error reading {signal_file.name}: {e}")
    
    mt5.shutdown()
    ascii_print("\n=== LOG READING COMPLETE ===")

if __name__ == "__main__":
    main()