from typing import Mapping

from models.business.logistic.assoc_bin_item import AssocBinItem
from models.business.logistic.item import Item
from models.business.trade.assoc_item_discount import AssocItemDiscount
from models.core.image import Image
from repositories.base.base_repository import BaseRepository
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement


class ItemRepository(BaseRepository[Item]):
    _model_cls = Item

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
            selectinload(cls._model_cls.images),
            selectinload(cls._model_cls.item_bins),
            selectinload(cls._model_cls.item_discounts),
            with_loader_criteria(Image, cls._expr(Image.is_active.is_(True))),
            with_loader_criteria(AssocBinItem, cls._expr(AssocBinItem.is_active.is_(True))),
            with_loader_criteria(AssocItemDiscount, cls._expr(AssocItemDiscount.is_active.is_(True))),
        )
