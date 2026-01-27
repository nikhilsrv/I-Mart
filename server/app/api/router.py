from fastapi import APIRouter

from api.routes.auth import router as auth_router
from api.routes.products import router as products_router

router = APIRouter(prefix="/api")

router.include_router(auth_router)
router.include_router(products_router)
