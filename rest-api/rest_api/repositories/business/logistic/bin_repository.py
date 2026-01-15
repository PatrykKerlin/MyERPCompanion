from collections.abc import Mapping

from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.business.logistic import AssocBinItem, Bin, Item
from repositories.base.base_repository import BaseRepository


class BinRepository(BaseRepository[Bin]):
    _model_cls = Bin

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
            selectinload(cls._model_cls.bin_items).selectinload(AssocBinItem.item),
            selectinload(cls._model_cls.warehouse),
            with_loader_criteria(AssocBinItem, cls._expr(AssocBinItem.is_active.is_(True))),
            with_loader_criteria(Item, cls._expr(Item.is_active.is_(True))),
        )
