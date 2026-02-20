# News Reader

This script is a news reader that fetches articles from various RSS feeds and searches for specific keywords within their content. If a keyword is found, it sends a notification via email, utilizing a dedicated email sending module for modularity.

## Configuration

The `config.py` file contains the following configurable options:

*   **Email Settings**: Configures the sender, recipient, and password for email notifications. **(Note: Email sending is now handled by the `email_sender` module, which retrieves sender credentials from environment variables `EMAIL_SENDER` and `EMAIL_PASSWORD`.)**
*   **Feeds**: A dictionary of RSS feed names and their corresponding URLs.
*   **Keywords**: A list of keywords to search for within the news articles.
*   **Hours Ago**: The number of hours to look back for new articles.

## How it Works

1.  Fetches articles from the configured RSS feeds.
2.  Parses the content of each article.
3.  Searches for any of the defined keywords within the article content.
4.  If a keyword is found, an email notification is sent to the configured recipient using the `email_sender` module.

## Run with Docker

Build the image from the `dockerfile`:

```bash
docker build -f dockerfile -t news-reader .
```

Run the container:

```bash
docker run --rm --env-file .env news-reader
```

If you do not use a `.env` file, pass required variables with `-e` (for example `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`).
