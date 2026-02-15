import os

# Notificaciones: "email" o "telegram"
NOTIFICATION_METHOD = os.getenv("NOTIFICATION_METHOD", "email").lower()

# Configuracion de correo
EMAIL_SENDER = "fallout716@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECIPIENT = "pmgiral@pm.me"

# Configuracion de Telegram para envio de notificaciones
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Configuracion de Telegram para busqueda en canales (Telethon)
TELEGRAM_ENABLE_SEARCH = os.getenv("TELEGRAM_ENABLE_SEARCH", "false").lower() == "true"
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "news_reader_session")

# Canales a revisar (variable de entorno, separados por coma, sin @)
# Ejemplo: TELEGRAM_CHANNELS="durov,examplechannel"
TELEGRAM_CHANNELS = [
    channel.strip()
    for channel in os.getenv("TELEGRAM_CHANNELS", "").split(",")
    if channel.strip()
]

FEEDS = {
    "meneame": "https://www.meneame.net/rss",
    "pwned": "https://www.reddit.com/r/pwned/.rss",
    "databreaches": "https://www.databreaches.net/feed/",
    "haveibeenpwned": "https://feeds.feedburner.com/HaveIBeenPwnedLatestBreaches",
    "ransomware": "https://www.ransomware.live/rss.xml",
    "ransomfeed": "https://ransomfeed.it/rss",
    "cisa": "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "nvd": "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml",
    "bleepingcomputer": "https://www.bleepingcomputer.com/feed/",
    "krebsonsecurity": "https://krebsonsecurity.com/feed/",
    "thehackernews": "https://feeds.feedburner.com/TheHackernews",
}

KEYWORDS = [
    "acronis",
    "breach",
    "ransomware",
    "leak",
    "exploit",
    "vulnerability",
    "hacked",
    "dump",
    "compromised",
    "incident",
    "attack",
]
HOURS_AGO = 8
