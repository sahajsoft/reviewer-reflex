"""Settings panel component."""

import reflex as rx

from pr_reviewer.models import AVAILABLE_MODELS, DEFAULT_MODEL
from pr_reviewer.state import PRState


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
                    rx.hstack(
                        rx.text("GitHub Token", size="2", weight="medium"),
                        rx.cond(
                            PRState.has_github_token,
                            rx.badge("Set", color="green", size="1"),
                            rx.badge("Not set", color="gray", size="1"),
                        ),
                        spacing="2",
                        align="center",
                    ),
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
                    rx.accordion.root(
                        rx.accordion.item(
                            header="How to get a GitHub token",
                            content=rx.vstack(
                                rx.ordered_list(
                                    rx.list_item(
                                        rx.text.span("Go to "),
                                        rx.link(
                                            "GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens",
                                            href="https://github.com/settings/tokens?type=beta",
                                            is_external=True,
                                        ),
                                    ),
                                    rx.list_item('Click "Generate new token"'),
                                    rx.list_item(
                                        rx.text.span("Configure: "),
                                        rx.unordered_list(
                                            rx.list_item(
                                                rx.text.span("Name: ", weight="medium"),
                                                "PR Reviewer App",
                                            ),
                                            rx.list_item(
                                                rx.text.span(
                                                    "Repository access: ",
                                                    weight="medium",
                                                ),
                                                "Select repos you want to review",
                                            ),
                                            rx.list_item(
                                                rx.text.span(
                                                    "Permissions: ", weight="medium"
                                                ),
                                                "Contents (Read) and Pull requests (Read)",
                                            ),
                                        ),
                                    ),
                                    rx.list_item('Click "Generate token" and copy it'),
                                    spacing="2",
                                ),
                                rx.callout(
                                    "For classic tokens, use the 'repo' scope instead.",
                                    icon="info",
                                    size="1",
                                ),
                                spacing="3",
                                align="start",
                                width="100%",
                                padding_y="2",
                            ),
                            value="token_help",
                        ),
                        collapsible=True,
                        variant="ghost",
                        width="100%",
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
