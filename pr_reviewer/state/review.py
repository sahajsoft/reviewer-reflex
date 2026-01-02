"""Review state for AI code review functionality."""

from __future__ import annotations

import collections.abc
from typing import Any

import reflex as rx

from pr_reviewer.services.reviewer import review_diff


class ReviewState(rx.State):
    """State for AI code review functionality."""

    file_reviews: dict[str, str] = {}
    current_review_file: str = ""
    is_reviewing: bool = False
    review_error: str = ""
    is_reviewing_all: bool = False
    review_all_current_index: int = 0

    # Synced from PRDataState for computed var access.
    # Reflex computed vars (@rx.var) cannot use async get_state() to access
    # other states, so we must sync these values when they change in PRDataState.
    # Sync points: PRDataState.fetch_pr() syncs files, PRDataState.select_file()
    # syncs selected_file.
    files: list[dict[str, Any]] = []
    selected_file: str = ""

    def _set_file_review(self, filename: str, content: str) -> None:
        """Set a file review, triggering proper state reactivity."""
        updated = dict(self.file_reviews)
        updated[filename] = content
        self.file_reviews = updated

    def set_files(self, files: list[dict[str, Any]]) -> None:
        """Set files for review (called after PR fetch)."""
        self.files = files
        self.file_reviews = {}

    def reset_review_state(self) -> None:
        """Reset all review-related state."""
        self.file_reviews = {}
        self.current_review_file = ""
        self.is_reviewing = False
        self.review_error = ""
        self.is_reviewing_all = False
        self.review_all_current_index = 0
        self.files = []
        self.selected_file = ""

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
        return [f for f in self.files if f.get("patch", "").strip()]

    @rx.var
    def reviewable_file_count(self) -> int:
        """Get the count of reviewable files."""
        return len(self.reviewable_files)

    @rx.var
    def reviewed_file_count(self) -> int:
        """Get the count of files that have been reviewed."""
        reviewable = self.reviewable_files
        return len([f for f in reviewable if f.get("filename") in self.file_reviews])

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

    async def review_file(self) -> collections.abc.AsyncGenerator[None, None]:
        """Review the currently selected file using AI."""
        from pr_reviewer.state.settings import SettingsState

        if self.is_reviewing:
            return  # Already reviewing, prevent concurrent reviews

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
        self._set_file_review(target_file, "")
        yield

        try:
            settings = await self.get_state(SettingsState)
            async for chunk in review_diff(
                target_file,
                diff,
                model=settings.model,
                provider=settings.provider,
            ):
                self._set_file_review(
                    target_file, self.file_reviews.get(target_file, "") + chunk
                )
                yield
        except Exception as e:
            self.review_error = str(e)
        finally:
            self.is_reviewing = False
            self.current_review_file = ""

    async def review_all_files(self) -> collections.abc.AsyncGenerator[None, None]:
        """Review all files with diffs using AI."""
        from pr_reviewer.state.settings import SettingsState

        if self.is_reviewing:
            return  # Already reviewing, prevent concurrent reviews

        reviewable = self.reviewable_files
        if not reviewable:
            return

        self.review_error = ""
        self.is_reviewing_all = True
        self.is_reviewing = True
        yield

        try:
            settings = await self.get_state(SettingsState)
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
                self._set_file_review(filename, "")
                yield

                try:
                    async for chunk in review_diff(
                        filename,
                        diff,
                        model=settings.model,
                        provider=settings.provider,
                    ):
                        self._set_file_review(
                            filename, self.file_reviews.get(filename, "") + chunk
                        )
                        yield
                except Exception as e:
                    self._set_file_review(filename, f"Error: {e}")
                    yield
        finally:
            self.is_reviewing_all = False
            self.is_reviewing = False
            self.current_review_file = ""
