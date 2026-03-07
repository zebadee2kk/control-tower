"""
Shared pytest fixtures for control-tower tests.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import MagicMock

import pytest
from github import Github
from github.Issue import Issue
from github.Label import Label
from github.NamedUser import NamedUser
from github.Repository import Repository

# ---------------------------------------------------------------------------
# Issue fixture helpers
# ---------------------------------------------------------------------------

def _make_label(name: str) -> MagicMock:
    lbl = MagicMock(spec=Label)
    lbl.name = name
    return lbl


def _make_user(login: str) -> MagicMock:
    user = MagicMock(spec=NamedUser)
    user.login = login
    return user


def _make_issue(
    number: int = 1,
    title: str = "Test issue",
    state: str = "open",
    labels: list[str] | None = None,
    body: str = "Issue body",
    days_old: int = 5,
    days_since_update: int = 5,
    is_pr: bool = False,
    assignees: list[str] | None = None,
) -> MagicMock:
    issue = MagicMock(spec=Issue)
    issue.number = number
    issue.title = title
    issue.state = state
    issue.body = body
    issue.html_url = f"https://github.com/owner/repo/issues/{number}"
    issue.labels = [_make_label(lbl) for lbl in (labels or [])]
    issue.assignees = [_make_user(u) for u in (assignees or [])]

    now = datetime.now(tz=UTC)
    issue.created_at = now - timedelta(days=days_old)
    issue.updated_at = now - timedelta(days=days_since_update)

    # pull_request attribute — None means it's a plain issue
    issue.pull_request = MagicMock() if is_pr else None

    return issue


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_issue_dict() -> dict[str, Any]:
    """Plain dict representing a single GitHub issue."""
    now = datetime.now(tz=UTC)
    return {
        "number": 42,
        "title": "Implement feature X",
        "state": "open",
        "labels": ["enhancement", "priority:high"],
        "created_at": (now - timedelta(days=10)).isoformat(),
        "updated_at": (now - timedelta(days=3)).isoformat(),
        "body": "Detailed description of feature X that needs to be implemented.",
        "url": "https://github.com/owner/repo/issues/42",
        "assignees": [],
    }


@pytest.fixture
def stale_issue_dict() -> dict[str, Any]:
    """Issue dict that is 40 days stale."""
    now = datetime.now(tz=UTC)
    return {
        "number": 7,
        "title": "Old unresolved bug",
        "state": "open",
        "labels": ["bug"],
        "created_at": (now - timedelta(days=45)).isoformat(),
        "updated_at": (now - timedelta(days=40)).isoformat(),
        "body": "This bug has been open for a long time.",
        "url": "https://github.com/owner/repo/issues/7",
        "assignees": [],
    }


@pytest.fixture
def mock_github_issue() -> MagicMock:
    """PyGithub Issue mock — 'gate:needs-approval' label, not a PR."""
    return _make_issue(
        number=10,
        title="Needs approval issue",
        labels=["gate:needs-approval", "priority:high"],
        body="Please approve this work.",
    )


@pytest.fixture
def mock_repo(mock_github_issue: MagicMock) -> MagicMock:
    """PyGithub Repository mock pre-loaded with one issue."""
    repo = MagicMock(spec=Repository)
    repo.get_issues.return_value = [mock_github_issue]
    return repo


@pytest.fixture
def mock_github(mock_repo: MagicMock) -> MagicMock:
    """PyGithub Github client mock."""
    client = MagicMock(spec=Github)
    client.get_repo.return_value = mock_repo
    return client
