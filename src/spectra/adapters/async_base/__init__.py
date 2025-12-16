"""
Async Base - Asyncio-compatible HTTP client infrastructure.

This module provides the foundation for parallel API calls using asyncio:
- AsyncRateLimiter: Async-compatible token bucket rate limiter
- AsyncHttpClient: Base async HTTP client with retry and rate limiting
- Parallel execution utilities for batch operations

Requires aiohttp: pip install aiohttp
"""

from .http_client import AsyncHttpClient
from .parallel import (
    ParallelExecutor,
    ParallelResult,
    batch_execute,
    gather_with_limit,
    run_parallel,
)
from .rate_limiter import AsyncRateLimiter


__all__ = [
    "AsyncHttpClient",
    "AsyncRateLimiter",
    "ParallelExecutor",
    "ParallelResult",
    "batch_execute",
    "gather_with_limit",
    "run_parallel",
]
