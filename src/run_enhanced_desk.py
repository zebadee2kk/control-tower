"""
run_enhanced_desk.py — GitHub Actions entry point for the Enhanced Decision Desk.

Workflow:
  1. Fetch all open issues from the repo
  2. Run AI scoring on issues needing attention (approval + blocked + high-priority)
  3. Render an enhanced Markdown report combining triage sections and AI scores
  4. Close the previous Enhanced Decision Desk issue, create a new one
  5. Log token usage to ai-cost-tracker (if configured)

Environment variables (set as GitHub Actions secrets / env):
  GITHUB_TOKEN            — required, write access to the repo
  GITHUB_REPOSITORY       — set automatically by Actions (owner/repo)
  ANTHROPIC_API_KEY       — for claude-haiku scoring (falls back to heuristic)
  OLLAMA_HOST             — for local model urgency classification
  AI_COST_TRACKER_URL     — optional, for cost logging
  AI_COST_TRACKER_TOKEN   — optional, for cost logging
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from github import Github

load_dotenv(os.path.expanduser("~/.env"), override=True)

# Local imports — path is set by the workflow's PYTHONPATH
from src.ai_analysis import score_issues_batch  # noqa: E402
from src.decision_desk import DecisionDesk  # noqa: E402
from src.integrations.cost_tracker import CostTrackerClient  # noqa: E402
from src.integrations.portfolio_scanner import (  # noqa: E402
    PortfolioScanner,
    PortfolioSummary,
)
from src.integrations.projects_sync import (  # noqa: E402
    REPO_TO_TRACK,
    ProjectsSync,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# How many issues to score with AI (caps cost; remainder still appears in report)
_AI_SCORE_LIMIT = 15


# ---------------------------------------------------------------------------
# Helper: Extract PAT from git-credentials
# ---------------------------------------------------------------------------

def _get_derek_pat() -> str | None:
    """Extract derek-ai-dev PAT from ~/.git-credentials.

    Returns the PAT string if found, None otherwise.
    """
    try:
        creds_path = Path.home() / ".git-credentials"
        if not creds_path.exists():
            return None

        with open(creds_path, encoding="utf-8") as f:
            for line in f:
                if "derek-ai-dev" in line:
                    # Format: https://derek-ai-dev:TOKEN@github.com
                    parts = line.split(":")
                    if len(parts) >= 3:
                        token = parts[2].split("@")[0]
                        return token.strip()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read git-credentials: %s", exc)

    return None


# ---------------------------------------------------------------------------
# Enhanced Markdown renderer
# ---------------------------------------------------------------------------

def _render_portfolio_section(summary: PortfolioSummary) -> list[str]:
    """Render the portfolio health summary as Markdown lines.

    Returns an empty list if the scan failed or produced no repos.
    """
    if summary.error or summary.total_repos == 0:
        return []

    grade_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "F": "🔴"}.get(
        summary.portfolio_grade, "⚪"
    )

    lines = [
        "## 📊 Portfolio Health",
        "",
        "| Repos | Avg Score | Grade | Healthy | Critical | Open Issues |",
        "|-------|-----------|-------|---------|----------|-------------|",
        (
            f"| {summary.total_repos} "
            f"| {summary.avg_health_score} "
            f"| {grade_emoji} **{summary.portfolio_grade}** "
            f"| {summary.healthy_count} "
            f"| {summary.critical_count} "
            f"| {summary.total_open_issues} |"
        ),
        "",
    ]

    if summary.top_repos:
        lines += ["**⚠️ Repos needing attention** *(lowest health scores)*", ""]
        for repo in summary.top_repos:
            grade_e = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "F": "🔴"}.get(
                repo.health_grade, "⚪"
            )
            archived_tag = " `archived`" if repo.archived else ""
            private_tag = " `private`" if repo.private else ""
            lines.append(
                f"- [{repo.name}]({repo.url}){archived_tag}{private_tag} — "
                f"**{repo.health_score}** {grade_e} {repo.health_grade} "
                f"({repo.open_issues} issues, {repo.days_since_update}d stale)"
            )
        lines.append("")

    lines += [
        f"*Scanned {summary.total_repos} repos at {summary.scan_timestamp[:16]} UTC*",
        "",
        "---",
        "",
    ]
    return lines


def _render_ai_section(scored: list[dict[str, Any]]) -> list[str]:
    """Render the AI scoring table as Markdown."""
    if not scored:
        return []

    lines = [
        "### 🤖 AI Priority Scoring",
        "",
        "| # | Score | Urgency | Summary | Action |",
        "|---|-------|---------|---------|--------|",
    ]
    for s in scored:
        urgency_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(
            s["urgency"], "⚪"
        )
        num = s["issue_number"]
        score = s["priority_score"]
        urgency = f"{urgency_emoji} {s['urgency']}"
        summary = s["one_line_summary"][:60]
        action = s["recommended_action"][:60]
        model_note = "" if s["ai_model"] != "heuristic" else " ⚠️"
        lines.append(f"| #{num}{model_note} | **{score}** | {urgency} | {summary} | {action} |")

    lines.append("")
    lines.append(
        "_⚠️ = heuristic score (AI unavailable for this issue). "
        "Scores are 0-100; higher = more urgent._"
    )
    lines.append("")
    return lines


def render_enhanced_report(
    report: dict[str, Any],
    desk: DecisionDesk,
    scored: list[dict[str, Any]],
    portfolio: PortfolioSummary | None = None,
) -> str:
    """Combine portfolio summary, standard Decision Desk, and AI scoring table.

    Args:
        report:    Structured report dict from :meth:`DecisionDesk.build_report`.
        desk:      :class:`DecisionDesk` instance (for Markdown rendering).
        scored:    AI-scored issue dicts from :func:`score_issues_batch`.
        portfolio: Optional portfolio health summary; omitted if ``None``.

    Returns:
        Full Markdown string ready to post as a GitHub issue body.
    """
    sections: list[str] = []

    # Portfolio section (prepended — most strategic view first)
    if portfolio is not None:
        portfolio_lines = _render_portfolio_section(portfolio)
        if portfolio_lines:
            sections.append("\n".join(portfolio_lines))

    # Standard Decision Desk triage
    sections.append(desk.render_markdown(report))

    # AI scoring table
    ai_lines = _render_ai_section(scored)
    if ai_lines:
        sections.append("\n".join(["", "---", ""] + ai_lines))

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY", "zebadee2kk/control-tower")

    if not token:
        logger.error("GITHUB_TOKEN not set — cannot proceed")
        sys.exit(1)

    logger.info("Starting Enhanced Decision Desk for %s", repo_name)

    # --- Portfolio scan (Phase 3B) ---
    portfolio: PortfolioSummary | None = None
    try:
        scanner = PortfolioScanner(token=token)
        repos = scanner.scan()
        portfolio = scanner.summarise(repos)
        logger.info(
            "Portfolio scan: %d repos, avg score %.1f (%s)",
            portfolio.total_repos,
            portfolio.avg_health_score,
            portfolio.portfolio_grade,
        )
    except Exception as exc:  # noqa: BLE001 — portfolio is bonus; never block the main report
        logger.warning("Portfolio scan skipped: %s", exc)

    # --- Build report ---
    desk = DecisionDesk(Github(token), repo_name)
    report = desk.build_report()

    summary = report["summary"]
    logger.info(
        "Report: %d approval, %d blocked, %d high-pri, %d stale",
        summary["needs_approval_count"],
        summary["blocked_count"],
        summary["high_priority_count"],
        summary["stale_count"],
    )

    # --- AI scoring on the issues most needing attention ---
    # Score needs-approval + blocked + high-priority (de-duplicated)
    to_score: list[dict[str, Any]] = []
    seen: set[int] = set()
    for issue in (
        report["needs_approval"] + report["blocked"] + report["high_priority"]
    ):
        if issue["number"] not in seen:
            seen.add(issue["number"])
            to_score.append(issue)

    if to_score:
        logger.info("Running AI scoring on %d issues (cap %d)", len(to_score), _AI_SCORE_LIMIT)
        scored = score_issues_batch(to_score, max_issues=_AI_SCORE_LIMIT)
    else:
        logger.info("No issues to score")
        scored = []

    # --- Render enhanced report ---
    body = render_enhanced_report(report, desk, scored, portfolio=portfolio)

    # --- Post to GitHub ---
    new_issue = desk.post_report(body)
    logger.info("Enhanced Decision Desk posted: %s", new_issue.html_url)

    # --- Sync to GitHub Projects v2 (Phase 3C) ---
    # This must not block the main report, so wrap in try/except
    try:
        pat = _get_derek_pat()
        if pat:
            sync = ProjectsSync(pat)

            # Extract repo name (e.g., "zebadee2kk/control-tower" → "control-tower")
            repo_short_name = repo_name.split("/")[-1]
            track = REPO_TO_TRACK.get(repo_short_name, "other")

            # Collect all issues we saw during the run
            all_issues_seen: set[str] = set()
            for issue_list in [
                report["needs_approval"],
                report["blocked"],
                report["high_priority"],
                report["stale"],
            ]:
                for issue in issue_list:
                    all_issues_seen.add(issue["node_id"])

            # 1. Sync decision-related issues (needs approval + awaiting decision)
            decision_issues = report["needs_approval"]
            for issue in decision_issues:
                try:
                    sync.add_issue_to_decisions(issue["node_id"], source="Decision Desk")
                    logger.debug(
                        "Synced decision issue #%d (%s)",
                        issue["number"],
                        issue["node_id"],
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to sync decision issue #%d: %s", issue["number"], exc)

            # 2. Sync blocked issues (with Source=Blocked Issue)
            blocked_issues = report["blocked"]
            for issue in blocked_issues:
                try:
                    sync.add_issue_to_decisions(issue["node_id"], source="Blocked Issue")
                    logger.debug(
                        "Synced blocked issue #%d (%s)",
                        issue["number"],
                        issue["node_id"],
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to sync blocked issue #%d: %s", issue["number"], exc)

            # 3. Sync all issues seen in run to Ecosystem Development with Track
            for node_id in all_issues_seen:
                try:
                    item_id = sync.add_issue_to_ecosystem(node_id)
                    if item_id:
                        sync.set_ecosystem_track(item_id, track)
                        logger.debug("Synced ecosystem issue %s with track %s", node_id, track)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to sync ecosystem issue %s: %s", node_id, exc)

            logger.info(
                "Projects sync complete: %d decision, %d blocked, %d ecosystem issues",
                len(decision_issues),
                len(blocked_issues),
                len(all_issues_seen),
            )
        else:
            logger.warning("Could not find derek-ai-dev PAT — skipping Projects sync")
    except Exception as exc:  # noqa: BLE001 — sync must never block the main report
        logger.warning("Projects sync failed (non-blocking): %s", exc)

    # --- Log costs (optional, graceful degradation) ---
    tracker = CostTrackerClient()
    if tracker.enabled and scored:
        # Estimate: each scored issue used ~400 tokens via claude-haiku + ~50 via Ollama
        ai_issues = [s for s in scored if s["ai_model"] != "heuristic"]
        ollama_issues = [s for s in scored if s["ai_model"] == "heuristic"]

        if ai_issues:
            tokens = len(ai_issues) * 400
            cost = tokens * 0.00000025  # claude-haiku input ~$0.25 / 1M tokens
            tracker.log_usage(
                provider="anthropic",
                model="claude-haiku-4-5-20251001",
                tokens=tokens,
                cost=cost,
                context={"workflow": "enhanced-decision-desk", "issues_scored": len(ai_issues)},
            )

        if ollama_issues:
            tracker.log_usage(
                provider="ollama",
                model="qwen2.5-coder:1.5b",
                tokens=len(ollama_issues) * 50,
                cost=0.0,
                context={"workflow": "enhanced-decision-desk", "issues_scored": len(ollama_issues)},
            )


if __name__ == "__main__":
    main()
