"""
Integration tests with mocked GitHub API responses.

These tests verify the full flow from adapter through client
using realistic API responses.
"""

import json
from unittest.mock import Mock, patch

import pytest

from spectra.adapters.github.adapter import GitHubAdapter
from spectra.core.ports.issue_tracker import IssueTrackerError


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def github_config():
    """GitHub adapter configuration."""
    return {
        "token": "ghp_test_token_12345",
        "owner": "test-org",
        "repo": "test-repo",
    }


@pytest.fixture
def mock_user_response():
    """Mock response for authenticated user."""
    return {
        "login": "testuser",
        "id": 12345,
        "name": "Test User",
        "email": "test@example.com",
    }


@pytest.fixture
def mock_issue_response():
    """Mock response for GitHub issue GET."""
    return {
        "number": 123,
        "title": "Sample User Story",
        "body": "**As a** developer\n**I want** a feature\n**So that** I can test",
        "state": "open",
        "labels": [
            {"name": "story"},
            {"name": "points:5"},
        ],
        "assignee": {"login": "testuser"},
        "milestone": {"number": 1, "title": "Sprint 1"},
    }


@pytest.fixture
def mock_issues_list_response():
    """Mock response for listing issues."""
    return [
        {
            "number": 10,
            "title": "Story Alpha",
            "body": "First story",
            "state": "open",
            "labels": [{"name": "story"}],
            "assignee": None,
        },
        {
            "number": 11,
            "title": "Story Beta",
            "body": "Second story",
            "state": "open",
            "labels": [{"name": "story"}, {"name": "status:in-progress"}],
            "assignee": {"login": "testuser"},
        },
    ]


@pytest.fixture
def mock_labels_response():
    """Mock response for listing labels."""
    return [
        {"name": "story", "color": "0e8a16"},
        {"name": "epic", "color": "6f42c1"},
        {"name": "subtask", "color": "fbca04"},
    ]


@pytest.fixture
def mock_comments_response():
    """Mock response for issue comments."""
    return [
        {
            "id": 1001,
            "body": "This is a comment",
            "user": {"login": "testuser"},
            "created_at": "2024-01-15T10:00:00Z",
        },
    ]


# =============================================================================
# GitHubAdapter Tests
# =============================================================================


class TestGitHubAdapterIntegration:
    """Integration tests for GitHubAdapter with mocked HTTP."""

    def test_get_issue_parses_response(self, github_config, mock_issue_response):
        """Test get_issue correctly parses API response."""
        adapter = GitHubAdapter(**github_config, dry_run=True)

        with patch.object(adapter._client, "get_issue") as mock_get:
            mock_get.return_value = mock_issue_response

            issue = adapter.get_issue("#123")

            assert issue.key == "#123"
            assert issue.summary == "Sample User Story"
            assert issue.status == "open"
            assert issue.issue_type == "Story"
            assert issue.story_points == 5.0
            assert issue.assignee == "testuser"

    def test_get_epic_children_with_milestone(self, github_config, mock_issues_list_response):
        """Test get_epic_children with milestone as epic."""
        adapter = GitHubAdapter(**github_config, dry_run=True)

        with patch.object(adapter._client, "list_issues") as mock_list:
            mock_list.return_value = mock_issues_list_response

            children = adapter.get_epic_children("1")

            assert len(children) == 2
            assert children[0].key == "#10"
            assert children[0].summary == "Story Alpha"
            assert children[1].key == "#11"
            assert children[1].status == "in progress"

    def test_get_issue_comments(self, github_config, mock_comments_response):
        """Test get_issue_comments returns parsed comments."""
        adapter = GitHubAdapter(**github_config, dry_run=True)

        with patch.object(adapter._client, "get_issue_comments") as mock_comments:
            mock_comments.return_value = mock_comments_response

            comments = adapter.get_issue_comments("#123")

            assert len(comments) == 1
            assert comments[0]["body"] == "This is a comment"

    def test_update_issue_description_dry_run(self, github_config):
        """Test update_issue_description in dry_run mode."""
        adapter = GitHubAdapter(**github_config, dry_run=True)

        result = adapter.update_issue_description("#123", "New description")

        assert result is True
        # Should not make any API calls in dry run

    def test_create_subtask_as_task_list(self, github_config, mock_issue_response):
        """Test create_subtask adds to parent body."""
        adapter = GitHubAdapter(**github_config, dry_run=False, subtasks_as_issues=False)

        with (
            patch.object(adapter._client, "get_issue") as mock_get,
            patch.object(adapter._client, "update_issue") as mock_update,
        ):
            mock_get.return_value = mock_issue_response

            result = adapter.create_subtask(
                parent_key="#123",
                summary="New subtask",
                description="Subtask description",
                project_key="test-repo",
            )

            # Task list items don't return a key
            assert result is None
            mock_update.assert_called_once()
            # Verify body was updated with task list
            call_kwargs = mock_update.call_args.kwargs
            assert "- [ ] **New subtask**" in call_kwargs.get("body", "")

    def test_create_subtask_as_issue(self, github_config):
        """Test create_subtask creates separate issue."""
        adapter = GitHubAdapter(**github_config, dry_run=False, subtasks_as_issues=True)

        with patch.object(adapter._client, "create_issue") as mock_create:
            mock_create.return_value = {"number": 456}

            result = adapter.create_subtask(
                parent_key="#123",
                summary="New subtask",
                description="Subtask description",
                project_key="test-repo",
                story_points=3,
            )

            assert result == "#456"
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert "subtask" in call_kwargs.get("labels", [])
            assert "points:3" in call_kwargs.get("labels", [])

    def test_transition_issue_to_done(self, github_config, mock_issue_response):
        """Test transition_issue closes issue for done status."""
        adapter = GitHubAdapter(**github_config, dry_run=False)

        with (
            patch.object(adapter._client, "get_issue") as mock_get,
            patch.object(adapter._client, "update_issue") as mock_update,
        ):
            mock_get.return_value = mock_issue_response

            result = adapter.transition_issue("#123", "done")

            assert result is True
            mock_update.assert_called_once()
            call_kwargs = mock_update.call_args.kwargs
            assert call_kwargs.get("state") == "closed"
            assert "status:done" in call_kwargs.get("labels", [])

    def test_add_comment(self, github_config):
        """Test add_comment adds to issue."""
        adapter = GitHubAdapter(**github_config, dry_run=False)

        with patch.object(adapter._client, "add_issue_comment") as mock_comment:
            result = adapter.add_comment("#123", "This is a comment")

            assert result is True
            mock_comment.assert_called_once_with(123, "This is a comment")

    def test_search_issues(self, github_config, mock_issues_list_response):
        """Test search_issues returns matching results."""
        adapter = GitHubAdapter(**github_config, dry_run=True)

        with patch.object(adapter._client, "search_issues") as mock_search:
            mock_search.return_value = mock_issues_list_response

            results = adapter.search_issues("is:open label:story", max_results=50)

            assert len(results) == 2
            assert results[0].summary == "Story Alpha"


class TestGitHubLinkOperations:
    """Tests for GitHub link operations."""

    def test_create_link_updates_body(self, github_config, mock_issue_response):
        """Test create_link adds reference to issue body."""
        from spectra.core.ports.issue_tracker import LinkType

        adapter = GitHubAdapter(**github_config, dry_run=False)

        with (
            patch.object(adapter._client, "get_issue") as mock_get,
            patch.object(adapter._client, "update_issue") as mock_update,
        ):
            mock_get.return_value = mock_issue_response

            result = adapter.create_link("#123", "#456", LinkType.BLOCKS)

            assert result is True
            mock_update.assert_called_once()
            call_kwargs = mock_update.call_args.kwargs
            assert "**Blocks:**" in call_kwargs.get("body", "")
            assert "#456" in call_kwargs.get("body", "")

    def test_get_issue_links_parses_body(self, github_config):
        """Test get_issue_links parses references from body."""
        adapter = GitHubAdapter(**github_config, dry_run=True)

        issue_with_links = {
            "number": 123,
            "title": "Issue with links",
            "body": "**Blocks:** #456, #789\n**Related to:** #999",
            "state": "open",
            "labels": [],
        }

        with patch.object(adapter._client, "get_issue") as mock_get:
            mock_get.return_value = issue_with_links

            links = adapter.get_issue_links("#123")

            assert len(links) >= 3
            block_targets = [l.target_key for l in links if l.link_type.value == "blocks"]
            assert "#456" in block_targets
            assert "#789" in block_targets

    def test_delete_link_removes_reference(self, github_config):
        """Test delete_link removes reference from body."""
        from spectra.core.ports.issue_tracker import LinkType

        adapter = GitHubAdapter(**github_config, dry_run=False)

        issue_with_links = {
            "number": 123,
            "title": "Issue",
            "body": "**Blocks:** #456, #789",
            "state": "open",
            "labels": [],
        }

        with (
            patch.object(adapter._client, "get_issue") as mock_get,
            patch.object(adapter._client, "update_issue") as mock_update,
        ):
            mock_get.return_value = issue_with_links

            result = adapter.delete_link("#123", "#456", LinkType.BLOCKS)

            assert result is True
            mock_update.assert_called_once()


class TestGitHubConnectionHandling:
    """Tests for connection handling."""

    def test_test_connection_success(self, github_config, mock_user_response):
        """Test connection test returns True on success."""
        adapter = GitHubAdapter(**github_config, dry_run=True)

        with patch.object(adapter._client, "test_connection") as mock_test:
            mock_test.return_value = True

            assert adapter.test_connection() is True

    def test_test_connection_failure(self, github_config):
        """Test connection test returns False on failure."""
        adapter = GitHubAdapter(**github_config, dry_run=True)

        with patch.object(adapter._client, "test_connection") as mock_test:
            mock_test.return_value = False

            assert adapter.test_connection() is False

    def test_adapter_name(self, github_config):
        """Test adapter returns correct name."""
        adapter = GitHubAdapter(**github_config, dry_run=True)
        assert adapter.name == "GitHub"


class TestGitHubExtendedOperations:
    """Tests for GitHub-specific extended operations."""

    def test_create_epic_as_milestone(self, github_config):
        """Test create_epic creates milestone."""
        adapter = GitHubAdapter(**github_config, dry_run=False)

        with patch.object(adapter._client, "create_milestone") as mock_create:
            mock_create.return_value = {"number": 5}

            result = adapter.create_epic("Sprint 5", "Sprint description", use_milestone=True)

            assert result == "milestone:5"
            mock_create.assert_called_once()

    def test_create_story(self, github_config):
        """Test create_story creates issue with story label."""
        adapter = GitHubAdapter(**github_config, dry_run=False)

        with patch.object(adapter._client, "create_issue") as mock_create:
            mock_create.return_value = {"number": 200}

            result = adapter.create_story(
                title="New Story",
                description="Story description",
                epic_key="milestone:5",
                story_points=8,
            )

            assert result == "#200"
            call_kwargs = mock_create.call_args.kwargs
            assert "story" in call_kwargs.get("labels", [])
            assert "points:8" in call_kwargs.get("labels", [])
            assert call_kwargs.get("milestone") == 5
