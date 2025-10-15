from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from services.base.base_service import BaseService


class CurrencyService(BaseService[CurrencyPlainSchema, CurrencyStrictSchema]):
    _plain_schema_cls = CurrencyPlainSchema
