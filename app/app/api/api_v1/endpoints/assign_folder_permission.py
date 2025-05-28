# API endpoints for managing folder permissions with authentication and access control
from typing import Any, List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_serializer
from odmantic import ObjectId
import json
from app.schemas.base_schema import BaseSchema

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.encoders import jsonable_encoder
from motor.core import AgnosticDatabase
from pydantic.networks import EmailStr

from app import crud, models, schemas
from app.api import deps
from app.api.auth import APIUser, get_current_user
from app.api.middleware.ratelimit import rate_limit

# router handles all folder permission related endpoints with proper authentication and validation
router = APIRouter()


# assign_folder_permission creates a new folder permission for a user by email
@router.post("", response_model=schemas.FolderPermission, status_code=201)
@router.post("/", response_model=schemas.FolderPermission, status_code=201)
@router.post(
    "/folder-permission", response_model=schemas.FolderPermission, status_code=201
)
async def assign_folder_permission(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
    folder_id: str = Body(...),
    email: EmailStr = Body(...),
) -> Any:
    """
    Assign folder permission to a user by email.
    Only admins can assign permissions.
    """
    # Check if current user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Only administrators can assign folder permissions"
        )

    # Validate folder exists
    try:
        folder_object_id = ObjectId(folder_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"'{folder_id}' is not a valid folder ID. It must be a 24-character hex string.",
        )

    folder = await crud.folder.get(db, id=folder_object_id)
    if not folder:
        raise HTTPException(
            status_code=404, detail=f"Folder with ID '{folder_id}' not found"
        )

    # Check if permission already exists
    has_permission = await crud.folder_permissions.has_permission(
        db, folder_id=folder_object_id, email=email
    )

    if has_permission:
        raise HTTPException(
            status_code=400,
            detail=f"Permission for user '{email}' on folder '{folder_id}' already exists",
        )

    # Create new permission
    permission_data = schemas.FolderPermissionCreate(
        email=email,
        folder_id=str(folder_object_id),
    )

    new_permission = await crud.folder_permissions.create(db, obj_in=permission_data)

    return schemas.FolderPermission.from_db_model(new_permission)


# read_folder_permissions retrieves all permissions for a specific folder
@router.get(
    "/{folder_id}",
    response_model=List[schemas.FolderPermission],
    response_model_exclude_unset=True,
)
@router.get(
    "/{folder_id}/",
    response_model=List[schemas.FolderPermission],
    response_model_exclude_unset=True,
)
async def read_folder_permissions(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
    folder_id: str,
) -> Any:
    """
    Get all permissions for a specific folder.
    Only admins can see all permissions for a folder.
    """
    # Check if current user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can view all folder permissions",
        )

    # Validate folder exists
    try:
        folder_object_id = ObjectId(folder_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"'{folder_id}' is not a valid folder ID. It must be a 24-character hex string.",
        )

    folder = await crud.folder.get(db, id=folder_object_id)
    if not folder:
        raise HTTPException(
            status_code=404, detail=f"Folder with ID '{folder_id}' not found"
        )

    # Get all permissions for this folder
    permissions = await crud.folder_permissions.get_by_folder_id(
        db, folder_id=folder_object_id
    )

    if not permissions:
        return []

    return [
        schemas.FolderPermission.from_db_model(permission) for permission in permissions
    ]


# check_user_folder_permission verifies if a specific user has permission for a folder
@router.get(
    "/{folder_id}/{email}",
    response_model=schemas.FolderPermission,
    response_model_exclude_unset=True,
)
@router.get(
    "/{folder_id}/{email}/",
    response_model=schemas.FolderPermission,
    response_model_exclude_unset=True,
)
async def check_user_folder_permission(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
    folder_id: str,
    email: EmailStr,
) -> Any:
    """
    Check if a specific user has permission for a folder.
    Admins can check any user's permission.
    Regular users can only check their own permissions.
    """
    # If not admin, can only check own permissions
    if not current_user.is_admin and current_user.email != email:
        raise HTTPException(
            status_code=403, detail="You can only check your own permissions"
        )

    # Validate folder exists
    try:
        folder_object_id = ObjectId(folder_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"'{folder_id}' is not a valid folder ID. It must be a 24-character hex string.",
        )

    folder = await crud.folder.get(db, id=folder_object_id)
    if not folder:
        raise HTTPException(
            status_code=404, detail=f"Folder with ID '{folder_id}' not found"
        )

    # Check if permission exists
    has_permission = await crud.folder_permissions.has_permission(
        db, folder_id=folder_object_id, email=email
    )

    if not has_permission:
        raise HTTPException(
            status_code=404,
            detail=f"No permission found for user '{email}' on folder '{folder_id}'",
        )

    # Get the permission
    permissions = await crud.folder_permissions.get_by_folder_and_email(
        db, folder_id=folder_object_id, email=email
    )

    return schemas.FolderPermission.from_db_model(permissions)


# revoke_folder_permission removes a user's permission for a specific folder
@router.delete(
    "/{folder_id}/{email}", response_model=schemas.FolderPermission, status_code=200
)
@router.delete(
    "/{folder_id}/{email}/", response_model=schemas.FolderPermission, status_code=200
)
async def revoke_folder_permission(
    *,
    db: AgnosticDatabase = Depends(deps.get_db),
    current_user: APIUser = Depends(get_current_user),
    rate_limit_info: dict = Depends(rate_limit),
    folder_id: str,
    email: EmailStr,
) -> Any:
    """
    Revoke folder permission from a user by email.
    Only admins can revoke permissions.
    """
    # Check if current user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Only administrators can revoke folder permissions"
        )

    # Validate folder exists
    try:
        folder_object_id = ObjectId(folder_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"'{folder_id}' is not a valid folder ID. It must be a 24-character hex string.",
        )

    folder = await crud.folder.get(db, id=folder_object_id)
    if not folder:
        raise HTTPException(
            status_code=404, detail=f"Folder with ID '{folder_id}' not found"
        )

    # Get the permission before deletion
    permission = await crud.folder_permissions.get_by_folder_and_email(
        db, folder_id=folder_object_id, email=email
    )

    if not permission:
        raise HTTPException(
            status_code=404,
            detail=f"Permission for user '{email}' on folder '{folder_id}' not found",
        )

    # Store permission for return
    permission_to_return = schemas.FolderPermission.from_db_model(permission)

    # Delete the permission
    deleted = await crud.folder_permissions.delete_by_folder_and_user(
        db, folder_id=folder_object_id, email=email
    )

    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete permission")

    return permission_to_return
