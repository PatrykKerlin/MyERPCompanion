from abc import ABC, abstractmethod
from inspect import isawaitable
from typing import Generic, List, Type, TypeVar, cast

from sqlalchemy.ext.asyncio import AsyncSession

from dtos.base import BaseDTO
from entities.base import BaseEntity
from repositories.base import BaseRepository
from schemas.base import BaseCreateSchema

TEntity = TypeVar("TEntity", bound=BaseEntity)
TRepository = TypeVar("TRepository", bound=BaseRepository)
TDTO = TypeVar("TDTO", bound=BaseDTO)
TCreate = TypeVar("TCreate", bound=BaseCreateSchema)


class BaseService(ABC, Generic[TEntity, TDTO, TCreate]):
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
        self, db: AsyncSession, schema: TCreate, user_id: int
    ) -> TDTO:
        entity = self.entity()
        result = self.__class__._set_attrs(db, entity, schema)
        if isawaitable(result):
            entity = await result
        else:
            entity = result
        entity = cast(TEntity, entity)
        setattr(entity, "created_by", user_id)
        saved_entity = await self.repository.save(db, entity)
        if saved_entity is None:
            raise ValueError("Entity could not be saved")
        entity = saved_entity
        return cast(TDTO, self.dto.from_entity(entity))

    async def update(
        self, db: AsyncSession, entity_id: int, schema: TCreate, user_id: int
    ) -> TDTO | None:
        entity = await self.repository.get_by_id(db, entity_id)
        if not entity:
            return None
        result = self.__class__._set_attrs(db, entity, schema)
        if isawaitable(result):
            entity = await result
        else:
            entity = result
        entity = cast(TEntity, entity)
        setattr(entity, "updated_by", user_id)
        entity = await self.repository.save(db, entity)
        return cast(TDTO, self.dto.from_entity(entity))

    async def delete(self, db: AsyncSession, entity_id: int, user_id: int) -> bool:
        entity = await self.repository.get_by_id(db, entity_id)
        if not entity:
            return False
        setattr(entity, "modified_by", user_id)
        result = await self.repository.delete(db, entity)
        return result

    @staticmethod
    @abstractmethod
    def _set_attrs(
        db: AsyncSession, model: TEntity, schema: TCreate
    ) -> TEntity:
        pass
