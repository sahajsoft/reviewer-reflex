# PR Reviewer Architecture

A local-first GitHub PR code review tool built with [Reflex](https://reflex.dev).

## Overview

PR Reviewer enables users to:

- Paste a GitHub PR URL and fetch the diff
- Get AI-powered code reviews streamed file-by-file
- Choose between AI providers (Anthropic Claude or OpenAI)
- Navigate and review files interactively

## Project Structure

```
pr_reviewer/
├── __init__.py              # Package exports
├── pr_reviewer.py           # Main app entry point & page layout
├── constants.py             # Enums, providers, model definitions
├── components/              # UI components (8 files)
│   ├── header.py            # Title, Review All button, Settings
│   ├── settings.py          # Settings panel (token, provider, model)
│   ├── pr_form.py           # PR URL input & error display
│   ├── pr_metadata.py       # PR info (title, author, description)
│   ├── file_drawer.py       # File list drawer (left sidebar)
│   ├── diff_view.py         # Diff viewer with syntax highlighting
│   └── review_panel.py      # AI review panel & review button
├── state/                   # State management (3 substates)
│   ├── settings.py          # SettingsState
│   ├── pr_data.py           # PRDataState
│   └── review.py            # ReviewState
└── services/                # Business logic
    ├── github.py            # GitHub API integration
    └── reviewer.py          # AI provider integration
```

## High-Level Architecture

```mermaid
flowchart TB
    subgraph UI["User Interface"]
        Components["Reflex Components"]
    end

    subgraph State["State Layer"]
        SettingsState["SettingsState<br/>(configuration)"]
        PRDataState["PRDataState<br/>(PR data)"]
        ReviewState["ReviewState<br/>(AI reviews)"]
    end

    subgraph Services["Services Layer"]
        GitHub["github.py"]
        Reviewer["reviewer.py"]
    end

    subgraph External["External APIs"]
        GitHubAPI["GitHub API"]
        AnthropicAPI["Anthropic Claude"]
        OpenAIAPI["OpenAI"]
    end

    Components --> SettingsState
    Components --> PRDataState
    Components --> ReviewState

    PRDataState --> GitHub
    ReviewState --> Reviewer

    GitHub --> GitHubAPI
    Reviewer --> AnthropicAPI
    Reviewer --> OpenAIAPI
```

## Data Flow

### Fetching a PR

```mermaid
sequenceDiagram
    participant User
    participant UI as pr_form.py
    participant PRData as PRDataState
    participant GH as github.py
    participant API as GitHub API
    participant Review as ReviewState

    User->>UI: Enter PR URL & click Fetch
    UI->>PRData: fetch_pr()
    PRData->>GH: parse_pr_url()
    GH-->>PRData: (owner, repo, pr_number)
    PRData->>GH: fetch_pr_metadata()
    GH->>API: GET /repos/.../pulls/N
    API-->>GH: PR metadata
    GH-->>PRData: title, description, branches
    PRData->>GH: fetch_pr_files()
    GH->>API: GET /repos/.../pulls/N/files
    API-->>GH: file list with diffs
    GH-->>PRData: files[]
    PRData->>Review: set_files(files)
    PRData->>Review: reset_review_state()
    PRData-->>UI: Update UI with PR data
```

### Reviewing a File

```mermaid
sequenceDiagram
    participant User
    participant UI as review_panel.py
    participant Review as ReviewState
    participant Svc as reviewer.py
    participant AI as AI Provider

    User->>UI: Click "Review This File"
    UI->>Review: review_file()
    Review->>Svc: review_diff(filename, diff)
    Svc->>AI: Stream request
    loop Streaming
        AI-->>Svc: text chunk
        Svc-->>Review: yield chunk
        Review-->>UI: Update review panel
    end
```

## Page Layout

```mermaid
flowchart TB
    subgraph Page["Main Page (100vh)"]
        Header["header()<br/>Title | Review All | Settings | Theme"]
        Settings["settings_panel()<br/>(conditionally shown)"]
        Form["pr_url_input()<br/>URL input + Fetch button"]
        Error["error_callout()"]

        subgraph PRInfo["PR Info (conditional)"]
            Meta["pr_metadata()<br/>Title, author, branches, stats"]
            Desc["pr_description()<br/>(collapsible)"]
        end

        subgraph MainContent["Main Content (conditional)"]
            Drawer["file_drawer()<br/>File list overlay"]
            subgraph SplitView["Side-by-Side (hstack)"]
                Diff["diff_view()<br/>60% width"]
                ReviewPanel["review_panel()<br/>40% width"]
            end
        end
    end

    Header --> Settings
    Settings --> Form
    Form --> Error
    Error --> PRInfo
    PRInfo --> MainContent
```

## Key Design Decisions

### Reflex Substates

The app uses **3 separate Reflex State classes** rather than a single monolithic state:

| State           | Responsibility                               |
| --------------- | -------------------------------------------- |
| `SettingsState` | User configuration (tokens, provider, model) |
| `PRDataState`   | PR fetching, metadata, file selection        |
| `ReviewState`   | AI reviews, streaming, progress tracking     |

This separation provides:

- Clear boundaries between concerns
- Independent state updates
- Easier testing and debugging

### State Synchronization

ReviewState needs access to files and selected file for computed vars. Since `@rx.var` can't use async `get_state()`, files are explicitly synced:

```python
# In PRDataState.fetch_pr()
review_state = await self.get_state(ReviewState)
review_state.set_files(files)
```

### Async Generators for Streaming

State methods that stream data use async generators:

```python
async def review_file(self) -> AsyncGenerator[None, None]:
    async for chunk in review_diff(...):
        self._set_file_review(filename, accumulated)
        yield  # Let UI update
```

## Environment Configuration

```
ANTHROPIC_API_KEY=sk-ant-xxx    # Required for Anthropic
OPENAI_API_KEY=sk-xxx           # Required for OpenAI
GITHUB_TOKEN=ghp_xxx            # Optional (increases rate limit 60→5000/hr)
```

## Related Documentation

- [State Management](./state-management.md) - Deep dive into substates
- [Components](./components.md) - UI component details
- [Services](./services.md) - GitHub and AI integration
