import base64
import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.product import Product
from db.session import get_db
from schemas.product import ProductDetailResponse, ProductListResponse, ProductResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


def encode_cursor(created_at: datetime, product_id: uuid.UUID) -> str:
    """Encode created_at and product_id into a cursor string."""
    data = {"created_at": created_at.isoformat(), "id": str(product_id)}
    return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID] | None:
    """Decode cursor string into created_at and product_id."""
    try:
        data = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        return datetime.fromisoformat(data["created_at"]), uuid.UUID(data["id"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


@router.get("", response_model=ProductListResponse)
async def get_all_products(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Number of products to return"),
    cursor: str | None = Query(None, description="Cursor for pagination"),
    category_id: uuid.UUID | None = Query(None, description="Filter by category ID"),
    search: str | None = Query(None, description="Search products by name or description"),
):
    """
    Get all active products with cursor-based pagination and optional filtering.
    """
    logger.info("Fetching products with limit=%d, cursor=%s, search=%s", limit, cursor, search)

    query = select(Product).where(
        Product.is_deleted == False,
        Product.is_active == True,
    )

    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern),
            )
        )

    # Apply cursor filter if provided
    if cursor:
        decoded = decode_cursor(cursor)
        if decoded is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cursor",
            )
        cursor_created_at, cursor_id = decoded
        # Get items with created_at < cursor OR (created_at == cursor AND id < cursor_id)
        query = query.where(
            or_(
                Product.created_at < cursor_created_at,
                tuple_(Product.created_at, Product.id) < tuple_(cursor_created_at, cursor_id),
            )
        )

    # Fetch one extra to determine has_more
    query = query.order_by(Product.created_at.desc(), Product.id.desc()).limit(limit + 1)
    result = await db.execute(query)
    products = list(result.scalars().all())

    # Check if there are more items
    has_more = len(products) > limit
    if has_more:
        products = products[:limit]

    # Generate next cursor from last item
    next_cursor = None
    if has_more and products:
        last_product = products[-1]
        next_cursor = encode_cursor(last_product.created_at, last_product.id)

    logger.info("Found %d products (has_more: %s)", len(products), has_more)

    return ProductListResponse(
        products=[ProductResponse.model_validate(p) for p in products],
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product_details(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific product including its category.
    """
    logger.info("Fetching product details for product_id=%s", product_id)

    query = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.id == product_id, Product.is_deleted == False)
    )
    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if product is None:
        logger.warning("Product not found: product_id=%s", product_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    logger.info("Product found: product_id=%s, name=%s", product_id, product.name)

    return ProductDetailResponse.model_validate(product)
