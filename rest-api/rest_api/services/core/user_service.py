from sqlalchemy.ext.asyncio import AsyncSession

from dtos.core import UserDTO
from entities.core import User
from repositories.core import GroupRepository, UserRepository
from schemas.core import UserCreate, UserUpdate
from services.base import BaseService
from services.core import AuthService


class UserService(BaseService):
    _dto = UserDTO
    _entity = User
    _repository = UserRepository

    async def create(
        self,
        db: AsyncSession,
        user_id: int,
        schema: UserCreate | None = None,
        dto: UserDTO | None = None,
    ) -> UserDTO | None:
        if not dto:
            dto = await self.__prepare_dto(db, schema)
        created_dto = await super().create(db, user_id, dto=dto)
        return created_dto

    async def update(
        self,
        db: AsyncSession,
        entity_id: int,
        user_id: int,
        schema: UserUpdate | None = None,
        dto: UserDTO | None = None,
    ) -> UserDTO | None:
        entity = await self.repository.get_by_id(db, entity_id)
        if not entity:
            return None
        if not dto:
            dto = await self.__prepare_dto(db, schema, exclude_unset=True)
        updated_dto = await super().update(db, entity_id, user_id, dto=dto)
        return updated_dto

    @classmethod
    async def __prepare_dto(
        cls,
        db: AsyncSession,
        schema: UserCreate | UserUpdate,
        exclude_unset: bool = False
    ) -> UserDTO:
        data = schema.dict(exclude_unset=exclude_unset)
        if "groups" in data:
            groups = await GroupRepository.get_all_by_names(db, data["groups"])
            data["groups"] = groups
        if "password" in data:
            data["password"] = AuthService.get_password_hash(data["password"])
        return cls._dto.from_schema(data)
