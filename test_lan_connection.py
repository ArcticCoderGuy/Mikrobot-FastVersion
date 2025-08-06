#!/usr/bin/env python3
"""
LAN CONNECTION TESTER
======================

Tests Mac ↔ Windows connection in same local network
Optimized for sub-millisecond trading execution
"""

import asyncio
import aiohttp
import time
import subprocess
import socket
from datetime import datetime

class LANConnectionTester:
    """Test LAN connectivity between Mac and Windows"""
    
    def __init__(self):
        # Network configuration for local testing
        self.mac_ip = self.get_local_ip()
        self.windows_ip = "192.168.0.100"  # Update with actual Windows IP
        self.windows_port = 8001
        
        print(f"🏠 LAN CONNECTION TESTER")
        print(f"🍎 Mac IP: {self.mac_ip}")
        print(f"🖥️ Windows Target: {self.windows_ip}:{self.windows_port}")
        print("=" * 50)
    
    def get_local_ip(self):
        """Get Mac's local IP address"""
        try:
            # Connect to external address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def test_ping(self):
        """Test basic ping connectivity"""
        print("🏓 Testing ping connectivity...")
        
        try:
            result = subprocess.run(
                ["ping", "-c", "3", self.windows_ip],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Extract average ping time
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'avg' in line:
                        parts = line.split('/')
                        if len(parts) >= 5:
                            avg_ping = parts[4]
                            print(f"✅ Ping successful - Average: {avg_ping}ms")
                            return True
                
                print("✅ Ping successful")
                return True
            else:
                print("❌ Ping failed")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Ping error: {e}")
            return False
    
    async def test_http_connectivity(self):
        """Test HTTP connection to Windows MT5 bridge"""
        print("🌐 Testing HTTP connectivity...")
        
        url = f"http://{self.windows_ip}:{self.windows_port}/status"
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(url) as response:
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000  # Convert to ms
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ HTTP connection successful")
                        print(f"   Latency: {latency:.2f}ms")
                        print(f"   Response: {data}")
                        return True
                    else:
                        print(f"❌ HTTP error: {response.status}")
                        return False
        
        except aiohttp.ClientConnectorError:
            print("❌ Connection refused - Windows MT5 bridge not running")
            print("   Start windows_mt5_executor.py on Windows machine")
            return False
        except asyncio.TimeoutError:
            print("❌ Connection timeout")
            return False
        except Exception as e:
            print(f"❌ HTTP error: {e}")
            return False
    
    async def test_trading_signal(self):
        """Test sending a trading signal"""
        print("📈 Testing trading signal transmission...")
        
        url = f"http://{self.windows_ip}:{self.windows_port}/execute"
        
        test_signal = {
            "symbol": "EURUSD",
            "action": "BUY",
            "volume": 0.01,
            "price": 1.0850,
            "stop_loss": 1.0800,
            "take_profit": 1.0900,
            "comment": "LAN_TEST",
            "magic": 99999,
            "signal_id": f"TEST_{int(time.time())}"
        }
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.post(url, json=test_signal) as response:
                    end_time = time.time()
                    latency = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Trading signal successful")
                        print(f"   Execution latency: {latency:.2f}ms")
                        print(f"   MT5 Response: {result}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Trading signal failed: {response.status}")
                        print(f"   Error: {error_text}")
                        return False
        
        except Exception as e:
            print(f"❌ Trading signal error: {e}")
            return False
    
    def measure_latency_series(self, count=10):
        """Measure latency over multiple requests"""
        print(f"⚡ Measuring latency over {count} requests...")
        
        latencies = []
        url = f"http://{self.windows_ip}:{self.windows_port}/status"
        
        async def single_request():
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as session:
                    start_time = time.time()
                    async with session.get(url) as response:
                        end_time = time.time()
                        if response.status == 200:
                            return (end_time - start_time) * 1000
            except:
                return None
        
        async def measure_all():
            tasks = [single_request() for _ in range(count)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if r is not None and not isinstance(r, Exception)]
        
        try:
            latencies = asyncio.run(measure_all())
            
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                min_latency = min(latencies)
                max_latency = max(latencies)
                
                print(f"📊 Latency Statistics:")
                print(f"   Average: {avg_latency:.2f}ms")
                print(f"   Minimum: {min_latency:.2f}ms") 
                print(f"   Maximum: {max_latency:.2f}ms")
                print(f"   Successful: {len(latencies)}/{count}")
                
                return avg_latency
            else:
                print("❌ No successful latency measurements")
                return None
                
        except Exception as e:
            print(f"❌ Latency measurement error: {e}")
            return None
    
    async def full_connectivity_test(self):
        """Run complete connectivity test suite"""
        print("🔍 RUNNING FULL LAN CONNECTIVITY TEST")
        print("=" * 50)
        
        results = {
            'ping': False,
            'http': False, 
            'trading_signal': False,
            'avg_latency': None
        }
        
        # Test 1: Ping
        results['ping'] = self.test_ping()
        print()
        
        # Test 2: HTTP Connectivity
        results['http'] = await self.test_http_connectivity()
        print()
        
        # Test 3: Trading Signal
        if results['http']:
            results['trading_signal'] = await self.test_trading_signal()
            print()
        
        # Test 4: Latency Analysis
        if results['http']:
            results['avg_latency'] = self.measure_latency_series()
            print()
        
        # Summary
        print("📊 CONNECTIVITY TEST SUMMARY:")
        print("-" * 30)
        print(f"🏓 Ping: {'✅ OK' if results['ping'] else '❌ FAIL'}")
        print(f"🌐 HTTP: {'✅ OK' if results['http'] else '❌ FAIL'}")
        print(f"📈 Trading: {'✅ OK' if results['trading_signal'] else '❌ FAIL'}")
        
        if results['avg_latency']:
            print(f"⚡ Avg Latency: {results['avg_latency']:.2f}ms")
            
            if results['avg_latency'] < 5:
                print("🔥 EXCELLENT - Sub-5ms latency!")
            elif results['avg_latency'] < 20:
                print("✅ GOOD - Low latency for trading")
            else:
                print("⚠️ OK - Higher latency than optimal")
        
        print()
        
        if all([results['ping'], results['http'], results['trading_signal']]):
            print("🎯 LAN CONNECTION: PERFECT FOR HIGH-FREQUENCY TRADING!")
            return True
        else:
            print("❌ LAN CONNECTION: NEEDS CONFIGURATION")
            return False

async def main():
    """Run LAN connectivity tests"""
    tester = LANConnectionTester()
    
    print("🚀 Starting LAN connectivity tests...")
    print("⚠️  Make sure Windows MT5 bridge is running first!")
    print()
    
    success = await tester.full_connectivity_test()
    
    if success:
        print("✅ LAN setup is READY for Mikrobot trading!")
        print("🔥 Ultra-low latency trading environment confirmed!")
    else:
        print("❌ LAN setup needs work before trading")
        print("📋 Check Windows MT5 bridge and network configuration")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit_code = 0 if result else 1
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        exit_code = 1
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        exit_code = 1
    
    exit(exit_code)