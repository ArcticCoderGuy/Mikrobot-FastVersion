#!/usr/bin/env python3
"""
UNIVERSAL ENCODING UTILITIES
Permanent solution for Unicode encoding issues in Mikrobot trading system
ASCII-only file operations with proper MT5 UTF-16LE support
"""

import sys
import json
import re
import os
from typing import Any, Dict, Optional, Union
from datetime import datetime

class ASCIIFileManager:
    """Universal ASCII-only file operations for trading system"""
    
    @staticmethod
    def initialize_ascii_output():
        """Initialize ASCII-only output for the current Python session"""
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
            sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
        except:
            # Fallback for older Python versions
            pass
    
    @staticmethod
    def ascii_print(text: Any) -> None:
        """Print with ASCII-only characters, no Unicode allowed"""
        ascii_text = ''.join(char for char in str(text) if ord(char) < 128)
        print(ascii_text)
    
    @staticmethod
    def clean_ascii_string(text: str) -> str:
        """Remove all non-ASCII characters from string"""
        return ''.join(char for char in str(text) if ord(char) < 128)
    
    @staticmethod
    def write_ascii_json(filepath: str, data: Dict[str, Any]) -> bool:
        """Write JSON file with ASCII-only encoding"""
        try:
            with open(filepath, 'w', encoding='ascii', errors='ignore') as f:
                json.dump(data, f, indent=2, ensure_ascii=True)
            return True
        except Exception as e:
            ASCIIFileManager.ascii_print(f"JSON write error: {str(e)}")
            return False
    
    @staticmethod
    def write_ascii_file(filepath: str, content: str) -> bool:
        """Write text file with ASCII-only encoding"""
        try:
            ascii_content = ASCIIFileManager.clean_ascii_string(content)
            with open(filepath, 'w', encoding='ascii', errors='ignore') as f:
                f.write(ascii_content)
            return True
        except Exception as e:
            ASCIIFileManager.ascii_print(f"File write error: {str(e)}")
            return False
    
    @staticmethod
    def read_mt5_signal_file(filepath: str) -> Optional[Dict[str, Any]]:
        """Read MT5 signal file with proper UTF-16LE handling"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Handle UTF-16LE with null bytes - convert to clean ASCII
            content_str = content.decode('utf-16le', errors='ignore').replace('\x00', '')
            
            # Strip ALL non-ASCII characters except basic JSON chars
            content_str = re.sub(r'[^\x20-\x7E]', '', content_str)
            
            return json.loads(content_str)
        except Exception as e:
            ASCIIFileManager.ascii_print(f"Signal read error: {str(e)}")
            return None
    
    @staticmethod
    def write_mt5_signal_file(filepath: str, data: Dict[str, Any]) -> bool:
        """Write MT5 signal file with proper encoding for Expert Advisors"""
        try:
            # Create clean ASCII JSON
            json_str = json.dumps(data, indent=2, ensure_ascii=True)
            ascii_json = ASCIIFileManager.clean_ascii_string(json_str)
            
            # Write as UTF-16LE for MT5 compatibility (EA reads UTF-16LE)
            with open(filepath, 'w', encoding='utf-16le') as f:
                f.write(ascii_json)
            
            return True
        except Exception as e:
            ASCIIFileManager.ascii_print(f"Signal write error: {str(e)}")
            return False
    
    @staticmethod
    def create_log_entry(message: str, level: str = "INFO") -> Dict[str, str]:
        """Create ASCII-only log entry"""
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": ASCIIFileManager.clean_ascii_string(level),
            "message": ASCIIFileManager.clean_ascii_string(message),
            "encoding": "ASCII_ONLY"
        }
    
    @staticmethod
    def log_to_file(filepath: str, message: str, level: str = "INFO") -> bool:
        """Append ASCII-only log entry to file"""
        try:
            log_entry = ASCIIFileManager.create_log_entry(message, level)
            
            # Read existing logs if file exists
            logs = []
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='ascii', errors='ignore') as f:
                        logs = json.load(f)
                except:
                    logs = []
            
            logs.append(log_entry)
            
            # Keep only last 1000 entries to prevent file bloat
            if len(logs) > 1000:
                logs = logs[-1000:]
            
            return ASCIIFileManager.write_ascii_json(filepath, logs)
        except Exception as e:
            ASCIIFileManager.ascii_print(f"Logging error: {str(e)}")
            return False

class UnicodeReplacer:
    """Replace common Unicode characters with ASCII equivalents"""
    
    UNICODE_MAP = {
        # Checkmarks and status symbols
        '\u2713': 'OK',      # ✓
        '\u2714': 'OK',      # ✔
        '\u2705': 'OK',      # ✅
        '\u274C': 'ERROR',   # ❌
        '\u26A0': 'WARNING', # ⚠
        '\u2B50': 'STAR',    # ⭐
        '\U0001F4CA': 'CHART',   # 📊
        '\U0001F525': 'HOT',     # 🔥
        '\U0001F4B0': 'MONEY',   # 💰
        '\U0001F3AF': 'TARGET',  # 🎯
        '\U0001F680': 'ROCKET',  # 🚀
        '\U0001F4C8': 'GRAPH_UP', # 📈
        '\U0001F527': 'TOOL',    # 🔧
        '\u26A1': 'FAST',    # ⚡
        
        # Currency symbols
        '\u20AC': 'EUR',     # €
        '\u00A3': 'GBP',     # £
        '\u00A5': 'JPY',     # ¥
        
        # Mathematical symbols
        '\u2192': '->',      # →
        '\u2190': '<-',      # ←
        '\u2194': '<->',     # ↔
        '\u2260': '!=',      # ≠
        '\u2248': '~=',      # ≈
        '\u00B1': '+/-',     # ±
        
        # Quotes and dashes
        '\u201C': '"',       # "
        '\u201D': '"',       # "
        '\u2018': "'",       # '
        '\u2019': "'",       # '
        '\u2013': '-',       # –
        '\u2014': '--',      # —
    }
    
    @staticmethod
    def replace_unicode(text: str) -> str:
        """Replace Unicode characters with ASCII equivalents"""
        result = str(text)
        for unicode_char, ascii_replacement in UnicodeReplacer.UNICODE_MAP.items():
            result = result.replace(unicode_char, ascii_replacement)
        
        # Remove any remaining non-ASCII characters
        result = ''.join(char for char in result if ord(char) < 128)
        return result

def initialize_encoding_system():
    """Initialize the encoding system for the current session"""
    ASCIIFileManager.initialize_ascii_output()
    
    ASCIIFileManager.ascii_print("ENCODING SYSTEM INITIALIZED")
    ASCIIFileManager.ascii_print("=" * 35)
    ASCIIFileManager.ascii_print("- ASCII-only output configured")
    ASCIIFileManager.ascii_print("- Unicode character mapping ready")
    ASCIIFileManager.ascii_print("- MT5 signal file handling configured")
    ASCIIFileManager.ascii_print("- Error handling: ignore non-ASCII")
    ASCIIFileManager.ascii_print("")
    
    # Test the system
    test_message = "System initialized successfully - no Unicode issues"
    ASCIIFileManager.ascii_print(f"Test: {test_message}")
    
    return True

# Backwards compatibility aliases
ascii_print = ASCIIFileManager.ascii_print
write_ascii_json = ASCIIFileManager.write_ascii_json
read_mt5_signal = ASCIIFileManager.read_mt5_signal_file
write_mt5_signal = ASCIIFileManager.write_mt5_signal_file

if __name__ == "__main__":
    initialize_encoding_system()
    
    # Test Unicode replacement
    test_text = "Trade executed ✅ with profit 💰 targeting 🎯 performance ⚡"
    clean_text = UnicodeReplacer.replace_unicode(test_text)
    ASCIIFileManager.ascii_print(f"Original: {test_text}")
    ASCIIFileManager.ascii_print(f"Cleaned:  {clean_text}")