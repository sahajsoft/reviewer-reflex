"""File drawer component for displaying changed files."""

import reflex as rx

from pr_reviewer.constants import FileStatus
from pr_reviewer.state import PRDataState


def file_status_indicator(status: str) -> rx.Component:
    """Return an icon based on file status."""
    return rx.match(  # pyright: ignore[reportReturnType]
        status,
        (FileStatus.ADDED, rx.text("+", color="green", weight="bold", size="2")),
        (FileStatus.REMOVED, rx.text("-", color="red", weight="bold", size="2")),
        (FileStatus.RENAMED, rx.text("R", color="orange", weight="bold", size="2")),
        rx.text("M", color="blue", weight="bold", size="2"),  # default: modified
    )


def file_list_item(file: dict) -> rx.Component:
    """Render a single file item."""
    filename = file["filename"]
    status = file["status"]
    additions = file["additions"].to(int)
    deletions = file["deletions"].to(int)

    return rx.box(
        rx.hstack(
            file_status_indicator(status),
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
            PRDataState.selected_file == filename,
            rx.color("blue", 3),
            "transparent",
        ),
        on_click=[
            lambda: PRDataState.select_file(filename),  # pyright: ignore[reportCallIssue]
            PRDataState.close_file_drawer,  # pyright: ignore[reportArgumentType]
        ],
    )


def file_drawer_content() -> rx.Component:
    """Inner content for the file drawer."""
    return rx.vstack(
        rx.hstack(
            rx.text("Changed Files", weight="bold", size="4"),
            rx.spacer(),
            rx.icon_button(
                rx.icon("x", size=18),
                variant="ghost",
                size="1",
                on_click=PRDataState.toggle_file_drawer,  # pyright: ignore[reportArgumentType]
            ),
            width="100%",
            align="center",
        ),
        rx.divider(),
        rx.scroll_area(
            rx.vstack(
                rx.foreach(PRDataState.files, file_list_item),
                spacing="1",
                width="100%",
            ),
            type="auto",
            scrollbars="vertical",
            style={"height": "calc(100vh - 120px)"},
        ),
        spacing="3",
        align="start",
        width="100%",
        height="100%",
    )


def file_drawer() -> rx.Component:
    """Drawer component for the file drawer."""
    return rx.drawer.root(
        rx.drawer.overlay(z_index="5"),
        rx.drawer.portal(
            rx.drawer.content(
                file_drawer_content(),
                height="100%",
                width="320px",
                padding="4",
                background_color=rx.color("gray", 1),
            ),
        ),
        open=PRDataState.file_drawer_open,
        on_open_change=PRDataState.set_file_drawer_open,  # pyright: ignore[reportArgumentType]
        direction="left",
    )


def file_drawer_trigger() -> rx.Component:
    """Button to open the file drawer."""
    return rx.cond(
        PRDataState.has_pr_loaded,
        rx.button(
            rx.icon("panel-left", size=16),
            rx.text("Files"),
            rx.badge(PRDataState.file_count, variant="soft"),
            variant="outline",
            size="2",
            on_click=PRDataState.toggle_file_drawer,  # pyright: ignore[reportArgumentType]
        ),
        rx.fragment(),
    )
