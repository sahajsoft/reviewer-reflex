# PR Reviewer

A local-first GitHub PR review tool built with Reflex. Paste a PR URL, fetch the diff, and get AI-powered code review streamed file-by-file.

## Prerequisites

- [just](https://github.com/casey/just) - command runner
- [uv](https://docs.astral.sh/uv/) - Python package manager

## Setup

```bash
just install
cp .env.example .env  # Add your ANTHROPIC_API_KEY
just dev
```

## Tasks

| Command          | Description                             |
| ---------------- | --------------------------------------- |
| `just dev`       | Start the development server            |
| `just lint`      | Run ruff and pyright checks             |
| `just fix`       | Auto-fix linting issues and format code |
| `just format`    | Format code with ruff                   |
| `just typecheck` | Run pyright type checking               |
| `just install`   | Install dependencies with uv            |

## Features

- Fetch public/private PRs via GitHub API
- Stream AI code reviews using Claude (Opus, Sonnet, Haiku)
- File-by-file navigation with syntax-highlighted diff viewer
- Review individual files or batch review all at once
