from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from dtos.base import BaseDTO
from entities.base import BaseEntity
from repositories.base import BaseRepository
from schemas.base import BaseCreateSchema
from utils.exceptions import SchemaAndDTOMissingException

TEntity = TypeVar("TEntity", bound=BaseEntity)
TRepository = TypeVar("TRepository", bound=BaseRepository)
TDTO = TypeVar("TDTO", bound=BaseDTO)
TCreateSchema = TypeVar("TCreateSchema", bound=BaseCreateSchema)


class BaseService(
    ABC, Generic[TEntity, TRepository, TDTO, TCreateSchema]
):
    _repository: type[TRepository]
    _entity: type[TEntity]
    _dto: type[TDTO]

    async def get_all(self, db: AsyncSession) -> list[TDTO]:
        entities = await self._repository.get_all(db)
        return [self._dto.from_entity(entity) for entity in entities]

    async def get_by_id(self, db: AsyncSession, entity_id: int) -> TDTO | None:
        entity = await self._repository.get_by_id(db, entity_id)
        if not entity:
            return None
        return self._dto.from_entity(entity)

    async def create(
        self,
        db: AsyncSession,
        user_id: int,
        schema: TCreateSchema | None = None,
        dto: TDTO | None = None,
    ) -> TDTO:
        if not schema and not dto:
            raise SchemaAndDTOMissingException()
        if not dto:
            dto = self._dto.from_schema(schema)
        entity = dto.to_entity(self._entity)
        setattr(entity, "created_by", user_id)
        saved_entity = await self._repository.save(db, entity)
        return self._dto.from_entity(saved_entity)

    async def update(
        self,
        db: AsyncSession,
        entity_id: int,
        user_id: int,
        schema: TCreateSchema | None = None,
        dto: TDTO | None = None,
    ) -> TDTO | None:
        if not schema and not dto:
            raise SchemaAndDTOMissingException()
        entity = await self._repository.get_by_id(db, entity_id)
        if not entity:
            return None
        if not dto:
            dto = self._dto.from_schema(schema)
        for key, value in dto.model_dump(exclude_unset=True).items():
            setattr(entity, key, value)
        setattr(entity, "updated_by", user_id)
        updated_entity = await self._repository.save(db, entity)
        return self._dto.from_entity(updated_entity)

    async def delete(self, db: AsyncSession, entity_id: int, user_id: int) -> bool:
        entity = await self._repository.get_by_id(db, entity_id)
        if not entity:
            return False
        setattr(entity, "modified_by", user_id)
        return await self._repository.delete(db, entity)
