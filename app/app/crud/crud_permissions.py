from typing import Any, Dict, Union, List

from motor.core import AgnosticDatabase
from odmantic import ObjectId
from app.crud.base import CRUDBase
from app.models import FolderPermission  # Updated model file
from app.schemas import (
    FolderPermissionCreate,
    FolderPermissionInDB,
    FolderPermissionUpdate,
)


class CRUDFolderPermission(
    CRUDBase[FolderPermission, FolderPermissionCreate, FolderPermissionUpdate]
):
    async def create(
        self, db: AgnosticDatabase, *, obj_in: FolderPermissionCreate
    ) -> FolderPermission:
        folder_permission = {
            **obj_in.model_dump(),  # Unpack all fields from obj_in
            "folder_id": obj_in.folder_id,  # Required (from FolderPermissionBase)
            "email": obj_in.email,  # Required (from FolderPermissionBase)
        }

        return await self.engine.save(FolderPermission(**folder_permission))

    async def update(
        self,
        db: AgnosticDatabase,
        *,
        db_obj: FolderPermission,
        obj_in: Union[FolderPermissionUpdate, Dict[str, Any]],
    ) -> FolderPermission:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def get_by_folder_id(
        self, db: AgnosticDatabase, folder_id: ObjectId
    ) -> List[FolderPermission]:
        """
        Retrieve all folder permissions with the specified folder_id
        """
        return await self.engine.find(self.model, self.model.folder_id == folder_id)

    async def get_by_email(self, email: str) -> List[FolderPermission]:
        """
        Retrieve all folder permissions for the specified email
        """
        return await self.engine.find(self.model, self.model.email == email)

    async def delete_by_folder_and_user(
        self, *, folder_id: ObjectId, email: str
    ) -> bool:
        """
        Delete a specific folder permission by folder_id and email
        Returns True if deleted, False if not found
        """
        permission = await self.engine.find_one(
            self.model,
            (self.model.folder_id == folder_id) & (self.model.email == email),
        )
        if permission:
            await self.engine.delete(permission)
            return True
        return False

    async def has_permission(self, *, folder_id: ObjectId, email: str) -> bool:
        """
        Check if a specific user has permission for a specific folder_id
        Returns True if a matching record exists, False otherwise
        """
        permission = await self.engine.find_one(
            self.model,
            (self.model.folder_id == folder_id) & (self.model.email == email),
        )
        return permission is not None

    async def get_by_folder_and_email(
        self, *, folder_id: ObjectId, email: str
    ) -> FolderPermission:
        """
        Get a specific folder permission by folder_id and email
        Returns the permission if found, None otherwise
        """
        return await self.engine.find_one(
            self.model,
            (self.model.folder_id == folder_id) & (self.model.email == email),
        )


folder_permissions = CRUDFolderPermission(FolderPermission)
