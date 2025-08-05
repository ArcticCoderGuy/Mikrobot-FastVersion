#!/usr/bin/env python3
"""
Encoding Utilities
Optimized encoding utilities with async support
"""

# Import from existing encoding_utils.py and extend with async capabilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from encoding_utils import ASCIIFileManager, UnicodeReplacer, ascii_print, write_ascii_json

# Re-export for backward compatibility
__all__ = ['ASCIIFileManager', 'UnicodeReplacer', 'ascii_print', 'write_ascii_json']
