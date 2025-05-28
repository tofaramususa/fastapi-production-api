from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from motor.core import AgnosticDatabase

from app import crud, schemas
from app.api import deps
from app.api.auth import APIUser, get_current_user
from app.api.middleware.ratelimit import rate_limit

router = APIRouter()


@router.get(
    "", response_model=schemas.NavigationResponse, response_model_exclude_unset=True
)
@router.get(
    "/", response_model=schemas.NavigationResponse, response_model_exclude_unset=True
)
async def get_folders_and_products(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
) -> Any:
    """
    Get all accessible folders and their associated products.
    Returns a single object containing both folders and products arrays.
    Admin users can see all folders and products.
    Regular users only see folders and products they have permission for.
    Raises 404 if no folders are found.
    """
    # Get folders the user has access to
    if current_user.is_admin:
        db_folders = await crud.folder.get_multi(db=db)
        if not db_folders:
            raise HTTPException(status_code=404, detail="No folders found")
    else:
        # Get permissions for the current user
        permissions = await crud.folder_permissions.get_by_email(
            db, email=current_user.email
        )
        folder_ids = [perm.folder_id for perm in permissions]

        if not folder_ids:
            raise HTTPException(status_code=404, detail="No folders found")

        # Get only the folders the user has permission for
        db_folders = []
        for folder_id in folder_ids:
            folder = await crud.folder.get(db, id=folder_id)
            if folder:
                db_folders.append(folder)

        if not db_folders:
            raise HTTPException(status_code=404, detail="No folders found")

    # Get all products from accessible folders
    all_products = []
    for folder in db_folders:
        products = await crud.products.get_by_folder_id(db, folder_id=folder.id)
        all_products.extend(products)

    return {
        "folders": [schemas.Folder.from_db_model(folder) for folder in db_folders],
        "products": [
            schemas.Product.from_db_model(product) for product in all_products
        ],
    }
