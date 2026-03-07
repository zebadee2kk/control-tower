"""
Unit tests for src/decision_desk.py
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from src.decision_desk import DecisionDesk, _issue_to_dict

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_label(name: str) -> MagicMock:
    lbl = MagicMock()
    lbl.name = name
    return lbl


def _make_user(login: str) -> MagicMock:
    user = MagicMock()
    user.login = login
    return user


def _make_gh_issue(
    number: int = 1,
    title: str = "Test",
    labels: list[str] | None = None,
    body: str = "Body",
    updated_days_ago: int = 5,
    is_pr: bool = False,
) -> MagicMock:
    issue = MagicMock()
    issue.number = number
    issue.title = title
    issue.state = "open"
    issue.body = body
    issue.html_url = f"https://github.com/o/r/issues/{number}"
    issue.labels = [_make_label(lbl) for lbl in (labels or [])]
    issue.assignees = []
    now = datetime.now(tz=UTC)
    issue.created_at = now - timedelta(days=10)
    issue.updated_at = now - timedelta(days=updated_days_ago)
    issue.pull_request = MagicMock() if is_pr else None
    return issue


# ---------------------------------------------------------------------------
# _issue_to_dict
# ---------------------------------------------------------------------------

class TestIssueToDict:
    def test_basic_fields(self) -> None:
        gh_issue = _make_gh_issue(number=5, title="My issue", labels=["bug"])
        result = _issue_to_dict(gh_issue)

        assert result["number"] == 5
        assert result["title"] == "My issue"
        assert result["labels"] == ["bug"]
        assert result["state"] == "open"
        assert "created_at" in result
        assert "updated_at" in result
        assert result["url"].endswith("/5")

    def test_none_body_becomes_empty_string(self) -> None:
        gh_issue = _make_gh_issue()
        gh_issue.body = None
        result = _issue_to_dict(gh_issue)
        assert result["body"] == ""

    def test_multiple_labels(self) -> None:
        gh_issue = _make_gh_issue(labels=["bug", "priority:high", "gate:needs-approval"])
        result = _issue_to_dict(gh_issue)
        assert len(result["labels"]) == 3
        assert "priority:high" in result["labels"]


# ---------------------------------------------------------------------------
# DecisionDesk construction
# ---------------------------------------------------------------------------

class TestDecisionDeskInit:
    def test_successful_init(self, mock_github: MagicMock, mock_repo: MagicMock) -> None:
        DecisionDesk(mock_github, "owner/repo")
        mock_github.get_repo.assert_called_once_with("owner/repo")

    def test_raises_on_github_error(self, mock_github: MagicMock) -> None:
        from github import GithubException
        mock_github.get_repo.side_effect = GithubException(404, "Not found")
        with pytest.raises(RuntimeError, match="Cannot access repo"):
            DecisionDesk(mock_github, "owner/missing-repo")


# ---------------------------------------------------------------------------
# get_issues
# ---------------------------------------------------------------------------

class TestGetIssues:
    def _desk(self, issues: list[MagicMock]) -> DecisionDesk:
        mock_gh = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_issues.return_value = issues
        mock_gh.get_repo.return_value = mock_repo
        return DecisionDesk(mock_gh, "owner/repo")

    def test_returns_non_pr_issues(self) -> None:
        issues = [
            _make_gh_issue(number=1, title="Real issue"),
            _make_gh_issue(number=2, title="A pull request", is_pr=True),
        ]
        desk = self._desk(issues)
        result = desk.get_issues()
        assert len(result) == 1
        assert result[0]["number"] == 1

    def test_label_filter_all_match(self) -> None:
        issues = [
            _make_gh_issue(number=1, labels=["priority:high", "enhancement"]),
            _make_gh_issue(number=2, labels=["bug"]),
        ]
        desk = self._desk(issues)
        result = desk.get_issues(labels=["priority:high"])
        assert len(result) == 1
        assert result[0]["number"] == 1

    def test_label_filter_requires_all(self) -> None:
        """Issue must have ALL requested labels to be included."""
        issues = [
            _make_gh_issue(number=1, labels=["priority:high", "gate:needs-approval"]),
            _make_gh_issue(number=2, labels=["priority:high"]),
        ]
        desk = self._desk(issues)
        result = desk.get_issues(labels=["priority:high", "gate:needs-approval"])
        assert len(result) == 1

    def test_search_term_matches_title(self) -> None:
        issues = [
            _make_gh_issue(number=1, title="Fix the login bug"),
            _make_gh_issue(number=2, title="Update README"),
        ]
        desk = self._desk(issues)
        result = desk.get_issues(search_term="login")
        assert len(result) == 1

    def test_search_term_matches_body(self) -> None:
        issues = [
            _make_gh_issue(number=1, title="Misc", body="Contains authentication issue"),
            _make_gh_issue(number=2, title="Other", body="Nothing relevant"),
        ]
        desk = self._desk(issues)
        result = desk.get_issues(search_term="authentication")
        assert len(result) == 1

    def test_search_term_case_insensitive(self) -> None:
        issues = [_make_gh_issue(number=1, title="Fix BUG in Auth")]
        desk = self._desk(issues)
        assert len(desk.get_issues(search_term="bug")) == 1
        assert len(desk.get_issues(search_term="BUG")) == 1
        assert len(desk.get_issues(search_term="Bug")) == 1

    def test_empty_repo_returns_empty_list(self) -> None:
        desk = self._desk([])
        assert desk.get_issues() == []


# ---------------------------------------------------------------------------
# Convenience filter methods
# ---------------------------------------------------------------------------

class TestConvenienceFilters:
    def _desk_with(self, issues: list[MagicMock]) -> DecisionDesk:
        mock_gh = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_issues.return_value = issues
        mock_gh.get_repo.return_value = mock_repo
        return DecisionDesk(mock_gh, "owner/repo")

    def test_get_needs_approval(self) -> None:
        issues = [
            _make_gh_issue(number=1, labels=["gate:needs-approval"]),
            _make_gh_issue(number=2, labels=["bug"]),
        ]
        desk = self._desk_with(issues)
        result = desk.get_needs_approval()
        assert len(result) == 1
        assert result[0]["number"] == 1

    def test_get_blocked(self) -> None:
        issues = [
            _make_gh_issue(number=1, labels=["state:blocked"]),
            _make_gh_issue(number=2, labels=["state:in-progress"]),
        ]
        desk = self._desk_with(issues)
        result = desk.get_blocked()
        assert len(result) == 1

    def test_get_stale_filters_by_days(self) -> None:
        issues = [
            _make_gh_issue(number=1, updated_days_ago=35),   # stale
            _make_gh_issue(number=2, updated_days_ago=5),    # fresh
        ]
        desk = self._desk_with(issues)
        stale = desk.get_stale(days=30)
        assert len(stale) == 1
        assert stale[0]["number"] == 1

    def test_get_high_priority_deduplicates(self) -> None:
        """An issue with both labels must appear only once."""
        issues = [
            _make_gh_issue(number=1, labels=["priority:high", "priority:critical"]),
        ]
        # get_issues is called twice (once for each label), mock must return issue each time
        mock_repo = MagicMock()
        mock_repo.get_issues.return_value = issues
        mock_gh = MagicMock()
        mock_gh.get_repo.return_value = mock_repo
        desk2 = DecisionDesk(mock_gh, "owner/repo")
        result = desk2.get_high_priority()
        # De-duplication means issue appears at most once
        numbers = [i["number"] for i in result]
        assert numbers.count(1) == 1


# ---------------------------------------------------------------------------
# Report building and rendering
# ---------------------------------------------------------------------------

class TestReportBuildAndRender:
    def _desk_with_issues(self) -> DecisionDesk:
        issues = [
            _make_gh_issue(number=1, labels=["gate:needs-approval"]),
            _make_gh_issue(number=2, labels=["state:blocked"]),
            _make_gh_issue(number=3, labels=["priority:high"]),
            _make_gh_issue(number=4, updated_days_ago=35),
        ]
        mock_gh = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_issues.return_value = issues
        mock_gh.get_repo.return_value = mock_repo
        return DecisionDesk(mock_gh, "owner/repo")

    def test_report_has_required_keys(self) -> None:
        desk = self._desk_with_issues()
        report = desk.build_report()
        for key in ("generated_at", "repo", "needs_approval", "blocked",
                    "high_priority", "stale", "summary"):
            assert key in report, f"Missing key: {key}"

    def test_summary_counts_are_ints(self) -> None:
        desk = self._desk_with_issues()
        report = desk.build_report()
        s = report["summary"]
        assert isinstance(s["needs_approval_count"], int)
        assert isinstance(s["blocked_count"], int)
        assert isinstance(s["high_priority_count"], int)
        assert isinstance(s["stale_count"], int)

    def test_render_markdown_contains_date(self) -> None:
        desk = self._desk_with_issues()
        report = desk.build_report()
        md = desk.render_markdown(report)
        today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
        assert today in md

    def test_render_markdown_sections_present(self) -> None:
        desk = self._desk_with_issues()
        report = desk.build_report()
        md = desk.render_markdown(report)
        assert "Needs Approval" in md
        assert "Blocked" in md
        assert "High Priority" in md
        assert "Stale" in md
        assert "Summary" in md

    def test_render_markdown_no_issues_shows_none(self) -> None:
        mock_gh = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_issues.return_value = []
        mock_gh.get_repo.return_value = mock_repo
        desk = DecisionDesk(mock_gh, "owner/repo")
        report = desk.build_report()
        md = desk.render_markdown(report)
        assert "*None*" in md
