from models.business.trade.currency import Currency
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from services.business.trade import CurrencyService
from utils.controller_factory import ControllerFactory

CurrencyController = ControllerFactory.create(
    model_cls=Currency,
    service_cls=CurrencyService,
    input_schema_cls=CurrencyStrictSchema,
    output_schema_cls=CurrencyPlainSchema,
)

__all__ = [
    "CurrencyController",
]
