"""Recommendation Bus — in-memory pub/sub per specs/09-constraint-priority-engine.md §4.

Phase 1: in-memory only. Engines publish recommendations; CPE subscribes and evaluates.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Awaitable, Callable

from .types import Recommendation


# Subscriber callback type
RecommendationSubscriber = Callable[[Recommendation], Awaitable[None]]


@dataclass
class RecommendationBus:
    """In-memory pub/sub for recommendations.

    Engines call `publish()` to send recommendations.
    CPE calls `subscribe()` to receive them for evaluation.

    Phase 1: single-process, in-memory only.
    """

    _subscriptions: list[RecommendationSubscriber] = field(default_factory=list)
    _published: list[Recommendation] = field(default_factory=list)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def subscribe(self, callback: RecommendationSubscriber) -> None:
        """Register a subscriber to receive all published recommendations."""
        self._subscriptions.append(callback)

    async def publish(self, recommendation: Recommendation) -> None:
        """Publish a recommendation to all subscribers."""
        async with self._lock:
            self._published.append(recommendation)

        # Deliver to all subscribers
        for callback in self._subscriptions:
            try:
                await callback(recommendation)
            except Exception:
                # Subscriber errors don't block other subscribers
                pass

    def get_all(self) -> list[Recommendation]:
        """Get all published recommendations (for re-evaluation)."""
        return list(self._published)

    def clear(self) -> None:
        """Clear all published recommendations (after CPE evaluation cycle)."""
        self._published.clear()


# Global bus instance — single bus per process in Phase 1
_global_bus: RecommendationBus | None = None


def get_recommendation_bus() -> RecommendationBus:
    """Get the global RecommendationBus instance."""
    global _global_bus
    if _global_bus is None:
        _global_bus = RecommendationBus()
    return _global_bus
