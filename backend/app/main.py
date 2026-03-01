"""
KlyrSignals Backend - FastAPI Application
AI-powered financial portfolio analyst
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from app.services.database import connect_db, disconnect_db
from app.api.v1 import auth, users, portfolio, analysis, market, health, migration, oauth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    yield
    # Shutdown
    await disconnect_db()

# Create FastAPI app
app = FastAPI(
    title="KlyrSignals API",
    description="AI-powered financial portfolio analyst API",
    version="1.6.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://klyrsignals.com",  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(migration.router, prefix="/api/v1/migrate", tags=["migration"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["oauth"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to KlyrSignals API v1.6",
        "version": "1.6.0",
        "docs": "/docs",
        "auth_required": True,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
