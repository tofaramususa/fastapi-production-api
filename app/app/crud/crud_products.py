from typing import Any, Dict, Union, List

from motor.core import AgnosticDatabase

from app.crud.base import CRUDBase
from app.models.product.productsModel import Products
from app.schemas.product import ProductCreate, ProductInDB, ProductUpdate


class CRUDProducts(CRUDBase[Products, ProductCreate, ProductUpdate]):
    async def create(self, db: AgnosticDatabase, *, obj_in: ProductCreate) -> Products:
        product = {
            **obj_in.model_dump(),
            "name": obj_in.name,
            "description": obj_in.description,
            "folder_id": obj_in.folder_id,
            "owner": obj_in.owner if obj_in.owner is not None else "",
        }

        return await self.engine.save(Products(**product))

    async def get_by_folder_id(
        self, db: AgnosticDatabase, folder_id: Any
    ) -> List[Products]:
        """
        Retrieve all products with the specified folder_id
        """
        return await self.engine.find(self.model, self.model.folder_id == folder_id)


products = CRUDProducts(Products)
