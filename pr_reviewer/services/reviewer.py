"""AI code review service supporting multiple providers."""

import os
from collections.abc import AsyncGenerator

import anthropic
import openai

from pr_reviewer.constants import DEFAULT_MODEL, DEFAULT_PROVIDER, Provider

SYSTEM_PROMPT = """You are an expert code reviewer. Analyze the provided diff and give a concise, actionable review.

Focus on:
- Bugs or logic errors
- Security vulnerabilities
- Performance issues
- Code clarity and maintainability
- Missing error handling

Format your response as markdown with sections:
## Summary
Brief 1-2 sentence summary of the changes.

## Issues
List any problems found (or "None found" if clean).

## Suggestions
Optional improvements (keep brief).

Be direct and specific. Reference line numbers from the diff when relevant."""


def _build_user_message(filename: str, diff: str) -> str:
    """Build the user message for the review request."""
    return f"""Review this diff for `{filename}`:

```diff
{diff}
```"""


async def _review_with_anthropic(
    user_message: str,
    model: str,
    api_key: str,
) -> AsyncGenerator[str, None]:
    """Stream a review using Anthropic's API."""
    client = anthropic.AsyncAnthropic(api_key=api_key)

    async with client.messages.stream(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text


async def _review_with_openai(
    user_message: str,
    model: str,
    api_key: str,
) -> AsyncGenerator[str, None]:
    """Stream a review using OpenAI's Responses API."""
    client = openai.AsyncOpenAI(api_key=api_key)

    stream = await client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=user_message,
        stream=True,
    )

    async for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta


async def review_diff(
    filename: str,
    diff: str,
    model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
    api_key: str | None = None,
) -> AsyncGenerator[str, None]:
    """Stream an AI code review for a diff.

    Args:
        filename: Name of the file being reviewed.
        diff: The diff patch content.
        model: Model ID to use.
        provider: AI provider ('anthropic' or 'openai').
        api_key: Optional API key (defaults to env var for provider).

    Yields:
        Text chunks as they stream from the API.

    Raises:
        Exception: On API errors or missing configuration.
    """
    user_message = _build_user_message(filename, diff)

    if provider == Provider.ANTHROPIC:
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise Exception(
                "ANTHROPIC_API_KEY not set. Add it to .env or provide in settings."
            )
        try:
            async for text in _review_with_anthropic(user_message, model, key):
                yield text
        except anthropic.APIError as e:
            raise Exception(f"Review failed for {filename}: {e}") from e

    elif provider == Provider.OPENAI:
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise Exception(
                "OPENAI_API_KEY not set. Add it to .env or provide in settings."
            )
        try:
            async for text in _review_with_openai(user_message, model, key):
                yield text
        except openai.APIError as e:
            raise Exception(f"Review failed for {filename}: {e}") from e

    else:
        raise Exception(f"Unknown provider: {provider}")
