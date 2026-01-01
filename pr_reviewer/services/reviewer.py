"""AI code review service using Anthropic API."""

import os
from collections.abc import AsyncGenerator

import anthropic

from pr_reviewer.models import DEFAULT_MODEL

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


async def review_diff(
    filename: str,
    diff: str,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
) -> AsyncGenerator[str, None]:
    """Stream an AI code review for a diff.

    Args:
        filename: Name of the file being reviewed.
        diff: The diff patch content.
        model: Anthropic model to use.
        api_key: Optional API key (defaults to ANTHROPIC_API_KEY env var).

    Yields:
        Text chunks as they stream from the API.

    Raises:
        Exception: On API errors.
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise Exception(
            "ANTHROPIC_API_KEY not set. Add it to .env or provide in settings."
        )

    client = anthropic.AsyncAnthropic(api_key=key)

    user_message = f"""Review this diff for `{filename}`:

```diff
{diff}
```"""

    async with client.messages.stream(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
