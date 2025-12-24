"""
GitLab Adapter - Implements IssueTrackerPort for GitLab Issues.

This package provides integration with GitLab Issues API.
Supports both GitLab.com and self-hosted GitLab instances.
"""

from .adapter import GitLabAdapter


__all__ = ["GitLabAdapter"]
