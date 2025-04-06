from collections.abc import Sequence
from typing import Generic, TypeVar, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ClauseElement, ColumnElement

from entities.base import BaseEntity

TEntity = TypeVar("TEntity", bound=BaseEntity)


class BaseRepository(Generic[TEntity]):
    _model_cls: type[TEntity]

    @classmethod
    def _build_query(
        cls, additional_filters: list[ColumnElement[bool]] | None = None
    ) -> Select:
        filters = [cls._model_cls.is_active == True]
        if additional_filters:
            filters.extend(additional_filters)
        return select(cls._model_cls).filter(*filters)

    @staticmethod
    def _expr(expression: ClauseElement | bool) -> ColumnElement[bool]:
        return cast(ColumnElement[bool], expression)

    @classmethod
    async def get_all(cls, session: AsyncSession) -> Sequence[TEntity]:
        query = cls._build_query()
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, entity_id: int) -> TEntity | None:
        query = cls._build_query([cls._expr(cls._model_cls.id == entity_id)])
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
        await session.commit()
        return True
