from collections.abc import Sequence
from typing import Generic, TypeVar, cast

from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ClauseElement, ColumnElement
from sqlalchemy.sql.schema import Column

from models.base import BaseModel

TModel = TypeVar("TModel", bound=BaseModel)


class BaseRepository(Generic[TModel]):
    _model_cls: type[TModel]

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        filters = [cls._model_cls.is_active == True]
        if additional_filters:
            filters.extend(additional_filters)
        query = select(cls._model_cls).filter(*filters)
        if sort_by and hasattr(cls._model_cls, sort_by):
            column = getattr(cls._model_cls, sort_by)
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
    ) -> Sequence[TModel]:
        query = cls._build_query(filters, sort_by, sort_order).offset(offset).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_one_by_id(cls, session: AsyncSession, model_id: int) -> TModel | None:
        query = cls._build_query([cls._expr(cls._model_cls.id == model_id)])
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def save(cls, session: AsyncSession, model: TModel, commit: bool = True) -> TModel | None:
        session.add(model)
        if commit:
            await session.commit()
        else:
            await session.flush()
        return await cls.get_one_by_id(session, int(model.id))

    @classmethod
    async def delete(cls, session: AsyncSession, model: TModel) -> bool:
        setattr(model, "is_active", False)
        await cls.__cascade_soft_delete(model)
        await session.commit()
        return True

    @classmethod
    async def count_all(cls, session: AsyncSession, filters: list[ColumnElement[bool]] | None = None) -> int:
        query = select(func.count()).select_from(cls._model_cls).filter(cls._expr(cls._model_cls.is_active == True))
        if filters:
            for filter in filters:
                query = query.filter(cls._expr(filter))
        result = await session.execute(query)
        return result.scalar_one()

    @classmethod
    async def __cascade_soft_delete(cls, model: TModel) -> None:
        for relation in cls._model_cls.__mapper__.relationships:
            if not relation.info.get("cascade_soft_delete", False):
                continue
            related = getattr(model, relation.key)
            if related is None:
                continue
            is_nullable = all(isinstance(column, Column) and column.nullable for column in relation.local_columns)
            if is_nullable:
                if relation.uselist:
                    setattr(model, relation.key, [])
                else:
                    setattr(model, relation.key, None)
                continue
            related_items = (
                related if isinstance(related, (Sequence, set)) and not isinstance(related, (str, bytes)) else [related]
            )
            for item in related_items:
                setattr(item, "is_active", False)
                setattr(item, "modified_by", model.modified_by)
