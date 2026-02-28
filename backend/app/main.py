"""
KlyrSignals Backend - FastAPI Application
AI-powered financial portfolio analyst
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.api.v1 import portfolio, analysis, market, health

# Create FastAPI app
app = FastAPI(
    title="KlyrSignals API",
    description="AI-powered financial portfolio analyst API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://klyrsignals.vercel.app",  # Production (update when deployed)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(portfolio.router)
app.include_router(analysis.router)
app.include_router(market.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to KlyrSignals API",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
