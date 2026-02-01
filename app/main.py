"""KlyrSignals FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.config import settings
from app.database import engine
from app.routes import users, connections, accounts, positions, analysis, health

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle."""
    logger.info("klyrsignals_starting", ai_provider=settings.ai_provider)
    yield
    await engine.dispose()
    logger.info("klyrsignals_shutdown")


app = FastAPI(
    title="KlyrSignals",
    description="Net worth & investment blind-spot analysis",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, tags=["health"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(connections.router, prefix="/api/v1/connections", tags=["connections"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["accounts"])
app.include_router(positions.router, prefix="/api/v1/positions", tags=["positions"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
