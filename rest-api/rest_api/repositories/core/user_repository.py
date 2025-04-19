from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from entities.core import Group, User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    _entity_cls = User

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(User.groups),
            with_loader_criteria(Group, cls._expr(Group.is_active == True)),
        )

    @classmethod
    async def get_by_username(cls, session: AsyncSession, username: str) -> User | None:
        query = super()._build_query([cls._expr(User.username == username)])
        result = await session.execute(query)
        return result.scalars().first()
