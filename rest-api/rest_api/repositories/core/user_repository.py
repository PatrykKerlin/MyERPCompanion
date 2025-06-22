from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.core import AssocUserGroup, Group, Language, Theme, User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    _model_cls = User

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.user_groups).selectinload(AssocUserGroup.group),
            selectinload(cls._model_cls.language),
            selectinload(cls._model_cls.theme),
            with_loader_criteria(Group, cls._expr(Group.is_active == True)),
            with_loader_criteria(Language, cls._expr(Language.is_active == True)),
            with_loader_criteria(Theme, cls._expr(Theme.is_active == True)),
        )

    @classmethod
    async def get_one_by_username(cls, session: AsyncSession, username: str) -> User | None:
        query = super()._build_query([cls._expr(cls._model_cls.username == username)])
        result = await session.execute(query)
        return result.scalars().first()
