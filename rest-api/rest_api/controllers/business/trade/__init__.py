from models.business.trade.currency import Currency
from models.business.trade.discount import Discount
from models.business.trade.supplier import Supplier
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from schemas.business.trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from services.business.trade import CurrencyService, DiscountService, SupplierService
from utils.controller_factory import ControllerFactory
from utils.enums import Action

CurrencyController = ControllerFactory.create(
    model_cls=Currency,
    service_cls=CurrencyService,
    input_schema_cls=CurrencyStrictSchema,
    output_schema_cls=CurrencyPlainSchema,
)
DiscountController = ControllerFactory.create(
    model_cls=Discount,
    service_cls=DiscountService,
    input_schema_cls=DiscountStrictSchema,
    output_schema_cls=DiscountPlainSchema,
    include={
        Action.GET_ALL: True,
        Action.GET_BULK: True,
        Action.GET_ONE: True,
        Action.CREATE: True,
        Action.UPDATE: True,
        Action.DELETE: True,
    },
)
SupplierController = ControllerFactory.create(
    model_cls=Supplier,
    service_cls=SupplierService,
    input_schema_cls=SupplierStrictSchema,
    output_schema_cls=SupplierPlainSchema,
)

__all__ = [
    "CurrencyController",
    "DiscountController",
    "SupplierController",
]
