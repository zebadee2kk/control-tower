"""Unit tests for src/integrations/portfolio_scanner.py."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from src.integrations.portfolio_scanner import (
    PortfolioScanner,
    PortfolioSummary,
    RepoHealth,
    _days_since,
    _grade,
    _score,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_repo(
    full_name: str = "zebadee2kk/test-repo",
    open_issues: int = 2,
    days_old: int = 5,
    archived: bool = False,
    private: bool = False,
    language: str = "Python",
    description: str = "A test repo",
    html_url: str = "https://github.com/zebadee2kk/test-repo",
) -> MagicMock:
    repo = MagicMock()
    repo.full_name = full_name
    repo.description = description
    repo.open_issues_count = open_issues
    repo.updated_at = datetime.now(UTC) - timedelta(days=days_old)
    repo.archived = archived
    repo.private = private
    repo.language = language
    repo.html_url = html_url
    return repo


def _make_scanner(mock_github: MagicMock, token: str = "tok") -> PortfolioScanner:  # noqa: S107
    with patch("src.integrations.portfolio_scanner.Github", return_value=mock_github):
        return PortfolioScanner(token=token)


# ---------------------------------------------------------------------------
# _score
# ---------------------------------------------------------------------------


class TestScore:
    def test_archived_is_zero(self):
        assert _score(0, 0, is_archived=True) == 0.0

    def test_no_issues_recent(self):
        # 100 + 10 bonus = 110 → capped at 100
        assert _score(0, 1, is_archived=False) == 100.0

    def test_issues_penalty(self):
        # 100 - (5 * 2) = 90, days=20 no stale, no bonus
        assert _score(5, 20, is_archived=False) == 90.0

    def test_issue_penalty_capped(self):
        # 100 - 40 (max) = 60
        assert _score(100, 20, is_archived=False) == 60.0

    def test_stale_penalty(self):
        # 100 - (50-30)*0.5 = 90
        assert _score(0, 50, is_archived=False) == 90.0

    def test_stale_penalty_capped(self):
        # 100 - 30 (max stale) = 70
        assert _score(0, 200, is_archived=False) == 70.0

    def test_recent_bonus(self):
        # 100 - 10 (5 issues) + 10 (recent) = 100
        assert _score(5, 3, is_archived=False) == 100.0

    def test_score_floor_zero(self):
        assert _score(1000, 1000, is_archived=False) >= 0.0

    def test_score_ceiling_100(self):
        assert _score(0, 0, is_archived=False) <= 100.0

    def test_returns_float(self):
        assert isinstance(_score(1, 1, is_archived=False), float)


# ---------------------------------------------------------------------------
# _grade
# ---------------------------------------------------------------------------


class TestGrade:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (100.0, "A"), (85.0, "A"), (84.9, "B"), (70.0, "B"),
            (69.9, "C"), (55.0, "C"), (54.9, "D"), (40.0, "D"),
            (39.9, "F"), (0.0, "F"),
        ],
    )
    def test_boundaries(self, score, expected):
        assert _grade(score) == expected


# ---------------------------------------------------------------------------
# _days_since
# ---------------------------------------------------------------------------


class TestDaysSince:
    def test_now_is_zero(self):
        assert _days_since(datetime.now(UTC)) == 0

    def test_yesterday_is_one(self):
        assert _days_since(datetime.now(UTC) - timedelta(days=1)) == 1

    def test_naive_datetime_treated_as_utc(self):
        naive = datetime.now().replace(tzinfo=None) - timedelta(days=3)
        assert _days_since(naive) >= 2


# ---------------------------------------------------------------------------
# PortfolioScanner construction
# ---------------------------------------------------------------------------


class TestPortfolioScannerInit:
    def test_raises_without_token(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        with pytest.raises(ValueError, match="GitHub token required"):
            PortfolioScanner(token=None)

    def test_uses_env_token(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "env-tok")
        with patch("src.integrations.portfolio_scanner.Github") as mock_gh:
            PortfolioScanner()
            mock_gh.assert_called_once_with("env-tok")

    def test_default_username(self, monkeypatch):
        monkeypatch.delenv("GITHUB_USERNAME", raising=False)
        with patch("src.integrations.portfolio_scanner.Github"):
            s = PortfolioScanner(token="tok")
        assert s._username == "zebadee2kk"

    def test_env_username(self, monkeypatch):
        monkeypatch.setenv("GITHUB_USERNAME", "richco")
        with patch("src.integrations.portfolio_scanner.Github"):
            s = PortfolioScanner(token="tok")
        assert s._username == "richco"

    def test_explicit_username(self, monkeypatch):
        monkeypatch.delenv("GITHUB_USERNAME", raising=False)
        with patch("src.integrations.portfolio_scanner.Github"):
            s = PortfolioScanner(token="tok", username="custom")
        assert s._username == "custom"

    def test_default_max_repos(self, monkeypatch):
        monkeypatch.delenv("PORTFOLIO_MAX_REPOS", raising=False)
        with patch("src.integrations.portfolio_scanner.Github"):
            s = PortfolioScanner(token="tok")
        assert s._max_repos == 30

    def test_env_max_repos(self, monkeypatch):
        monkeypatch.setenv("PORTFOLIO_MAX_REPOS", "10")
        with patch("src.integrations.portfolio_scanner.Github"):
            s = PortfolioScanner(token="tok")
        assert s._max_repos == 10

    def test_explicit_max_repos(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            s = PortfolioScanner(token="tok", max_repos=5)
        assert s._max_repos == 5


# ---------------------------------------------------------------------------
# PortfolioScanner.scan()
# ---------------------------------------------------------------------------


class TestPortfolioScannerScan:
    def _mock_github_with_repos(self, repos):
        mock_gh = MagicMock()
        mock_user = MagicMock()
        mock_user.get_repos.return_value = repos
        mock_gh.get_user.return_value = mock_user
        return mock_gh

    def test_returns_list(self):
        mock_gh = self._mock_github_with_repos([_make_mock_repo()])
        scanner = _make_scanner(mock_gh)
        result = scanner.scan()
        assert isinstance(result, list)

    def test_returns_repo_health_instances(self):
        mock_gh = self._mock_github_with_repos([_make_mock_repo()])
        scanner = _make_scanner(mock_gh)
        result = scanner.scan()
        assert all(isinstance(r, RepoHealth) for r in result)

    def test_sorted_worst_first(self):
        repos = [
            _make_mock_repo("z/healthy", open_issues=0, days_old=1),
            _make_mock_repo("z/sick", open_issues=20, days_old=90),
        ]
        mock_gh = self._mock_github_with_repos(repos)
        scanner = _make_scanner(mock_gh)
        result = scanner.scan()
        assert result[0].health_score <= result[-1].health_score

    def test_filters_private_when_requested(self):
        public = _make_mock_repo("z/public", private=False)
        private = _make_mock_repo("z/private", private=True)
        mock_gh = self._mock_github_with_repos([public, private])
        scanner = _make_scanner(mock_gh)
        result = scanner.scan(include_private=False)
        assert all(not r.private for r in result)

    def test_github_error_returns_empty(self):
        mock_gh = MagicMock()
        mock_gh.get_user.side_effect = GithubException(403, "Forbidden")
        scanner = _make_scanner(mock_gh)
        assert scanner.scan() == []

    def test_per_repo_error_skipped(self):
        bad_repo = MagicMock()
        bad_repo.full_name = "z/bad"
        type(bad_repo).updated_at = property(
            fget=lambda self: (_ for _ in ()).throw(Exception("API fail"))
        )
        good_repo = _make_mock_repo("z/good")
        mock_gh = self._mock_github_with_repos([bad_repo, good_repo])
        scanner = _make_scanner(mock_gh)
        result = scanner.scan()
        # Only the good repo makes it through
        assert len(result) == 1
        assert result[0].name == "z/good"

    def test_respects_max_repos_limit(self):
        repos = [_make_mock_repo(f"z/repo-{i}") for i in range(20)]
        mock_gh = self._mock_github_with_repos(repos)
        with patch("src.integrations.portfolio_scanner.Github", return_value=mock_gh):
            scanner = PortfolioScanner(token="tok", max_repos=5)
        result = scanner.scan()
        assert len(result) <= 5

    def test_archived_repo_scores_zero(self):
        repo = _make_mock_repo(archived=True)
        mock_gh = self._mock_github_with_repos([repo])
        scanner = _make_scanner(mock_gh)
        result = scanner.scan()
        assert result[0].health_score == 0.0
        assert result[0].health_grade == "F"

    def test_repo_health_fields_populated(self):
        repo = _make_mock_repo(
            full_name="z/myrepo",
            open_issues=3,
            days_old=10,
            language="Python",
            description="desc",
            html_url="https://github.com/z/myrepo",
            private=False,
            archived=False,
        )
        mock_gh = self._mock_github_with_repos([repo])
        scanner = _make_scanner(mock_gh)
        result = scanner.scan()
        r = result[0]
        assert r.name == "z/myrepo"
        assert r.open_issues == 3
        assert r.language == "Python"
        assert r.description == "desc"
        assert r.url == "https://github.com/z/myrepo"
        assert not r.private
        assert not r.archived


# ---------------------------------------------------------------------------
# PortfolioScanner.summarise()
# ---------------------------------------------------------------------------


class TestPortfolioScannerSummarise:
    def _make_health(self, score: float, open_issues: int = 0) -> RepoHealth:
        return RepoHealth(
            name=f"z/repo-{int(score)}",
            description="",
            open_issues=open_issues,
            days_since_update=10,
            health_score=score,
            health_grade=_grade(score),
            language=None,
            private=False,
            archived=False,
            url="https://github.com/z/repo",
        )

    def test_empty_list_returns_default_summary(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        summary = scanner.summarise([])
        assert summary.total_repos == 0
        assert summary.portfolio_grade == "N/A"

    def test_total_repos_count(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        repos = [self._make_health(80.0), self._make_health(60.0)]
        summary = scanner.summarise(repos)
        assert summary.total_repos == 2

    def test_avg_health_score(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        repos = [self._make_health(80.0), self._make_health(60.0)]
        summary = scanner.summarise(repos)
        assert summary.avg_health_score == 70.0

    def test_portfolio_grade_derived_from_avg(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        repos = [self._make_health(80.0), self._make_health(60.0)]  # avg=70 → B
        summary = scanner.summarise(repos)
        assert summary.portfolio_grade == "B"

    def test_critical_count(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        repos = [self._make_health(30.0), self._make_health(80.0)]
        summary = scanner.summarise(repos)
        assert summary.critical_count == 1

    def test_healthy_count(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        repos = [self._make_health(75.0), self._make_health(30.0)]
        summary = scanner.summarise(repos)
        assert summary.healthy_count == 1

    def test_total_open_issues(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        repos = [self._make_health(80.0, open_issues=3), self._make_health(60.0, open_issues=7)]
        summary = scanner.summarise(repos)
        assert summary.total_open_issues == 10

    def test_top_repos_max_five(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        repos = [self._make_health(float(s)) for s in range(10, 90, 10)]
        summary = scanner.summarise(repos)
        assert len(summary.top_repos) <= 5

    def test_top_repos_are_worst(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        repos = [self._make_health(90.0), self._make_health(20.0), self._make_health(50.0)]
        summary = scanner.summarise(repos)
        # top_repos should include the worst (20.0)
        scores = [r.health_score for r in summary.top_repos]
        assert 20.0 in scores

    def test_scan_timestamp_is_set(self):
        with patch("src.integrations.portfolio_scanner.Github"):
            scanner = PortfolioScanner(token="tok")
        summary = scanner.summarise([self._make_health(80.0)])
        assert summary.scan_timestamp != ""


# ---------------------------------------------------------------------------
# _render_portfolio_section integration
# ---------------------------------------------------------------------------


class TestRenderPortfolioSection:
    """Test the Markdown renderer in run_enhanced_desk for portfolio data."""

    def _make_summary(self, **kwargs) -> PortfolioSummary:
        defaults = dict(
            total_repos=10,
            avg_health_score=72.0,
            portfolio_grade="B",
            critical_count=1,
            healthy_count=7,
            total_open_issues=23,
            top_repos=[],
            scan_timestamp="2026-03-08T21:10:00+00:00",
            error="",
        )
        defaults.update(kwargs)
        return PortfolioSummary(**defaults)

    def test_empty_on_error(self):
        from src.run_enhanced_desk import _render_portfolio_section
        summary = self._make_summary(error="scan failed")
        assert _render_portfolio_section(summary) == []

    def test_empty_when_no_repos(self):
        from src.run_enhanced_desk import _render_portfolio_section
        summary = self._make_summary(total_repos=0)
        assert _render_portfolio_section(summary) == []

    def test_contains_repo_count(self):
        from src.run_enhanced_desk import _render_portfolio_section
        summary = self._make_summary()
        md = "\n".join(_render_portfolio_section(summary))
        assert "10" in md

    def test_contains_grade(self):
        from src.run_enhanced_desk import _render_portfolio_section
        summary = self._make_summary(portfolio_grade="B")
        md = "\n".join(_render_portfolio_section(summary))
        assert "B" in md

    def test_contains_portfolio_health_header(self):
        from src.run_enhanced_desk import _render_portfolio_section
        summary = self._make_summary()
        md = "\n".join(_render_portfolio_section(summary))
        assert "Portfolio Health" in md

    def test_attention_repos_listed(self):
        from src.run_enhanced_desk import _render_portfolio_section
        repo = RepoHealth(
            name="z/bad-repo",
            description="",
            open_issues=5,
            days_since_update=60,
            health_score=20.0,
            health_grade="F",
            language="Python",
            private=False,
            archived=False,
            url="https://github.com/z/bad-repo",
        )
        summary = self._make_summary(top_repos=[repo])
        md = "\n".join(_render_portfolio_section(summary))
        assert "bad-repo" in md
        assert "20.0" in md
