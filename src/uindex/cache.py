"""SQLite-based cache with TTL support."""

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class Cache:
    """Simple key-value cache backed by SQLite."""

    DEFAULT_TTL = 7 * 24 * 60 * 60  # 7 days in seconds

    def __init__(self, db_path: Path, ttl_seconds: int | None = None):
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)

    def get(self, key: str) -> Any | None:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value, created_at FROM cache WHERE key = ?",
                (key,)
            ).fetchone()

        if row is None:
            return None

        value, created_at = row
        if time.time() - created_at > self.ttl_seconds:
            self.delete(key)
            return None

        return json.loads(value)

    def set(self, key: str, value: Any) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (key, value, created_at)
                VALUES (?, ?, ?)
                """,
                (key, json.dumps(value), time.time())
            )

    def delete(self, key: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))
