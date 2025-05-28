from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from motor.core import AgnosticDatabase
from odmantic import ObjectId
from app import crud, models, schemas
from app.api import deps
from app.api.auth import APIUser, get_current_user, check_access_permission
from app.api.middleware.ratelimit import rate_limit

router = APIRouter()


@router.post("", response_model=schemas.Folder, status_code=201)
@router.post("/", response_model=schemas.Folder, status_code=201)
@router.post("/create", response_model=schemas.Folder, status_code=201)
async def create_new_folder(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
    name: str = Body(...),
    description: str = Body(""),
    owner: Optional[str] = Body(None),
    products: Optional[List[str]] = Body(None),
):
    """
    Create a new folder.
    Requires authentication.
    """
    # Use current user's email as owner if not provided
    if not owner:
        owner = current_user.email

    # Create folder data
    folder_in = schemas.FolderCreate(
        name=name, description=description, owner=owner, products=products or []
    )

    # Create folder in database
    try:
        folder = await crud.folder.create(db, obj_in=folder_in)
        return schemas.Folder.from_db_model(folder)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create folder: {str(e)}"
        )


# GET / - Retrieve all folders the user has access to
@router.get("/", response_model=List[schemas.Folder], response_model_exclude_unset=True)
@router.get("", response_model=List[schemas.Folder], response_model_exclude_unset=True)
async def read_all_folders(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
) -> Any:
    """
    Retrieve all folders that the user has access to.
    Admin users can see all folders.
    Regular users only see folders they have permission for.
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

    return [schemas.Folder.from_db_model(folder) for folder in db_folders]


@router.get(
    "/folders-and-products",
    response_model=schemas.NavigationResponse,
    response_model_exclude_unset=True,
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
    folders_with_products = []

    for folder in db_folders:
        products = await crud.products.get_by_folder_id(db, folder_id=folder.id)
        if products:
            folders_with_products.append(folder)
            all_products.extend(products)

    if not folders_with_products:
        raise HTTPException(
            status_code=404,
            detail="No folders with products found",
        )

    return {
        "folders": [
            schemas.Folder.from_db_model(folder)
            for folder in folders_with_products
        ],
        "products": [
            schemas.Product.from_db_model(product)
            for product in all_products
        ],
    }


# Remove or protect test endpoint
@router.get("/tester", response_model_exclude_unset=True)
@router.get("/tester/", response_model_exclude_unset=True)
async def test_endpoint(
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
) -> Any:
    """
    Protected test endpoint.
    """
    return {"message": "Hello, World!", "user": current_user.email}


# GET /{folder_id} - Retrieve a specific folder by ID
@router.get(
    "/{folder_id}", response_model=schemas.Folder, response_model_exclude_unset=True
)
@router.get(
    "/{folder_id}/", response_model=schemas.Folder, response_model_exclude_unset=True
)
async def read_folder(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    folder_id: str,
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
) -> Any:
    """
    Get a specific folder by ID.
    Requires authentication and proper permissions.
    """
    try:
        folder_object_id = ObjectId(folder_id)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"'{folder_id}' is not a valid folder ID. It must be a 24-character hex string.",
        )

    # Check permissions first
    await check_access_permission(db, current_user, folder_id=folder_object_id)

    # Fetch the folder by ID
    try:
        folder = await crud.folder.get(db, id=folder_object_id)
        if not folder:
            raise HTTPException(
                status_code=404, detail=f"Folder with ID '{folder_id}' not found"
            )
        return schemas.Folder.from_db_model(folder)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch folder: {str(e)}"
        )
