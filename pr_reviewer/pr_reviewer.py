"""PR Reviewer - AI-powered GitHub PR code review."""

import reflex as rx

from pr_reviewer.components import (
    diff_view,
    error_display,
    file_drawer,
    header,
    pr_input,
    pr_metadata,
    review_panel,
    settings_panel,
)
from pr_reviewer.state import PRState


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
