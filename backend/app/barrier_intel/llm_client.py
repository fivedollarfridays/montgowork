"""Provider-agnostic LLM streaming client factory.

Supports: anthropic (default) | openai | gemini | mock
Controlled via LLM_PROVIDER env var.

If the configured provider's API key is missing, automatically falls back to
the mock provider and logs a WARNING — no crash, zero-config local dev works.
"""

import asyncio
import logging

from anthropic import AsyncAnthropic

from app.barrier_intel.prompts import SYSTEM_PROMPT
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Maps provider name → (key getter, env var name)
_KEY_MAP: dict[str, tuple] = {
    "anthropic": (lambda s: s.anthropic_api_key, "ANTHROPIC_API_KEY"),
    "openai":    (lambda s: s.openai_api_key,    "OPENAI_API_KEY"),
    "gemini":    (lambda s: s.gemini_api_key,    "GEMINI_API_KEY"),
}


async def _anthropic_stream(prompt: str):
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    async with client.messages.stream(
        model=settings.claude_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            yield text, 0, 0
        final = await stream.get_final_message()
        yield "", final.usage.input_tokens, final.usage.output_tokens


async def _openai_stream(prompt: str):
    from openai import AsyncOpenAI
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    stream = await client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        stream=True,
        stream_options={"include_usage": True},
    )
    input_tokens = output_tokens = 0
    async for chunk in stream:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            yield delta, 0, 0
        if chunk.usage:
            input_tokens = chunk.usage.prompt_tokens
            output_tokens = chunk.usage.completion_tokens
    yield "", input_tokens, output_tokens


async def _gemini_stream(prompt: str):
    from google import genai
    from google.genai import types
    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        max_output_tokens=1024,
    )
    async for chunk in await client.aio.models.generate_content_stream(
        model=settings.gemini_model,
        contents=prompt,
        config=config,
    ):
        text = chunk.text if chunk.text else ""
        if text:
            yield text, 0, 0
    yield "", 0, 0


async def _mock_stream(prompt: str):
    """Mock LLM provider — works without any API key (local dev / CI)."""
    mock_response = (
        "I'm a mock LLM response. The system is working correctly, but I don't have access to "
        "real AI capabilities without an API key. The barrier intelligence system architecture "
        "is functioning properly - you can see this message because the streaming mechanism "
        "is working. To get actual AI responses, please configure a valid API key for one of "
        "the supported providers (anthropic, openai, or gemini)."
    )
    for word in mock_response.split():
        yield word + " ", 0, 0
        await asyncio.sleep(0.05)
    yield "", 50, 100


_PROVIDERS = {
    "anthropic": _anthropic_stream,
    "openai":    _openai_stream,
    "gemini":    _gemini_stream,
    "mock":      _mock_stream,
}


def _resolve_provider(settings, provider: str) -> str:
    """Return the provider to use, falling back to mock if key is missing."""
    if provider == "mock":
        return "mock"
    if provider not in _KEY_MAP:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Choose: {', '.join(_PROVIDERS)}"
        )
    key_getter, env_var = _KEY_MAP[provider]
    if not key_getter(settings):
        logger.warning(
            "%s is not set — LLM_PROVIDER='%s' will fall back to mock responses. "
            "Set %s in your .env to use the real provider.",
            env_var, provider, env_var,
        )
        return "mock"
    return provider


def get_llm_stream(prompt: str):
    """Return the async generator for the configured (or resolved) LLM provider."""
    settings = get_settings()
    configured = settings.llm_provider
    if configured not in _PROVIDERS:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{configured}'. Choose: {', '.join(_PROVIDERS)}"
        )
    resolved = _resolve_provider(settings, configured)
    return _PROVIDERS[resolved](prompt)
