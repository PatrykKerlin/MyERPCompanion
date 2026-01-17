from typing import Mapping

from sqlalchemy.orm import selectinload, with_loader_criteria
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement


from models.business.trade.currency import Currency
from models.business.trade.exchange_rate import ExchangeRate
from repositories.base.base_repository import BaseRepository


class ExchangeRateRepository(BaseRepository[ExchangeRate]):
    _model_cls = ExchangeRate

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
            selectinload(cls._model_cls.base_currency),
            selectinload(cls._model_cls.quote_currency),
            with_loader_criteria(Currency, cls._expr(Currency.is_active.is_(True))),
        )
