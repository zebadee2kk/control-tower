"""
Unit tests for DecisionDesk.post_report() and run_enhanced_desk rendering.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.decision_desk import DecisionDesk
from src.run_enhanced_desk import _render_ai_section, render_enhanced_report

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_desk(open_issues: list | None = None) -> tuple[DecisionDesk, MagicMock]:
    """Return a DecisionDesk wired to a mock repo, plus the mock repo."""
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_repo.get_issues.return_value = open_issues or []
    mock_repo.get_label.side_effect = Exception("not found")
    mock_repo.create_label.return_value = MagicMock()
    mock_gh.get_repo.return_value = mock_repo
    desk = DecisionDesk(mock_gh, "owner/repo")
    return desk, mock_repo


@pytest.fixture
def sample_report() -> dict[str, Any]:
    now = datetime.now(tz=UTC).isoformat()
    return {
        "generated_at": now,
        "repo": "owner/repo",
        "needs_approval": [
            {
                "number": 10,
                "title": "Approve this feature",
                "labels": ["gate:needs-approval"],
                "updated_at": now,
                "body": "",
                "url": "https://github.com/owner/repo/issues/10",
                "assignees": [],
                "state": "open",
                "created_at": now,
            }
        ],
        "blocked": [],
        "high_priority": [],
        "stale": [],
        "summary": {
            "needs_approval_count": 1,
            "blocked_count": 0,
            "high_priority_count": 0,
            "stale_count": 0,
        },
    }


@pytest.fixture
def sample_scored() -> list[dict[str, Any]]:
    return [
        {
            "issue_number": 10,
            "priority_score": 82,
            "urgency": "high",
            "one_line_summary": "Feature approval blocking team velocity",
            "recommended_action": "Review and approve before sprint end",
            "reasoning": "Blocking multiple developers.",
            "ai_model": "claude-haiku-4-5-20251001",
            "error": None,
        }
    ]


# ---------------------------------------------------------------------------
# DecisionDesk.post_report()
# ---------------------------------------------------------------------------

class TestPostReport:
    def test_creates_new_issue(self) -> None:
        desk, mock_repo = _make_desk()
        mock_new = MagicMock()
        mock_new.number = 99
        mock_new.html_url = "https://github.com/owner/repo/issues/99"
        mock_repo.create_issue.return_value = mock_new

        result = desk.post_report("## Report body")

        mock_repo.create_issue.assert_called_once()
        call_kwargs = mock_repo.create_issue.call_args.kwargs
        assert "Enhanced Decision Desk" in call_kwargs["title"]
        assert "## Report body" in call_kwargs["body"]
        assert result == mock_new

    def test_closes_old_enhanced_desk_issues(self) -> None:
        """Any previously open Enhanced Decision Desk issues are closed."""
        old_issue = MagicMock()
        old_issue.number = 55
        old_issue.title = "Enhanced Decision Desk 2026-03-06"
        old_issue.pull_request = None

        desk, mock_repo = _make_desk(open_issues=[old_issue])
        mock_repo.create_issue.return_value = MagicMock(number=56, html_url="...")

        desk.post_report("body")

        old_issue.edit.assert_called_once_with(state="closed", state_reason="completed")

    def test_does_not_close_unrelated_issues(self) -> None:
        """Issues without the enhanced-decision-desk title prefix are left alone."""
        unrelated = MagicMock()
        unrelated.number = 30
        unrelated.title = "Regular bug report"
        unrelated.pull_request = None

        desk, mock_repo = _make_desk(open_issues=[unrelated])
        mock_repo.create_issue.return_value = MagicMock(number=31, html_url="...")

        desk.post_report("body")

        unrelated.edit.assert_not_called()

    def test_does_not_close_pull_requests(self) -> None:
        """PRs returned by the issues API are never edited."""
        pr = MagicMock()
        pr.number = 40
        pr.title = "Enhanced Decision Desk 2026-03-05"
        pr.pull_request = MagicMock()  # marks it as a PR

        desk, mock_repo = _make_desk(open_issues=[pr])
        mock_repo.create_issue.return_value = MagicMock(number=41, html_url="...")

        desk.post_report("body")

        pr.edit.assert_not_called()

    def test_creates_label_if_missing(self) -> None:
        """If the enhanced-decision-desk label doesn't exist, it is created."""
        desk, mock_repo = _make_desk()
        mock_repo.get_label.side_effect = Exception("not found")
        mock_repo.create_issue.return_value = MagicMock(number=1, html_url="...")

        desk.post_report("body")

        mock_repo.create_label.assert_called_once_with(
            name="enhanced-decision-desk",
            color="0075ca",
            description="Auto-generated enhanced decision desk issue",
        )

    def test_skips_label_creation_if_already_exists(self) -> None:
        """If the label already exists, create_label is not called."""
        desk, mock_repo = _make_desk()
        mock_repo.get_label.side_effect = None  # no exception = label exists
        mock_repo.get_label.return_value = MagicMock()
        mock_repo.create_issue.return_value = MagicMock(number=1, html_url="...")

        desk.post_report("body")

        mock_repo.create_label.assert_not_called()

    def test_title_contains_todays_date(self) -> None:
        desk, mock_repo = _make_desk()
        mock_repo.create_issue.return_value = MagicMock(number=1, html_url="...")

        desk.post_report("body")

        today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
        title = mock_repo.create_issue.call_args.kwargs["title"]
        assert today in title


# ---------------------------------------------------------------------------
# _render_ai_section
# ---------------------------------------------------------------------------

class TestRenderAiSection:
    def test_empty_scored_returns_empty(self) -> None:
        assert _render_ai_section([]) == []

    def test_contains_issue_number(self, sample_scored: list[dict]) -> None:
        lines = _render_ai_section(sample_scored)
        combined = "\n".join(lines)
        assert "#10" in combined

    def test_contains_priority_score(self, sample_scored: list[dict]) -> None:
        lines = _render_ai_section(sample_scored)
        combined = "\n".join(lines)
        assert "82" in combined

    def test_urgency_emojis(self, sample_scored: list[dict]) -> None:
        for urgency, emoji in [
            ("critical", "🔴"), ("high", "🟠"), ("medium", "🟡"), ("low", "🟢")
        ]:
            scored = [{**sample_scored[0], "urgency": urgency}]
            lines = _render_ai_section(scored)
            combined = "\n".join(lines)
            assert emoji in combined

    def test_heuristic_fallback_marked(self, sample_scored: list[dict]) -> None:
        heuristic = [{**sample_scored[0], "ai_model": "heuristic"}]
        lines = _render_ai_section(heuristic)
        combined = "\n".join(lines)
        assert "⚠️" in combined

    def test_table_headers_present(self, sample_scored: list[dict]) -> None:
        lines = _render_ai_section(sample_scored)
        combined = "\n".join(lines)
        assert "Score" in combined
        assert "Urgency" in combined
        assert "Summary" in combined
        assert "Action" in combined


# ---------------------------------------------------------------------------
# render_enhanced_report
# ---------------------------------------------------------------------------

class TestRenderEnhancedReport:
    def test_contains_base_report_sections(
        self,
        sample_report: dict,
        sample_scored: list[dict],
    ) -> None:
        desk, _ = _make_desk()
        md = render_enhanced_report(sample_report, desk, sample_scored)
        assert "Needs Approval" in md
        assert "Blocked" in md
        assert "High Priority" in md

    def test_contains_ai_section_when_scored(
        self,
        sample_report: dict,
        sample_scored: list[dict],
    ) -> None:
        desk, _ = _make_desk()
        md = render_enhanced_report(sample_report, desk, sample_scored)
        assert "AI Priority Scoring" in md
        assert "#10" in md

    def test_no_ai_section_when_no_scores(self, sample_report: dict) -> None:
        desk, _ = _make_desk()
        md = render_enhanced_report(sample_report, desk, [])
        assert "AI Priority Scoring" not in md

    def test_is_string(self, sample_report: dict, sample_scored: list[dict]) -> None:
        desk, _ = _make_desk()
        result = render_enhanced_report(sample_report, desk, sample_scored)
        assert isinstance(result, str)
        assert len(result) > 0
