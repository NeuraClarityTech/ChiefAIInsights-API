# backend/main.py
"""
ChiefAI Insights API - Main Application
FastAPI application with authentication and enterprise integrations
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.connection import init_connection_pool, close_connection_pool
from api.routes import router as api_router
from api.auth_routes import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for application startup and shutdown"""
    # Startup
    print("🚀 Starting ChiefAI Insights API...")
    init_connection_pool()
    print("✅ Application started successfully!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down ChiefAI Insights API...")
    close_connection_pool()
    print("✅ Application shutdown complete!")

# Create FastAPI application
app = FastAPI(
    title="ChiefAI Insights API",
    description="Enterprise intelligence platform with prescriptive AI insights",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://neuraclaritytech.com",
        "https://www.neuraclaritytech.com",
        "https://chiefaiinsights.com",
        "https://www.chiefaiinsights.com",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
def root():
