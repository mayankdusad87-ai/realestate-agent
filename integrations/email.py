"""
Email sender via SMTP.

Supports HTML bodies, plain-text fallback, and file attachments.
Uses Python's built-in smtplib — no external email SDK required.
"""
import logging
import smtplib
from dataclasses import dataclass
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from config import SMTP_HOST, SMTP_PORT, SMTP_USE_TLS

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmailResult:
    """Immutable result of a single email send attempt."""

    to: str
    success: bool
    error: str | None = None


def send_email(
    to: str,
    subject: str,
    body_html: str,
    *,
    smtp_user: str,
    smtp_password: str,
    from_addr: str | None = None,
    body_text: str | None = None,
    attachments: list[str | Path] | None = None,
) -> EmailResult:
    """Send an email via SMTP.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body_html: HTML email body.
        smtp_user: SMTP login username.
        smtp_password: SMTP login password.
        from_addr: Sender address (defaults to smtp_user).
        body_text: Optional plain-text fallback body.
        attachments: Optional list of file paths to attach.
    """
    if not to or not subject:
        return EmailResult(to=to, success=False, error="Recipient and subject are required")

    sender = from_addr or smtp_user
    msg = MIMEMultipart("mixed")
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject

    # Attach text parts inside an "alternative" sub-part
    alt = MIMEMultipart("alternative")
    if body_text:
        alt.attach(MIMEText(body_text, "plain"))
    alt.attach(MIMEText(body_html, "html"))
    msg.attach(alt)

    # Attach files
    for file_path in attachments or []:
        path = Path(file_path)
        if not path.exists():
            logger.warning("Attachment not found, skipping: %s", path)
            continue
        part = MIMEBase("application", "octet-stream")
        part.set_payload(path.read_bytes())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={path.name}")
        msg.attach(part)

    try:
        if SMTP_USE_TLS:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(smtp_user, smtp_password)
        server.sendmail(sender, [to], msg.as_string())
        server.quit()
        logger.info("Email sent to %s: %s", to, subject)
        return EmailResult(to=to, success=True)
    except Exception as exc:
        logger.error("Email failed for %s: %s", to, exc)
        return EmailResult(to=to, success=False, error=str(exc))


def send_bulk_email(
    recipients: list[str],
    subject: str,
    body_html: str,
    *,
    smtp_user: str,
    smtp_password: str,
    from_addr: str | None = None,
    body_text: str | None = None,
    attachments: list[str | Path] | None = None,
) -> list[EmailResult]:
    """Send the same email to multiple recipients.

    Returns a list of EmailResult, one per recipient.
    """
    return [
        send_email(
            to=recipient,
            subject=subject,
            body_html=body_html,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            from_addr=from_addr,
            body_text=body_text,
            attachments=attachments,
        )
        for recipient in recipients
    ]
