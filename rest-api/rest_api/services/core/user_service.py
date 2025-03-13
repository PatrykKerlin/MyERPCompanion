from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria
from models.core import User, Group
from dtos.core import UserDTO
from schemas.core import UserCreate
from services.core import AuthService
from repositories.core import UserRepository, GroupRepository


class UserService:
    @classmethod
    async def get_users(cls, db: AsyncSession) -> List[UserDTO]:
        users = await UserRepository.get_all(db)
        dtos = [UserDTO.from_entity(user) for user in users]
        return dtos

    @classmethod
    async def get_user(cls, db: AsyncSession, user_id: int) -> UserDTO | None:
        user = await UserRepository.get_by_id(db, user_id)
        dto = UserDTO.from_entity(user) if user else None
        return dto

    @classmethod
    async def create_user(cls, db: AsyncSession, user_data: UserCreate, current_user_id: int) -> UserDTO:
        new_user = User()
        new_user = await cls.__set_user_attrs(db, new_user, user_data)
        new_user.created_by = current_user_id
        saved_user = await UserRepository.save(db, new_user)
        dto = UserDTO.from_entity(saved_user)
        return dto

    @classmethod
    async def update_user(cls, db: AsyncSession, user_id: int, user_data: UserCreate,
                          current_user_id: int) -> UserDTO | None:
        user = await UserRepository.get_by_id(db, user_id)
        if user is None:
            return None
        user = await cls.__set_user_attrs(db, user, user_data)
        user.updated_by = current_user_id
        updated_user = await UserRepository.save(db, user)
        dto = UserDTO.from_entity(updated_user)
        return dto

    @classmethod
    async def delete_user(cls, db: AsyncSession, user_id: int, current_user_id: int) -> bool:
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            return False
        user.modified_by = current_user_id
        result = await UserRepository.delete(db, user)
        return result

    @classmethod
    async def __set_user_attrs(cls, db: AsyncSession, user: User, user_data: UserCreate):
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
