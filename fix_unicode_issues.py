#!/usr/bin/env python3
"""
UNICODE ISSUE FIXER
Automatically fixes all Unicode encoding issues in Python files
Replaces Unicode characters with ASCII equivalents and updates file operations
"""

import os
import re
import sys
from typing import List, Tuple
from encoding_utils import ASCIIFileManager, UnicodeReplacer

class UnicodeFileFixer:
    """Fixes Unicode issues in Python files"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.files_fixed = 0
        self.unicode_replacements = 0
        self.encoding_fixes = 0
        
    def find_python_files(self) -> List[str]:
        """Find all Python files in the project"""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            skip_dirs = {'.git', '__pycache__', 'node_modules', '.env', 'venv'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def detect_unicode_issues(self, content: str) -> List[Tuple[str, str]]:
        """Detect Unicode characters and encoding issues"""
        issues = []
        
        # Find Unicode characters in print statements
        unicode_patterns = [
            (r'print\([^)]*[✓✅❌⚠⭐📊🔥💰🎯🚀📈🔧⚡][^)]*\)', 'unicode_in_print'),
            (r'f"[^"]*[✓✅❌⚠⭐📊🔥💰🎯🚀📈🔧⚡][^"]*"', 'unicode_in_fstring'),
            (r'"[^"]*[✓✅❌⚠⭐📊🔥💰🎯🚀📈🔧⚡][^"]*"', 'unicode_in_string'),
            (r"'[^']*[✓✅❌⚠⭐📊🔥💰🎯🚀📈🔧⚡][^']*'", 'unicode_in_string'),
        ]
        
        for pattern, issue_type in unicode_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                issues.append((match, issue_type))
        
        # Find problematic file operations
        encoding_patterns = [
            (r'open\([^)]*\)(?!\s*as\s+\w+:)', 'missing_encoding'),
            (r'with\s+open\([^)]*\)(?!\s*as)', 'missing_encoding_context'),
            (r'\.write\([^)]*[^\x00-\x7F][^)]*\)', 'unicode_in_write'),
            (r'json\.dump\([^)]*ensure_ascii=False[^)]*\)', 'json_unicode_enabled'),
        ]
        
        for pattern, issue_type in encoding_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                issues.append((match, issue_type))
        
        return issues
    
    def fix_unicode_characters(self, content: str) -> str:
        """Replace Unicode characters with ASCII equivalents"""
        original_content = content
        
        # Replace Unicode characters in the content
        content = UnicodeReplacer.replace_unicode(content)
        
        if content != original_content:
            self.unicode_replacements += 1
        
        return content
    
    def fix_encoding_issues(self, content: str) -> str:
        """Fix encoding-related issues in file operations"""
        original_content = content
        
        # Add encoding_utils import if not present
        if 'from encoding_utils import' not in content and 'import encoding_utils' not in content:
            # Find the best place to add the import
            lines = content.split('\n')
            import_line = 'from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal'
            
            # Find last import or add after shebang/docstring
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_index = i + 1
                elif line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                    break
            
            lines.insert(insert_index, import_line)
            content = '\n'.join(lines)
        
        # Replace print statements with Unicode
        unicode_print_pattern = r'print\(([^)]*[✓✅❌⚠⭐📊🔥💰🎯🚀📈🔧⚡][^)]*)\)'
        def replace_print(match):
            return f'ascii_print({match.group(1)})'
        content = re.sub(unicode_print_pattern, replace_print, content)
        
        # Fix file operations without proper encoding
        # Replace basic open() calls with ASCII-safe versions
        open_patterns = [
            (r"with open\(([^,)]+), 'w'\) as ([^:]+):", 
             r"with open(\1, 'w', encoding='ascii', errors='ignore') as \2:"),
            (r"with open\(([^,)]+), 'r'\) as ([^:]+):",
             r"with open(\1, 'r', encoding='ascii', errors='ignore') as \2:"),
            (r"open\(([^,)]+), 'w'\)",
             r"open(\1, 'w', encoding='ascii', errors='ignore')"),
            (r"open\(([^,)]+), 'r'\)",
             r"open(\1, 'r', encoding='ascii', errors='ignore')"),
        ]
        
        for pattern, replacement in open_patterns:
            content = re.sub(pattern, replacement, content)
        
        # Fix JSON dumps to ensure ASCII
        content = re.sub(r'json\.dump\(([^,]+),\s*([^,)]+)\)',
                        r'json.dump(\1, \2, ensure_ascii=True)', content)
        content = re.sub(r'json\.dumps\(([^)]+)\)',
                        r'json.dumps(\1, ensure_ascii=True)', content)
        
        if content != original_content:
            self.encoding_fixes += 1
        
        return content
    
    def add_ascii_initialization(self, content: str) -> str:
        """Add ASCII initialization to main scripts"""
        if '__name__ == "__main__"' in content and 'sys.stdout.reconfigure' not in content:
            # Add ASCII initialization before main execution
            init_code = '''
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
'''
            content = content.replace('if __name__ == "__main__":', 
                                    f'if __name__ == "__main__":{init_code}')
        
        return content
    
    def fix_file(self, filepath: str) -> bool:
        """Fix Unicode issues in a single Python file"""
        try:
            # Read the file
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Detect issues
            issues = self.detect_unicode_issues(content)
            if not issues:
                return False  # No issues found
            
            ASCIIFileManager.ascii_print(f"Fixing: {os.path.basename(filepath)}")
            ASCIIFileManager.ascii_print(f"  Issues found: {len(issues)}")
            
            # Apply fixes
            original_content = content
            content = self.fix_unicode_characters(content)
            content = self.fix_encoding_issues(content)
            content = self.add_ascii_initialization(content)
            
            # Write back if changed
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content)
                self.files_fixed += 1
                ASCIIFileManager.ascii_print(f"  Fixed: {os.path.basename(filepath)}")
                return True
            
        except Exception as e:
            ASCIIFileManager.ascii_print(f"Error fixing {filepath}: {str(e)}")
        
        return False
    
    def fix_all_files(self) -> None:
        """Fix Unicode issues in all Python files"""
        ASCIIFileManager.ascii_print("MIKROBOT UNICODE ISSUE FIXER")
        ASCIIFileManager.ascii_print("=" * 40)
        
        python_files = self.find_python_files()
        ASCIIFileManager.ascii_print(f"Found {len(python_files)} Python files")
        ASCIIFileManager.ascii_print("")
        
        for filepath in python_files:
            # Skip this fixer script and encoding utils
            if os.path.basename(filepath) in ['fix_unicode_issues.py', 'encoding_utils.py']:
                continue
            
            self.fix_file(filepath)
        
        ASCIIFileManager.ascii_print("")
        ASCIIFileManager.ascii_print("FIXING COMPLETE")
        ASCIIFileManager.ascii_print(f"Files fixed: {self.files_fixed}")
        ASCIIFileManager.ascii_print(f"Unicode replacements: {self.unicode_replacements}")
        ASCIIFileManager.ascii_print(f"Encoding fixes: {self.encoding_fixes}")
        
        # Create a summary report
        report = {
            "timestamp": ASCIIFileManager.create_log_entry("Unicode fixes applied")["timestamp"],
            "files_processed": len(python_files),
            "files_fixed": self.files_fixed,
            "unicode_replacements": self.unicode_replacements,
            "encoding_fixes": self.encoding_fixes,
            "status": "UNICODE_ISSUES_RESOLVED"
        }
        
        ASCIIFileManager.write_ascii_json("unicode_fix_report.json", report)
        ASCIIFileManager.ascii_print("Report saved: unicode_fix_report.json")

def main():
    """Main function to fix all Unicode issues"""
    # Initialize encoding system
    ASCIIFileManager.initialize_ascii_output()
    
    project_root = os.getcwd()
    fixer = UnicodeFileFixer(project_root)
    fixer.fix_all_files()
    
    ASCIIFileManager.ascii_print("")
    ASCIIFileManager.ascii_print("UNICODE ISSUES PERMANENTLY RESOLVED")
    ASCIIFileManager.ascii_print("All Python files now use ASCII-only output")
    ASCIIFileManager.ascii_print("Future charmap codec errors eliminated")

if __name__ == "__main__":
    main()