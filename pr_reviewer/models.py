"""Model definitions for PR Reviewer - single source of truth."""


class FileStatus:
    """Constants for file status values."""

    ADDED = "added"
    REMOVED = "removed"
    RENAMED = "renamed"
    MODIFIED = "modified"


MODELS = {
    "opus": ("claude-opus-4-5-20251101", "Claude Opus 4.5"),
    "sonnet": ("claude-sonnet-4-5-20250929", "Claude Sonnet 4.5"),
    "haiku": ("claude-haiku-4-5-20251001", "Claude Haiku 4.5"),
}
DEFAULT_MODEL_KEY = "sonnet"
DEFAULT_MODEL = MODELS[DEFAULT_MODEL_KEY][0]
AVAILABLE_MODELS = [(v[0], v[1]) for v in MODELS.values()]
