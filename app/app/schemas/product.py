from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from odmantic import ObjectId
from app.schemas.base_schema import BaseSchema


# Base Product model for shared properties
class ProductBase(BaseSchema):
    name: str
    description: str = ""


# Properties to receive via API on creation
class ProductCreate(ProductBase):
    folder_id: ObjectId
    owner: Optional[str] = ""


# Properties to receive via API on update
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    folder_id: Optional[str] = None
    owner: Optional[str] = None


# Properties stored in DB
class ProductInDBBase(BaseModel):
    id: ObjectId | None = None
    name: str
    description: str
    folder_id: ObjectId
    createdAt: datetime
    modifiedAt: datetime
    owner: str


# Additional properties stored in DB
class ProductInDB(ProductInDBBase):
    pass


# Additional properties to return via API
class Product(BaseSchema):
    id: str
    name: str
    description: str
    folder_id: str
    createdAt: datetime
    modifiedAt: datetime
    owner: str = ""

    model_config = ConfigDict(
        from_attributes=True, exclude_none=True, exclude_unset=True
    )

    @classmethod
    def from_db_model(cls, db_model):
        """
        Convert a MongoDB document model to a Product schema
        Handles ObjectId conversion and field name mapping
        """
        return cls(
            id=str(db_model.id),
            name=db_model.name,
            description=db_model.description,
            folder_id=str(db_model.folder_id),
            createdAt=db_model.createdAt,
            modifiedAt=db_model.modifiedAt,
            owner=db_model.owner if hasattr(db_model, "owner") else "",
        )


# Response model for listing products
class ProductList(BaseSchema):
    items: List[Product]
    total: int
