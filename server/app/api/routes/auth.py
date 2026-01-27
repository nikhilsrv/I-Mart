import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db

logger = logging.getLogger(__name__)
from schemas.auth import (
    AuthResponse,
    GoogleAuthRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from services.auth import AuthService
from utils.cookies import set_refresh_token_cookie

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google/login", response_model=AuthResponse)
async def google_login(
    request: GoogleAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Google OAuth login for existing users.
    Frontend sends the authorization code received from Google.
    """
    logger.info("Google login attempt started")
    auth_service = AuthService(db)

    try:
        user, access_token, refresh_token = await auth_service.google_login(
            request.code
        )
    except ValueError as e:
        logger.warning("Google login failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    set_refresh_token_cookie(response, refresh_token)
    logger.info("Google login successful for user_id=%s", user.id)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
        ),
        tokens=TokenResponse(
            access_token=access_token,
        ),
    )


@router.post("/google/signup", response_model=AuthResponse)
async def google_signup(
    request: GoogleAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Google OAuth signup for new users.
    Frontend sends the authorization code received from Google.
    """
    logger.info("Google signup attempt started")
    auth_service = AuthService(db)

    try:
        user, access_token, refresh_token = await auth_service.google_signup(
            request.code
        )
    except ValueError as e:
        logger.warning("Google signup failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    set_refresh_token_cookie(response, refresh_token)
    logger.info("Google signup successful for user_id=%s", user.id)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
        ),
        tokens=TokenResponse(
            access_token=access_token,
        ),
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    """
    logger.info("Token refresh attempt started")
    auth_service = AuthService(db)

    result = await auth_service.refresh_tokens(request.refresh_token)
    if result is None:
        logger.warning("Token refresh failed: invalid or expired refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user, access_token, new_refresh_token = result

    set_refresh_token_cookie(response, new_refresh_token)
    logger.info("Token refresh successful for user_id=%s", user.id)

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
        ),
        tokens=TokenResponse(
            access_token=access_token,
        ),
    )
