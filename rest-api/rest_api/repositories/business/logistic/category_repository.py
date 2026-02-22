from typing import Mapping

from models.business.logistic.category import Category
from models.business.trade.assoc_category_discount import AssocCategoryDiscount
from models.business.trade.discount import Discount
from repositories.base.base_repository import BaseRepository
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement


class CategoryRepository(BaseRepository[Category]):
    _model_cls = Category

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
            selectinload(cls._model_cls.category_discounts).selectinload(AssocCategoryDiscount.discount),
            with_loader_criteria(AssocCategoryDiscount, cls._expr(AssocCategoryDiscount.is_active.is_(True))),
            with_loader_criteria(Discount, cls._expr(Discount.is_active.is_(True))),
        )
