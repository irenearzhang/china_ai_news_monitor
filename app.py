#!/usr/bin/env python3
"""
China AI News Monitor - Railway Deployment

A Flask web app with scheduled news monitoring.
Railway requires a web server, so we provide one that runs the scheduler in background.

Environment Variables:
    SMTP_SERVER        - SMTP server address (e.g., smtp.gmail.com)
    SMTP_PORT          - SMTP port (e.g., 587)
    SENDER_EMAIL       - Sender email address
    SENDER_PASSWORD   - Sender app password
    RECIPIENT_EMAIL   - Recipient email address
    SENDER_NAME       - Sender name
    TIMEZONE          - Timezone (e.g., US/Pacific)
    SEND_TIME         - Time to send (e.g., 08:00)
"""

import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pytz
import json
import schedule
import yaml
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Admin API key for protected endpoints
ADMIN_API_KEY = os.environ.get('ADMIN_API_KEY', '')

# Articles cache
ARTICLES_CACHE_FILE = Path(__file__).parent / 'data' / 'latest_articles.json'

def load_cached_articles() -> dict:
    """Load articles from cache file."""
    if ARTICLES_CACHE_FILE.exists():
        try:
            with open(ARTICLES_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading articles cache: {e}")
    return {}

def require_api_key(f):
    """Decorator to require API key for admin endpoints."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not ADMIN_API_KEY:
            return jsonify({'error': 'API key not configured on server'}), 500

        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            provided_key = auth_header[7:]
        else:
            provided_key = request.args.get('api_key', '')

        if provided_key != ADMIN_API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401

        return f(*args, **kwargs)
    return decorated

# Subscribers storage
SUBSCRIBERS_FILE = Path(__file__).parent / 'data' / 'subscribers.json'

def load_subscribers() -> list:
    """Load subscribers from JSON file."""
    if SUBSCRIBERS_FILE.exists():
        with open(SUBSCRIBERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_subscribers(subscribers: list):
    """Save subscribers to JSON file."""
    SUBSCRIBERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump(subscribers, f, indent=2)

# Configuration
class Config:
    @staticmethod
    def get(key: str, default: str = "") -> str:
        return os.environ.get(key, default)
    
    @staticmethod
    def get_int(key: str, default: int) -> int:
        value = os.environ.get(key)
        return int(value) if value else default
    
    @staticmethod
    def load() -> dict:
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
            }
        }


class EmailSender:
    def __init__(self, config: dict):
        self.config = config
        self.email_config = config.get('email', {})
    
    def send_digest(self, articles_by_category: dict = None):
        """Send news digest email to all active subscribers via SendGrid API."""
        if not self.email_config.get('sender_email'):
            return False, "Sender email not configured"

        api_key = self.email_config.get('sender_password')  # API key stored here
        if not api_key:
            return False, "SendGrid API key not configured"

        # Get all recipients: subscribers + fallback to RECIPIENT_EMAIL
        subscribers = load_subscribers()
        active_emails = [s['email'] for s in subscribers if s.get('active', True)]

        # Add fallback recipient if no subscribers
        fallback = self.email_config.get('recipient_email')
        if fallback and fallback not in active_emails:
            active_emails.append(fallback)

        if not active_emails:
            return False, "No recipients configured"

        try:
            tz = pytz.timezone(self.config.get('monitoring', {}).get('timezone', 'US/Pacific'))
            now = datetime.now(tz)
            subject = f"🇨🇳 China AI News Daily - {now.strftime('%Y年%m月%d日')}"
            html = self._build_html(now)

            sg = SendGridAPIClient(api_key)
            sent_count = 0
            errors = []

            # Send to each subscriber individually
            for recipient in active_emails:
                try:
                    message = Mail(
                        from_email=Email(self.email_config['sender_email'],
                                        self.email_config.get('sender_name', 'China AI News Monitor')),
                        to_emails=To(recipient),
                        subject=subject,
                        html_content=html
                    )
                    response = sg.send(message)
                    if response.status_code in [200, 201, 202]:
                        sent_count += 1
                    else:
                        errors.append(f"{recipient}: HTTP {response.status_code}")
                except Exception as e:
                    errors.append(f"{recipient}: {str(e)}")

            if errors:
                return True, f"Sent to {sent_count}/{len(active_emails)} recipients. Errors: {errors}"
            return True, f"Email sent to {sent_count} subscriber(s)"

        except Exception as e:
            return False, str(e)
    
    def _build_html(self, now: datetime) -> str:
        """Build HTML email with articles from cache."""
        articles = load_cached_articles()

        # Category display names and icons
        category_info = {
            'ai_releases': ('🤖 New AI Model & Product Releases', '#e63946'),
            'government_policies': ('📜 AI & Technology Governance Policies', '#1d3557'),
            'social_impact': ('📖 Long Reads: Social Impact of AI', '#2a9d8f')
        }

        # Build article sections
        sections_html = ""
        total_articles = 0

        for category_key, (category_name, color) in category_info.items():
            category_articles = articles.get(category_key, [])
            total_articles += len(category_articles)

            sections_html += f'''
            <div style="margin: 20px 0;">
                <h2 style="color: {color}; border-bottom: 2px solid {color}; padding-bottom: 8px;">
                    {category_name}
                </h2>
            '''

            if category_articles:
                for article in category_articles[:10]:  # Limit to 10 per category
                    title = article.get('title', 'Untitled')
                    url = article.get('url', '#')
                    source = article.get('source', 'Unknown')
                    summary = article.get('summary', '')[:200] + '...' if article.get('summary') else ''

                    sections_html += f'''
                    <div style="margin: 12px 0; padding: 10px; background: #f8f9fa; border-radius: 6px;">
                        <a href="{url}" style="color: #1a1a1a; text-decoration: none; font-weight: bold; font-size: 15px;">
                            {title}
                        </a>
                        <div style="color: #666; font-size: 12px; margin-top: 4px;">
                            📰 {source}
                        </div>
                        {f'<p style="color: #444; font-size: 13px; margin: 8px 0 0 0;">{summary}</p>' if summary else ''}
                    </div>
                    '''
            else:
                sections_html += '<p style="color: #999; font-style: italic;">No articles in this category today.</p>'

            sections_html += '</div>'

        return f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; background: #ffffff;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 3px solid #e63946;">
                <h1 style="color: #1a1a1a; margin: 0;">🇨🇳 China AI News Daily</h1>
                <p style="color: #666; margin: 8px 0 0 0;">{now.strftime('%Y年%m月%d日')} · {total_articles} articles</p>
            </div>

            {sections_html}

            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center;">
                <p style="color: #666; font-size: 12px;">
                    Automated daily digest from 180+ Chinese AI news sources<br>
                    <a href="https://github.com/irenearzhang/china_ai_news_monitor" style="color: #e63946;">GitHub</a> ·
                    <a href="https://china-ai-news-monitor.onrender.com" style="color: #e63946;">Subscribe</a>
                </p>
            </div>
        </body>
        </html>
        """


class Scheduler:
    def __init__(self):
        self.config = Config.load()
        self.sender = EmailSender(self.config)
        self.tz = pytz.timezone(self.config.get('monitoring', {}).get('timezone', 'US/Pacific'))
        self.running = True
        self.last_run = None
        self.last_status = None
        
        send_time = self.config.get('monitoring', {}).get('send_time', '08:00')
        schedule.every().day.at(send_time).do(self.run_job)
    
    def run_job(self):
        """Run daily news monitoring."""
        print(f"[{datetime.now()}] Running scheduled job...")
        self.last_run = datetime.now()
        
        # Note: This would normally fetch news from web
        # For Railway, we send a notification that news fetching requires MCP tools
        success, message = self.sender.send_digest()
        self.last_status = message
        print(f"[{datetime.now()}] Job completed: {message}")
    
    def start(self):
        """Start scheduler in background thread."""
        def loop():
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        print(f"Scheduler started. Next run: {schedule.next_run()}")


# Initialize
config = Config.load()
scheduler = Scheduler()
scheduler.start()


# Flask Routes
@app.route('/')
def index():
    """Serve the subscription landing page."""
    return send_file('index.html')


@app.route('/api/info')
def info():
    """Service info endpoint."""
    return jsonify({
        'status': 'running',
        'service': 'China AI News Monitor',
        'scheduler': 'active',
        'next_run': str(schedule.next_run()),
        'last_run': str(scheduler.last_run) if scheduler.last_run else None,
        'last_status': scheduler.last_status,
        'timezone': config.get('monitoring', {}).get('timezone', 'US/Pacific'),
        'send_time': config.get('monitoring', {}).get('send_time', '08:00'),
    })


@app.route('/health')
def health():
    """Health check for Railway."""
    return jsonify({'status': 'healthy'})


@app.route('/trigger', methods=['POST'])
def trigger():
    """Manually trigger news digest."""
    if scheduler.running:
        scheduler.run_job()
        return jsonify({'status': 'triggered', 'message': scheduler.last_status})
    return jsonify({'status': 'error', 'message': 'Scheduler not running'}), 500


@app.route('/status')
def status():
    """Get scheduler status."""
    return jsonify({
        'running': scheduler.running,
        'next_run': str(schedule.next_run()),
        'last_run': str(scheduler.last_run) if scheduler.last_run else None,
        'last_status': scheduler.last_status,
    })


@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Subscribe an email to the newsletter."""
    data = request.get_json()

    if not data or not data.get('email'):
        return jsonify({'success': False, 'error': 'Email is required'}), 400

    email = data['email'].strip().lower()
    name = data.get('name', '').strip()

    # Basic email validation
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'error': 'Invalid email address'}), 400

    subscribers = load_subscribers()

    # Check for duplicate
    if any(s['email'] == email for s in subscribers):
        return jsonify({'success': False, 'error': 'This email is already subscribed'}), 409

    # Add new subscriber
    subscribers.append({
        'email': email,
        'name': name,
        'subscribed_at': datetime.now().isoformat(),
        'active': True
    })

    save_subscribers(subscribers)

    return jsonify({
        'success': True,
        'message': 'Successfully subscribed to China AI News Daily!'
    })


@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    """Unsubscribe an email from the newsletter."""
    data = request.get_json()

    if not data or not data.get('email'):
        return jsonify({'success': False, 'error': 'Email is required'}), 400

    email = data['email'].strip().lower()
    subscribers = load_subscribers()

    # Find and deactivate subscriber
    found = False
    for s in subscribers:
        if s['email'] == email:
            s['active'] = False
            s['unsubscribed_at'] = datetime.now().isoformat()
            found = True
            break

    if not found:
        return jsonify({'success': False, 'error': 'Email not found'}), 404

    save_subscribers(subscribers)

    return jsonify({
        'success': True,
        'message': 'Successfully unsubscribed'
    })


@app.route('/api/subscribers', methods=['GET'])
@require_api_key
def list_subscribers():
    """List all active subscribers (admin endpoint, requires API key)."""
    subscribers = load_subscribers()
    active = [s for s in subscribers if s.get('active', True)]
    return jsonify({
        'total': len(subscribers),
        'active': len(active),
        'subscribers': active
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
