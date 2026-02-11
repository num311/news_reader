# config.py

EMAIL_SENDER = "fallout716@gmail.com"
EMAIL_PASSWORD = "xxxxx"  # It is recommended to use environment variables for sensitive data
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
    "bleepingcomputer": "https://www.bleepingcomputer.com/feed/"
}

KEYWORDS = ["cyber", "acronis", "vuln"]
HOURS_AGO = 2
