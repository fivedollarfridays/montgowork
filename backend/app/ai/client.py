"""Multi-provider LLM client for generating plan narratives.

Supports: anthropic (default) | openai | gemini | mock
Controlled via LLM_PROVIDER env var.
"""

import json
import logging

from app.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from app.ai.types import PlanNarrative
from app.barrier_intel.llm_client import _PROVIDERS, _resolve_provider
from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def generate_narrative(
    barriers: list[str],
    qualifications: str,
    plan_data: dict,
) -> PlanNarrative:
    """Call configured LLM API to generate a personalized plan narrative.

    Raises provider errors to the caller.
    """
    from app.barrier_intel.llm_client import _PROVIDERS, _resolve_provider
    from app.core.config import get_settings
    
    settings = get_settings()
    configured = settings.llm_provider
    resolved = _resolve_provider(settings, configured)
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        barriers=", ".join(barriers),
        qualifications=qualifications,
        plan_data=json.dumps(plan_data, default=str),
    )

    # Use non-streaming approach for JSON reliability
    if resolved == "anthropic":
        return await _generate_anthropic_narrative(user_prompt)
    elif resolved == "openai":
        return await _generate_openai_narrative(user_prompt)
    elif resolved == "gemini":
        return await _generate_gemini_narrative(user_prompt)
    else:  # mock
        return build_fallback_narrative(barriers, qualifications, plan_data)


async def _generate_anthropic_narrative(user_prompt: str) -> PlanNarrative:
    """Generate narrative using Anthropic (non-streaming)."""
    from anthropic import AsyncAnthropic
    from app.core.config import get_settings
    
    settings = get_settings()
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    
    message = await client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    
    if not message.content:
        raise ValueError("Anthropic returned empty response")
    
    raw_response = message.content[0].text
    return _parse_narrative_response(raw_response)


async def _generate_openai_narrative(user_prompt: str) -> PlanNarrative:
    """Generate narrative using OpenAI (non-streaming)."""
    from openai import AsyncOpenAI
    from app.core.config import get_settings
    
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    response = await client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    if not response.choices or not response.choices[0].message.content:
        raise ValueError("OpenAI returned empty response")
    
    raw_response = response.choices[0].message.content
    return _parse_narrative_response(raw_response)


async def _generate_gemini_narrative(user_prompt: str) -> PlanNarrative:
    """Generate narrative using Gemini (non-streaming)."""
    from google import genai
    from google.genai import types
    from app.core.config import get_settings
    
    settings = get_settings()
    client = genai.Client(api_key=settings.gemini_api_key)
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        max_output_tokens=1024,
    )
    
    response = await client.aio.models.generate_content(
        model=settings.gemini_model,
        contents=user_prompt,
        config=config,
    )
    
    if not response.text:
        raise ValueError("Gemini returned empty response")
    
    raw_response = response.text
    return _parse_narrative_response(raw_response)


def _parse_narrative_response(raw_response: str) -> PlanNarrative:
    """Parse and clean LLM response into PlanNarrative."""
    if not raw_response:
        raise ValueError("LLM returned empty response")
    
    # Handle JSON wrapped in markdown code blocks (common with Gemini)
    cleaned = raw_response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]  # Remove ```json
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]   # Remove ```
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]  # Remove trailing ```
    cleaned = cleaned.strip()
    
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.warning("LLM returned invalid JSON (length=%d): %s", len(cleaned), cleaned[:200])
        
        # Try to fix common JSON issues
        try:
            # Attempt to fix truncated JSON by finding the last complete object
            if cleaned.count('{') > cleaned.count('}'):
                # Find the position of the last complete JSON object
                last_complete = cleaned.rfind('}')
                if last_complete > 0:
                    fixed = cleaned[:last_complete + 1]
                    parsed = json.loads(fixed)
                    logger.info("Fixed truncated JSON response")
                    return PlanNarrative(**parsed)
        except:
            pass
            
        raise ValueError("LLM returned invalid JSON") from exc
    return PlanNarrative(**parsed)


def _extract_actions_and_contacts(plan_data: dict) -> tuple[list[str], list[str], list[str]]:
    """Extract actions, contacts, and job titles from plan data."""
    actions = []
    contacts = []
    for barrier_card in plan_data.get("barriers", []):
        actions.extend(barrier_card.get("actions", []))
        for resource in barrier_card.get("resources", []):
            name = resource.get("name", "")
            phone = resource.get("phone", "")
            if name:
                contacts.append(f"{name} ({phone})" if phone else name)
    for step in plan_data.get("immediate_next_steps", []):
        if step not in actions:
            actions.append(step)
    job_titles = [m["title"] for m in plan_data.get("job_matches", []) if m.get("title")]
    return actions, contacts, job_titles


def build_fallback_narrative(
    barriers: list[str],
    qualifications: str,
    plan_data: dict,
) -> PlanNarrative:
    """Build a warm, Montgomery-specific narrative when the AI API is unavailable."""
    actions, contacts, job_titles = _extract_actions_and_contacts(plan_data)
    summary = _build_fallback_summary(barriers, contacts, job_titles)
    key_actions = _build_fallback_actions(actions)
    return PlanNarrative(summary=summary, key_actions=key_actions)


def _fallback_opening(barriers: list[str]) -> str:
    """Return an empathetic opening sentence based on whether barriers exist."""
    if barriers:
        return (
            "You have already taken a big step by identifying what is standing "
            "in your way. That takes real courage."
        )
    return (
        "You are taking an important first step, and there are people in "
        "Montgomery ready to help you move forward."
    )


def _fallback_next_step(contacts: list[str]) -> str:
    """Return a Monday-morning contact step for the fallback narrative."""
    if contacts:
        return (
            f"Your first step Monday morning is to reach out to {contacts[0]} "
            "-- they work with Montgomery residents every day and know exactly "
            "how to help."
        )
    return (
        "Monday morning, head to the Alabama Career Center on Carter Hill Road. "
        "The staff there help Montgomery residents just like you every single day."
    )


def _fallback_jobs_sentence(job_titles: list[str]) -> str:
    """Return a natural sentence about matched jobs, or empty string."""
    if not job_titles:
        return ""
    if len(job_titles) == 1:
        return f"We also found a {job_titles[0]} position that could be a great fit for you."
    if len(job_titles) > 2:
        joined = ", ".join(job_titles[:2]) + " and " + job_titles[2]
    else:
        joined = " and ".join(job_titles[:2])
    return f"We also found openings for {joined} that could be a great fit."


def _build_fallback_summary(
    barriers: list[str],
    contacts: list[str],
    job_titles: list[str],
) -> str:
    """Compose a warm, Montgomery-specific fallback summary."""
    parts = [
        _fallback_opening(barriers),
        _fallback_next_step(contacts),
    ]
    jobs_sentence = _fallback_jobs_sentence(job_titles)
    if jobs_sentence:
        parts.append(jobs_sentence)
    return " ".join(parts)


def _build_fallback_actions(actions: list[str]) -> list[str]:
    """Return up to 5 key actions, with a Montgomery-specific default."""
    if actions:
        return actions[:5]
    return [
        "Visit the Alabama Career Center on Carter Hill Road in Montgomery "
        "for personalized guidance"
    ]
