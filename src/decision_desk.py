"""
decision_desk.py — Enhanced GitHub issue triage for control-tower Phase 3A.

Fetches, filters, and groups issues from the control-tower repo.
Designed to be invoked from a GitHub Actions workflow or locally.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import UTC, datetime, timedelta
from typing import Any

from dotenv import load_dotenv
from github import Github, GithubException
from github.Issue import Issue

load_dotenv(os.path.expanduser("~/.env"), override=True)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _issue_to_dict(issue: Issue) -> dict[str, Any]:
    """Convert a PyGithub Issue object to a plain dict."""
    return {
        "number": issue.number,
        "title": issue.title,
        "state": issue.state,
        "labels": [label.name for label in issue.labels],
        "created_at": issue.created_at.isoformat(),
        "updated_at": issue.updated_at.isoformat(),
        "body": issue.body or "",
        "url": issue.html_url,
        "assignees": [a.login for a in issue.assignees],
    }


# ---------------------------------------------------------------------------
# DecisionDesk
# ---------------------------------------------------------------------------

class DecisionDesk:
    """
    Fetches and filters GitHub issues for the Decision Desk report.

    Parameters
    ----------
    github_client:
        Authenticated PyGithub ``Github`` instance.
    repo_name:
        Full repo name, e.g. ``"zebadee2kk/control-tower"``.
    """

    def __init__(self, github_client: Github, repo_name: str) -> None:
        self.github = github_client
        self._repo_name = repo_name
        try:
            self.repo = github_client.get_repo(repo_name)
        except GithubException as exc:
            raise RuntimeError(f"Cannot access repo '{repo_name}': {exc}") from exc

    # ------------------------------------------------------------------
    # Core fetch
    # ------------------------------------------------------------------

    def get_issues(
        self,
        state: str = "open",
        labels: list[str] | None = None,
        since: datetime | None = None,
        search_term: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Return a list of issue dicts, optionally filtered.

        Parameters
        ----------
        state:
            ``"open"``, ``"closed"``, or ``"all"``.
        labels:
            If provided, only issues carrying **all** of these labels are
            returned.
        since:
            Only issues updated at or after this timestamp.
        search_term:
            Case-insensitive regex matched against title and body.
        """
        kwargs: dict[str, Any] = {"state": state}
        if since:
            kwargs["since"] = since

        raw_issues = self.repo.get_issues(**kwargs)

        results: list[dict[str, Any]] = []
        for issue in raw_issues:
            # Skip pull requests (GitHub API returns PRs as issues)
            if issue.pull_request:
                continue

            issue_dict = _issue_to_dict(issue)

            # Label filter — issue must carry every requested label
            if labels:
                issue_labels = set(issue_dict["labels"])
                if not all(lbl in issue_labels for lbl in labels):
                    continue

            # Free-text search across title + body
            if search_term:
                pattern = re.compile(search_term, re.IGNORECASE)
                if not pattern.search(issue_dict["title"]) and not pattern.search(
                    issue_dict["body"]
                ):
                    continue

            results.append(issue_dict)

        return results

    # ------------------------------------------------------------------
    # Convenience filters
    # ------------------------------------------------------------------

    def get_needs_approval(self) -> list[dict[str, Any]]:
        """Issues carrying the ``gate:needs-approval`` label."""
        return self.get_issues(labels=["gate:needs-approval"])

    def get_blocked(self) -> list[dict[str, Any]]:
        """Issues carrying the ``state:blocked`` label."""
        return self.get_issues(labels=["state:blocked"])

    def get_high_priority(self) -> list[dict[str, Any]]:
        """Issues with a priority:high or priority:critical label."""
        high = self.get_issues(labels=["priority:high"])
        critical = self.get_issues(labels=["priority:critical"])
        # De-duplicate by issue number
        seen: set[int] = set()
        combined: list[dict[str, Any]] = []
        for issue in high + critical:
            if issue["number"] not in seen:
                seen.add(issue["number"])
                combined.append(issue)
        return sorted(combined, key=lambda i: i["number"])

    def get_stale(self, days: int = 30) -> list[dict[str, Any]]:
        """
        Issues not updated in ``days`` days.

        Parameters
        ----------
        days:
            Staleness threshold (default 30).
        """
        cutoff = datetime.now(tz=UTC) - timedelta(days=days)
        all_issues = self.get_issues()
        return [
            issue
            for issue in all_issues
            if datetime.fromisoformat(issue["updated_at"]) < cutoff
        ]

    def get_by_search(self, term: str) -> list[dict[str, Any]]:
        """Full-text search across title and body."""
        return self.get_issues(search_term=term)

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def build_report(self) -> dict[str, Any]:
        """
        Assemble a structured Decision Desk snapshot.

        Returns a dict with keys:
        - ``generated_at``  — ISO timestamp
        - ``repo``          — repo full name
        - ``needs_approval`` — list of issue dicts
        - ``blocked``       — list of issue dicts
        - ``high_priority`` — list of issue dicts
        - ``stale``         — list of issue dicts (30-day threshold)
        - ``summary``       — counts dict
        """
        logger.info("Building Decision Desk report for %s", self._repo_name)

        needs_approval = self.get_needs_approval()
        blocked = self.get_blocked()
        high_priority = self.get_high_priority()
        stale = self.get_stale()

        report: dict[str, Any] = {
            "generated_at": datetime.now(tz=UTC).isoformat(),
            "repo": self._repo_name,
            "needs_approval": needs_approval,
            "blocked": blocked,
            "high_priority": high_priority,
            "stale": stale,
            "summary": {
                "needs_approval_count": len(needs_approval),
                "blocked_count": len(blocked),
                "high_priority_count": len(high_priority),
                "stale_count": len(stale),
            },
        }

        logger.info(
            "Report built: %d approval, %d blocked, %d high-pri, %d stale",
            len(needs_approval),
            len(blocked),
            len(high_priority),
            len(stale),
        )
        return report

    def render_markdown(self, report: dict[str, Any]) -> str:
        """
        Render a Decision Desk report dict as a Markdown string suitable
        for posting as a GitHub issue body.
        """
        today = report["generated_at"][:10]
        lines: list[str] = [
            f"## 🗂️ Decision Desk — {today}",
            f"*Generated at {report['generated_at']}*",
            "",
        ]

        def _section(title: str, issues: list[dict[str, Any]]) -> list[str]:
            block = [f"### {title}", ""]
            if not issues:
                block.append("*None*")
            else:
                for iss in issues:
                    label_str = (
                        f" `{'` `'.join(iss['labels'])}`" if iss["labels"] else ""
                    )
                    block.append(f"- #{iss['number']}: **{iss['title']}**{label_str}")
            block.append("")
            return block

        lines += _section("🔔 Needs Approval", report["needs_approval"])
        lines += _section("🚧 Blocked", report["blocked"])
        lines += _section("🔴 High Priority", report["high_priority"])
        lines += _section("🕰️ Stale (30+ days)", report["stale"])

        s = report["summary"]
        lines += [
            "---",
            "**Summary**: "
            f"{s['needs_approval_count']} approval | "
            f"{s['blocked_count']} blocked | "
            f"{s['high_priority_count']} high-pri | "
            f"{s['stale_count']} stale",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import json

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY", "zebadee2kk/control-tower")

    if not token:
        raise SystemExit("GITHUB_TOKEN not set")

    desk = DecisionDesk(Github(token), repo)
    report = desk.build_report()

    print(desk.render_markdown(report))
    logger.info("Full report JSON:\n%s", json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
