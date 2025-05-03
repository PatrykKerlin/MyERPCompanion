from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.core import Setting, SettingKey
from repositories.base import BaseRepository


class SettingRepository(BaseRepository[Setting]):
    _model_cls = Setting

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.key),
            with_loader_criteria(SettingKey, cls._expr(SettingKey.is_active == True)),
        )
