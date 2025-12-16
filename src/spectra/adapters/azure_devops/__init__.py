"""
Azure DevOps Adapter - Integration with Azure DevOps Work Items.

This module provides the Azure DevOps implementation of the IssueTrackerPort,
enabling syncing markdown documents to Azure DevOps work items.
"""

from .adapter import AzureDevOpsAdapter
from .client import AzureDevOpsApiClient
from .plugin import AzureDevOpsTrackerPlugin


__all__ = [
    "AzureDevOpsAdapter",
    "AzureDevOpsApiClient",
    "AzureDevOpsTrackerPlugin",
]
