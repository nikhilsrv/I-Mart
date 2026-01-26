import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel

if TYPE_CHECKING:
    from db.models.users import User


class AddressType(str, Enum):
    SHIPPING = "shipping"
    BILLING = "billing"


class Address(BaseModel):
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    type: Mapped[AddressType] = mapped_column(nullable=False)
    street: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_default: Mapped[bool] = mapped_column(default=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="addresses")
