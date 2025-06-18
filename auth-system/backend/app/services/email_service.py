from pydantic import EmailStr

from app.config import settings
from app.core.email import send_email_async
# from app.core.email import render_email_template # Uncomment if using Jinja templates

async def send_registration_verification_email(
    email_to: EmailStr, username: str, verification_token: str
) -> None:
    """
    Sends a registration verification email.
    """
    project_name = settings.EMAILS_FROM_NAME or settings.PROJECT_NAME
    subject = f"{project_name} - Verify Your Email Address"

    # Construct verification URL
    # Ensure settings.FRONTEND_URL is configured correctly
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

    # Basic HTML content
    html_content = f"""
    <html>
        <body>
            <p>Hi {username},</p>
            <p>Thanks for registering at {project_name}. Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}">{verification_url}</a></p>
            <p>This link will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS} hours.</p>
            <p>If you did not register, please ignore this email.</p>
            <p>Thanks,</p>
            <p>The {project_name} Team</p>
        </body>
    </html>
    """
    # If using Jinja templates:
    # html_content = render_email_template(
    #     "verification.html",
    #     {"username": username, "project_name": project_name, "verification_url": verification_url, "expire_hours": settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS}
    # )

    await send_email_async(to_email=email_to, subject=subject, html_content=html_content)

async def send_password_reset_email(
    email_to: EmailStr, username: str, reset_token: str
) -> None:
    """
    Sends a password reset email.
    """
    project_name = settings.EMAILS_FROM_NAME or settings.PROJECT_NAME
    subject = f"{project_name} - Password Reset Request"

    # Construct password reset URL
    # Ensure settings.FRONTEND_URL is configured correctly
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    # Basic HTML content
    html_content = f"""
    <html>
        <body>
            <p>Hi {username},</p>
            <p>You (or someone else) requested a password reset for your account at {project_name}.</p>
            <p>If this was you, click the link below to reset your password:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <p>This link will expire in {settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS} hour(s).</p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <p>Thanks,</p>
            <p>The {project_name} Team</p>
        </body>
    </html>
    """
    # If using Jinja templates:
    # html_content = render_email_template(
    #     "password_reset.html",
    #     {"username": username, "project_name": project_name, "reset_url": reset_url, "expire_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS}
    # )

    await send_email_async(to_email=email_to, subject=subject, html_content=html_content)

async def send_password_change_notification_email(email_to: EmailStr, username: str) -> None:
    """
    Sends a notification after a password has been successfully changed.
    """
    project_name = settings.EMAILS_FROM_NAME or settings.PROJECT_NAME
    subject = f"{project_name} - Your Password Has Been Changed"

    html_content = f"""
    <html>
        <body>
            <p>Hi {username},</p>
            <p>This email confirms that the password for your account at {project_name} has been changed recently.</p>
            <p>If you did not make this change, please contact our support team immediately.</p>
            <p>Thanks,</p>
            <p>The {project_name} Team</p>
        </body>
    </html>
    """
    await send_email_async(to_email=email_to, subject=subject, html_content=html_content)
