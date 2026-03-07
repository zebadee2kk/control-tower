"""
cost_tracker.py — Thin REST client for the ai-cost-tracker service.

Behaviour:
  - If AI_COST_TRACKER_URL / AI_COST_TRACKER_TOKEN are not set, the client
    silently operates in "disabled" mode — log calls are no-ops.
  - If the service is set but unreachable (network error, timeout), a warning
    is logged and execution continues.  The caller is never interrupted.
  - All write operations return a ``bool`` indicating success so the caller
    can optionally surface failures without crashing.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"), override=True)

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 5
_DEFAULT_ACCOUNT_ID = "control-tower-prod"


class CostTrackerClient:
    """
    Client for the ai-cost-tracker REST API.

    Instantiate once and re-use across a workflow run.

    Example
    -------
    >>> tracker = CostTrackerClient()
    >>> tracker.log_usage("anthropic", "claude-haiku-4-5-20251001", tokens=320, cost=0.00008)
    True
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        account_id: str = _DEFAULT_ACCOUNT_ID,
    ) -> None:
        self.base_url = (base_url or os.getenv("AI_COST_TRACKER_URL", "")).rstrip("/")
        self.token = token or os.getenv("AI_COST_TRACKER_TOKEN", "")
        self.account_id = account_id

        self._enabled: bool = bool(self.base_url and self.token)
        if not self._enabled:
            logger.info(
                "CostTrackerClient: disabled (AI_COST_TRACKER_URL or "
                "AI_COST_TRACKER_TOKEN not set)"
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _post(self, path: str, payload: dict[str, Any]) -> bool:
        """
        POST to the tracker API.  Returns True on success, False on any error.
        Never raises.
        """
        if not self._enabled:
            return False  # silently skip

        url = f"{self.base_url}{path}"
        try:
            resp = requests.post(
                url, json=payload, headers=self._headers(), timeout=_TIMEOUT_SECONDS
            )
            resp.raise_for_status()
            return True
        except requests.exceptions.ConnectionError:
            logger.warning("CostTracker: cannot reach %s — service may be offline", url)
        except requests.exceptions.Timeout:
            logger.warning("CostTracker: request to %s timed out", url)
        except requests.exceptions.HTTPError as exc:
            logger.warning("CostTracker: HTTP error %s from %s", exc.response.status_code, url)
        except requests.exceptions.RequestException as exc:
            logger.warning("CostTracker: unexpected error posting to %s: %s", url, exc)
        return False

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """
        GET from the tracker API.  Returns parsed JSON on success, None on error.
        Never raises.
        """
        if not self._enabled:
            return None

        url = f"{self.base_url}{path}"
        try:
            resp = requests.get(
                url,
                params=params,
                headers=self._headers(),
                timeout=_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            return resp.json()  # type: ignore[no-any-return]
        except requests.exceptions.RequestException as exc:
            logger.warning("CostTracker: GET %s failed: %s", url, exc)
        return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """True if the client has a URL and token configured."""
        return self._enabled

    def health_check(self) -> bool:
        """
        Ping the tracker's health endpoint.

        Returns True if the service responds with a healthy status.
        """
        if not self._enabled:
            return False
        result = self._get("/api/health")
        return result is not None and result.get("status") == "healthy"

    def log_usage(
        self,
        provider: str,
        model: str,
        tokens: int,
        cost: float,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Log a single AI API call to the cost tracker.

        Parameters
        ----------
        provider:
            Provider name, e.g. ``"anthropic"``, ``"ollama"``.
        model:
            Model identifier, e.g. ``"claude-haiku-4-5-20251001"``.
        tokens:
            Total tokens consumed (input + output).
        cost:
            Estimated cost in USD.
        context:
            Optional arbitrary metadata (issue number, task type, etc.).

        Returns
        -------
        bool
            True if the record was accepted, False otherwise (caller can ignore).
        """
        payload: dict[str, Any] = {
            "account_id": self.account_id,
            "provider": provider,
            "model": model,
            "tokens": tokens,
            "cost_usd": round(cost, 8),
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }
        if context:
            payload["context"] = context

        ok = self._post("/api/usage", payload)
        if ok:
            logger.debug(
                "CostTracker: logged %d tokens / $%.6f (%s/%s)",
                tokens,
                cost,
                provider,
                model,
            )
        return ok

    def get_daily_summary(self, date: str | None = None) -> dict[str, Any] | None:
        """
        Fetch the daily cost summary for this account.

        Parameters
        ----------
        date:
            ISO date string ``"YYYY-MM-DD"`` (defaults to today UTC).

        Returns
        -------
        dict or None
            API response dict, or None if unavailable.
        """
        if not date:
            date = datetime.now(tz=UTC).strftime("%Y-%m-%d")
        return self._get("/api/summary/daily", params={"account_id": self.account_id, "date": date})

    def get_monthly_summary(self, year_month: str | None = None) -> dict[str, Any] | None:
        """
        Fetch the monthly cost summary.

        Parameters
        ----------
        year_month:
            ``"YYYY-MM"`` string (defaults to current UTC month).
        """
        if not year_month:
            year_month = datetime.now(tz=UTC).strftime("%Y-%m")
        return self._get(
            "/api/summary/monthly",
            params={"account_id": self.account_id, "month": year_month},
        )


# ---------------------------------------------------------------------------
# Module-level singleton — import and use directly
# ---------------------------------------------------------------------------

cost_tracker = CostTrackerClient()
