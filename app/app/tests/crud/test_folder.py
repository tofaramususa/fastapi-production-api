from fastapi.encoders import jsonable_encoder
from motor.core import AgnosticDatabase
import pytest
from typing import List
from datetime import datetime
from app import crud
from app.schemas.folder import FolderCreate, FolderUpdate, Folder
from app.tests.utils.utils import random_lower_string
from odmantic import ObjectId


@pytest.fixture
def test_folder_data() -> dict:
    """Fixture to provide test folder data"""
    return {
        "name": random_lower_string(),
        "description": random_lower_string(),
        "owner": random_lower_string(),
        "products": [],
    }


@pytest.mark.asyncio
async def test_create_folder(db: AgnosticDatabase) -> None:
    """Test basic folder creation"""
    name = random_lower_string()
    description = random_lower_string()
    owner = random_lower_string()
    folder_in = FolderCreate(name=name, description=description, owner=owner)
    folder = await crud.folder.create(db, obj_in=folder_in)
    assert folder.name == name
    assert folder.description == description
    assert folder.owner == owner
    assert isinstance(folder.createdAt, datetime)
    assert isinstance(folder.modifiedAt, datetime)


@pytest.mark.asyncio
async def test_create_folder_with_products(db: AgnosticDatabase) -> None:
    """Test folder creation with products"""
    name = random_lower_string()
    description = random_lower_string()
    owner = random_lower_string()
    products = [str(ObjectId()) for _ in range(3)]  # Create some dummy product IDs
    folder_in = FolderCreate(
        name=name, description=description, owner=owner, products=products
    )
    folder = await crud.folder.create(db, obj_in=folder_in)
    assert folder.name == name
    assert folder.description == description
    assert folder.owner == owner
    assert len(folder.products) == len(products)
    assert all(str(product_id) in products for product_id in folder.products)


@pytest.mark.asyncio
async def test_create_folder_minimal_data(db: AgnosticDatabase) -> None:
    """Test folder creation with minimal required data"""
    name = random_lower_string()
    folder_in = FolderCreate(name=name)
    folder = await crud.folder.create(db, obj_in=folder_in)
    assert folder.name == name
    assert folder.description == ""  # Default value
    assert folder.owner == ""  # Default value
    assert folder.products == []  # Default value


@pytest.mark.asyncio
async def test_get_folder(db: AgnosticDatabase, test_folder_data: dict) -> None:
    """Test retrieving a folder"""
    # Create a folder first
    folder_in = FolderCreate(**test_folder_data)
    created_folder = await crud.folder.create(db, obj_in=folder_in)

    # Get the folder
    retrieved_folder = await crud.folder.get(db, id=created_folder.id)
    assert retrieved_folder is not None
    assert retrieved_folder.name == test_folder_data["name"]
    assert retrieved_folder.description == test_folder_data["description"]
    assert retrieved_folder.owner == test_folder_data["owner"]


@pytest.mark.asyncio
async def test_get_nonexistent_folder(db: AgnosticDatabase) -> None:
    """Test retrieving a non-existent folder"""
    nonexistent_id = ObjectId()
    retrieved_folder = await crud.folder.get(db, id=nonexistent_id)
    assert retrieved_folder is None


@pytest.mark.asyncio
async def test_update_folder(db: AgnosticDatabase, test_folder_data: dict) -> None:
    """Test updating a folder"""
    # Create a folder first
    folder_in = FolderCreate(**test_folder_data)
    created_folder = await crud.folder.create(db, obj_in=folder_in)

    # Update the folder
    new_name = random_lower_string()
    new_description = random_lower_string()
    update_data = FolderUpdate(name=new_name, description=new_description)
    updated_folder = await crud.folder.update(
        db, db_obj=created_folder, obj_in=update_data
    )

    assert updated_folder.name == new_name
    assert updated_folder.description == new_description
    assert updated_folder.owner == test_folder_data["owner"]  # Should remain unchanged
    assert updated_folder.id == created_folder.id  # ID should remain the same


@pytest.mark.asyncio
async def test_update_folder_partial(
    db: AgnosticDatabase, test_folder_data: dict
) -> None:
    """Test partial update of a folder"""
    # Create a folder first
    folder_in = FolderCreate(**test_folder_data)
    created_folder = await crud.folder.create(db, obj_in=folder_in)

    # Update only the name
    new_name = random_lower_string()
    update_data = FolderUpdate(name=new_name)
    updated_folder = await crud.folder.update(
        db, db_obj=created_folder, obj_in=update_data
    )

    assert updated_folder.name == new_name
    assert (
        updated_folder.description == test_folder_data["description"]
    )  # Should remain unchanged
    assert updated_folder.owner == test_folder_data["owner"]  # Should remain unchanged


@pytest.mark.asyncio
async def test_delete_folder(db: AgnosticDatabase, test_folder_data: dict) -> None:
    """Test deleting a folder"""
    # Create a folder first
    folder_in = FolderCreate(**test_folder_data)
    created_folder = await crud.folder.create(db, obj_in=folder_in)

    # Delete the folder
    await crud.folder.engine.delete(created_folder)

    # Verify the folder is deleted
    retrieved_folder = await crud.folder.get(db, id=created_folder.id)
    assert retrieved_folder is None


@pytest.mark.asyncio
async def test_list_folders(db: AgnosticDatabase, test_folder_data: dict) -> None:
    """Test listing folders"""
    # Create multiple folders
    folders = []
    for _ in range(3):
        folder_in = FolderCreate(**test_folder_data)
        folder = await crud.folder.create(db, obj_in=folder_in)
        folders.append(folder)

    # List all folders
    all_folders = await crud.folder.get_multi(db)
    assert len(all_folders) >= len(folders)  # There might be other folders in the DB

    # Verify our created folders are in the list
    created_ids = {folder.id for folder in folders}
    listed_ids = {folder.id for folder in all_folders}
    assert created_ids.issubset(listed_ids)


@pytest.mark.asyncio
async def test_list_folders_with_pagination(
    db: AgnosticDatabase, test_folder_data: dict
) -> None:
    """Test listing folders with pagination"""
    # Create multiple folders
    folders = []
    for _ in range(5):
        folder_in = FolderCreate(**test_folder_data)
        folder = await crud.folder.create(db, obj_in=folder_in)
        folders.append(folder)

    # List folders with pagination
    page = 0
    page_break = True
    paginated_folders = await crud.folder.get_multi(
        db, page=page, page_break=page_break
    )
    assert len(paginated_folders) <= 100  # Default MULTI_MAX setting
