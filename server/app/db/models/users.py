from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel

if TYPE_CHECKING:
    from db.models.address import Address
    from db.models.cart import Cart
    from db.models.order import Order


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    refresh_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)

    # Relationships
    addresses: Mapped[list["Address"]] = relationship("Address", back_populates="user")
    cart: Mapped["Cart | None"] = relationship("Cart", back_populates="user", uselist=False)
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
