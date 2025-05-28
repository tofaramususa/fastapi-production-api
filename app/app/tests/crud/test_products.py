from fastapi.encoders import jsonable_encoder
from motor.core import AgnosticDatabase
import pytest
from typing import List
from datetime import datetime
from app import crud
from app.schemas.product import ProductCreate, ProductUpdate, Product
from app.tests.utils.utils import random_lower_string
from odmantic import ObjectId


@pytest.fixture
def test_product_data() -> dict:
    """Fixture to provide test product data"""
    return {
        "name": random_lower_string(),
        "description": random_lower_string(),
        "folder_id": ObjectId(),
        "owner": random_lower_string(),
    }


@pytest.mark.asyncio
async def test_create_product(db: AgnosticDatabase) -> None:
    """Test basic product creation"""
    name = random_lower_string()
    description = random_lower_string()
    folder_id = ObjectId()
    owner = random_lower_string()
    product_in = ProductCreate(
        name=name, description=description, folder_id=folder_id, owner=owner
    )
    product = await crud.products.create(db, obj_in=product_in)
    assert product.name == name
    assert product.description == description
    assert product.folder_id == folder_id
    assert product.owner == owner
    assert isinstance(product.createdAt, datetime)
    assert isinstance(product.modifiedAt, datetime)


@pytest.mark.asyncio
async def test_create_product_minimal_data(db: AgnosticDatabase) -> None:
    """Test product creation with minimal required data"""
    name = random_lower_string()
    folder_id = ObjectId()
    product_in = ProductCreate(name=name, folder_id=folder_id)
    product = await crud.products.create(db, obj_in=product_in)
    assert product.name == name
    assert product.folder_id == folder_id
    assert product.description == ""  # Default value
    assert product.owner == ""  # Default value


@pytest.mark.asyncio
async def test_get_product(db: AgnosticDatabase, test_product_data: dict) -> None:
    """Test retrieving a product"""
    # Create a product first
    product_in = ProductCreate(**test_product_data)
    created_product = await crud.products.create(db, obj_in=product_in)

    # Get the product
    retrieved_product = await crud.products.get(db, id=created_product.id)
    assert retrieved_product is not None
    assert retrieved_product.name == test_product_data["name"]
    assert retrieved_product.description == test_product_data["description"]
    assert retrieved_product.folder_id == test_product_data["folder_id"]
    assert retrieved_product.owner == test_product_data["owner"]


@pytest.mark.asyncio
async def test_get_nonexistent_product(db: AgnosticDatabase) -> None:
    """Test retrieving a non-existent product"""
    nonexistent_id = ObjectId()
    retrieved_product = await crud.products.get(db, id=nonexistent_id)
    assert retrieved_product is None


@pytest.mark.asyncio
async def test_update_product(db: AgnosticDatabase, test_product_data: dict) -> None:
    """Test updating a product"""
    # Create a product first
    product_in = ProductCreate(**test_product_data)
    created_product = await crud.products.create(db, obj_in=product_in)

    # Update the product
    new_name = random_lower_string()
    new_description = random_lower_string()
    update_data = ProductUpdate(name=new_name, description=new_description)
    updated_product = await crud.products.update(
        db, db_obj=created_product, obj_in=update_data
    )

    assert updated_product.name == new_name
    assert updated_product.description == new_description
    assert (
        updated_product.folder_id == test_product_data["folder_id"]
    )  # Should remain unchanged
    assert (
        updated_product.owner == test_product_data["owner"]
    )  # Should remain unchanged
    assert updated_product.id == created_product.id  # ID should remain the same


@pytest.mark.asyncio
async def test_update_product_partial(
    db: AgnosticDatabase, test_product_data: dict
) -> None:
    """Test partial update of a product"""
    # Create a product first
    product_in = ProductCreate(**test_product_data)
    created_product = await crud.products.create(db, obj_in=product_in)

    # Update only the name
    new_name = random_lower_string()
    update_data = ProductUpdate(name=new_name)
    updated_product = await crud.products.update(
        db, db_obj=created_product, obj_in=update_data
    )

    assert updated_product.name == new_name
    assert (
        updated_product.description == test_product_data["description"]
    )  # Should remain unchanged
    assert (
        updated_product.folder_id == test_product_data["folder_id"]
    )  # Should remain unchanged
    assert (
        updated_product.owner == test_product_data["owner"]
    )  # Should remain unchanged


@pytest.mark.asyncio
async def test_delete_product(db: AgnosticDatabase, test_product_data: dict) -> None:
    """Test deleting a product"""
    # Create a product first
    product_in = ProductCreate(**test_product_data)
    created_product = await crud.products.create(db, obj_in=product_in)

    # Delete the product
    await crud.products.engine.delete(created_product)

    # Verify the product is deleted
    retrieved_product = await crud.products.get(db, id=created_product.id)
    assert retrieved_product is None


@pytest.mark.asyncio
async def test_list_products(db: AgnosticDatabase, test_product_data: dict) -> None:
    """Test listing products"""
    # Create multiple products
    products = []
    for _ in range(3):
        product_in = ProductCreate(**test_product_data)
        product = await crud.products.create(db, obj_in=product_in)
        products.append(product)

    # List all products
    all_products = await crud.products.get_multi(db)
    assert len(all_products) >= len(products)  # There might be other products in the DB

    # Verify our created products are in the list
    created_ids = {product.id for product in products}
    listed_ids = {product.id for product in all_products}
    assert created_ids.issubset(listed_ids)


@pytest.mark.asyncio
async def test_list_products_with_pagination(
    db: AgnosticDatabase, test_product_data: dict
) -> None:
    """Test listing products with pagination"""
    # Create multiple products
    products = []
    for _ in range(5):
        product_in = ProductCreate(**test_product_data)
        product = await crud.products.create(db, obj_in=product_in)
        products.append(product)

    # List products with pagination
    page = 0
    page_break = True
    paginated_products = await crud.products.get_multi(
        db, page=page, page_break=page_break
    )
    assert len(paginated_products) <= 100  # Default MULTI_MAX setting


@pytest.mark.asyncio
async def test_get_products_by_folder_id(
    db: AgnosticDatabase, test_product_data: dict
) -> None:
    """Test retrieving products by folder_id"""
    # Create multiple products in the same folder
    folder_id = ObjectId()
    products = []
    for _ in range(3):
        product_data = {**test_product_data, "folder_id": folder_id}
        product_in = ProductCreate(**product_data)
        product = await crud.products.create(db, obj_in=product_in)
        products.append(product)

    # Get products by folder_id
    folder_products = await crud.products.get_by_folder_id(db, folder_id=folder_id)
    assert len(folder_products) == len(products)

    # Verify all products belong to the correct folder
    for product in folder_products:
        assert product.folder_id == folder_id
