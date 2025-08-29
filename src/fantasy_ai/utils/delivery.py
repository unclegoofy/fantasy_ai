import os
import smtplib
import requests
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Debug print to confirm .env is loading
print("SMTP config:", {
    "host": os.getenv("SMTP_HOST"),
    "port": os.getenv("SMTP_PORT"),
    "user": os.getenv("SMTP_USER"),
    "pass": os.getenv("SMTP_PASS"),
    "to": os.getenv("EMAIL_TO"),
    "send_from": os.getenv("SEND_FROM")
})

def send_email(subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    email_to = os.getenv("EMAIL_TO")
    send_from = os.getenv("SEND_FROM") or smtp_user  # fallback to SMTP_USER

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass, email_to]):
        print("❌ Missing SMTP configuration in .env")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = send_from
    msg["To"] = email_to
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        print("📧 Email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Email delivery failed: Authentication error — {e.smtp_error.decode()}")
    except Exception as e:
        print(f"❌ Email delivery failed: {e}")

def send_discord(body: str):
    webhook = os.getenv("DISCORD_WEBHOOK")
    if not webhook:
        print("❌ DISCORD_WEBHOOK not set in .env")
        return

    # Split message into safe chunks under Discord's 2000-character limit
    chunks = [body[i:i+1700] for i in range(0, len(body), 1700)]

    for chunk in chunks:
        try:
            response = requests.post(webhook, json={"content": chunk})
            if response.status_code == 204:
                print("💬 Discord message sent.")
            else:
                print(f"❌ Discord delivery failed: {response.status_code} {response.text}")
        except Exception as e:
            print(f"❌ Discord delivery error: {e}")