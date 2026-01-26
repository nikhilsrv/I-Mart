import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel

if TYPE_CHECKING:
    from db.models.product import Product


class Category(BaseModel):
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("category.id"), nullable=True
    )

    # Self-referencing relationship
    parent: Mapped["Category | None"] = relationship(
        "Category", remote_side="Category.id", back_populates="children"
    )
    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent"
    )

    # Relationship to products
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")
