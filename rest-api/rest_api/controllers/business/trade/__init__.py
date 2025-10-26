from models.business.trade.currency import Currency
from models.business.trade.supplier import Supplier
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from services.business.trade import CurrencyService, SupplierService
from utils.controller_factory import ControllerFactory

CurrencyController = ControllerFactory.create(
    model_cls=Currency,
    service_cls=CurrencyService,
    input_schema_cls=CurrencyStrictSchema,
    output_schema_cls=CurrencyPlainSchema,
)
SupplierController = ControllerFactory.create(
    model_cls=Supplier,
    service_cls=SupplierService,
    input_schema_cls=SupplierStrictSchema,
    output_schema_cls=SupplierPlainSchema,
)

__all__ = [
    "CurrencyController",
    "SupplierController",
]
