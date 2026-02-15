"""
Admin Authentication Module
Simple JWT-based authentication for admin dashboard
"""

from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, Header
from pydantic import BaseModel


# Configuration (move to environment variables in production)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # CHANGE THIS!
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_at: str
    user: dict


class AdminUser(BaseModel):
    username: str
    role: str = "admin"


def verify_password(username: str, password: str) -> bool:
    """
    Verify admin credentials.
    In production, use proper password hashing (bcrypt, argon2).
    """
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def create_access_token(username: str) -> tuple[str, datetime]:
    """Create JWT access token."""
    expires_at = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)

    payload = {
        "sub": username,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc),
        "role": "admin",
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expires_at


def verify_token(token: str) -> Optional[AdminUser]:
    """Verify JWT token and return user info."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role", "admin")

        if username is None:
            return None

        return AdminUser(username=username, role=role)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_admin(authorization: str = Header(None)) -> AdminUser:
    """
    Dependency to protect admin routes.
    Usage: user: AdminUser = Depends(require_admin)
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Use: Bearer <token>",
        )

    token = parts[1]
    user = verify_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user


# Audit log helper
def log_admin_action(user: AdminUser, action: str, details: dict = None):
    """Log admin actions for audit trail."""
    # In production, save to database
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": user.username,
        "action": action,
        "details": details or {},
    }
    # TODO: Save to database table admin_audit_logs
    print(f"[AUDIT] {log_entry}")
    return log_entry
