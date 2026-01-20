from typing import Mapping

from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.business.trade.assoc_order_status import AssocOrderStatus
from models.business.trade.order import Order
from models.business.trade.status import Status
from repositories.base.base_repository import BaseRepository


class StatusRepository(BaseRepository[Status]):
    _model_cls = Status

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
            selectinload(cls._model_cls.status_orders).selectinload(AssocOrderStatus.order),
            with_loader_criteria(AssocOrderStatus, cls._expr(AssocOrderStatus.is_active.is_(True))),
            with_loader_criteria(Order, cls._expr(Order.is_active.is_(True))),
        )
