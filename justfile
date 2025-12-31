# Development
dev:
    uv run reflex run

# Linting
lint:
    uv run ruff check .
    uv run pyright

# Fix linting issues
fix:
    uv run ruff check --fix .
    uv run ruff format .

# Format code
format:
    uv run ruff format .

# Type check
typecheck:
    uv run pyright

# Install dependencies
install:
    uv sync
