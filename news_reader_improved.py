#!/usr/bin/python3
"""
This script checks RSS feeds for news containing specific keywords within a
certain time frame and sends an email notification.
"""

from datetime import datetime, timedelta, timezone
from calendar import timegm
from email.utils import parsedate_to_datetime
import logging
import html
import config
from email_sender.sender import send_email

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

try:
    import feedparser
except ImportError:
    logging.error("Missing dependency 'feedparser'. Install with: pip install -r requirements.txt")
    raise SystemExit(1)


def _extract_entry_time(entry):
    """
    Returns a UTC datetime from common feedparser timestamp fields.
    """
    parsed_time = entry.get("updated_parsed") or entry.get("published_parsed")
    if parsed_time:
        return datetime.fromtimestamp(timegm(parsed_time), tz=timezone.utc)

    string_time = entry.get("updated") or entry.get("published")
    if not string_time:
        return None

    try:
        dt = parsedate_to_datetime(string_time)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def search_news(feed_url, keywords, hours):
    """
    Searches an RSS feed for entries containing specified keywords within a
    given time frame.

    Args:
        feed_url (str): The URL of the RSS feed.
        keywords (list): A list of keywords to search for.
        hours (int): The number of hours to look back for new entries.

    Returns:
        list: A list of dictionaries, each containing an 'entry' and the 'keyword' that triggered it.
    """
    interesting_entries = []
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(hours=hours)
    feed = feedparser.parse(feed_url)

    for entry in feed.entries:
        entry_time = _extract_entry_time(entry)
        is_recent = entry_time is None or entry_time > time_threshold
        if is_recent:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            for keyword in keywords:
                if (keyword.lower() in title.lower() or
                        keyword.lower() in summary.lower()):
                    interesting_entries.append({"entry": entry, "keyword": keyword})
                    break  # Move to the next entry once a keyword is found
    return interesting_entries


def format_email_body(entries):
    """
    Formats a list of feed entries (with associated keywords) into an HTML email body.

    Args:
        entries (list): A list of dictionaries, each containing an 'entry' and the 'keyword'.

    Returns:
        str: An HTML formatted string for the email body.
    """
    body_parts = []
    for item in entries:
        entry = item["entry"]
        keyword = item["keyword"]
        title = html.escape(entry.get("title", "N/A"))
        author = html.escape(entry.get("author", "N/A"))
        url = html.escape(entry.get("link", "#"))
        # Sanitize summary - escape any HTML in the summary to ensure it's displayed as plain text
        summary = html.escape(entry.get("summary", "No summary available."))

        news_item_html = f"""
        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #eee; border-radius: 5px;">
            <h3><b>Titulo :</b> <a href="{url}" style="text-decoration: none; color: #0056b3;">{title}</a></h3>
            <p><b>Autor : </b> {author}</p>
            <p><b>Palabra clave:</b> {html.escape(keyword)}</p>
            <p>{summary}</p>
        </div>
        """
        body_parts.append(news_item_html)
    return "".join(body_parts)


def main():
    """
    Main function to run the news reader.
    """
    all_interesting_entries = [] # New list to collect all entries
    all_found_news_titles = [] # To log all found news without repetition

    for feed_name, feed_url in config.FEEDS.items():
        logging.info("Searching for news in %s...", feed_name)
        interesting_entries_for_feed = search_news(feed_url, config.KEYWORDS, config.HOURS_AGO)

        if interesting_entries_for_feed:
            for item in interesting_entries_for_feed:
                entry = item["entry"]
                keyword = item["keyword"]
                title = entry.get("title", "N/A")
                if title not in all_found_news_titles: # Avoid duplicate logging/entries
                    logging.info(
                        "Found interesting news in %s (keyword: %s): %s",
                        feed_name,
                        keyword,
                        title
                    )
                    all_interesting_entries.append(item)
                    all_found_news_titles.append(title)
        else:
            logging.info("No interesting news found in %s.", feed_name)

    if all_interesting_entries:
        email_body = format_email_body(all_interesting_entries)
        subject = "Resumen diario de noticias con sus palabras clave" # Generic subject for all news
        send_email(config.EMAIL_RECIPIENT, subject, email_body)
    else:
        logging.info("No interesting news found across all feeds to send an email.")


if __name__ == "__main__":
    main()
