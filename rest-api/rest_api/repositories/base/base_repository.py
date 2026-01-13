from collections.abc import Mapping, Sequence
from typing import Generic, TypeVar, cast
from datetime import date, datetime, time

from sqlalchemy import String, asc, desc, func, select, Date, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_loader_criteria, InstrumentedAttribute
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ClauseElement, ColumnElement
from sqlalchemy.sql.schema import Column

from models.base.base_model import BaseModel
from models.core.user import User

TModel = TypeVar("TModel", bound=BaseModel)


class BaseRepository(Generic[TModel]):
    _model_cls: type[TModel]

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        offset: int,
        limit: int,
        filters: Mapping[str, str] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Sequence[TModel]:
        query = (
            cls._build_query(params_filters=filters, sort_by=sort_by, sort_order=sort_order).offset(offset).limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_one_by_id(cls, session: AsyncSession, model_id: int) -> TModel | None:
        query = cls._build_query(additional_filters=[cls._expr(cls._model_cls.id == model_id)])
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_many_by_ids(cls, session: AsyncSession, model_ids: list[int]) -> Sequence[TModel]:
        if len(model_ids) == 0:
            return []
        filters = [cls._expr(cls._model_cls.id.in_(list(set(model_ids))))]
        query = cls._build_query(additional_filters=filters, sort_by="id", sort_order="asc")
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def save(cls, session: AsyncSession, model: TModel) -> TModel:
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model

    @classmethod
    async def save_many(cls, session: AsyncSession, models: Sequence[TModel]) -> Sequence[TModel]:
        if not models:
            return []
        session.add_all(list(models))
        await session.commit()
        for model in models:
            await session.refresh(model)
        return models

    @classmethod
    async def delete(cls, session: AsyncSession, model: TModel) -> None:
        setattr(model, "is_active", False)
        await cls.__cascade_soft_delete(model)
        await session.commit()

    @classmethod
    async def delete_many(cls, session: AsyncSession, models: Sequence[TModel], commit: bool = True) -> None:
        if not models:
            return
        for model in models:
            setattr(model, "is_active", False)
            await cls.__cascade_soft_delete(model)
        await session.commit()

    @classmethod
    async def _count_all(
        cls,
        session: AsyncSession,
        params_filters: Mapping[str, str] | None = None,
        additional_filters: list[ColumnElement[bool]] | None = None,
    ) -> int:
        expressions = cls.__build_filter_expressions(
            filters_params=params_filters, additional_filters=additional_filters
        )
        query = select(func.count()).select_from(cls._model_cls).filter(*expressions)
        result = await session.execute(query)
        return result.scalar_one()

    @staticmethod
    def _expr(expression: ClauseElement | bool) -> ColumnElement[bool]:
        return cast(ColumnElement[bool], expression)

    @classmethod
    def _build_query(
        cls,
        params_filters: Mapping[str, str] | None = None,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        base_filters = [BaseRepository._expr(cls._model_cls.is_active.is_(True))]
        extra_filters = cls.__build_filters_from_params(params_filters)
        query_filters = [*base_filters, *extra_filters]

        if additional_filters:
            additional_filters.extend(query_filters)
        query = (
            select(cls._model_cls)
            .filter(*query_filters)
            .options(with_loader_criteria(User, cls._expr(User.is_active.is_(True))))
        )
        if sort_by and hasattr(cls._model_cls, sort_by):
            column = getattr(cls._model_cls, sort_by)
            if sort_order == "asc":
                query = query.order_by(asc(column))
            else:
                query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(getattr(cls._model_cls, "id")))
        return query

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

    @classmethod
    def __build_filter_expressions(
        cls,
        filters_params: Mapping[str, str] | None = None,
        additional_filters: list[ColumnElement[bool]] | None = None,
    ) -> list[ColumnElement[bool]]:
        base_filters = [cls._expr(cls._model_cls.is_active.is_(True))]
        params_filters = cls.__build_filters_from_params(filters_params)

        expressions = [*base_filters, *params_filters]
        if additional_filters:
            expressions.extend(additional_filters)

        return expressions

    @classmethod
    def __build_filters_from_params(cls, filters: Mapping[str, str] | None) -> list[ColumnElement[bool]]:
        if not filters:
            return []

        expressions: list[ColumnElement[bool]] = []

        for field_name, raw_value in filters.items():
            attribute = getattr(cls._model_cls, field_name, None)
            if not isinstance(attribute, InstrumentedAttribute):
                continue

            column_type = attribute.property.columns[0].type

            if isinstance(column_type, String):
                expressions.append(attribute.ilike(f"%{raw_value}%"))
                continue

            if isinstance(column_type, (Date, DateTime)):
                expressions.append(cls.__build_date_gte_expression(attribute, raw_value))
                continue

            expressions.append(attribute == raw_value)

        return expressions

    @classmethod
    def __build_date_gte_expression(cls, attribute: InstrumentedAttribute, raw_value: str) -> ColumnElement[bool]:
        date_part, separator, time_part = raw_value.partition(" ")

        date_parts = date_part.split("-")
        if len(date_parts) not in {1, 2, 3}:
            raise ValueError(
                f"Invalid date filter value: '{raw_value}'. Expected 'YYYY', 'YYYY-MM', 'YYYY-MM-DD', optionally with time 'HH:MM' or 'HH:MM:SS'."
            )

        year = int(date_parts[0])
        month = int(date_parts[1]) if len(date_parts) >= 2 else 1
        day = int(date_parts[2]) if len(date_parts) == 3 else 1

        start_date = date(year, month, day)

        column_type = attribute.property.columns[0].type
        if isinstance(column_type, DateTime):
            time_text = time_part.strip() if separator else ""
            if not time_text:
                start_time = time.min
            else:
                time_parts = time_text.split(":")
                if len(time_parts) not in {2, 3}:
                    raise ValueError(f"Invalid time filter value: '{raw_value}'. Expected 'HH:MM' or 'HH:MM:SS'.")
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                second = int(time_parts[2]) if len(time_parts) == 3 else 0
                start_time = time(hour, minute, second)

            return attribute >= datetime.combine(start_date, start_time)

        if isinstance(column_type, Date):
            return attribute >= start_date

        raise ValueError(f"Field '{attribute.key}' is not a date/datetime column.")
