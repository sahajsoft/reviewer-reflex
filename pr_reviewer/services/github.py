"""GitHub API service for fetching PR data."""

import re
from typing import Optional

import httpx

# Pattern to match GitHub PR URLs
PR_URL_PATTERN = re.compile(
    r"https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/pull/(\d+)"
)


def parse_pr_url(url: str) -> Optional[tuple[str, str, int]]:
    """Parse a GitHub PR URL into (owner, repo, pr_number).

    Args:
        url: GitHub PR URL like https://github.com/owner/repo/pull/123

    Returns:
        Tuple of (owner, repo, pr_number) or None if URL is invalid.
    """
    match = PR_URL_PATTERN.match(url.strip())
    if not match:
        return None
    owner, repo, pr_num = match.groups()
    return owner, repo, int(pr_num)


def _get_headers(token: Optional[str] = None) -> dict:
    """Build request headers with optional auth token.

    Args:
        token: Optional GitHub personal access token.

    Returns:
        Headers dict for GitHub API requests.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PR-Reviewer-App",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def _parse_link_header(link_header: str) -> Optional[str]:
    """Parse Link header to find 'next' URL.

    Args:
        link_header: The Link header value from GitHub API response.

    Returns:
        URL for next page, or None if no next page.
    """
    if not link_header:
        return None

    for part in link_header.split(","):
        section = part.split(";")
        if len(section) < 2:
            continue
        url_part = section[0].strip()
        rel_part = section[1].strip()

        if 'rel="next"' in rel_part:
            # Extract URL from angle brackets
            if url_part.startswith("<") and url_part.endswith(">"):
                return url_part[1:-1]
    return None


async def fetch_pr_metadata(
    owner: str,
    repo: str,
    pr_number: int,
    token: Optional[str] = None,
) -> dict:
    """Fetch PR metadata from GitHub API.

    Args:
        owner: Repository owner.
        repo: Repository name.
        pr_number: Pull request number.
        token: Optional GitHub token for authentication.

    Returns:
        Dict with PR metadata.

    Raises:
        Exception: On API errors with descriptive messages.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = _get_headers(token)

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, timeout=30.0)

        if response.status_code == 404:
            raise Exception(
                f"PR not found: {owner}/{repo}#{pr_number}. "
                "The repository may be private or the PR doesn't exist."
            )

        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining", "unknown")
            raise Exception(
                f"GitHub API rate limit exceeded. "
                f"Remaining requests: {remaining}. "
                "Add a GitHub token in settings to increase your rate limit."
            )

        response.raise_for_status()
        return response.json()


async def fetch_pr_files(
    owner: str,
    repo: str,
    pr_number: int,
    token: Optional[str] = None,
    max_files: int = 100,
) -> dict:
    """Fetch files changed in a PR with pagination support.

    Args:
        owner: Repository owner.
        repo: Repository name.
        pr_number: Pull request number.
        token: Optional GitHub token for authentication.
        max_files: Maximum number of files to fetch.

    Returns:
        Dict with keys:
            - files: List of file dicts from GitHub API
            - total_count: Total number of files fetched
            - truncated: True if max_files limit was reached

    Raises:
        Exception: On API errors with descriptive messages.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    headers = _get_headers(token)
    files: list[dict] = []
    truncated = False

    async with httpx.AsyncClient() as client:
        while url and len(files) < max_files:
            response = await client.get(
                url,
                headers=headers,
                params={"per_page": min(100, max_files - len(files))},
                timeout=30.0,
            )

            if response.status_code == 404:
                raise Exception(
                    f"PR not found: {owner}/{repo}#{pr_number}. "
                    "The repository may be private or the PR doesn't exist."
                )

            if response.status_code == 403:
                remaining = response.headers.get("X-RateLimit-Remaining", "unknown")
                raise Exception(
                    f"GitHub API rate limit exceeded. "
                    f"Remaining requests: {remaining}. "
                    "Add a GitHub token in settings to increase your rate limit."
                )

            response.raise_for_status()
            page_files = response.json()
            files.extend(page_files)

            # Check for next page
            link_header = response.headers.get("Link", "")
            url = _parse_link_header(link_header)

            # Check if we've hit the limit
            if len(files) >= max_files:
                truncated = True
                files = files[:max_files]
                break

    return {
        "files": files,
        "total_count": len(files),
        "truncated": truncated,
    }
