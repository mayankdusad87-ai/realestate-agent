"""
Tests for integrations.whatsapp — message sending and phone normalisation.
"""
from unittest.mock import MagicMock, patch

from integrations.whatsapp import (
    MessageResult,
    _normalize_phone,
    send_bulk,
    send_template,
    send_text,
)


# ── Phone normalisation ─────────────────────────────────────────────────


def test_normalize_strips_formatting():
    assert _normalize_phone("+91 98765-43210") == "919876543210"


def test_normalize_adds_india_code_for_10_digits():
    assert _normalize_phone("9876543210") == "919876543210"


def test_normalize_preserves_full_international():
    assert _normalize_phone("447911123456") == "447911123456"


def test_normalize_strips_parentheses():
    assert _normalize_phone("(91) 98765 43210") == "919876543210"


# ── Validation ───────────────────────────────────────────────────────────


def test_send_text_rejects_empty_phone():
    result = send_text("", "hello", access_token="t", phone_number_id="p")
    assert result.success is False
    assert "required" in result.error


def test_send_text_rejects_empty_message():
    result = send_text("9876543210", "", access_token="t", phone_number_id="p")
    assert result.success is False


def test_send_template_rejects_empty_template():
    result = send_template("9876543210", "", access_token="t", phone_number_id="p")
    assert result.success is False


# ── Successful send ──────────────────────────────────────────────────────


@patch("integrations.whatsapp.requests.post")
def test_send_text_success(mock_post):
    mock_post.return_value = MagicMock(
        ok=True,
        json=MagicMock(return_value={
            "messages": [{"id": "wamid.123"}],
        }),
    )

    result = send_text(
        "9876543210", "Hello!",
        access_token="token", phone_number_id="12345",
    )

    assert result.success is True
    assert result.message_id == "wamid.123"
    assert result.phone == "9876543210"


@patch("integrations.whatsapp.requests.post")
def test_send_text_api_error(mock_post):
    mock_post.return_value = MagicMock(
        ok=False,
        text="Bad Request",
        json=MagicMock(return_value={
            "error": {"message": "Invalid token"},
        }),
    )

    result = send_text(
        "9876543210", "Hello!",
        access_token="bad", phone_number_id="12345",
    )

    assert result.success is False
    assert "Invalid token" in result.error


@patch("integrations.whatsapp.requests.post")
def test_send_text_network_exception(mock_post):
    mock_post.side_effect = ConnectionError("timeout")

    result = send_text(
        "9876543210", "Hello!",
        access_token="token", phone_number_id="12345",
    )

    assert result.success is False
    assert "timeout" in result.error


# ── Template send ────────────────────────────────────────────────────────


@patch("integrations.whatsapp.requests.post")
def test_send_template_with_parameters(mock_post):
    mock_post.return_value = MagicMock(
        ok=True,
        json=MagicMock(return_value={
            "messages": [{"id": "wamid.456"}],
        }),
    )

    result = send_template(
        "9876543210", "payment_reminder",
        access_token="token", phone_number_id="12345",
        parameters=["Mr. Sharma", "5,00,000"],
    )

    assert result.success is True
    call_payload = mock_post.call_args[1]["json"]
    assert call_payload["template"]["components"][0]["parameters"][0]["text"] == "Mr. Sharma"


# ── Bulk send ────────────────────────────────────────────────────────────


@patch("integrations.whatsapp.requests.post")
def test_send_bulk(mock_post):
    mock_post.return_value = MagicMock(
        ok=True,
        json=MagicMock(return_value={"messages": [{"id": "wamid.x"}]}),
    )

    recipients = [
        {"phone": "9876543210", "name": "Alice"},
        {"phone": "9123456789", "name": "Bob"},
    ]

    results = send_bulk(
        recipients,
        message_builder=lambda r: f"Hi {r['name']}!",
        access_token="token",
        phone_number_id="12345",
    )

    assert len(results) == 2
    assert all(r.success for r in results)
