"""PR data state for fetching and storing PR information."""

from __future__ import annotations

import collections.abc
from typing import TYPE_CHECKING, Any

import reflex as rx

from pr_reviewer.services.github import fetch_pr_files, fetch_pr_metadata, parse_pr_url

if TYPE_CHECKING:
    pass


class PRDataState(rx.State):
    """State for PR data fetching and storage."""

    # PR input
    pr_url: str = ""

    # PR metadata (from GitHub API)
    pr_title: str = ""
    pr_author: str = ""
    pr_description: str = ""
    pr_base_branch: str = ""
    pr_head_branch: str = ""
    total_additions: int = 0
    total_deletions: int = 0

    # PR files
    files: list[dict[str, Any]] = []
    files_truncated: bool = False
    selected_file: str = ""

    # Loading/error state
    is_loading: bool = False
    error_message: str = ""

    # UI state
    file_drawer_open: bool = False
    description_expanded: bool = False

    def set_pr_url(self, value: str) -> None:
        """Set the PR URL."""
        self.pr_url = value

    @rx.var
    def has_pr_loaded(self) -> bool:
        """Check if a PR has been loaded."""
        return bool(self.pr_title)

    @rx.var
    def has_pr_description(self) -> bool:
        """Check if the PR has a description."""
        return bool(self.pr_description and self.pr_description.strip())

    @rx.var
    def file_count(self) -> int:
        """Get the number of files changed."""
        return len(self.files)

    def _find_file_by_name(self, filename: str) -> dict[str, Any] | None:
        """Find file data by filename."""
        for f in self.files:
            if f.get("filename") == filename:
                return f
        return None

    @rx.var
    def selected_file_data(self) -> dict[str, Any] | None:
        """Get the data for the currently selected file."""
        if not self.selected_file:
            return None
        return self._find_file_by_name(self.selected_file)

    @rx.var
    def selected_file_diff(self) -> str:
        """Get the diff patch for the currently selected file."""
        if not self.selected_file:
            return ""
        file_data = self._find_file_by_name(self.selected_file)
        return file_data.get("patch", "") if file_data else ""

    @rx.var
    def selected_file_has_diff(self) -> bool:
        """Check if the selected file has a diff available."""
        return bool(self.selected_file_diff)

    @rx.var
    def selected_file_additions(self) -> int:
        """Get additions count for the selected file."""
        if not self.selected_file:
            return 0
        file_data = self._find_file_by_name(self.selected_file)
        return file_data.get("additions", 0) if file_data else 0

    @rx.var
    def selected_file_deletions(self) -> int:
        """Get deletions count for the selected file."""
        if not self.selected_file:
            return 0
        file_data = self._find_file_by_name(self.selected_file)
        return file_data.get("deletions", 0) if file_data else 0

    @rx.var
    def selected_file_status(self) -> str:
        """Get status for the selected file."""
        if not self.selected_file:
            return ""
        file_data = self._find_file_by_name(self.selected_file)
        return file_data.get("status", "") if file_data else ""

    async def select_file(self, filename: str) -> None:
        """Select a file to view."""
        self.selected_file = filename
        # Sync to ReviewState
        from pr_reviewer.state.review import ReviewState

        review_state = await self.get_state(ReviewState)
        review_state.selected_file = filename

    def toggle_description(self) -> None:
        """Toggle the description expanded state."""
        self.description_expanded = not self.description_expanded

    def toggle_file_drawer(self) -> None:
        """Toggle the file drawer."""
        self.file_drawer_open = not self.file_drawer_open

    def close_file_drawer(self) -> None:
        """Close the file drawer."""
        self.file_drawer_open = False

    def set_file_drawer_open(self, value: bool) -> None:
        """Set the file drawer open state."""
        self.file_drawer_open = value

    def _reset_pr_state(self) -> None:
        """Reset all PR-related state."""
        self.error_message = ""
        self.pr_title = ""
        self.pr_author = ""
        self.pr_description = ""
        self.pr_base_branch = ""
        self.pr_head_branch = ""
        self.total_additions = 0
        self.total_deletions = 0
        self.files = []
        self.files_truncated = False
        self.selected_file = ""
        self.description_expanded = False

    async def fetch_pr(self) -> collections.abc.AsyncGenerator[None, None]:
        """Fetch PR data from GitHub."""
        from pr_reviewer.state.review import ReviewState
        from pr_reviewer.state.settings import SettingsState

        self._reset_pr_state()

        # Reset ReviewState
        review_state = await self.get_state(ReviewState)
        review_state.reset_review_state()

        if not self.pr_url.strip():
            self.error_message = "Please enter a PR URL"
            return

        parsed = parse_pr_url(self.pr_url)
        if not parsed:
            self.error_message = (
                "Invalid GitHub PR URL. Expected format: "
                "https://github.com/owner/repo/pull/123"
            )
            return

        owner, repo, pr_number = parsed
        self.is_loading = True
        yield

        try:
            settings = await self.get_state(SettingsState)
            token = settings.github_token or None
            metadata = await fetch_pr_metadata(owner, repo, pr_number, token=token)
            self.pr_title = metadata.get("title", "")
            self.pr_author = metadata.get("user", {}).get("login", "")
            self.pr_description = metadata.get("body", "") or ""
            self.pr_base_branch = metadata.get("base", {}).get("ref", "")
            self.pr_head_branch = metadata.get("head", {}).get("ref", "")
            self.total_additions = metadata.get("additions", 0)
            self.total_deletions = metadata.get("deletions", 0)

            files_data = await fetch_pr_files(owner, repo, pr_number, token=token)
            self.files = files_data.get("files", [])
            self.files_truncated = files_data.get("truncated", False)

            # Sync files to ReviewState
            review_state.set_files(self.files)
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False
