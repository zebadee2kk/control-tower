"""
test_projects_sync.py — Unit tests for ProjectsSync (GitHub Projects v2 integration).

Tests cover:
- GraphQL mutations (add item, set field value)
- Deduplication (check if item already exists)
- Field setters (status, track, priority, decision)
- Error handling and graceful degradation
- Dry-run mode
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.integrations.projects_sync import REPO_TO_TRACK, ProjectsSync


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Create a temporary github_projects.json config file."""
    config = {
        "projects": {
            "ecosystem_development": {
                "id": "PVT_kwDOD7CZdM4BRKZt",
                "fields": {
                    "status": {
                        "id": "PVTSSF_lADOD7CZdM4BRKZtzg_EhE8",
                        "options": {
                            "Backlog": "d929f5fa",
                            "In Progress": "cf569d51",
                            "Review": "96d833aa",
                            "Done": "3a74da74",
                        },
                    },
                    "priority": {
                        "id": "PVTSSF_lADOD7CZdM4BRKZtzg_EhO8",
                        "options": {
                            "Critical": "88e5f8ae",
                            "High": "32f9a037",
                            "Medium": "c7b3f606",
                            "Low": "16305f9c",
                        },
                    },
                    "track": {
                        "id": "PVTSSF_lADOD7CZdM4BRKZtzg_EhPs",
                        "options": {
                            "control-tower": "f1f447ed",
                            "portfolio": "0ea3cbd9",
                            "hamnet": "23ae42e9",
                            "hosting-ops": "82d80642",
                            "security": "48ca3ce4",
                            "ai-infra": "731ec11b",
                            "other": "f10c9676",
                        },
                    },
                },
            },
            "decisions_approvals": {
                "id": "PVT_kwDOD7CZdM4BRKaA",
                "fields": {
                    "decision": {
                        "id": "PVTSSF_lADOD7CZdM4BRKaAzg_EhSk",
                        "options": {
                            "Pending": "b09a2b22",
                            "Approved": "30fbdaa8",
                            "Rejected": "8647f5d1",
                            "Deferred": "79274a0d",
                        },
                    },
                    "source": {
                        "id": "PVTSSF_lADOD7CZdM4BRKaAzg_EhSo",
                        "options": {
                            "Decision Desk": "c0ba308b",
                            "Manual": "ab786f1c",
                            "Blocked Issue": "a7b3682a",
                        },
                    },
                },
            },
        }
    }
    config_file = tmp_path / "github_projects.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f)
    return config_file


@pytest.fixture
def sync(config_file: Path) -> ProjectsSync:
    """Create a ProjectsSync instance with test config."""
    return ProjectsSync(pat="test-pat-12345", config_path=config_file)


class TestProjectsSyncInit:
    """Test ProjectsSync initialization."""

    def test_init_with_config_path(self, config_file: Path) -> None:
        """Test initialization with explicit config path."""
        sync = ProjectsSync(pat="test-pat", config_path=config_file)
        assert sync.pat == "test-pat"
        assert sync.config is not None
        assert "projects" in sync.config

    def test_init_missing_config_raises(self) -> None:
        """Test that missing config file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ProjectsSync(pat="test-pat", config_path=Path("/nonexistent/config.json"))

    def test_init_dry_run_mode(self, config_file: Path) -> None:
        """Test initialization with dry_run=True."""
        sync = ProjectsSync(pat="test-pat", config_path=config_file, dry_run=True)
        assert sync.dry_run is True


class TestGraphQLQuery:
    """Test GraphQL query/mutation execution."""

    @patch("src.integrations.projects_sync.requests.post")
    def test_gql_query_success(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test successful GraphQL query."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"viewer": {"login": "derek-ai-dev"}}}
        mock_post.return_value = mock_response

        result = sync._gql_query("{ viewer { login } }")

        assert result == {"viewer": {"login": "derek-ai-dev"}}
        mock_post.assert_called_once()

    @patch("src.integrations.projects_sync.requests.post")
    def test_gql_query_with_variables(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test GraphQL query with variables."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"node": {"id": "test-id"}}}
        mock_post.return_value = mock_response

        variables = {"projectId": "PVT_kwDOD7CZdM4BRKZt"}
        result = sync._gql_query("query Test { node(id: $projectId) { id } }", variables)

        assert result == {"node": {"id": "test-id"}}
        call_args = mock_post.call_args
        assert call_args[1]["json"]["variables"] == variables

    @patch("src.integrations.projects_sync.requests.post")
    def test_gql_query_graphql_error(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test GraphQL query with API errors."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "errors": [{"message": "Invalid query"}]
        }
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="GraphQL errors"):
            sync._gql_query("{ invalid }")

    @patch("src.integrations.projects_sync.requests.post")
    def test_gql_query_request_error(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test GraphQL query with network error."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        with pytest.raises(RuntimeError, match="GraphQL request failed"):
            sync._gql_query("{ viewer { login } }")

    def test_gql_query_dry_run(self, sync: ProjectsSync) -> None:
        """Test that dry_run mode returns empty dict without making requests."""
        sync.dry_run = True
        result = sync._gql_query("{ viewer { login } }")
        assert result == {}


class TestFindItemByContent:
    """Test deduplication logic."""

    @patch("src.integrations.projects_sync.requests.post")
    def test_find_item_existing(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test finding an existing item in project."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "node": {
                    "items": {
                        "nodes": [
                            {
                                "id": "item-123",
                                "content": {"id": "issue-node-456"},
                            }
                        ]
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        result = sync.find_item_by_content("project-789", "issue-node-456")

        assert result == "item-123"

    @patch("src.integrations.projects_sync.requests.post")
    def test_find_item_not_found(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test that None is returned when item not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "node": {
                    "items": {
                        "nodes": [
                            {
                                "id": "item-123",
                                "content": {"id": "issue-node-999"},
                            }
                        ]
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        result = sync.find_item_by_content("project-789", "issue-node-456")

        assert result is None

    @patch("src.integrations.projects_sync.requests.post")
    def test_find_item_empty_project(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test finding item in empty project."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "node": {
                    "items": {
                        "nodes": []
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        result = sync.find_item_by_content("project-789", "issue-node-456")

        assert result is None

    @patch("src.integrations.projects_sync.requests.post")
    def test_find_item_api_error_returns_none(
        self, mock_post: MagicMock, sync: ProjectsSync
    ) -> None:
        """Test that API errors during find return None (graceful degradation)."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        result = sync.find_item_by_content("project-789", "issue-node-456")

        assert result is None


class TestAddItemToProject:
    """Test adding items to projects."""

    @patch("src.integrations.projects_sync.requests.post")
    def test_add_item_success(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test successfully adding an item to a project."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "addProjectV2ItemById": {
                    "item": {
                        "id": "item-123"
                    }
                }
            }
        }
        mock_post.return_value = mock_response

        result = sync.add_item_to_project("project-789", "issue-node-456")

        assert result == "item-123"

    @patch("src.integrations.projects_sync.requests.post")
    def test_add_item_missing_item_id(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test that None is returned if item ID is missing from response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "addProjectV2ItemById": {
                    "item": {}
                }
            }
        }
        mock_post.return_value = mock_response

        result = sync.add_item_to_project("project-789", "issue-node-456")

        assert result is None

    @patch("src.integrations.projects_sync.requests.post")
    def test_add_item_api_error_returns_none(
        self, mock_post: MagicMock, sync: ProjectsSync
    ) -> None:
        """Test that API errors during add return None (graceful degradation)."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        result = sync.add_item_to_project("project-789", "issue-node-456")

        assert result is None


class TestSetFieldValue:
    """Test setting field values on items."""

    @patch("src.integrations.projects_sync.requests.post")
    def test_set_field_success(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test successfully setting a field value."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": {
                "updateProjectV2ItemFieldValue": {
                    "clientMutationId": "mutation-123"
                }
            }
        }
        mock_post.return_value = mock_response

        result = sync.set_field_value(
            "project-789",
            "item-123",
            "field-456",
            "option-789"
        )

        assert result is True

    @patch("src.integrations.projects_sync.requests.post")
    def test_set_field_api_error(self, mock_post: MagicMock, sync: ProjectsSync) -> None:
        """Test that API errors during set_field return False."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        result = sync.set_field_value(
            "project-789",
            "item-123",
            "field-456",
            "option-789"
        )

        assert result is False


class TestEcosystemDevelopment:
    """Test Ecosystem Development board operations."""

    @patch.object(ProjectsSync, "find_item_by_content")
    @patch.object(ProjectsSync, "add_item_to_project")
    @patch.object(ProjectsSync, "set_field_value")
    def test_add_issue_to_ecosystem_new_item(
        self,
        mock_set_field: MagicMock,
        mock_add_item: MagicMock,
        mock_find: MagicMock,
        sync: ProjectsSync,
    ) -> None:
        """Test adding a new issue to Ecosystem Development."""
        mock_find.return_value = None  # Not found, so add it
        mock_add_item.return_value = "item-123"
        mock_set_field.return_value = True

        result = sync.add_issue_to_ecosystem("issue-node-456")

        assert result == "item-123"
        mock_find.assert_called_once()
        mock_add_item.assert_called_once()
        mock_set_field.assert_called_once()  # For Status=Backlog

    @patch.object(ProjectsSync, "find_item_by_content")
    @patch.object(ProjectsSync, "add_item_to_project")
    def test_add_issue_to_ecosystem_already_exists(
        self,
        mock_add_item: MagicMock,
        mock_find: MagicMock,
        sync: ProjectsSync,
    ) -> None:
        """Test that existing items are not re-added."""
        mock_find.return_value = "item-123"  # Already exists

        result = sync.add_issue_to_ecosystem("issue-node-456")

        assert result == "item-123"
        mock_add_item.assert_not_called()

    @patch.object(ProjectsSync, "set_field_value")
    def test_set_ecosystem_status(self, mock_set_field: MagicMock, sync: ProjectsSync) -> None:
        """Test setting Status field."""
        mock_set_field.return_value = True

        result = sync.set_ecosystem_status("item-123", "In Progress")

        assert result is True
        mock_set_field.assert_called_once()

    @patch.object(ProjectsSync, "set_field_value")
    def test_set_ecosystem_status_invalid(
        self, mock_set_field: MagicMock, sync: ProjectsSync
    ) -> None:
        """Test that invalid status values return False."""
        result = sync.set_ecosystem_status("item-123", "Invalid Status")

        assert result is False
        mock_set_field.assert_not_called()

    @patch.object(ProjectsSync, "set_field_value")
    def test_set_ecosystem_track(self, mock_set_field: MagicMock, sync: ProjectsSync) -> None:
        """Test setting Track field."""
        mock_set_field.return_value = True

        result = sync.set_ecosystem_track("item-123", "control-tower")

        assert result is True

    @patch.object(ProjectsSync, "set_field_value")
    def test_set_ecosystem_track_invalid(
        self, mock_set_field: MagicMock, sync: ProjectsSync
    ) -> None:
        """Test that invalid track values return False."""
        result = sync.set_ecosystem_track("item-123", "invalid-track")

        assert result is False
        mock_set_field.assert_not_called()

    @patch.object(ProjectsSync, "set_field_value")
    def test_set_ecosystem_priority(self, mock_set_field: MagicMock, sync: ProjectsSync) -> None:
        """Test setting Priority field."""
        mock_set_field.return_value = True

        result = sync.set_ecosystem_priority("item-123", "Critical")

        assert result is True

    @patch.object(ProjectsSync, "set_field_value")
    def test_set_ecosystem_priority_invalid(
        self, mock_set_field: MagicMock, sync: ProjectsSync
    ) -> None:
        """Test that invalid priority values return False."""
        result = sync.set_ecosystem_priority("item-123", "urgent")

        assert result is False
        mock_set_field.assert_not_called()


class TestDecisionsApprovals:
    """Test Decisions & Approvals board operations."""

    @patch.object(ProjectsSync, "find_item_by_content")
    @patch.object(ProjectsSync, "add_item_to_project")
    @patch.object(ProjectsSync, "set_field_value")
    def test_add_issue_to_decisions_new_item(
        self,
        mock_set_field: MagicMock,
        mock_add_item: MagicMock,
        mock_find: MagicMock,
        sync: ProjectsSync,
    ) -> None:
        """Test adding a new issue to Decisions & Approvals."""
        mock_find.return_value = None  # Not found
        mock_add_item.return_value = "item-123"
        mock_set_field.return_value = True

        result = sync.add_issue_to_decisions("issue-node-456", source="Decision Desk")

        assert result == "item-123"
        # Should set both Decision=Pending and Source
        assert mock_set_field.call_count == 2

    @patch.object(ProjectsSync, "find_item_by_content")
    @patch.object(ProjectsSync, "add_item_to_project")
    def test_add_issue_to_decisions_already_exists(
        self,
        mock_add_item: MagicMock,
        mock_find: MagicMock,
        sync: ProjectsSync,
    ) -> None:
        """Test that existing items are not re-added."""
        mock_find.return_value = "item-123"

        result = sync.add_issue_to_decisions("issue-node-456", source="Blocked Issue")

        assert result == "item-123"
        mock_add_item.assert_not_called()

    @patch.object(ProjectsSync, "set_field_value")
    def test_set_decision_status(self, mock_set_field: MagicMock, sync: ProjectsSync) -> None:
        """Test setting Decision field."""
        mock_set_field.return_value = True

        result = sync.set_decision_status("item-123", "Approved")

        assert result is True

    @patch.object(ProjectsSync, "set_field_value")
    def test_set_decision_status_invalid(
        self, mock_set_field: MagicMock, sync: ProjectsSync
    ) -> None:
        """Test that invalid decision values return False."""
        result = sync.set_decision_status("item-123", "Not A Decision")

        assert result is False
        mock_set_field.assert_not_called()


class TestRepoToTrackMapping:
    """Test repo name to track mapping."""

    def test_repo_mapping(self) -> None:
        """Test that repo mapping is correctly configured."""
        assert REPO_TO_TRACK["control-tower"] == "control-tower"
        assert REPO_TO_TRACK["portfolio-management"] == "portfolio"
        assert REPO_TO_TRACK["RedGuard-Suite"] == "security"
        assert REPO_TO_TRACK["ai-powertools"] == "ai-infra"

    def test_repo_mapping_default(self) -> None:
        """Test that unknown repos map to 'other'."""
        # The get() method in run_enhanced_desk.py should handle missing repos
        # by defaulting to "other"
        track = REPO_TO_TRACK.get("unknown-repo", "other")
        assert track == "other"
