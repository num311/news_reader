import os
import requests
from dotenv import load_dotenv

load_dotenv()



def send_telegram_message(message: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")
    if not chat_id:
        raise ValueError("TELEGRAM_CHAT_ID environment variable not set.")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        print(f"Message sent: {message}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")
        raise

def send_message(message: str):
    """
    Sends a message to the configured Telegram chat.
    This function is intended to be called by other modules.
    """
    send_telegram_message(message)

def test_send():
    print("Attempting to send a test message...")
    try:
        send_message("Hello from your Python Telegram bot! This is a test message.")
        print("Test message sent successfully!")
    except ValueError as e:
        print(f"Configuration error: {e}. Please ensure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set as environment variables.")
    except Exception as e:
        print(f"An unexpected error occurred during test send: {e}")

if __name__ == '__main__':
    test_send()
