from encoding_utils import ASCIIFileManager, ascii_print, write_ascii_json, read_mt5_signal, write_mt5_signal
#!/usr/bin/env python3
"""
MT5 Data Explorer - Deep Analysis of MT5 Data Folders and Configuration
Explores MetaTrader 5 data directories, log files, and configuration files
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
import configparser
import sqlite3
from typing import Dict, List, Any, Optional
import struct
import codecs

class MT5DataExplorer:
    """Explorer for MT5 data directories and configuration files"""
    
    def __init__(self):
        self.mt5_data_paths = []
        self.common_data_path = None
        self.terminal_data_path = None
        self.found_files = {
            'logs': [],
            'configs': [],
            'databases': [],
            'experts': [],
            'profiles': []
        }
        
    def find_mt5_data_directories(self) -> List[Path]:
        """Find all MT5 data directories"""
        data_paths = []
        
        # Common MT5 data locations
        potential_paths = [
            Path.home() / "AppData" / "Roaming" / "MetaQuotes" / "Terminal",
            Path("C:") / "Program Files" / "MetaTrader 5" / "MQL5",
            Path("C:") / "Program Files (x86)" / "MetaTrader 5" / "MQL5",
            Path("C:") / "Users" / "Public" / "Documents" / "MetaQuotes",
            Path.home() / "Documents" / "MetaQuotes",
        ]
        
        # Also check environment variables and registry hints
        try:
            import MetaTrader5 as mt5
            if mt5.initialize():
                terminal_info = mt5.terminal_info()
                if terminal_info:
                    if terminal_info.data_path:
                        potential_paths.append(Path(terminal_info.data_path))
                    if terminal_info.commondata_path:
                        potential_paths.append(Path(terminal_info.commondata_path))
                mt5.shutdown()
        except:
            pass
        
        # Check each potential path
        for path in potential_paths:
            if path.exists():
                data_paths.append(path)
                print(f" Found MT5 data directory: {path}")
                
                # Look for subdirectories
                for subdir in path.iterdir():
                    if subdir.is_dir() and len(subdir.name) == 32:  # Terminal hash directories
                        data_paths.append(subdir)
                        print(f"   Terminal directory: {subdir.name[:8]}...")
        
        self.mt5_data_paths = data_paths
        return data_paths
    
    def scan_directory_structure(self, base_path: Path) -> Dict[str, Any]:
        """Scan and categorize MT5 directory structure"""
        structure = {
            'base_path': str(base_path),
            'subdirectories': {},
            'files': {},
            'interesting_files': []
        }
        
        if not base_path.exists():
            return structure
        
        try:
            for item in base_path.iterdir():
                if item.is_dir():
                    # Recursively scan important subdirectories
                    if item.name.lower() in ['logs', 'config', 'profiles', 'mql5', 'experts', 'indicators']:
                        structure['subdirectories'][item.name] = self.scan_directory_structure(item)
                    else:
                        structure['subdirectories'][item.name] = {
                            'path': str(item),
                            'file_count': len(list(item.glob('*'))) if item.exists() else 0
                        }
                elif item.is_file():
                    file_info = {
                        'path': str(item),
                        'size': item.stat().st_size,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime),
                        'extension': item.suffix.lower()
                    }
                    
                    structure['files'][item.name] = file_info
                    
                    # Mark interesting files
                    interesting_extensions = ['.log', '.ini', '.cfg', '.set', '.ex5', '.mqh', '.mq5', '.db', '.sqlite']
                    if item.suffix.lower() in interesting_extensions:
                        structure['interesting_files'].append(file_info)
                        
        except PermissionError as e:
            structure['error'] = f"Permission denied: {e}"
        except Exception as e:
            structure['error'] = f"Error scanning: {e}"
        
        return structure
    
    def find_log_files(self) -> List[Dict[str, Any]]:
        """Find and analyze MT5 log files"""
        log_files = []
        
        for data_path in self.mt5_data_paths:
            # Common log locations
            log_locations = [
                data_path / "Logs",
                data_path / "Terminal" / "Logs",
                data_path / "MQL5" / "Logs"
            ]
            
            for log_location in log_locations:
                if log_location.exists():
                    for log_file in log_location.glob("*.log"):
                        try:
                            stat = log_file.stat()
                            log_info = {
                                'path': str(log_file),
                                'name': log_file.name,
                                'size': stat.st_size,
                                'modified': datetime.fromtimestamp(stat.st_mtime),
                                'type': self._classify_log_file(log_file.name),
                                'recent_entries': []
                            }
                            
                            # Read recent entries
                            try:
                                recent_entries = self.read_log_file_tail(log_file, 10)
                                log_info['recent_entries'] = recent_entries
                            except Exception as e:
                                log_info['read_error'] = str(e)
                            
                            log_files.append(log_info)
                            self.found_files['logs'].append(log_file)
                            
                        except Exception as e:
                            print(f"WARNING  Error processing log file {log_file}: {e}")
        
        return log_files
    
    def _classify_log_file(self, filename: str) -> str:
        """Classify log file type based on filename"""
        filename_lower = filename.lower()
        
        if 'journal' in filename_lower:
            return 'Journal'
        elif 'experts' in filename_lower or 'expert' in filename_lower:
            return 'Expert Advisor'
        elif 'terminal' in filename_lower:
            return 'Terminal'
        elif 'connect' in filename_lower:
            return 'Connection'
        elif 'trade' in filename_lower:
            return 'Trading'
        elif filename_lower.endswith('.log'):
            return 'General Log'
        else:
            return 'Unknown'
    
    def read_log_file_tail(self, log_file: Path, lines: int = 50) -> List[str]:
        """Read last N lines from a log file"""
        recent_lines = []
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'cp1252', 'ascii']
            
            for encoding in encodings:
                try:
                    with open(log_file, 'r', encoding=encoding, errors='ignore') as f:
                        all_lines = f.readlines()
                        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                        break
                except UnicodeDecodeError:
                    continue
            
            # Clean up lines
            cleaned_lines = []
            for line in recent_lines:
                line = line.strip()
                if line and len(line) > 0:
                    cleaned_lines.append(line)
            
            return cleaned_lines
            
        except Exception as e:
            print(f"WARNING  Could not read log file {log_file}: {e}")
            return []
    
    def find_configuration_files(self) -> List[Dict[str, Any]]:
        """Find MT5 configuration files"""
        config_files = []
        
        for data_path in self.mt5_data_paths:
            # Common config locations
            config_locations = [
                data_path / "config",
                data_path / "Config",
                data_path / "profiles",
                data_path / "Profiles",
                data_path
            ]
            
            config_extensions = ['.ini', '.cfg', '.set', '.tpl']
            
            for config_location in config_locations:
                if config_location.exists():
                    for ext in config_extensions:
                        for config_file in config_location.glob(f"*{ext}"):
                            try:
                                stat = config_file.stat()
                                config_info = {
                                    'path': str(config_file),
                                    'name': config_file.name,
                                    'size': stat.st_size,
                                    'modified': datetime.fromtimestamp(stat.st_mtime),
                                    'type': ext,
                                    'content': None
                                }
                                
                                # Try to read configuration content
                                try:
                                    config_content = self.read_config_file(config_file)
                                    config_info['content'] = config_content
                                except Exception as e:
                                    config_info['read_error'] = str(e)
                                
                                config_files.append(config_info)
                                self.found_files['configs'].append(config_file)
                                
                            except Exception as e:
                                print(f"WARNING  Error processing config file {config_file}: {e}")
        
        return config_files
    
    def read_config_file(self, config_file: Path) -> Dict[str, Any]:
        """Read and parse configuration file"""
        config_data = {}
        
        try:
            if config_file.suffix.lower() == '.ini':
                # Try to parse as INI file
                config = configparser.ConfigParser()
                config.read(config_file, encoding='utf-8')
                
                for section in config.sections():
                    config_data[section] = dict(config[section])
            
            elif config_file.suffix.lower() in ['.set', '.cfg']:
                # Parse as key=value pairs
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            config_data[key.strip()] = value.strip()
            
            else:
                # Read as plain text
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    config_data['content'] = f.read()
        
        except Exception as e:
            config_data['error'] = str(e)
        
        return config_data
    
    def find_expert_advisors(self) -> List[Dict[str, Any]]:
        """Find Expert Advisor files and information"""
        experts = []
        
        for data_path in self.mt5_data_paths:
            # Common EA locations
            expert_locations = [
                data_path / "MQL5" / "Experts",
                data_path / "Experts",
                data_path / "MQL5" / "Indicators",
                data_path / "Indicators"
            ]
            
            for expert_location in expert_locations:
                if expert_location.exists():
                    # Find .ex5 (compiled) and .mq5 (source) files
                    for ext in ['.ex5', '.mq5', '.mqh']:
                        for expert_file in expert_location.glob(f"*{ext}"):
                            try:
                                stat = expert_file.stat()
                                expert_info = {
                                    'path': str(expert_file),
                                    'name': expert_file.name,
                                    'size': stat.st_size,
                                    'modified': datetime.fromtimestamp(stat.st_mtime),
                                    'type': 'Compiled EA' if ext == '.ex5' else 'Source Code' if ext == '.mq5' else 'Include File',
                                    'extension': ext
                                }
                                
                                # Try to extract metadata for .mq5 files
                                if ext == '.mq5':
                                    try:
                                        metadata = self.extract_mq5_metadata(expert_file)
                                        expert_info['metadata'] = metadata
                                    except Exception as e:
                                        expert_info['metadata_error'] = str(e)
                                
                                experts.append(expert_info)
                                self.found_files['experts'].append(expert_file)
                                
                            except Exception as e:
                                print(f"WARNING  Error processing expert file {expert_file}: {e}")
        
        return experts
    
    def extract_mq5_metadata(self, mq5_file: Path) -> Dict[str, Any]:
        """Extract metadata from MQ5 source file"""
        metadata = {
            'properties': {},
            'inputs': [],
            'functions': []
        }
        
        try:
            with open(mq5_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Extract property directives
                import re
                
                # Find #property directives
                property_pattern = r'#property\s+(\w+)\s+(.+)'
                for match in re.finditer(property_pattern, content):
                    prop_name = match.group(1)
                    prop_value = match.group(2).strip().strip('"')
                    metadata['properties'][prop_name] = prop_value
                
                # Find input parameters
                input_pattern = r'input\s+(\w+)\s+(\w+)\s*=\s*([^;]+);'
                for match in re.finditer(input_pattern, content):
                    input_type = match.group(1)
                    input_name = match.group(2)
                    input_default = match.group(3).strip()
                    metadata['inputs'].append({
                        'type': input_type,
                        'name': input_name,
                        'default': input_default
                    })
                
                # Find main functions
                function_pattern = r'(int|void|double|bool|string)\s+(\w+)\s*\([^{]*\)'
                for match in re.finditer(function_pattern, content):
                    return_type = match.group(1)
                    func_name = match.group(2)
                    if func_name in ['OnInit', 'OnDeinit', 'OnTick', 'OnTrade', 'OnTimer']:
                        metadata['functions'].append({
                            'name': func_name,
                            'type': return_type
                        })
        
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
    
    def find_database_files(self) -> List[Dict[str, Any]]:
        """Find database files (history, ticks, etc.)"""
        databases = []
        
        for data_path in self.mt5_data_paths:
            # Common database locations
            db_locations = [
                data_path / "history",
                data_path / "History",
                data_path / "bases",
                data_path / "Bases"
            ]
            
            for db_location in db_locations:
                if db_location.exists():
                    # Find database files
                    for db_file in db_location.rglob("*"):
                        if db_file.is_file():
                            try:
                                stat = db_file.stat()
                                db_info = {
                                    'path': str(db_file),
                                    'name': db_file.name,
                                    'size': stat.st_size,
                                    'modified': datetime.fromtimestamp(stat.st_mtime),
                                    'type': self._classify_database_file(db_file)
                                }
                                
                                databases.append(db_info)
                                self.found_files['databases'].append(db_file)
                                
                            except Exception as e:
                                print(f"WARNING  Error processing database file {db_file}: {e}")
        
        return databases
    
    def _classify_database_file(self, db_file: Path) -> str:
        """Classify database file type"""
        name_lower = db_file.name.lower()
        
        if db_file.suffix.lower() in ['.hst', '.hcc']:
            return 'History Data'
        elif db_file.suffix.lower() in ['.tick', '.tck']:
            return 'Tick Data'
        elif 'symbols' in name_lower:
            return 'Symbol Database'
        elif 'accounts' in name_lower:
            return 'Account Database'
        else:
            return 'Unknown Database'
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive MT5 data analysis report"""
        print("CHART Generating comprehensive MT5 data analysis report...")
        
        # Find all data directories
        data_dirs = self.find_mt5_data_directories()
        
        # Analyze each directory
        directory_structures = {}
        for data_dir in data_dirs:
            directory_structures[str(data_dir)] = self.scan_directory_structure(data_dir)
        
        # Find specific file types
        log_files = self.find_log_files()
        config_files = self.find_configuration_files()
        expert_files = self.find_expert_advisors()
        database_files = self.find_database_files()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'data_directories_found': len(data_dirs),
                'log_files_found': len(log_files),
                'config_files_found': len(config_files),
                'expert_files_found': len(expert_files),
                'database_files_found': len(database_files)
            },
            'data_directories': [str(d) for d in data_dirs],
            'directory_structures': directory_structures,
            'log_files': log_files,
            'configuration_files': config_files,
            'expert_advisors': expert_files,
            'database_files': database_files
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "mt5_data_analysis_report.json"):
        """Save analysis report to JSON file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                return obj
            
            report_serializable = convert_datetime(report)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_serializable, f, indent=2, ensure_ascii=False)
            
            print(f"OK Report saved to {filename}")
            
        except Exception as e:
            print(f"ERROR Failed to save report: {e}")

def main():
    """Main function"""
    print(" MT5 Data Explorer - Deep Analysis of MT5 Data Structure")
    print("=" * 70)
    
    explorer = MT5DataExplorer()
    
    try:
        # Generate comprehensive report
        report = explorer.generate_report()
        
        # Display summary
        print(f"\n ANALYSIS SUMMARY:")
        print(f"  Data Directories: {report['summary']['data_directories_found']}")
        print(f"  Log Files: {report['summary']['log_files_found']}")
        print(f"  Config Files: {report['summary']['config_files_found']}")
        print(f"  Expert Files: {report['summary']['expert_files_found']}")
        print(f"  Database Files: {report['summary']['database_files_found']}")
        
        # Show some interesting findings
        if report['log_files']:
            print(f"\n RECENT LOG ENTRIES:")
            for log_file in report['log_files'][:3]:  # Show first 3 log files
                print(f"   {log_file['name']} ({log_file['type']}):")
                for entry in log_file['recent_entries'][:2]:  # Show 2 recent entries
                    print(f"     {entry}")
        
        if report['expert_advisors']:
            print(f"\n EXPERT ADVISORS FOUND:")
            for expert in report['expert_advisors'][:5]:  # Show first 5
                print(f"   {expert['name']} ({expert['type']}) - {expert['size']} bytes")
                if 'metadata' in expert and 'properties' in expert['metadata']:
                    props = expert['metadata']['properties']
                    if 'version' in props:
                        print(f"    Version: {props['version']}")
                    if 'description' in props:
                        print(f"    Description: {props['description']}")
        
        # Save detailed report
        explorer.save_report(report)
        
        print(f"\nOK Analysis complete! Check 'mt5_data_analysis_report.json' for full details.")
        
    except Exception as e:
        print(f"ERROR Analysis failed: {e}")

if __name__ == "__main__":
    # Initialize ASCII-only output
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

    main()