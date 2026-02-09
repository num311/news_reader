# config.py

EMAIL_SENDER = "fallout716@gmail.com"
EMAIL_PASSWORD = "fcok ptft kfyx prdw"  # It is recommended to use environment variables for sensitive data
EMAIL_RECIPIENT = "pmgiral@pm.me"

FEEDS = {
    "meneame": "https://www.meneame.net/rss",
    "pwned": "https://www.reddit.com/r/pwned/.rss",
    "HIBP":"https://feeds.feedburner.com/HaveIBeenPwnedLatestBreaches/",
    "Bleepin":"https://www.bleepingcomputer.com/feed/",
    "RansomFeed":"https://ransomfeed.it/rss",
    "RansomwareLive":"https://www.ransomware.live/rss.xml",
    "DataBreaches":"https://www.databreaches.net/feed/",
    "DarkFeed":"https://darkfeed.io/feed/"



}

KEYWORDS = ["acronis", "breach", "leak", "ransomware", "data breach","exploit", "cyberattack"]
HOURS_AGO = 8

# -- Notification Settings --
# Choose the notification channel: "email" or "telegram"
NOTIFICATION_CHANNEL = "email"

# Telegram Bot settings (only used if NOTIFICATION_CHANNEL is "telegram")
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with your bot's token
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"    # Replace with your chat ID
