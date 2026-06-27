"""Real SQLite connection pool with fixed max size — exhaustion is genuine."""
from __future__ import annotations

import sqlite3
import threading
import time
from contextlib import contextmanager
from queue import Empty, Full, Queue
from typing import Generator


class ConnectionPoolExhausted(Exception):
    """Raised when no connections are available in the pool."""


class PaymentConnectionPool:
    def __init__(self, db_path: str, max_size: int = 3):
        self.db_path = db_path
        self.max_size = max_size
        self._pool: Queue = Queue(maxsize=max_size)
        self._lock = threading.RLock()
        self._initialized = False
        self._held_connections: set = set()

    def _init_db(self) -> None:
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)
            conn.commit()
            conn.close()
            for _ in range(self.max_size):
                self._pool.put(self._create_connection())
            self._initialized = True

    def _create_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def acquire(self, timeout: float = 2.0) -> Generator[sqlite3.Connection, None, None]:
        self._init_db()
        conn = None
        try:
            conn = self._pool.get(timeout=timeout)
            self._held_connections.add(id(conn))
            yield conn
        except Empty:
            raise ConnectionPoolExhausted(
                f"Payment DB pool exhausted (max={self.max_size}). "
                f"Held: {len(self._held_connections)}"
            )
        finally:
            if conn is not None:
                self._held_connections.discard(id(conn))
                try:
                    self._pool.put_nowait(conn)
                except Full:
                    conn.close()

    def hold_connection(self, duration: float = 30.0) -> sqlite3.Connection:
        """Load generator: hold a connection open to exhaust the pool."""
        self._init_db()
        try:
            conn = self._pool.get(timeout=2.0)
            self._held_connections.add(id(conn))
            return conn
        except Empty:
            raise ConnectionPoolExhausted("Cannot hold — pool already exhausted")

    def release_held(self, conn: sqlite3.Connection) -> None:
        self._held_connections.discard(id(conn))
        try:
            self._pool.put_nowait(conn)
        except Full:
            conn.close()

    def reset(self) -> None:
        """Close all connections and recreate the pool."""
        with self._lock:
            while not self._pool.empty():
                try:
                    c = self._pool.get_nowait()
                    c.close()
                except Empty:
                    break
            self._held_connections.clear()
            self._initialized = False
            self._pool = Queue(maxsize=self.max_size)
            self._init_db()

    def stats(self) -> dict:
        return {
            "max_size": self.max_size,
            "available": self._pool.qsize(),
            "held": len(self._held_connections),
        }

    def recover_if_stale(self) -> None:
        """Restore pool when connections were leaked (available=0, nothing held)."""
        if self._initialized and self._pool.qsize() == 0 and not self._held_connections and not _load_held:
            self.reset()


# Global pool instance
_pool: PaymentConnectionPool | None = None
_load_held: list[sqlite3.Connection] = []


def get_pool(db_path: str = "payment.db") -> PaymentConnectionPool:
    global _pool
    if _pool is None:
        _pool = PaymentConnectionPool(db_path, max_size=3)
    _pool.recover_if_stale()
    return _pool


def get_load_held() -> list:
    return _load_held


def release_all_held(db_path: str = "payment.db") -> int:
    """Close load-generator held connections and restore the pool."""
    global _load_held
    released = len(_load_held)
    for conn in list(_load_held):
        try:
            conn.close()
        except Exception:
            pass
    _load_held.clear()
    if _pool:
        _pool.reset()
    return released


def reset_pool(db_path: str = "payment.db") -> None:
    release_all_held(db_path)
