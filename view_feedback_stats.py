#!/usr/bin/env python3
"""
View ML Learning Statistics
============================

Shows Pass/Fail feedback stats and ML learning progress
"""

import sqlite3
from datetime import datetime
import json

def view_stats():
    """Display feedback statistics"""
    
    try:
        conn = sqlite3.connect('mikrobot_feedback.db')
        cursor = conn.cursor()
        
        print("🧠 MIKROBOT ML LEARNING STATISTICS")
        print("=" * 50)
        
        # Overall stats
        cursor.execute('''
            SELECT 
                COUNT(*) as total_signals,
                SUM(CASE WHEN feedback = 'PASS' THEN 1 ELSE 0 END) as passes,
                SUM(CASE WHEN feedback = 'FAIL' THEN 1 ELSE 0 END) as fails
            FROM signal_feedback
        ''')
        
        total_row = cursor.fetchone()
        if total_row and total_row[0] > 0:
            total, passes, fails = total_row
            pass_rate = (passes / total) * 100
            
            print(f"📊 OVERALL PERFORMANCE:")
            print(f"   Total Signals: {total}")
            print(f"   ✅ Passes: {passes}")
            print(f"   ❌ Fails: {fails}")
            print(f"   📈 Pass Rate: {pass_rate:.1f}%")
            print()
        
        # Per-symbol stats
        cursor.execute('SELECT * FROM learning_stats ORDER BY pass_rate DESC, total_signals DESC')
        symbol_stats = cursor.fetchall()
        
        if symbol_stats:
            print("📈 SYMBOL PERFORMANCE:")
            print("-" * 50)
            print(f"{'Symbol':<8} {'Total':<6} {'Pass':<5} {'Fail':<5} {'Rate':<6} {'Status'}")
            print("-" * 50)
            
            for row in symbol_stats:
                symbol, total, passes, fails, rate, updated = row
                
                if total >= 5:
                    if rate >= 80:
                        status = "🔥 EXCELLENT"
                    elif rate >= 60:
                        status = "✅ GOOD"
                    elif rate >= 40:
                        status = "⚠️ AVERAGE"
                    else:
                        status = "❌ POOR"
                else:
                    status = "📊 LEARNING"
                
                print(f"{symbol:<8} {total:<6} {passes:<5} {fails:<5} {rate:<6.1f} {status}")
        else:
            print("📊 No learning data yet - start sending feedback!")
        
        print()
        
        # Recent feedback
        cursor.execute('''
            SELECT symbol, feedback, timestamp, feedback_time 
            FROM signal_feedback 
            ORDER BY feedback_time DESC 
            LIMIT 10
        ''')
        
        recent = cursor.fetchall()
        if recent:
            print("🕐 RECENT FEEDBACK:")
            print("-" * 40)
            for symbol, feedback, sig_time, fb_time in recent:
                fb_datetime = datetime.fromisoformat(fb_time)
                print(f"   {symbol}: {feedback} ({fb_datetime.strftime('%H:%M:%S')})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading stats: {e}")
        print("💡 Make sure to run the scanner first to create the database!")

def main():
    """Main stats viewer"""
    
    print("🔍 MIKROBOT ML LEARNING VIEWER")
    print("=" * 35)
    print()
    
    view_stats()
    
    print("\n💡 USAGE:")
    print("Reply to signal iMessages with:")
    print("   'Pass EURUSD' = Good signal")
    print("   'Fail GBPJPY' = Bad signal")
    print("\n🔄 Run this script anytime to see ML progress!")

if __name__ == "__main__":
    main()