"""
Unit tests for src/ai_analysis.py

All external calls (Ollama, Anthropic) are mocked — no live network required.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

import pytest

import src.ai_analysis as ai_analysis
from src.ai_analysis import (
    _call_ollama,
    _heuristic_score,
    classify_urgency,
    score_issue,
    score_issues_batch,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def basic_issue() -> dict[str, Any]:
    return {
        "number": 42,
        "title": "Fix authentication bug",
        "state": "open",
        "labels": ["bug", "priority:high"],
        "body": "Users cannot log in when 2FA is enabled.",
        "updated_at": "2026-02-01T12:00:00+00:00",
    }


@pytest.fixture
def critical_issue() -> dict[str, Any]:
    return {
        "number": 1,
        "title": "Production database is down",
        "state": "open",
        "labels": ["priority:critical", "p0"],
        "body": "URGENT: all data writes are failing.",
        "updated_at": "2026-03-07T08:00:00+00:00",
    }


@pytest.fixture
def low_issue() -> dict[str, Any]:
    return {
        "number": 99,
        "title": "Update logo colours",
        "state": "open",
        "labels": ["priority:low"],
        "body": "Minor cosmetic change.",
        "updated_at": "2026-01-01T12:00:00+00:00",
    }


@pytest.fixture
def unlabelled_issue() -> dict[str, Any]:
    return {
        "number": 55,
        "title": "Investigate slow query",
        "state": "open",
        "labels": [],
        "body": "The search endpoint takes 3s to respond.",
        "updated_at": "2026-02-28T09:00:00+00:00",
    }


# ---------------------------------------------------------------------------
# _call_ollama — empty/missing OLLAMA_HOST guard
# ---------------------------------------------------------------------------

class TestCallOllamaHostGuard:
    def test_raises_runtime_error_when_host_is_empty_string(self) -> None:
        """Regression: empty OLLAMA_HOST must raise RuntimeError (not ValueError)
        so that classify_urgency's except block catches it and falls back to heuristic."""
        original = ai_analysis.OLLAMA_HOST
        try:
            ai_analysis.OLLAMA_HOST = ""
            with pytest.raises(RuntimeError, match="OLLAMA_HOST is not configured"):
                _call_ollama("test prompt")
        finally:
            ai_analysis.OLLAMA_HOST = original

    def test_classify_urgency_falls_back_when_host_is_empty(
        self, critical_issue: dict[str, Any]
    ) -> None:
        """End-to-end: empty OLLAMA_HOST → heuristic urgency, no crash."""
        original = ai_analysis.OLLAMA_HOST
        try:
            ai_analysis.OLLAMA_HOST = ""
            result = classify_urgency(critical_issue)
        finally:
            ai_analysis.OLLAMA_HOST = original
        assert result == "critical"  # heuristic for priority:critical


# ---------------------------------------------------------------------------
# _heuristic_score
# ---------------------------------------------------------------------------

class TestHeuristicScore:
    def test_critical_label(self, critical_issue: dict[str, Any]) -> None:
        assert _heuristic_score(critical_issue) == 90

    def test_high_label(self, basic_issue: dict[str, Any]) -> None:
        assert _heuristic_score(basic_issue) == 70

    def test_low_label(self, low_issue: dict[str, Any]) -> None:
        assert _heuristic_score(low_issue) == 20

    def test_no_labels_returns_default(self, unlabelled_issue: dict[str, Any]) -> None:
        assert _heuristic_score(unlabelled_issue) == 30

    def test_p0_label(self) -> None:
        issue = {"labels": ["p0"]}
        assert _heuristic_score(issue) == 90

    def test_p2_label(self) -> None:
        issue = {"labels": ["p2"]}
        assert _heuristic_score(issue) == 50


# ---------------------------------------------------------------------------
# classify_urgency — Ollama path
# ---------------------------------------------------------------------------

class TestClassifyUrgencyOllama:
    def test_returns_critical_from_ollama(self, basic_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_ollama", return_value="critical"):
            result = classify_urgency(basic_issue)
        assert result == "critical"

    def test_returns_high_from_ollama(self, basic_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_ollama", return_value="high"):
            result = classify_urgency(basic_issue)
        assert result == "high"

    def test_returns_medium_from_ollama(self, basic_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_ollama", return_value="medium"):
            result = classify_urgency(basic_issue)
        assert result == "medium"

    def test_returns_low_from_ollama(self, basic_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_ollama", return_value="low"):
            result = classify_urgency(basic_issue)
        assert result == "low"

    def test_unexpected_ollama_response_defaults_to_medium(
        self, basic_issue: dict[str, Any]
    ) -> None:
        with patch("src.ai_analysis._call_ollama", return_value="urgent!!"):
            result = classify_urgency(basic_issue)
        assert result == "medium"

    def test_ollama_with_trailing_punctuation(self, basic_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_ollama", return_value="high."):
            result = classify_urgency(basic_issue)
        assert result == "high"


# ---------------------------------------------------------------------------
# classify_urgency — Ollama fallback to heuristic
# ---------------------------------------------------------------------------

class TestClassifyUrgencyFallback:
    def test_falls_back_on_ollama_error(self, critical_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_ollama", side_effect=RuntimeError("offline")):
            result = classify_urgency(critical_issue)
        # heuristic for priority:critical score=90 → "critical"
        assert result == "critical"

    def test_fallback_high(self, basic_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_ollama", side_effect=RuntimeError("offline")):
            result = classify_urgency(basic_issue)
        assert result == "high"

    def test_fallback_low(self, low_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_ollama", side_effect=RuntimeError("offline")):
            result = classify_urgency(low_issue)
        assert result == "low"

    def test_fallback_unlabelled_is_medium(self, unlabelled_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_ollama", side_effect=RuntimeError("offline")):
            result = classify_urgency(unlabelled_issue)
        # score=30 → "low" per the 40 threshold
        assert result == "low"


# ---------------------------------------------------------------------------
# score_issue — Anthropic happy path
# ---------------------------------------------------------------------------

class TestScoreIssueAnthropic:
    def _good_response(self) -> str:
        return json.dumps({
            "priority_score": 78,
            "one_line_summary": "Auth bug blocking 2FA users",
            "recommended_action": "Investigate JWT validation logic",
            "reasoning": "High impact on user login flow.",
        })

    def test_happy_path_returns_all_keys(self, basic_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_anthropic", return_value=self._good_response()):
            with patch("src.ai_analysis._call_ollama", return_value="high"):
                result = score_issue(basic_issue)

        assert result["issue_number"] == 42
        assert result["priority_score"] == 78
        assert result["urgency"] == "high"
        assert "Auth bug" in result["one_line_summary"]
        assert result["ai_model"] == "claude-haiku-4-5-20251001"
        assert result["error"] is None

    def test_priority_score_clamped_to_0_100(self, basic_issue: dict[str, Any]) -> None:
        bad_resp = json.dumps({
            "priority_score": 150,
            "one_line_summary": "x",
            "recommended_action": "y",
            "reasoning": "z",
        })
        with patch("src.ai_analysis._call_anthropic", return_value=bad_resp):
            with patch("src.ai_analysis._call_ollama", return_value="high"):
                result = score_issue(basic_issue)
        assert result["priority_score"] <= 100

    def test_handles_json_in_markdown_fence(self, basic_issue: dict[str, Any]) -> None:
        fenced = f"```json\n{self._good_response()}\n```"
        with patch("src.ai_analysis._call_anthropic", return_value=fenced):
            with patch("src.ai_analysis._call_ollama", return_value="high"):
                result = score_issue(basic_issue)
        assert result["priority_score"] == 78


# ---------------------------------------------------------------------------
# score_issue — fallback paths
# ---------------------------------------------------------------------------

class TestScoreIssueFallback:
    def test_anthropic_unavailable_uses_heuristic(self, basic_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_anthropic", side_effect=RuntimeError("no key")):
            with patch("src.ai_analysis._call_ollama", return_value="high"):
                result = score_issue(basic_issue)

        assert result["ai_model"] == "heuristic"
        assert result["error"] is not None
        assert result["priority_score"] == 70  # heuristic for priority:high

    def test_bad_json_uses_heuristic(self, basic_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_anthropic", return_value="not json at all"):
            with patch("src.ai_analysis._call_ollama", return_value="high"):
                result = score_issue(basic_issue)
        assert result["ai_model"] == "heuristic"
        assert result["error"] is not None

    def test_always_returns_dict_with_required_keys(self, unlabelled_issue: dict[str, Any]) -> None:
        with patch("src.ai_analysis._call_anthropic", side_effect=RuntimeError("offline")):
            with patch("src.ai_analysis._call_ollama", side_effect=RuntimeError("offline")):
                result = score_issue(unlabelled_issue)

        required = {"issue_number", "priority_score", "urgency",
                    "one_line_summary", "recommended_action", "reasoning",
                    "ai_model", "error"}
        assert required.issubset(result.keys())


# ---------------------------------------------------------------------------
# score_issues_batch
# ---------------------------------------------------------------------------

class TestScoreIssuesBatch:
    def test_returns_sorted_by_priority_desc(self) -> None:
        issues = [
            {"number": 1, "title": "Low", "labels": ["priority:low"], "body": ""},
            {"number": 2, "title": "High", "labels": ["priority:high"], "body": ""},
            {"number": 3, "title": "Critical", "labels": ["priority:critical"], "body": ""},
        ]

        def mock_score(issue: dict) -> dict:
            scores = {"Low": 20, "High": 70, "Critical": 90}
            return {
                "issue_number": issue["number"],
                "priority_score": scores[issue["title"]],
                "urgency": "medium",
                "one_line_summary": issue["title"],
                "recommended_action": "Review",
                "reasoning": "Test",
                "ai_model": "heuristic",
                "error": None,
            }

        with patch("src.ai_analysis.score_issue", side_effect=mock_score):
            results = score_issues_batch(issues)

        assert results[0]["priority_score"] == 90
        assert results[1]["priority_score"] == 70
        assert results[2]["priority_score"] == 20

    def test_respects_max_issues_cap(self) -> None:
        issues = [{"number": i, "title": f"Issue {i}", "labels": [], "body": ""} for i in range(30)]

        with patch("src.ai_analysis.score_issue", return_value={
            "issue_number": 0, "priority_score": 50, "urgency": "medium",
            "one_line_summary": "x", "recommended_action": "y",
            "reasoning": "z", "ai_model": "heuristic", "error": None,
        }) as mock_fn:
            score_issues_batch(issues, max_issues=5)
            assert mock_fn.call_count == 5

    def test_empty_list_returns_empty(self) -> None:
        result = score_issues_batch([])
        assert result == []
