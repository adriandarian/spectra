"""
Linear Adapter - Integration with Linear.

This module provides the Linear implementation of the IssueTrackerPort,
enabling syncing markdown documents to Linear issues.
"""

from .adapter import LinearAdapter
from .client import LinearApiClient
from .plugin import LinearTrackerPlugin


__all__ = [
    "LinearAdapter",
    "LinearApiClient",
    "LinearTrackerPlugin",
]
