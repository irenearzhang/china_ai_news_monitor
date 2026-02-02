#!/usr/bin/env python3
"""
China AI News Monitor - Main Orchestration Script

This script coordinates the daily news monitoring and email delivery.
It can run as a one-time fetch or as a persistent scheduler.

Usage:
    python main.py                    # Run once and send email
    python main.py --schedule         # Run as persistent scheduler
    python main.py --test-email       # Test email configuration
    python main.py --help             # Show this help message
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import pytz
import schedule
import yaml

from news_fetcher import NewsFetcher, save_articles_to_file, load_articles_from_file
from email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('china_ai_news_monitor.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class NewsMonitor:
    """Main class for coordinating news monitoring and email delivery."""
    
    def __init__(self, config_path: str = None):
        """Initialize the news monitor."""
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config_path = config_path
        self.config = self._load_config()
        
        self.fetcher = NewsFetcher(config_path)
        self.sender = EmailSender(config_path)
        
        # Data directory for caching
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.articles_cache_file = self.data_dir / "latest_articles.json"
    
    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def _display_status(self, articles_dict: dict):
        """Display status of fetched articles."""
        total = sum(len(articles) for articles in articles_dict.values())
        categories = sum(1 for articles in articles_dict.values() if articles)
        
        print("\n" + "=" * 60)
        print("📊 Fetch Summary")
        print("=" * 60)
        print(f"  Total articles found: {total}")
        print(f"  Categories with news: {categories}")
        print("")
        
        for category, articles in articles_dict.items():
            if articles:
                category_name = articles[0].category
                print(f"  📁 {category_name}: {len(articles)} articles")
        
        print("=" * 60)
    
    def run_mcp_search(self, queries: list, display_text: str) -> dict:
        """
        Wrapper for MCP batch_web_search tool.
        
        This method should be called with the actual MCP tool function.
        """
        # This is a placeholder - the actual MCP tool will be injected
        raise NotImplementedError(
            "MCP tools must be provided. Use run_with_mcp_tools() instead."
        )
    
    def run_with_mcp_tools(self, batch_web_search_func, extract_content_func):
        """
        Run the complete news monitoring pipeline using MCP tools.
        
        Args:
            batch_web_search_func: MCP batch_web_search function
            extract_content_func: MCP extract_content_from_websites function
        """
        logger.info("=" * 60)
        logger.info("🚀 Starting China AI News Monitor")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Fetch news for all categories
            articles_dict = self.fetcher.run_daily_fetch(
                web_search_func=batch_web_search_func,
                extract_func=extract_content_func
            )
            
            # Step 2: Display status
            self._display_status(articles_dict)
            
            # Step 3: Save to cache
            save_articles_to_file(articles_dict, self.articles_cache_file)
            logger.info(f"Articles saved to {self.articles_cache_file}")
            
            # Step 4: Send email
            logger.info("\n📧 Sending email digest...")
            if self.sender.send_email(articles_dict):
                logger.info("✅ Email sent successfully!")
            else:
                logger.warning("⚠️  Email sending failed. Check logs for details.")
            
            # Summary
            elapsed = datetime.now() - start_time
            total_articles = sum(len(articles) for articles in articles_dict.values())
            
            print("\n" + "=" * 60)
            print("✅ Daily Monitoring Complete!")
            print("=" * 60)
            print(f"  ⏱️  Time elapsed: {elapsed.total_seconds():.1f} seconds")
            print(f"  📰 Total articles: {total_articles}")
            print(f"  📧 Email status: {'Sent' if self.sender.send_email(articles_dict) else 'Failed'}")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Error during monitoring: {e}")
            return False
    
    def run_manual_fetch(self):
        """
        Run a manual fetch using cached search functionality.
        
        Note: This requires MCP tools to be available.
        """
        logger.info("Manual fetch mode requires MCP tools integration.")
        logger.info("Please use run_with_mcp_tools() with proper MCP tool functions.")
        return False
    
    def run_scheduled_job(self, batch_web_search_func, extract_content_func):
        """
        Execute the scheduled job once.
        """
        logger.info("Running scheduled news monitoring job...")
        return self.run_with_mcp_tools(batch_web_search_func, extract_content_func)
    
    def test_email(self) -> bool:
        """Test email configuration."""
        logger.info("Testing email configuration...")
        return self.sender.test_connection()
    
    def show_config(self):
        """Display current configuration."""
        print("\n" + "=" * 60)
        print("📋 Configuration")
        print("=" * 60)
        
        # Email config (masked)
        email_config = self.config.get('email', {})
        print("\n📧 Email Configuration:")
        print(f"  SMTP Server: {email_config.get('smtp_server', 'Not set')}")
        print(f"  SMTP Port: {email_config.get('smtp_port', 'Not set')}")
        print(f"  Sender: {email_config.get('sender_email', 'Not set')}")
        print(f"  Recipient: {email_config.get('recipient_email', 'Not set')}")
        
        # Monitoring config
        monitoring = self.config.get('monitoring', {})
        print(f"\n⏰ Send Time: {monitoring.get('send_time', '08:00')}")
        print(f"  Timezone: {monitoring.get('timezone', 'US/Pacific')}")
        print(f"  Days: Weekdays only (Mon-Fri)")
        
        # Article age settings
        print(f"\n📅 Article Age Limits:")
        normal_hours = monitoring.get('normal_hours', 24)
        monday_hours = monitoring.get('monday_hours', 72)
        print(f"  Tuesday-Friday: Last {normal_hours} hours")
        print(f"  Monday: Last {monday_hours} hours (covers weekend)")
        
        print(f"  Max articles per category: {monitoring.get('max_articles_per_category', 10)}")
        
        # Categories
        print(f"\n📁 Categories:")
        for key, config in self.config.get('categories', {}).items():
            print(f"  - {config.get('name', key)} ({len(config.get('keywords', []))} keywords)")
        
        print("=" * 60 + "\n")
    
    def setup_credentials_interactive(self):
        """Interactive setup for email credentials."""
        print("\n" + "=" * 60)
        print("🔐 Email Configuration Setup")
        print("=" * 60)
        
        email_config = self.config.get('email', {})
        
        # SMTP Server
        smtp_server = input(f"SMTP Server [{email_config.get('smtp_server', 'smtp.gmail.com')}]: ").strip()
        if not smtp_server:
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
        
        # SMTP Port
        smtp_port = input(f"SMTP Port [{email_config.get('smtp_port', 587)}]: ").strip()
        if not smtp_port:
            smtp_port = email_config.get('smtp_port', 587)
        else:
            smtp_port = int(smtp_port)
        
        # Sender Email
        sender_email = input("Sender Email: ").strip()
        
        # Sender Password (App Password)
        import getpass
        sender_password = getpass.getpass("Sender Password (App Password): ")
        
        # Recipient Email
        recipient_email = input("Recipient Email: ").strip()
        
        # Update config
        self.config['email'] = {
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'sender_email': sender_email,
            'sender_password': sender_password,
            'recipient_email': recipient_email,
            'sender_name': email_config.get('sender_name', 'China AI News Monitor')
        }
        
        # Save config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, sort_keys=False)
        
        print("\n✅ Configuration saved!")
        print("\n📝 Note: For Gmail, you'll need to use an App Password:")
        print("   1. Go to https://myaccount.google.com/security")
        print("   2. Enable 2-Factor Authentication")
        print("   3. Create an App Password for 'Mail'")


def run_scheduler(monitor: NewsMonitor, batch_web_search_func, extract_content_func):
    """Run the scheduler loop with weekday-only scheduling at 8AM PT."""
    monitoring_config = monitor.config.get('monitoring', {})
    send_time = monitoring_config.get('send_time', '08:00')
    timezone_name = monitoring_config.get('timezone', 'US/Pacific')
    days_of_week = monitoring_config.get('days_of_week', [1, 2, 3, 4, 5])  # Monday=1, Friday=5
    
    try:
        tz = pytz.timezone(timezone_name)
    except pytz.UnknownTimeZoneError:
        logger.warning(f"Unknown timezone {timezone_name}, using US/Pacific")
        tz = pytz.timezone('US/Pacific')
    
    logger.info(f"Scheduler started. Daily digest will be sent at {send_time} {timezone_name}")
    logger.info(f"Will only run on weekdays: {days_of_week} (Monday=1, Friday=5)")
    logger.info("Press Ctrl+C to stop")
    
    # Schedule the job to run on specified weekdays
    # schedule library uses 0-6 for Monday-Sunday, we need to convert
    # Our config uses 1-5 for Monday-Friday
    def should_run_today():
        """Check if today is a scheduled day."""
        now = datetime.now(tz)
        # Python weekday(): Monday=0, Sunday=6
        # Convert to our format: Monday=1, Sunday=7
        today_code = now.weekday() + 1
        return today_code in days_of_week
    
    def scheduled_job():
        """Run the job if it's a scheduled day."""
        if should_run_today():
            logger.info("Running scheduled news monitoring job...")
            monitor.run_scheduled_job(batch_web_search_func, extract_content_func)
        else:
            logger.info(f"Today is not a scheduled day, skipping...")
    
    # Schedule the job
    schedule.every().day.at(send_time).do(scheduled_job)
    
    # Check if we should run today, if so run immediately
    if should_run_today():
        logger.info("Running initial fetch...")
        monitor.run_scheduled_job(batch_web_search_func, extract_content_func)
    else:
        logger.info(f"Today is not a scheduled day, skipping initial fetch")
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="China AI News Monitor - Daily Email Digest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Run once and send email
  python main.py --schedule               # Run as persistent scheduler
  python main.py --test-email             # Test email configuration
  python main.py --setup                  # Interactive email setup
  python main.py --config                 # Show current configuration

Requirements:
  - MCP tools must be available for web search and content extraction
  - Email credentials must be configured in config.yaml
        """
    )
    
    parser.add_argument(
        '--schedule', '-s',
        action='store_true',
        help='Run as persistent scheduler'
    )
    parser.add_argument(
        '--test-email', '-t',
        action='store_true',
        help='Test email configuration'
    )
    parser.add_argument(
        '--setup', '-i',
        action='store_true',
        help='Interactive email configuration setup'
    )
    parser.add_argument(
        '--config', '-c',
        action='store_true',
        help='Show current configuration'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize monitor
    try:
        monitor = NewsMonitor()
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        sys.exit(1)
    
    # Handle commands
    if args.config:
        monitor.show_config()
        return
    
    if args.setup:
        monitor.setup_credentials_interactive()
        return
    
    if args.test_email:
        success = monitor.test_email()
        sys.exit(0 if success else 1)
    
    if args.schedule:
        logger.info("Scheduler mode requires MCP tool integration.")
        logger.info("Please check the documentation for proper setup.")
        print("\n⚠️  Scheduler mode requires MCP tools.")
        print("   Please run this script with proper MCP tool integration.")
        return
    
    # Default: Run once
    print("""
⚠️  Running requires MCP tool integration.

To use this tool, you need to run it within an MCP-enabled environment
or call the run_with_mcp_tools() method with proper MCP functions.

For standalone usage, please check the documentation for:
1. Setting up MCP tools
2. Configuring email credentials
3. Running as a scheduled job

Quick setup:
  1. Edit config.yaml with your email settings
  2. Run: python main.py --setup (interactive setup)
  3. Run: python main.py --test-email (test configuration)
  4. Integrate with your MCP environment
""")


if __name__ == "__main__":
    main()
