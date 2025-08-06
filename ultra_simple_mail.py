#!/usr/bin/env python3
import subprocess

def ultra_simple_test():
    """Ultra simple mail test"""
    print("📧 ULTRA SIMPLE MAIL TEST")
    
    # Try via command line
    message = "Hello from MIKROBOT - testing basic email delivery"
    cmd = f'echo "{message}" | mail -s "MIKROBOT Simple Test" markus@foxinthecode.fi'
    
    print(f"🔧 Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Command line mail sent!")
        else:
            print("❌ Command line mail failed")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    ultra_simple_test()