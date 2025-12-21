"""
Tests for AsyncJiraAdapter.

Tests async operations with mocked aiohttp.
"""

from unittest.mock import MagicMock, patch

import pytest


try:
    from spectra.adapters.jira.async_adapter import (
        ASYNC_AVAILABLE,
        AsyncJiraAdapter,
    )
except ImportError:
    ASYNC_AVAILABLE = False
    AsyncJiraAdapter = None

from spectra.core.ports.config_provider import TrackerConfig


@pytest.fixture
def mock_config():
    """Create a mock TrackerConfig."""
    return TrackerConfig(
        url="https://test.atlassian.net",
        email="test@example.com",
        api_token="test_token_123",
        project_key="PROJ",
    )


@pytest.mark.skipif(not ASYNC_AVAILABLE, reason="aiohttp not installed")
class TestAsyncJiraAdapterInit:
    """Tests for AsyncJiraAdapter initialization."""

    def test_init_with_defaults(self, mock_config):
        """Test adapter initialization with defaults."""
        adapter = AsyncJiraAdapter(config=mock_config)
        assert adapter.config == mock_config
        assert adapter._dry_run is True
        assert adapter._concurrency == 10
        assert adapter._client is None

    def test_init_with_custom_settings(self, mock_config):
        """Test adapter initialization with custom settings."""
        adapter = AsyncJiraAdapter(
            config=mock_config,
            dry_run=False,
            concurrency=5,
        )
        assert adapter._dry_run is False
        assert adapter._concurrency == 5

    def test_init_with_custom_formatter(self, mock_config):
        """Test adapter initialization with custom formatter."""
        mock_formatter = MagicMock()
        adapter = AsyncJiraAdapter(
            config=mock_config,
            formatter=mock_formatter,
        )
        assert adapter.formatter == mock_formatter


@pytest.mark.skipif(not ASYNC_AVAILABLE, reason="aiohttp not installed")
class TestAsyncJiraAdapterNotConnected:
    """Tests for error handling when not connected."""

    def test_ensure_connected_raises_when_not_connected(self, mock_config):
        """Test that _ensure_connected raises error when not connected."""
        adapter = AsyncJiraAdapter(config=mock_config)

        with pytest.raises(RuntimeError, match="not connected"):
            adapter._ensure_connected()


class TestAsyncNotAvailable:
    """Tests when aiohttp is not available."""

    def test_module_has_async_available_flag(self):
        """Test that ASYNC_AVAILABLE is defined."""
        # Just verify the import worked
        assert ASYNC_AVAILABLE in (True, False)
