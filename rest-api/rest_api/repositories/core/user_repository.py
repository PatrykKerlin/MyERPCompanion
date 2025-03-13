from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria
from models.core import User, Group


class UserRepository:
    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int) -> User | None:
        query = (
            select(User)
            .filter(User.id == user_id, User.is_active == True)
            .options(
                selectinload(User.groups),
                with_loader_criteria(Group, Group.is_active == True)
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_by_name(cls, db: AsyncSession, user_name: int) -> User | None:
        query = (
            select(User)
            .filter(User.username == user_name, User.is_active == True)
            .options(
                selectinload(User.groups),
                with_loader_criteria(Group, Group.is_active == True)
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_all(cls, db: AsyncSession) -> List[User]:
        query = (
            select(User)
            .filter(User.is_active == True)
            .options(
                selectinload(User.groups),
                with_loader_criteria(Group, Group.is_active == True)
            )
        )
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def save(cls, db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.commit()
        # await db.refresh(user)
        user = await cls.get_by_id(db, user.id)
        return user

    @classmethod
    async def update(cls, db: AsyncSession, user: User) -> User:
        await db.commit()
        # await db.refresh(user)
        user = await cls.get_by_id(db, user.id)
        return user

    @classmethod
    async def delete(cls, db: AsyncSession, user: User) -> bool:
        user.is_active = False
        await db.commit()
        await db.refresh(user)
        return True
