"""PR Reviewer - AI-powered GitHub PR code review."""

import reflex as rx

from pr_reviewer.state import PRState


def pr_input() -> rx.Component:
    """Input section for PR URL."""
    return rx.hstack(
        rx.input(
            placeholder="https://github.com/owner/repo/pull/123",
            value=PRState.pr_url,
            on_change=PRState.set_pr_url,  # pyright: ignore[reportArgumentType]
            width="400px",
            disabled=PRState.is_loading,
        ),
        rx.button(
            rx.cond(
                PRState.is_loading,
                rx.hstack(
                    rx.spinner(size="1"),
                    rx.text("Loading..."),
                    spacing="2",
                ),
                rx.text("Fetch PR"),
            ),
            on_click=PRState.fetch_pr,  # pyright: ignore[reportArgumentType]
            disabled=PRState.is_loading,
        ),
        spacing="2",
    )


def error_display() -> rx.Component:
    """Display error messages."""
    return rx.cond(
        PRState.error_message != "",
        rx.callout(
            PRState.error_message,
            icon="triangle-alert",
            color="red",
            width="100%",
            max_width="600px",
        ),
        rx.fragment(),
    )


def pr_metadata() -> rx.Component:
    """Display PR metadata when loaded."""
    return rx.cond(
        PRState.has_pr_loaded,
        rx.card(
            rx.vstack(
                rx.heading(PRState.pr_title, size="5"),
                rx.hstack(
                    rx.badge(PRState.pr_author, color="blue"),
                    rx.text("•", color="gray"),
                    rx.text(
                        PRState.pr_base_branch + " ← " + PRState.pr_head_branch,
                        color="gray",
                        size="2",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.divider(),
                rx.hstack(
                    rx.hstack(
                        rx.text("+", color="green", weight="bold"),
                        rx.text(PRState.total_additions, color="green"),
                        spacing="1",
                    ),
                    rx.hstack(
                        rx.text("-", color="red", weight="bold"),
                        rx.text(PRState.total_deletions, color="red"),
                        spacing="1",
                    ),
                    rx.text("•", color="gray"),
                    rx.text(
                        PRState.file_count.to_string() + " files changed",  # pyright: ignore[reportAttributeAccessIssue]
                        color="gray",
                    ),
                    spacing="3",
                    align="center",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            width="100%",
            max_width="600px",
        ),
        rx.fragment(),
    )


def index() -> rx.Component:
    """Main page."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("PR Reviewer", size="9"),
            rx.text("AI-powered GitHub PR code review", size="5", color="gray"),
            pr_input(),
            error_display(),
            pr_metadata(),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
    )


app = rx.App()
app.add_page(index)
