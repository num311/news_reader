#!/usr/bin/python3
"""
This script checks RSS feeds for news containing specific keywords within a
certain time frame and sends an email notification.
"""

from datetime import datetime, timedelta
from time import mktime
import logging
import os
import json
from typing import Dict, Set
import feedparser
import yagmail
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_news(feed_url, keywords, hours):
    """
    Searches an RSS feed for entries containing specified keywords within a
    given time frame.

    Args:
        feed_url (str): The URL of the RSS feed.
        keywords (list): A list of keywords to search for.
        hours (int): The number of hours to look back for new entries.

    Returns:
        list: A list of tuples, where each tuple contains a feedparser entry
              object and the keyword that was found.
    """
    found_items = []
    now = datetime.now()
    time_threshold = now - timedelta(hours=hours)
    feed = feedparser.parse(feed_url)

    for entry in feed.entries:
        entry_time = datetime.fromtimestamp(mktime(entry['updated_parsed']))
        if entry_time > time_threshold:
            for keyword in keywords:
                if (keyword.lower() in entry['title'].lower() or
                        keyword.lower() in entry['summary'].lower()):
                    found_items.append((entry, keyword))
                    break  # Move to the next entry once a keyword is found
    return found_items

def format_email_body(entries):
    """
    Formats a list of feed entries into an HTML email body.

    Args:
        entries (list): A list of feedparser entry objects.

    Returns:
        str: An HTML formatted string for the email body.
    """
    body = ""
    for entry in entries:
        title = entry.get('title', 'N/A')
        author = entry.get('author', 'N/A')
        url = entry.get('link', '#')
        summary = entry.get('summary', 'No summary available.')
        body += f"<b>Titulo :</b> {title}<br>"
        body += f"<b>Autor : </b> {author}<br>"
        body += f"<b>Enlace : </b><a href='{url}'>{url}</a><br>"
        body += f"<p>{summary}</p><hr>"
    return body

def format_telegram_message(entries):
    """
    Formats a list of feed entries into a message for Telegram.

    Args:
        entries (list): A list of feedparser entry objects.

    Returns:
        str: A string formatted for Telegram.
    """
    message = ""
    for entry in entries:
        title = entry.get('title', 'N/A')
        url = entry.get('link', '#')
        message += f"*{title}*\n"
        message += f"[Leer más]({url})\n\n"
    return message

def send_email(recipient, subject, body):
    """
    Sends an email using yagmail.

    Args:
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        body (str): The HTML body of the email.
    """
    try:
        email_sender = os.environ.get("EMAIL_SENDER")
        email_password = os.environ.get("EMAIL_PASSWORD")
        yag = yagmail.SMTP(user=email_sender, password=email_password)
        yag.send(
            to=recipient,
            subject=subject,
            contents=body
        )
        logging.info("Email sent successfully to %s", recipient)
    except Exception as e:
        logging.error("Failed to send email: %s", e)

def send_telegram_message(subject, body):
    """
    Sends a message to a Telegram chat using the bot API.

    Args:
        subject (str): The subject of the message (used as a title).
        body (str): The message body.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Telegram messages have a size limit, so we may need to split the message
    # For simplicity, we send the subject and body as separate parts if needed,
    # or combine them if short enough.
    full_message = f"*{subject}*\n\n{body}"

    params = {
        "chat_id": chat_id,
        "text": full_message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=params)
        response.raise_for_status()
        logging.info("Telegram message sent successfully.")
    except requests.exceptions.RequestException as e:
        logging.error("Failed to send Telegram message: %s", e)


def main():
    """
    Main function to run the news reader.
    """
    feeds_str = os.environ.get("FEEDS", "")
    feeds = dict(item.split("=") for item in feeds_str.split(","))
    keywords_str = os.environ.get("KEYWORDS", "")
    keywords = [keyword.strip() for keyword in keywords_str.split(",")]
    hours_ago = int(os.environ.get("HOURS_AGO", 8))
    notification_channel = os.environ.get("NOTIFICATION_CHANNEL", "email")
    email_recipient = os.environ.get("EMAIL_RECIPIENT")

    # Load store of previously sent items
    sent_store_path = os.environ.get("SENT_STORE_PATH", "sent_items.json")
    def load_sent_items(path: str) -> Dict[str, Set[str]]:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # convert lists to sets for faster lookup
            return {k: set(v) for k, v in data.items()}
        except Exception:
            return {}

    def save_sent_items(path: str, store: Dict[str, Set[str]]):
        serializable = {k: list(v) for k, v in store.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)

    def entry_id(entry) -> str:
        return entry.get('id') or entry.get('link') or entry.get('title')

    sent_items = load_sent_items(sent_store_path)

    for feed_name, feed_url in feeds.items():
        logging.info("Searching for news in %s...", feed_name)
        found_items = search_news(feed_url, keywords, hours_ago)
        if found_items:
            # Filter out entries already sent previously
            previously_sent = sent_items.get(feed_url, set())
            new_items = []
            for entry, kw in found_items:
                eid = entry_id(entry)
                if eid not in previously_sent:
                    new_items.append((entry, kw))

            if not new_items:
                logging.info("No new items to notify for %s (all were already sent).", feed_name)
                continue

            interesting_entries = [item[0] for item in new_items]
            found_keywords = sorted(list(set(item[1] for item in found_items)))
            
            log_message = (f"Found {len(interesting_entries)} interesting news in "
                           f"'{feed_name}' matching keywords: {found_keywords}")
            logging.info(log_message)
            
            subject = f"Noticias de {feed_name.capitalize()} sobre: {', '.join(found_keywords)}"

            if notification_channel.lower() == "email":
                body = format_email_body(interesting_entries)
                send_email(email_recipient, subject, body)
            elif notification_channel.lower() == "telegram":
                body = format_telegram_message(interesting_entries)
                send_telegram_message(subject, body)
            else:
                logging.warning("No valid notification channel configured. Please check NOTIFICATION_CHANNEL")
            # Mark sent entries and persist
            sent_set = sent_items.setdefault(feed_url, set())
            for entry in interesting_entries:
                sent_set.add(entry_id(entry))
            try:
                save_sent_items(sent_store_path, sent_items)
            except Exception as e:
                logging.error("Failed to update sent items store: %s", e)
        else:
            logging.info("No interesting news found in %s.", feed_name)

if __name__ == "__main__":
    main()
