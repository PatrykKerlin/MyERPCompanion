from abc import ABC, abstractmethod
from inspect import isawaitable
from typing import List, Type

from dtos.base import BaseDTO
from entities.base import BaseEntity
from repositories.base import BaseRepository
from schemas.base import BaseCreateSchema
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService(ABC):
    def __init__(
        self,
        repository: Type[BaseRepository],
        entity: Type[BaseEntity],
        dto: Type[BaseDTO],
    ) -> None:
        self.repository = repository
        self.entity = entity
        self.dto = dto

    async def get_all(self, db: AsyncSession) -> List[BaseDTO]:
        entities = await self.repository.get_all(db)
        return [self.dto.from_entity(entity) for entity in entities]

    async def get_by_id(self, db: AsyncSession, entity_id: int) -> BaseDTO | None:
        entity = await self.repository.get_by_id(db, entity_id)
        return self.dto.from_entity(entity) if entity else None

    async def create(
        self, db: AsyncSession, schema: BaseCreateSchema, user_id: int
    ) -> BaseDTO:
        entity = self.entity()
        result = self.__class__._set_attrs(db, entity, schema)
        if isawaitable(result):
            entity = await result
        else:
            entity = result
        entity.created_by = user_id
        entity = await self.repository.save(db, entity)
        return self.dto.from_entity(entity)

    async def update(
        self, db: AsyncSession, entity_id: int, schema: BaseCreateSchema, user_id: int
    ) -> BaseDTO | None:
        entity = await self.repository.get_by_id(db, entity_id)
        if not entity:
            return None
        result = self.__class__._set_attrs(db, entity, schema)
        if isawaitable(result):
            entity = await result
        else:
            entity = result
        entity.updated_by = user_id
        entity = await self.repository.save(db, entity)
        return self.dto.from_entity(entity)

    async def delete(self, db: AsyncSession, entity_id: int, user_id: int) -> bool:
        entity = await self.repository.get_by_id(db, entity_id)
        if not entity:
            return False
        entity.modified_by = user_id
        result = await self.repository.delete(db, entity)
        return result

    @staticmethod
    @abstractmethod
    def _set_attrs(
        db: AsyncSession, model: Type[BaseEntity], schema: BaseCreateSchema
    ) -> BaseEntity:
        pass
