import smtplib, os
from dotenv import load_dotenv

load_dotenv()

smtp_host = os.getenv("SMTP_HOST")
smtp_port = int(os.getenv("SMTP_PORT"))
smtp_user = os.getenv("SMTP_USER")
smtp_pass = os.getenv("SMTP_PASS")
send_from = os.getenv("SEND_FROM") or smtp_user
email_to = os.getenv("EMAIL_TO")

print(f"Testing SMTP login for {smtp_user}...")

try:
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(
            send_from,
            [email_to],
            "Subject: FantasyAI SMTP Test\n\nThis is a test email from FantasyAI."
        )
    print("✅ Email sent successfully.")
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ Authentication failed: {e.smtp_error.decode()}")
except Exception as e:
    print(f"❌ Email send failed: {e}")