from dtos.core import UserDTO
from entities.core import User
from repositories.core import GroupRepository, UserRepository
from schemas.core import UserCreate
from services.base import BaseService
from services.core import AuthService
from sqlalchemy.ext.asyncio import AsyncSession


class UserService(BaseService):
    def __init__(self):
        super().__init__(UserRepository, User, UserDTO)

    @staticmethod
    async def _set_attrs(db: AsyncSession, user: User, user_data: UserCreate):
        for key, value in user_data.dict().items():
            if key == "password":
                setattr(user, key, AuthService.get_password_hash(value))
            if key == "groups":
                continue
            else:
                setattr(user, key, value)
        groups = await GroupRepository.get_all_by_names(db, user_data.groups)
        user.groups = groups
        return user
