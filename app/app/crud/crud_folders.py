from typing import Any, Dict, Union

from motor.core import AgnosticDatabase

from app.crud.base import CRUDBase
from app.models.foldersModel import Folders
from app.schemas.folder import FolderCreate, FolderInDB, FolderUpdate


class CRUDFolders(CRUDBase[Folders, FolderCreate, FolderUpdate]):
    async def create(self, db: AgnosticDatabase, *, obj_in: FolderCreate) -> Folders:
        folder = {
            **obj_in.model_dump(),  # Unpack all fields from obj_in
            "name": obj_in.name,  # Optional (from FolderBase)
            "description": obj_in.description,  # Optional (from FolderBase)
            "owner": obj_in.owner
            if obj_in.owner is not None
            else "",  # Optional, defaults to ""
            "products": obj_in.products
            if obj_in.products is not None
            else [],  # Optional, defaults to None
        }

        return await self.engine.save(Folders(**folder))

    # async def update(self, db: AgnosticDatabase, *, db_obj: Folders, obj_in: Union[FolderUpdate, Dict[str, Any]]) -> Folders: # noqa
    #     if isinstance(obj_in, dict):
    #         update_data = obj_in
    #     else:
    #         update_data = obj_in.model_dump(exclude_unset=True)
    #     return await super().update(db, db_obj=db_obj, obj_in=update_data)


folder = CRUDFolders(Folders)
