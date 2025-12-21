"""
Async Base - HTTP client infrastructure with rate limiting.

This module provides the foundation for API clients:
- BaseHttpClient: Synchronous HTTP client base with retry and rate limiting
- TokenBucketRateLimiter: Synchronous token bucket rate limiter (base class)
- JiraRateLimiter, GitHubRateLimiter, LinearRateLimiter: API-specific rate limiters
- AsyncRateLimiter: Async-compatible token bucket rate limiter
- AsyncHttpClient: Base async HTTP client with retry and rate limiting
- Parallel execution utilities for batch operations

Requires aiohttp for async features: pip install aiohttp
"""

from .http_client import AsyncHttpClient
from .http_client_sync import BaseHttpClient
from .parallel import (
    ParallelExecutor,
    ParallelResult,
    batch_execute,
    gather_with_limit,
    run_parallel,
)
from .rate_limiter import AsyncRateLimiter
from .retry_utils import (
    RETRYABLE_STATUS_CODES,
    calculate_delay,
    get_retry_after,
    should_retry,
)
from .token_bucket import (
    GitHubRateLimiter,
    JiraRateLimiter,
    LinearRateLimiter,
    TokenBucketRateLimiter,
)


__all__ = [
    "RETRYABLE_STATUS_CODES",
    "AsyncHttpClient",
    "AsyncRateLimiter",
    "BaseHttpClient",
    "GitHubRateLimiter",
    "JiraRateLimiter",
    "LinearRateLimiter",
    "ParallelExecutor",
    "ParallelResult",
    "TokenBucketRateLimiter",
    "batch_execute",
    "calculate_delay",
    "gather_with_limit",
    "get_retry_after",
    "run_parallel",
    "should_retry",
]
