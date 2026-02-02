# Quick Start Guide

Get up and running with China AI News Monitor in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- An email account with SMTP access (Gmail recommended)

## Step 1: Get the Code

**Option A: Clone from GitHub**
```bash
git clone https://github.com/yourusername/china-ai-news-monitor.git
cd china-ai-news-monitor
```

**Option B: Download ZIP**
1. Download the ZIP file from GitHub
2. Extract it to a folder
3. Open terminal in that folder

## Step 2: Run Setup

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create necessary directories

## Step 3: Configure Email

```bash
python main.py --setup
```

Follow the prompts to enter:
- Your SMTP server (e.g., smtp.gmail.com)
- Your email address
- Your app password (see below for Gmail)
- Recipient email address

**For Gmail Users:**
1. Go to Google Account Settings > Security
2. Enable 2-Step Verification
3. Go to App Passwords (https://myaccount.google.com/apppasswords)
4. Create a new app password
5. Use that password in the setup

**For Other Email Providers:**
- Outlook/Office 365: smtp.office365.com, port 587
- Yahoo Mail: smtp.mail.yahoo.com, port 587
- iCloud Mail: smtp.mail.me.com, port 587

## Step 4: Test It Works

```bash
python main.py --test-email
```

You should receive a test email within a few seconds.

## Step 5: Run Your First News Digest

```bash
python main.py
```

This will fetch the latest Chinese AI news and send it to your inbox.

## Step 6: Automate Daily Updates (Optional)

To receive news automatically every weekday at 8 AM:

```bash
python main.py --schedule
```

Keep this running in the background!

## Customization

### Change Send Time

Edit `config.yaml`:
```yaml
monitoring:
  send_time: "09:00"  # Change to your preferred time
```

### Change Timezone

Edit `config.yaml`:
```yaml
monitoring:
  timezone: "Asia/Shanghai"  # Your timezone
```

### Add/Remove Keywords

Edit the `keywords` sections in `config.yaml` under each category.

## Troubleshooting

**"Module not found" errors:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Email not sending:**
- Make sure you're using an App Password, not your regular password
- Check your SMTP server and port settings
- Ensure 2-Step Verification is enabled (for Gmail)

**No articles found:**
- Check your internet connection
- Review the log file: `china_ai_news_monitor.log`

## Need Help?

- Check the full README.md
- Open an issue on GitHub
- Contact the maintainer

## License

MIT License - Free to use and modify!
