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

    # Review state
    file_reviews: dict[str, str] = {}
    current_review_file: str = ""
    is_reviewing: bool = False
    review_error: str = ""

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

    @rx.var
    def selected_file_diff(self) -> str:
        """Get the diff patch for the currently selected file."""
        if not self.selected_file:
            return ""
        for f in self.files:
            if f.get("filename") == self.selected_file:
                return f.get("patch", "")
        return ""

    @rx.var
    def selected_file_has_diff(self) -> bool:
        """Check if the selected file has a diff available."""
        return bool(self.selected_file_diff)

    @rx.var
    def selected_file_additions(self) -> int:
        """Get additions count for the selected file."""
        if not self.selected_file:
            return 0
        for f in self.files:
            if f.get("filename") == self.selected_file:
                return f.get("additions", 0)
        return 0

    @rx.var
    def selected_file_deletions(self) -> int:
        """Get deletions count for the selected file."""
        if not self.selected_file:
            return 0
        for f in self.files:
            if f.get("filename") == self.selected_file:
                return f.get("deletions", 0)
        return 0

    @rx.var
    def selected_file_status(self) -> str:
        """Get status for the selected file."""
        if not self.selected_file:
            return ""
        for f in self.files:
            if f.get("filename") == self.selected_file:
                return f.get("status", "")
        return ""

    @rx.var
    def selected_file_review(self) -> str:
        """Get the review for the currently selected file."""
        if not self.selected_file:
            return ""
        return self.file_reviews.get(self.selected_file, "")

    @rx.var
    def has_selected_file_review(self) -> bool:
        """Check if the selected file has a review."""
        return bool(self.selected_file_review)

    @rx.var
    def is_reviewing_selected_file(self) -> bool:
        """Check if we're currently reviewing the selected file."""
        return self.is_reviewing and self.current_review_file == self.selected_file

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
        self.file_reviews = {}
        self.review_error = ""

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

    async def review_file(self) -> collections.abc.AsyncGenerator[None, None]:
        """Review the currently selected file using AI."""
        from pr_reviewer.services.reviewer import review_diff

        target_file = self.selected_file
        if not target_file:
            return

        # Find the diff for this file
        diff = ""
        for f in self.files:
            if f.get("filename") == target_file:
                diff = f.get("patch", "")
                break

        if not diff:
            self.review_error = "No diff available for this file"
            return

        self.review_error = ""
        self.is_reviewing = True
        self.current_review_file = target_file
        self.file_reviews[target_file] = ""
        yield

        try:
            async for chunk in review_diff(target_file, diff):
                self.file_reviews[target_file] += chunk
                self.file_reviews = self.file_reviews  # Trigger state update
                yield
        except Exception as e:
            self.review_error = str(e)
        finally:
            self.is_reviewing = False
            self.current_review_file = ""
