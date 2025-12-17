"""
Cache Module - Caching layer for API responses.

Provides caching to reduce API calls and improve performance:
- CacheBackend: Abstract interface for cache storage
- MemoryCache: In-memory LRU cache with TTL support
- FileCache: File-based persistent cache
- CacheManager: High-level cache management

Example:
    >>> from spectra.adapters.cache import MemoryCache, CachedClient
    >>>
    >>> cache = MemoryCache(max_size=1000, default_ttl=300)
    >>> client = CachedClient(jira_client, cache)
    >>>
    >>> # First call hits API
    >>> issue = client.get_issue("PROJ-123")
    >>>
    >>> # Second call uses cache
    >>> issue = client.get_issue("PROJ-123")
"""

from .backend import CacheBackend, CacheEntry, CacheStats
from .file_cache import FileCache
from .keys import CacheKeyBuilder
from .manager import CacheManager
from .memory import MemoryCache


__all__ = [
    "CacheBackend",
    "CacheEntry",
    "CacheKeyBuilder",
    "CacheManager",
    "CacheStats",
    "FileCache",
    "MemoryCache",
]
