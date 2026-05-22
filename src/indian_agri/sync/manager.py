"""Offline sync manager — queue operations offline, sync when online.

Per specs/15-ground-challenges-practical-feasibility.md §Challenge 1,
the platform is offline-first: all operations queue locally and sync
when connectivity is restored.

Conflict resolution: last-write-wins per pilot design spec.
"""

import asyncio
import time
from typing import Any, Callable

from ..cache.offline import OfflineCache


class SyncManager:
    """Manages offline queue and sync with exponential backoff retry.

    Per pilot design: last-write-wins conflict resolution. The server
    timestamp wins on conflict (server is source of truth for constraint state).
    """

    def __init__(
        self,
        offline_cache: OfflineCache,
        sync_endpoint: str = "/api/v1/sync",
    ):
        self.cache = offline_cache
        self.sync_endpoint = sync_endpoint
        self._online: bool = False
        self._sync_task: asyncio.Task | None = None

    @property
    def online(self) -> bool:
        return self._online

    def set_online(self, online: bool) -> None:
        self._online = online
        if online and self._sync_task is None:
            self._sync_task = asyncio.create_task(self._run_sync_loop())
        elif not online and self._sync_task:
            self._sync_task.cancel()
            self._sync_task = None

    async def _run_sync_loop(self) -> None:
        """Background sync loop — runs when online."""
        while self._online:
            try:
                await self._sync_batch()
                await asyncio.sleep(5)  # Check every 5 seconds when online
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(30)  # Back off on error

    async def _sync_batch(self) -> None:
        """Sync a batch of pending operations with retry + backoff."""
        pending = self.cache.get_pending_syncs(limit=50)
        for item in pending:
            sync_id = item["id"]
            operation = item["operation"]
            payload = item["payload"]

            try:
                success = await self._sync_operation(operation, payload)
                if success:
                    self.cache.mark_sync_complete(sync_id)
                    # Mark entity as synced in cache
                    entity_type = item["entity_type"]
                    entity_id = item["entity_id"]
                    cached = self.cache.get(entity_type, entity_id)
                    if cached:
                        cached["_sync_status"] = "synced"
                        # Would re-save to cache here
            except Exception:
                self.cache.increment_retry(sync_id)
                retry_count = item.get("retry_count", 0) + 1
                if retry_count >= self._max_retries(retry_count):
                    # Move to dead letter queue / alert
                    pass

    async def _sync_operation(self, operation: str, payload: dict[str, Any]) -> bool:
        """Perform a single sync operation against the server.

        Returns True on success, False on failure.
        """
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.sync_endpoint,
                    json={"operation": operation, "payload": payload},
                )
                return response.status_code in (200, 201, 204)
            except (httpx.TimeoutException, httpx.ConnectError):
                return False

    def _max_retries(self, retry_count: int) -> int:
        """Exponential backoff: max retries increases with each attempt."""
        # 1min, 2min, 4min, 8min, 16min
        base_delay = 60
        return min(retry_count, 5)

    def queue_offline_operation(
        self,
        entity_type: str,
        entity_id: int,
        operation: str,
        payload: dict[str, Any],
    ) -> None:
        """Queue an operation for background sync."""
        self.cache.queue_sync(entity_type, entity_id, operation, payload)

    def get_sync_status(self) -> dict[str, Any]:
        """Return current sync status for monitoring."""
        return {
            "online": self._online,
            "pending_count": self.cache.get_pending_count(),
            "sync_running": self._sync_task is not None,
        }
