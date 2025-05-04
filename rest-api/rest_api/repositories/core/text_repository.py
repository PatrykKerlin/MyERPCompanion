from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.core import Text, Setting, SettingKey
from repositories.base import BaseRepository


class TextRepository(BaseRepository[Text]):
    _model_cls = Text

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.language).selectinload(Setting.key),
            with_loader_criteria(Setting, cls._expr(Setting.is_active == True)),
            with_loader_criteria(SettingKey, cls._expr(SettingKey.is_active == True)),
        )

    @classmethod
    async def get_all_by_language(
        cls,
        session: AsyncSession,
        language: str,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Text]:
        filters = [
            cls._expr(SettingKey.key == "language"),
            cls._expr(Setting.value == language),
        ]
        query = cls._build_query(filters)
        query = query.join(cls._model_cls.language).join(Setting.key).filter(*filters).offset(offset).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
