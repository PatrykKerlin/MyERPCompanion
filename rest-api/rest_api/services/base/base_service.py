from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from entities.base import BaseEntity
from repositories.base import BaseRepository
from schemas.base import BaseCreateSchema, BaseResponseSchema
from utils.exceptions import ConflictException

TEntity = TypeVar("TEntity", bound=BaseEntity)
TRepository = TypeVar("TRepository", bound=BaseRepository)
TCreateSchema = TypeVar("TCreateSchema", bound=BaseCreateSchema)
TResponseSchema = TypeVar("TResponseSchema", bound=BaseResponseSchema)


class BaseService(ABC, Generic[TEntity, TRepository, TCreateSchema, TResponseSchema]):
    _repository_cls: type[TRepository]
    _entity_cls: type[TEntity]
    _response_schema_cls: type[TResponseSchema]

    async def get_all(self, session: AsyncSession) -> list[TResponseSchema]:
        entities = await self._repository_cls.get_all(session)
        return [self._response_schema_cls.model_validate(entity) for entity in entities]

    async def get_by_id(
        self, session: AsyncSession, entity_id: int
    ) -> TResponseSchema | None:
        entity = await self._repository_cls.get_by_id(session, entity_id)
        if not entity:
            return None
        return self._response_schema_cls.model_validate(entity)

    async def create(
        self, session: AsyncSession, user_id: int, schema: TCreateSchema
    ) -> TResponseSchema:
        entity = self._entity_cls(**schema.model_dump())
        setattr(entity, "created_by", user_id)
        try:
            saved_entity = await self._repository_cls.save(session, entity)
        except IntegrityError:
            raise ConflictException()
        return self._response_schema_cls.model_validate(saved_entity)

    async def update(
        self, session: AsyncSession, entity_id: int, user_id: int, schema: TCreateSchema
    ) -> TResponseSchema | None:
        entity = await self._repository_cls.get_by_id(session, entity_id)
        if not entity:
            return None
        for key, value in schema.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)
        setattr(entity, "updated_by", user_id)
        try:
            updated_entity = await self._repository_cls.save(session, entity)
        except IntegrityError:
            raise ConflictException()
        return self._response_schema_cls.model_validate(updated_entity)

    async def delete(self, session: AsyncSession, entity_id: int, user_id: int) -> bool:
        entity = await self._repository_cls.get_by_id(session, entity_id)
        if not entity:
            return False
        setattr(entity, "modified_by", user_id)
        return await self._repository_cls.delete(session, entity)
