from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from entities.base import BaseEntity
from repositories.base import BaseRepository
from schemas.base import BaseInputSchema, BaseOutputSchema
from utils.exceptions import ConflictException, SaveException

TEntity = TypeVar("TEntity", bound=BaseEntity)
TRepository = TypeVar("TRepository", bound=BaseRepository)
TInputSchema = TypeVar("TInputSchema", bound=BaseInputSchema)
TOutputSchema = TypeVar("TOutputSchema", bound=BaseOutputSchema)


class BaseService(ABC, Generic[TEntity, TRepository, TInputSchema, TOutputSchema]):
    _repository_cls: type[TRepository]
    _entity_cls: type[TEntity]
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
        entities = await self._repository_cls.get_all(
            session=session,
            filters=filters,
            offset=offset,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        total = await self._repository_cls.count_all(session=session, filters=filters)
        schemas = [self._output_schema_cls.model_validate(entity) for entity in entities]
        return schemas, total

    async def get_by_id(self, session: AsyncSession, entity_id: int) -> TOutputSchema | None:
        entity = await self._repository_cls.get_by_id(session, entity_id)
        if not entity:
            return None
        return self._output_schema_cls.model_validate(entity)

    async def create(self, session: AsyncSession, user_id: int, schema: TInputSchema) -> TOutputSchema:
        entity = self._entity_cls(**schema.model_dump())
        setattr(entity, "created_by", user_id)
        try:
            saved_entity = await self._repository_cls.save(session, entity)
            if not saved_entity:
                raise SQLAlchemyError()
        except IntegrityError:
            raise ConflictException()
        except Exception:
            raise SaveException()
        return self._output_schema_cls.model_validate(saved_entity)

    async def update(
        self, session: AsyncSession, entity_id: int, user_id: int, schema: TInputSchema
    ) -> TOutputSchema | None:
        entity = await self._repository_cls.get_by_id(session, entity_id)
        if not entity:
            return None
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)
        setattr(entity, "updated_by", user_id)
        try:
            updated_entity = await self._repository_cls.save(session, entity)
            if not updated_entity:
                raise SQLAlchemyError()
        except IntegrityError:
            raise ConflictException()
        except Exception:
            raise SaveException()
        return self._output_schema_cls.model_validate(updated_entity)

    async def delete(self, session: AsyncSession, entity_id: int, user_id: int) -> bool:
        entity = await self._repository_cls.get_by_id(session, entity_id)
        if not entity:
            return False
        setattr(entity, "modified_by", user_id)
        return await self._repository_cls.delete(session, entity)
