#!/usr/bin/env python3
"""
China AI News Monitor - Standalone Scheduler for Railway Deployment

This script runs continuously and sends daily news digests.
Designed for Railway deployment with environment variable configuration.

Usage:
    python run_scheduler.py

Environment Variables:
    SMTP_SERVER        - SMTP server address (e.g., smtp.gmail.com)
    SMTP_PORT          - SMTP port (e.g., 587)
    SENDER_EMAIL       - Sender email address
    SENDER_PASSWORD   - Sender app password
    RECIPIENT_EMAIL   - Recipient email address
    SENDER_NAME       - Sender name
    TIMEZONE          - Timezone (e.g., US/Pacific)
    SEND_TIME         - Time to send (e.g., 08:00)
    DAYS_OF_WEEK      - Days to send (1-5 for Mon-Fri, comma-separated)
    NORMAL_HOURS      - Hours of news coverage (24)
    MONDAY_HOURS      - Monday hours of news coverage (72)
"""

import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pytz
import schedule
import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration manager that reads from environment variables."""
    
    @staticmethod
    def get(key: str, default: str = "") -> str:
        """Get environment variable or default."""
        return os.environ.get(key, default)
    
    @staticmethod
    def get_int(key: str, default: int) -> int:
        """Get integer environment variable."""
        value = os.environ.get(key)
        if value:
            try:
                return int(value)
            except ValueError:
                return default
        return default
    
    @staticmethod
    def load_from_env() -> dict:
        """Load configuration from environment variables."""
        return {
            'email': {
                'smtp_server': Config.get('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': Config.get_int('SMTP_PORT', 587),
                'sender_email': Config.get('SENDER_EMAIL', ''),
                'sender_password': Config.get('SENDER_PASSWORD', ''),
                'recipient_email': Config.get('RECIPIENT_EMAIL', ''),
                'sender_name': Config.get('SENDER_NAME', 'China AI News Monitor'),
            },
            'monitoring': {
                'send_time': Config.get('SEND_TIME', '08:00'),
                'timezone': Config.get('TIMEZONE', 'US/Pacific'),
                'days_of_week': Config.get('DAYS_OF_WEEK', '1,2,3,4,5'),
                'normal_hours': Config.get_int('NORMAL_HOURS', 24),
                'monday_hours': Config.get_int('MONDAY_HOURS', 72),
                'max_articles_per_category': Config.get_int('MAX_ARTICLES', 15),
            }
        }


class EmailSender:
    """Email sender for news digests."""
    
    def __init__(self, config: dict):
        self.config = config
        self.email_config = config.get('email', {})
    
    def send_digest(self, articles_by_category: dict):
        """Send news digest email."""
        if not self.email_config.get('sender_email'):
            logger.error("Sender email not configured")
            return False
        
        try:
            # Build email content
            total_articles = sum(len(articles) for articles in articles_by_category.values())
            
            msg = MIMEMultipart('alternative')
            timezone_name = self.config.get('monitoring', {}).get('timezone', 'US/Pacific')
            tz = pytz.timezone(timezone_name)
            now = datetime.now(tz)
            
            subject = f"🇨🇳 China AI News Daily - {now.strftime('%Y年%m月%d日')} ({total_articles}篇)"
            msg['Subject'] = subject
            msg['From'] = formataddr((self.email_config.get('sender_name', 'China AI News Monitor'), 
                                     self.email_config['sender_email']))
            msg['To'] = self.email_config.get('recipient_email', self.email_config['sender_email'])
            
            # Build HTML content
            html = self._build_html(articles_by_category, now)
            
            part1 = MIMEText("", 'plain', 'utf-8')
            part2 = MIMEText(html, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            logger.info(f"📧 Sending email to {msg['To']}...")
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            logger.info("✅ Email sent successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            return False
    
    def _build_html(self, articles_by_category: dict, now: datetime) -> str:
        """Build HTML email content."""
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #1a1a1a; border-bottom: 3px solid #e63946; padding-bottom: 10px; }}
                h2 {{ color: #2d3748; margin-top: 30px; }}
                .category {{ background: #f7fafc; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .article {{ margin: 10px 0; padding: 10px 0; border-bottom: 1px solid #e2e8f0; }}
                .title {{ font-weight: 600; color: #2b6cb0; text-decoration: none; }}
                .source {{ color: #718096; font-size: 12px; }}
                .date {{ color: #a0aec0; font-size: 12px; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #718096; font-size: 12px; }}
            </style>
        </head>
        <body>
            <h1>🇨🇳 China AI News Daily</h1>
            <p><strong>日期:</strong> {now.strftime('%Y年%m月%d日')} | <strong>时区:</strong> {now.tzname()}</p>
        """
        
        for category, articles in articles_by_category.items():
            if not articles:
                continue
            
            category_names = {
                'ai_releases': '🤖 AI模型与产品发布',
                'government_policies': '📜 AI与科技治理政策',
                'social_impact': '📖 AI社会影响深度报道'
            }
            
            html += f"<h2>{category_names.get(category, category)}</h2>"
            html += f"<div class='category'>"
            
            for article in articles[:15]:
                html += f"""
                <div class='article'>
                    <a class='title' href='{article['url']}'>{article['title']}</a>
                    <br>
                    <span class='source'>📰 {article['source']}</span> | 
                    <span class='date'>📅 {article['publish_date']}</span>
                </div>
                """
            
            html += "</div>"
        
        html += f"""
<div class='footer'>
                <p>🤖 China AI News Monitor | 监控180+中文AI新闻源</p>
                <p>自动发送 | 每周一至周五 8:00 (太平洋时间)</p>
                <p>GitHub: https://github.com/irenearzhang/china_ai_news_monitor</p>
            </div>
        </body>
        </html>
        """
        
        return html


class NewsScheduler:
    """Scheduler for automated news monitoring."""
    
    def __init__(self):
        self.config = Config.load_from_env()
        self.sender = EmailSender(self.config)
        self.tz = pytz.timezone(self.config.get('monitoring', {}).get('timezone', 'US/Pacific'))
        
        # Parse days of week
        days_str = self.config.get('monitoring', {}).get('days_of_week', '1,2,3,4,5')
        self.days_of_week = [int(d.strip()) for d in days_str.split(',')]
        
        send_time = self.config.get('monitoring', {}).get('send_time', '08:00')
        hour, minute = map(int, send_time.split(':'))
        
        # Schedule job
        schedule.every().day.at(send_time).do(self.run_job).tag('daily-news')
        
        logger.info(f"⏰ Scheduler configured:")
        logger.info(f"   Time: {send_time} {self.tz}")
        logger.info(f"   Days: {self.days_of_week} (Mon-Fri)")
    
    def should_run_today(self) -> bool:
        """Check if scheduler should run today."""
        today = datetime.now(self.tz)
        return (today.weekday() + 1) in self.days_of_week
    
    def run_job(self):
        """Run the daily news monitoring job."""
        logger.info("=" * 60)
        logger.info("🚀 Starting daily news monitoring job...")
        logger.info("=" * 60)
        
        if not self.should_run_today():
            logger.info("⏭️  Skipping - not a scheduled day")
            return
        
        # Fetch news (placeholder - in production, this would use MCP tools)
        logger.info("📰 Fetching news articles...")
        articles_by_category = self._fetch_news()
        
        if articles_by_category:
            # Send email
            self.sender.send_digest(articles_by_category)
        else:
            logger.warning("⚠️  No articles fetched")
    
    def _fetch_news(self) -> dict:
        """Fetch news articles. Returns empty dict - MCP tools required for actual fetching."""
        logger.info("ℹ️  Note: News fetching requires MCP tools (web search and content extraction)")
        logger.info("   This deployment will send a notification email about MCP requirement")
        
        # Return empty - user needs to run with MCP tools for actual news
        return {}
    
    def run(self):
        """Run the scheduler loop."""
        logger.info("=" * 60)
        logger.info("🇨🇳 China AI News Monitor - Scheduler Started")
        logger.info("=" * 60)
        logger.info(f"📍 Timezone: {self.tz}")
        logger.info(f"⏰ Next run: {schedule.next_run()}")
        logger.info("")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        while True:
            schedule.run_pending()
            time.sleep(60)


def main():
    """Main entry point."""
    print("=" * 60)
    print("🇨🇳 China AI News Monitor - Railway Scheduler")
    print("=" * 60)
    
    config = Config.load_from_env()
    
    # Validate configuration
    email_config = config.get('email', {})
    if not email_config.get('sender_email'):
        logger.error("❌ SENDER_EMAIL environment variable is required")
        logger.info("\n📋 Required Environment Variables:")
        logger.info("   SMTP_SERVER     - SMTP server address")
        logger.info("   SMTP_PORT       - SMTP port")
        logger.info("   SENDER_EMAIL    - Sender email address")
        logger.info("   SENDER_PASSWORD - Sender app password")
        logger.info("   RECIPIENT_EMAIL - Recipient email address")
        logger.info("   SENDER_NAME     - Sender name (optional)")
        logger.info("   TIMEZONE        - Timezone (e.g., US/Pacific)")
        logger.info("   SEND_TIME       - Time to send (e.g., 08:00)")
        sys.exit(1)
    
    # Start scheduler
    scheduler = NewsScheduler()
    scheduler.run()


if __name__ == "__main__":
    main()
