import logging
from uuid import UUID

import httpx
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.models.users import User
from utils.tokens import ALGORITHM, create_access_token, create_refresh_token

logger = logging.getLogger(__name__)

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def exchange_google_code(self, code: str) -> dict:
        """Exchange authorization code for Google tokens."""
        logger.debug("Exchanging Google authorization code")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
            )
            if response.status_code != 200:
                logger.error("Failed to exchange Google code: status=%s", response.status_code)
                raise ValueError(f"Failed to exchange code: {response.text}")
            logger.debug("Google code exchange successful")
            return response.json()

    async def get_google_user_info(self, access_token: str) -> dict:
        """Get user info from Google using the access token."""
        logger.debug("Fetching user info from Google")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code != 200:
                logger.error("Failed to get Google user info: status=%s", response.status_code)
                raise ValueError(f"Failed to get user info: {response.text}")
            logger.debug("Google user info fetched successfully")
            return response.json()

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create_user(self, email: str, name: str) -> User:
        """Create a new user."""
        logger.info("Creating new user")
        user = User(email=email, name=name)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info("User created successfully: user_id=%s", user.id)
        return user

    async def update_refresh_token(self, user: User, refresh_token: str) -> None:
        """Update user's refresh token."""
        user.refresh_token = refresh_token
        await self.db.commit()

    def verify_token(self, token: str, token_type: str = "access") -> UUID | None:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != token_type:
                logger.warning("Token type mismatch: expected=%s", token_type)
                return None
            user_id = payload.get("sub")
            if user_id is None:
                logger.warning("Token missing subject claim")
                return None
            return UUID(user_id)
        except JWTError:
            logger.warning("JWT verification failed")
            return None

    async def _get_google_user_data(self, code: str) -> dict:
        """Exchange code and get user data from Google."""
        google_tokens = await self.exchange_google_code(code)
        google_access_token = google_tokens["access_token"]
        return await self.get_google_user_info(google_access_token)

    async def _generate_and_store_tokens(self, user: User) -> tuple[str, str]:
        """Generate access and refresh tokens and store refresh token."""
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        await self.update_refresh_token(user, refresh_token)
        return access_token, refresh_token

    async def google_login(self, code: str) -> tuple[User, str, str]:
        """
        Handle Google OAuth login for existing users.
        Raises ValueError if user does not exist.
        """
        logger.info("Processing Google login")
        google_user = await self._get_google_user_data(code)
        email = google_user["email"]

        user = await self.get_user_by_email(email)
        if user is None:
            logger.warning("Login attempt for non-existent user")
            raise ValueError("User not found. Please sign up first.")

        access_token, refresh_token = await self._generate_and_store_tokens(user)
        logger.info("Google login completed: user_id=%s", user.id)
        return user, access_token, refresh_token

    async def google_signup(self, code: str) -> tuple[User, str, str]:
        """
        Handle Google OAuth signup for new users.
        Raises ValueError if user already exists.
        """
        logger.info("Processing Google signup")
        google_user = await self._get_google_user_data(code)
        email = google_user["email"]
        name = google_user.get("name", email.split("@")[0])

        existing_user = await self.get_user_by_email(email)
        if existing_user is not None:
            logger.warning("Signup attempt for existing user")
            raise ValueError("User already exists. Please log in instead.")

        user = await self.create_user(email=email, name=name)
        access_token, refresh_token = await self._generate_and_store_tokens(user)
        logger.info("Google signup completed: user_id=%s", user.id)
        return user, access_token, refresh_token

    async def refresh_tokens(self, refresh_token: str) -> tuple[User, str, str] | None:
        """
        Refresh access token using refresh token.
        Returns new tokens if valid.
        """
        logger.debug("Processing token refresh")
        user_id = self.verify_token(refresh_token, token_type="refresh")
        if user_id is None:
            logger.warning("Token refresh failed: invalid token")
            return None

        user = await self.get_user_by_id(user_id)
        if user is None or user.refresh_token != refresh_token:
            logger.warning("Token refresh failed: user not found or token mismatch")
            return None

        # Create new tokens
        new_access_token = create_access_token(user.id)
        new_refresh_token = create_refresh_token(user.id)

        # Update stored refresh token
        await self.update_refresh_token(user, new_refresh_token)

        logger.info("Token refresh completed: user_id=%s", user.id)
        return user, new_access_token, new_refresh_token

    async def logout(self, user: User) -> None:
        """Logout user by clearing refresh token."""
        logger.info("User logout: user_id=%s", user.id)
        user.refresh_token = None
        await self.db.commit()
