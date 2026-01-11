from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from utils.service_factory import ServiceFactory

CurrencyService = ServiceFactory.create(
    name_prefix="Currency",
    plain_schema_cls=CurrencyPlainSchema,
    strict_schema_cls=CurrencyStrictSchema,
)
SupplierService = ServiceFactory.create(
    name_prefix="Supplier",
    plain_schema_cls=SupplierPlainSchema,
    strict_schema_cls=SupplierStrictSchema,
)

__all__ = [
    "CurrencyService",
    "SupplierService",
]
