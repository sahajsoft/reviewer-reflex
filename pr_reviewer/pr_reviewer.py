"""PR Reviewer - AI-powered GitHub PR code review."""

import reflex as rx

from pr_reviewer.components.diff_view import diff_view
from pr_reviewer.components.file_drawer import file_drawer, file_drawer_trigger
from pr_reviewer.components.header import header
from pr_reviewer.components.review_panel import review_panel
from pr_reviewer.components.settings import settings_panel
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


def pr_description() -> rx.Component:
    """Collapsible PR description section."""
    return rx.cond(
        PRState.has_pr_body,
        rx.box(
            rx.hstack(
                rx.icon_button(
                    rx.cond(
                        PRState.description_expanded,
                        rx.icon("chevron-down", size=16),
                        rx.icon("chevron-right", size=16),
                    ),
                    variant="ghost",
                    size="1",
                    on_click=PRState.toggle_description,  # pyright: ignore[reportArgumentType]
                ),
                rx.text("Description", size="2", weight="medium", color="gray"),
                spacing="1",
                align="center",
                cursor="pointer",
                on_click=PRState.toggle_description,  # pyright: ignore[reportArgumentType]
            ),
            rx.cond(
                PRState.description_expanded,
                rx.box(
                    rx.markdown(PRState.pr_body, size="2"),
                    padding_left="6",
                    padding_top="2",
                ),
                rx.fragment(),
            ),
            width="100%",
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
                pr_description(),
                rx.divider(),
                rx.hstack(
                    file_drawer_trigger(),
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
    """Main content area with diff view and review panel."""

    return rx.cond(
        PRState.has_pr_loaded,
        rx.fragment(
            file_drawer(),  # Drawer - renders as overlay
            rx.hstack(
                rx.box(
                    diff_view(),
                    flex="1",
                    min_width="0",
                    overflow="hidden",
                    height="100%",
                ),
                rx.box(
                    review_panel(),
                    width="40%",
                    min_width="400px",
                    flex_shrink="0",
                    height="100%",
                    overflow="hidden",
                ),
                spacing="4",
                width="100%",
                align="stretch",
                flex="1",
                min_height="0",
            ),
        ),
        rx.fragment(),
    )


def index() -> rx.Component:
    """Main page."""

    return rx.box(
        rx.vstack(
            header(),
            settings_panel(),
            pr_input(),
            error_display(),
            pr_metadata(),
            main_content(),
            spacing="4",
            justify="start",
            width="100%",
            flex="1",
            min_height="0",
        ),
        width="100%",
        height="100vh",
        overflow="hidden",
        display="flex",
        flex_direction="column",
        padding="2rem",
    )


app = rx.App()
app.add_page(index)
