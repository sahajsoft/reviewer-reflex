"""Application state for PR Reviewer."""

import collections.abc
from typing import Any

import reflex as rx

from pr_reviewer.services.github import fetch_pr_files, fetch_pr_metadata, parse_pr_url


class PRState(rx.State):
    """State for the PR Reviewer application."""

    pr_url: str = ""

    pr_title: str = ""
    pr_author: str = ""
    pr_base_branch: str = ""
    pr_head_branch: str = ""
    total_additions: int = 0
    total_deletions: int = 0
    files: list[dict[str, Any]] = []
    is_loading: bool = False
    error_message: str = ""
    selected_file: str = ""

    def set_pr_url(self, value: str) -> None:
        """Set the PR URL."""
        self.pr_url = value

    @rx.var
    def has_pr_loaded(self) -> bool:
        """Check if a PR has been loaded."""
        return bool(self.pr_title)

    @rx.var
    def file_count(self) -> int:
        """Get the number of files changed."""
        return len(self.files)

    @rx.var
    def selected_file_data(self) -> dict[str, Any] | None:
        """Get the data for the currently selected file."""
        if not self.selected_file:
            return None
        for f in self.files:
            if f.get("filename") == self.selected_file:
                return f
        return None

    def select_file(self, filename: str) -> None:
        """Select a file to view."""
        self.selected_file = filename

    async def fetch_pr(
        self, form_data: dict[str, Any] | None = None
    ) -> collections.abc.AsyncGenerator[None, None]:
        """Fetch PR data from GitHub."""
        self.error_message = ""
        self.pr_title = ""
        self.pr_author = ""
        self.pr_base_branch = ""
        self.pr_head_branch = ""
        self.total_additions = 0
        self.total_deletions = 0
        self.files = []
        self.selected_file = ""

        if not self.pr_url.strip():
            self.error_message = "Please enter a PR URL"
            return

        parsed = parse_pr_url(self.pr_url)
        if not parsed:
            self.error_message = "Invalid GitHub PR URL. Expected format: https://github.com/owner/repo/pull/123"
            return

        owner, repo, pr_number = parsed
        self.is_loading = True
        yield

        try:
            metadata = await fetch_pr_metadata(owner, repo, pr_number)
            self.pr_title = metadata.get("title", "")
            self.pr_author = metadata.get("user", {}).get("login", "")
            self.pr_base_branch = metadata.get("base", {}).get("ref", "")
            self.pr_head_branch = metadata.get("head", {}).get("ref", "")
            self.total_additions = metadata.get("additions", 0)
            self.total_deletions = metadata.get("deletions", 0)

            files_data = await fetch_pr_files(owner, repo, pr_number)
            self.files = files_data.get("files", [])
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False
