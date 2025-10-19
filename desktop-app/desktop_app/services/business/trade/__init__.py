from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from utils.service_factory import ServiceFactory

CurrencyService = ServiceFactory.create(
    name_prefix="Currency",
    plain_schema_cls=CurrencyPlainSchema,
    strict_schema_cls=CurrencyStrictSchema,
)

__all__ = [
    "CurrencyService",
]
