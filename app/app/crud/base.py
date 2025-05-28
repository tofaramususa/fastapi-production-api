# explanation of each line -- https://grok.com/share/bGVnYWN5_b4040978-daaf-4e37-85c1-d2665ecac081
from typing import Any, Dict, Generic, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from motor.core import AgnosticDatabase
from odmantic import AIOEngine

from app.database.base_class import Base
from app.core.config import settings
from app.database.session import get_engine

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.engine: AIOEngine = get_engine()

    async def get(self, db: AgnosticDatabase, id: Any) -> ModelType | None:
        return await self.engine.find_one(self.model, self.model.id == id)

    async def get_multi(
        self, db: AgnosticDatabase, *, page: int = 0, page_break: bool = False
    ) -> list[ModelType]:  # noqa
        offset = (
            {"skip": page * settings.MULTI_MAX, "limit": settings.MULTI_MAX}
            if page_break
            else {}
        )  # noqa
        return await self.engine.find(self.model, **offset)

    async def create(
        self, db: AgnosticDatabase, *, obj_in: CreateSchemaType
    ) -> ModelType:  # noqa
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        return await self.engine.save(db_obj)

    async def update(
        self,
        db: AgnosticDatabase,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],  # noqa
    ) -> ModelType:
        # Get update data from either dict or Pydantic model
        update_data = (
            obj_in
            if isinstance(obj_in, dict)
            else obj_in.model_dump(exclude_unset=True)
        )

        # Update only the fields that are present in update_data
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # Save the updated object
        await self.engine.save(db_obj)
        return db_obj

    async def remove(self, db: AgnosticDatabase, *, id: int) -> ModelType:
        obj = await self.model.get(id)
        if obj:
            await self.engine.delete(obj)
        return obj
