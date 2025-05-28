from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from odmantic import ObjectId
from app.schemas.base_schema import BaseSchema
from app.schemas.product import Product  # Add import for Product schema


# Base Folder model for shared properties
class FolderBase(BaseModel):
    name: str
    description: str = ""


# Properties to receive via API on creation
class FolderCreate(FolderBase):
    owner: Optional[str] = ""
    products: Optional[List[str]] = None


# Properties to receive via API on update
class FolderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None


# Model for product operations within folders
class FolderProductOperation(BaseModel):
    product_ids: List[str]  # may need to change this to list[ObjectID]


# Properties stored in DB
class FolderInDBBase(BaseModel):
    id: ObjectId | None = None
    name: str
    description: str
    createdAt: datetime
    modifiedAt: datetime
    products: List[ObjectId] = Field(default_factory=list)
    owner: str


# Additional properties stored in DB
class FolderInDB(FolderInDBBase):
    pass


# Additional properties to return via API
class Folder(BaseModel):
    id: str
    name: str
    description: str
    createdAt: datetime
    modifiedAt: datetime
    products: List[str] = []
    owner: str = ""

    model_config = ConfigDict(
        from_attributes=True, exclude_none=True, exclude_unset=True
    )

    @classmethod
    def from_db_model(cls, db_model):
        """
        Convert a MongoDB document model to a Folder schema
        Handles ObjectId conversion and field name mapping
        """
        return cls(
            id=str(db_model.id),  # Convert ObjectId to string
            name=db_model.name,
            description=db_model.description,
            createdAt=db_model.createdAt,  # Map 'created' to 'createdAt'
            modifiedAt=db_model.modifiedAt,  # Map 'modified' to 'modifiedAt'
            # products=db_model.products if hasattr(db_model, "products") else [],
            owner=db_model.owner if hasattr(db_model, "owner") else "",
        )


# Response model for listing folders
class FolderList(BaseModel):
    items: List[Folder]
    total: int


# Response model for navigation endpoint
class NavigationResponse(BaseModel):
    folders: List[Folder]
    products: List[Product]

    model_config = ConfigDict(
        from_attributes=True, exclude_none=True, exclude_unset=True
    )
