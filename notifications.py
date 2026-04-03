import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import os
import ssl

def send_email(to_email, subject, body):
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    
    if not sender or not password:
        print(f"⚠️ [SIMULATION] Email to {to_email} | Subject: {subject} | Body: {body}")
        return False
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def send_whatsapp(to_phone, message):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_whatsapp = os.environ.get("TWILIO_WHATSAPP_NUMBER")
    
    if not account_sid or not auth_token:
        print(f"⚠️ [SIMULATION] WhatsApp to {to_phone} | Message: {message}")
        return False
        
    client = Client(account_sid, auth_token)
    try:
        msg = client.messages.create(
            body=message,
            from_=f"whatsapp:{from_whatsapp}",
            to=f"whatsapp:{to_phone}"
        )
        print(f"✅ WhatsApp message sent successfully to {to_phone}")
        return True
    except Exception as e:
        print(f"❌ Error sending WhatsApp: {e}")
        return False
