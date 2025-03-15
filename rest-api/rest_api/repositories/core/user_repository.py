from typing import List

from entities.core import Group, User
from repositories.base import BaseRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql.elements import BinaryExpression


class UserRepository(BaseRepository, model=User):
    @classmethod
    def _build_query(cls, additional_filters: List[BinaryExpression] | None = None):
        query = super()._build_query(additional_filters)
        return query.options(
            selectinload(User.groups),
            with_loader_criteria(Group, Group.is_active == True),
        )

    @classmethod
    async def get_by_name(cls, db: AsyncSession, user_name: int) -> User | None:
        query = super()._build_query([User.username == user_name])
        result = await db.execute(query)
        return result.scalars().first()
