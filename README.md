# News Reader

This script is a news reader that fetches articles from various RSS feeds and searches for specific keywords within their content. If a keyword is found, it sends a notification via email.

## Configuration

The `config.py` file contains the following configurable options:

*   **Email Settings**: Configures the sender, recipient, and password for email notifications.
*   **Feeds**: A dictionary of RSS feed names and their corresponding URLs.
*   **Keywords**: A list of keywords to search for within the news articles.
*   **Hours Ago**: The number of hours to look back for new articles.

## How it Works

1.  Fetches articles from the configured RSS feeds.
2.  Parses the content of each article.
3.  Searches for any of the defined keywords within the article content.
4.  If a keyword is found, an email notification is sent to the configured recipient.
