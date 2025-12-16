"""
Ports - Abstract interfaces for external dependencies.

Ports define the contracts that adapters must implement.
This enables dependency inversion and easy testing.
"""

from .async_tracker import AsyncIssueTrackerPort
from .config_provider import ConfigProviderPort
from .document_formatter import DocumentFormatterPort
from .document_output import (
    AuthenticationError as OutputAuthenticationError,
)
from .document_output import (
    DocumentOutputError,
    DocumentOutputPort,
)
from .document_output import (
    NotFoundError as OutputNotFoundError,
)
from .document_output import (
    PermissionError as OutputPermissionError,
)
from .document_output import (
    RateLimitError as OutputRateLimitError,
)
from .document_parser import DocumentParserPort, ParserError
from .issue_tracker import (
    AuthenticationError,
    IssueTrackerError,
    IssueTrackerPort,
    NotFoundError,
    PermissionError,
    RateLimitError,
    TransientError,
    TransitionError,
)


__all__ = [
    "AsyncIssueTrackerPort",
    "AuthenticationError",
    "ConfigProviderPort",
    "DocumentFormatterPort",
    # Output exceptions
    "DocumentOutputError",
    "DocumentOutputPort",
    "DocumentParserPort",
    # Issue tracker exceptions
    "IssueTrackerError",
    # Ports
    "IssueTrackerPort",
    "NotFoundError",
    "OutputAuthenticationError",
    "OutputNotFoundError",
    "OutputPermissionError",
    "OutputRateLimitError",
    # Parser exceptions
    "ParserError",
    "PermissionError",
    "RateLimitError",
    "TransientError",
    "TransitionError",
]
