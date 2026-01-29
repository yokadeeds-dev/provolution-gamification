# main.py - FastAPI Application Entry Point
"""
Provolution Gamification API
============================

The REST API backend for the Provolution Climate Gamification System.

Run with:
    uvicorn app.main:app --reload --port 8000

Or in production:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import os

from .database import check_database_health
from .routers import (
    auth_router,
    users_router,
    challenges_router,
    leaderboards_router,
    badges_router,
    rewards_router
)
from .routers.footprint import router as footprint_router
from .routers.google_auth import router as google_auth_router


# App metadata
API_VERSION = "1.0.0"
API_TITLE = "Provolution Gamification API"
API_DESCRIPTION = """
## 🌍 Provolution Climate Gamification System

Engage users in climate action through challenges, badges, and rewards.

### Features
- **Challenges**: Join and complete climate-action challenges
- **Progress Tracking**: Log daily activities and track progress  
- **Leaderboards**: Compete with others in CO₂ savings
- **Badges**: Earn badges for achievements
- **Hardware Rewards**: Redeem XP for eco-friendly hardware
- **CO₂ Footprint Calculator**: Calculate your personal carbon footprint

### Authentication
Most endpoints require JWT Bearer token authentication.
Obtain a token via `/auth/login` or `/auth/register`.

### Deployment
Hosted on Render.com | Frontend: Netlify
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("[START] Starting Provolution Gamification API...")
    print(f"[ENV] Running in {'production' if os.environ.get('RENDER') else 'development'} mode")
    
    health = check_database_health()
    if health['status'] == 'healthy':
        print(f"[OK] Database connected: {health['challenges_count']} challenges, {health['users_count']} users")
    else:
        print(f"[WARN] Database issue: {health.get('error', 'unknown')}")
    
    yield
    
    # Shutdown
    print("[STOP] Shutting down Provolution API...")


# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# CORS middleware - configured for local dev and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local development
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        # Production domains
        "https://provolution.org",
        "https://www.provolution.org",
        "https://app.provolution.org",
        # Netlify deployments
        "https://provolution-landing.netlify.app",
        "https://provolution-gamification.netlify.app",
    ],
    # Allow all Render.com subdomains
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2)) + "ms"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions gracefully."""
    # In production, don't expose error details
    if os.environ.get('RENDER'):
        message = "Ein unerwarteter Fehler ist aufgetreten"
    else:
        message = str(exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": message
            }
        }
    )


# Include routers
app.include_router(auth_router, prefix="/v1")
app.include_router(users_router, prefix="/v1")
app.include_router(challenges_router, prefix="/v1")
app.include_router(leaderboards_router, prefix="/v1")
app.include_router(badges_router, prefix="/v1")
app.include_router(rewards_router, prefix="/v1")
app.include_router(footprint_router, prefix="/v1")
app.include_router(google_auth_router, prefix="/v1")


# Root endpoint
@app.get("/", tags=["Status"])
def root():
    """API root - basic info."""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "docs": "/docs",
        "health": "/health",
        "environment": "production" if os.environ.get('RENDER') else "development"
    }


# Health check endpoint
@app.get("/health", tags=["Status"])
def health_check():
    """
    Health check endpoint for monitoring.
    Returns database status and basic stats.
    """
    db_health = check_database_health()
    
    return {
        "status": "ok" if db_health['status'] == 'healthy' else 'degraded',
        "version": API_VERSION,
        "database": db_health
    }


# API info endpoint
@app.get("/v1", tags=["Status"])
def api_v1_info():
    """API v1 information."""
    return {
        "version": "1.0",
        "endpoints": {
            "auth": "/v1/auth",
            "users": "/v1/users",
            "challenges": "/v1/challenges",
            "leaderboards": "/v1/leaderboards",
            "badges": "/v1/badges",
            "rewards": "/v1/rewards",
            "footprint": "/v1/footprint"
        }
    }
