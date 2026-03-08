"""portfolio_scanner.py — Phase 3B portfolio integration for control-tower.

Scans the GitHub portfolio (all repos owned by a configured user) and returns
structured health metrics that the Enhanced Decision Desk can embed in its
nightly issue.

This module is self-contained: it uses only PyGithub (already a control-tower
dependency) and stdlib.  It does *not* import from the portfolio-management
repo — that repo's MCP server is the interface for interactive AI clients;
this module is for the automated GitHub Actions workflow.

Design goals:
- Graceful degradation: if the scan fails for any reason, the caller receives
  an empty result and the Decision Desk still posts its normal report.
- No extra dependencies: PyGithub + stdlib only.
- Consistent scoring: health algorithm matches portfolio-management's scorer
  (basic depth — metrics available from the repo listing API without extra calls).

Environment variables:
    GITHUB_TOKEN      Required — also used by the rest of the workflow.
    GITHUB_USERNAME   GitHub username to scan (default: zebadee2kk).
    PORTFOLIO_MAX_REPOS  Max repos to include in one scan (default: 30).
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from github import Github, GithubException

logger = logging.getLogger(__name__)

_DEFAULT_USERNAME = "zebadee2kk"
_DEFAULT_MAX_REPOS = 30

# ---------------------------------------------------------------------------
# Health scoring constants — kept in sync with portfolio-management/src/health_scorer.py
# ---------------------------------------------------------------------------
_ISSUE_PENALTY_PER = 2.0
_ISSUE_PENALTY_MAX = 40.0
_STALE_THRESHOLD_DAYS = 30
_STALE_PENALTY_PER_DAY = 0.5
_STALE_PENALTY_MAX = 30.0
_RECENT_BONUS_DAYS = 7
_RECENT_BONUS = 10.0


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class RepoHealth:
    """Health snapshot for a single repository.

    Attributes:
        name:              Full repo name (``owner/repo``).
        description:       Repo description string.
        open_issues:       Count of open issues.
        days_since_update: Days since the repo was last updated.
        health_score:      0–100 composite health score.
        health_grade:      Letter grade derived from health_score (A–F).
        language:          Primary language or ``None``.
        private:           Whether the repo is private.
        archived:          Whether the repo is archived.
        url:               HTML URL of the repo.
    """

    name: str
    description: str
    open_issues: int
    days_since_update: int
    health_score: float
    health_grade: str
    language: str | None
    private: bool
    archived: bool
    url: str


@dataclass
class PortfolioSummary:
    """Aggregated metrics across the scanned portfolio.

    Attributes:
        total_repos:       Number of repos scanned.
        avg_health_score:  Mean health score across all repos.
        portfolio_grade:   Letter grade for the whole portfolio.
        critical_count:    Repos with health_score < 40.
        healthy_count:     Repos with health_score >= 70.
        total_open_issues: Sum of open_issues across all repos.
        top_repos:         Up to 5 repos sorted by health_score ascending (worst first).
        scan_timestamp:    ISO timestamp of the scan.
        error:             Non-empty if the scan failed entirely.
    """

    total_repos: int = 0
    avg_health_score: float = 0.0
    portfolio_grade: str = "N/A"
    critical_count: int = 0
    healthy_count: int = 0
    total_open_issues: int = 0
    top_repos: list[RepoHealth] = field(default_factory=list)
    scan_timestamp: str = ""
    error: str = ""


# ---------------------------------------------------------------------------
# Health scoring (mirrors portfolio-management/src/health_scorer.py basic depth)
# ---------------------------------------------------------------------------


def _score(open_issues: int, days_since_update: int, is_archived: bool) -> float:
    """Return a 0–100 health score from basic repo metrics.

    Args:
        open_issues:       Count of open issues on the repo.
        days_since_update: Days elapsed since last update.
        is_archived:       Whether the repo is archived.

    Returns:
        Float in [0.0, 100.0].
    """
    if is_archived:
        return 0.0

    score = 100.0
    score -= min(open_issues * _ISSUE_PENALTY_PER, _ISSUE_PENALTY_MAX)

    if days_since_update > _STALE_THRESHOLD_DAYS:
        excess = days_since_update - _STALE_THRESHOLD_DAYS
        score -= min(excess * _STALE_PENALTY_PER_DAY, _STALE_PENALTY_MAX)

    if days_since_update < _RECENT_BONUS_DAYS:
        score += _RECENT_BONUS

    return round(max(0.0, min(100.0, score)), 1)


def _grade(score: float) -> str:
    """Convert a numeric health score to a letter grade.

    Args:
        score: Value in [0, 100].

    Returns:
        One of ``'A'``, ``'B'``, ``'C'``, ``'D'``, ``'F'``.
    """
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _days_since(dt: datetime) -> int:
    """Return the whole number of days between *dt* and now (UTC).

    Args:
        dt: Datetime (aware or naive — naive treated as UTC).

    Returns:
        Non-negative integer.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return max(0, (datetime.now(UTC) - dt).days)


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


class PortfolioScanner:
    """Scans a GitHub user's repositories and computes health metrics.

    Args:
        token:     GitHub PAT.  Defaults to ``GITHUB_TOKEN`` env var.
        username:  GitHub username to scan.  Defaults to ``GITHUB_USERNAME``
                   env var, then ``zebadee2kk``.
        max_repos: Maximum number of repos to include per scan.  Defaults to
                   ``PORTFOLIO_MAX_REPOS`` env var, then 30.
    """

    def __init__(
        self,
        token: str | None = None,
        username: str | None = None,
        max_repos: int | None = None,
    ) -> None:
        resolved_token = token or os.getenv("GITHUB_TOKEN")
        if not resolved_token:
            raise ValueError(
                "GitHub token required: pass token= or set GITHUB_TOKEN env var"
            )
        self._gh = Github(resolved_token)
        self._username: str = (
            username
            or os.getenv("GITHUB_USERNAME")
            or _DEFAULT_USERNAME
        )
        env_max = os.getenv("PORTFOLIO_MAX_REPOS")
        self._max_repos: int = (
            max_repos
            if max_repos is not None
            else (int(env_max) if env_max else _DEFAULT_MAX_REPOS)
        )

    def scan(self, include_private: bool = True) -> list[RepoHealth]:
        """Scan repositories and return per-repo health data.

        Non-fatal errors on individual repos are logged and skipped; the scan
        continues.  If the user cannot be fetched, an empty list is returned.

        Args:
            include_private: Include private repos in the scan.

        Returns:
            List of :class:`RepoHealth` instances, sorted by health_score
            ascending (worst first).
        """
        try:
            user = self._gh.get_user(self._username)
            repos = list(user.get_repos())
        except GithubException as exc:
            logger.error("Portfolio scan failed: could not list repos: %s", exc)
            return []

        if not include_private:
            repos = [r for r in repos if not r.private]

        repos = repos[: self._max_repos]

        results: list[RepoHealth] = []
        for repo in repos:
            try:
                health = self._repo_health(repo)
                results.append(health)
            except Exception as exc:  # noqa: BLE001 — per-repo, keep scanning
                logger.warning("Skipping %s during portfolio scan: %s", repo.full_name, exc)

        results.sort(key=lambda r: r.health_score)
        logger.info(
            "Portfolio scan complete: %d repos scanned for %s",
            len(results),
            self._username,
        )
        return results

    def summarise(self, repos: list[RepoHealth]) -> PortfolioSummary:
        """Derive aggregate statistics from a list of repo health snapshots.

        Args:
            repos: Output of :meth:`scan`.

        Returns:
            A :class:`PortfolioSummary` describing the whole portfolio.
        """
        if not repos:
            return PortfolioSummary(scan_timestamp=datetime.now(UTC).isoformat())

        total = len(repos)
        avg = round(sum(r.health_score for r in repos) / total, 1)
        critical = sum(1 for r in repos if r.health_score < 40)
        healthy = sum(1 for r in repos if r.health_score >= 70)
        total_issues = sum(r.open_issues for r in repos)

        # Worst 5 repos (already sorted ascending by scan())
        top_repos = repos[:5]

        return PortfolioSummary(
            total_repos=total,
            avg_health_score=avg,
            portfolio_grade=_grade(avg),
            critical_count=critical,
            healthy_count=healthy,
            total_open_issues=total_issues,
            top_repos=top_repos,
            scan_timestamp=datetime.now(UTC).isoformat(),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _repo_health(self, repo: Any) -> RepoHealth:
        """Convert a PyGithub Repository object into a :class:`RepoHealth`."""
        days = _days_since(repo.updated_at)
        score = _score(repo.open_issues_count, days, repo.archived)
        return RepoHealth(
            name=repo.full_name,
            description=repo.description or "",
            open_issues=repo.open_issues_count,
            days_since_update=days,
            health_score=score,
            health_grade=_grade(score),
            language=repo.language,
            private=repo.private,
            archived=repo.archived,
            url=repo.html_url,
        )
