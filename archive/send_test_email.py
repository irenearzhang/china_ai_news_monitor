#!/usr/bin/env python3
"""
Send a test email with sample news articles
This script processes search results and sends a sample digest email
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def load_config():
    """Load configuration from config.yaml"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_sample_articles():
    """Create sample articles from the search results"""
    
    # Sample articles based on the search results we just got
    sample_data = {
        "ai_releases": [
            {
                "title": "周鸿祎发布2026年20个AI预言：我们正迈向百亿智能体时代",
                "url": "https://finance.sina.com.cn/tob/2026-01-09/doc-inhfswxt0514066.shtml",
                "source": "新浪财经",
                "publish_date": datetime.now() - timedelta(hours=4),
                "category": "🤖 New AI Model & Product Releases",
                "trust_score": 0.9,
                "keywords_matched": ["AI大模型 发布", "AI预言"]
            },
            {
                "title": "阿里千问全球走红，开源大模型引领2026年AI新趋势",
                "url": "https://www.sohu.com/a/970507311_114984",
                "source": "搜狐",
                "publish_date": datetime.now() - timedelta(hours=8),
                "category": "🤖 New AI Model & Product Releases",
                "trust_score": 0.8,
                "keywords_matched": ["通义千问", "大模型 发布"]
            },
            {
                "title": "阶跃星辰完成超50亿元B+轮融资，刷新中国大模型赛道单笔最高融资纪录",
                "url": "https://www.stcn.com/article/detail/3612291.html",
                "source": "证券时报",
                "publish_date": datetime.now() - timedelta(hours=12),
                "category": "🤖 New AI Model & Product Releases",
                "trust_score": 1.0,
                "keywords_matched": ["阶跃星辰", "AI融资"]
            },
            {
                "title": "月之暗面Kimi-latest:革新AI对话体验的智能助手",
                "url": "https://www.sohu.com/a/860672513_121924584",
                "source": "搜狐",
                "publish_date": datetime.now() - timedelta(hours=18),
                "category": "🤖 New AI Model & Product Releases",
                "trust_score": 0.8,
                "keywords_matched": ["月之暗面", "Kimi", "AI产品"]
            },
            {
                "title": "2026 AI商业中场：从原生多模态到超级入口",
                "url": "https://news.qq.com/rain/a/20251222A0725100",
                "source": "腾讯新闻",
                "publish_date": datetime.now() - timedelta(days=1),
                "category": "🤖 New AI Model & Product Releases",
                "trust_score": 0.9,
                "keywords_matched": ["AI大模型", "2026趋势"]
            }
        ],
        "government_policies": [
            {
                "title": "生成式人工智能服务管理暂行办法",
                "url": "http://www.gov.cn/zhengce/zhengceku/202307/content_6891752.htm",
                "source": "中国政府网",
                "publish_date": datetime.now() - timedelta(days=1),
                "category": "📜 AI & Technology Governance Policies",
                "trust_score": 1.0,
                "keywords_matched": ["生成式AI 管理规定", "网信办"]
            },
            {
                "title": "2025人工智能治理蓝皮书(2024年) - 中国信息通信研究院",
                "url": "https://m.book118.com/html/2025/0118/6235000051011031.shtm",
                "source": "原创力文档",
                "publish_date": datetime.now() - timedelta(days=2),
                "category": "📜 AI & Technology Governance Policies",
                "trust_score": 0.8,
                "keywords_matched": ["人工智能治理", "AI伦理"]
            },
            {
                "title": "我国人工智能相关主要法律法规、标准规范",
                "url": "https://m.blog.csdn.net/2402_84637076/article/details/145608008",
                "source": "CSDN",
                "publish_date": datetime.now() - timedelta(days=3),
                "category": "📜 AI & Technology Governance Policies",
                "trust_score": 0.7,
                "keywords_matched": ["AI 政策", "法律法规"]
            },
            {
                "title": "科技部:人工智能企业或需设立科技伦理审查委员会",
                "url": "https://36kr.com/newsflashes/1334536223610888",
                "source": "36氪",
                "publish_date": datetime.now() - timedelta(days=4),
                "category": "📜 AI & Technology Governance Policies",
                "trust_score": 0.9,
                "keywords_matched": ["AI 伦理", "科技部"]
            }
        ],
        "social_impact": [
            {
                "title": "智能时代的伦理挑战：人工智能的影响与责任",
                "url": "https://m.sohu.com/a/816652904_267471/",
                "source": "搜狐",
                "publish_date": datetime.now() - timedelta(hours=6),
                "category": "📖 Long Reads: Social Impact of AI",
                "trust_score": 0.8,
                "keywords_matched": ["AI 社会影响", "人工智能伦理"]
            },
            {
                "title": "人工智能风险解析:就业冲击与隐私安全成核心议题",
                "url": "https://www.sohu.com/a/881548449_121924584",
                "source": "搜狐",
                "publish_date": datetime.now() - timedelta(hours=12),
                "category": "📖 Long Reads: Social Impact of AI",
                "trust_score": 0.8,
                "keywords_matched": ["AI 就业 影响", "AI 隐私"]
            },
            {
                "title": "AI公平性：消除算法偏见的技术与政策",
                "url": "https://m.blog.csdn.net/universsky2015/article/details/142800701",
                "source": "CSDN",
                "publish_date": datetime.now() - timedelta(days=2),
                "category": "📖 Long Reads: Social Impact of AI",
                "trust_score": 0.7,
                "keywords_matched": ["算法 偏见", "AI公平性"]
            },
            {
                "title": "大模型哲学思考 ——技术、伦理与社会影响",
                "url": "https://www.talkwithtrend.com/Article/271005",
                "source": "twt社区",
                "publish_date": datetime.now() - timedelta(days=3),
                "category": "📖 Long Reads: Social Impact of AI",
                "trust_score": 0.7,
                "keywords_matched": ["大模型 社会价值", "技术反思"]
            },
            {
                "title": "达沃斯论坛热议AI社会影响",
                "url": "http://www.news.cn/liangzi/20260126/582547976bdc4c4483e41b05a7d4b429/c.html",
                "source": "新华网",
                "publish_date": datetime.now() - timedelta(days=4),
                "category": "📖 Long Reads: Social Impact of AI",
                "trust_score": 1.0,
                "keywords_matched": ["AI 社会 影响", "达沃斯论坛"]
            }
        ]
    }
    
    return sample_data


def generate_html_digest(articles_dict):
    """Generate HTML email digest"""
    
    # Calculate statistics
    total_articles = sum(len(articles) for articles in articles_dict.values())
    categories_count = sum(1 for articles in articles_dict.values() if articles)
    sources = set()
    for articles in articles_dict.values():
        for article in articles:
            sources.add(article['source'])
    sources_count = len(sources)
    
    # Format date
    date_str = datetime.now().strftime("%Y年%m月%d日 %A").replace("Monday", "星期一").replace("Tuesday", "星期二").replace("Wednesday", "星期三").replace("Thursday", "星期四").replace("Friday", "星期五").replace("Saturday", "星期六").replace("Sunday", "星期日")
    
    # Generate articles HTML
    html_parts = []
    
    for category_name, articles in articles_dict.items():
        if not articles:
            continue
        
        category_display = articles[0]['category']
        
        # Extract emoji
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
        for i, article in enumerate(articles, 1):
            date_str_article = article['publish_date'].strftime("%m月%d日 %H:%M")
            
            # Trust badge
            trust_score = article['trust_score']
            if trust_score >= 0.9:
                trust_badge = '<span class="trust-badge trust-high">高可信度</span>'
            elif trust_score >= 0.7:
                trust_badge = '<span class="trust-badge trust-medium">中可信度</span>'
            else:
                trust_badge = '<span class="trust-badge">一般来源</span>'
            
            # Keywords
            keywords_html = ""
            if article.get('keywords_matched'):
                keywords_html = '<div class="article-keywords">' + ' '.join([
                    f'<span class="keyword-tag">{kw}</span>' 
                    for kw in article['keywords_matched'][:3]
                ]) + '</div>'
            
            article_html = f"""
            <div class="article">
                <div class="article-title">
                    <a href="{article['url']}" target="_blank">{article['title']}</a>
                    {trust_badge}
                </div>
                <div class="article-meta">
                    📰 {article['source']} &nbsp;|&nbsp; 📅 {date_str_article}
                </div>
                {keywords_html}
            </div>
"""
            category_html += article_html
        
        category_html += "        </div>"
        html_parts.append(category_html)
    
    articles_html = '\n'.join(html_parts)
    
    # Full HTML template
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>China AI News Daily</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            padding: 30px 20px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            border-radius: 12px 12px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header .date {{
            margin-top: 10px;
            font-size: 14px;
            opacity: 0.8;
        }}
        .content {{
            background: white;
            padding: 30px;
            border-radius: 0 0 12px 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .category {{
            margin: 30px 0;
        }}
        .category:first-child {{
            margin-top: 0;
        }}
        .category-header {{
            display: flex;
            align-items: center;
            padding-bottom: 15px;
            border-bottom: 2px solid #1a1a2e;
            margin-bottom: 20px;
        }}
        .category-icon {{
            font-size: 24px;
            margin-right: 10px;
        }}
        .category-title {{
            font-size: 20px;
            font-weight: 600;
            color: #1a1a2e;
        }}
        .article {{
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }}
        .article:last-child {{
            border-bottom: none;
        }}
        .article-title {{
            font-size: 16px;
            font-weight: 500;
            color: #2c3e50;
            margin-bottom: 8px;
        }}
        .article-title a {{
            color: #3498db;
            text-decoration: none;
        }}
        .article-title a:hover {{
            text-decoration: underline;
        }}
        .article-meta {{
            font-size: 12px;
            color: #7f8c8d;
            margin-bottom: 8px;
        }}
        .article-keywords {{
            margin-top: 8px;
        }}
        .keyword-tag {{
            display: inline-block;
            background: #e8f4f8;
            color: #2980b9;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-right: 5px;
        }}
        .trust-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 10px;
        }}
        .trust-high {{
            background: #d5f5e3;
            color: #27ae60;
        }}
        .trust-medium {{
            background: #fdebd0;
            color: #e67e22;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #7f8c8d;
            border-top: 1px solid #eee;
            margin-top: 30px;
        }}
        .no-articles {{
            text-align: center;
            color: #7f8c8d;
            padding: 20px;
            font-style: italic;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            font-size: 13px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: 600;
            color: #3498db;
        }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🇨🇳 China AI News Daily</h1>
        <div class="date">{date_str}</div>
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
        {articles_html}
    </div>
    
    <div class="footer">
        <p>This daily digest is automatically generated by China AI News Monitor.</p>
        <p>Sources include: 36氪, 量子位, 机器之心, 新华社, 人民网, 财新, 南方周末, and other reputable Chinese media.</p>
        <p>© 2026 China AI News Monitor. All rights reserved.</p>
    </div>
</body>
</html>"""
    
    return html


def generate_plain_text_digest(articles_dict):
    """Generate plain text version"""
    
    lines = []
    lines.append("=" * 60)
    lines.append("🇨🇳 China AI News Daily | 每日简报")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"📅 {datetime.now().strftime('%Y年%m月%d日 %A').replace('Monday', '星期一').replace('Tuesday', '星期二').replace('Wednesday', '星期三').replace('Thursday', '星期四').replace('Friday', '星期五').replace('Saturday', '星期六').replace('Sunday', '星期日')}")
    lines.append("")
    
    for category_name, articles in articles_dict.items():
        if not articles:
            continue
        
        category_display = articles[0]['category']
        lines.append("")
        lines.append("-" * 60)
        lines.append(f"{category_display}")
        lines.append("-" * 60)
        
        for i, article in enumerate(articles, 1):
            date_str = article['publish_date'].strftime("%m月%d日 %H:%M")
            lines.append("")
            lines.append(f"{i}. {article['title']}")
            lines.append(f"   📰 来源: {article['source']}")
            lines.append(f"   📅 日期: {date_str}")
            lines.append(f"   🔗 链接: {article['url']}")
            if article.get('keywords_matched'):
                lines.append(f"   🏷️ 关键词: {', '.join(article['keywords_matched'][:3])}")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("Generated by China AI News Monitor")
    lines.append("© 2026 All rights reserved")
    lines.append("=" * 60)
    
    return '\n'.join(lines)


def send_email(html_content, text_content, config):
    """Send the email digest"""
    
    email_config = config.get('email', {})
    
    # Check configuration
    required_fields = ['smtp_server', 'smtp_port', 'sender_email', 'sender_password', 'recipient_email']
    for field in required_fields:
        if not email_config.get(field):
            print(f"❌ Missing email configuration: {field}")
            print("Please run: python main.py --setup")
            return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        subject = f"🇨🇳 China AI News Daily - {datetime.now().strftime('%Y年%m月%d日')}"
        msg['Subject'] = subject
        msg['From'] = formataddr(
            (email_config.get('sender_name', 'China AI News Monitor'), 
             email_config['sender_email'])
        )
        msg['To'] = email_config['recipient_email']
        
        # Attach both plain text and HTML
        part1 = MIMEText(text_content, 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        print("📧 Connecting to SMTP server...")
        server = smtplib.SMTP(
            email_config['smtp_server'],
            email_config['smtp_port']
        )
        server.starttls()
        
        print("🔐 Logging in...")
        server.login(
            email_config['sender_email'],
            email_config['sender_password']
        )
        
        print(f"📨 Sending email to {email_config['recipient_email']}...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def main():
    """Main function to send test email"""
    print("=" * 60)
    print("🇨🇳 China AI News Monitor - Test Email")
    print("=" * 60)
    print()
    
    # Load configuration
    print("📋 Loading configuration...")
    config = load_config()
    
    # Create sample articles
    print("📰 Creating sample articles from search results...")
    articles_dict = create_sample_articles()
    
    total_articles = sum(len(articles) for articles in articles_dict.values())
    print(f"   ✓ Created {total_articles} sample articles")
    
    for category, articles in articles_dict.items():
        if articles:
            print(f"   - {articles[0]['category']}: {len(articles)} articles")
    
    # Generate HTML digest
    print("\n🎨 Generating HTML email...")
    html_content = generate_html_digest(articles_dict)
    
    # Generate plain text
    print("📝 Generating plain text version...")
    text_content = generate_plain_text_digest(articles_dict)
    
    # Send email
    print("\n📨 Sending email...")
    success = send_email(html_content, text_content, config)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Test email sent successfully!")
        print("=" * 60)
        print("\nCheck your email inbox for the digest.")
        print("The email contains sample articles from all three categories.")
    else:
        print("\n" + "=" * 60)
        print("❌ Failed to send email")
        print("=" * 60)
        print("\nPlease check your email configuration and try again.")
        print("Run: python main.py --setup")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
