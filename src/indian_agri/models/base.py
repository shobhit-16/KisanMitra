from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class OfflineMixin(BaseModel):
    """Base mixin for all entities — enables offline-first local SQLite cache.

    Every entity implements to_dict() / from_dict() for local storage
    and remote sync. Sync status is tracked per entity.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: Optional[int] = None
    created_at: datetime = None
    updated_at: datetime = None
    _sync_status: str = "pending"  # pending | synced | conflict

    def to_dict(self) -> dict[str, Any]:
        """Serialize for local SQLite cache / JSON storage."""
        data = self.model_dump(mode="json")
        data["_sync_status"] = self._sync_status
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OfflineMixin":
        """Deserialize from local cache / JSON storage."""
        sync_status = data.pop("_sync_status", "pending")
        instance = cls.model_validate(data)
        instance._sync_status = sync_status
        return instance

    def mark_synced(self) -> None:
        self._sync_status = "synced"
        self.updated_at = datetime.utcnow()

    def mark_pending(self) -> None:
        self._sync_status = "pending"
        self.updated_at = datetime.utcnow()

    def mark_conflict(self) -> None:
        self._sync_status = "conflict"
        self.updated_at = datetime.utcnow()
