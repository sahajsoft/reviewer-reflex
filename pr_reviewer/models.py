"""Model definitions for PR Reviewer - single source of truth."""


class FileStatus:
    """Constants for file status values."""

    ADDED = "added"
    REMOVED = "removed"
    RENAMED = "renamed"
    MODIFIED = "modified"


class Provider:
    """AI provider constants."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"


ANTHROPIC_MODELS = {
    "opus": ("claude-opus-4-5-20251101", "Claude Opus 4.5"),
    "sonnet": ("claude-sonnet-4-5-20250929", "Claude Sonnet 4.5"),
    "haiku": ("claude-haiku-4-5-20251001", "Claude Haiku 4.5"),
}

OPENAI_MODELS = {
    "gpt-5.2": ("gpt-5.2", "GPT-5.2"),
    "codex": ("gpt-5.1-codex", "GPT-5.1 Codex"),
    "codex-mini": ("gpt-5.1-codex-mini", "GPT-5.1 Codex Mini"),
    "gpt-4o": ("gpt-4o", "GPT-4o"),
}

PROVIDERS = {
    Provider.ANTHROPIC: ("Anthropic", ANTHROPIC_MODELS),
    Provider.OPENAI: ("OpenAI", OPENAI_MODELS),
}

DEFAULT_PROVIDER = Provider.ANTHROPIC
DEFAULT_MODEL_KEY = "sonnet"
DEFAULT_MODEL = ANTHROPIC_MODELS[DEFAULT_MODEL_KEY][0]


def get_models_for_provider(provider: str) -> list[tuple[str, str]]:
    """Get list of (model_id, display_name) tuples for a provider."""
    if provider == Provider.ANTHROPIC:
        return [(v[0], v[1]) for v in ANTHROPIC_MODELS.values()]
    elif provider == Provider.OPENAI:
        return [(v[0], v[1]) for v in OPENAI_MODELS.values()]
    return []


def get_default_model_for_provider(provider: str) -> str:
    """Get the default model ID for a provider."""
    if provider == Provider.ANTHROPIC:
        return ANTHROPIC_MODELS["sonnet"][0]
    elif provider == Provider.OPENAI:
        return OPENAI_MODELS["gpt-5.2"][0]
    return DEFAULT_MODEL


# For backwards compatibility
MODELS = ANTHROPIC_MODELS
AVAILABLE_MODELS = [(v[0], v[1]) for v in ANTHROPIC_MODELS.values()]
