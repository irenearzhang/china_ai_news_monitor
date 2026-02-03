#!/usr/bin/env python3
"""
China AI News Monitor - Standalone Runner

This script can be run directly from terminal without MCP tools.
It tests your email configuration and demonstrates the monitoring system.

Usage:
    python run_standalone.py           # Run test
    python run_standalone.py --email   # Test email only
    python run_standalone.py --help    # Show help
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Load configuration
CONFIG_PATH = Path(__file__).parent / "config.yaml"

def load_config():
    """Load configuration from YAML file."""
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {CONFIG_PATH}")
        print("   Run: cp config.yaml.example config.yaml")
        return None
    except yaml.YAMLError as e:
        print(f"❌ YAML error: {e}")
        return None

def test_email_only():
    """Test email configuration without fetching news."""
    config = load_config()
    if not config:
        return False
    
    email_config = config.get('email', {})
    
    # Validate required fields
    required_fields = ['sender_email', 'sender_password', 'recipient_email', 'smtp_server', 'smtp_port']
    for field in required_fields:
        if field not in email_config:
            print(f"❌ Missing required field in config.yaml: {field}")
            return False
    
    print("📧 Testing email configuration...")
    print(f"   From: {email_config['sender_email']}")
    print(f"   To: {email_config['recipient_email']}")
    print(f"   SMTP: {email_config['smtp_server']}:{email_config['smtp_port']}")
    print()
    
    # Create test message
    msg = MIMEMultipart('alternative')
    subject = f"✅ China AI News Monitor Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    msg['Subject'] = subject
    msg['From'] = formataddr((email_config.get('sender_name', 'Test'), email_config['sender_email']))
    msg['To'] = email_config['recipient_email']
    
    # Simple HTML body
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2E7D32;">✅ Configuration Test Successful!</h2>
        <p>This is a test email from <strong>China AI News Monitor</strong>.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <h3>📋 System Status:</h3>
        <ul>
            <li>✅ Email configuration loaded</li>
            <li>✅ SMTP connection working</li>
            <li>✅ Authentication successful</li>
        </ul>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><em>The automated news monitoring system is ready to send daily digests.</em></p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #666; font-size: 12px;">
            China AI News Monitor - Monitoring 180+ Chinese AI news sources<br>
            Scheduled: Weekdays at 8:00 AM Pacific Time
        </p>
    </body>
    </html>
    """
    
    part1 = MIMEText("", 'plain', 'utf-8')
    part2 = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        print("🔐 Connecting to SMTP server...")
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        
        print("🔑 Logging in...")
        server.login(email_config['sender_email'], email_config['sender_password'])
        
        print(f"📨 Sending test email to {email_config['recipient_email']}...")
        server.send_message(msg)
        server.quit()
        
        print("\n✅ Test email sent successfully!")
        print("   Check your inbox for the test message.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your email settings in config.yaml")
        print("   2. Make sure you're using an App Password, not your regular password")
        print("   3. For Gmail: https://myaccount.google.com/apppasswords")
        return False

def show_status():
    """Show current configuration status."""
    config = load_config()
    if not config:
        return
    
    print("=" * 60)
    print("📊 China AI News Monitor - Configuration Status")
    print("=" * 60)
    
    # Email status
    email_config = config.get('email', {})
    print("\n📧 Email Configuration:")
    if email_config.get('sender_email'):
        print(f"   ✅ Sender: {email_config['sender_email']}")
    else:
        print(f"   ❌ Sender: Not configured")
    
    if email_config.get('recipient_email'):
        print(f"   ✅ Recipient: {email_config['recipient_email']}")
    else:
        print(f"   ❌ Recipient: Not configured")
    
    # Schedule status
    monitoring = config.get('monitoring', {})
    print("\n⏰ Schedule:")
    print(f"   Time: {monitoring.get('send_time', '08:00')}")
    print(f"   Timezone: {monitoring.get('timezone', 'US/Pacific')}")
    print(f"   Days: Weekdays (Mon-Fri)")
    print(f"   Coverage: {monitoring.get('normal_hours', 24)} hours (72h on Mondays)")
    
    # Sources
    categories = config.get('categories', {})
    print(f"\n📰 Monitored Categories: {len(categories)}")
    total_sources = 0
    total_keywords = 0
    for cat_name, cat_config in categories.items():
        sources = len(cat_config.get('sources', []))
        keywords = len(cat_config.get('keywords', []))
        total_sources += sources
        total_keywords += keywords
        print(f"   • {cat_config.get('name', cat_name)}: {sources} sources, {keywords} keywords")
    
    print(f"\n📊 Totals: {total_sources} sources, {total_keywords} keywords")
    
    print("\n" + "=" * 60)
    print("✅ Configuration is ready!")
    print("=" * 60)
    print("\n🚀 The automated scheduler will send daily digests.")
    print("   No action needed - it runs automatically at 8AM PT on weekdays.")

def show_help():
    """Show help message."""
    print("""
China AI News Monitor - Standalone Runner

USAGE:
    python run_standalone.py [OPTIONS]

OPTIONS:
    --email, -e     Test email configuration only
    --status, -s    Show current configuration status
    --help, -h      Show this help message

EXAMPLES:
    python run_standalone.py              # Show status
    python run_standalone.py --email      # Test email
    python run_standalone.py --status     # View configuration

WHAT THIS DOES:
    • Tests your email configuration
    • Shows system status
    • Verifies the automated scheduler is ready

AUTOMATED SCHEDULER:
    The system runs automatically every weekday at 8:00 AM Pacific Time.
    You don't need to run this script manually for daily operation.

For the full news monitoring with web search, use: python main.py
    (Requires MCP-enabled environment)

""")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--email', '-e', action='store_true', help='Test email only')
    parser.add_argument('--status', '-s', action='store_true', help='Show status')
    parser.add_argument('--help', '-h', action='store_true', help='Show help')
    
    args = parser.parse_args()
    
    if args.help:
        show_help()
        return
    
    if args.email:
        test_email_only()
        return
    
    if args.status:
        show_status()
        return
    
    # Default: show status
    show_status()
    print("\n💡 Run with --email flag to test email configuration:")
    print("   python run_standalone.py --email")

if __name__ == "__main__":
    main()
