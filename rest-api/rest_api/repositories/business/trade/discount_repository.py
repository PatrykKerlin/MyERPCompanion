from collections.abc import Mapping

from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.business.logistic.category import Category
from models.business.logistic.item import Item
from models.business.trade.assoc_category_discount import AssocCategoryDiscount
from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
from models.business.trade.assoc_item_discount import AssocItemDiscount
from models.business.trade.customer import Customer
from models.business.trade.discount import Discount
from repositories.base.base_repository import BaseRepository


class DiscountRepository(BaseRepository[Discount]):
    _model_cls = Discount

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
            selectinload(cls._model_cls.discount_categories).selectinload(AssocCategoryDiscount.category),
            selectinload(cls._model_cls.discount_customers).selectinload(AssocCustomerDiscount.customer),
            selectinload(cls._model_cls.discount_items).selectinload(AssocItemDiscount.item),
            with_loader_criteria(AssocCategoryDiscount, cls._expr(AssocCategoryDiscount.is_active.is_(True))),
            with_loader_criteria(AssocCustomerDiscount, cls._expr(AssocCustomerDiscount.is_active.is_(True))),
            with_loader_criteria(AssocItemDiscount, cls._expr(AssocItemDiscount.is_active.is_(True))),
            with_loader_criteria(Category, cls._expr(Item.is_active.is_(True))),
            with_loader_criteria(Customer, cls._expr(Item.is_active.is_(True))),
            with_loader_criteria(Item, cls._expr(Item.is_active.is_(True))),
        )
