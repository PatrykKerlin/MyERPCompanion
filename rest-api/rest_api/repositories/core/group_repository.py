from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from entities.core import Group
from repositories.base import BaseRepository


class GroupRepository(BaseRepository):
    _model = Group

    @classmethod
    async def get_all_by_names(
        cls, db: AsyncSession, names: list[str]
    ) -> Sequence[Group]:
        filters = [cls._expr(Group.name.in_(names))]
        query = cls._build_query(filters)
        result = await db.execute(query)
        return result.scalars().all()
