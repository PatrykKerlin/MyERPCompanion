from collections.abc import Mapping, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.core import Language, Translation
from repositories.base.base_repository import BaseRepository


class TranslationRepository(BaseRepository[Translation]):
    _model_cls = Translation

    @classmethod
    async def get_all_by_language(
        cls, session: AsyncSession, language: str, offset: int, limit: int
    ) -> Sequence[Translation]:
        additional_filters = cls.__language_filter(language)
        query = cls._build_query(additional_filters=additional_filters).offset(offset).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def count_all_by_language(cls, session: AsyncSession, language: str) -> int:
        additional_filters = cls.__language_filter(language)
        return await cls._count_all(session=session, additional_filters=additional_filters)

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
            with_loader_criteria(Language, cls._expr(Language.is_active.is_(True))),
        )

    @classmethod
    def __language_filter(cls, language: str) -> list[ColumnElement[bool]]:
        return [cls._expr(cls._model_cls.language.has(Language.symbol == language))]
