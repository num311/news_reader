# News Reader

This script is a news reader that fetches articles from various RSS feeds and searches for specific keywords within their content. If a keyword is found, it sends a notification via email, Telegram, or both, utilizing dedicated modules for modularity.

## Configuration

The `config.py` file contains the following configurable options:

*   **Notification Channel**: Configures how notifications are sent. Options are `"email"`, `"telegram"`, or `"both"`.
*   **Email Settings**: Configures the sender, recipient, and password for email notifications. **(Note: Email sending is now handled by the `email_sender` module, which retrieves sender credentials from environment variables `EMAIL_SENDER` and `EMAIL_PASSWORD`.)**
*   **Telegram Settings**: Telegram delivery uses environment variables only. You must set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
*   **Feeds**: A dictionary of RSS feed names and their corresponding URLs.
*   **Keywords**: A list of keywords to search for within the news articles.
*   **Hours Ago**: The number of hours to look back for new articles.

## How it Works

1.  Fetches articles from the configured RSS feeds.
2.  Parses the content of each article.
3.  Searches for any of the defined keywords within the article content.
4.  If a keyword is found, a notification is sent using the configured channel (`email`, `telegram`, or `both`).

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Set the required environment variables (or create a `.env` file):

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export EMAIL_SENDER="your_email@example.com"
export EMAIL_PASSWORD="your_email_password"
```

Run the script:

```bash
python news_reader_improved.py
```

## Tests

Install pytest and run the test suite:

```bash
pip install pytest
python -m pytest tests/ -v
```

## Run with Docker

Build the image from the `dockerfile`:

```bash
docker build -f dockerfile -t news-reader .
```

Run the container (without `.env` file):

```bash
docker run --rm \
  -e EMAIL_SENDER="your_email@example.com" \
  -e EMAIL_PASSWORD="your_email_password" \
  -e TELEGRAM_BOT_TOKEN="your_bot_token" \
  -e TELEGRAM_CHAT_ID="your_chat_id" \
  news-reader
```

Using a `.env` file is optional. If you prefer it, you can still run:

```bash
docker run --rm --env-file .env news-reader
```
