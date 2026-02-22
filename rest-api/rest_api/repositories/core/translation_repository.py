from collections.abc import Mapping, Sequence

from models.core import Translation
from repositories.base.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement


class TranslationRepository(BaseRepository[Translation]):
    _model_cls = Translation

    @classmethod
    async def get_all_by_language_id(
        cls, session: AsyncSession, language_id: int, offset: int, limit: int
    ) -> Sequence[Translation]:
        additional_filters = [cls._expr(cls._model_cls.language_id == language_id)]
        query = cls._build_query(additional_filters=additional_filters).offset(offset).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def count_all_by_language_id(cls, session: AsyncSession, language_id: int) -> int:
        additional_filters = [cls._expr(cls._model_cls.language_id == language_id)]
        return await cls._count_all(session=session, additional_filters=additional_filters)

    @classmethod
    def _build_query(
        cls,
        params_filters: Mapping[str, str] | None = None,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        return super()._build_query(params_filters, additional_filters, sort_by, sort_order)
