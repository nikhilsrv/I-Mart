from enum import Enum

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import BaseModel


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    refresh_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
