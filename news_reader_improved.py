#!/usr/bin/python3
"""
This script checks RSS feeds for news containing specific keywords within a
certain time frame and sends an email notification.
"""

from datetime import datetime, timedelta
from time import mktime
import logging
import feedparser
import yagmail
import config

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
        list: A list of feedparser entry objects that match the criteria.
    """
    interesting_entries = []
    now = datetime.now()
    time_threshold = now - timedelta(hours=hours)
    feed = feedparser.parse(feed_url)

    for entry in feed.entries:
        entry_time = datetime.fromtimestamp(mktime(entry['updated_parsed']))
        if entry_time > time_threshold:
            for keyword in keywords:
                if (keyword.lower() in entry['title'].lower() or
                        keyword.lower() in entry['summary'].lower()):
                    interesting_entries.append(entry)
                    break  # Move to the next entry once a keyword is found
    return interesting_entries

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

def send_notification_email(recipient, subject, body):
    """
    Sends an email using yagmail.

    Args:
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        body (str): The HTML body of the email.
    """
    try:
        yag = yagmail.SMTP(user=config.EMAIL_SENDER, password=config.EMAIL_PASSWORD)
        yag.send(
            to=recipient,
            subject=subject,
            contents=body
        )
        logging.info("Email sent successfully to %s", recipient)
    except Exception as e:
        logging.error("Failed to send email: %s", e)

def main():
    """
    Main function to run the news reader.
    """
    for feed_name, feed_url in config.FEEDS.items():
        logging.info("Searching for news in %s...", feed_name)
        interesting_entries = search_news(feed_url, config.KEYWORDS, config.HOURS_AGO)

        if interesting_entries:
            logging.info("Found %d interesting news in %s.", len(interesting_entries), feed_name)
            email_body = format_email_body(interesting_entries)
            subject = f"Noticias de {feed_name.capitalize()} con sus palabras clave"
            send_notification_email(config.EMAIL_RECIPIENT, subject, email_body)
        else:
            logging.info("No interesting news found in %s.", feed_name)

if __name__ == "__main__":
    main()
