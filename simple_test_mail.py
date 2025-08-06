#!/usr/bin/env python3
"""
Simple mail test to verify functionality
"""

from src.mikrobot_v2.notifications.mail_notifier import MailNotifier

def simple_test():
    """Send one simple test email"""
    
    print("📧 SIMPLE MAIL TEST")
    print("=" * 30)
    
    # Create notifier with correct email
    notifier = MailNotifier(recipient_email="markus@foxinthecode.fi")
    
    print(f"📬 Recipient: {notifier.recipient_email}")
    print(f"📤 Sender account: {notifier.sender_account}")
    
    # Send simple test
    subject = "MIKROBOT Test - Single Message"
    body = """This is a single test message from MIKROBOT.

Testing email delivery functionality.

If you receive this, the email system is working correctly.

Time sent: Just now"""
    
    print("\n📤 Sending test email...")
    success = notifier.send_mail_with_chart(subject, body)
    
    if success:
        print("✅ Email sent successfully!")
        print("📧 Check markus@foxinthecode.fi")
    else:
        print("❌ Email failed")
    
    print("\n" + "=" * 30)
    print("Done - sent ONLY one test message")

if __name__ == "__main__":
    simple_test()