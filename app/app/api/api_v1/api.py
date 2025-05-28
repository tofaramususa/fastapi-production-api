from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    folders,
    products,
    assign_folder_permission,
)

api_router = APIRouter()
api_router.include_router(folders.router, prefix="/folders", tags=["folders"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(
    assign_folder_permission.router, prefix="/folder-permissions", tags=["permissions"]
)
