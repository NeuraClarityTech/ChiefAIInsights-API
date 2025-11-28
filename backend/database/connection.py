# backend/database/connection.py
"""
Database connection management for ChiefAI Insights
Handles PostgreSQL connection to Supabase with connection pooling
"""

import os
from typing import Generator
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

# Database connection pool
connection_pool = None

def init_connection_pool():
    """Initialize database connection pool"""
    global connection_pool
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=database_url
        )
        print("✅ Database connection pool initialized")
    except Exception as e:
        print(f"❌ Error initializing connection pool: {e}")
        raise

def get_db_connection():
    """
    Get a database connection from the pool
    """
    global connection_pool
    
    if connection_pool is None:
        init_connection_pool()
    
    try:
        connection = connection_pool.getconn()
        return connection
    except Exception as e:
        print(f"❌ Error getting connection: {e}")
        raise

def release_db_connection(connection):
    """Return a connection to the pool"""
    global connection_pool
    
    if connection_pool and connection:
        connection_pool.putconn(connection)

def get_db() -> Generator:
    """
    Dependency for FastAPI endpoints
    """
    connection = get_db_connection()
    try:
        yield connection
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise
    finally:
        release_db_connection(connection)

def close_connection_pool():
    """Close all connections in the pool"""
    global connection_pool
    
    if connection_pool:
        connection_pool.closeall()
        print("✅ Database connection pool closed")
