# backend/utils/auth.py
"""
Authentication utilities for ChiefAI Insights
Handles JWT tokens, password hashing, and authentication logic
"""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from psycopg2.extras import RealDictCursor

from database.connection import get_db
from models.user import TokenData, UserInDB

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_by_email(email: str, db) -> Optional[UserInDB]:
    """Get user by email from database"""
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        SELECT id, name, email, password_hash, company_name, role, 
               is_verified, is_active, created_at, last_login, updated_at
        FROM users WHERE email = %s
        """,
        (email,)
    )
    user_data = cursor.fetchone()
    cursor.close()
    
    if user_data:
        return UserInDB(**dict(user_data))
    return None

def get_user_by_id(user_id: str, db) -> Optional[UserInDB]:
    """Get user by ID from database"""
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        SELECT id, name, email, password_hash, company_name, role, 
               is_verified, is_active, created_at, last_login, updated_at
        FROM users WHERE id = %s
        """,
        (user_id,)
    )
    user_data = cursor.fetchone()
    cursor.close()
    
    if user_data:
        return UserInDB(**dict(user_data))
    return None

def authenticate_user(email: str, password: str, db) -> Optional[UserInDB]:
    """Authenticate user with email and password"""
    user = get_user_by_email(email, db)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

def update_last_login(user_id: str, db):
    """Update user's last login timestamp"""
    cursor = db.cursor()
    cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user_id,))
    cursor.close()
    db.commit()

def store_refresh_token(user_id: str, token: str, db):
    """Store refresh token in database"""
    cursor = db.cursor()
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    cursor.execute(
        "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
        (user_id, token, expires_at)
    )
    cursor.close()
    db.commit()

def validate_refresh_token(token: str, db) -> Optional[str]:
    """Validate refresh token and return user_id if valid"""
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT user_id, expires_at, is_revoked FROM refresh_tokens WHERE token = %s",
        (token,)
    )
    token_data = cursor.fetchone()
    cursor.close()
    
    if not token_data or token_data['is_revoked'] or token_data['expires_at'] < datetime.utcnow():
        return None
    return token_data['user_id']

def revoke_refresh_token(token: str, db):
    """Revoke a refresh token"""
    cursor = db.cursor()
    cursor.execute("UPDATE refresh_tokens SET is_revoked = TRUE WHERE token = %s", (token,))
    cursor.close()
    db.commit()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
) -> UserInDB:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    token_data = decode_token(token)
    user = get_user_by_id(token_data.user_id, db)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

async def require_admin(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
