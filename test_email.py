#!/usr/bin/env python3
"""
Simple test script to verify email configuration is working.
"""

import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime

def test_email_config():
    """Test if email configuration is valid."""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print("❌ config.yaml not found!")
        return None
    except yaml.YAMLError as e:
        print(f"❌ YAML error: {e}")
        return None

def send_test_email(config):
    """Send a simple test email."""
    email_config = config.get('email', {})
    
    # Validate required fields
    required_fields = ['sender_email', 'sender_password', 'recipient_email', 'smtp_server', 'smtp_port']
    for field in required_fields:
        if field not in email_config:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Create test message
    msg = MIMEMultipart('alternative')
    subject = f"✅ China AI News Monitor Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg['Subject'] = subject
    msg['From'] = formataddr((email_config.get('sender_name', 'Test'), email_config['sender_email']))
    msg['To'] = email_config['recipient_email']
    
    # Simple HTML body
    html_content = f"""
    <html>
    <body>
        <h2>✅ Configuration Test Successful!</h2>
        <p>This is a test email from China AI News Monitor.</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Status:</strong> Email configuration is working correctly!</p>
        <hr>
        <p><em>The automated news monitoring system is ready to send daily digests.</em></p>
    </body>
    </html>
    """
    
    part1 = MIMEText("", 'plain', 'utf-8')
    part2 = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        print("📧 Connecting to SMTP server...")
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        
        print("🔐 Logging in...")
        server.login(email_config['sender_email'], email_config['sender_password'])
        
        print(f"📨 Sending email to {email_config['recipient_email']}...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 China AI News Monitor - Email Configuration Test")
    print("=" * 60)
    
    # Test configuration
    config = test_email_config()
    if not config:
        return
    
    print("✅ Configuration loaded successfully!")
    
    # Send test email
    if send_test_email(config):
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("Your email configuration is working correctly.")
        print("The automated scheduler will send daily news digests.")
    else:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)

if __name__ == "__main__":
    main()
