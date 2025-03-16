from typing import Generic, List, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression

from entities.base import BaseEntity

TEntity = TypeVar("TEntity", bound=BaseEntity)


class BaseRepository(Generic[TEntity]):
    model: Type[TEntity]

    @classmethod
    def _build_query(cls, additional_filters: List[BinaryExpression] | None = None) -> Select:
        filters: List[BinaryExpression] = [cls.model.is_active == True]
        if additional_filters:
            filters.extend(additional_filters)
        return select(cls.model).filter(*filters)

    @classmethod
    async def get_all(cls, db: AsyncSession) -> Sequence[TEntity]:
        query = cls._build_query()
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, entity_id: int) -> TEntity | None:
        query = cls._build_query([cls.model.id == entity_id])
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def save(cls, db: AsyncSession, entity: TEntity) -> TEntity | None:
        db.add(entity)
        await db.commit()
        return await cls.get_by_id(db, int(entity.id))

    @classmethod
    async def delete(cls, db: AsyncSession, entity: TEntity) -> bool:
        setattr(entity, "is_active", False)
        await db.commit()
        return True
