"""
Tests for Shortcut Adapter.
"""

from unittest.mock import MagicMock, patch

import pytest

from spectra.adapters.shortcut.adapter import ShortcutAdapter
from spectra.adapters.shortcut.client import ShortcutApiClient, ShortcutRateLimiter
from spectra.adapters.shortcut.plugin import ShortcutTrackerPlugin, create_plugin
from spectra.core.ports.issue_tracker import (
    AuthenticationError,
    NotFoundError,
    TransitionError,
)


# =============================================================================
# Rate Limiter Tests
# =============================================================================


class TestShortcutRateLimiter:
    """Tests for ShortcutRateLimiter."""

    def test_acquire_with_available_tokens(self):
        """Should immediately acquire when tokens available."""
        limiter = ShortcutRateLimiter(requests_per_second=10.0, burst_size=5)

        assert limiter.acquire(timeout=0.1) is True
        assert limiter.acquire(timeout=0.1) is True
        assert limiter.acquire(timeout=0.1) is True

    def test_stats_tracking(self):
        """Should track request statistics."""
        limiter = ShortcutRateLimiter(requests_per_second=10.0, burst_size=5)

        limiter.acquire()
        limiter.acquire()

        stats = limiter.stats
        assert stats["total_requests"] == 2
        assert "current_tokens" in stats
        assert "requests_per_second" in stats

    def test_update_from_response(self):
        """Should update state from Shortcut response headers."""
        limiter = ShortcutRateLimiter()

        mock_response = MagicMock()
        mock_response.headers = {"Retry-After": "60"}
        mock_response.status_code = 200

        limiter.update_from_response(mock_response)

        # Should handle retry-after header
        assert limiter._retry_after is not None


# =============================================================================
# API Client Tests
# =============================================================================


class TestShortcutApiClient:
    """Tests for ShortcutApiClient."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock session for testing."""
        with patch("spectra.adapters.shortcut.client.requests.Session") as mock:
            session = MagicMock()
            mock.return_value = session
            yield session

    @pytest.fixture
    def client(self, mock_session):
        """Create a test client with mocked session."""
        return ShortcutApiClient(
            api_token="test_token",
            workspace_id="test_workspace",
            dry_run=False,
        )

    def test_initialization(self, mock_session):
        """Should initialize with correct configuration."""
        client = ShortcutApiClient(api_token="test_token", workspace_id="test_workspace")

        assert client.api_url == "https://api.app.shortcut.com/api/v3"
        assert client.dry_run is True  # Default

    def test_request_get(self, client, mock_session):
        """Should execute GET request."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "name": "Test Story"}
        mock_response.headers = {}
        mock_session.request.return_value = mock_response

        result = client.request("GET", "/stories/123")

        assert result["id"] == 123
        mock_session.request.assert_called_once()

    def test_authentication_error(self, client, mock_session):
        """Should raise AuthenticationError on 401."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_session.request.return_value = mock_response

        with pytest.raises(AuthenticationError):
            client.request("GET", "/member")

    def test_not_found_error(self, client, mock_session):
        """Should raise NotFoundError on 404."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_session.request.return_value = mock_response

        with pytest.raises(NotFoundError):
            client.request("GET", "/stories/999")

    def test_get_story(self, client, mock_session):
        """Should get a story by ID."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "name": "Test Story",
            "description": "Test description",
        }
        mock_response.headers = {}
        mock_session.request.return_value = mock_response

        result = client.get_story(123)

        assert result["id"] == 123
        assert result["name"] == "Test Story"

    def test_get_story_dependencies(self, client, mock_session):
        """Should get story dependencies."""
        # Mock get_story to return story with dependencies
        mock_story_response = MagicMock()
        mock_story_response.ok = True
        mock_story_response.status_code = 200
        mock_story_response.json.return_value = {
            "id": 123,
            "depends_on": [{"id": 456}, {"id": 789}],
        }
        mock_story_response.headers = {}
        mock_session.request.return_value = mock_story_response

        deps = client.get_story_dependencies(123)

        assert deps == [456, 789]

    def test_add_story_dependency(self, client, mock_session):
        """Should add a story dependency."""
        # Mock get_story (called first to get current deps)
        mock_get_response = MagicMock()
        mock_get_response.ok = True
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "id": 123,
            "depends_on": [],
        }
        mock_get_response.headers = {}

        # Mock update_story response
        mock_update_response = MagicMock()
        mock_update_response.ok = True
        mock_update_response.status_code = 200
        mock_update_response.json.return_value = {"id": 123}
        mock_update_response.headers = {}

        mock_session.request.side_effect = [mock_get_response, mock_update_response]

        result = client.add_story_dependency(123, 456)

        assert result["id"] == 123
        # Verify update was called with new dependency
        assert mock_session.request.call_count == 2

    def test_remove_story_dependency(self, client, mock_session):
        """Should remove a story dependency."""
        # Mock get_story (called first to get current deps)
        mock_get_response = MagicMock()
        mock_get_response.ok = True
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "id": 123,
            "depends_on": [{"id": 456}, {"id": 789}],
        }
        mock_get_response.headers = {}

        # Mock update_story response
        mock_update_response = MagicMock()
        mock_update_response.ok = True
        mock_update_response.status_code = 200
        mock_update_response.json.return_value = {"id": 123}
        mock_update_response.headers = {}

        mock_session.request.side_effect = [mock_get_response, mock_update_response]

        result = client.remove_story_dependency(123, 456)

        assert result["id"] == 123
        # Verify update was called with dependency removed
        assert mock_session.request.call_count == 2

    def test_create_story(self, client, mock_session):
        """Should create a new story."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 456,
            "name": "New Story",
        }
        mock_response.headers = {}
        mock_session.request.return_value = mock_response

        result = client.create_story(name="New Story", description="Description")

        assert result["id"] == 456
        mock_session.request.assert_called_once()

    def test_get_workflow_states(self, client, mock_session):
        """Should get workflow states."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "workflow-1",
                "states": [
                    {"id": 1, "name": "To Do", "type": "unstarted"},
                    {"id": 2, "name": "In Progress", "type": "started"},
                ],
            }
        ]
        mock_response.headers = {}
        mock_session.request.return_value = mock_response

        states = client.get_workflow_states()

        assert len(states) == 2
        assert states[0]["name"] == "To Do"


# =============================================================================
# Adapter Tests
# =============================================================================


class TestShortcutAdapter:
    """Tests for ShortcutAdapter."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client."""
        return MagicMock(spec=ShortcutApiClient)

    @pytest.fixture
    def adapter(self, mock_client):
        """Create an adapter with mocked client."""
        adapter = ShortcutAdapter(
            api_token="test_token",
            workspace_id="test_workspace",
            dry_run=False,  # Set to False so methods actually call the client
        )
        adapter._client = mock_client
        return adapter

    def test_name(self, adapter):
        """Should return correct name."""
        assert adapter.name == "Shortcut"

    def test_get_issue(self, adapter, mock_client):
        """Should get an issue by key."""
        mock_client.get_story.return_value = {
            "id": 123,
            "name": "Test Story",
            "description": "Description",
            "workflow_state": {"name": "In Progress"},
            "story_type": "feature",
            "estimate": 5,
            "owners": [],
            "tasks": [],
            "comments": [],
        }

        result = adapter.get_issue("123")

        assert result.key == "123"
        assert result.summary == "Test Story"
        assert result.status == "In Progress"

    def test_get_epic_children(self, adapter, mock_client):
        """Should get epic children."""
        mock_client.get_epic_stories.return_value = [
            {
                "id": 1,
                "name": "Story 1",
                "workflow_state": {"name": "To Do"},
                "story_type": "feature",
                "estimate": None,
                "owners": [],
                "tasks": [],
                "comments": [],
            },
            {
                "id": 2,
                "name": "Story 2",
                "workflow_state": {"name": "Done"},
                "story_type": "feature",
                "estimate": 3,
                "owners": [],
                "tasks": [],
                "comments": [],
            },
        ]

        results = adapter.get_epic_children("100")

        assert len(results) == 2
        assert results[0].key == "1"
        assert results[1].key == "2"

    def test_create_subtask(self, adapter, mock_client):
        """Should create a subtask."""
        mock_client.create_task.return_value = {"id": 456}

        result = adapter.create_subtask(
            parent_key="123",
            summary="Subtask",
            description="Description",
            project_key="PROJ",
        )

        assert result == "123-T456"
        mock_client.create_task.assert_called_once()

    def test_transition_issue(self, adapter, mock_client):
        """Should transition an issue."""
        mock_client.get_workflow_states.return_value = [
            {"id": 1, "name": "To Do"},
            {"id": 2, "name": "In Progress"},
            {"id": 3, "name": "Done"},
        ]

        adapter.transition_issue("123", "In Progress")

        mock_client.update_story.assert_called_once_with(123, workflow_state_id=2)

    def test_transition_issue_invalid_state(self, adapter, mock_client):
        """Should raise TransitionError for invalid state."""
        mock_client.get_workflow_states.return_value = [
            {"id": 1, "name": "To Do"},
        ]

        with pytest.raises(TransitionError) as exc_info:
            adapter.transition_issue("123", "Invalid State")
        assert "Invalid State" in str(exc_info.value)

    def test_update_issue_story_points(self, adapter, mock_client):
        """Should update story points."""
        adapter.update_issue_story_points("123", 5.0)

        mock_client.update_story.assert_called_once_with(123, estimate=5)

    def test_add_comment(self, adapter, mock_client):
        """Should add a comment."""
        adapter.add_comment("123", "Test comment")

        mock_client.create_comment.assert_called_once_with(123, "Test comment")

    def test_get_issue_links(self, adapter, mock_client):
        """Should get issue links (dependencies)."""
        mock_client.get_story_dependencies.return_value = [456, 789]

        links = adapter.get_issue_links("123")

        assert len(links) == 2
        assert links[0].target_key == "456"
        assert links[1].target_key == "789"
        assert all(link.link_type.value == "depends on" for link in links)

    def test_get_issue_links_empty(self, adapter, mock_client):
        """Should return empty list when no dependencies."""
        mock_client.get_story_dependencies.return_value = []

        links = adapter.get_issue_links("123")

        assert links == []

    def test_create_link_depends_on(self, adapter, mock_client):
        """Should create a DEPENDS_ON link."""
        from spectra.core.ports.issue_tracker import LinkType

        adapter.create_link("123", "456", LinkType.DEPENDS_ON)

        mock_client.add_story_dependency.assert_called_once_with(123, 456)

    def test_create_link_is_dependency_of(self, adapter, mock_client):
        """Should create an IS_DEPENDENCY_OF link (reverse)."""
        from spectra.core.ports.issue_tracker import LinkType

        adapter.create_link("123", "456", LinkType.IS_DEPENDENCY_OF)

        mock_client.add_story_dependency.assert_called_once_with(456, 123)

    def test_create_link_blocks(self, adapter, mock_client):
        """Should create a BLOCKS link (target depends on source)."""
        from spectra.core.ports.issue_tracker import LinkType

        adapter.create_link("123", "456", LinkType.BLOCKS)

        mock_client.add_story_dependency.assert_called_once_with(456, 123)

    def test_create_link_is_blocked_by(self, adapter, mock_client):
        """Should create an IS_BLOCKED_BY link (source depends on target)."""
        from spectra.core.ports.issue_tracker import LinkType

        adapter.create_link("123", "456", LinkType.IS_BLOCKED_BY)

        mock_client.add_story_dependency.assert_called_once_with(123, 456)

    def test_delete_link(self, adapter, mock_client):
        """Should delete a dependency link."""
        from spectra.core.ports.issue_tracker import LinkType

        adapter.delete_link("123", "456", LinkType.DEPENDS_ON)

        mock_client.remove_story_dependency.assert_called_once_with(123, 456)

    def test_delete_link_no_type(self, adapter, mock_client):
        """Should delete link in both directions when type not specified."""
        adapter.delete_link("123", "456")

        # Should try both directions
        assert mock_client.remove_story_dependency.call_count == 2
        mock_client.remove_story_dependency.assert_any_call(123, 456)
        mock_client.remove_story_dependency.assert_any_call(456, 123)


# =============================================================================
# Plugin Tests
# =============================================================================


class TestShortcutTrackerPlugin:
    """Tests for ShortcutTrackerPlugin."""

    def test_metadata(self):
        """Should have correct metadata."""
        from spectra.plugins.base import PluginType

        plugin = ShortcutTrackerPlugin()
        metadata = plugin.metadata

        assert metadata.name == "shortcut"
        assert metadata.plugin_type == PluginType.TRACKER

    @patch.dict(
        "os.environ", {"SHORTCUT_API_TOKEN": "env_token", "SHORTCUT_WORKSPACE_ID": "env_workspace"}
    )
    def test_initialize_from_env(self):
        """Should initialize from environment variables."""
        plugin = ShortcutTrackerPlugin()
        plugin.config = {}

        with patch("spectra.adapters.shortcut.plugin.ShortcutAdapter") as mock_adapter:
            mock_adapter.return_value = MagicMock()
            plugin.initialize()

            mock_adapter.assert_called_once_with(
                api_token="env_token",
                workspace_id="env_workspace",
                api_url="https://api.app.shortcut.com/api/v3",
                dry_run=True,
            )

    def test_validate_config_missing_token(self):
        """Should validate missing API token."""
        plugin = ShortcutTrackerPlugin()
        plugin.config = {}

        errors = plugin.validate_config()

        assert len(errors) > 0
        assert any("token" in error.lower() for error in errors)

    def test_create_plugin(self):
        """Should create plugin instance."""
        plugin = create_plugin({"api_token": "test", "workspace_id": "ws"})

        assert isinstance(plugin, ShortcutTrackerPlugin)
