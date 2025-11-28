# backend/api/routes.py
"""
Legacy API routes - temporarily simplified for authentication deployment
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health():
    """Legacy health check endpoint"""
    return {"status": "healthy"}

@router.get("/test")
def test():
    """Test endpoint"""
    return {"message": "Legacy API routes operational"}
