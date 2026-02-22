from typing import Mapping

from models.business.trade import AssocCustomerDiscount, Customer, Discount
from repositories.base.base_repository import BaseRepository
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement


class CustomerRepository(BaseRepository[Customer]):
    _model_cls = Customer

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
            selectinload(cls._model_cls.customer_discounts).selectinload(AssocCustomerDiscount.discount),
            selectinload(cls._model_cls.user),
            with_loader_criteria(AssocCustomerDiscount, cls._expr(AssocCustomerDiscount.is_active.is_(True))),
            with_loader_criteria(Discount, cls._expr(Discount.is_active.is_(True))),
        )
