from fastapi.encoders import jsonable_encoder
from motor.core import AgnosticDatabase
import pytest
from typing import List, Dict, Any
from datetime import datetime
from app import crud
from app.schemas.folder_permission import (
    FolderPermissionCreate,
    FolderPermissionUpdate,
    FolderPermissionInDB,
)
from app.tests.utils.utils import random_lower_string
from odmantic import ObjectId


@pytest.fixture
def test_permission_data() -> dict:
    """Fixture to provide test permission data"""
    return {
        "folder_id": str(ObjectId()),
        "email": f"{random_lower_string()}@example.com",
    }


@pytest.mark.asyncio
async def test_create_permission(db: AgnosticDatabase) -> None:
    """Test basic permission creation"""
    folder_id = str(ObjectId())
    email = f"{random_lower_string()}@example.com"

    permission_in = FolderPermissionCreate(folder_id=folder_id, email=email)

    permission = await crud.folder_permissions.create(db, obj_in=permission_in)
    assert permission.folder_id == ObjectId(folder_id)
    assert permission.email == email
    assert isinstance(permission.createdAt, datetime)
    assert isinstance(permission.modifiedAt, datetime)


@pytest.mark.asyncio
async def test_get_permission(db: AgnosticDatabase, test_permission_data: dict) -> None:
    """Test retrieving a permission entry"""
    # Create a permission entry first
    permission_in = FolderPermissionCreate(**test_permission_data)
    created_permission = await crud.folder_permissions.create(db, obj_in=permission_in)

    # Get the permission entry
    retrieved_permission = await crud.folder_permissions.get(
        db, id=created_permission.id
    )
    assert retrieved_permission is not None
    assert retrieved_permission.folder_id == ObjectId(test_permission_data["folder_id"])
    assert retrieved_permission.email == test_permission_data["email"]


@pytest.mark.asyncio
async def test_get_nonexistent_permission(db: AgnosticDatabase) -> None:
    """Test retrieving a non-existent permission entry"""
    nonexistent_id = ObjectId()
    retrieved_permission = await crud.folder_permissions.get(db, id=nonexistent_id)
    assert retrieved_permission is None


@pytest.mark.asyncio
async def test_update_permission(
    db: AgnosticDatabase, test_permission_data: dict
) -> None:
    """Test updating a permission entry"""
    # Create a permission entry first
    permission_in = FolderPermissionCreate(**test_permission_data)
    created_permission = await crud.folder_permissions.create(db, obj_in=permission_in)

    # Update the permission entry
    new_email = f"{random_lower_string()}@example.com"
    update_data = FolderPermissionUpdate(email=new_email)
    updated_permission = await crud.folder_permissions.update(
        db, db_obj=created_permission, obj_in=update_data
    )

    assert updated_permission.email == new_email
    assert updated_permission.folder_id == ObjectId(
        test_permission_data["folder_id"]
    )  # Should remain unchanged
    assert updated_permission.id == created_permission.id  # ID should remain the same


@pytest.mark.asyncio
async def test_delete_permission(
    db: AgnosticDatabase, test_permission_data: dict
) -> None:
    """Test deleting a permission entry"""
    # Create a permission entry first
    permission_in = FolderPermissionCreate(**test_permission_data)
    created_permission = await crud.folder_permissions.create(db, obj_in=permission_in)

    # Delete the permission entry
    await crud.folder_permissions.engine.delete(created_permission)

    # Verify the permission entry is deleted
    retrieved_permission = await crud.folder_permissions.get(
        db, id=created_permission.id
    )
    assert retrieved_permission is None


@pytest.mark.asyncio
async def test_list_permissions(
    db: AgnosticDatabase, test_permission_data: dict
) -> None:
    """Test listing permission entries"""
    # Create multiple permission entries
    permission_entries = []
    for _ in range(3):
        permission_in = FolderPermissionCreate(**test_permission_data)
        permission = await crud.folder_permissions.create(db, obj_in=permission_in)
        permission_entries.append(permission)

    # List all permission entries
    all_permissions = await crud.folder_permissions.get_multi(db)
    assert len(all_permissions) >= len(
        permission_entries
    )  # There might be other entries in the DB

    # Verify our created entries are in the list
    created_ids = {entry.id for entry in permission_entries}
    listed_ids = {entry.id for entry in all_permissions}
    assert created_ids.issubset(listed_ids)


@pytest.mark.asyncio
async def test_list_permissions_with_pagination(
    db: AgnosticDatabase, test_permission_data: dict
) -> None:
    """Test listing permission entries with pagination"""
    # Create multiple permission entries
    permission_entries = []
    for _ in range(5):
        permission_in = FolderPermissionCreate(**test_permission_data)
        permission = await crud.folder_permissions.create(db, obj_in=permission_in)
        permission_entries.append(permission)

    # List permission entries with pagination
    page = 0
    page_break = True
    paginated_permissions = await crud.folder_permissions.get_multi(
        db, page=page, page_break=page_break
    )
    assert len(paginated_permissions) <= 100  # Default MULTI_MAX setting


@pytest.mark.asyncio
async def test_get_permissions_by_folder_id(
    db: AgnosticDatabase, test_permission_data: dict
) -> None:
    """Test retrieving permissions by folder_id"""
    # Create multiple permission entries for the same folder
    folder_id = ObjectId(test_permission_data["folder_id"])
    permission_entries = []
    for _ in range(3):
        permission_in = FolderPermissionCreate(**test_permission_data)
        permission = await crud.folder_permissions.create(db, obj_in=permission_in)
        permission_entries.append(permission)

    # Get permissions by folder_id
    folder_permissions = await crud.folder_permissions.get_by_folder_id(
        db, folder_id=folder_id
    )
    assert len(folder_permissions) == len(permission_entries)

    # Verify all entries belong to the correct folder
    for permission in folder_permissions:
        assert permission.folder_id == folder_id


@pytest.mark.asyncio
async def test_get_permissions_by_email(
    db: AgnosticDatabase, test_permission_data: dict
) -> None:
    """Test retrieving permissions by email"""
    # Create multiple permission entries for the same email
    email = test_permission_data["email"]
    permission_entries = []
    for _ in range(3):
        permission_in = FolderPermissionCreate(**test_permission_data)
        permission = await crud.folder_permissions.create(db, obj_in=permission_in)
        permission_entries.append(permission)

    # Get permissions by email
    email_permissions = await crud.folder_permissions.get_by_email(email=email)
    assert len(email_permissions) == len(permission_entries)

    # Verify all entries belong to the correct email
    for permission in email_permissions:
        assert permission.email == email


@pytest.mark.asyncio
async def test_delete_by_folder_and_user(
    db: AgnosticDatabase, test_permission_data: dict
) -> None:
    """Test deleting a permission by folder_id and email"""
    # Create a permission entry
    permission_in = FolderPermissionCreate(**test_permission_data)
    created_permission = await crud.folder_permissions.create(db, obj_in=permission_in)

    # Delete the permission by folder_id and email
    result = await crud.folder_permissions.delete_by_folder_and_user(
        folder_id=ObjectId(test_permission_data["folder_id"]),
        email=test_permission_data["email"],
    )
    assert result is True

    # Verify the permission is deleted
    retrieved_permission = await crud.folder_permissions.get(
        db, id=created_permission.id
    )
    assert retrieved_permission is None


@pytest.mark.asyncio
async def test_has_permission(db: AgnosticDatabase, test_permission_data: dict) -> None:
    """Test checking if a user has permission for a folder"""
    # Create a permission entry
    permission_in = FolderPermissionCreate(**test_permission_data)
    await crud.folder_permissions.create(db, obj_in=permission_in)

    # Check if the user has permission
    has_perm = await crud.folder_permissions.has_permission(
        folder_id=ObjectId(test_permission_data["folder_id"]),
        email=test_permission_data["email"],
    )
    assert has_perm is True

    # Check for non-existent permission
    has_perm = await crud.folder_permissions.has_permission(
        folder_id=ObjectId(), email="nonexistent@example.com"
    )
    assert has_perm is False


@pytest.mark.asyncio
async def test_get_by_folder_and_email(
    db: AgnosticDatabase, test_permission_data: dict
) -> None:
    """Test getting a permission by folder_id and email"""
    # Create a permission entry
    permission_in = FolderPermissionCreate(**test_permission_data)
    created_permission = await crud.folder_permissions.create(db, obj_in=permission_in)

    # Get the permission by folder_id and email
    retrieved_permission = await crud.folder_permissions.get_by_folder_and_email(
        folder_id=ObjectId(test_permission_data["folder_id"]),
        email=test_permission_data["email"],
    )
    assert retrieved_permission is not None
    assert retrieved_permission.id == created_permission.id
    assert retrieved_permission.folder_id == ObjectId(test_permission_data["folder_id"])
    assert retrieved_permission.email == test_permission_data["email"]
