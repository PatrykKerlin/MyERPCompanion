from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from models.base import BaseModel
from repositories.base import BaseRepository
from schemas.base import BaseInputSchema, BaseOutputSchema
from utils.exceptions import ConflictException, SaveException

TModel = TypeVar("TModel", bound=BaseModel)
TRepository = TypeVar("TRepository", bound=BaseRepository)
TInputSchema = TypeVar("TInputSchema", bound=BaseInputSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BaseOutputSchema)


class BaseService(ABC, Generic[TModel, TRepository, TInputSchema, TOutputSchema]):
    _repository_cls: type[TRepository]
    _model_cls: type[TModel]
    _output_schema_cls: type[TOutputSchema]

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

    async def get_by_id(self, session: AsyncSession, model_id: int) -> TOutputSchema | None:
        model = await self._repository_cls.get_by_id(session, model_id)
        if not model:
            return None
        return self._output_schema_cls.model_validate(model)

    async def create(self, session: AsyncSession, user_id: int, schema: TInputSchema) -> TOutputSchema:
        model = self._model_cls(**schema.model_dump())
        setattr(model, "created_by", user_id)
        try:
            saved_model = await self._repository_cls.save(session, model)
            if not saved_model:
                raise SQLAlchemyError()
        except IntegrityError:
            raise ConflictException()
        except Exception:
            raise SaveException()
        return self._output_schema_cls.model_validate(saved_model)

    async def update(
        self, session: AsyncSession, model_id: int, user_id: int, schema: TInputSchema
    ) -> TOutputSchema | None:
        model = await self._repository_cls.get_by_id(session, model_id)
        if not model:
            return None
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(model, key, value)
        setattr(model, "updated_by", user_id)
        try:
            updated_model = await self._repository_cls.save(session, model)
            if not updated_model:
                raise SQLAlchemyError()
        except IntegrityError:
            raise ConflictException()
        except Exception:
            raise SaveException()
        return self._output_schema_cls.model_validate(updated_model)

    async def delete(self, session: AsyncSession, model_id: int, user_id: int) -> bool:
        model = await self._repository_cls.get_by_id(session, model_id)
        if not model:
            return False
        setattr(model, "modified_by", user_id)
        return await self._repository_cls.delete(session, model)
