"""
Authentication Router.

Provides authentication endpoints.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ohgrt_api.auth.dependencies import get_current_db_user, get_db
from ohgrt_api.auth.firebase import verify_firebase_token
from ohgrt_api.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token_type,
)
from ohgrt_api.db.models import User as DBUser
from ohgrt_api.oauth.base import delete_credential, get_credential

logger = logging.getLogger(__name__)


def get_or_create_user(db: Session, firebase_user: dict) -> DBUser:
    """Get existing user or create new one from Firebase user data."""
    user = db.query(DBUser).filter(DBUser.firebase_uid == firebase_user["uid"]).first()

    if not user:
        # Create new user
        user = DBUser(
            firebase_uid=firebase_user["uid"],
            email=firebase_user.get("email", f"{firebase_user['uid']}@firebase.local"),
            display_name=firebase_user.get("name"),
            photo_url=firebase_user.get("picture"),
            last_login_at=datetime.now(timezone.utc),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created new user: {user.id} for Firebase UID: {firebase_user['uid']}")
    else:
        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()

    return user

router = APIRouter(prefix="/auth", tags=["authentication"])

# List of OAuth provider IDs
OAUTH_PROVIDERS = ["gmail", "github", "slack", "jira", "uber"]


class ProviderStatus(BaseModel):
    """Provider connection status."""
    name: str
    connected: bool
    email: Optional[str] = None


class GoogleSignInRequest(BaseModel):
    """Request model for Google Sign-In."""

    id_token: str = Field(..., description="Firebase ID token")


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshRequest(BaseModel):
    """Request model for token refresh."""

    refresh_token: str


@router.post("/google", response_model=TokenResponse)
async def google_sign_in(
    request: GoogleSignInRequest,
    db: Session = Depends(get_db),
):
    """
    Sign in with Google via Firebase.

    Args:
        request: GoogleSignInRequest with Firebase ID token
        db: Database session

    Returns:
        TokenResponse with access and refresh tokens
    """
    # Verify Firebase token
    firebase_user = await verify_firebase_token(request.id_token)

    if not firebase_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token",
        )

    # Get or create user in database
    db_user = get_or_create_user(db, firebase_user)

    # Create JWT tokens
    token_data = {
        "sub": firebase_user["uid"],
        "email": firebase_user.get("email"),
        "name": firebase_user.get("name"),
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,  # 15 minutes in seconds
        user={
            "id": firebase_user["uid"],
            "email": firebase_user.get("email"),
            "name": firebase_user.get("name"),
            "picture": firebase_user.get("picture"),
        },
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(request: RefreshRequest):
    """
    Refresh access token using refresh token.

    Args:
        request: RefreshRequest with refresh token

    Returns:
        TokenResponse with new tokens
    """
    payload = verify_token_type(request.refresh_token, "refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Create new tokens
    token_data = {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "name": payload.get("name"),
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=15 * 60,
        user={
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "name": payload.get("name"),
        },
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint.

    Client should discard tokens. Server-side token revocation
    can be implemented with a token blacklist if needed.
    """
    return {"message": "Logged out successfully"}


class UserProfileResponse(BaseModel):
    """Response model for user profile."""

    id: str
    email: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    created_at: Optional[str] = None


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: DBUser = Depends(get_current_db_user),
):
    """
    Get the current authenticated user's profile.

    Returns:
        UserProfileResponse with user details
    """
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        display_name=current_user.display_name,
        photo_url=current_user.photo_url,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None,
    )


@router.get("/providers", response_model=List[ProviderStatus])
async def get_provider_statuses(
    current_user: DBUser = Depends(get_current_db_user),
    db: Session = Depends(get_db),
):
    """
    Get connection status for all OAuth providers.

    Returns a list of providers with their connection status.
    """
    statuses = []
    for provider in OAUTH_PROVIDERS:
        credential = get_credential(db, current_user.id, provider)
        if credential:
            statuses.append(ProviderStatus(
                name=provider,
                connected=True,
                email=credential.config.get("email") if credential.config else None,
            ))
        else:
            statuses.append(ProviderStatus(
                name=provider,
                connected=False,
            ))
    return statuses


@router.delete("/providers/{provider}")
async def disconnect_provider(
    provider: str,
    current_user: DBUser = Depends(get_current_db_user),
    db: Session = Depends(get_db),
):
    """
    Disconnect an OAuth provider.
    """
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown provider: {provider}",
        )

    deleted = delete_credential(db, current_user.id, provider)
    if deleted:
        logger.info(f"Provider {provider} disconnected for user {current_user.id}")
        return {"success": True, "message": f"{provider} disconnected"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{provider} not connected",
    )
