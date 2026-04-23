"""
Tests for agents.base — BaseAgent, AgentResult, and formatting utilities.
"""
from unittest.mock import MagicMock, patch

import pytest

from agents.base import AgentResult, BaseAgent


# ── Concrete stub for testing the abstract class ─────────────────────────


class _StubAgent(BaseAgent):
    """Minimal concrete agent for testing base-class behaviour."""

    @property
    def name(self) -> str:
        return "Stub Agent"

    def build_prompt(self, data: dict) -> str:
        return f"Analyse: {data.get('topic', 'unknown')}"

    def parse_response(self, raw: str) -> dict[str, str]:
        if "SECTION_" not in raw:
            return {}
        sections = {}
        for sec in raw.split("SECTION_")[1:]:
            if ":" in sec:
                num = sec.split(":")[0].strip()
                sections[num] = ":".join(sec.split(":")[1:]).strip()
        return sections


# ── AgentResult immutability ─────────────────────────────────────────────


def test_agent_result_defaults():
    r = AgentResult()
    assert r.sections == {}
    assert r.raw_response == ""
    assert r.success is False
    assert r.error is None


def test_agent_result_is_frozen():
    r = AgentResult(success=True)
    with pytest.raises(AttributeError):
        r.success = False


# ── BaseAgent instantiation ──────────────────────────────────────────────


def test_stub_agent_name():
    agent = _StubAgent("fake-key")
    assert agent.name == "Stub Agent"


def test_build_prompt_uses_data():
    agent = _StubAgent("fake-key")
    prompt = agent.build_prompt({"topic": "Mumbai market"})
    assert "Mumbai market" in prompt


# ── call_llm retry logic ─────────────────────────────────────────────────


@patch("agents.base.time.sleep", return_value=None)
def test_call_llm_retries_on_failure(mock_sleep):
    agent = _StubAgent("fake-key", max_retries=3, retry_delay=0)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="SECTION_1: Data"))]

    agent._client = MagicMock()
    agent._client.chat.completions.create.side_effect = [
        RuntimeError("timeout"),
        mock_response,
    ]

    result = agent.call_llm("test prompt")
    assert result == "SECTION_1: Data"
    assert agent._client.chat.completions.create.call_count == 2
    assert mock_sleep.call_count == 1


@patch("agents.base.time.sleep", return_value=None)
def test_call_llm_raises_after_exhausting_retries(mock_sleep):
    agent = _StubAgent("fake-key", max_retries=2, retry_delay=0)
    agent._client = MagicMock()
    agent._client.chat.completions.create.side_effect = RuntimeError("down")

    with pytest.raises(RuntimeError, match="down"):
        agent.call_llm("test prompt")

    assert agent._client.chat.completions.create.call_count == 2


@patch("agents.base.time.sleep", return_value=None)
def test_call_llm_invokes_on_retry_callback(mock_sleep):
    agent = _StubAgent("fake-key", max_retries=3, retry_delay=0)

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="ok"))]

    agent._client = MagicMock()
    agent._client.chat.completions.create.side_effect = [
        RuntimeError("err"),
        mock_response,
    ]

    callback_calls = []
    agent.call_llm("p", on_retry=lambda a, m, e: callback_calls.append((a, m)))

    assert len(callback_calls) == 1
    assert callback_calls[0] == (1, 3)


# ── run() pipeline ───────────────────────────────────────────────────────


@patch("agents.base.time.sleep", return_value=None)
def test_run_success(mock_sleep):
    agent = _StubAgent("fake-key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="SECTION_1: Market data here"))
    ]
    agent._client = MagicMock()
    agent._client.chat.completions.create.return_value = mock_response

    result = agent.run({"topic": "test"})
    assert result.success is True
    assert result.agent_name == "Stub Agent"
    assert "1" in result.sections
    assert "Market data here" in result.sections["1"]


@patch("agents.base.time.sleep", return_value=None)
def test_run_returns_failure_on_error(mock_sleep):
    agent = _StubAgent("fake-key", max_retries=1, retry_delay=0)
    agent._client = MagicMock()
    agent._client.chat.completions.create.side_effect = RuntimeError("boom")

    result = agent.run({"topic": "test"})
    assert result.success is False
    assert result.error == "boom"
    assert result.agent_name == "Stub Agent"


@patch("agents.base.time.sleep", return_value=None)
def test_run_returns_failure_when_parse_returns_empty(mock_sleep):
    agent = _StubAgent("fake-key")

    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="No sections here"))
    ]
    agent._client = MagicMock()
    agent._client.chat.completions.create.return_value = mock_response

    result = agent.run({"topic": "test"})
    assert result.success is False
    assert result.sections == {}
    assert result.raw_response == "No sections here"


# ── Formatting helpers ───────────────────────────────────────────────────


def test_format_traffic_light():
    assert BaseAgent.format_traffic_light("green") == "\U0001f7e2"
    assert BaseAgent.format_traffic_light("amber") == "\U0001f7e1"
    assert BaseAgent.format_traffic_light("red") == "\U0001f534"
    assert BaseAgent.format_traffic_light("unknown") == "\u26aa"


def test_format_inr_crores():
    assert BaseAgent.format_inr(150) == "\u20b91.50 Cr"
    assert BaseAgent.format_inr(100) == "\u20b91.00 Cr"


def test_format_inr_lakhs():
    assert BaseAgent.format_inr(50) == "\u20b950.0 L"
    assert BaseAgent.format_inr(99.5) == "\u20b999.5 L"
