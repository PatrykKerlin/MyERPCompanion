from collections.abc import Mapping, Sequence
from datetime import date, datetime, time, timedelta
from typing import Generic, TypeVar, cast

from sqlalchemy import Date, DateTime, String, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute, selectinload, with_loader_criteria
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
        loaded = await cls.get_one_by_id(session, model.id)
        return loaded if loaded is not None else model

    @classmethod
    async def save_many(cls, session: AsyncSession, models: Sequence[TModel]) -> Sequence[TModel]:
        if not models:
            return []
        session.add_all(list(models))
        await session.commit()
        ids = [model.id for model in models]
        loaded_models = await cls.get_many_by_ids(session, ids)
        loaded_by_id = {model.id: model for model in loaded_models}
        return [loaded_by_id.get(model_id, model) for model_id, model in zip(ids, models, strict=False)]

    @classmethod
    async def delete(cls, session: AsyncSession, model: TModel) -> None:
        loaded_model = await cls.__get_with_cascade(session, model.id)
        if loaded_model is None:
            return
        setattr(loaded_model, "is_active", False)
        await cls.__cascade_soft_delete(loaded_model)
        await session.commit()

    @classmethod
    async def delete_many(cls, session: AsyncSession, models: Sequence[TModel]) -> None:
        if not models:
            return
        ids = [model.id for model in models]
        loaded_models = await cls.__get_many_with_cascade(session, ids)
        for model in loaded_models:
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
            query_filters.extend(additional_filters)
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
    def __cascade_load_options(cls) -> list:
        options = []
        for relation in cls._model_cls.__mapper__.relationships:
            if relation.info.get("cascade_soft_delete", False):
                options.append(selectinload(getattr(cls._model_cls, relation.key)))
        return options

    @classmethod
    async def __get_with_cascade(cls, session: AsyncSession, model_id: int) -> TModel | None:
        query = select(cls._model_cls).filter(cls._model_cls.id == model_id).options(*cls.__cascade_load_options())
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def __get_many_with_cascade(cls, session: AsyncSession, model_ids: list[int]) -> Sequence[TModel]:
        if not model_ids:
            return []
        query = (
            select(cls._model_cls)
            .filter(cls._model_cls.id.in_(list(set(model_ids))))
            .options(*cls.__cascade_load_options())
        )
        result = await session.execute(query)
        return result.scalars().all()

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
                expressions.append(cls.__build_date_filter_expression(attribute, str(raw_value)))
                continue

            expressions.append(attribute == raw_value)

        return expressions

    @classmethod
    def __build_date_filter_expression(cls, attribute: InstrumentedAttribute, raw_value: str) -> ColumnElement[bool]:
        date_part, separator, time_part = raw_value.strip().partition(" ")

        date_parts = date_part.split("-")
        if len(date_parts) not in {1, 2, 3}:
            raise ValueError(
                f"Invalid date filter value: '{raw_value}'. Expected 'YYYY', 'YYYY-MM', 'YYYY-MM-DD', optionally with time 'HH:MM' or 'HH:MM:SS'."
            )

        year = int(date_parts[0])
        month = int(date_parts[1]) if len(date_parts) >= 2 else 1
        day = int(date_parts[2]) if len(date_parts) == 3 else 1

        column_type = attribute.property.columns[0].type

        if isinstance(column_type, DateTime):
            time_parts: list[str] | None = None

            if separator and time_part.strip():
                time_parts = time_part.strip().split(":")
                if len(time_parts) not in {2, 3}:
                    raise ValueError(f"Invalid time filter value: '{raw_value}'. Expected 'HH:MM' or 'HH:MM:SS'.")

                hour = int(time_parts[0])
                minute = int(time_parts[1])
                second = int(time_parts[2]) if len(time_parts) == 3 else 0
                start_time = time(hour, minute, second)
            else:
                start_time = time.min

            start_dt = datetime.combine(date(year, month, day), start_time)

            if len(date_parts) == 1:
                end_dt = datetime(year + 1, 1, 1)
            elif len(date_parts) == 2:
                end_dt = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
            else:
                if time_parts is None:
                    end_dt = start_dt + timedelta(days=1)
                elif len(time_parts) == 2:
                    end_dt = start_dt + timedelta(minutes=1)
                else:
                    end_dt = start_dt + timedelta(seconds=1)

            return (attribute >= start_dt) & (attribute < end_dt)

        if isinstance(column_type, Date):
            start_d = date(year, month, day)

            if len(date_parts) == 1:
                end_d = date(year + 1, 1, 1)
            elif len(date_parts) == 2:
                end_d = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
            else:
                end_d = start_d + timedelta(days=1)

            return (attribute >= start_d) & (attribute < end_d)

        raise ValueError(f"Field '{attribute.key}' is not a date/datetime column.")
