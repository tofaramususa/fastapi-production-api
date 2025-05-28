from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from odmantic import ObjectId


# Base FolderPermission model for shared properties
class FolderPermissionBase(BaseModel):
    folder_id: ObjectId
    email: EmailStr


# Properties to receive via API on creation
class FolderPermissionCreate(FolderPermissionBase):
    pass


# Properties to receive via API on update
class FolderPermissionUpdate(BaseModel):
    folder_id: Optional[ObjectId] = None
    email: Optional[EmailStr] = None


# Properties stored in DB
class FolderPermissionInDBBase(BaseModel):
    id: ObjectId | None = None
    folder_id: ObjectId
    email: EmailStr
    createdAt: datetime
    modifiedAt: datetime


# Additional properties stored in DB
class FolderPermissionInDB(FolderPermissionInDBBase):
    pass


# Additional properties to return via API
class FolderPermission(BaseModel):
    id: str
    folder_id: str  # String representation for API
    email: EmailStr
    createdAt: datetime
    modifiedAt: datetime

    model_config = ConfigDict(
        from_attributes=True, exclude_none=True, exclude_unset=True
    )

    @classmethod
    def from_db_model(cls, db_model):
        """
        Convert a MongoDB document model to a FolderPermission schema
        Handles ObjectId conversion and field name mapping
        """
        return cls(
            id=str(db_model.id),  # Convert ObjectId to string
            folder_id=str(db_model.folder_id),  # Convert ObjectId to string
            email=db_model.email,
            createdAt=db_model.createdAt,
            modifiedAt=db_model.modifiedAt,
        )


# Response model for listing folder permissions
class FolderPermissionList(BaseModel):
    items: List[FolderPermission]
    total: int
