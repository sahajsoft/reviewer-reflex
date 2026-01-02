# PR Reviewer

A local-first GitHub PR review tool built with Reflex. Paste a PR URL, fetch the diff, and get AI-powered code reviews streamed file-by-file.

## Prerequisites

- [just](https://github.com/casey/just) - command runner
- [uv](https://docs.astral.sh/uv/) - Python package manager

## Setup

```bash
just install
cp .env.example .env  # Add your API keys
just dev
```

## Environment Variables

| Variable            | Required | Description                                      |
| ------------------- | -------- | ------------------------------------------------ |
| `ANTHROPIC_API_KEY` | Yes\*    | Claude API key                                   |
| `OPENAI_API_KEY`    | Yes\*    | OpenAI API key                                   |
| `GITHUB_TOKEN`      | No       | GitHub PAT for private repos & higher rate limit |

\* At least one AI provider key is required.

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
- Stream AI code reviews with Anthropic (Claude) or OpenAI (GPT)
- File-by-file navigation with syntax-highlighted diff viewer
- Review individual files or batch review all at once
- In-app settings for API keys, provider, and model selection

## AI Providers

| Provider  | Models                                               |
| --------- | ---------------------------------------------------- |
| Anthropic | Claude Opus 4.5, Claude Sonnet 4.5, Claude Haiku 4.5 |
| OpenAI    | GPT-5.2, GPT-5.1 Codex, GPT-5.1 Codex Mini, GPT-4o   |
