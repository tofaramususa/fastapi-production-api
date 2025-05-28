from __future__ import annotations
from typing import List
from datetime import datetime
from pydantic import EmailStr, ConfigDict
from odmantic import ObjectId, Field
from app.database.base_class import Base


def datetime_now_sec():
    return datetime.now().replace(microsecond=0)


class FolderPermission(Base):
    folder_id: ObjectId = Field(...)
    email: EmailStr = Field(...)
    # permissions: List[str] = Field(...)
    createdAt: datetime = Field(default_factory=datetime_now_sec)
    modifiedAt: datetime = Field(default_factory=datetime_now_sec)

    model_config = ConfigDict(
        extra="allow",
    )
