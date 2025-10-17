from models.business.trade.currency import Currency
from repositories.business.trade import CurrencyRepository
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from utils.service_factory import ServiceFactory

CurrencyService = ServiceFactory.create(
    model_cls=Currency,
    repository_cls=CurrencyRepository,
    input_schema_cls=CurrencyStrictSchema,
    output_schema_cls=CurrencyPlainSchema,
)


__all__ = [
    "CurrencyService",
]
