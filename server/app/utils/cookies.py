from fastapi import Response
from core.config import settings

def set_refresh_token_cookie(response: Response, token: str) -> None:
    """Set refresh token as an HTTP-only cookie."""
    response.set_cookie(
        key="refresh_token",
        value=token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=settings.APP_ENV == "production",
        secure=settings.APP_ENV == "production",
        samesite="lax",
    )



def clear_auth_cookies(response: Response) -> None:
    """Clear authentication cookies."""
    response.delete_cookie(
        key="refresh_token",
        httponly=settings.APP_ENV == "production",
        secure=settings.APP_ENV == "production",
        samesite="lax",
    )
