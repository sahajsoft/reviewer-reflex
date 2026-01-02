"""State management for PR Reviewer.

This module provides the application state split into focused state classes:
- SettingsState: GitHub token and model configuration
- ReviewState: AI code review functionality
- PRDataState: PR data fetching and storage

Components reference states directly using get_state() for cross-state access.
"""

from pr_reviewer.state.pr_data import PRDataState
from pr_reviewer.state.review import ReviewState
from pr_reviewer.state.settings import SettingsState

__all__ = [
    "PRDataState",
    "ReviewState",
    "SettingsState",
]
