import os
import yagmail
from dotenv import load_dotenv

load_dotenv()


def send_email(subject: str, body: str, attachments: list[str] | None = None):
    """Send an email to yourself via Gmail.

    Set these environment variables:
        GMAIL_ADDRESS: Your Gmail address
        GMAIL_APP_PASSWORD: Your Google App Password (from https://myaccount.google.com/apppasswords)
    """
    email = os.environ.get("GMAIL_ADDRESS")
    password = os.environ.get("GMAIL_APP_PASSWORD")

    if not email or not password:
        raise ValueError("Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables")

    yag = yagmail.SMTP(email, password)
    yag.send(to=email, subject=subject, contents=body, attachments=attachments)
    print(f"Email sent: {subject}")


if __name__ == "__main__":
    # Example usage
    send_email(
        subject="Test from Premier League Stats",
        body="Hello! This is a test email."
    )
