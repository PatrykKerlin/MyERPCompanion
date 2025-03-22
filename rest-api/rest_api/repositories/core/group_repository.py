from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria

from entities.core import Group


class GroupRepository:
    @classmethod
    async def get_by_id(cls, db: AsyncSession, user_id: int) -> Group | None:
        query = select(Group).filter(Group.id == user_id, Group.is_active == True)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def get_all(cls, db: AsyncSession) -> List[Group | None]:
        query = select(Group).filter(Group.is_active == True)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_all_by_names(
        cls, db: AsyncSession, names: List[str]
    ) -> List[Group | None]:
        query = select(Group).filter(Group.is_active == True, Group.name.in_(names))
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def save(cls, db: AsyncSession, group: Group) -> Group:
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return group

    @classmethod
    async def update(cls, db: AsyncSession, group: Group) -> Group:
        await db.commit()
        await db.refresh(group)
        return group

    @classmethod
    async def delete(cls, db: AsyncSession, group: Group) -> bool:
        group.is_active = False
        await db.commit()
        await db.refresh(group)
        return True
