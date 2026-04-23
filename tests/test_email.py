"""
Tests for integrations.email — SMTP email sending.
"""
from unittest.mock import MagicMock, patch

import pytest

from integrations.email import EmailResult, send_bulk_email, send_email


# ── Validation ───────────────────────────────────────────────────────────


def test_send_email_rejects_empty_recipient():
    result = send_email(
        "", "Subject", "<p>Body</p>",
        smtp_user="u", smtp_password="p",
    )
    assert result.success is False
    assert "required" in result.error


def test_send_email_rejects_empty_subject():
    result = send_email(
        "to@example.com", "", "<p>Body</p>",
        smtp_user="u", smtp_password="p",
    )
    assert result.success is False


# ── Successful send ──────────────────────────────────────────────────────


@patch("integrations.email.smtplib.SMTP")
def test_send_email_success(mock_smtp_cls):
    mock_server = MagicMock()
    mock_smtp_cls.return_value = mock_server

    result = send_email(
        "to@example.com",
        "Test Subject",
        "<h1>Hello</h1>",
        smtp_user="user@gmail.com",
        smtp_password="pass",
    )

    assert result.success is True
    assert result.to == "to@example.com"
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user@gmail.com", "pass")
    mock_server.sendmail.assert_called_once()
    mock_server.quit.assert_called_once()


@patch("integrations.email.smtplib.SMTP")
def test_send_email_with_text_fallback(mock_smtp_cls):
    mock_server = MagicMock()
    mock_smtp_cls.return_value = mock_server

    result = send_email(
        "to@example.com",
        "Subject",
        "<p>HTML</p>",
        smtp_user="u",
        smtp_password="p",
        body_text="Plain text fallback",
    )

    assert result.success is True
    sent_msg = mock_server.sendmail.call_args[0][2]
    assert "Plain text fallback" in sent_msg


@patch("integrations.email.smtplib.SMTP")
def test_send_email_with_custom_from(mock_smtp_cls):
    mock_server = MagicMock()
    mock_smtp_cls.return_value = mock_server

    send_email(
        "to@example.com",
        "Subject",
        "<p>Body</p>",
        smtp_user="u",
        smtp_password="p",
        from_addr="custom@company.com",
    )

    sent_from = mock_server.sendmail.call_args[0][0]
    assert sent_from == "custom@company.com"


@patch("integrations.email.smtplib.SMTP")
def test_send_email_with_attachment(mock_smtp_cls, tmp_path):
    mock_server = MagicMock()
    mock_smtp_cls.return_value = mock_server

    attachment = tmp_path / "report.pdf"
    attachment.write_bytes(b"%PDF-1.4 fake content")

    result = send_email(
        "to@example.com",
        "Report",
        "<p>See attached</p>",
        smtp_user="u",
        smtp_password="p",
        attachments=[str(attachment)],
    )

    assert result.success is True
    sent_msg = mock_server.sendmail.call_args[0][2]
    assert "report.pdf" in sent_msg


@patch("integrations.email.smtplib.SMTP")
def test_send_email_skips_missing_attachment(mock_smtp_cls):
    mock_server = MagicMock()
    mock_smtp_cls.return_value = mock_server

    result = send_email(
        "to@example.com",
        "Subject",
        "<p>Body</p>",
        smtp_user="u",
        smtp_password="p",
        attachments=["/nonexistent/file.pdf"],
    )

    assert result.success is True


# ── Error handling ───────────────────────────────────────────────────────


@patch("integrations.email.smtplib.SMTP")
def test_send_email_smtp_failure(mock_smtp_cls):
    mock_smtp_cls.return_value.starttls.side_effect = ConnectionError("refused")

    result = send_email(
        "to@example.com", "Subject", "<p>Body</p>",
        smtp_user="u", smtp_password="p",
    )

    assert result.success is False
    assert "refused" in result.error


# ── Bulk send ────────────────────────────────────────────────────────────


@patch("integrations.email.smtplib.SMTP")
def test_send_bulk_email(mock_smtp_cls):
    mock_server = MagicMock()
    mock_smtp_cls.return_value = mock_server

    results = send_bulk_email(
        ["a@b.com", "c@d.com"],
        "Subject",
        "<p>Body</p>",
        smtp_user="u",
        smtp_password="p",
    )

    assert len(results) == 2
    assert all(r.success for r in results)


# ── EmailResult immutability ─────────────────────────────────────────────


def test_email_result_is_frozen():
    r = EmailResult(to="a@b.com", success=True)
    with pytest.raises(AttributeError):
        r.success = False
