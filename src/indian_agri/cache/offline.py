"""Offline-first cache layer using local SQLite.

Per specs/01-domain-model.md §9.3, all entities must be storable
in a local SQLite cache on the mobile device for offline access.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..models.base import OfflineMixin

# Default path for local cache
DEFAULT_CACHE_PATH = Path.home() / ".indian_agri" / "offline_cache.db"


class OfflineCache:
    """Local SQLite cache for offline-first entity storage.

    Uses last-write-wins conflict resolution per pilot design
    (specs/15-ground-challenges-practical-feasibility.md §Challenge 1).
    """

    def __init__(self, db_path: Path | str = DEFAULT_CACHE_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._init_schema()
        return self._conn

    def _init_schema(self) -> None:
        conn = self._conn
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entity_cache (
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                data TEXT NOT NULL,
                sync_status TEXT NOT NULL DEFAULT 'pending',
                updated_at TEXT NOT NULL,
                PRIMARY KEY (entity_type, entity_id)
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sync_status
            ON entity_cache(sync_status)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                operation TEXT NOT NULL,
                payload TEXT NOT NULL,
                queued_at TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0
            )
        """)
        conn.commit()

    # ── Entity CRUD ────────────────────────────────────────────────

    def save(self, entity: OfflineMixin, entity_type: str) -> None:
        """Save entity to local cache."""
        conn = self._get_conn()
        data = entity.to_dict()
        entity_id = data.pop("id")
        sync_status = data.pop("_sync_status", "pending")
        data_json = json.dumps(data, default=str)
        now = datetime.utcnow().isoformat()
        conn.execute(
            """
            INSERT OR REPLACE INTO entity_cache
                (entity_type, entity_id, data, sync_status, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (entity_type, entity_id, data_json, sync_status, now),
        )
        conn.commit()

    def get(self, entity_type: str, entity_id: int) -> Optional[dict[str, Any]]:
        """Retrieve entity from local cache."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT data, sync_status FROM entity_cache WHERE entity_type=? AND entity_id=?",
            (entity_type, entity_id),
        ).fetchone()
        if row is None:
            return None
        data = json.loads(row["data"])
        data["_sync_status"] = row["sync_status"]
        return data

    def get_all(self, entity_type: str) -> list[dict[str, Any]]:
        """Retrieve all entities of a type from local cache."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT entity_id, data, sync_status FROM entity_cache WHERE entity_type=?",
            (entity_type,),
        ).fetchall()
        results = []
        for row in rows:
            data = json.loads(row["data"])
            data["_sync_status"] = row["sync_status"]
            results.append(data)
        return results

    def delete(self, entity_type: str, entity_id: int) -> None:
        """Delete entity from local cache."""
        conn = self._get_conn()
        conn.execute(
            "DELETE FROM entity_cache WHERE entity_type=? AND entity_id=?",
            (entity_type, entity_id),
        )
        conn.commit()

    # ── Sync Queue ──────────────────────────────────────────────────

    def queue_sync(
        self, entity_type: str, entity_id: int, operation: str, payload: dict[str, Any]
    ) -> None:
        """Add entity operation to the sync queue."""
        conn = self._get_conn()
        now = datetime.utcnow().isoformat()
        conn.execute(
            """
            INSERT INTO sync_queue (entity_type, entity_id, operation, payload, queued_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (entity_type, entity_id, operation, json.dumps(payload, default=str), now),
        )
        conn.commit()

    def get_pending_syncs(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get pending sync operations, oldest first."""
        conn = self._get_conn()
        rows = conn.execute(
            """
            SELECT id, entity_type, entity_id, operation, payload, queued_at, retry_count
            FROM sync_queue
            ORDER BY queued_at ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]

    def mark_sync_complete(self, sync_id: int) -> None:
        """Remove a sync operation from the queue on success."""
        conn = self._get_conn()
        conn.execute("DELETE FROM sync_queue WHERE id=?", (sync_id,))
        conn.commit()

    def increment_retry(self, sync_id: int) -> None:
        """Increment retry count for a failed sync operation."""
        conn = self._get_conn()
        conn.execute(
            "UPDATE sync_queue SET retry_count = retry_count + 1 WHERE id=?",
            (sync_id,),
        )
        conn.commit()

    def get_pending_count(self) -> int:
        """Return count of pending sync operations."""
        conn = self._get_conn()
        row = conn.execute("SELECT COUNT(*) as c FROM sync_queue").fetchone()
        return row["c"] if row else 0

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
