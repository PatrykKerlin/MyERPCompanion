from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.business import Carrier, DeliveryMethod, Unit
from repositories.base import BaseRepository


class DeliveryMethodRepository(BaseRepository[DeliveryMethod]):
    _model_cls = DeliveryMethod

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.carrier),
            selectinload(cls._model_cls.unit),
            with_loader_criteria(Carrier, cls._expr(Carrier.is_active == True)),
            with_loader_criteria(Unit, cls._expr(Unit.is_active == True)),
        )
