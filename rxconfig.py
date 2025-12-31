import reflex as rx

config = rx.Config(
    app_name="pr_reviewer",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)