import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

EMAIL_ADDRESS = os.getenv("ALERT_EMAIL")
EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")
TO_EMAIL = os.getenv("ALERT_RECEIVER_EMAIL")
print("Sender:", EMAIL_ADDRESS)
print("Receiver:", TO_EMAIL)
print(repr(EMAIL_PASSWORD))
print(f"Length: {len(EMAIL_PASSWORD)}")


msg = EmailMessage()
msg['Subject'] = 'Test Panic Alert'
msg['From'] = EMAIL_ADDRESS
msg['To'] = TO_EMAIL
msg.set_content("This is a test panic alert message.")

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
    print("✅ Email sent successfully.")
except Exception as e:
    print("❌ Email failed:", e)
