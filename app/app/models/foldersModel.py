from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from datetime import datetime
from pydantic import EmailStr, ConfigDict
from odmantic import ObjectId, Field

from app.database.base_class import Base

# if TYPE_CHECKING:
#     from . import Token


def datetime_now_sec():
    return datetime.now().replace(microsecond=0)


class Folders(Base):
    createdAt: datetime = Field(default_factory=datetime_now_sec)
    modifiedAt: datetime = Field(default_factory=datetime_now_sec)
    name: str = Field(...)
    description: str = Field(default="")
    products: list[ObjectId] = Field(
        default_factory=list
    )  # references to Product objects
    owner: str = Field(default="")
