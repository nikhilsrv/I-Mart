import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None

    model_config = {"from_attributes": True}


class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    description: str | None = None
    price: Decimal
    compare_price: Decimal | None = None
    sku: str | None = None
    stock_quantity: int
    is_active: bool
    image_url: str | None = None
    category_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductDetailResponse(ProductResponse):
    category: CategoryResponse


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    next_cursor: str | None = None
    has_more: bool
