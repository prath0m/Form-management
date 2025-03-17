from django.template.loader import render_to_string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from django.conf import settings


def send_email_notification(subject, template_name, context, to_email):
    """
    Sends an email notification using a Django template for the email body.
    """
    try:
        # Render the email body using the template and context
        body = render_to_string(template_name, context)

        # Create the email
        msg = MIMEMultipart()
        msg["From"] = settings.EMAIL_HOST_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))  # Attach the email body as HTML

        # Connect to the SMTP server and send the email
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.sendmail(settings.EMAIL_HOST_USER, to_email, msg.as_string())

        print("✅ Email sent successfully! to ", to_email)
    except Exception as e:
        print(f"❌ Error sending email: {e}")
