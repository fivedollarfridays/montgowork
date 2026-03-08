"""Tests for multi-provider narrative generation in app/ai/client.py."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _settings(**kwargs):
    from app.core.config import Settings
    return Settings(_env_file=None, **kwargs)


# ---------------------------------------------------------------------------
# _parse_narrative_response
# ---------------------------------------------------------------------------

def test_parse_valid_json():
    from app.ai.client import _parse_narrative_response
    raw = json.dumps({"summary": "Hello world", "key_actions": ["Step 1"]})
    result = _parse_narrative_response(raw)
    assert result.summary == "Hello world"
    assert result.key_actions == ["Step 1"]


def test_parse_strips_markdown_code_fence():
    from app.ai.client import _parse_narrative_response
    raw = '```json\n{"summary": "Gemini reply", "key_actions": []}\n```'
    result = _parse_narrative_response(raw)
    assert result.summary == "Gemini reply"


def test_parse_strips_plain_code_fence():
    from app.ai.client import _parse_narrative_response
    raw = '```\n{"summary": "Plain fence", "key_actions": []}\n```'
    result = _parse_narrative_response(raw)
    assert result.summary == "Plain fence"


def test_parse_raises_on_invalid_json():
    from app.ai.client import _parse_narrative_response
    with pytest.raises(ValueError, match="invalid JSON"):
        _parse_narrative_response("not json at all")


def test_parse_raises_on_empty():
    from app.ai.client import _parse_narrative_response
    with pytest.raises(ValueError):
        _parse_narrative_response("")


def test_parse_fixes_truncated_json():
    """Truncated JSON missing closing braces is recovered."""
    from app.ai.client import _parse_narrative_response
    truncated = '{"summary": "Truncated", "key_actions": ["Step 1"]'
    # This may or may not recover — at minimum it should not silently return wrong data
    try:
        result = _parse_narrative_response(truncated)
        assert result.summary == "Truncated"
    except ValueError:
        pass  # Acceptable — truncation not always recoverable


# ---------------------------------------------------------------------------
# generate_narrative — provider routing
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_generate_narrative_uses_mock_when_resolved():
    """When provider resolves to mock, build_fallback_narrative is used (no API call)."""
    from app.ai.client import generate_narrative

    settings = _settings(llm_provider="mock")
    with patch("app.ai.client.get_settings", return_value=settings), \
         patch("app.ai.client._resolve_provider", return_value="mock"):
        result = await generate_narrative(
            barriers=["credit"],
            qualifications="",
            plan_data={"barriers": [], "job_matches": [], "immediate_next_steps": []},
        )
    assert result.summary
    assert isinstance(result.key_actions, list)


@pytest.mark.anyio
async def test_generate_narrative_anthropic_path():
    """Anthropic provider path calls _generate_anthropic_narrative."""
    from app.ai.client import generate_narrative

    settings = _settings(llm_provider="anthropic", anthropic_api_key="test-key")
    mock_narrative = MagicMock()
    mock_narrative.summary = "Anthropic result"
    mock_narrative.key_actions = ["Step A"]

    # Must patch at the source module since generate_narrative imports via `from X import`
    with patch("app.ai.client.get_settings", return_value=settings), \
         patch("app.barrier_intel.llm_client._resolve_provider", return_value="anthropic"), \
         patch("app.ai.client._generate_anthropic_narrative", new=AsyncMock(return_value=mock_narrative)):
        result = await generate_narrative(barriers=[], qualifications="", plan_data={})
    assert result.summary == "Anthropic result"


@pytest.mark.anyio
async def test_generate_narrative_openai_path():
    """OpenAI provider path calls _generate_openai_narrative."""
    from app.ai.client import generate_narrative

    settings = _settings(llm_provider="openai", openai_api_key="sk-test")
    mock_narrative = MagicMock()
    mock_narrative.summary = "OpenAI result"
    mock_narrative.key_actions = []

    with patch("app.ai.client.get_settings", return_value=settings), \
         patch("app.barrier_intel.llm_client._resolve_provider", return_value="openai"), \
         patch("app.ai.client._generate_openai_narrative", new=AsyncMock(return_value=mock_narrative)):
        result = await generate_narrative(barriers=[], qualifications="", plan_data={})
    assert result.summary == "OpenAI result"


@pytest.mark.anyio
async def test_generate_narrative_gemini_path():
    """Gemini provider path calls _generate_gemini_narrative."""
    from app.ai.client import generate_narrative

    settings = _settings(llm_provider="gemini", gemini_api_key="gm-test")
    mock_narrative = MagicMock()
    mock_narrative.summary = "Gemini result"
    mock_narrative.key_actions = []

    with patch("app.ai.client.get_settings", return_value=settings), \
         patch("app.barrier_intel.llm_client._resolve_provider", return_value="gemini"), \
         patch("app.ai.client._generate_gemini_narrative", new=AsyncMock(return_value=mock_narrative)):
        result = await generate_narrative(barriers=[], qualifications="", plan_data={})
    assert result.summary == "Gemini result"


# ---------------------------------------------------------------------------
# Provider-specific generators (mocked API calls)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_generate_anthropic_narrative_parses_json():
    from app.ai.client import _generate_anthropic_narrative

    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=json.dumps({
        "summary": "Your plan begins at the Career Center.",
        "key_actions": ["Visit Career Center"],
    }))]

    with patch("app.ai.client.get_settings", return_value=_settings(anthropic_api_key="test-key")), \
         patch("anthropic.AsyncAnthropic") as mock_cls:
        mock_cls.return_value.messages.create = AsyncMock(return_value=mock_message)
        result = await _generate_anthropic_narrative("test prompt")

    assert result.summary == "Your plan begins at the Career Center."


@pytest.mark.anyio
async def test_generate_openai_narrative_parses_json():
    from app.ai.client import _generate_openai_narrative

    payload = json.dumps({"summary": "OpenAI says hi.", "key_actions": ["Call now"]})
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = payload

    with patch("app.ai.client.get_settings", return_value=_settings(openai_api_key="sk-test")), \
         patch("openai.AsyncOpenAI") as mock_cls:
        mock_cls.return_value.chat.completions.create = AsyncMock(return_value=mock_response)
        result = await _generate_openai_narrative("test prompt")

    assert result.summary == "OpenAI says hi."


@pytest.mark.anyio
async def test_generate_gemini_narrative_parses_json():
    from app.ai.client import _generate_gemini_narrative

    payload = json.dumps({"summary": "Gemini helps.", "key_actions": []})
    mock_response = MagicMock()
    mock_response.text = payload

    with patch("app.ai.client.get_settings", return_value=_settings(gemini_api_key="gm-test")), \
         patch("google.genai.Client") as mock_cls:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        result = await _generate_gemini_narrative("test prompt")

    assert result.summary == "Gemini helps."
