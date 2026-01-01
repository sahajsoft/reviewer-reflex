"""Application state for PR Reviewer."""

import collections.abc
from typing import Any

import reflex as rx

from pr_reviewer.models import DEFAULT_MODEL
from pr_reviewer.services.github import fetch_pr_files, fetch_pr_metadata, parse_pr_url
from pr_reviewer.services.reviewer import review_diff


class PRState(rx.State):
    """State for the PR Reviewer application."""

    pr_url: str = ""

    pr_title: str = ""
    pr_author: str = ""
    pr_body: str = ""
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

    # Settings state
    settings_open: bool = False
    github_token: str = ""
    model: str = DEFAULT_MODEL

    # UI state
    file_drawer_open: bool = False
    description_expanded: bool = False

    # Review all state
    is_reviewing_all: bool = False
    review_all_current_index: int = 0

    def set_pr_url(self, value: str) -> None:
        """Set the PR URL."""
        self.pr_url = value

    @rx.var
    def has_pr_loaded(self) -> bool:
        """Check if a PR has been loaded."""
        return bool(self.pr_title)

    @rx.var
    def has_pr_body(self) -> bool:
        """Check if the PR has a description."""
        return bool(self.pr_body and self.pr_body.strip())

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

    @rx.var
    def reviewable_files(self) -> list[dict[str, Any]]:
        """Get files that have diffs and can be reviewed."""
        return [f for f in self.files if f.get("patch")]

    @rx.var
    def reviewable_file_count(self) -> int:
        """Get the count of reviewable files."""
        return len(self.reviewable_files)

    @rx.var
    def reviewed_file_count(self) -> int:
        """Get the count of files that have been reviewed."""
        reviewable = [f.get("filename") for f in self.files if f.get("patch")]
        return len([f for f in reviewable if f in self.file_reviews])

    @rx.var
    def review_progress_text(self) -> str:
        """Get progress text for review all."""
        return f"{self.reviewed_file_count}/{self.reviewable_file_count}"

    @rx.var
    def all_files_reviewed(self) -> bool:
        """Check if all reviewable files have been reviewed."""
        return (
            self.reviewed_file_count == self.reviewable_file_count
            and self.reviewable_file_count > 0
        )

    def select_file(self, filename: str) -> None:
        """Select a file to view."""
        self.selected_file = filename

    def toggle_settings(self) -> None:
        """Toggle the settings panel."""
        self.settings_open = not self.settings_open

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

    def set_model(self, value: str) -> None:
        """Set the AI model."""
        self.model = value

    def set_github_token(self, value: str) -> None:
        """Set the GitHub token."""
        self.github_token = value

    async def fetch_pr(
        self, form_data: dict[str, Any] | None = None
    ) -> collections.abc.AsyncGenerator[None, None]:
        """Fetch PR data from GitHub."""
        self.error_message = ""
        self.pr_title = ""
        self.pr_author = ""
        self.pr_body = ""
        self.pr_base_branch = ""
        self.pr_head_branch = ""
        self.total_additions = 0
        self.total_deletions = 0
        self.files = []
        self.selected_file = ""
        self.file_reviews = {}
        self.review_error = ""
        self.description_expanded = False

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
            token = self.github_token or None
            metadata = await fetch_pr_metadata(owner, repo, pr_number, token=token)
            self.pr_title = metadata.get("title", "")
            self.pr_author = metadata.get("user", {}).get("login", "")
            self.pr_body = metadata.get("body", "") or ""
            self.pr_base_branch = metadata.get("base", {}).get("ref", "")
            self.pr_head_branch = metadata.get("head", {}).get("ref", "")
            self.total_additions = metadata.get("additions", 0)
            self.total_deletions = metadata.get("deletions", 0)

            files_data = await fetch_pr_files(owner, repo, pr_number, token=token)
            self.files = files_data.get("files", [])
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False

    async def review_file(self) -> collections.abc.AsyncGenerator[None, None]:
        """Review the currently selected file using AI."""

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
            async for chunk in review_diff(target_file, diff, model=self.model):
                self.file_reviews[target_file] += chunk
                self.file_reviews = self.file_reviews  # Trigger state update
                yield
        except Exception as e:
            self.review_error = str(e)
        finally:
            self.is_reviewing = False
            self.current_review_file = ""

    async def review_all_files(self) -> collections.abc.AsyncGenerator[None, None]:
        """Review all files with diffs using AI."""

        reviewable = [f for f in self.files if f.get("patch")]
        if not reviewable:
            return

        self.review_error = ""
        self.is_reviewing_all = True
        self.is_reviewing = True
        yield

        try:
            for idx, file_data in enumerate(reviewable):
                filename = file_data.get("filename", "")
                diff = file_data.get("patch", "")

                if not filename or not diff:
                    continue

                # Skip already reviewed files
                if filename in self.file_reviews:
                    continue

                self.review_all_current_index = idx
                self.current_review_file = filename
                self.file_reviews[filename] = ""
                yield

                try:
                    async for chunk in review_diff(filename, diff, model=self.model):
                        self.file_reviews[filename] += chunk
                        self.file_reviews = self.file_reviews  # Trigger state update
                        yield
                except Exception as e:
                    self.file_reviews[filename] = f"Error: {e}"
                    yield
        finally:
            self.is_reviewing_all = False
            self.is_reviewing = False
            self.current_review_file = ""
