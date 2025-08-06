"""
iMessage Feedback Listener
==========================

Listens for your feedback messages: "Pass" or "Fail"
Improves ML pattern recognition based on your validation
"""

import sqlite3
import subprocess
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
import threading

logger = logging.getLogger(__name__)

class iMessageFeedbackListener:
    """
    Listen for iMessage feedback and learn from it
    """
    
    def __init__(self, database_path: str = "mikrobot_feedback.db"):
        self.db_path = database_path
        self.your_number = "+358440606044"
        self.running = False
        self.last_signals = {}  # Store recent signals for feedback matching
        
        self.init_database()
        logger.info("📱 iMessage Feedback Listener initialized")
    
    def init_database(self):
        """Initialize SQLite database for feedback storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symbol TEXT,
                signal_type TEXT,
                phase INTEGER,
                price REAL,
                confidence REAL,
                direction TEXT,
                feedback TEXT,  -- 'PASS' or 'FAIL'
                feedback_time TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_stats (
                symbol TEXT PRIMARY KEY,
                total_signals INTEGER DEFAULT 0,
                pass_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                pass_rate REAL DEFAULT 0.0,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("📊 Feedback database initialized")
    
    def store_signal(self, symbol: str, signal_data: dict) -> str:
        """Store signal for feedback matching"""
        signal_id = f"{symbol}_{int(time.time())}"
        self.last_signals[signal_id] = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'phase': signal_data.get('phase', 0),
            'price': signal_data.get('price', 0),
            'confidence': signal_data.get('confidence', 0),
            'direction': signal_data.get('direction', 'UNKNOWN'),
            'signal_type': 'LIGHTNING_BOLT'
        }
        
        # Keep only last 50 signals to avoid memory bloat
        if len(self.last_signals) > 50:
            oldest_key = min(self.last_signals.keys())
            del self.last_signals[oldest_key]
        
        return signal_id
    
    def get_latest_messages(self) -> List[Dict]:
        """Get latest iMessages using AppleScript"""
        try:
            # AppleScript to get recent messages
            applescript = f'''
            tell application "Messages"
                set recentMessages to {{}}
                set targetBuddy to buddy "{self.your_number}" of (1st service whose service type = iMessage)
                set recentChats to chats whose participants contains targetBuddy
                
                repeat with aChat in recentChats
                    set chatMessages to messages of aChat
                    set messageCount to count of chatMessages
                    
                    -- Get last 5 messages
                    if messageCount > 0 then
                        set startIndex to messageCount - 4
                        if startIndex < 1 then set startIndex to 1
                        
                        repeat with i from startIndex to messageCount
                            set msg to item i of chatMessages
                            set msgText to text of msg
                            set msgDate to date sent of msg
                            set msgService to service of msg
                            set recentMessages to recentMessages & {{text:msgText, date:msgDate, service:msgService}}
                        end repeat
                    end if
                end repeat
                
                return recentMessages
            end tell
            '''
            
            result = subprocess.run([
                'osascript', '-e', applescript
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse AppleScript output (basic parsing)
                messages = []
                output_lines = result.stdout.strip().split('\n')
                
                for line in output_lines:
                    if 'text:' in line:
                        # Extract message text (simplified parsing)
                        if 'pass' in line.lower() or 'fail' in line.lower():
                            messages.append({
                                'text': line.lower(),
                                'timestamp': datetime.now().isoformat()
                            })
                
                return messages
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
        
        return []
    
    def process_feedback_message(self, message_text: str) -> Optional[Dict]:
        """Process feedback message and extract Pass/Fail"""
        text = message_text.lower().strip()
        
        feedback = None
        symbol = None
        
        # Look for feedback keywords
        if 'pass' in text:
            feedback = 'PASS'
        elif 'fail' in text:
            feedback = 'FAIL'
        else:
            return None
        
        # Try to extract symbol (look for common forex pairs)
        common_symbols = [
            'eurusd', 'gbpusd', 'usdjpy', 'usdchf', 'audusd', 'usdcad', 'nzdusd',
            'eurjpy', 'eurgbp', 'eurchf', 'gbpjpy', 'audjpy', 'cadjpy',
            'btcusd', 'ethusd', 'xrpusd', 'linkusd', 'adausd'
        ]
        
        for sym in common_symbols:
            if sym in text:
                symbol = sym.upper()
                break
        
        return {
            'feedback': feedback,
            'symbol': symbol,
            'message': message_text,
            'timestamp': datetime.now().isoformat()
        }
    
    def match_feedback_to_signal(self, feedback_data: Dict) -> Optional[str]:
        """Match feedback to recent signal"""
        if not feedback_data.get('symbol'):
            return None
        
        symbol = feedback_data['symbol']
        
        # Find most recent signal for this symbol
        for signal_id, signal in reversed(self.last_signals.items()):
            if signal['symbol'] == symbol:
                return signal_id
        
        return None
    
    def store_feedback(self, signal_id: str, feedback_data: Dict):
        """Store feedback in database"""
        if signal_id not in self.last_signals:
            return
        
        signal = self.last_signals[signal_id]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Store detailed feedback
        cursor.execute('''
            INSERT INTO signal_feedback 
            (timestamp, symbol, signal_type, phase, price, confidence, direction, feedback, feedback_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            signal['timestamp'],
            signal['symbol'],
            signal['signal_type'],
            signal['phase'],
            signal['price'],
            signal['confidence'],
            signal['direction'],
            feedback_data['feedback'],
            feedback_data['timestamp']
        ))
        
        # Update learning stats
        cursor.execute('''
            INSERT OR REPLACE INTO learning_stats 
            (symbol, total_signals, pass_count, fail_count, pass_rate, last_updated)
            VALUES (
                ?,
                COALESCE((SELECT total_signals FROM learning_stats WHERE symbol = ?), 0) + 1,
                COALESCE((SELECT pass_count FROM learning_stats WHERE symbol = ?), 0) + ?,
                COALESCE((SELECT fail_count FROM learning_stats WHERE symbol = ?), 0) + ?,
                0.0,
                ?
            )
        ''', (
            signal['symbol'],
            signal['symbol'],
            signal['symbol'],
            1 if feedback_data['feedback'] == 'PASS' else 0,
            signal['symbol'],
            1 if feedback_data['feedback'] == 'FAIL' else 0,
            datetime.now().isoformat()
        ))
        
        # Update pass rate
        cursor.execute('''
            UPDATE learning_stats 
            SET pass_rate = CAST(pass_count AS REAL) / CAST(total_signals AS REAL) * 100.0
            WHERE symbol = ?
        ''', (signal['symbol'],))
        
        conn.commit()
        conn.close()
        
        logger.info(f"📊 Feedback stored: {signal['symbol']} - {feedback_data['feedback']}")
        
        # Remove processed signal
        del self.last_signals[signal_id]
    
    def get_learning_stats(self) -> Dict:
        """Get learning statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM learning_stats ORDER BY pass_rate DESC')
        stats = {}
        
        for row in cursor.fetchall():
            symbol = row[0]
            stats[symbol] = {
                'total_signals': row[1],
                'pass_count': row[2],
                'fail_count': row[3],
                'pass_rate': row[4],
                'last_updated': row[5]
            }
        
        conn.close()
        return stats
    
    def should_trust_signal(self, symbol: str, confidence: float) -> bool:
        """Decide if signal should be trusted based on learning"""
        stats = self.get_learning_stats()
        
        if symbol not in stats:
            # No history - trust if confidence > 75%
            return confidence > 0.75
        
        symbol_stats = stats[symbol]
        
        # If we have enough data, use pass rate
        if symbol_stats['total_signals'] >= 5:
            pass_rate = symbol_stats['pass_rate']
            
            # Adjust confidence threshold based on historical performance
            if pass_rate > 80:
                return confidence > 0.6  # Lower threshold for good performers
            elif pass_rate > 60:
                return confidence > 0.75  # Normal threshold
            else:
                return confidence > 0.9  # Higher threshold for poor performers
        
        # Not enough data - use default threshold
        return confidence > 0.75
    
    def listen_for_feedback(self):
        """Main feedback listening loop"""
        logger.info("👂 Starting iMessage feedback listener...")
        
        last_check = datetime.now()
        
        while self.running:
            try:
                # Get recent messages
                messages = self.get_latest_messages()
                
                for msg in messages:
                    msg_time = datetime.fromisoformat(msg['timestamp'])
                    if msg_time <= last_check:
                        continue
                    
                    # Process feedback
                    feedback = self.process_feedback_message(msg['text'])
                    if feedback:
                        signal_id = self.match_feedback_to_signal(feedback)
                        if signal_id:
                            self.store_feedback(signal_id, feedback)
                            
                            # Send confirmation
                            from ..notifications.imessage_notifier import imessage_notifier
                            
                            stats = self.get_learning_stats()
                            symbol_stats = stats.get(feedback['symbol'], {})
                            pass_rate = symbol_stats.get('pass_rate', 0)
                            
                            confirmation = f"""✅ FEEDBACK RECEIVED

📊 {feedback['symbol']}: {feedback['feedback']}
🧠 ML Learning updated
📈 Pass rate: {pass_rate:.1f}%

Thanks for the validation!
🎯 Future signals improved"""
                            
                            imessage_notifier.send_imessage(confirmation)
                            logger.info(f"📱 Feedback confirmation sent: {feedback['symbol']} {feedback['feedback']}")
                
                last_check = datetime.now()
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Feedback listener error: {e}")
                time.sleep(30)  # Wait longer on error
    
    def start_listener(self):
        """Start feedback listener in background thread"""
        self.running = True
        listener_thread = threading.Thread(target=self.listen_for_feedback)
        listener_thread.daemon = True
        listener_thread.start()
        logger.info("🎧 iMessage feedback listener started")
    
    def stop_listener(self):
        """Stop feedback listener"""
        self.running = False
        logger.info("🛑 iMessage feedback listener stopped")

# Global feedback listener instance
feedback_listener = iMessageFeedbackListener()

def start_feedback_system():
    """Start the feedback system"""
    feedback_listener.start_listener()

def store_signal_for_feedback(symbol: str, signal_data: dict) -> str:
    """Store signal and return ID for feedback matching"""
    return feedback_listener.store_signal(symbol, signal_data)

def get_signal_trust_score(symbol: str, confidence: float) -> bool:
    """Check if signal should be trusted based on learning"""
    return feedback_listener.should_trust_signal(symbol, confidence)