# backend/models/user.py
"""
User models for authentication and data validation
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re

# Request Models (Input)

class UserRegister(BaseModel):
    """User registration request"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    company_name: Optional[str] = Field(None, max_length=200)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate name format"""
        if not re.match(r'^[a-zA-Z\s\-\']+$', v):
            raise ValueError('Name can only contain letters, spaces, hyphens, and apostrophes')
        return v.strip()

class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str

class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

# Response Models (Output)

class Token(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    email: Optional[str] = None

class UserResponse(BaseModel):
    """User data response (safe - no password)"""
    id: str
    name: str
    email: str
    company_name: Optional[str] = None
    role: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserInDB(BaseModel):
    """User data in database (includes password hash)"""
    id: str
    name: str
    email: str
    password_hash: str
    company_name: Optional[str] = None
    role: str = "user"
    is_verified: bool = False
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    updated_at: datetime

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
