#!/usr/bin/python3
"""
Checks RSS feeds for news containing specific keywords within a time window
and sends notifications via email or Telegram.
"""

import logging
import html
from datetime import datetime, timedelta, timezone
from calendar import timegm
from email.utils import parsedate_to_datetime
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser
import config
from packages.telegram_sender import send_message
from packages.email_sender import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

_KEYWORDS_LOWER = [kw.lower() for kw in config.KEYWORDS]
_TELEGRAM_MAX_CHARS = 4096


def _extract_entry_time(entry: Dict[str, Any]) -> Optional[datetime]:
    for field in ("updated_parsed", "published_parsed"):
        if entry.get(field):
            return datetime.fromtimestamp(timegm(entry[field]), tz=timezone.utc)

    for field in ("updated", "published"):
        if entry.get(field):
            try:
                dt = parsedate_to_datetime(entry[field])
                return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
            except Exception:
                continue

    return None


def is_entry_recent(entry: Dict[str, Any], hours: int) -> bool:
    entry_time = _extract_entry_time(entry)
    if entry_time is None:
        return True
    return entry_time > datetime.now(timezone.utc) - timedelta(hours=hours)


def find_keyword_in_entry(entry: Dict[str, Any]) -> Optional[str]:
    title = entry.get("title", "").lower()
    summary = entry.get("summary", "").lower()
    for kw_lower, kw_original in zip(_KEYWORDS_LOWER, config.KEYWORDS):
        if kw_lower in title or kw_lower in summary:
            return kw_original
    return None


def process_feed(feed_name: str, feed_url: str, hours: int) -> List[Dict[str, Any]]:
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        logging.error("Failed to parse feed %s: %s", feed_name, e)
        return []

    results = [
        {"entry": entry, "keyword": kw, "feed_name": feed_name}
        for entry in feed.entries
        if is_entry_recent(entry, hours)
        for kw in (find_keyword_in_entry(entry),)
        if kw
    ]

    logging.info("%s: %d match(es) found.", feed_name, len(results))
    return results


def _esc(entry: Dict[str, Any], field: str, default: str = "N/A") -> str:
    return html.escape(entry.get(field, default))


def format_entry_html(item: Dict[str, Any]) -> str:
    entry = item["entry"]
    url = _esc(entry, "link", "#")
    title = _esc(entry, "title")
    author = _esc(entry, "author")
    summary = _esc(entry, "summary", "No summary available.")

    return f"""
    <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #eee; border-radius: 5px;">
        <h3><b>Titulo :</b> <a href="{url}" style="text-decoration: none; color: #0056b3;">{title}</a></h3>
        <p><b>Autor : </b> {author}</p>
        <p><b>Palabra clave:</b> {html.escape(item['keyword'])}</p>
        <p><b>Resumen:</b><br>{summary}</p>
    </div>
    """


def format_entry_text(item: Dict[str, Any]) -> str:
    entry = item["entry"]
    message = f"Title: {entry.get('title', 'N/A')}\nKeyword: {item['keyword']}\nLink: {entry.get('link', '#')}"
    if len(message) > _TELEGRAM_MAX_CHARS:
        message = message[:_TELEGRAM_MAX_CHARS - 3] + "..."
    return message


def send_notifications(news_items: List[Dict[str, Any]]) -> None:
    if not news_items:
        return

    if config.NOTIFICATION_CHANNEL in ("email", "both"):
        send_email(
            config.EMAIL_RECIPIENT,
            "Resumen diario de noticias con sus palabras clave",
            "".join(format_entry_html(item) for item in news_items),
        )

    if config.NOTIFICATION_CHANNEL in ("telegram", "both"):
        for item in news_items:
            try:
                send_message(format_entry_text(item))
            except Exception as e:
                logging.error("Failed to send Telegram message: %s", e)


def collect_news() -> List[Dict[str, Any]]:
    all_entries = []
    seen_urls: set = set()

    with ThreadPoolExecutor(max_workers=len(config.FEEDS)) as executor:
        futures = {
            executor.submit(process_feed, name, url, config.HOURS_AGO): name
            for name, url in config.FEEDS.items()
        }

        for future in as_completed(futures):
            feed_name = futures[future]
            try:
                for item in future.result():
                    url = item["entry"].get("link", "")
                    if url not in seen_urls:
                        seen_urls.add(url)
                        all_entries.append(item)
                        logging.info(
                            "[%s] keyword=%s | %s",
                            feed_name, item["keyword"], item["entry"].get("title", "N/A")
                        )
            except Exception as e:
                logging.error("Unexpected error processing feed %s: %s", feed_name, e)

    return all_entries


def main():
    news_items = collect_news()
    if news_items:
        send_notifications(news_items)
    else:
        logging.info("No interesting news found across all feeds.")


if __name__ == "__main__":
    main()
