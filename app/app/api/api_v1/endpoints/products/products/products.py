# API endpoints for managing products with authentication, access control, and folder-based organization
from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from motor.core import AgnosticDatabase
from odmantic import ObjectId
from app import crud, models, schemas
from app.api import deps
from app.api.auth import APIUser, get_current_user, check_access_permission
from app.api.middleware.accessChecks import validate_and_get_object_id
from app.api.middleware.ratelimit import rate_limit, product_creation_rate_limit

# router handles all product-related endpoints with proper authentication and validation
router = APIRouter()


# create_product creates a new product in a specified folder and triggers prompt generation
@router.post("", response_model=schemas.Product)
@router.post("/", response_model=schemas.Product)
async def create_product(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(product_creation_rate_limit),
    name: str = Body(..., embed=True),
    folder_id: str = Body(..., embed=True, alias="folder_id"),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Create a new product with the specified name and folder ID.
    Requires authentication and folder access permission.
    Rate limited to 1 product creation per 2 hours per user.
    """
    # Validate folder_id and check permissions
    folder_object_id = await validate_and_get_object_id(folder_id, "folder")

    try:
        # Check if user has permission to access the folder
        await check_access_permission(db, current_user, folder_id=folder_object_id)
    except HTTPException as e:
        if e.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to create products in folder {folder_id}",
            )
        raise e

    # Create product data
    product_in = schemas.ProductCreate(
        name=name, folder_id=folder_object_id, owner=current_user.email
    )

    # Create product in database
    try:
        product = await crud.products.create(db, obj_in=product_in)
        # if product:
            # background_tasks.add_task(
            #     triggerPromptGeneration,
            #     product_name=product.name,
            #     product_id=str(product.id),
            # )
        # return schemas.Product.from_db_model(product)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create product: {str(e)}"
        )


# read_folder_products retrieves all products in a folder
@router.get("", response_model=List[schemas.Product], response_model_exclude_unset=True)
@router.get(
    "/", response_model=List[schemas.Product], response_model_exclude_unset=True
)
async def read_folder_products(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
    folder_id: str = Query(
        ..., description="The ID of the folder to retrieve products from"
    ),
) -> Any:
    """
    Retrieve all products in a specific folder.
    Requires authentication and folder access permission.
    Returns 404 if no products found.
    """
    # Validate folder_id and check permissions
    folder_object_id = await validate_and_get_object_id(folder_id, "folder")

    try:
        # Check if user has permission to access the folder
        await check_access_permission(db, current_user, folder_id=folder_object_id)
    except HTTPException as e:
        if e.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to view products in folder {folder_id}",
            )
        raise e

    # Fetch the products by folder ID
    try:
        products = await crud.products.get_by_folder_id(db, folder_id=folder_object_id)
        if not products:
            raise HTTPException(
                status_code=404, detail=f"No products found for folder ID: {folder_id}"
            )

        return [schemas.Product.from_db_model(product) for product in products]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch products: {str(e)}"
        )


# read_product retrieves a specific product by its ID with access control
@router.get(
    "/{product_id}", response_model=schemas.Product, response_model_exclude_unset=True
)
async def read_product(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
    product_id: str,
) -> Any:
    """
    Retrieve a specific product by its ID.
    Requires authentication and proper permissions.
    """
    # Validate product_id
    product_object_id = await validate_and_get_object_id(product_id, "product")

    try:
        # Check if user has permission to access this product
        await check_access_permission(db, current_user, product_id=product_object_id)
    except HTTPException as e:
        if e.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail=f"You don't have permission to access product {product_id}",
            )
        raise e

    # Fetch the product by ID
    try:
        product = await crud.products.get(db, id=product_object_id)
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product with ID '{product_id}' not found"
            )
        return schemas.Product.from_db_model(product)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch product: {str(e)}"
        )
