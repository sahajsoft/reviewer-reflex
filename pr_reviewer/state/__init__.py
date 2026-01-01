"""State management for PR Reviewer.

This module provides the application state split into focused mixins:
- SettingsMixin: GitHub token and model configuration
- ReviewMixin: AI code review functionality
- PRDataMixin: PR data fetching and storage

The PRState class combines all mixins into a single unified state.
"""

import reflex as rx

from pr_reviewer.state.pr_data_mixin import PRDataMixin
from pr_reviewer.state.review_mixin import ReviewMixin
from pr_reviewer.state.settings_mixin import SettingsMixin

__all__ = [
    "PRDataMixin",
    "PRState",
    "ReviewMixin",
    "SettingsMixin",
]


class PRState(SettingsMixin, PRDataMixin, ReviewMixin, rx.State):
    """Combined state for the PR Reviewer application.

    This class inherits from all state mixins to provide a unified state
    that can be used throughout the application. The mixins are:

    - SettingsMixin: GitHub token, AI model selection, settings panel
    - PRDataMixin: PR URL, metadata, files, loading state
    - ReviewMixin: File reviews, review progress, review methods
    """

    pass
