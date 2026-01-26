import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel

if TYPE_CHECKING:
    from db.models.cart import Cart
    from db.models.product import Product


class CartItem(BaseModel):
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
    )

    cart_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("cart.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")
