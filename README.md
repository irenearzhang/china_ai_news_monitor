Note: Irene vibecoded this with MiniMax Agent and did not check the codebase; apologies in advance for any bugs

# China AI News Monitor

A daily email digest service that monitors Chinese AI news from 180+ reputable Chinese-language sources. This tool automatically fetches and sends you a curated daily email containing:

- 🤖 New AI model and product releases from Chinese AI labs
- 📜 AI and technology governance policies from Chinese government bodies  
- 📖 Long-form articles discussing the social impact of AI

## ⭐ Features

- **180+ Curated Sources**: From major tech media to popular WeChat channels
- **Smart Date Filtering**: Only includes articles from the last 24 hours (72 hours on Mondays)
- **Trust Scoring**: Articles are scored based on source credibility (100+ sources)
- **Automated Daily Digests**: Receives fresh news every weekday morning
- **Categorized Content**: Clear organization by news category
- **Weekday Only**: No weekend emails - respects your personal time
- **Responsive HTML Email**: Beautiful, readable email format

## 🚀 Quick Start

### For New Users

1. **Clone or download the code:**
   ```bash
   git clone https://github.com/yourusername/china-ai-news-monitor.git
   cd china-ai-news-monitor
   ```

2. **Copy and configure:**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml with your email settings
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test it out:**
   ```bash
   python main.py
   ```

That's it! Check your inbox for your first AI news digest.

## 📰 Monitored Categories

| Category | Description | Sources |
|----------|-------------|---------|
| 🤖 AI Releases | New models and products | 60+ sources |
| 📜 Policies | Government regulations | 40+ sources |
| 📖 Social Impact | Long-form analysis | 80+ sources |

### 🤖 AI Releases Sources

**Tech Media:** 36氪, 量子位, 机器之心, AI科技评论, 澎湃科技, 第一财经, 虎嗅, 钛媒体, 极客公园, 爱范儿, IT之家, 雷锋网, 智东西, 深科技, InfoQ, 甲子光年

**WeChat AI Channels:** 我爱计算机视觉, 机器学习社区, AI派, 深度学习社区, DataFunTalk, 大数据文摘, 算法与数学之美, AI产品君, 新智元, CSDN, GitChat

**Business & Investment:** 晚点LatePost, 42章经, 乱翻书, 投中网, 36氪Pro

**International:** 南华早报, SCMP, Reuters China, Bloomberg China

### 📜 Government Policy Sources

**Official Government:** 新华社, 人民网, 央视新闻, 国务院公报, 工信部, 网信办, 科技部, 发改委, 教育部, 财政部, 司法部, 国家数据局, 国家知识产权局

**Official WeChat:** 网信中国, 工信微报, 科技部发布, 国家发展改革委, 中国政府网

**Policy Analysis:** 财新, 南方周末, 澎湃思想市场, FT中文网, 经济学人

### 📖 Social Impact Sources

**Long-form Journalism:** 财新, 南方周末, 三联生活周刊, 澎湃新闻, 新京报, 凤凰周刊, 南方人物周刊, 人物, GQ中国

**Society & Culture:** X博士, 故事硬核, 好奇心日报, 全现在, 端传媒, 网易浪潮, 谷雨实验室

**Lifestyle & Tech Impact:** 硬核电台, 故事FM, 随机波动, 声东击西

**Academic:** 清华大学, 北京大学, 中国社科院, 中国信通院, 中国人工智能学会

## 🏆 Source Credibility System

| Tier | Score | Sources |
|------|-------|---------|
| Tier 1 | 1.0 | Official government (新华社, 人民网, 工信部, etc.) |
| Tier 2 | 0.95-1.0 | Premium journalism (财新, 南方周末, 三联) |
| Tier 3 | 0.85-0.9 | Major tech media (36氪, 量子位, 机器之心) |
| Tier 4 | 0.8-0.85 | Tech news (智东西, InfoQ, 甲子光年) |
| Tier 5 | 0.7-0.8 | WeChat AI channels (我爱计算机视觉, etc.) |
| Tier 6+ | 0.65-0.75 | Society, culture, academic sources |

## 📁 What's Included

```
china-ai-news-monitor/
├── main.py              # Main application (run this!)
├── news_fetcher.py      # News fetching and filtering
├── email_sender.py      # Email generation and sending
├── config.yaml.example  # Configuration template (safe to share)
├── config.yaml          # Your personal settings (not shared)
├── requirements.txt     # Python dependencies
├── setup.sh             # Setup script
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── data/                # Data storage
```

## 🔧 Configuration

All settings are managed through `config.yaml`. Key settings:

### Email Settings
```yaml
email:
  smtp_server: smtp.gmail.com      # Your SMTP server
  smtp_port: 587                   # Port 587 for TLS
  sender_email: you@example.com    # Your email
  sender_password: your-app-password  # App password (not regular password!)
  recipient_email: friend@example.com # Who gets the news
  sender_name: China AI News Monitor
```

### Schedule Settings
```yaml
monitoring:
  send_time: "08:00"           # Time to send (24-hour format)
  timezone: "US/Pacific"       # Your timezone
  days_of_week: [1, 2, 3, 4, 5]  # Weekdays only (Mon=1, Fri=5)
  normal_hours: 24             # Last 24 hours (Tue-Fri)
  monday_hours: 72             # Last 72 hours (Monday)
```

## 💡 Usage

### Run Once (Manual)
```bash
python main.py
```

### Run Scheduler (Automatic)
```bash
python main.py --schedule
```

### Other Commands
```bash
python main.py --config      # View current settings
python main.py --test-email  # Test email connection
python main.py --setup       # Reconfigure email
python main.py --verbose     # Debug logging
```

## 🔐 Getting Your App Password

**For Gmail:**
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"
3. Go to https://myaccount.google.com/apppasswords
4. Create a new app password
5. Use that 16-character password in config.yaml

**For Other Providers:**
- Outlook/Office 365: smtp.office365.com
- Yahoo: smtp.mail.yahoo.com
- iCloud: smtp.mail.me.com

## 🌍 Sharing with Friends

This tool is designed to be shared! Here's how:

### Option 1: Share the GitHub Link
Send friends the repository URL and they can clone it.

### Option 2: Direct Setup for Friends
```bash
git clone https://github.com/yourusername/china-ai-news-monitor.git
cd china-ai-news-monitor
cp config.yaml.example config.yaml
# Edit config.yaml with email settings
python main.py
```

### Option 3: Fork the Repository
Friends can fork the repo and customize their own sources and keywords.

### Customization Before Sharing
Edit `config.yaml` to change:
- Keywords for each category (100+ keywords total)
- News sources to monitor (180+ sources)
- Trust scores for sources (100+ weighted sources)
- Email template styling

## 🛠️ Dependencies

See `requirements.txt` for full list:
- PyYAML - Configuration parsing
- python-dateutil - Date handling
- pytz - Timezone support
- schedule - Job scheduling
- beautifulsoup4 - HTML parsing

Install with:
```bash
pip install -r requirements.txt
```

## 🔒 Security Notes

- **Never commit** config.yaml with real credentials to GitHub
- **Use App Passwords** instead of regular passwords
- **Review logs** periodically for any issues
- **config.yaml.example** is safe to share (no real credentials)

## 🐛 Troubleshooting

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**Email authentication failed:**
- Are you using an App Password?
- Is 2-Step Verification enabled on Gmail?

**No articles found:**
- Check your internet connection
- Try running with `--verbose` to see search queries
- Review `china_ai_news_monitor.log`

**Scheduler not running:**
- Keep the script running in background:
  ```bash
  nohup python main.py --schedule > output.log 2>&1 &
  ```

## 📝 License

MIT License - Free to use, modify, and share!

## 🤝 Contributing

Found a bug? Have a feature request? Open an issue or submit a pull request.

## 🙏 Credits

Built with ❤️ for researchers and China tech watchers.

---

## ☁️ Deploy to Railway (24/7 Automatic)

Deploy to Railway for fully automated 24/7 operation - works even when your computer is off!

### Step 1: Fork the Repository
1. Go to: https://github.com/irenearzhang/china_ai_news_monitor
2. Click **"Fork"** (top right) to fork it to your GitHub account

### Step 2: Create Railway Project
1. Go to: https://railway.app/new
2. Click **"Login with GitHub"** and authorize Railway
3. Click **"Deploy from GitHub repo"**
4. Select your forked repository: `yourusername/china_ai_news_monitor`

### Step 3: Add Environment Variables
In your Railway project dashboard:
1. Click on your project → **"Variables"** tab
2. Add these variables:

| Variable | Value |
|----------|-------|
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SENDER_EMAIL` | `your-email@gmail.com` |
| `SENDER_PASSWORD` | `your-app-password` |
| `RECIPIENT_EMAIL` | `recipient@example.com` |
| `SENDER_NAME` | `China AI News Monitor` |
| `TIMEZONE` | `US/Pacific` |
| `SEND_TIME` | `08:00` |

### Step 4: Deploy
1. Railway will automatically deploy from your GitHub repo
2. Click **"Deploy"** to start
3. Check the **"Logs"** tab for status

### Step 5: Verify
- Check logs for successful deployment
- Test with: Railway → Your Service → Actions → Run Command → `python test_email.py`
- You'll receive your first daily email at 8:00 AM!

### Troubleshooting Railway
- **Email not sending?** Check logs for errors
- **Environment variables not working?** Make sure to click "Deploy" after adding variables
- **Need to restart?** Click "Actions" → "Restart" in Railway dashboard

### What You Get
- ✅ 24/7 automated operation
- ✅ Daily emails at 8:00 AM PT
- ✅ Works even when computer is off
- ✅ Free tier available

---

**Questions? Open an issue on GitHub!**
