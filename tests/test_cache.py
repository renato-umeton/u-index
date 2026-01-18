"""Tests for SQLite-based cache with TTL support."""

import time
from pathlib import Path
from uindex.cache import Cache


def test_cache_set_and_get(tmp_path):
    """Cache stores and retrieves values."""
    cache = Cache(tmp_path / "test.db")
    cache.set("key1", {"data": "value"})
    assert cache.get("key1") == {"data": "value"}


def test_cache_miss(tmp_path):
    """Cache returns None for missing keys."""
    cache = Cache(tmp_path / "test.db")
    assert cache.get("nonexistent") is None


def test_cache_expiry(tmp_path):
    """Cache returns None for expired entries."""
    cache = Cache(tmp_path / "test.db", ttl_seconds=1)
    cache.set("key1", {"data": "value"})
    time.sleep(1.1)
    assert cache.get("key1") is None


def test_cache_overwrite(tmp_path):
    """Cache overwrites existing values."""
    cache = Cache(tmp_path / "test.db")
    cache.set("key1", {"old": "data"})
    cache.set("key1", {"new": "data"})
    assert cache.get("key1") == {"new": "data"}
