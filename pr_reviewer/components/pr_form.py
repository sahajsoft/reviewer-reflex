"""PR form components - input and error display."""

import reflex as rx

from pr_reviewer.state import PRDataState


def pr_url_input() -> rx.Component:
    """Input section for PR URL."""
    return rx.form(
        rx.hstack(
            rx.input(
                placeholder="https://github.com/owner/repo/pull/123",
                value=PRDataState.pr_url,
                on_change=PRDataState.set_pr_url,  # pyright: ignore[reportArgumentType]
                width="400px",
                disabled=PRDataState.is_loading,
                name="pr_url",
            ),
            rx.button(
                rx.cond(
                    PRDataState.is_loading,
                    rx.hstack(
                        rx.spinner(size="1"),
                        rx.text("Loading..."),
                        spacing="2",
                    ),
                    rx.text("Fetch PR"),
                ),
                type="submit",
                disabled=PRDataState.is_loading,
            ),
            spacing="2",
        ),
        on_submit=PRDataState.fetch_pr,  # pyright: ignore[reportArgumentType]
        reset_on_submit=False,
    )


def error_callout() -> rx.Component:
    """Display error messages as a callout."""
    return rx.cond(
        PRDataState.error_message != "",
        rx.callout(
            PRDataState.error_message,
            icon="triangle-alert",
            color="red",
            width="100%",
            max_width="600px",
        ),
        rx.fragment(),
    )
