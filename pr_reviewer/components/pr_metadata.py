"""PR metadata display components."""

import reflex as rx

from pr_reviewer.components.file_drawer import file_drawer_trigger
from pr_reviewer.state import PRDataState


def pr_description() -> rx.Component:
    """Collapsible PR description section."""
    return rx.cond(
        PRDataState.has_pr_description,
        rx.box(
            rx.hstack(
                rx.icon_button(
                    rx.cond(
                        PRDataState.description_expanded,
                        rx.icon("chevron-down", size=16),
                        rx.icon("chevron-right", size=16),
                    ),
                    variant="ghost",
                    size="1",
                    on_click=PRDataState.toggle_description,  # pyright: ignore[reportArgumentType]
                ),
                rx.text("Description", size="2", weight="medium", color="gray"),
                spacing="1",
                align="center",
                cursor="pointer",
                on_click=PRDataState.toggle_description,  # pyright: ignore[reportArgumentType]
            ),
            rx.cond(
                PRDataState.description_expanded,
                rx.box(
                    rx.markdown(PRDataState.pr_description, size="2"),
                    padding_left="6",
                    padding_top="2",
                ),
                rx.fragment(),
            ),
            width="100%",
        ),
        rx.fragment(),
    )


def truncation_warning() -> rx.Component:
    """Warning displayed when PR has more files than can be shown."""
    return rx.cond(
        PRDataState.files_truncated,
        rx.callout(
            "This PR has more than 100 files. Only the first 100 are shown.",
            icon="triangle-alert",
            color="orange",
        ),
        rx.fragment(),
    )


def pr_metadata() -> rx.Component:
    """Display PR metadata when loaded."""

    return rx.cond(
        PRDataState.has_pr_loaded,
        rx.card(
            rx.vstack(
                truncation_warning(),
                rx.heading(PRDataState.pr_title, size="5"),
                rx.hstack(
                    rx.badge(PRDataState.pr_author, color="blue"),
                    rx.text("•", color="gray"),
                    rx.text(
                        PRDataState.pr_base_branch + " ← " + PRDataState.pr_head_branch,
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
                        rx.text(PRDataState.total_additions, color="green"),
                        spacing="1",
                    ),
                    rx.hstack(
                        rx.text("-", color="red", weight="bold"),
                        rx.text(PRDataState.total_deletions, color="red"),
                        spacing="1",
                    ),
                    rx.text("•", color="gray"),
                    rx.text(
                        PRDataState.file_count.to_string() + " files changed",  # pyright: ignore[reportAttributeAccessIssue]
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
