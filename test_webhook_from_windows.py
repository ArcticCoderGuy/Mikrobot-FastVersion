#!/usr/bin/env python3
"""
Test script for Windows to test Mac webhook connectivity
Copy this to Windows machine and run to test reverse connection
"""

import requests
import json
from datetime import datetime

def test_mac_connection():
    """Test connection from Windows to Mac"""
    
    mac_ip = "192.168.0.114"
    mac_port = 8000
    
    print(f"🖥️ Testing Windows → Mac connection")
    print(f"🍎 Mac target: {mac_ip}:{mac_port}")
    print("=" * 50)
    
    # Test basic connectivity
    try:
        url = f"http://{mac_ip}:{mac_port}/bridge/status"
        print(f"🌐 Testing Mac webhook status...")
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("✅ Mac webhook is reachable!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Mac webhook error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Mac webhook not running")
        print("   Start Django server on Mac first")
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test confirmation endpoint
    try:
        url = f"http://{mac_ip}:{mac_port}/bridge/webhook/mt5-confirmation"
        print(f"📨 Testing confirmation endpoint...")
        
        test_confirmation = {
            'signal_id': 'TEST_123',
            'ticket': 12345,
            'deal': 12345,
            'status': 'EXECUTED',
            'execution_time': datetime.now().isoformat(),
            'price': 1.0850,
            'volume': 0.01
        }
        
        response = requests.post(url, json=test_confirmation, timeout=5)
        
        if response.status_code == 200:
            print("✅ Confirmation endpoint works!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Confirmation error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Confirmation test error: {e}")
    
    print("\n🔥 Windows → Mac connectivity test complete!")

if __name__ == "__main__":
    test_mac_connection()