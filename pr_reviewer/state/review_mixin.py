"""Review state mixin for AI code review functionality."""

import collections.abc
from typing import Any

import reflex as rx

from pr_reviewer.services.reviewer import review_diff


class ReviewMixin(rx.State, mixin=True):
    """Mixin for review-related state.

    Note: This mixin expects the following attributes from the parent state:
    - files: list[dict[str, Any]]
    - selected_file: str
    - provider: str
    - model: str
    - github_token: str
    """

    file_reviews: dict[str, str] = {}
    current_review_file: str = ""
    is_reviewing: bool = False
    review_error: str = ""
    is_reviewing_all: bool = False
    review_all_current_index: int = 0

    def _update_file_review(self, filename: str, content: str) -> None:
        """Update a file review, triggering proper state reactivity."""
        updated = dict(self.file_reviews)
        updated[filename] = content
        self.file_reviews = updated

    @rx.var
    def selected_file_review(self) -> str:
        """Get the review for the currently selected file."""
        if not self.selected_file:  # type: ignore[attr-defined]
            return ""
        return self.file_reviews.get(self.selected_file, "")  # type: ignore[attr-defined]

    @rx.var
    def has_selected_file_review(self) -> bool:
        """Check if the selected file has a review."""
        return bool(self.selected_file_review)

    @rx.var
    def is_reviewing_selected_file(self) -> bool:
        """Check if we're currently reviewing the selected file."""
        return self.is_reviewing and self.current_review_file == self.selected_file  # type: ignore[attr-defined]

    @rx.var
    def reviewable_files(self) -> list[dict[str, Any]]:
        """Get files that have diffs and can be reviewed."""
        return [f for f in self.files if f.get("patch", "").strip()]  # type: ignore[attr-defined]

    @rx.var
    def reviewable_file_count(self) -> int:
        """Get the count of reviewable files."""
        return len(self.reviewable_files)

    @rx.var
    def reviewed_file_count(self) -> int:
        """Get the count of files that have been reviewed."""
        return len(
            [f for f in self.reviewable_files if f.get("filename") in self.file_reviews]
        )

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
        if self.is_reviewing:
            return  # Already reviewing, prevent concurrent reviews

        target_file = self.selected_file  # type: ignore[attr-defined]
        if not target_file:
            return

        # Find the diff for this file
        diff = ""
        for f in self.files:  # type: ignore[attr-defined]
            if f.get("filename") == target_file:
                diff = f.get("patch", "")
                break

        if not diff:
            self.review_error = "No diff available for this file"
            return

        self.review_error = ""
        self.is_reviewing = True
        self.current_review_file = target_file
        self._update_file_review(target_file, "")
        yield

        try:
            async for chunk in review_diff(
                target_file,
                diff,
                model=self.model,  # type: ignore[attr-defined]
                provider=self.provider,  # type: ignore[attr-defined]
            ):
                self._update_file_review(
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
        if self.is_reviewing:
            return  # Already reviewing, prevent concurrent reviews

        if not self.reviewable_files:
            return

        self.review_error = ""
        self.is_reviewing_all = True
        self.is_reviewing = True
        yield

        try:
            for idx, file_data in enumerate(self.reviewable_files):
                filename = file_data.get("filename", "")
                diff = file_data.get("patch", "")

                if not filename or not diff:
                    continue

                # Skip already reviewed files
                if filename in self.file_reviews:
                    continue

                self.review_all_current_index = idx
                self.current_review_file = filename
                self._update_file_review(filename, "")
                yield

                try:
                    async for chunk in review_diff(
                        filename,
                        diff,
                        model=self.model,  # type: ignore[attr-defined]
                        provider=self.provider,  # type: ignore[attr-defined]
                    ):
                        self._update_file_review(
                            filename, self.file_reviews.get(filename, "") + chunk
                        )
                        yield
                except Exception as e:
                    self._update_file_review(filename, f"Error: {e}")
                    yield
        finally:
            self.is_reviewing_all = False
            self.is_reviewing = False
            self.current_review_file = ""
