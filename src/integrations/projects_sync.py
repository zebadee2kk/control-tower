"""
projects_sync.py — Sync control-tower nightly output to GitHub Projects v2.

Handles GraphQL mutations and queries for:
- Adding issues to projects (addProjectV2ItemById)
- Setting field values (updateProjectV2ItemFieldValue)
- Checking if items already exist (dedup)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import requests

logger = logging.getLogger(__name__)

# Repo name → Track option mapping
REPO_TO_TRACK = {
    "control-tower": "control-tower",
    "derek-ai": "control-tower",
    "portfolio-management": "portfolio",
    "ai-cost-tracker": "portfolio",
    "Project-HeliOS": "hamnet",
    "ProjectLodestar": "hosting-ops",
    "RedGuard-Suite": "security",
    "sentinelforge": "security",
    "ai-powertools": "ai-infra",
    "LocalLLM-Router-Project": "ai-infra",
}


class ProjectsSync:
    """Sync control-tower nightly output to GitHub Projects v2.

    Uses GraphQL mutations to add issues, update field values, and check
    for existing items (dedup).
    """

    # GraphQL API endpoint
    GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

    def __init__(
        self,
        pat: str,
        config_path: Path | None = None,
        dry_run: bool = False,
    ) -> None:
        """Initialize ProjectsSync with PAT and config.

        Args:
            pat: GitHub Personal Access Token (derek-ai-dev, project scope).
            config_path: Path to github_projects.json. If None, looks in
                         ~/Documents/github-repos/derek-ai/config/
            dry_run: If True, log mutations but don't execute them.
        """
        self.pat = pat
        self.dry_run = dry_run
        self.headers = {
            "Authorization": f"bearer {pat}",
            "Content-Type": "application/json",
        }

        # Load config
        if config_path is None:
            config_path = (
                Path.home()
                / "Documents/github-repos/derek-ai/config/github_projects.json"
            )

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, encoding="utf-8") as f:
            self.config = json.load(f)

        logger.info(
            "ProjectsSync initialized with config from %s (dry_run=%s)",
            config_path,
            dry_run,
        )

    # -----------------------------------------------------------------------
    # GraphQL helpers
    # -----------------------------------------------------------------------

    def _gql_query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query/mutation.

        Args:
            query: GraphQL query string.
            variables: Optional variables dict.

        Returns:
            Response data dict (or empty if dry_run).

        Raises:
            RuntimeError: If API returns errors.
        """
        if self.dry_run:
            logger.debug("DRY RUN: Would execute query: %s", query[:100])
            return {}

        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            resp = requests.post(
                self.GRAPHQL_ENDPOINT,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"GraphQL request failed: {exc}") from exc

        data = resp.json()

        if "errors" in data:
            raise RuntimeError(f"GraphQL errors: {data['errors']}")

        return data.get("data", {})

    # -----------------------------------------------------------------------
    # Project-specific helpers
    # -----------------------------------------------------------------------

    def find_item_by_content(self, project_id: str, content_node_id: str) -> str | None:
        """Check if an issue is already in a project.

        Args:
            project_id: Project v2 ID (e.g., "PVT_kwDOD7CZdM4BRKZt").
            content_node_id: Issue node ID.

        Returns:
            Item ID if found, None otherwise.
        """
        query = """
            query FindProjectItem($projectId: ID!, $contentId: ID!) {
              node(id: $projectId) {
                ... on ProjectV2 {
                  items(first: 100, query: "is:not closed") {
                    nodes {
                      id
                      content {
                        ... on Issue {
                          id
                        }
                      }
                    }
                  }
                }
              }
            }
        """
        variables = {"projectId": project_id, "contentId": content_node_id}

        try:
            data = self._gql_query(query, variables)
            node = data.get("node", {})
            items = node.get("items", {}).get("nodes", [])

            for item in items:
                content = item.get("content", {})
                if content.get("id") == content_node_id:
                    logger.debug("Found existing item %s for issue %s", item["id"], content_node_id)
                    return item["id"]

            logger.debug(
                "No existing item found for issue %s in project %s",
                content_node_id,
                project_id,
            )
            return None
        except Exception as exc:  # noqa: BLE001
            logger.error("Error checking for existing item: %s", exc)
            return None

    def add_item_to_project(self, project_id: str, issue_node_id: str) -> str | None:
        """Add an issue to a project.

        Args:
            project_id: Project v2 ID.
            issue_node_id: Issue node ID.

        Returns:
            Item ID if successful, None otherwise.
        """
        mutation = """
            mutation AddProjectItem($projectId: ID!, $contentId: ID!) {
              addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
                item {
                  id
                }
              }
            }
        """
        variables = {"projectId": project_id, "contentId": issue_node_id}

        try:
            data = self._gql_query(mutation, variables)
            item_id = data.get("addProjectV2ItemById", {}).get("item", {}).get("id")
            if item_id:
                logger.info(
                    "Added issue %s to project %s as item %s",
                    issue_node_id,
                    project_id,
                    item_id,
                )
                return item_id
            else:
                logger.warning("Failed to get item ID after adding issue %s", issue_node_id)
                return None
        except Exception as exc:  # noqa: BLE001
            logger.error("Error adding item to project: %s", exc)
            return None

    def set_field_value(
        self,
        project_id: str,
        item_id: str,
        field_id: str,
        option_id: str,
    ) -> bool:
        """Set a field value on a project item.

        Args:
            project_id: Project v2 ID.
            item_id: Item ID.
            field_id: Field ID.
            option_id: Option ID (for single-select fields).

        Returns:
            True if successful, False otherwise.
        """
        mutation = """
            mutation SetFieldValue(
              $projectId: ID!
              $itemId: ID!
              $fieldId: ID!
              $value: ProjectV2FieldValue!
            ) {
              updateProjectV2ItemFieldValue(
                input: {
                  projectId: $projectId
                  itemId: $itemId
                  fieldId: $fieldId
                  value: $value
                }
              ) {
                clientMutationId
              }
            }
        """
        variables = {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "value": {"singleSelectOptionId": option_id},
        }

        try:
            self._gql_query(mutation, variables)
            logger.info(
                "Set field %s on item %s to option %s",
                field_id,
                item_id,
                option_id,
            )
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("Error setting field value: %s", exc)
            return False

    # -----------------------------------------------------------------------
    # Ecosystem Development board
    # -----------------------------------------------------------------------

    def add_issue_to_ecosystem(self, issue_node_id: str) -> str | None:
        """Add an issue to Ecosystem Development board.

        Sets Status=Backlog if the issue is not already in the project.

        Args:
            issue_node_id: Issue node ID.

        Returns:
            Item ID if successful, None otherwise.
        """
        ecosystem_config = self.config.get("projects", {}).get("ecosystem_development", {})
        project_id = ecosystem_config.get("id")

        if not project_id:
            logger.error("Ecosystem Development project ID not found in config")
            return None

        # Check if already exists
        existing_item_id = self.find_item_by_content(project_id, issue_node_id)
        if existing_item_id:
            logger.info("Issue %s already in Ecosystem Development", issue_node_id)
            return existing_item_id

        # Add item
        item_id = self.add_item_to_project(project_id, issue_node_id)
        if not item_id:
            return None

        # Set Status = Backlog
        status_field = ecosystem_config.get("fields", {}).get("status", {})
        status_field_id = status_field.get("id")
        backlog_option_id = status_field.get("options", {}).get("Backlog")

        if status_field_id and backlog_option_id:
            self.set_field_value(project_id, item_id, status_field_id, backlog_option_id)
        else:
            logger.warning("Status field config incomplete")

        return item_id

    def set_ecosystem_status(self, item_id: str, status: str) -> bool:
        """Set Status field on an Ecosystem Development item.

        Args:
            item_id: Item ID.
            status: One of: Backlog, In Progress, Review, Done.

        Returns:
            True if successful, False otherwise.
        """
        ecosystem_config = self.config.get("projects", {}).get("ecosystem_development", {})
        project_id = ecosystem_config.get("id")
        status_field = ecosystem_config.get("fields", {}).get("status", {})
        field_id = status_field.get("id")
        options = status_field.get("options", {})
        option_id = options.get(status)

        if not all([project_id, field_id, option_id]):
            logger.error("Status field config incomplete for status=%s", status)
            return False

        return self.set_field_value(project_id, item_id, field_id, option_id)

    def set_ecosystem_track(self, item_id: str, track: str) -> bool:
        """Set Track field on an Ecosystem Development item.

        Args:
            item_id: Item ID.
            track: One of: control-tower, portfolio, hamnet, hosting-ops, security, ai-infra, other.

        Returns:
            True if successful, False otherwise.
        """
        ecosystem_config = self.config.get("projects", {}).get("ecosystem_development", {})
        project_id = ecosystem_config.get("id")
        track_field = ecosystem_config.get("fields", {}).get("track", {})
        field_id = track_field.get("id")
        options = track_field.get("options", {})
        option_id = options.get(track)

        if not all([project_id, field_id, option_id]):
            logger.error("Track field config incomplete for track=%s", track)
            return False

        return self.set_field_value(project_id, item_id, field_id, option_id)

    def set_ecosystem_priority(self, item_id: str, priority: str) -> bool:
        """Set Priority field on an Ecosystem Development item.

        Args:
            item_id: Item ID.
            priority: One of: Critical, High, Medium, Low.

        Returns:
            True if successful, False otherwise.
        """
        ecosystem_config = self.config.get("projects", {}).get("ecosystem_development", {})
        project_id = ecosystem_config.get("id")
        priority_field = ecosystem_config.get("fields", {}).get("priority", {})
        field_id = priority_field.get("id")
        options = priority_field.get("options", {})
        option_id = options.get(priority)

        if not all([project_id, field_id, option_id]):
            logger.error("Priority field config incomplete for priority=%s", priority)
            return False

        return self.set_field_value(project_id, item_id, field_id, option_id)

    # -----------------------------------------------------------------------
    # Decisions & Approvals board
    # -----------------------------------------------------------------------

    def add_issue_to_decisions(self, issue_node_id: str, source: str) -> str | None:
        """Add an issue to Decisions & Approvals board.

        Sets Decision=Pending and Source=<source>.

        Args:
            issue_node_id: Issue node ID.
            source: One of: Decision Desk, Manual, Blocked Issue.

        Returns:
            Item ID if successful, None otherwise.
        """
        decisions_config = self.config.get("projects", {}).get("decisions_approvals", {})
        project_id = decisions_config.get("id")

        if not project_id:
            logger.error("Decisions & Approvals project ID not found in config")
            return None

        # Check if already exists
        existing_item_id = self.find_item_by_content(project_id, issue_node_id)
        if existing_item_id:
            logger.info("Issue %s already in Decisions & Approvals", issue_node_id)
            return existing_item_id

        # Add item
        item_id = self.add_item_to_project(project_id, issue_node_id)
        if not item_id:
            return None

        # Set Decision = Pending
        decision_field = decisions_config.get("fields", {}).get("decision", {})
        decision_field_id = decision_field.get("id")
        pending_option_id = decision_field.get("options", {}).get("Pending")

        if decision_field_id and pending_option_id:
            self.set_field_value(project_id, item_id, decision_field_id, pending_option_id)
        else:
            logger.warning("Decision field config incomplete")

        # Set Source = <source>
        source_field = decisions_config.get("fields", {}).get("source", {})
        source_field_id = source_field.get("id")
        source_option_id = source_field.get("options", {}).get(source)

        if source_field_id and source_option_id:
            self.set_field_value(project_id, item_id, source_field_id, source_option_id)
        else:
            logger.warning("Source field config incomplete for source=%s", source)

        return item_id

    def set_decision_status(self, item_id: str, decision: str) -> bool:
        """Set Decision field on a Decisions & Approvals item.

        Args:
            item_id: Item ID.
            decision: One of: Pending, Approved, Rejected, Deferred.

        Returns:
            True if successful, False otherwise.
        """
        decisions_config = self.config.get("projects", {}).get("decisions_approvals", {})
        project_id = decisions_config.get("id")
        decision_field = decisions_config.get("fields", {}).get("decision", {})
        field_id = decision_field.get("id")
        options = decision_field.get("options", {})
        option_id = options.get(decision)

        if not all([project_id, field_id, option_id]):
            logger.error("Decision field config incomplete for decision=%s", decision)
            return False

        return self.set_field_value(project_id, item_id, field_id, option_id)
