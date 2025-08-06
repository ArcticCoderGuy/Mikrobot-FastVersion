"""
Mail Notification System for Lightning Bolt
===========================================

Sends email notifications with chart attachments
"""

import subprocess
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class MailNotifier:
    """
    macOS Mail notification system for Lightning Bolt phases
    """
    
    def __init__(self, recipient_email: Optional[str] = None, sender_account: str = "iCloud"):
        """
        Initialize Mail notifier
        
        Args:
            recipient_email: Email address to send to
            sender_account: Mail account to send from (iCloud or Paretobox)
        """
        self.recipient_email = recipient_email or "markus@foxinthecode.fi"  # Default email
        self.sender_account = sender_account
        self.enabled = True
        
        logger.info(f"📧 Mail Notifier initialized - Account: {sender_account}")
    
    def send_mail_with_chart(self, subject: str, message: str, 
                            chart_path: Optional[str] = None) -> bool:
        """
        Send email with optional chart attachment using macOS Mail
        """
        if not self.enabled:
            return False
        
        try:
            # Escape strings for AppleScript
            safe_subject = subject.replace('"', '\\"')
            safe_message = message.replace('"', '\\"').replace('\n', '\\r')
            
            if chart_path and os.path.exists(chart_path):
                # Email with attachment
                applescript = f'''
                tell application "Mail"
                    set newMessage to make new outgoing message with properties {{subject:"{safe_subject}", content:"{safe_message}", visible:false}}
                    
                    tell newMessage
                        make new to recipient with properties {{address:"{self.recipient_email}"}}
                        make new attachment with properties {{file name:POSIX file "{chart_path}"}} at after last paragraph
                    end tell
                    
                    -- Send the message
                    send newMessage
                end tell
                '''
                logger.info(f"📧 Sending email with chart: {os.path.basename(chart_path)}")
            else:
                # Text only email
                applescript = f'''
                tell application "Mail"
                    set newMessage to make new outgoing message with properties {{subject:"{safe_subject}", content:"{safe_message}", visible:false}}
                    
                    tell newMessage
                        make new to recipient with properties {{address:"{self.recipient_email}"}}
                    end tell
                    
                    send newMessage
                end tell
                '''
                logger.info(f"📧 Sending text-only email")
            
            # Execute AppleScript
            result = subprocess.run(['osascript', '-e', applescript],
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                logger.info(f"✅ Email sent to {self.recipient_email}")
                return True
            else:
                logger.error(f"❌ Email failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Email timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Email error: {e}")
            return False
    
    def notify_lightning_bolt(self, symbol: str, phase: int, phase_name: str,
                            price: float, confidence: float, chart_path: Optional[str] = None) -> bool:
        """
        Send Lightning Bolt notification via email
        """
        # Phase emojis
        phase_emojis = {
            1: "⚡",  # BOS
            2: "🔄",  # Retest
            3: "🚀"   # Entry
        }
        
        emoji = phase_emojis.get(phase, "📊")
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Email subject
        subject = f"⚡ LIGHTNING BOLT - {symbol} - Phase {phase}: {phase_name}"
        
        # Email body
        if phase == 1:
            body = f"""🔥 MIKROBOT LIGHTNING BOLT ALERT
            
PHASE 1: BREAK OF STRUCTURE DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: {symbol}
Price: {price:.5f}
Confidence: {confidence:.1%}
Time: {timestamp}

The Lightning Bolt pattern has been initiated!
BOS (Break of Structure) confirmed on M5 timeframe.

Next: Monitoring for Phase 2 (Retest on M1)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ML/MCP Pattern Recognition System
Professional Candlestick Chart Attached
"""
        
        elif phase == 2:
            body = f"""🔥 MIKROBOT LIGHTNING BOLT ALERT
            
PHASE 2: RETEST CONFIRMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: {symbol}
Retest Price: {price:.5f}
Confidence: {confidence:.1%}
Time: {timestamp}

Retest successful on M1 timeframe!
Pattern structure maintained.

Next: Preparing for Phase 3 (+0.6 Ylipip Entry)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ML/MCP Pattern Recognition System
Professional Candlestick Chart Attached
"""
        
        elif phase == 3:
            body = f"""🚀 MIKROBOT LIGHTNING BOLT - ENTRY SIGNAL!
            
PHASE 3: +0.6 YLIPIP ENTRY EXECUTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: {symbol}
Entry Price: {price:.5f}
Confidence: {confidence:.1%}
Time: {timestamp}

⚡ LIGHTNING BOLT PATTERN COMPLETE! ⚡

Trade Parameters:
• Entry: {price:.5f}
• Pattern: 3-Phase Lightning Bolt
• ML/MCP Confidence: 92%+

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Professional Candlestick Chart Attached
Trade Executed Successfully!
"""
        
        else:
            body = f"""📊 MIKROBOT ALERT
            
{phase_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Symbol: {symbol}
Price: {price:.5f}
Confidence: {confidence:.1%}
Time: {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chart Attached
"""
        
        return self.send_mail_with_chart(subject, body, chart_path)
    
    def test_notification(self) -> bool:
        """
        Send test email to verify Mail works
        """
        subject = "🔧 MIKROBOT Mail Test"
        body = f"""MIKROBOT EMAIL NOTIFICATION TEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Mail notification system online
📧 Sending from: {self.sender_account}
📬 Recipient: {self.recipient_email}
🕐 Time: {datetime.now().strftime('%H:%M:%S')}

Ready for Lightning Bolt alerts! ⚡

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is a test message from MIKROBOT
"""
        
        return self.send_mail_with_chart(subject, body)

# Global mail notifier
mail_notifier = MailNotifier()

# Convenience functions
def notify_bos_via_mail(symbol: str, price: float, confidence: float, chart_path: Optional[str] = None):
    """Send BOS notification via email"""
    return mail_notifier.notify_lightning_bolt(symbol, 1, "BOS_DETECTION", 
                                              price, confidence, chart_path)

def notify_retest_via_mail(symbol: str, price: float, confidence: float, chart_path: Optional[str] = None):
    """Send Retest notification via email"""
    return mail_notifier.notify_lightning_bolt(symbol, 2, "RETEST_CONFIRMATION",
                                              price, confidence, chart_path)

def notify_entry_via_mail(symbol: str, price: float, confidence: float, chart_path: Optional[str] = None):
    """Send Entry notification via email"""
    return mail_notifier.notify_lightning_bolt(symbol, 3, "YLIPIP_ENTRY",
                                              price, confidence, chart_path)