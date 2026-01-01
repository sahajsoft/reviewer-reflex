"""Settings state mixin for token and model configuration."""

import reflex as rx

from pr_reviewer.models import DEFAULT_MODEL


class SettingsMixin(rx.State, mixin=True):
    """Mixin for settings-related state."""

    settings_open: bool = False
    github_token: str = ""
    model: str = DEFAULT_MODEL

    @rx.var
    def has_github_token(self) -> bool:
        """Check if a GitHub token is configured."""
        return bool(self.github_token)

    def toggle_settings(self) -> None:
        """Toggle the settings panel."""
        self.settings_open = not self.settings_open

    def set_model(self, value: str) -> None:
        """Set the AI model."""
        self.model = value

    def set_github_token(self, value: str) -> None:
        """Set the GitHub token."""
        self.github_token = value
