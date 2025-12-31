# PR Reviewer

A local-first GitHub PR review tool built with Reflex. Paste a PR URL, fetch the diff, and get AI-powered code review streamed file-by-file.

## Setup

```bash
uv sync
cp .env.example .env  # Add your OPENAI_API_KEY
reflex run
```

## Features (planned)

- Fetch public PRs via GitHub API (optional token for private repos)
- Stream AI code reviews using OpenAI
- File-by-file navigation with diff viewer
