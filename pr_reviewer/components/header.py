"""Header component with settings and review all button."""

import reflex as rx

from pr_reviewer.state import PRDataState, ReviewState, SettingsState


def settings_button() -> rx.Component:
    """Settings gear button."""
    return rx.icon_button(
        rx.icon("settings", size=20),
        variant="ghost",
        size="2",
        on_click=SettingsState.toggle_settings,  # pyright: ignore[reportArgumentType]
        title="Settings",
    )


def review_all_button() -> rx.Component:
    """Button to review all files."""
    return rx.cond(
        PRDataState.has_pr_loaded,
        rx.cond(
            ReviewState.is_reviewing_all,
            rx.button(
                rx.hstack(
                    rx.spinner(size="1"),
                    rx.text("Reviewing..."),
                    rx.badge(
                        ReviewState.review_progress_text,
                        color="blue",
                        variant="soft",
                    ),
                    spacing="2",
                ),
                disabled=True,
                size="2",
            ),
            rx.cond(
                ReviewState.all_files_reviewed,
                rx.button(
                    rx.hstack(
                        rx.icon("circle-check", size=16),
                        rx.text("All Reviewed"),
                        rx.badge(
                            ReviewState.review_progress_text,
                            color="green",
                            variant="soft",
                        ),
                        spacing="2",
                    ),
                    disabled=True,
                    color="green",
                    variant="soft",
                    size="2",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("sparkles", size=16),
                        rx.text("Review All"),
                        rx.cond(
                            ReviewState.reviewed_file_count > 0,
                            rx.badge(
                                ReviewState.review_progress_text,
                                color="blue",
                                variant="soft",
                            ),
                            rx.fragment(),
                        ),
                        spacing="2",
                    ),
                    on_click=ReviewState.review_all_files,  # pyright: ignore[reportArgumentType]
                    disabled=ReviewState.is_reviewing
                    | (ReviewState.reviewable_file_count == 0),
                    size="2",
                ),
            ),
        ),
        rx.fragment(),
    )


def header() -> rx.Component:
    """Application header with title and controls."""
    return rx.hstack(
        rx.vstack(
            rx.heading("PR Reviewer", size="9"),
            rx.text("AI-powered GitHub PR code review", size="5", color="gray"),
            spacing="1",
            align="start",
        ),
        rx.spacer(),
        rx.hstack(
            review_all_button(),
            settings_button(),
            rx.color_mode.button(),
            spacing="2",
            align="center",
        ),
        width="100%",
        align="center",
        padding_bottom="4",
    )
