"""Review panel component for displaying AI code reviews."""

import reflex as rx

from pr_reviewer.state import PRState


def review_button() -> rx.Component:
    """Button to trigger AI review of the selected file."""
    return rx.cond(
        PRState.is_reviewing_selected_file,
        rx.button(
            rx.hstack(
                rx.spinner(size="1"),
                rx.text("Reviewing..."),
                spacing="2",
            ),
            disabled=True,
            width="100%",
        ),
        rx.button(
            rx.hstack(
                rx.icon("sparkles", size=16),
                rx.text("Review This File"),
                spacing="2",
            ),
            on_click=PRState.review_file,  # pyright: ignore[reportArgumentType]
            disabled=~PRState.selected_file_has_diff | PRState.is_reviewing,
            width="100%",
        ),
    )


def review_content() -> rx.Component:
    """Display the AI review content."""
    return rx.cond(
        PRState.has_selected_file_review,
        rx.scroll_area(
            rx.box(
                rx.markdown(
                    PRState.selected_file_review,
                    component_map={
                        "code": lambda text: rx.code(
                            text,
                            style={
                                "white_space": "pre-wrap",
                                "word_break": "break-all",
                                "font_size": "12px",
                            },
                        ),
                    },
                ),
                padding="4",
                width="100%",
                font_size="14px",
                style={
                    "word_wrap": "break-word",
                    "overflow_wrap": "break-word",
                    "& pre": {
                        "white_space": "pre-wrap",
                        "word_break": "break-all",
                        "font_size": "12px",
                    },
                    "& code": {
                        "white_space": "pre-wrap",
                        "word_break": "break-all",
                        "font_size": "12px",
                    },
                },
            ),
            type="auto",
            scrollbars="both",
            flex="1",
            min_height="0",
            width="100%",
        ),
        rx.cond(
            PRState.is_reviewing_selected_file,
            rx.box(
                rx.vstack(
                    rx.spinner(size="3"),
                    rx.text("Analyzing code...", color="gray", size="2"),
                    spacing="3",
                    align="center",
                ),
                padding="6",
                text_align="center",
                width="100%",
                flex="1",
            ),
            rx.box(
                rx.vstack(
                    rx.icon("message-square-text", size=32, color=rx.color("gray", 7)),
                    rx.text("No review yet", color="gray", size="3"),
                    rx.text(
                        "Click the button above to get an AI review",
                        color="gray",
                        size="2",
                    ),
                    spacing="2",
                    align="center",
                ),
                padding="6",
                text_align="center",
                width="100%",
                flex="1",
            ),
        ),
    )


def review_error_display() -> rx.Component:
    """Display review errors."""
    return rx.cond(
        PRState.review_error != "",
        rx.callout(
            PRState.review_error,
            icon="triangle-alert",
            color="red",
            size="1",
        ),
        rx.fragment(),
    )


def review_panel() -> rx.Component:
    """Panel for AI code review of the selected file."""
    return rx.cond(
        PRState.selected_file != "",
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("bot", size=18),
                    rx.text("AI Review", weight="bold", size="3"),
                    rx.spacer(),
                    rx.badge(PRState.model, color_scheme="gray", size="1"),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                rx.divider(),
                review_button(),
                review_error_display(),
                review_content(),
                spacing="3",
                align="start",
                width="100%",
                height="100%",
                flex="1",
                min_width="0",
                overflow="hidden",
            ),
            padding="3",
            border_radius="lg",
            border=f"1px solid {rx.color('gray', 5)}",
            width="100%",
            height="100%",
            display="flex",
            flex_direction="column",
            overflow="hidden",
        ),
        rx.fragment(),
    )
