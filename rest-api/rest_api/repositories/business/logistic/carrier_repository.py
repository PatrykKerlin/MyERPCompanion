from typing import Mapping

from models.business.logistic.carrier import Carrier
from models.business.logistic.delivery_method import DeliveryMethod
from repositories.base.base_repository import BaseRepository
from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement


class CarrierRepository(BaseRepository[Carrier]):
    _model_cls = Carrier

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
            selectinload(cls._model_cls.delivery_methods),
            with_loader_criteria(DeliveryMethod, cls._expr(DeliveryMethod.is_active.is_(True))),
        )
