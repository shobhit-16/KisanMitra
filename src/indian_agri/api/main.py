"""FastAPI application — Indian Agri Digital Product.

Per specs/06-delivery-channels.md §offline-first, the API is designed
for offline-capable mobile clients. All write operations return immediately
and queue for background sync.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .deps import close_dataflow, close_redis, init_dataflow, init_redis

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown events."""
    import os

    database_url = os.environ.get(
        "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/indian_agri"
    )
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    await init_dataflow(database_url)
    await init_redis(redis_url)

    yield

    await close_redis()
    await close_dataflow()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Indian Agri Digital Product",
        description=(
            "Voice-first, offline-capable agricultural advisory platform. "
            "Delivers personalized recommendations via IVR, WhatsApp, and USSD."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — allow mobile app clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check():
        """Health endpoint for load balancers and monitoring."""
        return {
            "status": "healthy",
            "service": "indian-agri-digital-product",
            "version": "0.1.0",
        }

    @app.get("/health/ready")
    async def readiness_check():
        """Readiness check — verifies DB and Redis connectivity."""
        from .deps import get_dataflow, get_redis

        try:
            df = get_dataflow()
            # DataFlow health check
            await df.execute("SELECT 1")
        except Exception as e:
            return {"status": "not_ready", "database": str(e)}

        try:
            redis_client = await get_redis()
            await redis_client.ping()
        except Exception as e:
            return {"status": "not_ready", "redis": str(e)}

        return {"status": "ready", "database": "ok", "redis": "ok"}

    return app


app = create_app()
