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
from typing import Any

from dotenv import load_dotenv
from github import Github

load_dotenv(os.path.expanduser("~/.env"), override=True)

# Local imports — path is set by the workflow's PYTHONPATH
from src.ai_analysis import score_issues_batch  # noqa: E402
from src.decision_desk import DecisionDesk  # noqa: E402
from src.integrations.cost_tracker import CostTrackerClient  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# How many issues to score with AI (caps cost; remainder still appears in report)
_AI_SCORE_LIMIT = 15


# ---------------------------------------------------------------------------
# Enhanced Markdown renderer
# ---------------------------------------------------------------------------

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
) -> str:
    """
    Combine the standard Decision Desk Markdown with the AI scoring table.
    """
    # Start with the standard report body
    base_md = desk.render_markdown(report)

    # Append AI section
    ai_lines = _render_ai_section(scored)
    if ai_lines:
        ai_block = "\n".join(["", "---", ""] + ai_lines)
        return base_md + ai_block

    return base_md


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
    body = render_enhanced_report(report, desk, scored)

    # --- Post to GitHub ---
    new_issue = desk.post_report(body)
    logger.info("Enhanced Decision Desk posted: %s", new_issue.html_url)

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
