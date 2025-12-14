"""
Async Base - Asyncio-compatible HTTP client infrastructure.

This module provides the foundation for parallel API calls using asyncio:
- AsyncRateLimiter: Async-compatible token bucket rate limiter
- AsyncHttpClient: Base async HTTP client with retry and rate limiting
- Parallel execution utilities for batch operations

Requires aiohttp: pip install aiohttp
"""

from .rate_limiter import AsyncRateLimiter
from .http_client import AsyncHttpClient
from .parallel import (
    gather_with_limit,
    batch_execute,
    run_parallel,
    ParallelResult,
    ParallelExecutor,
)

__all__ = [
    "AsyncRateLimiter",
    "AsyncHttpClient",
    "gather_with_limit",
    "batch_execute",
    "run_parallel",
    "ParallelResult",
    "ParallelExecutor",
]

