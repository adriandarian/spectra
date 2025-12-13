"""
Linear Adapter - Integration with Linear.

This module provides the Linear implementation of the IssueTrackerPort,
enabling syncing markdown documents to Linear issues.
"""

from .client import LinearApiClient
from .adapter import LinearAdapter
from .plugin import LinearTrackerPlugin

__all__ = [
    "LinearApiClient",
    "LinearAdapter",
    "LinearTrackerPlugin",
]

