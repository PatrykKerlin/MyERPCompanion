from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from models.base import BaseModel
from repositories.base import BaseRepository
from schemas.base import BasePlainSchema, BaseStrictSchema

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

    async def _handle_assoc_table(
        self,
        session: AsyncSession,
        owner_model: TModel,
        assoc_repo_cls: type[BaseRepository],
        model_cls: type[BaseModel],
        owner_field: str,
        related_field: str,
        owner_id: int,
        related_ids: list[int],
        related_repo_cls: type[BaseRepository],
        created_by: int | None = None,
        modified_by: int | None = None,
    ) -> None:
        existing_assoc_models = await assoc_repo_cls.get_all(
            session, filters=[assoc_repo_cls._expr(getattr(model_cls, owner_field) == owner_id)]
        )
        existing_related_ids = {getattr(assoc, related_field) for assoc in existing_assoc_models}
        new_related_ids = set(related_ids)
        ids_to_add = new_related_ids - existing_related_ids
        ids_to_drop = existing_related_ids - new_related_ids

        for assoc_model in existing_assoc_models:
            if getattr(assoc_model, related_field) in ids_to_drop:
                if modified_by:
                    setattr(assoc_model, "modified_by", modified_by)
                await assoc_repo_cls.delete(session, assoc_model, False)

        for index, id_to_add in enumerate(ids_to_add, start=1):
            related_model = await related_repo_cls.get_one_by_id(session, id_to_add)
            if not related_model:
                raise NoResultFound(self._not_found_message.format(model=self._model_cls.__name__, id=id_to_add))
            assoc_model = model_cls(
                **{owner_field: owner_id, related_field: related_model.id, "created_by": created_by}
            )
            await assoc_repo_cls.save(session, assoc_model, False)

        await self._repository_cls.commit(session)
        await self._repository_cls.refresh(session, owner_model)
