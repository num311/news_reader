import os
import yagmail

def send_email(receiver_email, subject, contents, attachments=None):
    """
    Sends an email using yagmail.

    Args:
        receiver_email (str): The email address of the recipient.
        subject (str): The subject of the email.
        contents (str or list): The content of the email. Can be a string or a list of strings/file paths.
        attachments (list, optional): A list of file paths to attach. Defaults to None.
    """
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("Error: EMAIL_SENDER and/or EMAIL_PASSWORD environment variables are not set.")
        return

    try:
        yag = yagmail.SMTP(sender_email, sender_password)
        yag.send(
            to=receiver_email,
            subject=subject,
            contents=contents,
            attachments=attachments
        )
        print(f"Email sent successfully to {receiver_email}!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    # Example usage (requires EMAIL_SENDER and EMAIL_PASSWORD environment variables to be set):
    # import os
    # os.environ["EMAIL_SENDER"] = "your_email@gmail.com"
    # os.environ["EMAIL_PASSWORD"] = "your_app_password"
    # send_email("recipient@example.com", "Test Subject", "Hello from Python!", attachments=["path/to/your/file.pdf"])
    pass