from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.database.connection import init_db, close_db
from backend.api.auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting ChiefAI Insights API...")
    await init_db()
    print("✅ Database connection pool initialized")
    yield
    print("👋 Shutting down ChiefAI Insights API...")
    await close_db()
    print("✅ Database connections closed")


app = FastAPI(
    title="ChiefAI Insights API",
    description="Executive Intelligence Platform - Now with Authentication",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])


@app.get("/")
async def root():
    return {
        "message": "ChiefAI Insights API v2.0",
        "status": "online",
        "features": ["authentication", "jwt_tokens", "user_management"],
        "endpoints": {
            "docs": "/docs",
            "auth": "/api/auth/*"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "authentication": "enabled"
    }
