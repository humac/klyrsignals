"""LLM Connector: multi-provider AI integration (OpenAI, Anthropic, Ollama).

Routes analysis prompts to the configured AI provider and parses responses.
"""

import json

import httpx
import structlog

from app.config import settings
from app.exceptions import AIProviderError
from app.schemas.analysis import KlyrSignal

logger = structlog.get_logger()


async def generate_signals(
    system_prompt: str,
    user_prompt: str,
) -> tuple[list[KlyrSignal], str]:
    """Send analysis context to the configured AI provider and parse signals.

    Returns (signals_list, raw_summary_text).
    """
    provider = settings.ai_provider.lower()

    try:
        if provider == "openai":
            raw = await _call_openai(system_prompt, user_prompt)
        elif provider == "anthropic":
            raw = await _call_anthropic(system_prompt, user_prompt)
        elif provider == "ollama":
            raw = await _call_ollama(system_prompt, user_prompt)
        else:
            raise AIProviderError(provider, f"Unknown AI provider: {provider}")

        signals = _parse_signals(raw)
        return signals, raw

    except AIProviderError:
        raise
    except Exception as e:
        logger.error("ai_generation_failed", provider=provider, error=str(e))
        # Return fallback signals based on rules only
        return [], f"AI analysis unavailable ({provider}): {str(e)}"


async def _call_openai(system_prompt: str, user_prompt: str) -> str:
    """Call OpenAI GPT-4o API."""
    import openai

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=4000,
    )

    return response.choices[0].message.content or ""


async def _call_anthropic(system_prompt: str, user_prompt: str) -> str:
    """Call Anthropic Claude 3.5 API."""
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.content[0].text


async def _call_ollama(system_prompt: str, user_prompt: str) -> str:
    """Call local Ollama instance."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/chat",
            json={
                "model": "llama3.1:8b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 4000,
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")


def _parse_signals(raw_response: str) -> list[KlyrSignal]:
    """Parse AI response into structured KlyrSignal objects.

    Handles various response formats (pure JSON, markdown-wrapped, etc.)
    """
    if not raw_response:
        return []

    # Strip markdown code fences if present
    text = raw_response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (code fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)

    # Try to find JSON array in the response
    try:
        # Direct parse
        data = json.loads(text)
        if isinstance(data, list):
            return [KlyrSignal(**item) for item in data]
        if isinstance(data, dict) and "signals" in data:
            return [KlyrSignal(**item) for item in data["signals"]]
    except (json.JSONDecodeError, ValueError):
        pass

    # Try to extract JSON array from text
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads(text[start:end + 1])
            return [KlyrSignal(**item) for item in data]
        except (json.JSONDecodeError, ValueError):
            pass

    logger.warning("ai_response_parse_failed", response_length=len(raw_response))
    return []
