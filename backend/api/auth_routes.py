# backend/api/auth_routes.py
"""
Authentication API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
from datetime import timedelta
import uuid

from database.connection import get_db
from models.user import UserRegister, UserLogin, UserResponse, Token, MessageResponse, TokenRefresh
from utils.auth import (
    hash_password, authenticate_user, create_access_token, create_refresh_token,
    get_current_user, store_refresh_token, validate_refresh_token, 
    revoke_refresh_token, update_last_login, get_user_by_email, 
    get_user_by_id, UserInDB, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db = Depends(get_db)):
    """Register a new user"""
    existing_user = get_user_by_email(user_data.email, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    password_hash = hash_password(user_data.password)
    cursor = db.cursor(cursor_factory=RealDictCursor)
    user_id = str(uuid.uuid4())
    
    cursor.execute(
        """
        INSERT INTO users (id, name, email, password_hash, company_name, role, is_verified, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, name, email, company_name, role, is_verified, is_active, created_at, last_login
        """,
        (user_id, user_data.name, user_data.email, password_hash, 
         user_data.company_name, "user", False, True)
    )
    
    new_user = cursor.fetchone()
    cursor.close()
    db.commit()
    
    return UserResponse(**dict(new_user))

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db = Depends(get_db)):
    """Login with email and password"""
    user = authenticate_user(user_credentials.email, user_credentials.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    
    update_last_login(user.id, db)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})
    store_refresh_token(user.id, refresh_token, db)
    
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenRefresh, db = Depends(get_db)):
    """Refresh access token"""
    user_id = validate_refresh_token(token_data.refresh_token, db)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(user_id, db)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    new_refresh_token = create_refresh_token(data={"sub": user.id, "email": user.email})
    revoke_refresh_token(token_data.refresh_token, db)
    store_refresh_token(user.id, new_refresh_token, db)
    
    return Token(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")

@router.post("/logout", response_model=MessageResponse)
def logout(token_data: TokenRefresh, db = Depends(get_db)):
    """Logout user"""
    revoke_refresh_token(token_data.refresh_token, db)
    return MessageResponse(message="Successfully logged out", success=True)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """Get current user's profile"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        company_name=current_user.company_name,
        role=current_user.role,
        is_verified=current_user.is_verified,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.get("/verify-token", response_model=MessageResponse)
def verify_token(current_user: UserInDB = Depends(get_current_user)):
    """Verify if token is valid"""
    return MessageResponse(message="Token is valid", success=True)
