"""
WhatsApp Business API client (Meta Cloud API).

Supports plain-text messages, template messages, and bulk sends.
Phone numbers are auto-normalized to the E.164 format expected by Meta.
"""
import logging
from collections.abc import Callable
from dataclasses import dataclass

import requests

from config import WHATSAPP_API_TIMEOUT, WHATSAPP_API_URL

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MessageResult:
    """Immutable result of a single WhatsApp send attempt."""

    phone: str
    success: bool
    message_id: str | None = None
    error: str | None = None


# ── Public API ───────────────────────────────────────────────────────────


def send_text(
    phone: str,
    message: str,
    *,
    access_token: str,
    phone_number_id: str,
) -> MessageResult:
    """Send a plain-text WhatsApp message."""
    if not phone or not message:
        return MessageResult(
            phone=phone, success=False, error="Phone and message are required"
        )

    payload = {
        "messaging_product": "whatsapp",
        "to": _normalize_phone(phone),
        "type": "text",
        "text": {"body": message},
    }
    return _send(phone, payload, access_token=access_token, phone_number_id=phone_number_id)


def send_template(
    phone: str,
    template_name: str,
    *,
    access_token: str,
    phone_number_id: str,
    language_code: str = "en",
    parameters: list[str] | None = None,
) -> MessageResult:
    """Send a pre-approved template message."""
    if not phone or not template_name:
        return MessageResult(
            phone=phone, success=False, error="Phone and template_name are required"
        )

    template: dict = {
        "name": template_name,
        "language": {"code": language_code},
    }
    if parameters:
        template["components"] = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": p} for p in parameters],
            }
        ]

    payload = {
        "messaging_product": "whatsapp",
        "to": _normalize_phone(phone),
        "type": "template",
        "template": template,
    }
    return _send(phone, payload, access_token=access_token, phone_number_id=phone_number_id)


def send_bulk(
    recipients: list[dict],
    message_builder: Callable[[dict], str],
    *,
    access_token: str,
    phone_number_id: str,
) -> list[MessageResult]:
    """Send personalised messages to multiple recipients.

    Args:
        recipients: List of dicts, each containing at least a ``phone`` key.
        message_builder: Takes a recipient dict, returns the message body.
        access_token: WhatsApp Business API access token.
        phone_number_id: WhatsApp Business phone-number ID.
    """
    return [
        send_text(
            r.get("phone", ""),
            message_builder(r),
            access_token=access_token,
            phone_number_id=phone_number_id,
        )
        for r in recipients
    ]


# ── Internals ────────────────────────────────────────────────────────────


def _send(
    phone: str,
    payload: dict,
    *,
    access_token: str,
    phone_number_id: str,
) -> MessageResult:
    """Low-level POST to the Meta messages endpoint."""
    url = f"{WHATSAPP_API_URL}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=WHATSAPP_API_TIMEOUT)
        data = res.json()

        if res.ok and "messages" in data:
            msg_id = data["messages"][0].get("id", "")
            logger.info("WhatsApp sent to %s: %s", phone, msg_id)
            return MessageResult(phone=phone, success=True, message_id=msg_id)

        error = data.get("error", {}).get("message", res.text)
        logger.warning("WhatsApp failed for %s: %s", phone, error)
        return MessageResult(phone=phone, success=False, error=error)
    except Exception as exc:
        logger.error("WhatsApp send error for %s: %s", phone, exc)
        return MessageResult(phone=phone, success=False, error=str(exc))


def _normalize_phone(phone: str) -> str:
    """Strip formatting and ensure an Indian country-code prefix."""
    cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]
    # Bare 10-digit Indian mobile number → prefix with 91
    if len(cleaned) == 10 and cleaned.isdigit():
        cleaned = "91" + cleaned
    return cleaned
