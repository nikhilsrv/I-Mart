import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel

if TYPE_CHECKING:
    from db.models.users import User
    from db.models.cart_item import CartItem


class Cart(BaseModel):
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id"), unique=True, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cart")
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )
