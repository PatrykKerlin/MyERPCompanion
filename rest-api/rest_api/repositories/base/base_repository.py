from collections.abc import Sequence
from typing import Generic, TypeVar, cast

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ClauseElement, ColumnElement

from entities.base import Base, BaseEntity

TEntity = TypeVar("TEntity", bound=BaseEntity)


class BaseRepository(Generic[TEntity]):
    _entity_cls: type[TEntity]

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        filters = [cls._entity_cls.is_active == True]
        if additional_filters:
            filters.extend(additional_filters)
        query = select(cls._entity_cls).filter(*filters)
        if sort_by and hasattr(cls._entity_cls, sort_by):
            column = getattr(cls._entity_cls, sort_by)
            if sort_order == "asc":
                query = query.order_by(asc(column))
            else:
                query = query.order_by(desc(column))
        return query

    @staticmethod
    def _expr(expression: ClauseElement | bool) -> ColumnElement[bool]:
        return cast(ColumnElement[bool], expression)

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        filters: list[ColumnElement[bool]] | None = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Sequence[TEntity]:
        query = cls._build_query(filters, sort_by, sort_order).offset(offset).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, entity_id: int) -> TEntity | None:
        query = cls._build_query([cls._expr(cls._entity_cls.id == entity_id)])
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def save(cls, session: AsyncSession, entity: TEntity) -> TEntity | None:
        session.add(entity)
        await session.commit()
        return await cls.get_by_id(session, int(entity.id))

    @classmethod
    async def delete(cls, session: AsyncSession, entity: TEntity) -> bool:
        setattr(entity, "is_active", False)
        await cls.__cascade_soft_delete(entity)
        await session.commit()
        return True

    @classmethod
    async def count_all(cls, session: AsyncSession, filters: list[ColumnElement[bool]] | None = None) -> int:
        query = select(func.count()).select_from(cls._entity_cls).filter(cls._expr(cls._entity_cls.is_active == True))
        if filters:
            for filter in filters:
                query = query.filter(cls._expr(filter))
        result = await session.execute(query)
        return result.scalar_one()

    @classmethod
    async def __cascade_soft_delete(cls, entity: TEntity) -> None:
        for relation in cls._entity_cls.__mapper__.relationships:
            if not relation.info.get("cascade_soft_delete", False):
                continue
            related = getattr(entity, relation.key)
            if related is None:
                continue
            if isinstance(related, (Sequence, set)) and not isinstance(related, (str, bytes)):
                for obj in related:
                    if hasattr(obj, "is_active"):
                        setattr(obj, "is_active", False)
            else:
                if hasattr(related, "is_active"):
                    setattr(related, "is_active", False)
