"""Issue tracker adapters - implementations for various platforms."""

from spectra.adapters.azure_devops import AzureDevOpsAdapter
from spectra.adapters.confluence import ConfluenceAdapter
from spectra.adapters.github import GitHubAdapter
from spectra.adapters.jira import JiraAdapter
from spectra.adapters.linear import LinearAdapter


__all__ = [
    "AzureDevOpsAdapter",
    "ConfluenceAdapter",
    "GitHubAdapter",
    "JiraAdapter",
    "LinearAdapter",
]
