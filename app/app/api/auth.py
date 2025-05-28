# Authentication and authorization utilities for the API
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Optional, Union
from ..database.firebase import get_firebase_user
from app.core.config import settings
from app.crud.crud_permissions import folder_permissions
from app.crud.crud_products import products
from odmantic import ObjectId
from motor.core import AgnosticDatabase

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# APIUser represents an authenticated user with their permissions
class APIUser(BaseModel):
    email: EmailStr
    uid: str
    is_admin: bool


# get_current_user validates the authentication token and returns the current user
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> APIUser:
    """
    Validates the authentication token and returns the current user.
    Supports both Firebase authentication and master token access.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    # Check if token matches master key
    master_key = settings.MASTER_TOKEN
    if master_key and token == master_key:
        return APIUser(email="admin@dirtyboots.ai", uid="master", is_admin=True)

    user_data = await get_firebase_user(token)
    if not user_data:
        raise credentials_exception

    email = user_data.get("email", "")

    # Check if user's email domain is in the admin domains list
    is_admin = False
    admin_domains = ["beuseful.ai", "dirtyboots.ai", "onely.com"]

    if email:
        domain = email.split("@")[-1].lower() if "@" in email else ""
        is_admin = domain in admin_domains

    # Ensure user_data has all required fields
    user_data = {
        "email": email,
        "uid": user_data.get("uid"),
        "is_admin": is_admin,
    }  # Set to True for admin domains
    return APIUser(**user_data)


# get_folder_id_from_product retrieves the folder ID associated with a product
async def get_folder_id_from_product(
    db: AgnosticDatabase, product_id: ObjectId
) -> Optional[ObjectId]:
    """Get folder_id from a product_id. Returns None if product not found."""
    product = await products.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )
    return product.folder_id


# check_access_permission verifies if a user has permission to access a specific resource
async def check_access_permission(
    db: AgnosticDatabase,
    user: APIUser,
    product_id: Optional[ObjectId] = None,
    folder_id: Optional[ObjectId] = None,
) -> bool:
    """
    Check if a user has permission to access a specific resource.
    Can check by either product_id or folder_id.
    Returns True if:
    1. User is an admin
    2. User has explicit permission for the folder
    Raises HTTPException if no permission is found.
    """
    # Admins always have access
    if user.is_admin:
        return True

    # Determine folder_id if product_id was provided
    if product_id and not folder_id:
        folder_id = await get_folder_id_from_product(db, product_id)

    if not folder_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either product_id or folder_id must be provided",
        )

    # Check if user has explicit permission
    has_access = await folder_permissions.has_permission(
        db=db, folder_id=folder_id, email=user.email
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No permission to access this resource",
        )

    return True
