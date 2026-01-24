from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.session import get_db
from schemas.auth import (
    AuthResponse,
    GoogleLoginRequest,
    GoogleSignupRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from services.auth import AuthService
from utils.cookies import set_refresh_token_cookie

router = APIRouter(prefix="/auth", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


@router.get("/google/login")
async def google_login():
    """
    Redirect to Google OAuth login page for existing users.
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": "login",
    }
    google_auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=google_auth_url)


@router.get("/google/signup")
async def google_signup():
    """
    Redirect to Google OAuth page for new user registration.
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": "signup",
    }
    google_auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Google OAuth callback.
    This endpoint is called by Google after user authorizes.
    Behavior depends on state: 'login' for existing users, 'signup' for new users.
    """
    if state not in ("login", "signup"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter",
        )

    auth_service = AuthService(db)

    try:
        if state == "login":
            user, access_token, refresh_token = await auth_service.google_login(code)
        else:
            user, access_token, refresh_token = await auth_service.google_signup(code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    set_refresh_token_cookie(response, refresh_token)

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
    auth_service = AuthService(db)

    result = await auth_service.refresh_tokens(request.refresh_token)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user, access_token, new_refresh_token = result

    set_refresh_token_cookie(response, new_refresh_token)

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
