from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement

from models.business import Carrier, Currency
from repositories.base import BaseRepository


class CarrierRepository(BaseRepository[Carrier]):
    _model_cls = Carrier

    @classmethod
    def _build_query(
        cls,
        additional_filters: list[ColumnElement[bool]] | None = None,
        sort_by: str | None = None,
        sort_order: str = "asc",
    ) -> Select:
        query = super()._build_query(additional_filters, sort_by, sort_order)
        return query.options(
            selectinload(cls._model_cls.currency),
            with_loader_criteria(Currency, cls._expr(Currency.is_active.is_(True))),
        )
