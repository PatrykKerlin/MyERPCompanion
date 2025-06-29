from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.core import Language, Translation
from repositories.base import BaseRepository


class TranslationRepository(BaseRepository[Translation]):
    _model_cls = Translation

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.language),
            with_loader_criteria(Language, cls._expr(Language.is_active == True)),
        )
