from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.core import Group


class GroupService:
    @classmethod
    async def create_group(cls, db: AsyncSession, name: str) -> Group:
        group = Group(name=name)
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return group

    @classmethod
    async def get_all_groups(cls, db: AsyncSession) -> list:
        result = await db.execute(select(Group))
        return result.scalars().all()
