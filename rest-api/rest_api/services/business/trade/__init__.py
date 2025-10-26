from models.business.trade.currency import Currency
from models.business.trade.supplier import Supplier
from repositories.business.trade import CurrencyRepository, SupplierRepository
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from utils.service_factory import ServiceFactory

CurrencyService = ServiceFactory.create(
    model_cls=Currency,
    repository_cls=CurrencyRepository,
    input_schema_cls=CurrencyStrictSchema,
    output_schema_cls=CurrencyPlainSchema,
)
SupplierService = ServiceFactory.create(
    model_cls=Supplier,
    repository_cls=SupplierRepository,
    input_schema_cls=SupplierStrictSchema,
    output_schema_cls=SupplierPlainSchema,
)


__all__ = [
    "CurrencyService",
    "SupplierService",
]
