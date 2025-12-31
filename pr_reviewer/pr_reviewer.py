"""PR Reviewer - AI-powered GitHub PR code review."""

import reflex as rx


class State(rx.State):
    """The app state."""

    pr_url: str = ""

    def set_pr_url(self, value: str) -> None:
        """Set the PR URL."""
        self.pr_url = value


def index() -> rx.Component:
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("PR Reviewer", size="9"),
            rx.text("AI-powered GitHub PR code review", size="5", color="gray"),
            rx.hstack(
                rx.input(
                    placeholder="https://github.com/owner/repo/pull/123",
                    value=State.pr_url,
                    on_change=State.set_pr_url,
                    width="400px",
                ),
                rx.button("Fetch PR"),
                spacing="2",
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
    )


app = rx.App()
app.add_page(index)
