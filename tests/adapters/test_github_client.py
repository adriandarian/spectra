"""
Tests for GitHubApiClient.

Tests REST API client with mocked HTTP responses.
"""

from unittest.mock import MagicMock, patch

import pytest

from spectra.adapters.github.client import GitHubRateLimiter


@pytest.fixture
def mock_issue_response():
    """Mock GitHub issue response."""
    return {
        "number": 123,
        "title": "Test Issue",
        "body": "Issue description",
        "state": "open",
        "labels": [{"name": "bug"}],
        "assignee": {"login": "testuser"},
        "milestone": {"number": 1, "title": "Sprint 1"},
    }


class TestGitHubRateLimiter:
    """Tests for GitHubRateLimiter."""

    def test_init(self):
        """Test rate limiter initialization."""
        limiter = GitHubRateLimiter(requests_per_second=5.0, burst_size=10)
        assert limiter.requests_per_second == 5.0
        assert limiter.burst_size == 10

    def test_acquire_token(self):
        """Test acquiring a token."""
        limiter = GitHubRateLimiter(requests_per_second=100.0, burst_size=10)
        result = limiter.acquire(timeout=1.0)
        assert result is True

    def test_acquire_depletes_tokens(self):
        """Test that acquiring depletes tokens."""
        limiter = GitHubRateLimiter(requests_per_second=100.0, burst_size=5)

        # Acquire all tokens
        for _ in range(5):
            limiter.acquire(timeout=0.1)

        # Next acquire should wait
        initial_tokens = limiter._tokens
        assert initial_tokens < 1.0

    def test_stats(self):
        """Test stats property."""
        limiter = GitHubRateLimiter()
        limiter.acquire()

        stats = limiter.stats
        assert "total_requests" in stats
        assert stats["total_requests"] == 1

    def test_reset(self):
        """Test reset method."""
        limiter = GitHubRateLimiter(burst_size=10)
        limiter.acquire()
        limiter.acquire()

        limiter.reset()

        assert limiter._tokens == 10.0
        assert limiter._total_requests == 0

    def test_update_from_response(self):
        """Test updating from GitHub response headers."""
        limiter = GitHubRateLimiter()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-RateLimit-Remaining": "4999",
            "X-RateLimit-Reset": "1234567890",
        }

        limiter.update_from_response(mock_response)

        assert limiter._rate_limit_remaining == 4999

    def test_update_from_rate_limit_response(self):
        """Test rate adjustment on 429."""
        limiter = GitHubRateLimiter(requests_per_second=10.0)
        original_rate = limiter.requests_per_second

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {}

        limiter.update_from_response(mock_response)

        assert limiter.requests_per_second < original_rate

    def test_should_wait_for_github_limit_no_remaining(self):
        """Test _should_wait_for_github_limit when no remaining set."""
        limiter = GitHubRateLimiter()
        assert limiter._should_wait_for_github_limit() is False

    def test_should_wait_for_github_limit_low_remaining(self):
        """Test _should_wait_for_github_limit when remaining is low."""
        limiter = GitHubRateLimiter()
        limiter._rate_limit_remaining = 3
        assert limiter._should_wait_for_github_limit() is True

    def test_github_wait_time_no_reset(self):
        """Test _github_wait_time when no reset time set."""
        limiter = GitHubRateLimiter()
        assert limiter._github_wait_time() == 60.0

    def test_refill_tokens(self):
        """Test _refill_tokens adds tokens over time."""
        limiter = GitHubRateLimiter(requests_per_second=1000.0, burst_size=10)
        limiter._tokens = 0.0

        # Simulate time passing by calling refill
        import time

        time.sleep(0.01)
        limiter._refill_tokens()

        assert limiter._tokens > 0


class TestGitHubApiClientInit:
    """Tests for GitHubApiClient initialization."""

    def test_init_sets_attributes(self):
        """Test initialization sets basic attributes."""
        with patch("spectra.adapters.github.client.requests.Session"):
            from spectra.adapters.github.client import GitHubApiClient

            client = GitHubApiClient(
                token="ghp_test",
                owner="owner",
                repo="repo",
            )

            assert client.owner == "owner"
            assert client.repo == "repo"
            assert client.dry_run is True

    def test_init_with_custom_base_url(self):
        """Test initialization with enterprise URL."""
        with patch("spectra.adapters.github.client.requests.Session"):
            from spectra.adapters.github.client import GitHubApiClient

            client = GitHubApiClient(
                token="ghp_test",
                owner="owner",
                repo="repo",
                base_url="https://github.enterprise.com/api/v3/",
            )

            assert client.base_url == "https://github.enterprise.com/api/v3"

    def test_init_without_rate_limiter(self):
        """Test initialization without rate limiting."""
        with patch("spectra.adapters.github.client.requests.Session"):
            from spectra.adapters.github.client import GitHubApiClient

            client = GitHubApiClient(
                token="ghp_test",
                owner="owner",
                repo="repo",
                requests_per_second=None,
            )

            assert client._rate_limiter is None

    def test_init_with_rate_limiter(self):
        """Test initialization with rate limiting."""
        with patch("spectra.adapters.github.client.requests.Session"):
            from spectra.adapters.github.client import GitHubApiClient

            client = GitHubApiClient(
                token="ghp_test",
                owner="owner",
                repo="repo",
                requests_per_second=5.0,
            )

            assert client._rate_limiter is not None
