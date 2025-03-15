from typing import Any, List, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression


class BaseRepository:
    _model: Type[Any] = None

    def __init_subclass__(cls, model: Type[Any] = None, **kwargs):
        if model is not None:
            cls._model = model
        super().__init_subclass__(**kwargs)
        if cls._model is None:
            raise NotImplementedError(
                f"Class {cls.__name__} must set the _model attribute"
            )

    @classmethod
    def _build_query(
        cls, additional_filters: List[BinaryExpression] | None = None
    ) -> Select:
        filters = [cls._model.is_active == True]
        if additional_filters:
            filters.extend(additional_filters)
        return select(cls._model).filter(*filters)

    @classmethod
    async def get_all(cls, db: AsyncSession) -> List[Any]:
        query = cls._build_query()
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, entity_id: int) -> Any | None:
        query = cls._build_query([cls._model.id == entity_id])
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def save(cls, db: AsyncSession, entity: Any) -> Any:
        db.add(entity)
        await db.commit()
        return await cls.get_by_id(db, entity.id)

    @classmethod
    async def delete(cls, db: AsyncSession, entity: Any) -> bool:
        entity.is_active = False
        await db.commit()
        return True
