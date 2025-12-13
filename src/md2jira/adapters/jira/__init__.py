"""
Jira Adapter - Implementation of IssueTrackerPort for Atlassian Jira.

Includes both synchronous and asynchronous clients:
- JiraApiClient: Synchronous client for simple use cases
- AsyncJiraApiClient: Async client with parallel request support
"""

from .adapter import JiraAdapter
from .client import JiraApiClient

# Async client is optional (requires aiohttp)
try:
    from .async_client import AsyncJiraApiClient
    ASYNC_AVAILABLE = True
except ImportError:
    AsyncJiraApiClient = None  # type: ignore[misc, assignment]
    ASYNC_AVAILABLE = False

__all__ = ["JiraAdapter", "JiraApiClient", "AsyncJiraApiClient", "ASYNC_AVAILABLE"]

