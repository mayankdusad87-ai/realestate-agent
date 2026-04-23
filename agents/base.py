"""
Base agent class — LLM call with retry, output formatting, and report generation.

All agents inherit from BaseAgent and implement build_prompt() and parse_response().
The base class handles Groq API calls, retry logic, and common formatting utilities.
"""
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field

from groq import Groq

from config import (
    GROQ_MAX_RETRIES,
    GROQ_MAX_TOKENS,
    GROQ_MODEL,
    GROQ_RETRY_DELAY_SECONDS,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentResult:
    """Immutable result from an agent run."""

    sections: dict[str, str] = field(default_factory=dict)
    raw_response: str = ""
    agent_name: str = ""
    success: bool = False
    error: str | None = None


class BaseAgent(ABC):
    """Abstract base class for all real estate AI agents.

    Subclasses must implement:
        name       — human-readable agent name (property)
        build_prompt — construct an LLM prompt from input data
        parse_response — parse LLM text into structured sections
    """

    def __init__(
        self,
        groq_key: str,
        *,
        model: str = GROQ_MODEL,
        max_tokens: int = GROQ_MAX_TOKENS,
        max_retries: int = GROQ_MAX_RETRIES,
        retry_delay: float = GROQ_RETRY_DELAY_SECONDS,
    ):
        self._client = Groq(api_key=groq_key)
        self._model = model
        self._max_tokens = max_tokens
        self._max_retries = max_retries
        self._retry_delay = retry_delay

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name."""

    @abstractmethod
    def build_prompt(self, data: dict) -> str:
        """Build the LLM prompt from input data."""

    @abstractmethod
    def parse_response(self, raw: str) -> dict[str, str]:
        """Parse raw LLM response into a dict of named sections."""

    # ── LLM call with retry ──────────────────────────────────────────────

    def call_llm(
        self,
        prompt: str,
        *,
        on_retry: Callable[[int, int, Exception], None] | None = None,
    ) -> str:
        """Call Groq LLM with retry logic. Returns raw response text.

        Args:
            prompt: The user prompt to send.
            on_retry: Optional callback(attempt, max_retries, exception)
                      invoked before each retry sleep.

        Raises:
            Exception: Re-raises the last exception after all retries fail.
        """
        for attempt in range(1, self._max_retries + 1):
            try:
                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self._max_tokens,
                )
                return response.choices[0].message.content
            except Exception as exc:
                logger.warning(
                    "%s: LLM attempt %d/%d failed: %s",
                    self.name,
                    attempt,
                    self._max_retries,
                    exc,
                )
                if attempt < self._max_retries:
                    if on_retry:
                        on_retry(attempt, self._max_retries, exc)
                    time.sleep(self._retry_delay)
                else:
                    raise

    # ── Full pipeline ────────────────────────────────────────────────────

    def run(
        self,
        data: dict,
        *,
        on_retry: Callable[[int, int, Exception], None] | None = None,
    ) -> AgentResult:
        """Full pipeline: build prompt → call LLM → parse response.

        Returns an AgentResult; never raises.
        """
        try:
            prompt = self.build_prompt(data)
            raw = self.call_llm(prompt, on_retry=on_retry)
            sections = self.parse_response(raw)
            return AgentResult(
                sections=sections,
                raw_response=raw,
                agent_name=self.name,
                success=bool(sections),
            )
        except Exception as exc:
            logger.error("%s: run failed: %s", self.name, exc)
            return AgentResult(
                agent_name=self.name,
                error=str(exc),
            )

    # ── Formatting utilities ─────────────────────────────────────────────

    @staticmethod
    def format_traffic_light(status: str) -> str:
        """Map a status string to a traffic-light emoji."""
        mapping = {"green": "\U0001f7e2", "amber": "\U0001f7e1", "red": "\U0001f534"}
        return mapping.get(status.lower(), "\u26aa")

    @staticmethod
    def format_inr(amount_lakhs: float) -> str:
        """Format an amount (in lakhs) as a human-readable INR string."""
        if amount_lakhs >= 100:
            return f"\u20b9{amount_lakhs / 100:.2f} Cr"
        return f"\u20b9{amount_lakhs:.1f} L"
