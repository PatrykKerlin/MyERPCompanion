from models.business.trade.assoc_category_discount import AssocCategoryDiscount
from models.business.trade.assoc_customer_discount import AssocCustomerDiscount
from models.business.trade.assoc_item_discount import AssocItemDiscount
from models.business.trade.currency import Currency
from models.business.trade.customer import Customer
from models.business.trade.discount import Discount
from models.business.trade.supplier import Supplier
from schemas.business.trade.assoc_category_discount_schema import (
    AssocCategoryDiscountPlainSchema,
    AssocCategoryDiscountStrictSchema,
)
from schemas.business.trade.assoc_customer_discount_schema import (
    AssocCustomerDiscountPlainSchema,
    AssocCustomerDiscountStrictSchema,
)
from schemas.business.trade.assoc_item_discount_schema import (
    AssocItemDiscountPlainSchema,
    AssocItemDiscountStrictSchema,
)
from schemas.business.trade.currency_schema import CurrencyPlainSchema, CurrencyStrictSchema
from schemas.business.trade.customer_schema import CustomerPlainSchema, CustomerStrictSchema
from schemas.business.trade.discount_schema import DiscountPlainSchema, DiscountStrictSchema
from schemas.business.trade.supplier_schema import SupplierPlainSchema, SupplierStrictSchema
from services.business.trade import (
    AssocCategoryDiscountService,
    AssocCustomerDiscountService,
    AssocItemDiscountService,
    CurrencyService,
    CustomerService,
    DiscountService,
    SupplierService,
)
from utils.controller_factory import ControllerFactory
from utils.enums import Action


AssocCategoryDiscountController = ControllerFactory.create(
    model_cls=AssocCategoryDiscount,
    service_cls=AssocCategoryDiscountService,
    input_schema_cls=AssocCategoryDiscountStrictSchema,
    output_schema_cls=AssocCategoryDiscountPlainSchema,
    include={
        Action.GET_ONE: True,
        Action.GET_ALL: True,
        Action.GET_BULK: True,
        Action.CREATE: True,
        Action.CREATE_BULK: True,
        Action.UPDATE: True,
        Action.UPDATE_BULK: True,
        Action.DELETE: True,
        Action.DELETE_BULK: True,
    },
)
AssocCustomerDiscountController = ControllerFactory.create(
    model_cls=AssocCustomerDiscount,
    service_cls=AssocCustomerDiscountService,
    input_schema_cls=AssocCustomerDiscountStrictSchema,
    output_schema_cls=AssocCustomerDiscountPlainSchema,
    include={
        Action.GET_ONE: True,
        Action.GET_ALL: True,
        Action.GET_BULK: True,
        Action.CREATE: True,
        Action.CREATE_BULK: True,
        Action.UPDATE: True,
        Action.UPDATE_BULK: True,
        Action.DELETE: True,
        Action.DELETE_BULK: True,
    },
)
AssocItemDiscountController = ControllerFactory.create(
    model_cls=AssocItemDiscount,
    service_cls=AssocItemDiscountService,
    input_schema_cls=AssocItemDiscountStrictSchema,
    output_schema_cls=AssocItemDiscountPlainSchema,
    include={
        Action.GET_ONE: True,
        Action.GET_ALL: True,
        Action.GET_BULK: True,
        Action.CREATE: True,
        Action.CREATE_BULK: True,
        Action.UPDATE: True,
        Action.UPDATE_BULK: True,
        Action.DELETE: True,
        Action.DELETE_BULK: True,
    },
)
CurrencyController = ControllerFactory.create(
    model_cls=Currency,
    service_cls=CurrencyService,
    input_schema_cls=CurrencyStrictSchema,
    output_schema_cls=CurrencyPlainSchema,
)
CustomerController = ControllerFactory.create(
    model_cls=Customer,
    service_cls=CustomerService,
    input_schema_cls=CustomerStrictSchema,
    output_schema_cls=CustomerPlainSchema,
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
    "AssocCategoryDiscountController",
    "AssocCustomerDiscountController",
    "AssocItemDiscountController",
    "CurrencyController",
    "CustomerController",
    "DiscountController",
    "SupplierController",
]
