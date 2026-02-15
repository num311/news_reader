import os

# Notificaciones: "email"
NOTIFICATION_METHOD = "email"

# Configuracion de correo
EMAIL_SENDER = "fallout716@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECIPIENT = "pmgiral@pm.me"

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
