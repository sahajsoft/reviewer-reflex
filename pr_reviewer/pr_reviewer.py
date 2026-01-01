"""PR Reviewer - AI-powered GitHub PR code review."""

import reflex as rx

from pr_reviewer.components.file_tree import file_tree
from pr_reviewer.state import PRState


def pr_input() -> rx.Component:
    """Input section for PR URL."""
    return rx.form(
        rx.hstack(
            rx.input(
                placeholder="https://github.com/owner/repo/pull/123",
                value=PRState.pr_url,
                on_change=PRState.set_pr_url,  # pyright: ignore[reportArgumentType]
                width="400px",
                disabled=PRState.is_loading,
                name="pr_url",
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
                type="submit",
                disabled=PRState.is_loading,
            ),
            spacing="2",
        ),
        on_submit=PRState.fetch_pr,  # pyright: ignore[reportArgumentType]
        reset_on_submit=False,
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
        ),
        rx.fragment(),
    )


def main_content() -> rx.Component:
    """Main content area with file tree, diff view, and review panel."""
    from pr_reviewer.components.diff_view import diff_view
    from pr_reviewer.components.review_panel import review_panel

    return rx.cond(
        PRState.has_pr_loaded,
        rx.hstack(
            rx.box(
                file_tree(),
                width="250px",
                flex_shrink="0",
            ),
            rx.box(
                diff_view(),
                flex="1",
                min_width="0",
            ),
            rx.box(
                review_panel(),
                width="350px",
                flex_shrink="0",
            ),
            spacing="4",
            width="100%",
            align="start",
        ),
        rx.fragment(),
    )


def index() -> rx.Component:
    """Main page."""
    from pr_reviewer.components.header import header
    from pr_reviewer.components.settings import settings_panel

    return rx.container(
        rx.vstack(
            header(),
            settings_panel(),
            pr_input(),
            error_display(),
            pr_metadata(),
            main_content(),
            spacing="5",
            justify="start",
            padding_top="4",
            min_height="85vh",
            width="100%",
        ),
        size="4",
    )


app = rx.App()
app.add_page(index)
