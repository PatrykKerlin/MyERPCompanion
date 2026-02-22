from typing import Mapping

from models.business.trade.exchange_rate import ExchangeRate
from repositories.base.base_repository import BaseRepository
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement


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
        return query
