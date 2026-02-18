from abc import ABC
from collections.abc import Mapping
from decimal import Decimal
from typing import Generic, Sequence, TypeVar

from models.base.base_model import BaseModel
from repositories.base.base_repository import BaseRepository
from schemas.base.base_schema import BasePlainSchema, BaseStrictSchema
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

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
        filters: Mapping[str, str] | None = None,
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
        total = await self._repository_cls._count_all(session=session, params_filters=filters)
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
        loaded_model = await self._repository_cls.get_one_by_id(session, saved_model.id)
        if not loaded_model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=saved_model.id))
        return self._output_schema_cls.model_validate(loaded_model)

    async def create_bulk(
        self, session: AsyncSession, created_by: int, schemas: list[TInputSchema]
    ) -> list[TOutputSchema]:
        if not schemas:
            return []
        models: list[TModel] = []
        for schema in schemas:
            model = self._model_cls(**schema.model_dump())
            setattr(model, "created_by", created_by)
            models.append(model)
        saved_models = await self._repository_cls.save_many(session, models)
        saved_ids = [model.id for model in saved_models]
        loaded_models = await self._repository_cls.get_many_by_ids(session, saved_ids)
        loaded_by_id = {model.id: model for model in loaded_models}
        return [
            self._output_schema_cls.model_validate(loaded_by_id[model_id])
            for model_id in saved_ids
            if model_id in loaded_by_id
        ]

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
        loaded_model = await self._repository_cls.get_one_by_id(session, updated_model.id)
        if not loaded_model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=updated_model.id))
        return self._output_schema_cls.model_validate(loaded_model)

    async def update_bulk(
        self, session: AsyncSession, items: Sequence[tuple[int, TInputSchema]], modified_by: int
    ) -> list[TOutputSchema]:
        if not items:
            return []
        ids = [item[0] for item in items]
        models = list(await self._repository_cls.get_many_by_ids(session=session, model_ids=ids))
        existing_by_id = {model.id: model for model in models}
        missing_ids = {model_id for model_id in ids if model_id not in existing_by_id.keys()}
        if missing_ids:
            raise NoResultFound(
                self._not_found_message.format(model=self._model_cls.__name__, id=str(sorted(missing_ids)))
            )
        for model_id, schema in items:
            model = existing_by_id[model_id]
            for key, value in schema.model_dump(exclude_unset=True).items():
                setattr(model, key, value)
            setattr(model, "modified_by", modified_by)
        updated_models = await self._repository_cls.save_many(session=session, models=list(existing_by_id.values()))
        updated_ids = [model.id for model in updated_models]
        loaded_models = await self._repository_cls.get_many_by_ids(session, updated_ids)
        loaded_by_id = {model.id: model for model in loaded_models}
        return [
            self._output_schema_cls.model_validate(loaded_by_id[model_id])
            for model_id in updated_ids
            if model_id in loaded_by_id
        ]

    async def delete(self, session: AsyncSession, model_id: int, modified_by: int) -> None:
        model = await self._repository_cls.get_one_by_id(session, model_id)
        if not model:
            raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=model_id))
        setattr(model, "modified_by", modified_by)
        await self._repository_cls.delete(session, model)

    async def delete_bulk(self, session: AsyncSession, model_ids: list[int], modified_by: int) -> None:
        if not model_ids:
            return
        ids = list(set(model_ids))
        models = list(await self._repository_cls.get_many_by_ids(session=session, model_ids=ids))
        existing_ids = {model.id for model in models}
        missing_ids = [model_id for model_id in ids if model_id not in existing_ids]
        if missing_ids:
            raise NoResultFound(
                self._not_found_message.format(model=self._model_cls.__name__, id=str(sorted(missing_ids)))
            )
        for model in models:
            setattr(model, "modified_by", modified_by)
        await self._repository_cls.delete_many(session, models)

    @staticmethod
    def _to_float(value: Decimal | float | int | None) -> float:
        if value is None:
            return 0
        return float(value)
