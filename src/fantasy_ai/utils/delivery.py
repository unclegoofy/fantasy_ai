import os
import smtplib
import requests
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def _mask(s): return s[:2] + "****" + s[-2:] if s else "None"

# Debug print to confirm .env is loading
print("SMTP config:", {
    "provider": os.getenv("EMAIL_PROVIDER"),
    "host": os.getenv("SMTP_HOST"),
    "port": os.getenv("SMTP_PORT"),
    "user": os.getenv("SMTP_USER"),
    "pass": _mask(os.getenv("SMTP_PASS")),
    "to": os.getenv("EMAIL_TO"),
    "send_from": os.getenv("SMTP_FROM"),
    "sendgrid_key": _mask(os.getenv("SENDGRID_API_KEY"))
})

def send_email(subject: str, body: str):
    if not body or len(body.strip()) < 10:
        print("⚠️ Email body appears empty or too short — skipping send.")
        return

    provider = os.getenv("EMAIL_PROVIDER", "gmail").lower()
    print(f"📤 Email body preview:\n{body[:300]}...\n---")

    if provider == "sendgrid":
        send_via_sendgrid(subject, body)
    elif provider == "gmail":
        send_via_gmail(subject, body)
    else:
        print(f"❌ Unsupported EMAIL_PROVIDER: {provider}")

def send_via_gmail(subject: str, body: str):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    email_to = os.getenv("EMAIL_TO")
    send_from = os.getenv("SMTP_FROM") or smtp_user

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass, email_to]):
        print("❌ Missing Gmail SMTP configuration in .env")
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
        print("📧 Email sent successfully via Gmail.")
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail delivery failed: Authentication error — {e.smtp_error.decode()}")
    except Exception as e:
        print(f"❌ Gmail delivery failed: {e}")

def send_via_sendgrid(subject: str, body: str):
    api_key = os.getenv("SENDGRID_API_KEY")
    email_to = os.getenv("EMAIL_TO")
    send_from = os.getenv("SMTP_FROM")

    if not all([api_key, email_to, send_from]):
        print("❌ Missing SendGrid configuration in .env")
        return

    payload = {
        "personalizations": [{"to": [{"email": email_to}]}],
        "from": {"email": send_from},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers)
        if response.status_code == 202:
            print("📧 Email sent successfully via SendGrid.")
        else:
            print(f"❌ SendGrid delivery failed: {response.status_code} — {response.text}")
    except Exception as e:
        print(f"❌ SendGrid delivery error: {e}")

def send_discord(body: str):
    webhook = os.getenv("DISCORD_WEBHOOK")
    if not webhook:
        print("❌ DISCORD_WEBHOOK not set in .env")
        return

    if not body or len(body.strip()) < 10:
        print("⚠️ Discord body appears empty or too short — skipping send.")
        return

    print(f"📤 Discord body preview:\n{body[:300]}...\n---")

    chunks = [body[i:i+1700] for i in range(0, len(body), 1700)]

    for i, chunk in enumerate(chunks):
        payload = {"content": f"📦 Digest Part {i+1}:\n{chunk}"}
        try:
            response = requests.post(webhook, json=payload)
            if response.status_code == 204:
                print(f"💬 Discord message sent (Part {i+1}).")
            else:
                print(f"❌ Discord delivery failed: {response.status_code} {response.text}")
        except Exception as e:
            print(f"❌ Discord delivery error: {e}")