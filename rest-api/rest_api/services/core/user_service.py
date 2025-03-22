from sqlalchemy.ext.asyncio import AsyncSession

from dtos.core import UserDTO
from entities.core import User
from repositories.core import GroupRepository, UserRepository
from schemas.core import UserCreate, UserUpdate
from services.base import BaseService
from services.core import AuthService


class UserService(BaseService):
    def __init__(self):
        super().__init__(UserRepository, User, UserDTO)

    async def create(
        self, db: AsyncSession, user_id: int, schema: UserCreate | None = None, dto: UserDTO | None = None
    ) -> UserDTO | None:
        create_data = schema.dict()
        if "groups" in create_data:
            groups = await GroupRepository.get_all_by_names(db, create_data["groups"])
            create_data["groups"] = groups
        if "password" in create_data:
            create_data["password"] = AuthService.get_password_hash(create_data["password"])
        if not dto:
            dto = UserDTO.from_schema(create_data)

        return super().update(db, user_id, dto=dto)

    async def update(
        self, db: AsyncSession, entity_id: int, user_id: int, schema: UserUpdate | None = None,
        dto: UserDTO | None = None
    ) -> UserDTO | None:
        entity = await self.repository.get_by_id(db, entity_id)
        if not entity:
            return None
        update_data = schema.dict(exclude_unset=True)
        if "groups" in update_data:
            groups = await GroupRepository.get_all_by_names(db, update_data["groups"])
            update_data["groups"] = groups
        if "password" in update_data:
            update_data["password"] = AuthService.get_password_hash(update_data["password"])
        if not dto:
            dto = UserDTO.from_schema(update_data)

        return super().update(db, entity_id, user_id, dto=dto)
