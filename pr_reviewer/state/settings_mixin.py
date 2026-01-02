"""Settings state mixin for token and model configuration."""

import reflex as rx

from pr_reviewer.models import (
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    Provider,
    get_default_model_for_provider,
    get_models_for_provider,
)


class SettingsMixin(rx.State, mixin=True):
    """Mixin for settings-related state."""

    settings_open: bool = False
    github_token: str = ""
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL

    @rx.var
    def has_github_token(self) -> bool:
        """Check if a GitHub token is configured."""
        return bool(self.github_token)

    @rx.var
    def provider_display_name(self) -> str:
        """Get the display name for the current provider."""
        if self.provider == Provider.ANTHROPIC:
            return "Anthropic"
        elif self.provider == Provider.OPENAI:
            return "OpenAI"
        return self.provider

    @rx.var
    def available_models(self) -> list[tuple[str, str]]:
        """Get available models for the current provider."""
        return get_models_for_provider(self.provider)

    @rx.var
    def available_model_names(self) -> list[str]:
        """Get display names of available models for the select dropdown."""
        return [display_name for _, display_name in self.available_models]

    @rx.var
    def model_display_name(self) -> str:
        """Get the display name for the current model."""
        for model_id, display_name in self.available_models:
            if model_id == self.model:
                return display_name
        return self.model

    def toggle_settings(self) -> None:
        """Toggle the settings panel."""
        self.settings_open = not self.settings_open

    def set_provider(self, value: str) -> None:
        """Set the AI provider and reset model to provider's default."""
        self.provider = value
        self.model = get_default_model_for_provider(value)

    def set_model(self, value: str) -> None:
        """Set the AI model by model ID."""
        self.model = value

    def set_model_by_display_name(self, display_name: str) -> None:
        """Set the AI model by display name."""
        for model_id, name in self.available_models:
            if name == display_name:
                self.model = model_id
                return

    def set_github_token(self, value: str) -> None:
        """Set the GitHub token."""
        self.github_token = value
