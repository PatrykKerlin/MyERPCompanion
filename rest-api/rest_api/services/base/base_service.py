from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from models.base.base_model import BaseModel
from repositories.base.base_repository import BaseRepository
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema

TModel = TypeVar("TModel", bound=BaseModel)
TRepository = TypeVar("TRepository", bound=BaseRepository)
TInputSchema = TypeVar("TInputSchema", bound=BaseStrictSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BasePlainSchema)


class BaseService(ABC, Generic[TModel, TRepository, TInputSchema, TOutputSchema]):
    _repository_cls: type[TRepository]
    _model_cls: type[TModel]
    _output_schema_cls: type[TOutputSchema]

    def __init__(self) -> None:
        self._not_found_message = "{model} with ID {id} not found."

    async def get_all(
        self,
        session: AsyncSession,
        filters: list[ColumnElement[bool]] | None = None,
        offset: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> tuple[list[TOutputSchema], int]:
        models = await self._repository_cls.get_all(
            session=session,
            filters=filters,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        total = await self._repository_cls.count_all(session=session, filters=filters)
        schemas = [self._output_schema_cls.model_validate(model) for model in models]
        return schemas, total

    async def get_one_by_id(self, session: AsyncSession, model_id: int) -> TOutputSchema:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        return self._output_schema_cls.model_validate(model)

    async def get_many_by_ids(self, session: AsyncSession, model_ids: list[int]) -> list[TOutputSchema]:
        models = await self._repository_cls.get_many_by_ids(session=session, model_ids=model_ids)
        return [self._output_schema_cls.model_validate(model) for model in models]

    async def create(self, session: AsyncSession, created_by: int, schema: TInputSchema) -> TOutputSchema:
        model = self._model_cls(**schema.model_dump())
        setattr(model, "created_by", created_by)
        saved_model = await self._repository_cls.save(session, model)
        return self._output_schema_cls.model_validate(saved_model)

    async def update(
        self, session: AsyncSession, model_id: int, modified_by: int, schema: TInputSchema
    ) -> TOutputSchema:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(model, key, value)
        setattr(model, "modified_by", modified_by)
        updated_model = await self._repository_cls.save(session, model)
        return self._output_schema_cls.model_validate(updated_model)

    async def delete(self, session: AsyncSession, model_id: int, modified_by: int) -> None:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        setattr(model, "modified_by", modified_by)
        await self._repository_cls.delete(session, model)
