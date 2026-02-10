from collections.abc import Mapping

from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.core import AssocUserGroup, Group, Language, User
from repositories.base.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    _model_cls = User

    @classmethod
    async def get_one_by_username(cls, session, username: str) -> User | None:
        query = cls._build_query(additional_filters=[cls._expr(cls._model_cls.username == username)])
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    def _build_query(
        cls,
        params_filters: Mapping[str, str] | None = None,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(params_filters, additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.language),
            selectinload(cls._model_cls.user_groups).selectinload(AssocUserGroup.group),
            with_loader_criteria(AssocUserGroup, cls._expr(AssocUserGroup.is_active.is_(True))),
            with_loader_criteria(Group, cls._expr(Group.is_active.is_(True))),
            with_loader_criteria(Language, cls._expr(Language.is_active.is_(True))),
        )
