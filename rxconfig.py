import reflex as rx
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    app_name="pr_reviewer",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
