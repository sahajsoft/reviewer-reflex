"""File tree component for displaying changed files."""

import reflex as rx

from pr_reviewer.state import PRState


def status_icon(status: str) -> rx.Component:
    """Return an icon based on file status."""
    return rx.match(  # pyright: ignore[reportReturnType]
        status,
        ("added", rx.text("+", color="green", weight="bold", size="2")),
        ("removed", rx.text("-", color="red", weight="bold", size="2")),
        ("renamed", rx.text("R", color="orange", weight="bold", size="2")),
        rx.text("M", color="blue", weight="bold", size="2"),  # default: modified
    )


def file_item(file: dict) -> rx.Component:
    """Render a single file item."""
    filename = file["filename"]
    status = file["status"]
    additions = file["additions"].to(int)
    deletions = file["deletions"].to(int)

    return rx.box(
        rx.hstack(
            status_icon(status),
            rx.text(
                filename,
                size="2",
                style={"word_break": "break_all"},
                flex="1",
            ),
            rx.hstack(
                rx.cond(
                    additions > 0,
                    rx.text(rx.Var.create(f"+{additions}"), color="green", size="1"),
                    rx.fragment(),
                ),
                rx.cond(
                    deletions > 0,
                    rx.text(rx.Var.create(f"-{deletions}"), color="red", size="1"),
                    rx.fragment(),
                ),
                spacing="1",
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        padding="2",
        border_radius="md",
        cursor="pointer",
        _hover={"background": rx.color("gray", 3)},
        background=rx.cond(
            PRState.selected_file == filename,
            rx.color("blue", 3),
            "transparent",
        ),
        on_click=lambda: PRState.select_file(filename),  # pyright: ignore[reportCallIssue]
    )


def file_tree() -> rx.Component:
    """Component showing the list of changed files."""
    return rx.cond(
        PRState.has_pr_loaded,
        rx.box(
            rx.vstack(
                rx.text("Changed Files", weight="bold", size="3"),
                rx.divider(),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(PRState.files, file_item),
                        spacing="1",
                        width="100%",
                    ),
                    type="auto",
                    scrollbars="vertical",
                    style={"max_height": "60vh"},
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            padding="3",
            border_radius="lg",
            border=f"1px solid {rx.color('gray', 5)}",
            width="100%",
            min_width="250px",
        ),
        rx.fragment(),
    )
