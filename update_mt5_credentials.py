#!/usr/bin/env python3
"""
MT5 Credentials Update Script
Updates all files with new MT5 account credentials
"""

import os
import re
import json
import glob
from pathlib import Path

# Old and new credentials
OLD_CREDENTIALS = {
    'login': '95244786',
    'password': 'Ua@tOnLp', 
    'server': 'MetaQuotesDemo'
}

NEW_CREDENTIALS = {
    'login': '95244786',
    'password': 'Ua@tOnLp',
    'server': 'MetaQuotesDemo',
    'readonly_password': 'Oo-gKoOo'
}

def update_file_content(file_path, content):
    """Update file content with new credentials"""
    modified = False
    
    # Replace login number
    if OLD_CREDENTIALS['login'] in content:
        content = content.replace(OLD_CREDENTIALS['login'], NEW_CREDENTIALS['login'])
        modified = True
    
    # Replace password (be careful with special characters)
    if OLD_CREDENTIALS['password'] in content:
        content = content.replace(OLD_CREDENTIALS['password'], NEW_CREDENTIALS['password'])
        modified = True
    
    # Replace server name
    if OLD_CREDENTIALS['server'] in content:
        content = content.replace(OLD_CREDENTIALS['server'], NEW_CREDENTIALS['server'])
        modified = True
    
    # Additional patterns for server
    if 'MetaQuotesDemo' in content:
        content = content.replace('MetaQuotesDemo', 'MetaQuotesDemo')
        modified = True
        
    return content, modified

def update_json_file(file_path):
    """Special handling for JSON files"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        
        modified = False
        
        # Check if it's a dict and update recursively
        if isinstance(data, dict):
            def update_dict(d):
                nonlocal modified
                for key, value in d.items():
                    if isinstance(value, str):
                        if OLD_CREDENTIALS['login'] in value:
                            d[key] = value.replace(OLD_CREDENTIALS['login'], NEW_CREDENTIALS['login'])
                            modified = True
                        if OLD_CREDENTIALS['password'] in value:
                            d[key] = value.replace(OLD_CREDENTIALS['password'], NEW_CREDENTIALS['password'])
                            modified = True
                        if OLD_CREDENTIALS['server'] in value:
                            d[key] = value.replace(OLD_CREDENTIALS['server'], NEW_CREDENTIALS['server'])
                            modified = True
                    elif isinstance(value, dict):
                        update_dict(value)
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            if isinstance(item, str):
                                if OLD_CREDENTIALS['login'] in item:
                                    value[i] = item.replace(OLD_CREDENTIALS['login'], NEW_CREDENTIALS['login'])
                                    modified = True
                                if OLD_CREDENTIALS['password'] in item:
                                    value[i] = item.replace(OLD_CREDENTIALS['password'], NEW_CREDENTIALS['password'])
                                    modified = True
                                if OLD_CREDENTIALS['server'] in item:
                                    value[i] = item.replace(OLD_CREDENTIALS['server'], NEW_CREDENTIALS['server'])
                                    modified = True
                            elif isinstance(item, dict):
                                update_dict(item)
            
            update_dict(data)
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
            
    except (json.JSONDecodeError, UnicodeDecodeError):
        # If JSON parsing fails, treat as regular text file
        pass
    
    return False

def main():
    """Main update function"""
    
    print("🔄 MIKROBOT MT5 CREDENTIALS UPDATE")
    print("=" * 50)
    print(f"Old Account: {OLD_CREDENTIALS['login']} @ {OLD_CREDENTIALS['server']}")
    print(f"New Account: {NEW_CREDENTIALS['login']} @ {NEW_CREDENTIALS['server']}")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    files_updated = 0
    files_checked = 0
    
    # File patterns to check
    patterns = [
        "*.py",
        "*.json", 
        "*.md",
        "*.txt",
        "*.log",
        "*.bat"
    ]
    
    # Get all files matching patterns
    all_files = []
    for pattern in patterns:
        all_files.extend(glob.glob(str(project_root / "**" / pattern), recursive=True))
    
    # Remove duplicates and exclude certain directories
    exclude_dirs = ['.git', '__pycache__', '.venv', 'venv']
    unique_files = []
    for file_path in all_files:
        path_obj = Path(file_path)
        if not any(exclude_dir in path_obj.parts for exclude_dir in exclude_dirs):
            if file_path not in unique_files:
                unique_files.append(file_path)
    
    print(f"📁 Checking {len(unique_files)} files...")
    
    for file_path in unique_files:
        try:
            files_checked += 1
            
            # Handle JSON files specially
            if file_path.endswith('.json'):
                if update_json_file(file_path):
                    files_updated += 1
                    print(f"✅ Updated JSON: {Path(file_path).name}")
                continue
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except:
                    continue
            
            # Check if file contains old credentials
            has_old_creds = (OLD_CREDENTIALS['login'] in content or 
                           OLD_CREDENTIALS['password'] in content or 
                           OLD_CREDENTIALS['server'] in content or
                           'MetaQuotesDemo' in content)
            
            if has_old_creds:
                # Update content
                new_content, modified = update_file_content(file_path, content)
                
                if modified:
                    # Write updated content
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    files_updated += 1
                    print(f"✅ Updated: {Path(file_path).name}")
                    
        except Exception as e:
            print(f"⚠️  Error updating {file_path}: {e}")
    
    print("=" * 50)
    print(f"📊 UPDATE COMPLETE")
    print(f"   Files checked: {files_checked}")
    print(f"   Files updated: {files_updated}")
    print("=" * 50)
    
    # Create verification report
    verification_report = {
        "update_timestamp": "2025-08-05T23:42:00Z",
        "old_credentials": {
            "login": OLD_CREDENTIALS['login'],
            "server": OLD_CREDENTIALS['server']
        },
        "new_credentials": {
            "login": NEW_CREDENTIALS['login'],
            "server": NEW_CREDENTIALS['server']
        },
        "files_checked": files_checked,
        "files_updated": files_updated,
        "status": "completed"
    }
    
    with open(project_root / 'mt5_credentials_update_report.json', 'w') as f:
        json.dump(verification_report, f, indent=2)
    
    print("📄 Update report saved: mt5_credentials_update_report.json")
    
    return files_updated > 0

if __name__ == "__main__":
    main()