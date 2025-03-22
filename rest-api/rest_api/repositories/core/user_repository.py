from typing import List, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression

from entities.core import Group, User
from repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

    @classmethod
    def _build_query(cls, additional_filters: List[BinaryExpression] | None = None) -> Select:
        query = super()._build_query(additional_filters)
        return query.options(
            selectinload(User.groups),
            with_loader_criteria(Group, Group.is_active == True),
        )

    @classmethod
    async def get_by_name(cls, db: AsyncSession, user_name: str) -> User | None:
        query = super()._build_query([cast(BinaryExpression, User.username == user_name)])
        result = await db.execute(query)
        return result.scalars().first()
