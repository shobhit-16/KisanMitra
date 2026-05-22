"""Dependency injection for FastAPI — DataFlow session + Redis session per request."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
from dotenv import load_dotenv
import dataflow
from dataflow import DataFlow

load_dotenv()

# Global DataFlow instance — initialized at startup
_dataflow: DataFlow | None = None
_redis_pool: redis.ConnectionPool | None = None


async def init_dataflow(database_url: str) -> DataFlow:
    """Initialize DataFlow with the given database URL."""
    global _dataflow
    _dataflow = DataFlow(database_url)
    return _dataflow


async def close_dataflow() -> None:
    """Close DataFlow connection pool."""
    global _dataflow
    if _dataflow is not None:
        await _dataflow.aclose()
        _dataflow = None


async def init_redis(redis_url: str) -> redis.ConnectionPool:
    """Initialize Redis connection pool."""
    global _redis_pool
    _redis_pool = redis.ConnectionPool.from_url(redis_url, decode_responses=True)
    return _redis_pool


async def close_redis() -> None:
    """Close Redis connection pool."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.disconnect()
        _redis_pool = None


def get_dataflow() -> DataFlow:
    """Get the DataFlow instance. Raises if not initialized."""
    if _dataflow is None:
        raise RuntimeError("DataFlow not initialized. Call init_dataflow() first.")
    return _dataflow


async def get_redis() -> redis.Redis:
    """Get a Redis client from the pool."""
    if _redis_pool is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis.Redis(connection_pool=_redis_pool)


@asynccontextmanager
async def get_redis_session() -> AsyncGenerator[redis.Redis, None]:
    """Redis session context manager per request."""
    client = await get_redis()
    try:
        yield client
    finally:
        pass  # Connection is managed by the pool
