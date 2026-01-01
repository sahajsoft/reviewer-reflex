"""Diff view component for displaying file changes."""

import reflex as rx

from pr_reviewer.models import FileStatus
from pr_reviewer.state import PRState


def diff_header() -> rx.Component:
    """Header showing filename and change stats."""
    return rx.hstack(
        rx.text(PRState.selected_file, weight="bold", size="3"),
        rx.spacer(),
        rx.hstack(
            rx.cond(
                PRState.selected_file_additions > 0,
                rx.text(
                    "+" + PRState.selected_file_additions.to_string(),  # pyright: ignore[reportAttributeAccessIssue]
                    color="green",
                    size="2",
                ),
                rx.fragment(),
            ),
            rx.cond(
                PRState.selected_file_deletions > 0,
                rx.text(
                    "-" + PRState.selected_file_deletions.to_string(),  # pyright: ignore[reportAttributeAccessIssue]
                    color="red",
                    size="2",
                ),
                rx.fragment(),
            ),
            rx.badge(
                PRState.selected_file_status,
                color=rx.match(
                    PRState.selected_file_status,
                    (FileStatus.ADDED, "green"),
                    (FileStatus.REMOVED, "red"),
                    (FileStatus.RENAMED, "orange"),
                    "blue",
                ),
                size="1",
            ),
            spacing="2",
            align="center",
        ),
        width="100%",
        align="center",
        padding_bottom="2",
    )


def diff_content() -> rx.Component:
    """Display the diff content with syntax highlighting."""
    return rx.cond(
        PRState.selected_file_has_diff,
        rx.scroll_area(
            rx.code_block(
                PRState.selected_file_diff,
                language="diff",
                show_line_numbers=True,
                wrap_long_lines=True,
                font_size="13px",
            ),
            type="auto",
            scrollbars="both",
            flex="1",
            min_height="0",
        ),
        rx.box(
            rx.vstack(
                rx.icon("file-x", size=32, color=rx.color("gray", 9)),
                rx.text("No diff available", color="gray", size="3"),
                rx.text(
                    "This file may be binary or too large to display",
                    color="gray",
                    size="2",
                ),
                spacing="2",
                align="center",
            ),
            padding="8",
            text_align="center",
            width="100%",
            flex="1",
        ),
    )


def diff_view() -> rx.Component:
    """Component for displaying the diff of a selected file."""
    return rx.cond(
        PRState.selected_file != "",
        rx.box(
            rx.vstack(
                diff_header(),
                rx.divider(),
                diff_content(),
                spacing="2",
                align="start",
                width="100%",
                height="100%",
                flex="1",
            ),
            padding="3",
            border_radius="lg",
            border=f"1px solid {rx.color('gray', 5)}",
            width="100%",
            height="100%",
            display="flex",
            flex_direction="column",
        ),
        rx.box(
            rx.vstack(
                rx.icon("file-code", size=48, color=rx.color("gray", 7)),
                rx.text("Select a file to view its diff", color="gray", size="3"),
                spacing="3",
                align="center",
            ),
            padding="8",
            text_align="center",
            width="100%",
            height="100%",
            display="flex",
            align_items="center",
            justify_content="center",
        ),
    )
