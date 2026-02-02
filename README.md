# China AI News Monitor

A daily email digest service that monitors Chinese AI news from reputable Chinese-language sources. This tool automatically fetches and sends you a curated daily email containing:

- 🤖 New AI model and product releases from Chinese AI labs
- 📜 AI and technology governance policies from Chinese government bodies  
- 📖 Long-form articles discussing the social impact of AI

## ⭐ Features

- **Automated Daily Digests**: Receives fresh news every weekday morning
- **Smart Date Filtering**: Only includes articles from the last 24 hours (72 hours on Mondays)
- **Curated Sources**: Only pulls from reputable Chinese-language media outlets
- **Trust Scoring**: Articles are scored based on source credibility
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

2. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure your email:**
   ```bash
   python main.py --setup
   ```

4. **Test it out:**
   ```bash
   python main.py
   ```

That's it! Check your inbox for your first AI news digest.

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md).

## 📁 What's Included

```
china-ai-news-monitor/
├── main.py              # Main application (run this!)
├── news_fetcher.py      # News fetching and filtering
├── email_sender.py      # Email generation and sending
├── config.example.yaml  # Configuration template
├── config.yaml          # Your personal settings (not shared)
├── setup.sh             # Setup script
├── requirements.txt     # Python dependencies
├── QUICKSTART.md        # 5-minute setup guide
├── README.md            # This file
└── archive/             # Old test files (not needed)
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

## 📰 Monitored Categories

| Category | Description | Examples |
|----------|-------------|----------|
| 🤖 AI Releases | New models and products | 文心一言, 通义千问, 智谱AI |
| 📜 Policies | Government regulations | AI监管, 数据安全法, 网信办政策 |
| 📖 Social Impact | Long-form analysis | AI伦理, 就业影响, 隐私保护 |

## 🏆 Trusted Sources

**Premium (1.0):** 新华社, 人民网, 财新, 南方周末, 国务院公报, 工信部, 网信办, 科技部, 发改委

**High (0.9):** 36氪, 量子位, 机器之心, 澎湃新闻

**Medium (0.8):** 第一财经, 新京报, 三联生活周刊

**Standard (0.7):** 凤凰周刊, AI科技评论

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

### Option 2: Export Your Configuration
If you've customized keywords or sources, you can share your config:
```bash
# Copy your config (remove sensitive email/password first)
cp config.yaml config.yaml.backup
# Edit and remove email section before sharing
```

### Option 3: Fork the Repository
Friends can fork the repo and customize their own settings.

### Customize Before Sharing
Edit `config.yaml` to change:
- Keywords for each category
- News sources to monitor
- Trust scores for sources
- Email template styling

## 🛠️ Customization

### Add Custom Keywords
```yaml
categories:
  ai_releases:
    keywords:
      - "你的新关键词"
```

### Add New Sources
```yaml
categories:
  ai_releases:
    sources:
      - "新来源"

source_weights:
  "新来源": 0.8
```

### Change Email Template
Edit `_get_email_template()` in `email_sender.py` to customize HTML.

## 📦 Dependencies

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
- **Config template** (config.example.yaml) is safe to share

## 🐛 Troubleshooting

**"Module not found" errors:**
```bash
source venv/bin/activate
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

**Questions? Open an issue on GitHub!**
