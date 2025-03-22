from abc import ABC, abstractmethod
from typing import Generic, List, Type, TypeVar, cast

from sqlalchemy.ext.asyncio import AsyncSession

from dtos.base import BaseDTO
from entities.base import BaseEntity
from repositories.base import BaseRepository
from schemas.base import BaseCreateSchema, BaseUpdateSchema
from helpers.exceptions import SchemaAndDTOMissingException
from helpers.helpers import create_or_update_instance, get_instance_attributes

TEntity = TypeVar("TEntity", bound=BaseEntity)
TRepository = TypeVar("TRepository", bound=BaseRepository)
TDTO = TypeVar("TDTO", bound=BaseDTO)
TCreateSchema = TypeVar("TCreateSchema", bound=BaseCreateSchema)
TUpdateSchema = TypeVar("TUpdateSchema", bound=BaseUpdateSchema)


class BaseService(ABC, Generic[TEntity, TDTO, TCreateSchema]):
    def __init__(
        self,
        repository: Type[TRepository],
        entity: Type[TEntity],
        dto: Type[TDTO],
    ) -> None:
        self.repository = repository
        self.entity = entity
        self.dto = dto

    async def get_all(self, db: AsyncSession) -> List[TDTO]:
        entities = await self.repository.get_all(db)
        return [cast(TDTO, self.dto.from_entity(entity)) for entity in entities]

    async def get_by_id(self, db: AsyncSession, entity_id: int) -> TDTO | None:
        entity = await self.repository.get_by_id(db, entity_id)
        return cast(TDTO, self.dto.from_entity(entity)) if entity else None

    async def create(
        self, db: AsyncSession, user_id: int, schema: TUpdateSchema | None = None, dto: TDTO | None = None
    ) -> TDTO:
        if not schema and not dto:
            raise SchemaAndDTOMissingException()
        if schema:
            dto = UserDTO.from_schema(schema)
        entity = create_or_update_instance(TEntity, get_instance_attributes(dto))
        entity = cast(TEntity, entity)
        setattr(entity, "created_by", user_id)
        saved_entity = await self.repository.save(db, entity)
        saved_dto = self.dto.from_entity(saved_entity)
        saved_dto = cast(TDTO, saved_dto)
        saved_dto.call_all_deleters()
        return saved_dto

    async def update(
        self, db: AsyncSession, entity_id: int, user_id: int, schema: TUpdateSchema | None = None,
        dto: TDTO | None = None
    ) -> TDTO | None:
        if not schema and not dto:
            raise SchemaAndDTOMissingException()
        entity = await self.repository.get_by_id(db, entity_id)
        entity = cast(TEntity, entity)
        if not entity:
            return None
        if schema:
            dto = UserDTO.from_schema(schema)
        entity = create_or_update_instance(TEntity, get_instance_attributes(dto), entity)
        setattr(entity, "updated_by", user_id)
        updated_entity = await self.repository.save(db, entity)
        updated_dto = self.dto.from_entity(updated_entity)
        updated_dto = cast(TDTO, updated_dto)
        updated_dto.call_all_deleters()
        return updated_entity

    async def delete(self, db: AsyncSession, entity_id: int, user_id: int) -> bool:
        entity = await self.repository.get_by_id(db, entity_id)
        if not entity:
            return False
        setattr(entity, "modified_by", user_id)
        result = await self.repository.delete(db, entity)
        return result
