#!/usr/bin/python3
"""
This script checks RSS feeds for news containing specific keywords within a
certain time frame and sends notifications via email or Telegram.
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def _extract_entry_time(entry: Dict[str, Any]) -> Optional[datetime]:
    """
    Returns a UTC datetime object from common feedparser timestamp fields.
    Prioritizes parsed fields over raw string fields.
    """
    # Try using pre-parsed fields first (more reliable)
    for field in ("updated_parsed", "published_parsed"):
        if entry.get(field):
            return datetime.fromtimestamp(timegm(entry[field]), tz=timezone.utc)

    # Fallback to parsing raw string fields
    for field in ("updated", "published"):
        if not entry.get(field):
            continue
        try:
            dt = parsedate_to_datetime(entry[field])
            # Ensure timezone is UTC
            return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
        except Exception:
            continue  # Try next field if parsing fails

    return None


def is_entry_recent(entry: Dict[str, Any], hours: int) -> bool:
    """
    Checks if a feed entry was published within the last 'hours'.
    """
    entry_time = _extract_entry_time(entry)
    if entry_time is None:
        # If no date is found, we assume it's recent enough to be safe, 
        # or you might prefer to skip undated entries.
        return True
    
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
    return entry_time > time_threshold


def find_keyword_in_entry(entry: Dict[str, Any], keywords: List[str]) -> Optional[str]:
    """
    Checks if any keyword exists in the entry's title or summary.
    Returns the first matching keyword, or None.
    """
    title = entry.get("title", "").lower()
    summary = entry.get("summary", "").lower()
    
    for keyword in keywords:
        kw_lower = keyword.lower()
        if kw_lower in title or kw_lower in summary:
            return keyword
            
    return None


def process_feed(feed_name: str, feed_url: str, keywords: List[str], hours: int) -> List[Dict[str, Any]]:
    """
    Fetches and filters entries from a single RSS feed.
    Returns a list of interesting entries with their metadata.
    """
    logging.info("Searching for news in %s...", feed_name)
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        logging.error("Failed to parse feed %s: %s", feed_name, e)
        return []

    interesting_entries = []
    
    for entry in feed.entries:
        if is_entry_recent(entry, hours):
            keyword = find_keyword_in_entry(entry, keywords)
            if keyword:
                interesting_entries.append({
                    "entry": entry,
                    "keyword": keyword,
                    "feed_name": feed_name
                })
                
    if not interesting_entries:
        logging.info("No interesting news found in %s.", feed_name)
        
    return interesting_entries


def format_entry_html(item: Dict[str, Any]) -> str:
    """
    Formats a single news item as an HTML block for email.
    """
    entry = item["entry"]
    keyword = item["keyword"]
    
    title = html.escape(entry.get("title", "N/A"))
    author = html.escape(entry.get("author", "N/A"))
    url = html.escape(entry.get("link", "#"))
    summary = html.escape(entry.get("summary", "No summary available."))

    return f"""
    <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #eee; border-radius: 5px;">
        <h3><b>Titulo :</b> <a href="{url}" style="text-decoration: none; color: #0056b3;">{title}</a></h3>
        <p><b>Autor : </b> {author}</p>
        <p><b>Palabra clave:</b> {html.escape(keyword)}</p>
        <p><b>Resumen:</b><br>{summary}</p>
    </div>
    """


def format_entry_text(item: Dict[str, Any]) -> str:
    """
    Formats a single news item as plain text for Telegram/Logs.
    """
    entry = item["entry"]
    return f"Title: {entry.get('title', 'N/A')}\nKeyword: {item['keyword']}\nLink: {entry.get('link', '#')}"


def send_notifications(news_items: List[Dict[str, Any]]) -> None:
    """
    Sends notifications for the collected news items based on configuration.
    """
    if not news_items:
        return

    # Email Notification
    if config.NOTIFICATION_CHANNEL in ["email", "both"]:
        email_body_parts = [format_entry_html(item) for item in news_items]
        email_body = "".join(email_body_parts)
        subject = "Resumen diario de noticias con sus palabras clave"
        send_email(config.EMAIL_RECIPIENT, subject, email_body)

    # Telegram Notification
    if config.NOTIFICATION_CHANNEL in ["telegram", "both"]:
        for item in news_items:
            message = format_entry_text(item)
            try:
                send_message(message)
                logging.info(f"Sent Telegram message: {message.splitlines()[0]}")
            except Exception as e:
                logging.error(f"Failed to send Telegram message: {e}")


def collect_news() -> List[Dict[str, Any]]:
    """
    Fetches all configured feeds in parallel and collects interesting news.
    Handles deduplication based on title.
    """
    all_interesting_entries = []
    seen_titles = set()

    with ThreadPoolExecutor(max_workers=len(config.FEEDS)) as executor:
        futures = {
            executor.submit(process_feed, feed_name, feed_url, config.KEYWORDS, config.HOURS_AGO): feed_name
            for feed_name, feed_url in config.FEEDS.items()
        }

        for future in as_completed(futures):
            feed_name = futures[future]
            try:
                feed_entries = future.result()
            except Exception as e:
                logging.error("Unexpected error processing feed %s: %s", feed_name, e)
                continue

            for item in feed_entries:
                title = item["entry"].get("title", "N/A")

                if title not in seen_titles:
                    seen_titles.add(title)
                    all_interesting_entries.append(item)
                    logging.info(
                        "Found interesting news in %s (keyword: %s): %s",
                        feed_name, item["keyword"], title
                    )

    return all_interesting_entries


def main():
    """
    Main execution flow.
    """
    news_items = collect_news()
    
    if news_items:
        send_notifications(news_items)
    else:
        logging.info("No interesting news found across all feeds.")


if __name__ == "__main__":
    main()
