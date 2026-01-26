import uuid
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel

if TYPE_CHECKING:
    from db.models.users import User
    from db.models.address import Address
    from db.models.order_item import OrderItem


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(BaseModel):
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    order_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.PENDING)
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    shipping_address_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("address.id"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    shipping_address: Mapped["Address"] = relationship("Address")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
