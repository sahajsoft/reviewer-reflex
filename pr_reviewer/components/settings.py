"""Settings panel component."""

import reflex as rx

from pr_reviewer.state import DEFAULT_MODEL, PRState

AVAILABLE_MODELS = [
    ("claude-opus-4-5", "Claude Opus 4.5"),
    ("claude-sonnet-4-5", "Claude Sonnet 4.5"),
    ("claude-haiku-4-5", "Claude Haiku 4.5"),
]


def settings_panel() -> rx.Component:
    """Collapsible settings panel."""
    return rx.cond(
        PRState.settings_open,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("settings", size=18),
                    rx.text("Settings", weight="bold", size="3"),
                    rx.spacer(),
                    rx.icon_button(
                        rx.icon("x", size=16),
                        variant="ghost",
                        size="1",
                        on_click=PRState.toggle_settings,  # pyright: ignore[reportArgumentType]
                    ),
                    spacing="2",
                    align="center",
                    width="100%",
                ),
                rx.divider(),
                rx.vstack(
                    rx.text("GitHub Token", size="2", weight="medium"),
                    rx.input(
                        placeholder="ghp_xxxx (optional, for private repos)",
                        value=PRState.github_token,
                        on_change=PRState.set_github_token,  # pyright: ignore[reportArgumentType]
                        type="password",
                        width="100%",
                    ),
                    rx.text(
                        "Required for private repos and higher rate limits",
                        size="1",
                        color="gray",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("AI Model", size="2", weight="medium"),
                    rx.select(
                        [model[1] for model in AVAILABLE_MODELS],
                        value=rx.match(
                            PRState.model,
                            *[(model[0], model[1]) for model in AVAILABLE_MODELS],
                            "Claude Sonnet 4.5",  # default
                        ),
                        on_change=lambda v: PRState.set_model(  # pyright: ignore[reportArgumentType, reportCallIssue]
                            rx.match(
                                v,
                                *[(model[1], model[0]) for model in AVAILABLE_MODELS],
                                DEFAULT_MODEL,  # default
                            )
                        ),
                        width="100%",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                spacing="4",
                align="start",
                width="100%",
            ),
            width="100%",
            max_width="600px",
        ),
        rx.fragment(),
    )
