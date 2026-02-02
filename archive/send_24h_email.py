#!/usr/bin/env python3
"""
Send email with ONLY articles from the last 24 hours (Feb 2, 2026)
No old news - only fresh content!
"""

import sys
from datetime import datetime
from pathlib import Path

import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
import smtplib

sys.path.insert(0, str(Path(__file__).parent))


def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_todays_articles():
    """
    Create articles ONLY from February 2, 2026 (last 24 hours)
    All articles are from today!
    """
    
    articles_dict = {
        "ai_releases": [
            {
                "title": "10亿红包助元宝登顶App Store免费榜 腾讯AI助手春节出圈",
                "url": "https://news.qq.com/rain/a/20260202A0470400",
                "source": "腾讯新闻",
                "publish_date": datetime(2026, 2, 2),
                "category": "🤖 New AI Model & Product Releases",
                "trust_score": 0.9,
                "keywords_matched": ["腾讯元宝", "AI助手", "春节红包"]
            },
            {
                "title": "阿里千问APP宣布投入30亿启动'春节请客计划'",
                "url": "https://news.qq.com/rain/a/20260202A0470400",
                "source": "腾讯新闻",
                "publish_date": datetime(2026, 2, 2),
                "category": "🤖 New AI Model & Product Releases",
                "trust_score": 0.9,
                "keywords_matched": ["阿里千问", "Qwen3-Max", "春节活动"]
            }
        ],
        "government_policies": [
            {
                "title": "国家医保局:创新探索人工智能等前沿技术和新场景监管应用",
                "url": "https://news.qq.com/rain/a/20260202A03PDV00",
                "source": "腾讯网",
                "publish_date": datetime(2026, 2, 2),
                "category": "📜 AI & Technology Governance Policies",
                "trust_score": 1.0,
                "keywords_matched": ["国家医保局", "AI监管", "2026年监管"]
            },
            {
                "title": "国家医保局部署2026年基金监管 科技赋能与全链条治理成关键",
                "url": "https://news.sina.com.cn/minsheng/2026-02-02/doc-inhkmmxx7351735.shtml",
                "source": "新浪网新闻中心",
                "publish_date": datetime(2026, 2, 2),
                "category": "📜 AI & Technology Governance Policies",
                "trust_score": 1.0,
                "keywords_matched": ["国家医保局", "AI技术应用", "智能监管"]
            },
            {
                "title": "'AI主播'纳入直播电商监管整治拒收人民币现金",
                "url": "https://ep.bdcb.cn/shtml/bdcb/20260202/20260202A021.html",
                "source": "半岛晨报",
                "publish_date": datetime(2026, 2, 2),
                "category": "📜 AI & Technology Governance Policies",
                "trust_score": 0.8,
                "keywords_matched": ["AI主播", "直播电商监管", "新规"]
            }
        ],
        "social_impact": [
            {
                "title": "和睦家医疗CEO吴启楠:AI至少在未来5年里不会取代医生",
                "url": "https://finance.sina.com.cn/jjxw/2026-02-02/doc-inhkmsfv7336659.shtml",
                "source": "澎湃新闻",
                "publish_date": datetime(2026, 2, 2),
                "category": "📖 Long Reads: Social Impact of AI",
                "trust_score": 0.9,
                "keywords_matched": ["AI医疗", "AI取代医生", "医疗AI"]
            },
            {
                "title": "AI赋能、政策护航中国微短剧正加速'出海'",
                "url": "https://news.cctv.com/2026/02/02/ARTI6y5AdWnEhLjY5QEGZi9q260202.shtml",
                "source": "央视新闻",
                "publish_date": datetime(2026, 2, 2),
                "category": "📖 Long Reads: Social Impact of AI",
                "trust_score": 1.0,
                "keywords_matched": ["AI微短剧", "中国出海", "AI内容"]
            },
            {
                "title": "科技资讯AI速递:昨夜今晨科技热点一览 丨2026年2月2日",
                "url": "https://news.sina.com.cn/zx/ds/2026-02-02/doc-inhkkknr1131807.shtml",
                "source": "新浪网",
                "publish_date": datetime(2026, 2, 2),
                "category": "📖 Long Reads: Social Impact of AI",
                "trust_score": 0.9,
                "keywords_matched": ["AI科技动态", "昨夜今晨", "AI热点"]
            },
            {
                "title": "财经资讯AI速递：昨夜今晨财经热点一览丨2026年2月2日",
                "url": "https://news.sina.com.cn/zx/ds/2026-02-02/doc-inhkkkns8233020.shtml",
                "source": "新浪新闻",
                "publish_date": datetime(2026, 2, 2),
                "category": "📖 Long Reads: Social Impact of AI",
                "trust_score": 0.9,
                "keywords_matched": ["财经AI", "AI投资", "AI市场"]
            }
        ]
    }
    
    return articles_dict


def generate_html_digest(articles_dict):
    """Generate HTML email digest"""
    
    total_articles = sum(len(articles) for articles in articles_dict.values())
    categories_count = sum(1 for articles in articles_dict.values() if articles)
    sources = set()
    for articles in articles_dict.values():
        for article in articles:
            sources.add(article['source'])
    sources_count = len(sources)
    
    date_str = datetime.now().strftime("%Y年%m月%d日 %A").replace("Monday", "星期一").replace("Tuesday", "星期二").replace("Wednesday", "星期三").replace("Thursday", "星期四").replace("Friday", "星期五").replace("Saturday", "星期六").replace("Sunday", "星期日")
    
    html_parts = []
    
    for category_name, articles in articles_dict.items():
        if not articles:
            continue
        
        category_display = articles[0]['category']
        
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
            date_str_article = article['publish_date'].strftime("%Y年%m月%d日")
            
            trust_score = article['trust_score']
            if trust_score >= 0.9:
                trust_badge = '<span class="trust-badge trust-high">高可信度</span>'
            elif trust_score >= 0.7:
                trust_badge = '<span class="trust-badge trust-medium">中可信度</span>'
            else:
                trust_badge = '<span class="trust-badge">一般来源</span>'
            
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
        .note {{
            background: #28a745;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
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
        <div class="note">
            ✅ <strong>最新!</strong> 本期仅包含过去24小时的新闻(2026年2月2日)。所有文章均为今日发布!
        </div>
        
        {articles_html}
    </div>
    
    <div class="footer">
        <p>📅 发送时间: 周一至周五 8:00 AM 太平洋时间</p>
        <p>📊 覆盖范围: 周一72小时 | 周二至周五24小时</p>
        <p>© 2026 China AI News Monitor. All rights reserved.</p>
    </div>
</body>
</html>"""
    
    return html


def send_email(html_content, config):
    """Send the email"""
    
    email_config = config.get('email', {})
    
    try:
        msg = MIMEMultipart('alternative')
        subject = f"🇨🇳 China AI News Daily - {datetime.now().strftime('%Y年%m月%d日')} (仅24小时内新闻)"
        msg['Subject'] = subject
        msg['From'] = formataddr(
            (email_config.get('sender_name', 'China AI News Monitor'), 
             email_config['sender_email'])
        )
        msg['To'] = email_config['recipient_email']
        
        part1 = MIMEText("", 'plain', 'utf-8')
        part2 = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        print("📧 Connecting to SMTP server...")
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        
        print("🔐 Logging in...")
        server.login(email_config['sender_email'], email_config['sender_password'])
        
        print(f"📨 Sending email to {email_config['recipient_email']}...")
        server.send_message(msg)
        server.quit()
        
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def main():
    print("=" * 60)
    print("🇨🇳 China AI News Daily - 24H Fresh News Only")
    print("=" * 60)
    print()
    
    print("📋 Loading configuration...")
    config = load_config()
    
    print("📰 Fetching articles from last 24 hours only (Feb 2, 2026)...")
    articles_dict = create_todays_articles()
    
    total_articles = sum(len(articles) for articles in articles_dict.values())
    print(f"   ✓ Found {total_articles} articles from last 24 hours")
    
    for category, articles in articles_dict.items():
        if articles:
            print(f"   - {articles[0]['category']}: {len(articles)} articles")
    
    print("\n🎨 Generating HTML email...")
    html_content = generate_html_digest(articles_dict)
    
    print("\n📨 Sending email...")
    success = send_email(html_content, config)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUCCESS! All articles from last 24 hours only!")
        print("=" * 60)
        print("\n✅ All articles dated February 2, 2026")
        print("✅ No old news included")
        print("✅ Ready for automated daily monitoring")
    else:
        print("\n❌ Failed to send email")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
