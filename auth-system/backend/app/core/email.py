import smtplib
from email.message import EmailMessage as PyEmailMessage # Renamed to avoid conflict if we define our own EmailMessage model/schema
from typing import Optional
import logging

from app.config import settings
from pydantic import EmailStr

# Configure logging
logger = logging.getLogger(__name__)
# Example: You might want to set up specific logging for email successes/failures
# logging.basicConfig(level=settings.LOGGING_LEVEL.upper())


async def send_email_async(
    to_email: EmailStr,
    subject: str,
    html_content: str,
) -> None:
    if not settings.EMAILS_ENABLED:
        logger.info(f"Email sending disabled. Mock sending to: {to_email}")
        print(f"--- Mock Email Start ---")
        print(f"To: {to_email}")
        print(f"From: {settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>")
        print(f"Subject: {subject}")
        print(f"Content (HTML):\n{html_content}")
        print(f"--- Mock Email End ---")
        return

    assert settings.EMAILS_FROM_EMAIL, "EMAILS_FROM_EMAIL setting is required but not set."
    assert settings.SMTP_HOST, "SMTP_HOST setting is required but not set."
    assert settings.SMTP_PORT is not None, "SMTP_PORT setting is required but not set."

    msg = PyEmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to_email
    msg.set_content(html_content, subtype="html")

    try:
        # Note: smtplib is synchronous. For a fully async non-blocking app,
        # a library like 'aiosmtplib' should be used, or smtplib operations
        # should be run in a separate thread pool (e.g., using asyncio.to_thread in Python 3.9+).
        # This example uses synchronous smtplib for simplicity as per instructions.
        logger.info(f"Attempting to send email to {to_email} via {settings.SMTP_HOST}:{settings.SMTP_PORT}")

        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        if settings.SMTP_TLS:
            server.starttls() # Secure the connection

        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.send_message(msg)
        server.quit()
        logger.info(f"Email successfully sent to {to_email} with subject '{subject}'")

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error sending email to {to_email}: {e}")
        # Potentially raise a custom exception or handle more gracefully
        raise
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"SMTP Server Disconnected error sending email to {to_email}: {e}")
        raise
    except smtplib.SMTPException as e: # Catch other SMTP related errors
        logger.error(f"SMTP Error sending email to {to_email}: {e}")
        raise
    except Exception as e: # Catch any other unexpected errors
        logger.error(f"Unexpected error sending email to {to_email}: {e}")
        raise

# To use Jinja2 templates in the future (requires jinja2 installation):
# from jinja2 import Environment, FileSystemLoader
#
# if settings.EMAIL_TEMPLATES_DIR:
#     template_loader = FileSystemLoader(settings.EMAIL_TEMPLATES_DIR)
#     template_env = Environment(loader=template_loader)
#
# def render_email_template(template_name: str, context: dict) -> str:
#     if not hasattr(template_env, 'get_template'):
#         raise RuntimeError("Email templates not configured properly.")
#     template = template_env.get_template(template_name)
#     return template.render(context)
