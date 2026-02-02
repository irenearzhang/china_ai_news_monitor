"""
China AI News Monitor - Email Sender Module

This module handles generating and sending HTML email digests.
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from news_fetcher import Article

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailSender:
    """Handles email composition and sending."""
    
    def __init__(self, config_path: str = None):
        """Initialize the email sender with configuration."""
        if config_path is None:
            config_path = Path(__file__).parent / "config.yaml"
        
        self.config = self._load_config(config_path)
        self.email_config = self.config.get('email', {})
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def _get_email_template(self) -> str:
        """Get the HTML email template."""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>China AI News Daily</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            padding: 30px 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            border-radius: 12px 12px 0 0;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }
        .header .date {
            margin-top: 10px;
            font-size: 14px;
            opacity: 0.8;
        }
        .content {
            background: white;
            padding: 30px;
            border-radius: 0 0 12px 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .category {
            margin: 30px 0;
        }
        .category:first-child {
            margin-top: 0;
        }
        .category-header {
            display: flex;
            align-items: center;
            padding-bottom: 15px;
            border-bottom: 2px solid #1a1a2e;
            margin-bottom: 20px;
        }
        .category-icon {
            font-size: 24px;
            margin-right: 10px;
        }
        .category-title {
            font-size: 20px;
            font-weight: 600;
            color: #1a1a2e;
        }
        .article {
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        .article:last-child {
            border-bottom: none;
        }
        .article-title {
            font-size: 16px;
            font-weight: 500;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        .article-title a {
            color: #3498db;
            text-decoration: none;
        }
        .article-title a:hover {
            text-decoration: underline;
        }
        .article-meta {
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 8px;
        }
        .article-summary {
            font-size: 14px;
            color: #555;
            line-height: 1.5;
        }
        .article-keywords {
            margin-top: 8px;
        }
        .keyword-tag {
            display: inline-block;
            background: #e8f4f8;
            color: #2980b9;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-right: 5px;
        }
        .trust-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 10px;
        }
        .trust-high {
            background: #d5f5e3;
            color: #27ae60;
        }
        .trust-medium {
            background: #fdebd0;
            color: #e67e22;
        }
        .footer {
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #7f8c8d;
            border-top: 1px solid #eee;
            margin-top: 30px;
        }
        .no-articles {
            text-align: center;
            color: #7f8c8d;
            padding: 20px;
            font-style: italic;
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            font-size: 13px;
        }
        .stat-item {
            text-align: center;
        }
        .stat-number {
            font-size: 24px;
            font-weight: 600;
            color: #3498db;
        }
        .stat-label {
            color: #7f8c8d;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🇨🇳 China AI News Daily</h1>
        <div class="date">{date}</div>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_articles}</div>
                <div class="stat-label">Articles</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{categories_count}</div>
                <div class="stat-label">Categories</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{sources_count}</div>
                <div class="stat-label">Sources</div>
            </div>
        </div>
    </div>
    
    <div class="content">
        {articles_content}
    </div>
    
    <div class="footer">
        <p>This daily digest is automatically generated by China AI News Monitor.</p>
        <p>Sources include: 36氪, 量子位, 机器之心, 新华社, 人民网, 财新, 南方周末, and other reputable Chinese media.</p>
        <p>© {year} China AI News Monitor. All rights reserved.</p>
    </div>
</body>
</html>"""
    
    def _format_date(self, date_obj: datetime) -> str:
        """Format date in Chinese format."""
        return date_obj.strftime("%Y年%m月%d日 %A").replace("Monday", "星期一").replace("Tuesday", "星期二").replace("Wednesday", "星期三").replace("Thursday", "星期四").replace("Friday", "星期五").replace("Saturday", "星期六").replace("Sunday", "星期日")
    
    def _get_trust_badge(self, score: float) -> str:
        """Get trust score badge HTML."""
        if score >= 0.9:
            return '<span class="trust-badge trust-high">高可信度</span>'
        elif score >= 0.7:
            return '<span class="trust-badge trust-medium">中可信度</span>'
        else:
            return '<span class="trust-badge">一般来源</span>'
    
    def _generate_articles_html(self, articles_dict: Dict[str, List[Article]]) -> str:
        """Generate HTML for all articles."""
        html_parts = []
        total_articles = 0
        categories_with_articles = 0
        
        for category_name, articles in articles_dict.items():
            if not articles:
                continue
            
            categories_with_articles += 1
            total_articles += len(articles)
            
            # Get category display name
            category_display = articles[0].category if articles else category_name
            
            # Extract emoji from category name
            emoji = ""
            if "🤖" in category_display:
                emoji = "🤖"
            elif "📜" in category_display:
                emoji = "📜"
            elif "📖" in category_display:
                emoji = "📖"
            
            category_html = f"""
        <div class="category">
            <div class="category-header">
                <span class="category-icon">{emoji}</span>
                <span class="category-title">{category_display}</span>
            </div>
"""
            for article in articles:
                date_str = article.publish_date.strftime("%m月%d日 %H:%M") if article.publish_date else "刚刚"
                
                # Keywords tags
                keywords_html = ""
                if article.keywords_matched:
                    keywords_html = '<div class="article-keywords">' + ' '.join([
                        f'<span class="keyword-tag">{kw}</span>' 
                        for kw in article.keywords_matched[:3]
                    ]) + '</div>'
                
                article_html = f"""
            <div class="article">
                <div class="article-title">
                    <a href="{article.url}" target="_blank">{article.title}</a>
                    {self._get_trust_badge(article.trust_score)}
                </div>
                <div class="article-meta">
                    📰 {article.source} &nbsp;|&nbsp; 📅 {date_str}
                </div>
                {keywords_html}
            </div>
"""
                category_html += article_html
            
            category_html += "        </div>"
            html_parts.append(category_html)
        
        if not html_parts:
            return '<div class="no-articles">No articles found for today. Check back tomorrow!</div>'
        
        return '\n'.join(html_parts)
    
    def generate_digest_html(self, articles_dict: Dict[str, List[Article]]) -> str:
        """Generate the complete HTML email digest."""
        template = self._get_email_template()
        
        # Calculate statistics
        total_articles = sum(len(articles) for articles in articles_dict.values())
        categories_count = sum(1 for articles in articles_dict.values() if articles)
        sources = set()
        for articles in articles_dict.values():
            for article in articles:
                sources.add(article.source)
        sources_count = len(sources)
        
        # Generate content
        date_str = self._format_date(datetime.now())
        articles_html = self._generate_articles_html(articles_dict)
        
        # Fill template
        html = template.format(
            date=date_str,
            total_articles=total_articles,
            categories_count=categories_count,
            sources_count=sources_count,
            articles_content=articles_html,
            year=datetime.now().year
        )
        
        return html
    
    def generate_plain_text_digest(self, articles_dict: Dict[str, List[Article]]) -> str:
        """Generate plain text version of the digest."""
        lines = []
        lines.append("=" * 60)
        lines.append("🇨🇳 China AI News Daily | 每日简报")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"📅 {self._format_date(datetime.now())}")
        lines.append("")
        
        for category_name, articles in articles_dict.items():
            if not articles:
                continue
            
            category_display = articles[0].category if articles else category_name
            lines.append("")
            lines.append("-" * 60)
            lines.append(f"{category_display}")
            lines.append("-" * 60)
            
            for i, article in enumerate(articles, 1):
                date_str = article.publish_date.strftime("%m月%d日 %H:%M") if article.publish_date else "刚刚"
                lines.append("")
                lines.append(f"{i}. {article.title}")
                lines.append(f"   📰 来源: {article.source}")
                lines.append(f"   📅 日期: {date_str}")
                lines.append(f"   🔗 链接: {article.url}")
                if article.keywords_matched:
                    lines.append(f"   🏷️ 关键词: {', '.join(article.keywords_matched[:3])}")
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("Generated by China AI News Monitor")
        lines.append("© 2026 All rights reserved")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def send_email(self, articles_dict: Dict[str, List[Article]], subject: str = None) -> bool:
        """
        Send the email digest.
        
        Args:
            articles_dict: Dictionary of articles by category
            subject: Optional custom subject line
        
        Returns:
            True if email sent successfully, False otherwise
        """
        # Check if email configuration is complete
        required_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password', 'recipient_email']
        for field in required_fields:
            if not self.email_config.get(field):
                logger.error(f"Missing email configuration: {field}")
                return False
        
        try:
            # Generate email content
            html_content = self.generate_digest_html(articles_dict)
            text_content = self.generate_plain_text_digest(articles_dict)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject or f"🇨🇳 China AI News Daily - {datetime.now().strftime('%Y年%m月%d日')}"
            msg['From'] = formataddr(
                (self.email_config.get('sender_name', 'China AI News Monitor'), 
                 self.email_config['sender_email'])
            )
            msg['To'] = self.email_config['recipient_email']
            
            # Attach both plain text and HTML
            part1 = MIMEText(text_content, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            server = smtplib.SMTP(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            )
            server.starttls()
            server.login(
                self.email_config['sender_email'],
                self.email_config['sender_password']
            )
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {self.email_config['recipient_email']}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending email: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test SMTP connection without sending email."""
        try:
            server = smtplib.SMTP(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            )
            server.starttls()
            server.login(
                self.email_config['sender_email'],
                self.email_config['sender_password']
            )
            server.quit()
            logger.info("SMTP connection test successful")
            return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False


if __name__ == "__main__":
    # Test the email sender
    sender = EmailSender()
    print("Email Sender initialized successfully")
    print(f"SMTP Server: {sender.email_config.get('smtp_server', 'Not configured')}")
