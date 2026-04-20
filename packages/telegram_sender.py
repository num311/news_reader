import logging
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_message(message: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")
    if not chat_id:
        raise ValueError("TELEGRAM_CHAT_ID environment variable not set.")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    logging.info("Telegram message sent: %s", message.splitlines()[0])
    return response.json()


if __name__ == "__main__":
    try:
        send_message("Hello from your Python Telegram bot! This is a test message.")
    except Exception as e:
        logging.error("Test send failed: %s", e)
