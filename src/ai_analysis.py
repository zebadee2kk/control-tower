"""
ai_analysis.py — AI-powered issue scoring for control-tower Phase 3A.

Model routing (Phase 3A hardcoded — zebra-ecosystem bypassed for MVP):
  - Simple classification (urgency bucket) → Ollama qwen2.5-coder:1.5b (local, free)
  - Complex scoring (priority 0-100 + recommendations) → Anthropic claude-haiku-4-5

Graceful degradation: if Ollama is unreachable, falls back to Anthropic for all
tasks.  If Anthropic is also unavailable, returns a heuristic-only result with a
clear warning so the caller can still produce a useful report.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.request
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"), override=True)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://192.168.120.211:11434")
OLLAMA_MODEL: str = "qwen2.5-coder:1.5b"
ANTHROPIC_MODEL: str = "claude-haiku-4-5-20251001"

# Simple classification prompt — intentionally short so it runs fast on a 1.5b model
_CLASSIFY_PROMPT = """\
You are a GitHub issue triage assistant.

Classify the urgency of the following issue into ONE of these buckets:
  critical | high | medium | low

Reply with ONLY the single word (no punctuation, no explanation).

Title: {title}
Labels: {labels}
Body (first 300 chars): {body}
"""

# Full scoring prompt — richer reasoning, sent to Anthropic
_SCORE_PROMPT = """\
You are a senior engineering project manager reviewing a GitHub issue.

Analyse the issue and respond in valid JSON with exactly these keys:
  "priority_score"     : integer 0-100 (100 = drop everything, 0 = ignore)
  "one_line_summary"   : string, max 15 words
  "recommended_action" : string, one concrete next step for the developer
  "reasoning"          : string, 1-2 sentences explaining the score

Issue:
  Number: {number}
  Title:  {title}
  Labels: {labels}
  Body:   {body}
"""


# ---------------------------------------------------------------------------
# Low-level model calls
# ---------------------------------------------------------------------------

def _call_ollama(prompt: str, model: str = OLLAMA_MODEL, timeout: int = 30) -> str:
    """
    Call the local Ollama API (non-streaming).

    Returns the text content of the response, or raises ``RuntimeError``
    if the request fails or ``OLLAMA_HOST`` is not configured.
    """
    if not OLLAMA_HOST:
        raise RuntimeError("OLLAMA_HOST is not configured — skipping Ollama call")

    payload = json.dumps(
        {"model": model, "prompt": prompt, "stream": False}
    ).encode()

    req = urllib.request.Request(  # noqa: S310 — internal LAN endpoint, not user-supplied
        f"{OLLAMA_HOST}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            data = json.loads(resp.read())
            return data.get("response", "").strip()
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Ollama call failed: {exc}") from exc


def _call_anthropic(prompt: str, model: str = ANTHROPIC_MODEL) -> str:
    """
    Call Anthropic claude-haiku via the SDK.

    Returns the text content, or raises ``RuntimeError`` on failure.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)
    try:
        message = client.messages.create(
            model=model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except anthropic.APIError as exc:
        raise RuntimeError(f"Anthropic call failed: {exc}") from exc


# ---------------------------------------------------------------------------
# Heuristic fallback (no AI available)
# ---------------------------------------------------------------------------

_PRIORITY_LABELS: dict[str, int] = {
    "priority:critical": 90,
    "priority:high": 70,
    "priority:medium": 50,
    "priority:low": 20,
}

_URGENCY_LABELS: dict[str, int] = {
    "p0": 90,
    "p1": 70,
    "p2": 50,
    "p3": 20,
}


def _heuristic_score(issue: dict[str, Any]) -> int:
    """Derive a rough priority score from labels alone."""
    labels: list[str] = issue.get("labels", [])
    for label in labels:
        if label in _PRIORITY_LABELS:
            return _PRIORITY_LABELS[label]
        if label in _URGENCY_LABELS:
            return _URGENCY_LABELS[label]
    # Boost stale issues slightly to surface them
    return 30


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_urgency(issue: dict[str, Any]) -> str:
    """
    Classify issue urgency using the local Ollama model.

    Falls back to a heuristic label-based classification if Ollama is
    unavailable.

    Returns one of: ``"critical"``, ``"high"``, ``"medium"``, ``"low"``.
    """
    prompt = _CLASSIFY_PROMPT.format(
        title=issue.get("title", ""),
        labels=", ".join(issue.get("labels", [])) or "none",
        body=(issue.get("body", "") or "")[:300],
    )

    try:
        raw = _call_ollama(prompt)
        # Extract the first word and normalise
        word = raw.split()[0].lower().strip(".,;:") if raw else ""
        if word in {"critical", "high", "medium", "low"}:
            return word
        logger.warning("Ollama returned unexpected urgency '%s', defaulting to medium", raw)
        return "medium"
    except RuntimeError as exc:
        logger.warning("Ollama unavailable (%s), using label heuristic for urgency", exc)
        score = _heuristic_score(issue)
        if score >= 85:
            return "critical"
        if score >= 65:
            return "high"
        if score >= 40:
            return "medium"
        return "low"


def score_issue(issue: dict[str, Any]) -> dict[str, Any]:
    """
    Produce a full AI-powered analysis of a single issue.

    Tries Anthropic claude-haiku first.  If unavailable, falls back to
    heuristic scoring so the caller always gets a usable result.

    Returns a dict with keys:
      - ``issue_number``      : int
      - ``priority_score``    : int 0-100
      - ``urgency``           : str (from classify_urgency)
      - ``one_line_summary``  : str
      - ``recommended_action``: str
      - ``reasoning``         : str
      - ``ai_model``          : str (which model was used, or "heuristic")
      - ``error``             : str | None (populated if fallback was used)
    """
    prompt = _SCORE_PROMPT.format(
        number=issue.get("number", "?"),
        title=issue.get("title", ""),
        labels=", ".join(issue.get("labels", [])) or "none",
        body=(issue.get("body", "") or "")[:800],
    )

    error: str | None = None
    ai_model = ANTHROPIC_MODEL
    priority_score: int = _heuristic_score(issue)
    one_line_summary: str = issue.get("title", "")[:80]
    recommended_action: str = "Review and triage"
    reasoning: str = "Heuristic score — AI unavailable"

    try:
        raw = _call_anthropic(prompt)

        # Parse JSON from response (model may wrap in markdown fences)
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON found in Anthropic response: {raw!r}")

        parsed: dict[str, Any] = json.loads(json_match.group())
        priority_score = int(parsed.get("priority_score", priority_score))
        one_line_summary = str(parsed.get("one_line_summary", one_line_summary))
        recommended_action = str(parsed.get("recommended_action", recommended_action))
        reasoning = str(parsed.get("reasoning", reasoning))

    except RuntimeError as exc:
        error = str(exc)
        logger.warning("Anthropic unavailable (%s), using heuristic score", exc)
        ai_model = "heuristic"
    except (ValueError, json.JSONDecodeError, KeyError) as exc:
        error = f"JSON parse error: {exc}"
        logger.warning("Could not parse Anthropic response: %s", exc)
        ai_model = "heuristic"

    urgency = classify_urgency(issue)

    return {
        "issue_number": issue.get("number"),
        "priority_score": max(0, min(100, priority_score)),
        "urgency": urgency,
        "one_line_summary": one_line_summary,
        "recommended_action": recommended_action,
        "reasoning": reasoning,
        "ai_model": ai_model,
        "error": error,
    }


def score_issues_batch(
    issues: list[dict[str, Any]],
    max_issues: int = 20,
) -> list[dict[str, Any]]:
    """
    Score a list of issues, returning results sorted by priority (desc).

    Parameters
    ----------
    issues:
        List of issue dicts (as returned by ``DecisionDesk.get_issues()``).
    max_issues:
        Cap to avoid runaway API costs (default 20).
    """
    results: list[dict[str, Any]] = []
    for issue in issues[:max_issues]:
        logger.info("Scoring issue #%s: %s", issue.get("number"), issue.get("title"))
        result = score_issue(issue)
        results.append(result)

    return sorted(results, key=lambda r: r["priority_score"], reverse=True)
